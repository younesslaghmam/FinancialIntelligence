"""
Database cleanup utility for Financial AI Platform
This script clears all data from the database tables while preserving the table structure.
"""

import os
import logging
from app import app, db
from models import MarketData, TechnicalIndicator, NewsArticle, SentimentAnalysis, Report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_database():
    """Delete all records from all database tables"""
    with app.app_context():
        try:
            # Delete records from each table in an order that respects foreign keys
            logger.info("Deleting all sentiment analysis records...")
            SentimentAnalysis.query.delete()
            
            logger.info("Deleting all news article records...")
            NewsArticle.query.delete()
            
            logger.info("Deleting all technical indicator records...")
            TechnicalIndicator.query.delete()
            
            logger.info("Deleting all market data records...")
            MarketData.query.delete()
            
            logger.info("Deleting all report records...")
            Report.query.delete()
            
            # Commit the transaction
            db.session.commit()
            logger.info("Database cleaned successfully!")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error cleaning database: {str(e)}")
            raise

if __name__ == "__main__":
    clean_database()