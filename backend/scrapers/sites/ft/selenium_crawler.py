from backend.scrapers.base.selenium_base_crawler import SeleniumBaseCrawler
from bs4 import BeautifulSoup
import re

class FTSeleniumCrawler(SeleniumBaseCrawler):
    def __init__(self, headless=True):
        super().__init__(headless=headless)

    def crawl_url(self, url):
        # FT articles are typically in specific containers
        main_selector = 'article, .article-body, .story-body, .o-topper, .o-body'
        html = self.fetch_page(url)
        if not html:
            return None
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try to extract title
        title = soup.title.string if soup.title else ''
        
        # Try to extract main content
        main = soup.select_one(main_selector)
        if main and len(main.get_text()) > 200:
            content = main.get_text(separator=' ', strip=True)
        else:
            # Fallback: try <main> or all text
            main2 = soup.find('main')
            if main2 and len(main2.get_text()) > 200:
                content = main2.get_text(separator=' ', strip=True)
            else:
                content = soup.get_text(separator=' ', strip=True)
        
        # Clean FT-specific content patterns
        cleaned_content = self._clean_ft_content(content)
        
        return {
            'url': url,
            'content': cleaned_content,
            'title': title,
            'extraction_method': 'selenium'
        }
    
    def _clean_ft_content(self, content: str) -> str:
        """Clean FT-specific content patterns."""
        if not content:
            return ""
        
        # FT-specific patterns to remove
        ft_patterns = [
            r'Accessibility help.*?\]',
            r'Skip to navigation.*?\]',
            r'Skip to content.*?\]',
            r'Skip to footer.*?\]',
            r'Financial Times.*?\]',
            r'Subscribe.*?\]',
            r'Sign in.*?\]',
            r'MyFT.*?\]',
            r'Portfolio.*?\]',
            r'Markets.*?\]',
            r'Companies.*?\]',
            r'Technology.*?\]',
            r'World.*?\]',
            r'Opinion.*?\]',
        ]
        
        cleaned = content
        for pattern in ft_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned 