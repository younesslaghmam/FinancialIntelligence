import logging
import os
import pandas as pd
import requests
from datetime import datetime, timedelta
import yfinance as yf
from app import db
from models import MarketData, NewsArticle
from utils.web_scraper import get_website_text_content

logger = logging.getLogger(__name__)

class DataAgent:
    """
    Agent responsible for retrieving financial data from external sources
    and storing it in the database for further analysis.
    """
    
    def __init__(self):
        """Initialize the data agent with API keys"""
        self.alpha_vantage_api_key = os.environ.get("ALPHA_VANTAGE_API_KEY", "demo")
        logger.info("Data Agent initialized")
    
    def fetch_historical_data(self, symbol, start_date, end_date):
        """
        Fetch historical market data for a symbol
        
        Args:
            symbol (str): Stock symbol
            start_date (datetime): Start date
            end_date (datetime): End date
            
        Returns:
            list: List of market data records
        """
        logger.info(f"Fetching historical data for {symbol} from {start_date} to {end_date}")
        
        try:
            # Try first with yfinance
            data = self._fetch_from_yfinance(symbol, start_date, end_date)
            
            # If yfinance fails, try Alpha Vantage
            if not data:
                data = self._fetch_from_alpha_vantage(symbol, start_date, end_date)
                
            # Store data in the database
            self._store_market_data(data, symbol)
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            raise Exception(f"Failed to retrieve data for {symbol}: {str(e)}")
    
    def _fetch_from_yfinance(self, symbol, start_date, end_date):
        """Fetch data from Yahoo Finance API"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            
            if df.empty:
                logger.warning(f"No data returned from Yahoo Finance for {symbol}")
                return []
            
            # Convert to list of dictionaries format
            result = []
            for index, row in df.iterrows():
                result.append({
                    "symbol": symbol,
                    "timestamp": index.to_pydatetime(),
                    "open": row['Open'],
                    "high": row['High'],
                    "low": row['Low'],
                    "close": row['Close'],
                    "volume": row['Volume']
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching from Yahoo Finance: {str(e)}")
            return []
    
    def _fetch_from_alpha_vantage(self, symbol, start_date, end_date):
        """Fetch data from Alpha Vantage API"""
        try:
            base_url = "https://www.alphavantage.co/query"
            
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": self.alpha_vantage_api_key,
                "outputsize": "full"
            }
            
            response = requests.get(base_url, params=params, verify=False)
            
            if response.status_code != 200:
                logger.error(f"Alpha Vantage API error: {response.status_code}")
                return []
            
            data = response.json()
            
            if "Error Message" in data:
                logger.error(f"Alpha Vantage API error: {data['Error Message']}")
                return []
            
            if "Time Series (Daily)" not in data:
                logger.error("Unexpected Alpha Vantage API response format")
                return []
            
            time_series = data["Time Series (Daily)"]
            
            result = []
            for date_str, values in time_series.items():
                date = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Only include data within our date range
                if start_date <= date <= end_date:
                    result.append({
                        "symbol": symbol,
                        "timestamp": date,
                        "open": float(values["1. open"]),
                        "high": float(values["2. high"]),
                        "low": float(values["3. low"]),
                        "close": float(values["4. close"]),
                        "volume": int(values["5. volume"])
                    })
            
            # Sort by date
            result.sort(key=lambda x: x["timestamp"])
            return result
            
        except Exception as e:
            logger.error(f"Error fetching from Alpha Vantage: {str(e)}")
            return []
    
    def _store_market_data(self, data, symbol):
        """Store market data in the database"""
        try:
            # Get existing data timestamps to avoid duplicates
            existing_timestamps = set()
            existing_records = MarketData.query.filter_by(symbol=symbol).all()
            for record in existing_records:
                existing_timestamps.add(record.timestamp.strftime("%Y-%m-%d"))
            
            # Add new records
            for item in data:
                timestamp_str = item["timestamp"].strftime("%Y-%m-%d")
                if timestamp_str not in existing_timestamps:
                    record = MarketData(
                        symbol=symbol,
                        timestamp=item["timestamp"],
                        open_price=item["open"],
                        high_price=item["high"],
                        low_price=item["low"],
                        close_price=item["close"],
                        volume=item["volume"]
                    )
                    db.session.add(record)
            
            db.session.commit()
            logger.info(f"Stored {len(data)} market data records for {symbol}")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error storing market data: {str(e)}")
    
    def fetch_news(self, symbol, days=7):
        """
        Fetch news articles related to a symbol
        
        Args:
            symbol (str): Stock symbol
            days (int): Number of days of news to fetch
            
        Returns:
            list: List of news article records
        """
        logger.info(f"Fetching news for {symbol} over past {days} days")
        
        try:
            # Check for existing news articles in our database
            start_date = datetime.now() - timedelta(days=days)
            existing_news = NewsArticle.query.filter(
                NewsArticle.symbols.contains(symbol),
                NewsArticle.published_at >= start_date
            ).all()
            
            if len(existing_news) >= 5:  # If we have enough articles
                logger.info(f"Using {len(existing_news)} cached news articles for {symbol}")
                return [self._news_to_dict(article) for article in existing_news]
            
            # If we don't have enough cached news, fetch from Alpha Vantage News API
            news_articles = self._fetch_news_from_alpha_vantage(symbol, days)
            
            # If Alpha Vantage didn't return enough articles, try to fetch from Financial Modeling Prep (free tier)
            if len(news_articles) < 5:
                news_articles += self._fetch_news_from_alternative_source(symbol, days)
            
            return news_articles
            
        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            raise Exception(f"Failed to retrieve news for {symbol}: {str(e)}")
    
    def _fetch_news_from_alpha_vantage(self, symbol, days):
        """Fetch news from Alpha Vantage API"""
        try:
            base_url = "https://www.alphavantage.co/query"
            
            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": symbol,
                "apikey": self.alpha_vantage_api_key,
                "limit": 50  # Get more articles to filter by date
            }
            
            response = requests.get(base_url, params=params, verify=False)
            
            if response.status_code != 200:
                logger.error(f"Alpha Vantage News API error: {response.status_code}")
                return []
            
            data = response.json()
            
            if "feed" not in data:
                logger.error("Unexpected Alpha Vantage News API response format")
                return []
            
            start_date = datetime.now() - timedelta(days=days)
            result = []
            
            for article in data["feed"]:
                # Parse the time
                time_published = datetime.strptime(article["time_published"][:19], "%Y%m%dT%H%M%S")
                
                # Only include articles within our date range
                if time_published >= start_date:
                    # Store in database
                    db_article = NewsArticle(
                        title=article["title"],
                        source=article.get("source", "Alpha Vantage"),
                        url=article.get("url", ""),
                        published_at=time_published,
                        content=article.get("summary", ""),
                        symbols=symbol
                    )
                    db.session.add(db_article)
                    db.session.commit()
                    
                    # Add to result
                    result.append(self._news_to_dict(db_article))
            
            logger.info(f"Fetched {len(result)} news articles from Alpha Vantage for {symbol}")
            return result
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error fetching news from Alpha Vantage: {str(e)}")
            return []
    
    def _fetch_news_from_alternative_source(self, symbol, days):
        """
        Fetch news from an alternative source 
        (simulates scraping from financial websites)
        """
        # In a real implementation, this would use web scraping to get news
        # from financial websites like MarketWatch, Yahoo Finance, etc.
        # For this implementation, we'll just add a placeholder message.
        logger.info(f"Using web_scraper to get news for {symbol}")
        try:
            # Create a placeholder article for demonstration
            article = NewsArticle(
                title=f"Latest financial news for {symbol}",
                source="Financial Web Scraper",
                url="",
                published_at=datetime.now(),
                content=f"This is a placeholder for scraped news content about {symbol}. In a production environment, this would contain actual news scraped from financial websites.",
                symbols=symbol
            )
            db.session.add(article)
            db.session.commit()
            
            return [self._news_to_dict(article)]
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating alternative news source: {str(e)}")
            return []
    
    def _news_to_dict(self, news_article):
        """Convert a NewsArticle model to a dictionary"""
        return {
            "id": news_article.id,
            "title": news_article.title,
            "source": news_article.source,
            "url": news_article.url,
            "published_at": news_article.published_at.isoformat() if news_article.published_at else None,
            "content": news_article.content,
            "symbols": news_article.symbols
        }
