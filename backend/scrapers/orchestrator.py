import asyncio
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
from .sites.wsj.crawler import WSJCrawler
from .sites.ft.crawler import FTCrawler
from .sites.bloomberg.crawler import BloombergCrawler
from .sites.cnn.crawler import CNNCrawler
from .sites.investopedia.crawler import InvestopediaCrawler
from .sites.cnbc.crawler import CNBCcrawler
from .sites.shopify.crawler import ShopifyNewsCrawler
from .sites.hbr.crawler import HBRCrawler
from .sites.invesco.crawler import InvescoCrawler

# Selenium fallback crawlers
from .sites.wsj.selenium_crawler import WSJSeleniumCrawler
from .sites.bloomberg.selenium_crawler import BloombergSeleniumCrawler
from .sites.cnn.selenium_crawler import CNNSeleniumCrawler
from .sites.cnbc.selenium_crawler import CNBCSeleniumCrawler
from .sites.hbr.selenium_crawler import HBRSeleniumCrawler
from .sites.investopedia.selenium_crawler import InvestopediaSeleniumCrawler
from .sites.shopify.selenium_crawler import ShopifySeleniumCrawler
from .sites.invesco.selenium_crawler import InvescoSeleniumCrawler
from .sites.ft.selenium_crawler import FTSeleniumCrawler

class CrawlerOrchestrator:
    """Orchestrates multiple crawlers and manages the crawling process."""
    
    def __init__(self):
        self.crawlers = {
            'wsj.com': WSJCrawler(),
            'ft.com': FTCrawler(),
            'bloomberg.com': BloombergCrawler(),
            'cnn.com': CNNCrawler(),
            'investopedia.com': InvestopediaCrawler(),
            'cnbc.com': CNBCcrawler(),
            'shopify.com': ShopifyNewsCrawler(),
            'hbr.org': HBRCrawler(),
            'invesco.com': InvescoCrawler(),
        }
        
        # Selenium fallback crawlers for problematic sites
        self.selenium_crawlers = {
            'wsj.com': WSJSeleniumCrawler(),
            'bloomberg.com': BloombergSeleniumCrawler(),
            'cnn.com': CNNSeleniumCrawler(),
            'cnbc.com': CNBCSeleniumCrawler(),
            'hbr.org': HBRSeleniumCrawler(),
            'investopedia.com': InvestopediaSeleniumCrawler(),
            'shopify.com': ShopifySeleniumCrawler(),
            'invesco.com': InvescoSeleniumCrawler(),
            'ft.com': FTSeleniumCrawler(),
        }
        
    def get_crawler_for_url(self, url: str):
        """Get the appropriate crawler for a given URL."""
        domain = urlparse(url).netloc
        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Handle subdomains like edition.cnn.com -> cnn.com
        if domain.startswith('edition.'):
            domain = domain.replace('edition.', '')
        
        return self.crawlers.get(domain)
    
    async def crawl_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Crawl a single URL using the appropriate crawler with Selenium fallback."""
        domain = self._get_domain_from_url(url)
        crawler = self.get_crawler_for_url(url)
        
        if not crawler:
            print(f"No crawler found for domain: {urlparse(url).netloc}")
            return None
        
        # Try Crawl4AI first
        result = await crawler.crawl_url(url)
        
        # If Crawl4AI fails and we have a Selenium fallback, try that
        if result is None and domain in self.selenium_crawlers:
            print(f"🔄 Crawl4AI failed for {url}, trying Selenium fallback...")
            selenium_crawler = self.selenium_crawlers[domain]
            try:
                result = selenium_crawler.crawl_url(url)
                if result:
                    print(f"✅ Selenium fallback succeeded for {url}")
                    # Convert Selenium result to match Crawl4AI format
                    result = self._convert_selenium_result(result, domain)
            except Exception as e:
                print(f"❌ Selenium fallback failed for {url}: {e}")
                result = None
        
        return result
    
    def _get_domain_from_url(self, url: str) -> str:
        """Extract domain from URL for fallback logic."""
        domain = urlparse(url).netloc
        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
        # Handle subdomains like edition.cnn.com -> cnn.com
        if domain.startswith('edition.'):
            domain = domain.replace('edition.', '')
        return domain
    
    def _convert_selenium_result(self, selenium_result: Dict[str, Any], domain: str) -> Dict[str, Any]:
        """Convert Selenium result to match Crawl4AI format."""
        content = selenium_result.get('content', '')
        word_count = len(content.split())
        
        # Calculate quality score (simplified)
        quality_score = min(word_count / 500, 1.0) if word_count > 50 else 0.0
        
        # Try to extract publication date from content or use current time
        published_at = None
        try:
            # For now, use current time as fallback
            from datetime import datetime
            published_at = datetime.utcnow()
        except:
            pass
        
        return {
            'resource_id': f"{domain.replace('.', '_')}_{hash(selenium_result['url']) % 10000}",
            'url': selenium_result['url'],
            'title': selenium_result.get('title', ''),
            'content': content,
            'summary': '',
            'ai_explanation': '',
            'published_at': published_at,
            'category': 'general',
            'status': 'active',
            'metadata_json': {
                'source_domain': domain,
                'section': '',
                'author': '',
                'word_count': word_count,
                'quality_score': quality_score,
                'extraction_method': 'selenium',
                'crawled_at': datetime.utcnow()
            }
        }
    
    async def crawl_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Crawl multiple URLs concurrently."""
        tasks = []
        for url in urls:
            task = asyncio.create_task(self.crawl_url(url))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None results and exceptions
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Error during crawling: {result}")
            elif result is not None:
                valid_results.append(result)
        
        return valid_results
    
    def get_supported_domains(self) -> List[str]:
        """Get list of supported domains."""
        return list(self.crawlers.keys())
    
    async def test_crawlers(self, test_urls: List[str]) -> Dict[str, Any]:
        """Test all crawlers with sample URLs."""
        results = {}
        
        for url in test_urls:
            print(f"\nTesting crawler for: {url}")
            result = await self.crawl_url(url)
            
            if result:
                print(f"✅ Success - {result.get('title', 'No title')}")
                print(f"   Word count: {len(result.get('content', '').split())}")
                print(f"   Category: {result.get('category', 'unknown')}")
                print(f"   Quality score: {result.get('metadata_json', {}).get('quality_score', 0):.2f}")
            else:
                print(f"❌ Failed to crawl: {url}")
            
            results[url] = result
        
        return results 