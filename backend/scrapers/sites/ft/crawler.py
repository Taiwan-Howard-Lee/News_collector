import re
from typing import Dict, Any
from urllib.parse import urlparse
from ...base import BaseCrawler

class FTCrawler(BaseCrawler):
    """Financial Times crawler with financial news focus."""
    
    def __init__(self):
        super().__init__(rate_limit=1.5)  # Respectful rate limiting
    
    def get_site_config(self) -> Dict[str, Any]:
        return {
            'domain': 'ft.com',
            'categories': ['markets', 'business', 'technology', 'world', 'opinion'],
            'quality_thresholds': {
                'min_words': 300,
                'min_paragraphs': 3
            }
        }
    
    def extract_content(self, result) -> Dict[str, Any]:
        """Extract content from FT pages."""
        # Handle CrawlResultContainer
        if hasattr(result, '_results') and result._results:
            result = result._results[0]
        
        # Get raw content
        passage = getattr(result, 'markdown', None) or getattr(result, 'extracted_content', None)
        if not passage:
            return {}
        
        # Extract metadata
        metadata = self._extract_metadata(result)
        
        # Clean content - FT has specific patterns
        cleaned_content = self._clean_ft_content(passage)
        
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
    
    def _clean_ft_content(self, content: str) -> str:
        """Clean FT-specific content patterns."""
        if not content:
            return ""
        
        # FT-specific patterns
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
    
    def _determine_category(self, url: str, content: str) -> str:
        """Determine content category based on URL and content."""
        url_lower = url.lower()
        content_lower = content.lower()
        
        # URL-based categorization
        if 'markets' in url_lower or 'trading' in url_lower:
            return 'markets'
        elif 'companies' in url_lower or 'business' in url_lower:
            return 'business'
        elif 'technology' in url_lower or 'tech' in url_lower:
            return 'technology'
        elif 'world' in url_lower or 'international' in url_lower:
            return 'world'
        elif 'opinion' in url_lower or 'comment' in url_lower:
            return 'opinion'
        
        # Content-based categorization
        if any(word in content_lower for word in ['market', 'trading', 'investor', 'stock']):
            return 'markets'
        elif any(word in content_lower for word in ['company', 'corporate', 'earnings', 'revenue']):
            return 'business'
        elif any(word in content_lower for word in ['technology', 'software', 'digital', 'innovation']):
            return 'technology'
        elif any(word in content_lower for word in ['international', 'global', 'world', 'country']):
            return 'world'
        
        return 'general'
    
    def _extract_section_from_url(self, url: str) -> str:
        """Extract section from FT URL."""
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