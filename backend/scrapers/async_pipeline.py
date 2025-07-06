import asyncio
import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from backend.database.google_sheets_handler import get_gspread_client, insert_article, insert_log
from backend.scrapers.sites.channelnewsasia.discoverer import discover_links as cna_discoverer
from backend.scrapers.article_extractor import extract_article_content
from backend.database.google_sheets_handler import GOOGLE_SHEET_ID

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def scrape_and_prepare_article(url: str):
    """
    Asynchronously scrapes a single URL and prepares the article data dictionary.
    Does not insert into the database.
    """
    logging.info(f"Scraping: {url}")
    loop = asyncio.get_event_loop()
    
    try:
        # Run synchronous extraction in a thread pool executor
        article_content = await loop.run_in_executor(
            None,  # Uses the default executor
            extract_article_content,
            url
        )

        if article_content and article_content.get('text'):
            article_data = {
                'article_id': f"cna_{uuid.uuid4()}",
                'source': 'Channel NewsAsia',
                'url': url,
                'discovered_at': datetime.utcnow().isoformat(),
                'title': article_content.get('title'),
                'content': article_content.get('text'),
                'summary': 'N/A',
                'status': 'processed'
            }
            logging.info(f"Successfully scraped: {article_content.get('title')}")
            return article_data
        else:
            logging.warning(f"Could not extract content from: {url}")
            return None
    except Exception as e:
        logging.error(f"Error scraping {url}: {e}")
        return None

async def run_async_pipeline(max_workers: int):
    """
    Runs the full scraping pipeline asynchronously using a specified number of workers.
    """
    start_time = time.time()
    logging.info(f"Starting asynchronous pipeline with {max_workers} workers...")

    g_client = get_gspread_client()
    if not g_client:
        logging.error("Pipeline failed: Could not connect to Google Sheets API.")
        return

    # Fetch existing URLs to avoid duplicates
    existing_urls = set()
    try:
        articles_sheet = g_client.open_by_key(GOOGLE_SHEET_ID).worksheet('Articles')
        urls_in_sheet = articles_sheet.col_values(3) # URL is in the 3rd column
        existing_urls.update(urls_in_sheet)
        logging.info(f"Found {len(existing_urls)} existing URLs.")
    except Exception as e:
        logging.warning(f"Could not fetch existing URLs: {e}")

    # Discover links from multiple categories
    source_urls = [
        'https://www.channelnewsasia.com/singapore',
        'https://www.channelnewsasia.com/business',
        'https://www.channelnewsasia.com/sport'
    ]

    all_discovered_links = set()
    logging.info(f"Discovering links from {len(source_urls)} categories...")
    for url in source_urls:
        discovered = cna_discoverer(url)
        all_discovered_links.update(discovered)
    
    new_links = [link for link in all_discovered_links if link not in existing_urls]
    logging.info(f"Discovered {len(new_links)} new articles to process.")

    if not new_links:
        logging.info("No new articles to process. Pipeline finished.")
        return

    # Set up the thread pool executor
    loop = asyncio.get_event_loop()
    loop.set_default_executor(ThreadPoolExecutor(max_workers=max_workers))

    # Stage 1: Concurrently scrape all new links
    logging.info("--- Stage 1: Scraping all new articles ---")
    tasks = [scrape_and_prepare_article(link) for link in new_links]
    scraped_articles = await asyncio.gather(*tasks)
    
    # Filter out failed scrapes
    valid_articles = [article for article in scraped_articles if article is not None]
    
    articles_processed = len(valid_articles)
    if articles_processed == 0:
        logging.info("No new articles were successfully scraped. Pipeline finished.")
        return

    scraping_duration = time.time() - start_time
    logging.info(f"--- Stage 1 finished in {scraping_duration:.2f} seconds. Scraped {articles_processed} articles. ---")

    # Stage 2: Batch insert into Google Sheets
    logging.info("--- Stage 2: Batch inserting articles into Google Sheets ---")
    try:
        articles_sheet = g_client.open_by_key(GOOGLE_SHEET_ID).worksheet('Articles')
        
        # Prepare rows for batch update
        rows_to_insert = [
            [
                article['article_id'],
                article['source'],
                article['url'],
                article['discovered_at'],
                article['title'],
                article['content'],
                article['summary'],
                article['status']
            ] for article in valid_articles
        ]
        
        articles_sheet.append_rows(rows_to_insert, value_input_option='USER_ENTERED')
        logging.info(f"Successfully inserted {articles_processed} articles into the spreadsheet.")

    except Exception as e:
        logging.error(f"Failed to batch insert articles: {e}")
        return

    total_duration = time.time() - start_time
    logging.info(f"--- Stage 2 finished. Total pipeline duration: {total_duration:.2f} seconds. ---")

    # Log the completion of the run
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'level': 'INFO',
        'event': 'AsyncPipelineFinished',
        'details': f'Processed {articles_processed} articles in {total_duration:.2f}s with {max_workers} workers.'
    }
    insert_log(g_client, log_data)
