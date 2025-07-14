import re
from typing import Dict, Any
from urllib.parse import urlparse
from ...base import BaseCrawler

class BloombergCrawler(BaseCrawler):
    """Bloomberg crawler with financial news focus."""
    
    def __init__(self):
        super().__init__(rate_limit=1.0)  # Conservative rate limiting
    
    def get_site_config(self) -> Dict[str, Any]:
        return {
            'domain': 'bloomberg.com',
            'categories': ['markets', 'business', 'technology', 'politics', 'economics'],
            'quality_thresholds': {
                'min_words': 250,
                'min_paragraphs': 2
            }
        }
    
    def extract_content(self, result) -> Dict[str, Any]:
        """Extract content from Bloomberg pages."""
        # Get raw content
        passage = getattr(result, 'markdown', None) or getattr(result, 'extracted_content', None)
        if not passage:
            return {}
        
        # Extract metadata
        metadata = self._extract_metadata(result)
        
        # Clean content - Bloomberg has specific patterns
        cleaned_content = self._clean_bloomberg_content(passage)
        
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
    
    def _clean_bloomberg_content(self, content: str) -> str:
        """Clean Bloomberg-specific content patterns."""
        if not content:
            return ""
        
        # Bloomberg-specific patterns - more aggressive cleaning
        bloomberg_patterns = [
            r'Your browser is.*?Try a different browser.*?Learn more',
            r'Your browser is.*?Learn more.*?\]',
            r'This browser is out of date.*?\]',
            r'Learn more.*?\]',
            r'Bloomberg.*?\]',
            r'Subscribe.*?\]',
            r'Sign in.*?\]',
            r'Markets.*?\]',
            r'Technology.*?\]',
            r'Politics.*?\]',
            r'Business.*?\]',
            r'Opinion.*?\]',
            r'Pursuits.*?\]',
            r'Green.*?\]',
            r'CityLab.*?\]',
            r'Hyperdrive.*?\]',
            r'Skip Navigation.*?\]',
            r'Skip to content.*?\]',
            r'Skip to main content.*?\]',
            r'Navigation.*?\]',
            r'Menu.*?\]',
            r'Search.*?\]',
            r'Log in.*?\]',
            r'Register.*?\]',
        ]
        
        cleaned = content
        for pattern in bloomberg_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove excessive whitespace and empty lines
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'^\s*$\n', '', cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()
        
        # If content is still too long with mostly navigation, try to extract main content
        if len(cleaned) > 10000:
            # Try to find the main content section
            lines = cleaned.split('\n')
            main_content_lines = []
            in_main_content = False
            
            for line in lines:
                line = line.strip()
                if len(line) > 50 and not any(nav in line.lower() for nav in ['menu', 'navigation', 'skip', 'subscribe', 'sign in']):
                    main_content_lines.append(line)
            
            if main_content_lines:
                cleaned = ' '.join(main_content_lines)
        
        return cleaned
    
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
        elif 'economics' in url_lower or 'economy' in url_lower:
            return 'economics'
        
        # Content-based categorization
        if any(word in content_lower for word in ['market', 'trading', 'investor', 'stock', 'bond']):
            return 'markets'
        elif any(word in content_lower for word in ['company', 'corporate', 'earnings', 'revenue']):
            return 'business'
        elif any(word in content_lower for word in ['technology', 'software', 'digital', 'innovation']):
            return 'technology'
        elif any(word in content_lower for word in ['government', 'policy', 'regulation', 'law']):
            return 'politics'
        elif any(word in content_lower for word in ['economy', 'economic', 'gdp', 'inflation']):
            return 'economics'
        
        return 'general'
    
    def _extract_section_from_url(self, url: str) -> str:
        """Extract section from Bloomberg URL."""
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