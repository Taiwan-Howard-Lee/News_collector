from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid
import os

# Check if we're using PostgreSQL or SQLite
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/news.db')
IS_POSTGRESQL = DATABASE_URL.startswith('postgresql')

if IS_POSTGRESQL:
    from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
else:
    # For SQLite, use Text instead of JSONB and TSVECTOR
    JSONB = Text
    TSVECTOR = Text

Base = declarative_base()

class Resource(Base):
    """Database model for information resources (articles, guides, opportunities, etc.) with PostgreSQL optimizations."""
    
    __tablename__ = 'resources'
    
    id = Column(Integer, primary_key=True)
    resource_id = Column(String(255), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    source = Column(String(100), nullable=True)
    url = Column(String(500), nullable=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    ai_explanation = Column(Text, nullable=True)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    relevance_score = Column(Float, default=0.0)
    category = Column(String(100), nullable=True)
    status = Column(String(50), default='active')  # active, outdated, important, archived
    metadata_json = Column(JSONB, nullable=True)  # Flexible metadata storage
    search_vector = Column(TSVECTOR, nullable=True)  # Full-text search vector

    # Instagram-style fields
    image_url = Column(String(500), nullable=True)  # Screenshot or AI-generated image
    hashtags = Column(JSONB, nullable=True)  # Instagram-style hashtags
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    engagement_score = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for performance
    if IS_POSTGRESQL:
        __table_args__ = (
            Index('idx_resources_source_date', 'source', 'discovered_at'),
            Index('idx_resources_relevance', 'relevance_score'),
            Index('idx_resources_category', 'category'),
            Index('idx_resources_published', 'published_at'),
            Index('idx_resources_search', 'search_vector', postgresql_using='gin'),
        )
    else:
        __table_args__ = (
            Index('idx_resources_source_date', 'source', 'discovered_at'),
            Index('idx_resources_relevance', 'relevance_score'),
            Index('idx_resources_category', 'category'),
            Index('idx_resources_published', 'published_at'),
        )
    
    def __repr__(self):
        return f"<Resource(id={self.id}, title='{self.title[:50]}...', source='{self.source}')>"
    
    def to_dict(self):
        """Convert resource to dictionary for API responses."""
        return {
            'id': self.id,
            'resource_id': self.resource_id,
            'source': self.source,
            'url': self.url,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'ai_explanation': self.ai_explanation,
            'discovered_at': self.discovered_at.isoformat() if self.discovered_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'relevance_score': self.relevance_score,
            'category': self.category,
            'status': self.status,
            'metadata_json': self.metadata_json,
            'image_url': self.image_url,
            'hashtags': self.hashtags or [],
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'shares_count': self.shares_count,
            'engagement_score': self.engagement_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def to_instagram_post(self):
        """Convert Resource to Instagram-style post format"""
        return {
            'id': str(self.id),
            'title': self.title,
            'caption': self._generate_caption(),
            'imageUrl': self.image_url or self._generate_placeholder_image(),
            'sourceUrl': self.url,
            'sourceName': self.source,
            'createdAt': self.published_at.isoformat() if self.published_at else self.discovered_at.isoformat(),
            'hashtags': self._generate_hashtags(),
            'likesCount': self.likes_count,
            'isLiked': False,  # Will be determined by user preferences
            'isBookmarked': False,  # Will be determined by user preferences
            'comments': [],  # Will be populated separately
            'category': self.category,
            'relevanceScore': self.relevance_score
        }

    def _generate_caption(self):
        """Generate Instagram-style caption"""
        caption = self.summary if self.summary else self.title
        if len(caption) > 150:
            caption = caption[:147] + "..."
        return caption

    def _generate_placeholder_image(self):
        """Generate placeholder image URL based on category"""
        category = self.category.lower() if self.category else 'general'
        return f'assets/images/placeholder_{category}.png'

    def _generate_hashtags(self):
        """Generate Instagram-style hashtags"""
        if self.hashtags:
            return self.hashtags

        hashtags = ['Singapore']

        if self.category:
            hashtags.append(self.category.replace(' ', ''))

        if self.source:
            hashtags.append(self.source.replace(' ', '').replace('.', ''))

        # Add content-based hashtags
        content = f"{self.title} {self.summary or ''}".lower()
        keyword_map = {
            'ai': 'AI',
            'artificial intelligence': 'AI',
            'technology': 'Tech',
            'fintech': 'Fintech',
            'startup': 'Startup',
            'government': 'Government',
            'policy': 'Policy',
            'economy': 'Economy',
            'business': 'Business',
            'finance': 'Finance',
            'property': 'Property',
            'housing': 'Housing',
            'mrt': 'MRT',
            'transport': 'Transport',
            'education': 'Education',
            'healthcare': 'Healthcare',
        }

        for keyword, hashtag in keyword_map.items():
            if keyword in content and hashtag not in hashtags:
                hashtags.append(hashtag)

        return hashtags[:5]  # Limit to 5 hashtags