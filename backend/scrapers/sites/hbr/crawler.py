import re
from typing import Dict, Any
from urllib.parse import urlparse
from ...base import BaseCrawler

class HBRCrawler(BaseCrawler):
    """Harvard Business Review crawler for business and management content."""
    def __init__(self):
        super().__init__(rate_limit=1.0)
    def get_site_config(self) -> Dict[str, Any]:
        return {
            'domain': 'hbr.org',
            'categories': ['business', 'management', 'leadership', 'strategy', 'innovation'],
            'quality_thresholds': {'min_words': 200, 'min_paragraphs': 2}
        }
    def extract_content(self, result) -> Dict[str, Any]:
        passage = getattr(result, 'markdown', None) or getattr(result, 'extracted_content', None)
        if not passage:
            return {}
        metadata = self._extract_metadata(result)
        cleaned_content = self._clean_hbr_content(passage)
        url = getattr(result, 'url', '')
        category = self._determine_category(url, cleaned_content)
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
    def _clean_hbr_content(self, content: str) -> str:
        if not content:
            return ""
        patterns = [r'Skip to content.*?\]', r'HBR.*?\]', r'Subscribe.*?\]', r'Sign in.*?\]', r'Business.*?\]', r'Management.*?\]', r'Leadership.*?\]', r'Strategy.*?\]', r'Innovation.*?\]', r'Big Ideas.*?\]', r'Cart.*?\]']
        cleaned = content
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        return cleaned
    def _determine_category(self, url: str, content: str) -> str:
        url_lower = url.lower()
        content_lower = content.lower()
        if 'business' in url_lower:
            return 'business'
        elif 'management' in url_lower:
            return 'management'
        elif 'leadership' in url_lower:
            return 'leadership'
        elif 'strategy' in url_lower:
            return 'strategy'
        elif 'innovation' in url_lower:
            return 'innovation'
        if any(word in content_lower for word in ['business', 'company', 'corporate']):
            return 'business'
        elif any(word in content_lower for word in ['management', 'manager', 'admin']):
            return 'management'
        elif any(word in content_lower for word in ['leadership', 'leader', 'executive']):
            return 'leadership'
        elif any(word in content_lower for word in ['strategy', 'plan', 'tactic']):
            return 'strategy'
        elif any(word in content_lower for word in ['innovation', 'innovate', 'creative']):
            return 'innovation'
        return 'general'
    def _extract_section_from_url(self, url: str) -> str:
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