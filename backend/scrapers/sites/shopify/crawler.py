import re
from typing import Dict, Any
from urllib.parse import urlparse
from ...base import BaseCrawler

class ShopifyNewsCrawler(BaseCrawler):
    """Shopify News crawler for press releases and company news."""
    def __init__(self):
        super().__init__(rate_limit=1.0)
    def get_site_config(self) -> Dict[str, Any]:
        return {
            'domain': 'shopify.com',
            'categories': ['business', 'technology', 'ecommerce'],
            'quality_thresholds': {'min_words': 100, 'min_paragraphs': 1}
        }
    def extract_content(self, result) -> Dict[str, Any]:
        passage = getattr(result, 'markdown', None) or getattr(result, 'extracted_content', None)
        if not passage:
            return {}
        metadata = self._extract_metadata(result)
        cleaned_content = self._clean_shopify_content(passage)
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
    def _clean_shopify_content(self, content: str) -> str:
        if not content:
            return ""
        patterns = [r'Skip to Content.*?\]', r'Shopify.*?\]', r'Pressroom.*?\]', r'Subscribe.*?\]', r'Sign in.*?\]', r'Business.*?\]', r'Technology.*?\]', r'Ecommerce.*?\]', r'News.*?\]', r'Cart.*?\]']
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
        elif 'technology' in url_lower:
            return 'technology'
        elif 'ecommerce' in url_lower:
            return 'ecommerce'
        if any(word in content_lower for word in ['business', 'company', 'corporate']):
            return 'business'
        elif any(word in content_lower for word in ['technology', 'software', 'digital']):
            return 'technology'
        elif any(word in content_lower for word in ['ecommerce', 'shop', 'retail']):
            return 'ecommerce'
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