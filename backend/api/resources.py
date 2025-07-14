from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from ..database.connection import get_db
from ..models.resource import Resource
from ..utils.ai_processor import AIProcessor

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["Resources"])

# Initialize AI processor
ai_processor = AIProcessor()

@router.get("/articles", summary="Get Articles")
def get_articles(
    search: Optional[str] = Query(None, description="Search query"),
    source: Optional[str] = Query(None, description="Filter by source"),
    date_filter: Optional[str] = Query(None, description="Date filter (today, yesterday, week, month)"),
    sort_by: Optional[str] = Query("relevance", description="Sort by (relevance, date-desc, date-asc, source)"),
    limit: int = Query(50, ge=1, le=100, description="Number of articles to return"),
    offset: int = Query(0, ge=0, description="Number of articles to skip"),
    db: Session = Depends(get_db)
):
    """
    Retrieve articles with optional filtering, searching, and sorting.
    """
    try:
        # Start with base query
        query = db.query(Resource).filter(Resource.status == 'active')
        
        # Apply search filter
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                Resource.title.ilike(search_term) |
                Resource.summary.ilike(search_term) |
                Resource.content.ilike(search_term)
            )
        
        # Apply source filter
        if source:
            query = query.filter(Resource.source == source)
        
        # Apply date filter
        if date_filter:
            now = datetime.utcnow()
            if date_filter == "today":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                query = query.filter(Resource.discovered_at >= start_date)
            elif date_filter == "yesterday":
                yesterday = now - timedelta(days=1)
                start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                query = query.filter(Resource.discovered_at >= start_date, Resource.discovered_at < end_date)
            elif date_filter == "week":
                start_date = now - timedelta(days=7)
                query = query.filter(Resource.discovered_at >= start_date)
            elif date_filter == "month":
                start_date = now - timedelta(days=30)
                query = query.filter(Resource.discovered_at >= start_date)
        
        # Apply sorting
        if sort_by == "date-desc":
            query = query.order_by(Resource.discovered_at.desc())
        elif sort_by == "date-asc":
            query = query.order_by(Resource.discovered_at.asc())
        elif sort_by == "source":
            query = query.order_by(Resource.source, Resource.discovered_at.desc())
        else:  # relevance (default)
            query = query.order_by(Resource.relevance_score.desc(), Resource.discovered_at.desc())
        
        # Apply pagination
        articles = query.offset(offset).limit(limit).all()
        
        # Convert to dict format
        articles_data = [article.to_dict() for article in articles]
        
        # Get total count for pagination
        total_count = query.count()
        
        return {
            "articles": articles_data,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count
        }
        
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/articles/{article_id}", summary="Get Single Article")
def get_article(article_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a single article by ID.
    """
    try:
        article = db.query(Resource).filter(
            Resource.resource_id == article_id,
            Resource.status == 'active'
        ).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return article.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching article {article_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/sources", summary="Get Available Sources")
def get_sources(db: Session = Depends(get_db)):
    """
    Get list of available news sources.
    """
    try:
        # Get distinct sources from database
        sources = db.query(Resource.source).filter(
            Resource.status == 'active',
            Resource.source.isnot(None)
        ).distinct().all()
        
        source_list = [source[0] for source in sources if source[0]]
        source_list.sort()
        
        return {"sources": source_list}
        
    except Exception as e:
        logger.error(f"Error fetching sources: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats", summary="Get Database Statistics")
def get_stats(db: Session = Depends(get_db)):
    """
    Get database statistics and metrics.
    """
    try:
        from sqlalchemy import func
        
        # Total articles
        total_articles = db.query(Resource).filter(Resource.status == 'active').count()
        
        # Articles by source
        sources_stats = db.query(
            Resource.source,
            func.count(Resource.id).label('count')
        ).filter(Resource.status == 'active').group_by(Resource.source).all()
        
        # Articles by category
        category_stats = db.query(
            Resource.category,
            func.count(Resource.id).label('count')
        ).filter(Resource.status == 'active').group_by(Resource.category).all()
        
        # Recent articles (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_articles = db.query(Resource).filter(
            Resource.status == 'active',
            Resource.discovered_at >= yesterday
        ).count()
        
        return {
            "total_articles": total_articles,
            "recent_articles": recent_articles,
            "sources": {source: count for source, count in sources_stats},
            "categories": {category: count for category, count in category_stats},
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# AI Chat Endpoints
@router.post("/ai/chat", summary="Chat with AI about Articles")
def chat_with_ai(chat_data: dict, db: Session = Depends(get_db)):
    """
    Chat with AI about articles or general news topics.
    """
    try:
        message = chat_data.get('message')
        article_id = chat_data.get('article_id')

        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        # Get article context if provided
        article_context = ""
        if article_id:
            article = db.query(Resource).filter(
                Resource.resource_id == article_id,
                Resource.status == 'active'
            ).first()

            if article:
                article_context = f"""
                Article Title: {article.title}
                Article Summary: {article.summary}
                Article Content: {article.content[:1000]}...
                """

        # Generate AI response
        response = ai_processor.chat_about_article(message, article_context)

        if response:
            return {
                "response": response,
                "article_id": article_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate AI response")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/ai/summarize", summary="AI Summarize Article")
def ai_summarize_article(data: dict, db: Session = Depends(get_db)):
    """
    Generate AI summary for an article.
    """
    try:
        article_id = data.get('article_id')
        custom_length = data.get('length', 200)

        if not article_id:
            raise HTTPException(status_code=400, detail="article_id is required")

        # Get article
        article = db.query(Resource).filter(
            Resource.resource_id == article_id,
            Resource.status == 'active'
        ).first()

        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        # Generate summary
        summary = ai_processor.generate_summary(article.content, custom_length)

        if summary:
            return {
                "summary": summary,
                "article_id": article_id,
                "length": len(summary)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate summary")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating AI summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/ai/explain-relevance", summary="AI Explain Article Relevance")
def ai_explain_relevance(data: dict, db: Session = Depends(get_db)):
    """
    Get AI explanation of why an article is relevant to user.
    """
    try:
        article_id = data.get('article_id')
        user_profile = data.get('user_profile', {})

        if not article_id:
            raise HTTPException(status_code=400, detail="article_id is required")

        # Get article
        article = db.query(Resource).filter(
            Resource.resource_id == article_id,
            Resource.status == 'active'
        ).first()

        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        # Generate relevance explanation
        article_dict = article.to_dict()
        explanation = ai_processor.generate_relevance_explanation(article_dict, user_profile)

        if explanation:
            return {
                "explanation": explanation,
                "article_id": article_id,
                "relevance_score": article.relevance_score
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate explanation")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating relevance explanation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/ai/daily-briefing", summary="Generate Daily News Briefing")
def generate_daily_briefing(data: dict, db: Session = Depends(get_db)):
    """
    Generate a personalized daily news briefing.
    """
    try:
        user_profile = data.get('user_profile', {})

        # Get today's top articles
        from datetime import datetime, timedelta
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        articles = db.query(Resource).filter(
            Resource.status == 'active',
            Resource.discovered_at >= today
        ).order_by(Resource.relevance_score.desc()).limit(10).all()

        if not articles:
            # Fallback to recent articles if no articles today
            yesterday = today - timedelta(days=1)
            articles = db.query(Resource).filter(
                Resource.status == 'active',
                Resource.discovered_at >= yesterday
            ).order_by(Resource.relevance_score.desc()).limit(10).all()

        articles_data = [article.to_dict() for article in articles]

        # Generate briefing
        briefing = ai_processor.generate_daily_briefing(articles_data, user_profile)

        if briefing:
            return {
                "briefing": briefing,
                "article_count": len(articles_data),
                "generated_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate briefing")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating daily briefing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/ai/personalized-insights", summary="Get Personalized Article Insights")
def get_personalized_insights(data: dict, db: Session = Depends(get_db)):
    """
    Get personalized insights for articles based on user profile.
    """
    try:
        article_ids = data.get('article_ids', [])
        user_profile = data.get('user_profile', {})

        if not article_ids:
            raise HTTPException(status_code=400, detail="article_ids are required")

        # Get articles
        articles = db.query(Resource).filter(
            Resource.resource_id.in_(article_ids),
            Resource.status == 'active'
        ).all()

        articles_data = [article.to_dict() for article in articles]

        # Generate personalized insights
        enhanced_articles = ai_processor.generate_personalized_insights(articles_data, user_profile)

        return {
            "articles": enhanced_articles,
            "generated_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating personalized insights: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/ai/sentiment-analysis", summary="Analyze Article Sentiment")
def analyze_article_sentiment(data: dict, db: Session = Depends(get_db)):
    """
    Analyze sentiment of an article.
    """
    try:
        article_id = data.get('article_id')

        if not article_id:
            raise HTTPException(status_code=400, detail="article_id is required")

        # Get article
        article = db.query(Resource).filter(
            Resource.resource_id == article_id,
            Resource.status == 'active'
        ).first()

        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        # Analyze sentiment
        sentiment_analysis = ai_processor.analyze_sentiment(article.content)

        if sentiment_analysis:
            return {
                "article_id": article_id,
                "sentiment_analysis": sentiment_analysis,
                "analyzed_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to analyze sentiment")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# User Management Endpoints
@router.post("/user/profile", summary="Save User Profile")
def save_user_profile(profile_data: dict, db: Session = Depends(get_db)):
    """
    Save user profile data from onboarding.
    """
    try:
        # Validate required fields
        required_fields = ['q1', 'q2', 'q3', 'q4']
        for field in required_fields:
            if field not in profile_data or not profile_data[field].strip():
                raise HTTPException(status_code=400, detail=f"Field {field} is required")

        # Here you would typically save to a User table
        # For now, we'll just return success
        logger.info(f"User profile saved: {profile_data}")

        return {"status": "success", "message": "Profile saved successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving user profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# User Management Endpoints
@router.post("/user/profile", summary="Save User Profile")
def save_user_profile(profile_data: dict, db: Session = Depends(get_db)):
    """
    Save user profile data from onboarding.
    """
    try:
        # Validate required fields
        required_fields = ['q1', 'q2', 'q3', 'q4']
        for field in required_fields:
            if field not in profile_data or not profile_data[field].strip():
                raise HTTPException(status_code=400, detail=f"Field {field} is required")

        # Here you would typically save to a User table
        # For now, we'll just return success
        logger.info(f"User profile saved: {profile_data}")

        return {"status": "success", "message": "Profile saved successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving user profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/user/profile/{email}", summary="Get User Profile")
def get_user_profile(email: str, db: Session = Depends(get_db)):
    """
    Get user profile by email.
    """
    try:
        # For now, return a mock profile
        # In production, you'd query the User table

        return {
            "user_email": email,
            "profile_q1_answer": "Sample long-term goals",
            "profile_q2_answer": "Sample passionate topics",
            "profile_q3_answer": "Sample avoided news",
            "ai_persona_description": "Sample AI persona",
            "engagement_points": 0,
            "created_at": datetime.utcnow().isoformat(),
            "last_active": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Engagement Tracking
@router.post("/engagement", summary="Track User Engagement")
def track_engagement(engagement_data: dict, db: Session = Depends(get_db)):
    """
    Track user engagement with articles.
    """
    try:
        article_id = engagement_data.get('article_id')
        action = engagement_data.get('action')

        if not article_id or not action:
            raise HTTPException(status_code=400, detail="article_id and action are required")

        # Log engagement
        logger.info(f"Engagement tracked: {action} on article {article_id}")

        return {"status": "success", "message": "Engagement tracked"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error tracking engagement: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
