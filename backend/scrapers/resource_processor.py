import json
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models.resource import Resource
from ..database.connection import get_db

class ResourceProcessor:
    """Handles processing and storing crawled resources in the database."""
    
    def __init__(self):
        self.db = next(get_db())
    
    def store_resource(self, resource_data: Dict[str, Any]) -> Optional[Resource]:
        """Store a crawled resource in the database."""
        try:
            # Check if resource already exists
            existing_resource = self.db.query(Resource).filter(
                Resource.resource_id == resource_data['resource_id']
            ).first()
            
            if existing_resource:
                # Update existing resource
                existing_resource.title = resource_data['title']
                existing_resource.content = resource_data['content']
                existing_resource.summary = resource_data['summary']
                existing_resource.published_at = resource_data.get('published_at')
                existing_resource.category = resource_data['category']
                existing_resource.metadata_json = resource_data['metadata_json']
                existing_resource.updated_at = datetime.utcnow()
                
                self.db.commit()
                return existing_resource
            else:
                # Create new resource
                new_resource = Resource(
                    resource_id=resource_data['resource_id'],
                    url=resource_data['url'],
                    title=resource_data['title'],
                    content=resource_data['content'],
                    summary=resource_data['summary'],
                    ai_explanation=resource_data['ai_explanation'],
                    published_at=resource_data.get('published_at'),
                    category=resource_data['category'],
                    status=resource_data['status'],
                    metadata_json=resource_data['metadata_json']
                )
                
                self.db.add(new_resource)
                self.db.commit()
                self.db.refresh(new_resource)
                return new_resource
                
        except Exception as e:
            print(f"Error storing resource: {e}")
            self.db.rollback()
            return None
    
    def store_resources(self, resources: list) -> Dict[str, Any]:
        """Store multiple resources and return statistics."""
        results = {
            'total': len(resources),
            'stored': 0,
            'updated': 0,
            'failed': 0,
            'errors': []
        }
        
        for resource_data in resources:
            try:
                result = self.store_resource(resource_data)
                if result:
                    results['stored'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(str(e))
        
        return results
    
    def get_resource_stats(self) -> Dict[str, Any]:
        """Get statistics about stored resources."""
        try:
            total_resources = self.db.query(Resource).count()
            active_resources = self.db.query(Resource).filter(Resource.status == 'active').count()
            
            # Category breakdown
            from sqlalchemy import func
            categories = self.db.query(Resource.category, func.count(Resource.id)).group_by(Resource.category).all()
            category_stats = {cat: count for cat, count in categories}
            
            # Source domain breakdown - use PostgreSQL JSON operators
            from sqlalchemy import func, text
            domains = self.db.query(
                func.cast(Resource.metadata_json['source_domain'], func.String),
                func.count(Resource.id)
            ).group_by(
                Resource.metadata_json['source_domain']
            ).all()
            domain_stats = {domain: count for domain, count in domains if domain}
            
            return {
                'total_resources': total_resources,
                'active_resources': active_resources,
                'category_breakdown': category_stats,
                'domain_breakdown': domain_stats
            }
            
        except Exception as e:
            print(f"Error getting resource stats: {e}")
            return {} 