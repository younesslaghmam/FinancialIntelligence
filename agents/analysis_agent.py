import logging
import pandas as pd
import numpy as np
import json
from datetime import datetime
from app import db
from models import TechnicalIndicator

logger = logging.getLogger(__name__)

class AnalysisAgent:
    """
    Agent responsible for performing technical and fundamental analysis
    on financial data. Calculates various technical indicators and ratios.
    """
    
    def __init__(self):
        """Initialize the analysis agent"""
        logger.info("Analysis Agent initialized")
    
    def calculate_indicators(self, market_data, indicators=None, params=None):
        """
        Calculate technical indicators for market data
        
        Args:
            market_data (list): List of market data records
            indicators (list): List of indicators to calculate
            params (dict): Parameters for indicators
            
        Returns:
            dict: Dictionary with calculated indicators
        """
        logger.info(f"Calculating indicators: {indicators}")
        
        if not indicators:
            indicators = ['SMA', 'EMA', 'RSI', 'MACD', 'BBANDS']
        
        if not params:
            params = {}
        elif isinstance(params, str):
            try:
                params = json.loads(params)
            except:
                params = {}
        
        # Convert market data to pandas DataFrame for easier calculations
        df = self._convert_to_dataframe(market_data)
        
        if df.empty:
            logger.warning("Empty market data, can't calculate indicators")
            return {indicator: [] for indicator in indicators}
        
        # Calculate each requested indicator
        results = {}
        
        for indicator in indicators:
            indicator = indicator.upper()
            
            if indicator == 'SMA':
                results[indicator] = self._calculate_sma(df, params.get('sma_period', 20))
            elif indicator == 'EMA':
                results[indicator] = self._calculate_ema(df, params.get('ema_period', 20))
            elif indicator == 'RSI':
                results[indicator] = self._calculate_rsi(df, params.get('rsi_period', 14))
            elif indicator == 'MACD':
                results[indicator] = self._calculate_macd(
                    df, 
                    params.get('macd_fast_period', 12),
                    params.get('macd_slow_period', 26),
                    params.get('macd_signal_period', 9)
                )
            elif indicator == 'BBANDS':
                results[indicator] = self._calculate_bollinger_bands(
                    df, 
                    params.get('bb_period', 20),
                    params.get('bb_std_dev', 2)
                )
        
        return results
    
    def _convert_to_dataframe(self, market_data):
        """Convert market data list to pandas DataFrame"""
        if not market_data:
            return pd.DataFrame()
        
        # If market_data is already a DataFrame, return it
        if isinstance(market_data, pd.DataFrame):
            return market_data
        
        # Convert list of dictionaries to DataFrame
        df = pd.DataFrame(market_data)
        
        # Ensure we have the required columns
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        
        # Map column names if they're different
        column_mapping = {
            'timestamp': 'timestamp',
            'open_price': 'open',
            'high_price': 'high',
            'low_price': 'low',
            'close_price': 'close',
            'volume': 'volume'
        }
        
        # Rename columns if needed
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns and new_name not in df.columns:
                df[new_name] = df[old_name]
        
        # Check if we have all required columns
        for col in required_columns:
            if col not in df.columns:
                logger.error(f"Required column {col} not found in market data")
                return pd.DataFrame()
        
        # Set timestamp as index
        if 'timestamp' in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)
        
        return df
    
    def _calculate_sma(self, df, period=20):
        """
        Calculate Simple Moving Average
        
        Args:
            df (DataFrame): Market data
            period (int): Period for SMA calculation
            
        Returns:
            list: SMA values as dictionaries
        """
        try:
            symbol = df['symbol'].iloc[0] if 'symbol' in df.columns else 'Unknown'
            
            # Calculate SMA
            sma = df['close'].rolling(window=period).mean()
            
            # Convert to list of dictionaries
            result = []
            for idx, value in sma.items():
                if not np.isnan(value):
                    data_point = {
                        "timestamp": idx.to_pydatetime(),
                        "value": value,
                        "indicator_type": "SMA",
                        "symbol": symbol,
                        "parameters": json.dumps({"period": period})
                    }
                    result.append(data_point)
                    
                    # Store in database
                    self._store_indicator(data_point)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating SMA: {str(e)}")
            return []
    
    def _calculate_ema(self, df, period=20):
        """
        Calculate Exponential Moving Average
        
        Args:
            df (DataFrame): Market data
            period (int): Period for EMA calculation
            
        Returns:
            list: EMA values as dictionaries
        """
        try:
            symbol = df['symbol'].iloc[0] if 'symbol' in df.columns else 'Unknown'
            
            # Calculate EMA
            ema = df['close'].ewm(span=period, adjust=False).mean()
            
            # Convert to list of dictionaries
            result = []
            for idx, value in ema.items():
                if not np.isnan(value):
                    data_point = {
                        "timestamp": idx.to_pydatetime(),
                        "value": value,
                        "indicator_type": "EMA",
                        "symbol": symbol,
                        "parameters": json.dumps({"period": period})
                    }
                    result.append(data_point)
                    
                    # Store in database
                    self._store_indicator(data_point)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating EMA: {str(e)}")
            return []
    
    def _calculate_rsi(self, df, period=14):
        """
        Calculate Relative Strength Index
        
        Args:
            df (DataFrame): Market data
            period (int): Period for RSI calculation
            
        Returns:
            list: RSI values as dictionaries
        """
        try:
            symbol = df['symbol'].iloc[0] if 'symbol' in df.columns else 'Unknown'
            
            # Calculate RSI
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            # Convert to list of dictionaries
            result = []
            for idx, value in rsi.items():
                if not np.isnan(value):
                    data_point = {
                        "timestamp": idx.to_pydatetime(),
                        "value": value,
                        "indicator_type": "RSI",
                        "symbol": symbol,
                        "parameters": json.dumps({"period": period})
                    }
                    result.append(data_point)
                    
                    # Store in database
                    self._store_indicator(data_point)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {str(e)}")
            return []
    
    def _calculate_macd(self, df, fast_period=12, slow_period=26, signal_period=9):
        """
        Calculate Moving Average Convergence Divergence
        
        Args:
            df (DataFrame): Market data
            fast_period (int): Fast period for MACD
            slow_period (int): Slow period for MACD
            signal_period (int): Signal period for MACD
            
        Returns:
            list: MACD values as dictionaries
        """
        try:
            symbol = df['symbol'].iloc[0] if 'symbol' in df.columns else 'Unknown'
            
            # Calculate MACD
            exp1 = df['close'].ewm(span=fast_period, adjust=False).mean()
            exp2 = df['close'].ewm(span=slow_period, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=signal_period, adjust=False).mean()
            histogram = macd - signal
            
            # Convert to list of dictionaries
            result = []
            for idx in macd.index:
                macd_val = macd[idx]
                signal_val = signal[idx]
                hist_val = histogram[idx]
                
                if not (np.isnan(macd_val) or np.isnan(signal_val) or np.isnan(hist_val)):
                    data_point = {
                        "timestamp": idx.to_pydatetime(),
                        "value": float(macd_val),  # Convert numpy float to Python float
                        "signal": float(signal_val),
                        "histogram": float(hist_val),
                        "indicator_type": "MACD",
                        "symbol": symbol,
                        "parameters": json.dumps({
                            "fast_period": fast_period, 
                            "slow_period": slow_period,
                            "signal_period": signal_period
                        })
                    }
                    result.append(data_point)
                    
                    # Store in database
                    self._store_indicator(data_point)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating MACD: {str(e)}")
            return []
    
    def _calculate_bollinger_bands(self, df, period=20, std_dev=2):
        """
        Calculate Bollinger Bands
        
        Args:
            df (DataFrame): Market data
            period (int): Period for Bollinger Bands
            std_dev (float): Standard deviation multiplier
            
        Returns:
            list: Bollinger Bands values as dictionaries
        """
        try:
            symbol = df['symbol'].iloc[0] if 'symbol' in df.columns else 'Unknown'
            
            # Calculate Bollinger Bands
            middle_band = df['close'].rolling(window=period).mean()
            std = df['close'].rolling(window=period).std()
            
            upper_band = middle_band + (std * std_dev)
            lower_band = middle_band - (std * std_dev)
            
            # Convert to list of dictionaries
            result = []
            for idx in middle_band.index:
                middle = middle_band[idx]
                upper = upper_band[idx]
                lower = lower_band[idx]
                
                if not (np.isnan(middle) or np.isnan(upper) or np.isnan(lower)):
                    data_point = {
                        "timestamp": idx.to_pydatetime(),
                        "middle": float(middle),  # Convert numpy float to Python float
                        "upper": float(upper),
                        "lower": float(lower),
                        "indicator_type": "BBANDS",
                        "symbol": symbol,
                        "parameters": json.dumps({"period": period, "std_dev": std_dev})
                    }
                    result.append(data_point)
                    
                    # Store in database
                    self._store_indicator(data_point)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {str(e)}")
            return []
    
    def _store_indicator(self, indicator_data):
        """Store technical indicator in the database"""
        try:
            # Check if this indicator already exists
            existing = TechnicalIndicator.query.filter_by(
                symbol=indicator_data["symbol"],
                timestamp=indicator_data["timestamp"],
                indicator_type=indicator_data["indicator_type"],
                parameters=indicator_data["parameters"]
            ).first()
            
            if existing:
                # Update existing record
                if "value" in indicator_data:
                    # Convert numpy.float64 to native Python float if needed
                    if hasattr(indicator_data["value"], "item"):
                        existing.value = float(indicator_data["value"])
                    else:
                        existing.value = indicator_data["value"]
                db.session.commit()
                return
            
            # Create new record
            indicator = TechnicalIndicator(
                symbol=indicator_data["symbol"],
                timestamp=indicator_data["timestamp"],
                indicator_type=indicator_data["indicator_type"],
                parameters=indicator_data["parameters"]
            )
            
            if "value" in indicator_data:
                # Convert numpy.float64 to native Python float if needed
                if hasattr(indicator_data["value"], "item"):
                    indicator.value = float(indicator_data["value"])
                else:
                    indicator.value = indicator_data["value"]
            
            db.session.add(indicator)
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error storing indicator: {str(e)}")
