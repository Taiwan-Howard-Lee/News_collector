import logging
import requests
import hashlib
from newspaper import Article
import trafilatura

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_article_content(url: str) -> dict:
    """
    Extracts article content using Trafilatura for the main text and 
    Newspaper3k for metadata. It uses the requests library with a User-Agent
    to avoid being blocked.

    Args:
        url: The URL of the article to process.

    Returns:
        A dictionary containing the article's title, text, publish date, 
        and content hash, or None if extraction fails.
    """
    logging.info(f"Processing URL: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Fetch the page content using requests to handle potential blocks
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        downloaded_html = response.text

        if not downloaded_html:
            logging.error(f"Failed to fetch URL content for {url}.")
            return None

        # 1. Use Trafilatura to get the main body of the article
        content = trafilatura.extract(downloaded_html, include_comments=False, include_tables=False)
        if not content or len(content) < 100:
            logging.error(f"Trafilatura failed to extract sufficient content from {url}.")
            return None
        
        logging.info(f"Successfully extracted content from {url} using Trafilatura.")
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        # 2. Use Newspaper3k on the same HTML to extract metadata
        article = Article(url)
        article.download(input_html=downloaded_html)
        article.parse()

        return {
            'title': article.title,
            'text': content,
            'publish_date': article.publish_date,
            'content_hash': content_hash
        }

    except requests.RequestException as e:
        logging.error(f"Failed to fetch {url} with requests: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred while processing {url}: {e}")
        return None

if __name__ == '__main__':
    # Add test URLs here
    test_urls = [
        "https://www.channelnewsasia.com/singapore/work-permit-no-maximum-employment-period-age-s-pass-foreign-workers-4981096", # New valid CNA link
        "https://www.businesstimes.com.sg/companies-markets/long-overdue-experts-welcome-advisory-against-private-sector-use-nric-numbers-authentication",
        "https://www.businesstimes.com.sg/opinion-features/data-changing-shareholder-capitalism"
    ]
    for test_url in test_urls:
        data = extract_article_content(test_url)
        if data:
            print(f"--- Successfully extracted: {data.get('title', 'No Title')} ---")
            print(f"URL: {test_url}")
            print(f"Text length: {len(data.get('text', ''))}")
            print("--------------------------------------------------")
        else:
            print(f"--- Failed to extract: {test_url} ---")
            print("--------------------------------------------------")
