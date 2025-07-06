import google.generativeai as genai
import logging
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProcessor:
    """Handles AI processing tasks using Google Gemini API."""
    
    def __init__(self):
        """Initialize the AI processor with Gemini API."""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
    def generate_summary(self, content: str, max_length: int = 200) -> Optional[str]:
        """
        Generate a concise summary of the article content.
        
        Args:
            content: The article content to summarize
            max_length: Maximum length of the summary
            
        Returns:
            Generated summary or None if failed
        """
        try:
            prompt = f"""
            Summarize the following Singapore news article in {max_length} characters or less.
            Focus on the key facts and main points. Write in a clear, objective tone.
            
            Article content:
            {content}
            
            Summary:
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None
    
    def calculate_relevance_score(self, article: Dict, user_profile: Dict) -> float:
        """
        Calculate relevance score for an article based on user profile.
        
        Args:
            article: Article data containing title, content, summary
            user_profile: User profile with preferences
            
        Returns:
            Relevance score between 0 and 100
        """
        try:
            # Extract user interests and avoid topics
            interests = user_profile.get('profile_q2_answer', '').lower()
            avoid_topics = user_profile.get('profile_q3_answer', '').lower()
            
            # Prepare content for analysis
            title = article.get('title', '').lower()
            summary = article.get('summary', '').lower()
            content = article.get('content', '').lower()
            
            score = 50  # Base score
            
            # Check for interest keywords
            if interests:
                interest_keywords = [word.strip() for word in interests.split(',') if word.strip()]
                for keyword in interest_keywords:
                    if keyword in title or keyword in summary or keyword in content:
                        score += 10
            
            # Check for avoid keywords
            if avoid_topics:
                avoid_keywords = [word.strip() for word in avoid_topics.split(',') if word.strip()]
                for keyword in avoid_keywords:
                    if keyword in title or keyword in summary or keyword in content:
                        score -= 15
            
            # Ensure score is within bounds
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error calculating relevance score: {e}")
            return 50.0  # Default neutral score
    
    def generate_relevance_explanation(self, article: Dict, user_profile: Dict) -> Optional[str]:
        """
        Generate an explanation of why an article is relevant to the user.
        
        Args:
            article: Article data
            user_profile: User profile with preferences
            
        Returns:
            AI-generated explanation or None if failed
        """
        try:
            prompt = f"""
            Explain in one sentence why this Singapore news article might be relevant to a user with these interests: {user_profile.get('profile_q2_answer', 'General news')}
            
            Article title: {article.get('title', '')}
            Article summary: {article.get('summary', '')}
            
            Write a brief, engaging explanation that highlights the connection to the user's interests.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating relevance explanation: {e}")
            return None
    
    def categorize_article(self, content: str) -> Optional[str]:
        """
        Categorize the article into predefined categories.
        
        Args:
            content: Article content
            
        Returns:
            Category name or None if failed
        """
        try:
            categories = [
                "politics", "economy", "society", "technology", "health", 
                "education", "transport", "housing", "environment", "culture", "sports"
            ]
            
            prompt = f"""
            Categorize this Singapore news article into one of these categories:
            {', '.join(categories)}
            
            Article content: {content[:500]}...
            
            Return only the category name, nothing else.
            """
            
            response = self.model.generate_content(prompt)
            category = response.text.strip().lower()
            
            if category in categories:
                return category
            else:
                return "general"
                
        except Exception as e:
            logger.error(f"Error categorizing article: {e}")
            return "general"
    
    def process_article(self, article: Dict, user_profile: Optional[Dict] = None) -> Dict:
        """
        Process an article with AI enhancements.
        
        Args:
            article: Article data
            user_profile: Optional user profile for personalization
            
        Returns:
            Enhanced article data
        """
        processed_article = article.copy()
        
        # Generate summary if not present
        if not processed_article.get('summary') and processed_article.get('content'):
            summary = self.generate_summary(processed_article['content'])
            if summary:
                processed_article['summary'] = summary
        
        # Categorize article
        if not processed_article.get('category') and processed_article.get('content'):
            category = self.categorize_article(processed_article['content'])
            if category:
                processed_article['category'] = category
        
        # Calculate relevance score if user profile provided
        if user_profile:
            relevance_score = self.calculate_relevance_score(processed_article, user_profile)
            processed_article['relevance_score'] = relevance_score
            
            # Generate relevance explanation
            explanation = self.generate_relevance_explanation(processed_article, user_profile)
            if explanation:
                processed_article['relevance_explanation'] = explanation
        
        return processed_article 