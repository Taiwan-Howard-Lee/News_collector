from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from backend.database.connection import get_db
from backend.database.repository import ArticleRepository

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/articles", tags=["Articles"])

@router.get("/", summary="Get Articles")
async def get_articles(
    limit: int = Query(default=50, ge=1, le=100, description="Number of articles to return"),
    offset: int = Query(default=0, ge=0, description="Number of articles to skip"),
    source: Optional[str] = Query(default=None, description="Filter by source"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    days: int = Query(default=7, ge=1, le=30, description="Articles from last N days"),
    db: Session = Depends(get_db)
):
    """
    Retrieve articles with optional filtering.
    
    Returns a list of articles with pagination and filtering options.
    """
    try:
        repo = ArticleRepository(db)
        articles = repo.get_articles(
            limit=limit,
            offset=offset,
            source=source,
            category=category,
            days=days
        )
        
        return {
            "articles": [article.to_dict() for article in articles],
            "total": len(articles),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error retrieving articles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{article_id}", summary="Get Article by ID")
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific article by its ID.
    """
    try:
        repo = ArticleRepository(db)
        article = repo.get_article_by_id(article_id)
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return article.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving article {article_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/sources/list", summary="Get Available Sources")
async def get_sources():
    """
    Get a list of all available news sources.
    """
    try:
        sources = [
            {"name": "Channel NewsAsia", "category": "general", "enabled": True},
            {"name": "TODAY Singapore", "category": "general", "enabled": True},
            {"name": "The Business Times", "category": "business", "enabled": True},
            {"name": "The Straits Times", "category": "general", "enabled": True},
            {"name": "Yahoo Singapore News", "category": "general", "enabled": True}
        ]
        
        return {"sources": sources}
        
    except Exception as e:
        logger.error(f"Error retrieving sources: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/categories/list", summary="Get Available Categories")
async def get_categories():
    """
    Get a list of all available article categories.
    """
    try:
        categories = [
            "politics", "economy", "society", "technology", "health",
            "education", "transport", "housing", "environment", "culture", "sports"
        ]
        
        return {"categories": categories}
        
    except Exception as e:
        logger.error(f"Error retrieving categories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/refresh", summary="Trigger Manual Refresh")
async def refresh_articles():
    """
    Trigger a manual refresh of articles from all sources.
    """
    try:
        # TODO: Implement scraping logic
        logger.info("Manual article refresh triggered")
        
        return {
            "status": "success",
            "message": "Article refresh initiated",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error during article refresh: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats/summary", summary="Get Article Statistics")
async def get_article_stats(db: Session = Depends(get_db)):
    """
    Get summary statistics about articles.
    """
    try:
        repo = ArticleRepository(db)
        stats = repo.get_article_stats()
        
        return stats
        
    except Exception as e:
        logger.error(f"Error retrieving article stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 