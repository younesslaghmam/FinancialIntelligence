import logging
from datetime import datetime, timedelta
from app import db
from models import MarketData, TechnicalIndicator, NewsArticle, SentimentAnalysis, Report

logger = logging.getLogger(__name__)

def clean_old_data(days=30):
    """
    Clean up old data from the database that's older than specified days
    
    Args:
        days (int): Days to keep data for
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Delete old market data
        old_market_data = MarketData.query.filter(MarketData.timestamp < cutoff_date).all()
        for data in old_market_data:
            db.session.delete(data)
        
        # Delete old technical indicators
        old_indicators = TechnicalIndicator.query.filter(TechnicalIndicator.timestamp < cutoff_date).all()
        for indicator in old_indicators:
            db.session.delete(indicator)
        
        # Delete old news articles
        old_news = NewsArticle.query.filter(NewsArticle.published_at < cutoff_date).all()
        for news in old_news:
            db.session.delete(news)
        
        # Commit changes
        db.session.commit()
        logger.info(f"Cleaned up database data older than {days} days")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error cleaning old data: {str(e)}")

def get_unique_symbols():
    """
    Get list of unique symbols in the database
    
    Returns:
        list: List of unique symbols
    """
    try:
        # Get symbols from market data
        market_symbols = db.session.query(MarketData.symbol).distinct().all()
        market_symbols = [symbol[0] for symbol in market_symbols]
        
        # Get symbols from technical indicators
        indicator_symbols = db.session.query(TechnicalIndicator.symbol).distinct().all()
        indicator_symbols = [symbol[0] for symbol in indicator_symbols]
        
        # Combine and remove duplicates
        all_symbols = set(market_symbols + indicator_symbols)
        
        return sorted(list(all_symbols))
        
    except Exception as e:
        logger.error(f"Error getting unique symbols: {str(e)}")
        return []

def get_database_stats():
    """
    Get database statistics
    
    Returns:
        dict: Database statistics
    """
    try:
        # Count records in each table
        market_data_count = db.session.query(MarketData).count()
        indicator_count = db.session.query(TechnicalIndicator).count()
        news_count = db.session.query(NewsArticle).count()
        sentiment_count = db.session.query(SentimentAnalysis).count()
        report_count = db.session.query(Report).count()
        
        # Get unique symbols
        symbols = get_unique_symbols()
        
        # Get the newest and oldest data points
        newest_data = db.session.query(MarketData).order_by(MarketData.timestamp.desc()).first()
        oldest_data = db.session.query(MarketData).order_by(MarketData.timestamp.asc()).first()
        
        return {
            'market_data_count': market_data_count,
            'indicator_count': indicator_count,
            'news_count': news_count,
            'sentiment_count': sentiment_count,
            'report_count': report_count,
            'symbol_count': len(symbols),
            'symbols': symbols[:10],  # First 10 symbols
            'newest_data': newest_data.timestamp if newest_data else None,
            'oldest_data': oldest_data.timestamp if oldest_data else None
        }
        
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        return {
            'error': str(e)
        }
