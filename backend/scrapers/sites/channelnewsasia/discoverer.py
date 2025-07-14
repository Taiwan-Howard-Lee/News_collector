import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def discover_links(html_content: str, base_url: str = "https://www.channelnewsasia.com") -> list:
    """
    Discovers all resource links from a CNA category page by finding links within headline tags.

    Args:
        html_content: The HTML content of the page as a string.
        base_url: The base URL to resolve relative links.

    Returns:
        A list of unique, absolute URLs to resources found on the page.
    """
    soup = BeautifulSoup(html_content, 'lxml')
    links = set()

    # Find all headline tags (h1, h2, h3, h6) which commonly contain resource links.
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h6']):
        a_tag = tag.find('a', href=True)
        if a_tag:
            href = a_tag['href']
            # Ensure the link is a relative path to a resource, not an external site or anchor.
            if href.startswith('/') and not href.startswith('//') and not href.startswith('/video'):
                full_url = urljoin(base_url, href)
                links.add(full_url)

    logging.info(f"Discovered {len(links)} unique resource links from {base_url}.")
    return list(links)

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
