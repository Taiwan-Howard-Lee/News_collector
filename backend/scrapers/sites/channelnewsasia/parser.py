import logging
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse(html_content: str) -> str:
    """
    Parses the HTML of a Channel NewsAsia article to extract the core text content.
    This version iterates through all 'text-long' divs to find the main article body,
    making it more resilient to page structure changes.

    Args:
        html_content: The raw HTML string of the article page.

    Returns:
        A clean string containing only the article's body text, or an empty string if parsing fails.
    """
    try:
        soup = BeautifulSoup(html_content, 'lxml')

        # Find all divs with the 'text-long' class. CNA pages can have multiple.
        possible_bodies = soup.find_all('div', class_='text-long')

        if not possible_bodies:
            logging.warning("CNA Parser: Could not find any 'div.text-long' elements. Page structure may have changed.")
            return ""

        # Iterate through the found divs and return the first one with substantial content.
        for body in possible_bodies:
            paragraphs = body.find_all('p')
            clean_text = ' '.join(p.get_text(strip=True) for p in paragraphs)
            
            # Assume the main content will be longer than a certain threshold (e.g., 200 chars).
            if len(clean_text) > 200:
                logging.info(f"Successfully parsed article, extracted {len(clean_text)} characters.")
                return clean_text
        
        logging.warning("CNA Parser: Found 'text-long' divs, but none contained sufficient text content.")
        return ""

    except Exception as e:
        logging.error(f"An error occurred while parsing the article with BeautifulSoup: {e}")
        return ""
