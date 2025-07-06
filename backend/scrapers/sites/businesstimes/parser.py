from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse(html_content: str) -> str:
    """
    Parses the HTML of a Business Times article to extract the main text content.

    Args:
        html_content: The HTML of the article page as a string.

    Returns:
        The extracted article text, or an empty string if content is not found.
    """
    try:
        soup = BeautifulSoup(html_content, 'lxml')

        # The main article content is often in a div with a specific class.
        # Based on inspection, 'prose' is a likely candidate for article content.
        content_element = soup.find('div', class_='prose')
        
        if content_element:
            return content_element.get_text(separator='\n', strip=True)

        logging.warning("Parser could not find the main content element with class 'prose'. The site structure may have changed.")
        return ""

    except Exception as e:
        logging.error(f"An error occurred during parsing: {e}")
        return ""
