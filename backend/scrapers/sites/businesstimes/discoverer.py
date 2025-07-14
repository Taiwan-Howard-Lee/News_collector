import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def discover_links(html_content: str, base_url: str = "https://www.businesstimes.com.sg") -> list:
    """
    Discovers all resource links from a Business Times page.

    Args:
        html_content: The HTML content of the page as a string.
        base_url: The base URL to resolve relative links.

    Returns:
        A list of unique, absolute URLs to resources found on the page.
    """
    soup = BeautifulSoup(html_content, 'lxml')
    links = set()

    # Find all headline tags (h1, h3) which commonly contain resource links.
    for tag in soup.find_all(['h1', 'h3']):
        a_tag = tag.find('a', href=True)
        if a_tag:
            href = a_tag['href']
            # Make sure it's a relative link to a resource
            if href.startswith('/') and not href.startswith('//'):
                full_url = urljoin(base_url, href)
                # Filter out non-resource links based on URL patterns
                if '/resource/' in href or '/news/' in href or '/opinion/' in href:
                    links.add(full_url)

    logging.info(f"Discovered {len(links)} unique resource links from {base_url}.")
    return list(links)
