import re
from typing import Dict, Any
from urllib.parse import urlparse
from ...base import BaseCrawler

class InvescoCrawler(BaseCrawler):
    """Invesco crawler for financial insights and reports."""
    def __init__(self):
        super().__init__(rate_limit=1.0)
    def get_site_config(self) -> Dict[str, Any]:
        return {
            'domain': 'invesco.com',
            'categories': ['finance', 'insights', 'investment', 'markets'],
            'quality_thresholds': {'min_words': 100, 'min_paragraphs': 1}
        }
    def extract_content(self, result) -> Dict[str, Any]:
        passage = getattr(result, 'markdown', None) or getattr(result, 'extracted_content', None)
        if not passage:
            return {}
        metadata = self._extract_metadata(result)
        cleaned_content = self._clean_invesco_content(passage)
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
    def _clean_invesco_content(self, content: str) -> str:
        if not content:
            return ""
        patterns = [r'Skip to main content.*?\]', r'Invesco.*?\]', r'Subscribe.*?\]', r'Sign in.*?\]', r'Insights.*?\]', r'Investment.*?\]', r'Markets.*?\]', r'Finance.*?\]', r'Cart.*?\]']
        cleaned = content
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        return cleaned
    def _determine_category(self, url: str, content: str) -> str:
        url_lower = url.lower()
        content_lower = content.lower()
        if 'insights' in url_lower:
            return 'insights'
        elif 'investment' in url_lower:
            return 'investment'
        elif 'markets' in url_lower:
            return 'markets'
        elif 'finance' in url_lower:
            return 'finance'
        if any(word in content_lower for word in ['insight', 'analysis', 'report']):
            return 'insights'
        elif any(word in content_lower for word in ['investment', 'portfolio', 'fund']):
            return 'investment'
        elif any(word in content_lower for word in ['market', 'stock', 'bond']):
            return 'markets'
        elif any(word in content_lower for word in ['finance', 'financial', 'money']):
            return 'finance'
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