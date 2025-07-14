from backend.scrapers.base.selenium_base_crawler import SeleniumBaseCrawler
from bs4 import BeautifulSoup

class BloombergSeleniumCrawler(SeleniumBaseCrawler):
    def __init__(self, headless=True):
        super().__init__(headless=headless)

    def crawl_url(self, url):
        # Bloomberg articles are often in <article> tags or specific containers
        main_selector = 'article, .article-body, .story-body'
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
        return {
            'url': url,
            'content': content,
            'title': title,
            'extraction_method': 'selenium'
        } 