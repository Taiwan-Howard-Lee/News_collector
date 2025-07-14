from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from backend.models.resource import Resource
from backend.models.user import User

logger = logging.getLogger(__name__)

class ResourceRepository:
    """Repository for resource database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_resource(self, resource_data: Dict[str, Any]) -> Resource:
        """Create a new resource."""
        try:
            resource = Resource(**resource_data)
            self.db.add(resource)
            self.db.commit()
            self.db.refresh(resource)
            logger.info(f"Created resource: {resource.title}")
            return resource
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating resource: {e}")
            raise
    
    def get_resource_by_id(self, resource_id: int) -> Optional[Resource]:
        """Get resource by ID."""
        return self.db.query(Resource).filter(Resource.id == resource_id).first()
    
    def get_resource_by_url(self, url: str) -> Optional[Resource]:
        """Get resource by URL."""
        return self.db.query(Resource).filter(Resource.url == url).first()
    
    def get_resources(
        self,
        limit: int = 50,
        offset: int = 0,
        source: Optional[str] = None,
        category: Optional[str] = None,
        days: int = 7,
        min_relevance: Optional[float] = None
    ) -> List[Resource]:
        """Get resources with filtering and pagination."""
        query = self.db.query(Resource)
        
        # Apply filters
        if source:
            query = query.filter(Resource.source == source)
        
        if category:
            query = query.filter(Resource.category == category)
        
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(Resource.discovered_at >= cutoff_date)
        
        if min_relevance is not None:
            query = query.filter(Resource.relevance_score >= min_relevance)
        
        # Order by relevance and date
        query = query.order_by(desc(Resource.relevance_score), desc(Resource.discovered_at))
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        return query.all()
    
    def search_resources(self, search_term: str, limit: int = 20) -> List[Resource]:
        """Search resources using PostgreSQL full-text search."""
        search_pattern = f"%{search_term}%"
        return self.db.query(Resource).filter(
            or_(
                Resource.title.ilike(search_pattern),
                Resource.content.ilike(search_pattern),
                Resource.summary.ilike(search_pattern)
            )
        ).order_by(desc(Resource.relevance_score)).limit(limit).all()
    
    def update_resource(self, resource_id: int, update_data: Dict[str, Any]) -> Optional[Resource]:
        """Update a resource."""
        try:
            resource = self.get_resource_by_id(resource_id)
            if resource:
                for key, value in update_data.items():
                    setattr(resource, key, value)
                resource.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(resource)
                logger.info(f"Updated resource: {resource.title}")
                return resource
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating resource: {e}")
            raise
        return None
    
    def delete_resource(self, resource_id: int) -> bool:
        """Delete a resource."""
        try:
            resource = self.get_resource_by_id(resource_id)
            if resource:
                self.db.delete(resource)
                self.db.commit()
                logger.info(f"Deleted resource: {resource.title}")
                return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting resource: {e}")
            raise
        return False
    
    def get_resource_stats(self) -> Dict[str, Any]:
        """Get resource statistics."""
        try:
            total_resources = self.db.query(func.count(Resource.id)).scalar()
            
            today = datetime.utcnow().date()
            resources_today = self.db.query(func.count(Resource.id)).filter(
                func.date(Resource.discovered_at) == today
            ).scalar()
            
            week_ago = datetime.utcnow() - timedelta(days=7)
            resources_this_week = self.db.query(func.count(Resource.id)).filter(
                Resource.discovered_at >= week_ago
            ).scalar()
            
            # Category distribution
            category_stats = self.db.query(
                Resource.category,
                func.count(Resource.id)
            ).group_by(Resource.category).all()
            
            # Source distribution
            source_stats = self.db.query(
                Resource.source,
                func.count(Resource.id)
            ).group_by(Resource.source).all()
            
            return {
                "total_resources": total_resources,
                "resources_today": resources_today,
                "resources_this_week": resources_this_week,
                "categories": dict(category_stats),
                "sources": dict(source_stats),
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting resource stats: {e}")
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