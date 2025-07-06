from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Article(Base):
    """Database model for news articles."""
    
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(String(255), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    source = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    relevance_score = Column(Float, default=0.0)
    category = Column(String(50), nullable=True)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:50]}...', source='{self.source}')>"
    
    def to_dict(self):
        """Convert article to dictionary for API responses."""
        return {
            'id': self.id,
            'article_id': self.article_id,
            'source': self.source,
            'url': self.url,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'discovered_at': self.discovered_at.isoformat() if self.discovered_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'relevance_score': self.relevance_score,
            'category': self.category,
            'is_processed': self.is_processed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 