"""
Image generation service for Instagram-style posts.
Handles screenshot capture, AI image generation, and image optimization.
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import hashlib
import aiohttp
import aiofiles
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# Configure logging
logger = logging.getLogger(__name__)

class ImageGenerator:
    """Service for generating images for Instagram-style posts"""
    
    def __init__(self):
        self.cache_dir = "data/images"
        self.placeholder_dir = "data/placeholders"
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure image directories exist"""
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.placeholder_dir, exist_ok=True)
    
    async def generate_post_image(self, article_data: Dict[str, Any]) -> str:
        """
        Generate an image for an Instagram post.
        Priority: Screenshot > AI Generated > Scraped > Placeholder
        """
        try:
            # Try screenshot first
            screenshot_url = await self.capture_screenshot(article_data.get('url'))
            if screenshot_url:
                return screenshot_url
            
            # Try AI generation
            ai_image_url = await self.generate_ai_image(article_data)
            if ai_image_url:
                return ai_image_url
            
            # Try scraping existing image
            scraped_url = await self.scrape_article_image(article_data.get('url'))
            if scraped_url:
                return scraped_url
            
            # Fallback to category placeholder
            return self.generate_category_placeholder(article_data.get('category', 'general'))
            
        except Exception as e:
            logger.error(f"Error generating post image: {e}")
            return self.generate_category_placeholder(article_data.get('category', 'general'))
    
    async def capture_screenshot(self, url: str) -> Optional[str]:
        """
        Capture screenshot of article page using headless browser.
        This would require Playwright or Selenium in production.
        """
        if not url:
            return None
        
        try:
            # For now, return None - would implement with Playwright
            # TODO: Implement with Playwright for production
            logger.info(f"Screenshot capture not implemented yet for: {url}")
            return None
            
        except Exception as e:
            logger.error(f"Error capturing screenshot for {url}: {e}")
            return None
    
    async def generate_ai_image(self, article_data: Dict[str, Any]) -> Optional[str]:
        """
        Generate AI image based on article content.
        This would integrate with DALL-E, Midjourney, or Stable Diffusion.
        """
        try:
            # For now, return None - would implement with AI image APIs
            # TODO: Implement with DALL-E or Stable Diffusion
            logger.info(f"AI image generation not implemented yet for: {article_data.get('title', 'Unknown')}")
            return None
            
        except Exception as e:
            logger.error(f"Error generating AI image: {e}")
            return None
    
    async def scrape_article_image(self, url: str) -> Optional[str]:
        """
        Scrape featured image from article page.
        """
        if not url:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # Simple image extraction (would use BeautifulSoup in production)
                        # Look for common meta tags
                        import re
                        
                        # Try Open Graph image
                        og_match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
                        if og_match:
                            image_url = og_match.group(1)
                            return await self.cache_external_image(image_url)
                        
                        # Try Twitter card image
                        twitter_match = re.search(r'<meta name="twitter:image" content="([^"]+)"', html)
                        if twitter_match:
                            image_url = twitter_match.group(1)
                            return await self.cache_external_image(image_url)
            
            return None
            
        except Exception as e:
            logger.error(f"Error scraping image from {url}: {e}")
            return None
    
    async def cache_external_image(self, image_url: str) -> Optional[str]:
        """
        Download and cache external image.
        """
        try:
            # Generate cache filename
            url_hash = hashlib.md5(image_url.encode()).hexdigest()
            cache_path = os.path.join(self.cache_dir, f"{url_hash}.jpg")
            
            # Check if already cached
            if os.path.exists(cache_path):
                return f"/images/{url_hash}.jpg"
            
            # Download image
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, timeout=10) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        
                        # Optimize and save image
                        optimized_data = self.optimize_image(image_data)
                        
                        async with aiofiles.open(cache_path, 'wb') as f:
                            await f.write(optimized_data)
                        
                        return f"/images/{url_hash}.jpg"
            
            return None
            
        except Exception as e:
            logger.error(f"Error caching image {image_url}: {e}")
            return None
    
    def optimize_image(self, image_data: bytes) -> bytes:
        """
        Optimize image for Instagram-style posts (1080x1080 square).
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize to Instagram square format
            size = (1080, 1080)
            
            # Calculate crop box to maintain aspect ratio
            width, height = image.size
            if width > height:
                # Landscape - crop sides
                crop_size = min(width, height)
                left = (width - crop_size) // 2
                top = 0
                right = left + crop_size
                bottom = crop_size
            else:
                # Portrait - crop top/bottom
                crop_size = min(width, height)
                left = 0
                top = (height - crop_size) // 2
                right = crop_size
                bottom = top + crop_size
            
            # Crop and resize
            image = image.crop((left, top, right, bottom))
            image = image.resize(size, Image.Resampling.LANCZOS)
            
            # Save optimized image
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            return image_data
    
    def generate_category_placeholder(self, category: str) -> str:
        """
        Generate a beautiful category-based placeholder image.
        """
        try:
            category_lower = category.lower()
            placeholder_path = os.path.join(self.placeholder_dir, f"{category_lower}.jpg")
            
            # Check if placeholder already exists
            if os.path.exists(placeholder_path):
                return f"/placeholders/{category_lower}.jpg"
            
            # Create placeholder image
            size = (1080, 1080)
            
            # Enhanced category color schemes with gradients
            color_schemes = {
                'business': ('#667eea', '#764ba2', '💼', '#f093fb'),
                'technology': ('#4facfe', '#00f2fe', '💻', '#43e97b'),
                'politics': ('#fa709a', '#fee140', '🏛️', '#ffecd2'),
                'finance': ('#a8edea', '#fed6e3', '💰', '#ffd89b'),
                'property': ('#d299c2', '#fef9d7', '🏠', '#89f7fe'),
                'transport': ('#89f7fe', '#66a6ff', '🚇', '#a8edea'),
                'education': ('#ffecd2', '#fcb69f', '🎓', '#ff8a80'),
                'healthcare': ('#ff9a9e', '#fecfef', '🏥', '#ffecd2'),
                'environment': ('#a8e6cf', '#dcedc1', '🌱', '#ffd3a5'),
                'sports': ('#ffa726', '#ff7043', '⚽', '#ffcc02'),
                'entertainment': ('#667eea', '#764ba2', '🎭', '#f093fb'),
            }
            
            primary_color, secondary_color, emoji, accent_color = color_schemes.get(
                category_lower, ('#607D8B', '#455A64', '📰', '#90A4AE')
            )
            
            # Create smooth gradient background
            image = Image.new('RGB', size, primary_color)
            draw = ImageDraw.Draw(image)

            # Create diagonal gradient effect
            for i in range(size[1]):
                for j in range(size[0]):
                    # Calculate diagonal ratio
                    ratio = (i + j) / (size[0] + size[1])
                    ratio = min(1.0, max(0.0, ratio))

                    # Smooth curve for better gradient
                    ratio = ratio * ratio * (3.0 - 2.0 * ratio)  # Smoothstep function

                    r1, g1, b1 = tuple(int(primary_color[j:j+2], 16) for j in (1, 3, 5))
                    r2, g2, b2 = tuple(int(secondary_color[j:j+2], 16) for j in (1, 3, 5))
                    r3, g3, b3 = tuple(int(accent_color[j:j+2], 16) for j in (1, 3, 5))

                    if ratio < 0.5:
                        # First half: primary to secondary
                        local_ratio = ratio * 2
                        r = int(r1 + (r2 - r1) * local_ratio)
                        g = int(g1 + (g2 - g1) * local_ratio)
                        b = int(b1 + (b2 - b1) * local_ratio)
                    else:
                        # Second half: secondary to accent
                        local_ratio = (ratio - 0.5) * 2
                        r = int(r2 + (r3 - r2) * local_ratio)
                        g = int(g2 + (g3 - g2) * local_ratio)
                        b = int(b2 + (b3 - b2) * local_ratio)

                    # Add subtle noise for texture
                    if (i + j) % 3 == 0:
                        r = min(255, r + 5)
                        g = min(255, g + 5)
                        b = min(255, b + 5)

                    draw.point((j, i), fill=(r, g, b))
            
            # Add category text and emoji
            try:
                # Try to load a nice font
                font_size = 120
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
                emoji_font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 200)
            except:
                # Fallback to default font
                font = ImageFont.load_default()
                emoji_font = ImageFont.load_default()
            
            # Draw emoji
            emoji_bbox = draw.textbbox((0, 0), emoji, font=emoji_font)
            emoji_width = emoji_bbox[2] - emoji_bbox[0]
            emoji_height = emoji_bbox[3] - emoji_bbox[1]
            emoji_x = (size[0] - emoji_width) // 2
            emoji_y = (size[1] - emoji_height) // 2 - 100
            draw.text((emoji_x, emoji_y), emoji, font=emoji_font, fill='white')
            
            # Draw category name
            category_text = category.title()
            text_bbox = draw.textbbox((0, 0), category_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = (size[0] - text_width) // 2
            text_y = emoji_y + 250
            
            # Add text shadow
            draw.text((text_x + 2, text_y + 2), category_text, font=font, fill='black')
            draw.text((text_x, text_y), category_text, font=font, fill='white')
            
            # Save placeholder
            image.save(placeholder_path, 'JPEG', quality=90)
            
            return f"/placeholders/{category_lower}.jpg"
            
        except Exception as e:
            logger.error(f"Error generating placeholder for {category}: {e}")
            return "/placeholders/default.jpg"
    
    def get_image_url(self, relative_path: str) -> str:
        """
        Convert relative image path to full URL.
        """
        base_url = os.getenv('BASE_URL', 'http://localhost:8000')
        return f"{base_url}{relative_path}"

# Global instance
image_generator = ImageGenerator()
