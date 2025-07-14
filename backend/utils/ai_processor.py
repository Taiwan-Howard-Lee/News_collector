import google.generativeai as genai
import logging
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/.env')

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
        Generate a concise summary of the resource content.
        Args:
            content: The resource content to summarize
            max_length: Maximum length of the summary
        Returns:
            Generated summary or None if failed
        """
        try:
            prompt = f"""
            Summarize the following information resource in {max_length} characters or less.
            Focus on the key facts and main points. Write in a clear, objective tone.

            Resource content:
            {content}

            Summary:
            """
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None

    async def generate_comment_response(self, article_title: str, article_summary: str, user_comment: str) -> Optional[str]:
        """
        Generate an AI response to a user comment on an article.
        Args:
            article_title: Title of the article
            article_summary: Summary of the article
            user_comment: User's comment to respond to
        Returns:
            AI-generated response or None if failed
        """
        try:
            prompt = f"""
            You are an AI assistant for a Singapore news platform. A user has commented on an article.
            Provide a helpful, informative, and engaging response that adds value to the discussion.

            Article Title: {article_title}
            Article Summary: {article_summary}

            User Comment: {user_comment}

            Guidelines:
            - Be conversational and friendly
            - Provide additional context or insights related to the article
            - Ask thoughtful follow-up questions if appropriate
            - Keep response under 200 characters for Instagram-style format
            - Focus on Singapore context when relevant
            - Be objective and balanced

            AI Response:
            """
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating comment response: {e}")
            return None
    
    def calculate_relevance_score(self, resource: Dict, user_profile: Dict) -> float:
        """
        Calculate relevance score for a resource based on user profile.
        Args:
            resource: Resource data containing title, content, summary
            user_profile: User profile with preferences
        Returns:
            Relevance score between 0 and 100
        """
        try:
            interests = user_profile.get('profile_q2_answer', '').lower()
            avoid_topics = user_profile.get('profile_q3_answer', '').lower()
            title = resource.get('title', '').lower()
            summary = resource.get('summary', '').lower()
            content = resource.get('content', '').lower()
            score = 50  # Base score
            if interests:
                interest_keywords = [word.strip() for word in interests.split(',') if word.strip()]
                for keyword in interest_keywords:
                    if keyword in title or keyword in summary or keyword in content:
                        score += 10
            if avoid_topics:
                avoid_keywords = [word.strip() for word in avoid_topics.split(',') if word.strip()]
                for keyword in avoid_keywords:
                    if keyword in title or keyword in summary or keyword in content:
                        score -= 15
            return max(0, min(100, score))
        except Exception as e:
            logger.error(f"Error calculating relevance score: {e}")
            return 50.0  # Default neutral score
    
    def generate_relevance_explanation(self, resource: Dict, user_profile: Dict) -> Optional[str]:
        """
        Generate an explanation of why a resource is relevant to the user.
        Args:
            resource: Resource data
            user_profile: User profile with preferences
        Returns:
            AI-generated explanation or None if failed
        """
        try:
            prompt = f"""
            Explain in one sentence why this information resource might be relevant to a user with these interests: {user_profile.get('profile_q2_answer', 'General information')}
            Resource title: {resource.get('title', '')}
            Resource summary: {resource.get('summary', '')}
            Write a brief, engaging explanation that highlights the connection to the user's interests.
            """
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating relevance explanation: {e}")
            return None
    
    def categorize_resource(self, content: str) -> Optional[str]:
        """
        Categorize the resource into predefined categories.
        Args:
            content: Resource content
        Returns:
            Category name or None if failed
        """
        try:
            categories = [
                "politics", "economy", "society", "technology", "health", 
                "education", "transport", "housing", "environment", "culture", "sports"
            ]
            prompt = f"""
            Categorize this information resource into one of these categories:
            {', '.join(categories)}
            Resource content: {content[:500]}...
            Return only the category name, nothing else.
            """
            response = self.model.generate_content(prompt)
            category = response.text.strip().lower()
            if category in categories:
                return category
            else:
                return "general"
        except Exception as e:
            logger.error(f"Error categorizing resource: {e}")
            return "general"
    
    def process_resource(self, resource: Dict, user_profile: Optional[Dict] = None) -> Dict:
        """
        Process a resource with AI enhancements.
        Args:
            resource: Resource data
            user_profile: Optional user profile for personalization
        Returns:
            Enhanced resource data
        """
        processed_resource = resource.copy()
        if not processed_resource.get('summary') and processed_resource.get('content'):
            summary = self.generate_summary(processed_resource['content'])
            if summary:
                processed_resource['summary'] = summary
        if not processed_resource.get('category') and processed_resource.get('content'):
            category = self.categorize_resource(processed_resource['content'])
            if category:
                processed_resource['category'] = category
        if user_profile:
            relevance_score = self.calculate_relevance_score(processed_resource, user_profile)
            processed_resource['relevance_score'] = relevance_score
            explanation = self.generate_relevance_explanation(processed_resource, user_profile)
            if explanation:
                processed_resource['relevance_explanation'] = explanation
        return processed_resource

    def chat_about_article(self, user_message: str, article_context: str = "") -> Optional[str]:
        """
        Generate a conversational response about an article or general news topic.
        Args:
            user_message: User's question or comment
            article_context: Optional article context for more specific responses
        Returns:
            AI-generated conversational response
        """
        try:
            if article_context:
                prompt = f"""
                You are a knowledgeable and friendly AI assistant helping users understand Singapore news and current events.

                Article Context:
                {article_context}

                User Question/Comment: {user_message}

                Please provide a helpful, informative, and engaging response. If the user is asking about the article,
                reference specific details from it. If they're asking broader questions, provide context and insights
                about Singapore's current affairs. Keep your response conversational but informative.

                Response:
                """
            else:
                prompt = f"""
                You are a knowledgeable and friendly AI assistant specializing in Singapore news and current events.

                User Question/Comment: {user_message}

                Please provide a helpful, informative, and engaging response about Singapore news, politics, economy,
                society, or current affairs. Keep your response conversational but informative.

                Response:
                """

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            logger.error(f"Error in chat response: {e}")
            return None

    def generate_personalized_insights(self, articles: List[Dict], user_profile: Dict) -> List[Dict]:
        """
        Generate personalized insights for a list of articles based on user profile.
        Args:
            articles: List of article dictionaries
            user_profile: User profile with preferences
        Returns:
            Articles enhanced with personalized insights
        """
        try:
            enhanced_articles = []
            user_interests = user_profile.get('profile_q2_answer', '')
            user_goals = user_profile.get('profile_q1_answer', '')

            for article in articles:
                enhanced_article = article.copy()

                # Generate personalized insight
                prompt = f"""
                Based on this user's profile:
                - Goals: {user_goals}
                - Interests: {user_interests}

                And this article:
                - Title: {article.get('title', '')}
                - Summary: {article.get('summary', '')}

                Generate a brief, personalized insight (1-2 sentences) explaining why this article
                might be valuable to this specific user. Focus on actionable insights or connections
                to their goals and interests.

                Insight:
                """

                try:
                    response = self.model.generate_content(prompt)
                    enhanced_article['personalized_insight'] = response.text.strip()
                except Exception as e:
                    logger.error(f"Error generating insight for article {article.get('id', 'unknown')}: {e}")
                    enhanced_article['personalized_insight'] = None

                enhanced_articles.append(enhanced_article)

            return enhanced_articles

        except Exception as e:
            logger.error(f"Error generating personalized insights: {e}")
            return articles

    def generate_daily_briefing(self, articles: List[Dict], user_profile: Dict) -> Optional[str]:
        """
        Generate a personalized daily news briefing.
        Args:
            articles: List of today's top articles
            user_profile: User profile for personalization
        Returns:
            AI-generated daily briefing
        """
        try:
            user_interests = user_profile.get('profile_q2_answer', '')
            user_goals = user_profile.get('profile_q1_answer', '')

            # Prepare article summaries
            article_summaries = []
            for i, article in enumerate(articles[:5], 1):  # Top 5 articles
                article_summaries.append(f"{i}. {article.get('title', '')} - {article.get('summary', '')}")

            prompt = f"""
            Create a personalized daily news briefing for a user with these interests and goals:
            - Goals: {user_goals}
            - Interests: {user_interests}

            Today's top Singapore news articles:
            {chr(10).join(article_summaries)}

            Write a engaging, conversational briefing (200-300 words) that:
            1. Highlights the most relevant stories for this user
            2. Connects news to their interests and goals
            3. Provides actionable insights or implications
            4. Maintains an informative but friendly tone

            Daily Briefing:
            """

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            logger.error(f"Error generating daily briefing: {e}")
            return None

    def analyze_sentiment(self, content: str) -> Optional[Dict]:
        """
        Analyze the sentiment of article content.
        Args:
            content: Article content to analyze
        Returns:
            Sentiment analysis results
        """
        try:
            prompt = f"""
            Analyze the sentiment and tone of this news article content:

            {content[:1000]}...

            Provide analysis in this format:
            Sentiment: [Positive/Negative/Neutral]
            Confidence: [High/Medium/Low]
            Key Emotions: [list main emotions detected]
            Tone: [Professional/Casual/Urgent/etc.]

            Analysis:
            """

            response = self.model.generate_content(prompt)
            analysis_text = response.text.strip()

            # Parse the response (simplified parsing)
            lines = analysis_text.split('\n')
            result = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    result[key.strip().lower().replace(' ', '_')] = value.strip()

            return result

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return None