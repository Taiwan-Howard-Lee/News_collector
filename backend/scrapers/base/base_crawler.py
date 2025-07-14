import asyncio
import hashlib
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler, models
import types

class BaseCrawler(ABC):
    """Base crawler class with common functionality for all site-specific crawlers."""
    
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self.last_request_time = 0
        
    async def _rate_limit(self):
        """Implement rate limiting between requests."""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            await asyncio.sleep(self.rate_limit - time_since_last)
        self.last_request_time = asyncio.get_event_loop().time()
    
    def _generate_resource_id(self, url: str) -> str:
        """Generate a unique resource ID from URL."""
        domain = urlparse(url).netloc
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        return f"{domain.replace('.', '_')}_{url_hash}"
    
    def _clean_content(self, content: str) -> str:
        """Clean extracted content by removing navigation, ads, and boilerplate."""
        if not content:
            return ""
        
        # Remove common navigation patterns
        nav_patterns = [
            r'Skip to content.*?\]',
            r'Skip to navigation.*?\]',
            r'Skip to footer.*?\]',
            r'\[Navigation Menu\].*?\]',
            r'\[Skip to main content\].*?\]',
            r'Your browser is.*?Try a different browser',
            r'CNN values your feedback.*?\]',
            r'\[.*?Menu.*?\]',
            r'\[.*?Navigation.*?\]',
            r'\[.*?Search.*?\]',
            r'\[.*?Subscribe.*?\]',
            r'\[.*?Sign in.*?\]',
            r'\[.*?Log in.*?\]',
            r'\[.*?Account.*?\]',
            r'\[.*?Settings.*?\]',
            r'\[.*?Help.*?\]',
            r'\[.*?Contact.*?\]',
            r'\[.*?About.*?\]',
            r'\[.*?Privacy.*?\]',
            r'\[.*?Terms.*?\]',
            r'\[.*?Cookie.*?\]',
            r'\[.*?Ad.*?\]',
            r'\[.*?Advertisement.*?\]',
            r'\[.*?Sponsored.*?\]',
        ]
        
        cleaned = content
        for pattern in nav_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _extract_metadata(self, result) -> Dict[str, Any]:
        """Extract metadata from crawl result."""
        metadata = {}
        
        if hasattr(result, 'metadata') and result.metadata:
            metadata.update({
                'title': result.metadata.get('title'),
                'published_at': result.metadata.get('date_published'),
                'summary': result.metadata.get('description'),
                'author': result.metadata.get('author'),
            })
        
        return metadata
    
    def _calculate_quality_score(self, content: str, word_count: int) -> float:
        """Calculate content quality score (0-1)."""
        if not content or word_count < 50:  # Lowered minimum word count
            return 0.0
        
        # Base score from word count
        score = min(word_count / 500, 1.0)  # More lenient scoring
        
        # Penalize for navigation/ads (less aggressive)
        nav_indicators = ['menu', 'navigation', 'skip to', 'advertisement', 'sponsored']
        nav_count = sum(1 for indicator in nav_indicators if indicator in content.lower())
        score -= nav_count * 0.05  # Less penalty
        
        return max(score, 0.0)
    
    @abstractmethod
    def get_site_config(self) -> Dict[str, Any]:
        """Return site-specific configuration."""
        pass
    
    @abstractmethod
    def extract_content(self, result) -> Dict[str, Any]:
        """Extract content using site-specific logic."""
        pass
    
    async def crawl_url(self, url: str, max_retries: int = 2) -> Optional[Dict[str, Any]]:
        """Crawl a single URL and return structured data with retry logic."""
        await self._rate_limit()
        
        for attempt in range(max_retries + 1):
            try:
                async with AsyncWebCrawler() as crawler:
                    result_or_gen = await crawler.arun(url=url)
                    
                                    # Handle different result types
                if hasattr(result_or_gen, '_results') and result_or_gen._results:
                    result = result_or_gen._results[0]
                elif isinstance(result_or_gen, models.CrawlResultContainer):
                    result = result_or_gen[0]
                elif isinstance(result_or_gen, types.AsyncGeneratorType):
                    result = None
                    async for item in result_or_gen:
                        result = item
                        break
                else:
                    result = result_or_gen
                    
                    if result is None:
                        return None
                    
                    # Extract content using site-specific logic
                    content_data = self.extract_content(result)
                    
                    if not content_data or not content_data.get('content'):
                        return None
                    
                    # Clean content
                    content_data['content'] = self._clean_content(content_data['content'])
                    
                    if not content_data['content']:
                        return None
                    
                    # Generate resource data
                    resource_id = self._generate_resource_id(url)
                    word_count = len(content_data['content'].split())
                    quality_score = self._calculate_quality_score(content_data['content'], word_count)
                    
                    # Only return if quality is acceptable (lowered for testing)
                    if quality_score < 0.1:
                        return None
                    
                    return {
                        'resource_id': resource_id,
                        'url': url,
                        'title': content_data.get('title', ''),
                        'content': content_data['content'],
                        'summary': content_data.get('summary', ''),
                        'ai_explanation': '',  # No AI processing
                        'published_at': content_data.get('published_at'),
                        'category': content_data.get('category', 'general'),
                        'status': 'active',
                        'metadata_json': {
                            'source_domain': urlparse(url).netloc,
                            'section': content_data.get('section', ''),
                            'author': content_data.get('author', ''),
                            'word_count': word_count,
                            'quality_score': quality_score,
                            'extraction_method': 'crawl4ai',
                            'crawled_at': datetime.utcnow().isoformat()
                        }
                    }
                    
            except Exception as e:
                if attempt < max_retries:
                    print(f"Attempt {attempt + 1} failed for {url}: {e}")
                    await asyncio.sleep(1)  # Wait before retry
                    continue
                else:
                    print(f"All attempts failed for {url}: {e}")
                    return None
        
        return None 