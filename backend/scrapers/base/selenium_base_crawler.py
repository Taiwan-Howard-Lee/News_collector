import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

class SeleniumBaseCrawler:
    def __init__(self, headless=True):
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        self.driver = webdriver.Chrome(options=options)

    def fetch_page(self, url, wait_time=3):
        try:
            self.driver.get(url)
            time.sleep(wait_time)  # Wait for JS to load
            return self.driver.page_source
        except Exception as e:
            print(f"Selenium fetch error: {e}")
            return None

    def extract_main_content(self, url, main_selector=None, wait_time=3):
        html = self.fetch_page(url, wait_time=wait_time)
        if not html:
            return None
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        
        if main_selector:
            main = soup.select_one(main_selector)
            if main:
                return self._clean_content(main.get_text(separator=' ', strip=True))
        
        # Fallback: try to find <article> or main content heuristically
        for tag in ['article', 'main', 'section']:
            el = soup.find(tag)
            if el and len(el.get_text()) > 200:
                return self._clean_content(el.get_text(separator=' ', strip=True))
        
        # Fallback: return cleaned all text if nothing else
        return self._clean_content(soup.get_text(separator=' ', strip=True))
    
    def _clean_content(self, content):
        """Clean extracted content by removing common noise."""
        if not content:
            return ""
        
        # Remove common noise patterns
        noise_patterns = [
            r'cookie|privacy|terms|subscribe|sign up|sign in|advertisement|ad',
            r'feedback|survey|rate this|how relevant',
            r'skip to|navigation|menu|search',
            r'loading|please wait|detecting',
            r'robot|captcha|verification'
        ]
        
        import re
        cleaned = content
        for pattern in noise_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned

    def close(self):
        self.driver.quit() 