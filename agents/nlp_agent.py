import logging
import os
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
# Using only NLTK for sentiment analysis to avoid dependency on transformers
from app import db
from models import SentimentAnalysis

logger = logging.getLogger(__name__)

class NLPAgent:
    """
    Agent responsible for natural language processing tasks,
    including sentiment analysis of financial news.
    """
    
    def __init__(self):
        """Initialize the NLP agent with sentiment analysis models"""
        logger.info("Initializing NLP Agent")
        
        # Initialize NLTK's VADER for basic sentiment analysis
        try:
            nltk.download('vader_lexicon', quiet=True)
            self.vader = SentimentIntensityAnalyzer()
            logger.info("VADER sentiment analyzer initialized")
        except Exception as e:
            logger.error(f"Error initializing VADER: {str(e)}")
            self.vader = None
        
        # We're using only NLTK VADER for sentiment analysis
        self.sentiment_pipeline = None
    
    def analyze_sentiment(self, news_articles):
        """
        Analyze sentiment of news articles
        
        Args:
            news_articles (list): List of news article dictionaries
            
        Returns:
            list: List of sentiment analysis results
        """
        logger.info(f"Analyzing sentiment for {len(news_articles)} news articles")
        
        results = []
        
        for article in news_articles:
            try:
                article_id = article.get('id')
                title = article.get('title', '')
                content = article.get('content', '')
                
                # Check if we already have a sentiment analysis for this article
                existing = SentimentAnalysis.query.filter_by(news_id=article_id).first()
                
                if existing:
                    logger.info(f"Using cached sentiment analysis for article {article_id}")
                    results.append({
                        'news_id': article_id,
                        'title': title,
                        'sentiment_score': existing.sentiment_score,
                        'sentiment_label': self._score_to_label(existing.sentiment_score)
                    })
                    continue
                
                # Combine title and content for better analysis
                text = f"{title} {content}"
                
                # Get sentiment score
                sentiment_score = self._get_sentiment_score(text)
                
                # Store in database
                sentiment = SentimentAnalysis(
                    news_id=article_id,
                    sentiment_score=sentiment_score
                )
                db.session.add(sentiment)
                db.session.commit()
                
                # Add to results
                results.append({
                    'news_id': article_id,
                    'title': title,
                    'sentiment_score': sentiment_score,
                    'sentiment_label': self._score_to_label(sentiment_score)
                })
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error analyzing sentiment: {str(e)}")
        
        return results
    
    def _get_sentiment_score(self, text):
        """
        Get sentiment score using VADER model
        
        Args:
            text (str): Text to analyze
            
        Returns:
            float: Sentiment score between -1.0 (negative) and 1.0 (positive)
        """
        try:
            # Use VADER for sentiment analysis
            if self.vader is not None:
                scores = self.vader.polarity_scores(text)
                return scores['compound']  # compound score between -1 and 1
            
            # No models available
            else:
                logger.warning("No sentiment analysis models available")
                return 0.0
                
        except Exception as e:
            logger.error(f"Error getting sentiment score: {str(e)}")
            return 0.0
    
    def _score_to_label(self, score):
        """
        Convert sentiment score to human-readable label
        
        Args:
            score (float): Sentiment score
            
        Returns:
            str: Sentiment label
        """
        if score >= 0.05:
            return "Positive"
        elif score <= -0.05:
            return "Negative"
        else:
            return "Neutral"
