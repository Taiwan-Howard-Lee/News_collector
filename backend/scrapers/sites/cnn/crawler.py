import re
from typing import Dict, Any
from urllib.parse import urlparse
from ...base import BaseCrawler

class CNNCrawler(BaseCrawler):
    """CNN crawler with international news focus."""
    
    def __init__(self):
        super().__init__(rate_limit=1.5)  # Respectful rate limiting
    
    def get_site_config(self) -> Dict[str, Any]:
        return {
            'domain': 'cnn.com',
            'categories': ['world', 'business', 'technology', 'politics', 'health'],
            'quality_thresholds': {
                'min_words': 200,
                'min_paragraphs': 2
            }
        }
    
    def extract_content(self, result) -> Dict[str, Any]:
        """Extract content from CNN pages."""
        # Handle CrawlResultContainer
        if hasattr(result, '_results') and result._results:
            result = result._results[0]
        
        # Get raw content
        passage = getattr(result, 'markdown', None) or getattr(result, 'extracted_content', None)
        if not passage:
            return {}
        
        # Extract metadata
        metadata = self._extract_metadata(result)
        
        # Clean content - CNN has specific patterns
        cleaned_content = self._clean_cnn_content(passage)
        
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
    
    def _clean_cnn_content(self, content: str) -> str:
        """Clean CNN-specific content patterns."""
        if not content:
            return ""
        
        # CNN-specific patterns to remove
        cnn_patterns = [
            r'CNN values your feedback.*?\]',
            r'How relevant is this ad.*?\]',
            r'Did you encounter any technical issues.*?\]',
            r'Video player was slow.*?\]',
            r'Video content never loaded.*?\]',
            r'Ad froze or did not function.*?\]',
            r'Skip Navigation.*?\]',
            r'Skip to content.*?\]',
            r'CNN.*?\]',
            r'Subscribe.*?\]',
            r'Sign in.*?\]',
            r'World.*?\]',
            r'Business.*?\]',
            r'Technology.*?\]',
            r'Politics.*?\]',
            r'Health.*?\]',
            r'Entertainment.*?\]',
            r'Sports.*?\]',
            r'Cancel.*?Submit',
            r'Thank You!.*?',
            r'Your effort and contr.*?',
            r'\[.*?\]',  # Remove all bracketed content
            r'### CNN values your feedback.*?Submit',
            r'### How relevant is this ad.*?Submit',
        ]
        
        cleaned = content
        for pattern in cnn_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove excessive whitespace and empty lines
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'^\s*$\n', '', cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()
        
        # If content is mostly navigation, try to extract article content
        if len(cleaned) < 200:  # Too short, likely just navigation
            # Look for article patterns
            article_patterns = [
                r'(?:CNN|Reuters|Associated Press).*?(?:reported|said|announced|confirmed)',
                r'(?:Breaking|Latest|Update).*?(?:news|report|announcement)',
                r'(?:According to|Officials|Authorities).*?(?:said|confirmed|announced)',
            ]
            
            for pattern in article_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                if matches:
                    cleaned = ' '.join(matches)
                    break
        
        return cleaned
    
    def _determine_category(self, url: str, content: str) -> str:
        """Determine content category based on URL and content."""
        url_lower = url.lower()
        content_lower = content.lower()
        
        # URL-based categorization
        if 'world' in url_lower or 'international' in url_lower:
            return 'world'
        elif 'business' in url_lower or 'economy' in url_lower:
            return 'business'
        elif 'technology' in url_lower or 'tech' in url_lower:
            return 'technology'
        elif 'politics' in url_lower or 'government' in url_lower:
            return 'politics'
        elif 'health' in url_lower or 'medical' in url_lower:
            return 'health'
        
        # Content-based categorization
        if any(word in content_lower for word in ['international', 'global', 'world', 'country', 'nation']):
            return 'world'
        elif any(word in content_lower for word in ['business', 'economy', 'market', 'company', 'corporate']):
            return 'business'
        elif any(word in content_lower for word in ['technology', 'software', 'digital', 'innovation', 'tech']):
            return 'technology'
        elif any(word in content_lower for word in ['government', 'policy', 'regulation', 'law', 'political']):
            return 'politics'
        elif any(word in content_lower for word in ['health', 'medical', 'doctor', 'hospital', 'disease']):
            return 'health'
        
        return 'general'
    
    def _extract_section_from_url(self, url: str) -> str:
        """Extract section from CNN URL."""
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