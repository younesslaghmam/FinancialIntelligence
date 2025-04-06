import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

def parse_date(date_str, default_days=30):
    """
    Parse date string to datetime object
    
    Args:
        date_str (str): Date string in YYYY-MM-DD format
        default_days (int): Default days ago if date_str is None
        
    Returns:
        datetime: Parsed date
    """
    try:
        if date_str:
            return datetime.strptime(date_str, '%Y-%m-%d')
        else:
            return datetime.now() - timedelta(days=default_days)
    except Exception as e:
        logger.error(f"Error parsing date {date_str}: {str(e)}")
        return datetime.now() - timedelta(days=default_days)

def format_currency(value, currency='$'):
    """
    Format value as currency
    
    Args:
        value (float): Value to format
        currency (str): Currency symbol
        
    Returns:
        str: Formatted currency string
    """
    try:
        return f"{currency}{value:,.2f}"
    except Exception as e:
        logger.error(f"Error formatting currency: {str(e)}")
        return f"{currency}0.00"

def get_indicator_full_name(indicator_code):
    """
    Get full name of technical indicator from code
    
    Args:
        indicator_code (str): Indicator code
        
    Returns:
        str: Full name of indicator
    """
    indicator_names = {
        'SMA': 'Simple Moving Average',
        'EMA': 'Exponential Moving Average',
        'RSI': 'Relative Strength Index',
        'MACD': 'Moving Average Convergence Divergence',
        'BBANDS': 'Bollinger Bands',
        'ATR': 'Average True Range',
        'OBV': 'On-Balance Volume',
        'ADX': 'Average Directional Index',
        'STOCH': 'Stochastic Oscillator',
        'ROC': 'Rate of Change'
    }
    
    return indicator_names.get(indicator_code.upper(), indicator_code)

def split_list_into_chunks(items, chunk_size=3):
    """
    Split a list into chunks
    
    Args:
        items (list): List to split
        chunk_size (int): Size of each chunk
        
    Returns:
        list: List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

def safe_json_loads(json_str, default=None):
    """
    Safely load JSON string
    
    Args:
        json_str (str): JSON string to load
        default (any): Default value if loading fails
        
    Returns:
        any: Loaded JSON data or default
    """
    try:
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"Error loading JSON: {str(e)}")
        return default if default is not None else {}
