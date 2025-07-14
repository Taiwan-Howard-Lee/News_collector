import asyncio
import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from backend.scrapers.sites.channelnewsasia.discoverer import discover_links as cna_discoverer
from backend.scrapers.resource_extractor import extract_resource_content

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def scrape_and_prepare_resource(url: str):
    """
    Asynchronously scrapes a single URL and prepares the resource data dictionary.
    Does not insert into the database.
    """
    logging.info(f"Scraping: {url}")
    loop = asyncio.get_event_loop()
    
    try:
        # Run synchronous extraction in a thread pool executor
        resource_content = await loop.run_in_executor(
            None,  # Uses the default executor
            extract_resource_content,
            url
        )

        if resource_content and resource_content.get('text'):
            resource_data = {
                'resource_id': f"cna_{uuid.uuid4()}",
                'source': 'Channel NewsAsia',
                'url': url,
                'discovered_at': datetime.utcnow().isoformat(),
                'title': resource_content.get('title'),
                'content': resource_content.get('text'),
                'summary': 'N/A',
                'status': 'active'
            }
            logging.info(f"Successfully scraped: {resource_content.get('title')}")
            return resource_data
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

    # Discover links from multiple categories (example, should be modularized)
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
    
    new_links = list(all_discovered_links)
    logging.info(f"Discovered {len(new_links)} new resources to process.")

    if not new_links:
        logging.info("No new resources to process. Pipeline finished.")
        return

    # Set up the thread pool executor
    loop = asyncio.get_event_loop()
    loop.set_default_executor(ThreadPoolExecutor(max_workers=max_workers))

    # Stage 1: Concurrently scrape all new links
    logging.info("--- Stage 1: Scraping all new resources ---")
    tasks = [scrape_and_prepare_resource(link) for link in new_links]
    scraped_resources = await asyncio.gather(*tasks)
    
    # Filter out failed scrapes
    valid_resources = [resource for resource in scraped_resources if resource is not None]
    
    resources_processed = len(valid_resources)
    if resources_processed == 0:
        logging.info("No new resources were successfully scraped. Pipeline finished.")
        return

    scraping_duration = time.time() - start_time
    logging.info(f"--- Stage 1 finished in {scraping_duration:.2f} seconds. Scraped {resources_processed} resources. ---")

    # TODO: Insert valid_resources into the PostgreSQL database here
    # (This should be implemented in the next step)

    total_duration = time.time() - start_time
    logging.info(f"--- Pipeline finished. Total duration: {total_duration:.2f} seconds. ---")
