import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def discover_links(url: str) -> list[str]:
    """
    Discovers all article links from a CNA category page by finding links within headline tags.

    Args:
        url: The URL of the CNA category page to scrape.

    Returns:
        A list of unique, absolute URLs to articles found on the page.
    """
    links = set()
    try:
        response = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        # Find all headline tags (h1, h2, h3, h6) which commonly contain article links.
        headings = soup.find_all(['h1', 'h2', 'h3', 'h6'])

        if not headings:
            logging.warning(f"No h1, h2, h3, or h6 elements found on {url}. The page structure may be unusual.")
            return []

        for heading in headings:
            link_tag = heading.find('a')
            if link_tag and link_tag.has_attr('href'):
                href = link_tag['href']
                # Ensure the link is a relative path to an article, not an external site or anchor.
                if href.startswith('/') and not href.startswith('//'):
                    full_url = urljoin(url, href)
                    links.add(full_url)
        
        logging.info(f"Discovered {len(links)} unique article links from {url}.")
        return list(links)

    except requests.RequestException as e:
        logging.error(f"Failed to fetch URL {url}: {e}")
        return []
    except Exception as e:
        logging.error(f"An error occurred during link discovery: {e}")
        return []

if __name__ == '__main__':
    international_url = 'https://www.channelnewsasia.com/international'
    print(f"--- Discovering links from: {international_url} ---")
    discovered_links = discover_links(international_url)

    if discovered_links:
        print(f"Found {len(discovered_links)} links:")
        for i, link in enumerate(discovered_links, 1):
            print(f"{i}. {link}")
    else:
        print("No links were discovered.")
