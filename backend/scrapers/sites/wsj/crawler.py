import re
from typing import Dict, Any
from urllib.parse import urlparse
from ...base import BaseCrawler

class WSJCrawler(BaseCrawler):
    """Wall Street Journal crawler with financial news focus."""
    
    def __init__(self):
        super().__init__(rate_limit=2.0)  # Respectful rate limiting
    
    def get_site_config(self) -> Dict[str, Any]:
        return {
            'domain': 'wsj.com',
            'categories': ['markets', 'business', 'technology', 'politics'],
            'quality_thresholds': {
                'min_words': 200,
                'min_paragraphs': 2
            }
        }
    
    def extract_content(self, result) -> Dict[str, Any]:
        """Extract content from WSJ pages."""
        # Get raw content
        passage = getattr(result, 'markdown', None) or getattr(result, 'extracted_content', None)
        if not passage:
            return {}
        
        # Extract metadata
        metadata = self._extract_metadata(result)
        
        # Clean content
        cleaned_content = self._clean_content(passage)
        
        # Determine category from URL or content
        url = getattr(result, 'url', '')
        category = self._determine_category(url, cleaned_content)
        
        # Extract section from URL
        section = self._extract_section_from_url(url)
        
        return {
            'content': cleaned_content,
            'title': metadata.get('title', ''),
            'summary': metadata.get('summary', ''),
            'published_at': metadata.get('published_at'),
            'author': metadata.get('author', ''),
            'category': category,
            'section': section
        }
    
    def _determine_category(self, url: str, content: str) -> str:
        """Determine content category based on URL and content."""
        url_lower = url.lower()
        content_lower = content.lower()
        
        # URL-based categorization
        if 'markets' in url_lower or 'stocks' in url_lower:
            return 'markets'
        elif 'business' in url_lower or 'companies' in url_lower:
            return 'business'
        elif 'technology' in url_lower or 'tech' in url_lower:
            return 'technology'
        elif 'politics' in url_lower or 'government' in url_lower:
            return 'politics'
        
        # Content-based categorization
        if any(word in content_lower for word in ['stock', 'market', 'trading', 'investor']):
            return 'markets'
        elif any(word in content_lower for word in ['company', 'corporate', 'earnings', 'revenue']):
            return 'business'
        elif any(word in content_lower for word in ['technology', 'software', 'digital', 'innovation']):
            return 'technology'
        
        return 'general'
    
    def _extract_section_from_url(self, url: str) -> str:
        """Extract section from WSJ URL."""
        try:
            path = urlparse(url).path
            if path.startswith('/'):
                path = path[1:]
            sections = path.split('/')
            if sections:
                return sections[0]
        except:
            pass
        return 'general' 