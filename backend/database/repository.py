from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from backend.models.article import Article
from backend.models.user import User

logger = logging.getLogger(__name__)

class ArticleRepository:
    """Repository for article database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_article(self, article_data: Dict[str, Any]) -> Article:
        """Create a new article."""
        try:
            article = Article(**article_data)
            self.db.add(article)
            self.db.commit()
            self.db.refresh(article)
            logger.info(f"Created article: {article.title}")
            return article
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating article: {e}")
            raise
    
    def get_article_by_id(self, article_id: int) -> Optional[Article]:
        """Get article by ID."""
        return self.db.query(Article).filter(Article.id == article_id).first()
    
    def get_article_by_url(self, url: str) -> Optional[Article]:
        """Get article by URL."""
        return self.db.query(Article).filter(Article.url == url).first()
    
    def get_articles(
        self,
        limit: int = 50,
        offset: int = 0,
        source: Optional[str] = None,
        category: Optional[str] = None,
        days: int = 7,
        min_relevance: Optional[float] = None
    ) -> List[Article]:
        """Get articles with filtering and pagination."""
        query = self.db.query(Article)
        
        # Apply filters
        if source:
            query = query.filter(Article.source == source)
        
        if category:
            query = query.filter(Article.category == category)
        
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(Article.discovered_at >= cutoff_date)
        
        if min_relevance is not None:
            query = query.filter(Article.relevance_score >= min_relevance)
        
        # Order by relevance and date
        query = query.order_by(desc(Article.relevance_score), desc(Article.discovered_at))
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        return query.all()
    
    def search_articles(self, search_term: str, limit: int = 20) -> List[Article]:
        """Search articles using PostgreSQL full-text search."""
        # For PostgreSQL, we can use full-text search
        # For now, use simple LIKE search
        search_pattern = f"%{search_term}%"
        return self.db.query(Article).filter(
            or_(
                Article.title.ilike(search_pattern),
                Article.content.ilike(search_pattern),
                Article.summary.ilike(search_pattern)
            )
        ).order_by(desc(Article.relevance_score)).limit(limit).all()
    
    def update_article(self, article_id: int, update_data: Dict[str, Any]) -> Optional[Article]:
        """Update an article."""
        try:
            article = self.get_article_by_id(article_id)
            if article:
                for key, value in update_data.items():
                    setattr(article, key, value)
                article.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(article)
                logger.info(f"Updated article: {article.title}")
                return article
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating article: {e}")
            raise
        return None
    
    def delete_article(self, article_id: int) -> bool:
        """Delete an article."""
        try:
            article = self.get_article_by_id(article_id)
            if article:
                self.db.delete(article)
                self.db.commit()
                logger.info(f"Deleted article: {article.title}")
                return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting article: {e}")
            raise
        return False
    
    def get_article_stats(self) -> Dict[str, Any]:
        """Get article statistics."""
        try:
            total_articles = self.db.query(func.count(Article.id)).scalar()
            
            today = datetime.utcnow().date()
            articles_today = self.db.query(func.count(Article.id)).filter(
                func.date(Article.discovered_at) == today
            ).scalar()
            
            week_ago = datetime.utcnow() - timedelta(days=7)
            articles_this_week = self.db.query(func.count(Article.id)).filter(
                Article.discovered_at >= week_ago
            ).scalar()
            
            # Category distribution
            category_stats = self.db.query(
                Article.category,
                func.count(Article.id)
            ).group_by(Article.category).all()
            
            # Source distribution
            source_stats = self.db.query(
                Article.source,
                func.count(Article.id)
            ).group_by(Article.source).all()
            
            return {
                "total_articles": total_articles,
                "articles_today": articles_today,
                "articles_this_week": articles_this_week,
                "categories": dict(category_stats),
                "sources": dict(source_stats),
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting article stats: {e}")
            raise

class UserRepository:
    """Repository for user database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user."""
        try:
            user = User(**user_data)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"Created user: {user.email}")
            return user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user: {e}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user(self, email: str, update_data: Dict[str, Any]) -> Optional[User]:
        """Update a user."""
        try:
            user = self.get_user_by_email(email)
            if user:
                for key, value in update_data.items():
                    setattr(user, key, value)
                user.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(user)
                logger.info(f"Updated user: {user.email}")
                return user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user: {e}")
            raise
        return None
    
    def update_engagement_points(self, email: str, points: int) -> Optional[User]:
        """Update user engagement points."""
        try:
            user = self.get_user_by_email(email)
            if user:
                user.engagement_points += points
                user.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(user)
                logger.info(f"Updated engagement points for {user.email}: +{points}")
                return user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating engagement points: {e}")
            raise
        return None 