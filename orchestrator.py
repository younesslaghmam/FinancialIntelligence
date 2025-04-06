import logging
from datetime import datetime, timedelta
import json
from app import db
from agents.data_agent import DataAgent
from agents.analysis_agent import AnalysisAgent
from agents.nlp_agent import NLPAgent
from agents.report_agent import ReportAgent
from models import MarketData, TechnicalIndicator, NewsArticle, SentimentAnalysis, Report

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Orchestrates the workflow between different agents to perform financial analysis tasks.
    Acts as the central coordinator for the multi-agent system.
    """
    
    def __init__(self):
        """Initialize the orchestrator with all required agents"""
        self.data_agent = DataAgent()
        self.analysis_agent = AnalysisAgent()
        self.nlp_agent = NLPAgent()
        self.report_agent = ReportAgent()
        logger.info("Orchestrator initialized with all agents")
    
    def run_technical_analysis(self, symbol, start_date=None, end_date=None, indicators=None):
        """
        Run a technical analysis workflow on the specified symbol
        
        Args:
            symbol (str): Stock symbol to analyze
            start_date (str, optional): Start date for analysis in YYYY-MM-DD format
            end_date (str, optional): End date for analysis in YYYY-MM-DD format
            indicators (list, optional): List of indicators to calculate
            
        Returns:
            dict: Results of the analysis
        """
        logger.info(f"Running technical analysis for {symbol}")
        
        # Convert dates if provided
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_date = datetime.now() - timedelta(days=90)
            
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            end_date = datetime.now()
            
        if not indicators:
            indicators = ['SMA', 'EMA', 'RSI', 'MACD', 'BBANDS']
        
        # Step 1: Fetch market data using the data agent
        market_data = self.data_agent.fetch_historical_data(symbol, start_date, end_date)
        
        # Step 2: Calculate technical indicators using the analysis agent
        analysis_results = self.analysis_agent.calculate_indicators(market_data, indicators)
        
        # Return combined results
        return {
            'market_data': market_data,
            'analysis_results': analysis_results,
            'symbol': symbol,
            'start_date': start_date,
            'end_date': end_date,
            'indicators': indicators
        }
    
    def run_sentiment_analysis(self, symbol, days=7):
        """
        Run sentiment analysis for news related to the symbol
        
        Args:
            symbol (str): Stock symbol to analyze
            days (int): Number of days of news to analyze
            
        Returns:
            dict: Results of the sentiment analysis
        """
        logger.info(f"Running sentiment analysis for {symbol} over past {days} days")
        
        # Step 1: Fetch news data using the data agent
        news_articles = self.data_agent.fetch_news(symbol, days)
        
        # Step 2: Analyze sentiment using the NLP agent
        sentiment_results = self.nlp_agent.analyze_sentiment(news_articles)
        
        # Return combined results as a dictionary (not a list)
        return {
            'news_articles': news_articles,
            'sentiment_results': sentiment_results,
            'symbol': symbol,
            'days': days
        }
    
    def generate_report(self, title, symbols, report_type='comprehensive'):
        """
        Generate a comprehensive report for the specified symbols
        
        Args:
            title (str): Report title
            symbols (list): List of stock symbols to include
            report_type (str): Type of report to generate
            
        Returns:
            int: ID of the generated report
        """
        logger.info(f"Generating {report_type} report for {symbols}")
        
        report_data = {
            'title': title,
            'symbols': symbols,
            'report_type': report_type,
            'timestamp': datetime.now(),
            'sections': []
        }
        
        # Fetch data for all symbols
        for symbol in symbols:
            # Get market data
            market_data = self.data_agent.fetch_historical_data(
                symbol, 
                datetime.now() - timedelta(days=30), 
                datetime.now()
            )
            
            # Get technical analysis
            if report_type in ['technical', 'comprehensive']:
                indicators = ['SMA', 'EMA', 'RSI', 'MACD', 'BBANDS']
                analysis = self.analysis_agent.calculate_indicators(market_data, indicators)
                report_data['sections'].append({
                    'type': 'technical_analysis',
                    'symbol': symbol,
                    'data': analysis
                })
            
            # Get sentiment analysis
            if report_type in ['sentiment', 'comprehensive']:
                news = self.data_agent.fetch_news(symbol, 7)
                sentiment = self.nlp_agent.analyze_sentiment(news)
                report_data['sections'].append({
                    'type': 'sentiment_analysis',
                    'symbol': symbol,
                    'data': sentiment
                })
        
        # Generate the report using the report agent
        report_html = self.report_agent.generate_report(report_data)
        
        # Save the report to the database
        report = Report(
            title=title,
            symbols=','.join(symbols),
            report_type=report_type,
            content_html=report_html
        )
        db.session.add(report)
        db.session.commit()
        
        return report.id
    
    def get_market_data(self, symbol, days=30):
        """
        Get market data for the specified symbol
        
        Args:
            symbol (str): Stock symbol
            days (int): Number of days of data to retrieve
            
        Returns:
            list: Market data records
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Check if we have the data cached
        data = MarketData.query.filter(
            MarketData.symbol == symbol,
            MarketData.timestamp >= start_date,
            MarketData.timestamp <= end_date
        ).order_by(MarketData.timestamp).all()
        
        # If we don't have enough data, fetch it
        if len(data) < days/2:  # If we have less than half the data needed
            logger.info(f"Insufficient cached data for {symbol}, fetching from source")
            data = self.data_agent.fetch_historical_data(symbol, start_date, end_date)
        else:
            data = [d.to_dict() for d in data]
            
        return data
    
    def get_indicator_data(self, symbol, indicator, days=30, params=None):
        """
        Get technical indicator data for the specified symbol
        
        Args:
            symbol (str): Stock symbol
            indicator (str): Indicator name
            days (int): Number of days of data
            params (str): Indicator parameters as JSON string
            
        Returns:
            list: Indicator data records
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Check if we have the indicator data cached
        data = TechnicalIndicator.query.filter(
            TechnicalIndicator.symbol == symbol,
            TechnicalIndicator.indicator_type == indicator,
            TechnicalIndicator.timestamp >= start_date,
            TechnicalIndicator.timestamp <= end_date
        ).order_by(TechnicalIndicator.timestamp).all()
        
        # If we don't have enough data, calculate it
        if len(data) < days/2:  # If we have less than half the data needed
            logger.info(f"Insufficient cached indicator data for {symbol}, calculating")
            
            # Get market data first
            market_data = self.get_market_data(symbol, days)
            
            # Calculate the indicator
            data = self.analysis_agent.calculate_indicators(market_data, [indicator], params)
            data = data.get(indicator, [])
        else:
            data = [d.to_dict() for d in data]
            
        return data
