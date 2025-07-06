import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def discover_links(url: str) -> list[str]:
    """
    Discovers all article links from a Business Times page.

    Args:
        url: The URL of the Business Times page to scrape.

    Returns:
        A list of unique, absolute URLs to articles found on the page.
    """
    links = set()
    try:
        response = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        # Find all headline tags (h1, h3) which commonly contain article links.
        headings = soup.find_all(['h1', 'h3'])

        if not headings:
            logging.warning(f"No h1 or h3 elements found on {url}. The page structure may be unusual.")
            return []

        for heading in headings:
            link_tag = heading.find('a')
            if link_tag and link_tag.has_attr('href'):
                href = link_tag['href']
                # Make sure it's a relative link to an article
                if href.startswith('/') and not href.startswith('//'):
                    full_url = urljoin(url, href)
                    # Filter out non-article links based on URL patterns
                    if any(keyword in full_url for keyword in ['/companies-markets/', '/property/', '/international/', '/opinion-features/', '/lifestyle/', '/startups-tech/', '/singapore/']):
                        links.add(full_url)

        logging.info(f"Discovered {len(links)} unique article links from {url}.")
        return list(links)

    except requests.RequestException as e:
        logging.error(f"Failed to fetch URL {url}: {e}")
        return []
    except Exception as e:
        logging.error(f"An error occurred during link discovery: {e}")
        return []
