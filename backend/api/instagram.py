from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timedelta
import json
import logging

from ..database.connection import get_db
from ..models.resource import Resource
from ..utils.ai_processor import AIProcessor
from ..services.image_generator import image_generator

router = APIRouter(prefix="/instagram", tags=["instagram"])
logger = logging.getLogger(__name__)

@router.get("/posts")
async def get_instagram_posts(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get Instagram-style posts with pagination"""
    try:
        query = db.query(Resource).filter(Resource.status == 'active')
        
        if category:
            query = query.filter(Resource.category == category)
        
        # Order by relevance score and recency
        query = query.order_by(
            desc(Resource.relevance_score),
            desc(Resource.published_at),
            desc(Resource.discovered_at)
        )
        
        resources = query.offset(offset).limit(limit).all()
        
        posts = [resource.to_instagram_post() for resource in resources]
        
        return {
            "posts": posts,
            "total": query.count(),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stories")
async def get_instagram_stories(db: Session = Depends(get_db)):
    """Get Instagram-style stories"""
    try:
        # Get recent breaking news for stories
        breaking_news = db.query(Resource).filter(
            Resource.status == 'active',
            Resource.discovered_at >= datetime.utcnow() - timedelta(hours=24)
        ).order_by(desc(Resource.relevance_score)).limit(5).all()
        
        # Get daily briefing (top stories of the day)
        daily_briefing = db.query(Resource).filter(
            Resource.status == 'active',
            Resource.discovered_at >= datetime.utcnow() - timedelta(hours=24)
        ).order_by(desc(Resource.relevance_score)).limit(10).all()
        
        # Get category highlights
        categories = ['Business', 'Technology', 'Politics', 'Finance', 'Property']
        category_stories = []
        
        for category in categories:
            top_story = db.query(Resource).filter(
                Resource.category == category,
                Resource.status == 'active',
                Resource.discovered_at >= datetime.utcnow() - timedelta(days=1)
            ).order_by(desc(Resource.relevance_score)).first()
            
            if top_story:
                category_stories.append({
                    'id': f'category_{category}',
                    'title': category,
                    'imageUrl': f'assets/images/category_{category.lower()}.png',
                    'content': top_story.summary or top_story.title,
                    'type': 'category',
                    'createdAt': datetime.utcnow().isoformat(),
                    'expiresAt': (datetime.utcnow() + timedelta(hours=24)).isoformat(),
                    'isViewed': False,
                    'category': category,
                    'viewsCount': 0
                })
        
        stories = []
        
        # Daily briefing story
        if daily_briefing:
            stories.append({
                'id': 'daily_briefing',
                'title': 'Daily Briefing',
                'imageUrl': 'assets/images/daily_briefing.png',
                'content': f"Today's top {len(daily_briefing)} Singapore news highlights",
                'type': 'dailyBriefing',
                'createdAt': datetime.utcnow().isoformat(),
                'expiresAt': (datetime.utcnow() + timedelta(hours=24)).isoformat(),
                'isViewed': False,
                'slides': [
                    {
                        'id': f'slide_{i}',
                        'imageUrl': story.image_url or story._generate_placeholder_image(),
                        'title': story.title,
                        'text': story.summary,
                        'duration': 5,
                        'actionUrl': story.url,
                        'actionText': 'Read More'
                    } for i, story in enumerate(daily_briefing[:5])
                ],
                'viewsCount': 0
            })
        
        # Breaking news story
        if breaking_news:
            stories.append({
                'id': 'breaking_news',
                'title': 'Breaking',
                'imageUrl': 'assets/images/breaking_news.png',
                'content': 'Latest breaking news from Singapore',
                'type': 'breakingNews',
                'createdAt': datetime.utcnow().isoformat(),
                'expiresAt': (datetime.utcnow() + timedelta(hours=24)).isoformat(),
                'isViewed': False,
                'slides': [
                    {
                        'id': f'breaking_slide_{i}',
                        'imageUrl': story.image_url or story._generate_placeholder_image(),
                        'title': story.title,
                        'text': story.summary,
                        'duration': 5,
                        'actionUrl': story.url,
                        'actionText': 'Read More'
                    } for i, story in enumerate(breaking_news[:3])
                ],
                'viewsCount': 0
            })
        
        # Add category stories
        stories.extend(category_stories)
        
        return {"stories": stories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts/{post_id}/like")
async def like_post(post_id: int, db: Session = Depends(get_db)):
    """Like/unlike a post"""
    try:
        resource = db.query(Resource).filter(Resource.id == post_id).first()
        if not resource:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Toggle like (in real app, this would be user-specific)
        resource.likes_count += 1
        resource.engagement_score = calculate_engagement_score(resource)
        
        db.commit()
        
        return {
            "success": True,
            "likes_count": resource.likes_count,
            "engagement_score": resource.engagement_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts/{post_id}/share")
async def share_post(post_id: int, db: Session = Depends(get_db)):
    """Share a post"""
    try:
        resource = db.query(Resource).filter(Resource.id == post_id).first()
        if not resource:
            raise HTTPException(status_code=404, detail="Post not found")
        
        resource.shares_count += 1
        resource.engagement_score = calculate_engagement_score(resource)
        
        db.commit()
        
        return {
            "success": True,
            "shares_count": resource.shares_count,
            "engagement_score": resource.engagement_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts/{post_id}/comment")
async def add_comment(
    post_id: int,
    comment_data: dict,
    db: Session = Depends(get_db)
):
    """Add AI-generated comment to a post"""
    try:
        resource = db.query(Resource).filter(Resource.id == post_id).first()
        if not resource:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Generate AI response using the AI processor
        ai_processor = AIProcessor()
        user_comment = comment_data.get('comment', '')
        
        # Generate AI response based on the article content
        ai_response = await ai_processor.generate_comment_response(
            article_title=resource.title,
            article_summary=resource.summary,
            user_comment=user_comment
        )
        
        resource.comments_count += 1
        resource.engagement_score = calculate_engagement_score(resource)
        
        db.commit()
        
        return {
            "success": True,
            "ai_response": ai_response,
            "comments_count": resource.comments_count,
            "engagement_score": resource.engagement_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trending")
async def get_trending_posts(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get trending posts based on engagement"""
    try:
        # Get posts with high engagement in the last 24 hours
        trending_posts = db.query(Resource).filter(
            Resource.status == 'active',
            Resource.discovered_at >= datetime.utcnow() - timedelta(hours=24),
            Resource.engagement_score > 0
        ).order_by(
            desc(Resource.engagement_score),
            desc(Resource.likes_count),
            desc(Resource.shares_count)
        ).limit(limit).all()
        
        posts = [resource.to_instagram_post() for resource in trending_posts]
        
        return {"trending_posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get available categories with post counts"""
    try:
        categories = db.query(
            Resource.category,
            func.count(Resource.id).label('count')
        ).filter(
            Resource.status == 'active',
            Resource.category.isnot(None)
        ).group_by(Resource.category).all()

        return {
            "categories": [
                {
                    "name": category,
                    "count": count,
                    "icon": get_category_icon(category)
                }
                for category, count in categories
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts/{post_id}/generate-image")
async def generate_post_image(post_id: int, db: Session = Depends(get_db)):
    """Generate an image for a specific post"""
    try:
        resource = db.query(Resource).filter(Resource.id == post_id).first()
        if not resource:
            raise HTTPException(status_code=404, detail="Post not found")

        # Prepare article data for image generation
        article_data = {
            'title': resource.title,
            'summary': resource.summary,
            'category': resource.category,
            'url': resource.url,
            'source': resource.source
        }

        # Generate image
        image_url = await image_generator.generate_post_image(article_data)

        # Update resource with generated image URL
        resource.image_url = image_url
        db.commit()

        return {
            "success": True,
            "image_url": image_url,
            "post_id": post_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-all-images")
async def generate_all_images(db: Session = Depends(get_db)):
    """Generate images for all posts that don't have them"""
    try:
        # Get posts without images
        resources = db.query(Resource).filter(
            Resource.status == 'active',
            Resource.image_url.is_(None)
        ).all()

        generated_count = 0
        for resource in resources:
            try:
                article_data = {
                    'title': resource.title,
                    'summary': resource.summary,
                    'category': resource.category,
                    'url': resource.url,
                    'source': resource.source
                }

                image_url = await image_generator.generate_post_image(article_data)
                resource.image_url = image_url
                generated_count += 1

            except Exception as e:
                logger.error(f"Error generating image for post {resource.id}: {e}")
                continue

        db.commit()

        return {
            "success": True,
            "generated_count": generated_count,
            "total_posts": len(resources)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def calculate_engagement_score(resource: Resource) -> float:
    """Calculate engagement score based on likes, comments, and shares"""
    # Weighted engagement score
    likes_weight = 1.0
    comments_weight = 2.0
    shares_weight = 3.0
    
    engagement = (
        resource.likes_count * likes_weight +
        resource.comments_count * comments_weight +
        resource.shares_count * shares_weight
    )
    
    # Normalize by time (newer posts get slight boost)
    time_factor = 1.0
    if resource.discovered_at:
        hours_old = (datetime.utcnow() - resource.discovered_at).total_seconds() / 3600
        time_factor = max(0.1, 1.0 - (hours_old / 168))  # Decay over a week
    
    return engagement * time_factor * resource.relevance_score

def get_category_icon(category: str) -> str:
    """Get icon for category"""
    icons = {
        'Business': '💼',
        'Technology': '💻',
        'Politics': '🏛️',
        'Finance': '💰',
        'Property': '🏠',
        'Education': '🎓',
        'Healthcare': '🏥',
        'Transport': '🚇',
        'Environment': '🌱',
        'Sports': '⚽',
        'Entertainment': '🎭'
    }
    return icons.get(category, '📰')
