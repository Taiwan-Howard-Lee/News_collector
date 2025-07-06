from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    """Database model for user profiles and preferences."""
    
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    profile_q1_answer = Column(Text, nullable=True)  # What type of news interests you most?
    profile_q2_answer = Column(Text, nullable=True)  # What topics or keywords are you most interested in?
    profile_q3_answer = Column(Text, nullable=True)  # What topics would you prefer to avoid?
    ai_persona_description = Column(Text, nullable=True)  # How should the AI chat with you?
    engagement_points = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', points={self.engagement_points})>"
    
    def to_dict(self):
        """Convert user to dictionary for API responses."""
        return {
            'id': self.id,
            'email': self.email,
            'profile_q1_answer': self.profile_q1_answer,
            'profile_q2_answer': self.profile_q2_answer,
            'profile_q3_answer': self.profile_q3_answer,
            'ai_persona_description': self.ai_persona_description,
            'engagement_points': self.engagement_points,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 