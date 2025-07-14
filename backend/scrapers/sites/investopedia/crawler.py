import re
from typing import Dict, Any
from urllib.parse import urlparse
from ...base import BaseCrawler

class InvestopediaCrawler(BaseCrawler):
    """Investopedia crawler with educational content focus."""
    
    def __init__(self):
        super().__init__(rate_limit=1.0)  # Conservative rate limiting
    
    def get_site_config(self) -> Dict[str, Any]:
        return {
            'domain': 'investopedia.com',
            'categories': ['education', 'markets', 'business', 'finance', 'investing'],
            'quality_thresholds': {
                'min_words': 300,
                'min_paragraphs': 3
            }
        }
    
    def extract_content(self, result) -> Dict[str, Any]:
        """Extract content from Investopedia pages."""
        # Get raw content
        passage = getattr(result, 'markdown', None) or getattr(result, 'extracted_content', None)
        if not passage:
            return {}
        
        # Extract metadata
        metadata = self._extract_metadata(result)
        
        # Clean content - Investopedia has specific patterns
        cleaned_content = self._clean_investopedia_content(passage)
        
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
    
    def _clean_investopedia_content(self, content: str) -> str:
        """Clean Investopedia-specific content patterns."""
        if not content:
            return ""
        
        # Investopedia-specific patterns
        investopedia_patterns = [
            r'Skip to content.*?\]',
            r'Investopedia.*?\]',
            r'Subscribe.*?\]',
            r'Sign in.*?\]',
            r'News.*?\]',
            r'Markets.*?\]',
            r'Business.*?\]',
            r'Technology.*?\]',
            r'Personal Finance.*?\]',
            r'Investing.*?\]',
            r'Academy.*?\]',
            r'Dictionary.*?\]',
            r'Simulator.*?\]',
            r'Portfolio.*?\]',
            r'Watchlist.*?\]',
            r'My Account.*?\]',
        ]
        
        cleaned = content
        for pattern in investopedia_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove excessive whitespace and empty lines
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'^\s*$\n', '', cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _determine_category(self, url: str, content: str) -> str:
        """Determine content category based on URL and content."""
        url_lower = url.lower()
        content_lower = content.lower()
        
        # URL-based categorization
        if 'academy' in url_lower or 'tutorial' in url_lower or 'guide' in url_lower:
            return 'education'
        elif 'markets' in url_lower or 'trading' in url_lower:
            return 'markets'
        elif 'business' in url_lower or 'corporate' in url_lower:
            return 'business'
        elif 'finance' in url_lower or 'financial' in url_lower:
            return 'finance'
        elif 'investing' in url_lower or 'investment' in url_lower:
            return 'investing'
        
        # Content-based categorization
        if any(word in content_lower for word in ['tutorial', 'guide', 'learn', 'education', 'academy', 'how to']):
            return 'education'
        elif any(word in content_lower for word in ['market', 'trading', 'stock', 'bond', 'commodity']):
            return 'markets'
        elif any(word in content_lower for word in ['business', 'corporate', 'company', 'enterprise']):
            return 'business'
        elif any(word in content_lower for word in ['finance', 'financial', 'money', 'banking']):
            return 'finance'
        elif any(word in content_lower for word in ['invest', 'investment', 'portfolio', 'asset']):
            return 'investing'
        
        return 'general'
    
    def _extract_section_from_url(self, url: str) -> str:
        """Extract section from Investopedia URL."""
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