import logging
import requests
from bs4 import BeautifulSoup
import trafilatura
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def get_website_text_content(url: str) -> str:
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and easier to understand.
    
    Args:
        url (str): URL of the website to scrape
        
    Returns:
        str: Extracted text content from the website
    """
    # Send a request to the website
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            return text if text else "No content could be extracted from the page."
        else:
            return "Failed to download the page."
    except Exception as e:
        logger.error(f"Error extracting text from {url}: {str(e)}")
        return f"Error extracting text: {str(e)}"

def scrape_financial_news(symbol: str) -> list:
    """
    Scrape financial news related to a stock symbol
    
    Args:
        symbol (str): Stock symbol to search for
        
    Returns:
        list: List of news article dictionaries
    """
    try:
        # In a real implementation, this would scrape from financial news websites
        # For now, we'll return a placeholder message
        logger.info(f"Scraping financial news for {symbol}")
        
        return [{
            "title": f"Latest financial news for {symbol}",
            "source": "Web Scraper",
            "url": "",
            "published_at": None,
            "content": f"This is a placeholder for scraped news content about {symbol}. In a production environment, this would contain actual news scraped from financial websites."
        }]
    except Exception as e:
        logger.error(f"Error scraping financial news for {symbol}: {str(e)}")
        return []

def is_valid_url(url: str) -> bool:
    """
    Check if a URL is valid
    
    Args:
        url (str): URL to check
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception as e:
        logger.error(f"Error validating URL {url}: {str(e)}")
        return False

def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    try:
        if not text:
            return ""
            
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    except Exception as e:
        logger.error(f"Error cleaning text: {str(e)}")
        return text if text else ""
