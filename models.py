from datetime import datetime
from app import db

class MarketData(db.Model):
    """Model for storing market price data"""
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    open_price = db.Column(db.Float)
    high_price = db.Column(db.Float)
    low_price = db.Column(db.Float)
    close_price = db.Column(db.Float)
    volume = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MarketData {self.symbol} @ {self.timestamp}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "open": self.open_price,
            "high": self.high_price,
            "low": self.low_price,
            "close": self.close_price,
            "volume": self.volume
        }

class TechnicalIndicator(db.Model):
    """Model for storing calculated technical indicators"""
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    indicator_type = db.Column(db.String(20), nullable=False, index=True)  # e.g., RSI, MACD, SMA
    value = db.Column(db.Float)
    parameters = db.Column(db.String(100))  # JSON string with params like period, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TechnicalIndicator {self.indicator_type} for {self.symbol} @ {self.timestamp}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "indicator_type": self.indicator_type,
            "value": self.value,
            "parameters": self.parameters
        }

class NewsArticle(db.Model):
    """Model for storing financial news articles"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    source = db.Column(db.String(100))
    url = db.Column(db.String(512))
    published_at = db.Column(db.DateTime, index=True)
    content = db.Column(db.Text)
    symbols = db.Column(db.String(100))  # Related symbols as comma-separated values
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<NewsArticle {self.title[:30]}... @ {self.published_at}>"

class SentimentAnalysis(db.Model):
    """Model for storing sentiment analysis results"""
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news_article.id'), nullable=False)
    sentiment_score = db.Column(db.Float)  # Range: -1.0 (negative) to 1.0 (positive)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    news = db.relationship('NewsArticle', backref=db.backref('sentiment', lazy=True))
    
    def __repr__(self):
        return f"<SentimentAnalysis {self.sentiment_score} for news {self.news_id}>"

class Report(db.Model):
    """Model for storing generated reports"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    symbols = db.Column(db.String(100))  # Symbols included in the report
    report_type = db.Column(db.String(50))  # e.g., technical_analysis, sentiment, comprehensive
    content_html = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Report {self.title} - {self.report_type} @ {self.created_at}>"
