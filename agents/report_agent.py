import logging
import os
import json
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
from jinja2 import Template

logger = logging.getLogger(__name__)

class ReportAgent:
    """
    Agent responsible for generating reports with visualizations
    from financial analysis data.
    """
    
    def __init__(self):
        """Initialize the report agent"""
        logger.info("Report Agent initialized")
    
    def generate_report(self, report_data):
        """
        Generate an HTML report from analysis data
        
        Args:
            report_data (dict): Report data structure
            
        Returns:
            str: HTML report content
        """
        logger.info(f"Generating {report_data['report_type']} report for {report_data['symbols']}")
        
        # Create context for the report template
        context = {
            'title': report_data['title'],
            'timestamp': report_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'symbols': ', '.join(report_data['symbols']) if isinstance(report_data['symbols'], list) else report_data['symbols'],
            'report_type': report_data['report_type'],
            'sections': []
        }
        
        # Process each section
        for section in report_data['sections']:
            section_type = section['type']
            symbol = section['symbol']
            data = section['data']
            
            if section_type == 'technical_analysis':
                context['sections'].append(self._generate_technical_section(symbol, data))
            elif section_type == 'sentiment_analysis':
                context['sections'].append(self._generate_sentiment_section(symbol, data))
            # Add more section types as needed
        
        # Generate HTML from template
        html = self._render_template(context)
        
        return html
    
    def _generate_technical_section(self, symbol, data):
        """Generate the technical analysis section of the report"""
        charts = []
        insights = []
        
        # Generate charts for each indicator
        for indicator, values in data.items():
            if not values:
                continue
                
            if indicator == 'SMA' or indicator == 'EMA':
                chart = self._generate_moving_average_chart(symbol, indicator, values, data.get('market_data', []))
                if chart:
                    charts.append(chart)
                    
                # Generate insights
                insights.append(self._generate_ma_insight(symbol, indicator, values))
                
            elif indicator == 'RSI':
                chart = self._generate_rsi_chart(symbol, values)
                if chart:
                    charts.append(chart)
                    
                # Generate insights
                insights.append(self._generate_rsi_insight(symbol, values))
                
            elif indicator == 'MACD':
                chart = self._generate_macd_chart(symbol, values)
                if chart:
                    charts.append(chart)
                    
                # Generate insights
                insights.append(self._generate_macd_insight(symbol, values))
                
            elif indicator == 'BBANDS':
                chart = self._generate_bbands_chart(symbol, values, data.get('market_data', []))
                if chart:
                    charts.append(chart)
                    
                # Generate insights
                insights.append(self._generate_bbands_insight(symbol, values))
        
        # Create section
        section = {
            'title': f'Technical Analysis for {symbol}',
            'type': 'technical_analysis',
            'charts': charts,
            'insights': insights
        }
        
        return section
    
    def _generate_sentiment_section(self, symbol, data):
        """Generate the sentiment analysis section of the report"""
        # Check if data is a list or dictionary
        if isinstance(data, list):
            # It's a list of sentiment results, create a proper dict structure
            sentiment_results = data
            news_articles = []
            # Try to extract news info from sentiment results if available
            for result in sentiment_results:
                if 'news' in result and isinstance(result['news'], dict):
                    news_articles.append(result['news'])
        else:
            # Extract news articles and sentiment results from dict
            news_articles = data.get('news_articles', [])
            sentiment_results = data.get('sentiment_results', [])
        
        # Calculate overall sentiment score
        if sentiment_results:
            overall_score = sum(result['sentiment_score'] for result in sentiment_results) / len(sentiment_results)
            overall_label = self._get_sentiment_label(overall_score)
        else:
            overall_score = 0
            overall_label = 'Neutral'
        
        # Generate sentiment chart
        chart = self._generate_sentiment_chart(symbol, sentiment_results)
        
        # Create insights
        insights = [
            f"Overall sentiment for {symbol} is {overall_label} (score: {overall_score:.2f}).",
            f"Analyzed {len(sentiment_results)} news articles related to {symbol}."
        ]
        
        # Add specific article insights
        for i, result in enumerate(sentiment_results[:3]):  # Top 3 articles
            title = result.get('title', f"Article {i+1}")
            sentiment_label = result.get('sentiment_label', self._get_sentiment_label(result.get('sentiment_score', 0)))
            sentiment_score = result.get('sentiment_score', 0)
            insights.append(f"Article: \"{title}\" - {sentiment_label} (score: {sentiment_score:.2f})")
        
        # Create section
        section = {
            'title': f'Sentiment Analysis for {symbol}',
            'type': 'sentiment_analysis',
            'chart': chart,
            'insights': insights,
            'news_articles': news_articles[:5] if news_articles else []  # Show top 5 articles
        }
        
        return section
    
    def _generate_moving_average_chart(self, symbol, indicator, values, market_data):
        """Generate chart for Moving Averages"""
        try:
            # Prepare data
            dates = [value['timestamp'] for value in values]
            ma_values = [value['value'] for value in values]
            
            # Create figure
            plt.figure(figsize=(10, 6))
            
            # Plot moving average
            plt.plot(dates, ma_values, label=f"{indicator} ({self._get_indicator_period(values[0])})")
            
            # Plot price if market data is available
            if market_data:
                price_dates = [data['timestamp'] for data in market_data]
                prices = [data['close'] for data in market_data]
                plt.plot(price_dates, prices, label='Close Price')
            
            # Formatting
            plt.title(f"{indicator} for {symbol}")
            plt.xlabel('Date')
            plt.ylabel('Value')
            plt.legend()
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Convert plot to base64 image
            img = self._fig_to_base64(plt)
            plt.close()
            
            return img
            
        except Exception as e:
            logger.error(f"Error generating {indicator} chart: {str(e)}")
            plt.close()
            return None
    
    def _generate_rsi_chart(self, symbol, values):
        """Generate chart for RSI"""
        try:
            # Prepare data
            dates = [value['timestamp'] for value in values]
            rsi_values = [value['value'] for value in values]
            
            # Create figure
            plt.figure(figsize=(10, 6))
            
            # Plot RSI
            plt.plot(dates, rsi_values, label=f"RSI ({self._get_indicator_period(values[0])})")
            
            # Add overbought/oversold lines
            plt.axhline(y=70, color='r', linestyle='--', alpha=0.3, label='Overbought (70)')
            plt.axhline(y=30, color='g', linestyle='--', alpha=0.3, label='Oversold (30)')
            plt.axhline(y=50, color='k', linestyle='--', alpha=0.2)
            
            # Formatting
            plt.title(f"RSI for {symbol}")
            plt.xlabel('Date')
            plt.ylabel('RSI Value')
            plt.legend()
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.ylim(0, 100)
            plt.tight_layout()
            
            # Convert plot to base64 image
            img = self._fig_to_base64(plt)
            plt.close()
            
            return img
            
        except Exception as e:
            logger.error(f"Error generating RSI chart: {str(e)}")
            plt.close()
            return None
    
    def _generate_macd_chart(self, symbol, values):
        """Generate chart for MACD"""
        try:
            # Prepare data
            dates = [value['timestamp'] for value in values]
            macd_values = [value['value'] for value in values]
            signal_values = [value['signal'] for value in values]
            histogram_values = [value['histogram'] for value in values]
            
            # Create figure with two subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1]})
            
            # Plot MACD and Signal on top subplot
            ax1.plot(dates, macd_values, label='MACD')
            ax1.plot(dates, signal_values, label='Signal')
            ax1.axhline(y=0, color='k', linestyle='--', alpha=0.2)
            ax1.set_title(f"MACD for {symbol}")
            ax1.set_ylabel('Value')
            ax1.legend()
            ax1.grid(True)
            
            # Plot Histogram on bottom subplot
            colors = ['g' if val >= 0 else 'r' for val in histogram_values]
            ax2.bar(dates, histogram_values, color=colors, alpha=0.5, label='Histogram')
            ax2.axhline(y=0, color='k', linestyle='--', alpha=0.2)
            ax2.set_xlabel('Date')
            ax2.set_ylabel('Histogram')
            ax2.grid(True)
            
            # Formatting
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Convert plot to base64 image
            img = self._fig_to_base64(plt)
            plt.close()
            
            return img
            
        except Exception as e:
            logger.error(f"Error generating MACD chart: {str(e)}")
            plt.close()
            return None
    
    def _generate_bbands_chart(self, symbol, values, market_data):
        """Generate chart for Bollinger Bands"""
        try:
            # Prepare data
            dates = [value['timestamp'] for value in values]
            upper_values = [value['upper'] for value in values]
            middle_values = [value['middle'] for value in values]
            lower_values = [value['lower'] for value in values]
            
            # Create figure
            plt.figure(figsize=(10, 6))
            
            # Plot Bollinger Bands
            plt.plot(dates, upper_values, 'r--', label='Upper Band')
            plt.plot(dates, middle_values, 'k-', label='Middle Band')
            plt.plot(dates, lower_values, 'g--', label='Lower Band')
            
            # Plot price if market data is available
            if market_data:
                price_dates = [data['timestamp'] for data in market_data]
                prices = [data['close'] for data in market_data]
                plt.plot(price_dates, prices, 'b-', label='Close Price')
            
            # Formatting
            params = json.loads(values[0]['parameters'])
            plt.title(f"Bollinger Bands for {symbol} (Period: {params.get('period', 20)}, StdDev: {params.get('std_dev', 2)})")
            plt.xlabel('Date')
            plt.ylabel('Value')
            plt.legend()
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Convert plot to base64 image
            img = self._fig_to_base64(plt)
            plt.close()
            
            return img
            
        except Exception as e:
            logger.error(f"Error generating Bollinger Bands chart: {str(e)}")
            plt.close()
            return None
    
    def _generate_sentiment_chart(self, symbol, sentiment_results):
        """Generate chart for sentiment analysis"""
        try:
            # Prepare data
            if not sentiment_results:
                return None
                
            # Sort by published date if available
            sentiment_results = sorted(sentiment_results, key=lambda x: x.get('published_at', ''))
            
            titles = [result.get('title', f"Article {i}")[:30] + "..." for i, result in enumerate(sentiment_results)]
            scores = [result['sentiment_score'] for result in sentiment_results]
            labels = [result['sentiment_label'] for result in sentiment_results]
            
            # Create colors based on sentiment
            colors = []
            for score in scores:
                if score >= 0.05:
                    colors.append('green')
                elif score <= -0.05:
                    colors.append('red')
                else:
                    colors.append('gray')
            
            # Create figure
            plt.figure(figsize=(10, 6))
            
            # Plot sentiment scores
            plt.bar(range(len(scores)), scores, color=colors)
            
            # Formatting
            plt.title(f"Sentiment Analysis for {symbol}")
            plt.xlabel('News Articles')
            plt.ylabel('Sentiment Score (-1 to 1)')
            plt.axhline(y=0, color='k', linestyle='--', alpha=0.2)
            plt.xticks(range(len(titles)), titles, rotation=45, ha='right')
            plt.ylim(-1, 1)
            plt.tight_layout()
            
            # Convert plot to base64 image
            img = self._fig_to_base64(plt)
            plt.close()
            
            return img
            
        except Exception as e:
            logger.error(f"Error generating sentiment chart: {str(e)}")
            plt.close()
            return None
    
    def _fig_to_base64(self, fig):
        """Convert matplotlib figure to base64 encoded string"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        return f"data:image/png;base64,{img_str}"
    
    def _get_indicator_period(self, indicator):
        """Extract period from indicator parameters"""
        try:
            params = json.loads(indicator['parameters'])
            return params.get('period', 'N/A')
        except:
            return 'N/A'
    
    def _get_sentiment_label(self, score):
        """Convert sentiment score to label"""
        if score >= 0.05:
            return "Positive"
        elif score <= -0.05:
            return "Negative"
        else:
            return "Neutral"
    
    def _generate_ma_insight(self, symbol, indicator, values):
        """Generate insight for moving averages"""
        if not values:
            return f"Insufficient data to generate {indicator} insights for {symbol}."
            
        try:
            # Get the most recent MA values
            recent_values = values[-5:]
            
            # Calculate the trend
            if len(recent_values) < 2:
                return f"Recent {indicator} data is available for {symbol}."
                
            first_val = recent_values[0]['value']
            last_val = recent_values[-1]['value']
            
            if last_val > first_val:
                percent_change = (last_val - first_val) / first_val * 100
                return f"{indicator} for {symbol} is in an uptrend, increasing by {percent_change:.2f}% over the last {len(recent_values)} periods."
            elif last_val < first_val:
                percent_change = (first_val - last_val) / first_val * 100
                return f"{indicator} for {symbol} is in a downtrend, decreasing by {percent_change:.2f}% over the last {len(recent_values)} periods."
            else:
                return f"{indicator} for {symbol} has remained flat recently."
                
        except Exception as e:
            logger.error(f"Error generating MA insight: {str(e)}")
            return f"Analysis available for {symbol} using {indicator}."
    
    def _generate_rsi_insight(self, symbol, values):
        """Generate insight for RSI"""
        if not values:
            return f"Insufficient data to generate RSI insights for {symbol}."
            
        try:
            # Get the most recent RSI value
            recent_rsi = values[-1]['value']
            
            if recent_rsi > 70:
                return f"RSI for {symbol} is currently at {recent_rsi:.2f}, indicating an overbought condition. Consider watching for potential reversal signals."
            elif recent_rsi < 30:
                return f"RSI for {symbol} is currently at {recent_rsi:.2f}, indicating an oversold condition. Consider watching for potential recovery signals."
            elif recent_rsi > 50:
                return f"RSI for {symbol} is currently at {recent_rsi:.2f}, showing moderate positive momentum."
            else:
                return f"RSI for {symbol} is currently at {recent_rsi:.2f}, showing moderate negative momentum."
                
        except Exception as e:
            logger.error(f"Error generating RSI insight: {str(e)}")
            return f"RSI analysis available for {symbol}."
    
    def _generate_macd_insight(self, symbol, values):
        """Generate insight for MACD"""
        if not values or len(values) < 2:
            return f"Insufficient data to generate MACD insights for {symbol}."
            
        try:
            # Get recent MACD values
            current = values[-1]
            previous = values[-2]
            
            # Check for crossover
            current_macd = current['value']
            current_signal = current['signal']
            previous_macd = previous['value']
            previous_signal = previous['signal']
            
            if current_macd > current_signal and previous_macd <= previous_signal:
                return f"MACD for {symbol} recently crossed above the signal line, indicating a potential bullish trend is forming."
            elif current_macd < current_signal and previous_macd >= previous_signal:
                return f"MACD for {symbol} recently crossed below the signal line, indicating a potential bearish trend is forming."
            elif current_macd > 0 and current_signal > 0:
                return f"MACD and signal line for {symbol} are both positive, suggesting continued upward momentum."
            elif current_macd < 0 and current_signal < 0:
                return f"MACD and signal line for {symbol} are both negative, suggesting continued downward momentum."
            else:
                return f"MACD for {symbol} is at {current_macd:.2f} with signal line at {current_signal:.2f}."
                
        except Exception as e:
            logger.error(f"Error generating MACD insight: {str(e)}")
            return f"MACD analysis available for {symbol}."
    
    def _generate_bbands_insight(self, symbol, values):
        """Generate insight for Bollinger Bands"""
        if not values:
            return f"Insufficient data to generate Bollinger Bands insights for {symbol}."
            
        try:
            # Get the most recent values
            recent = values[-1]
            middle = recent['middle']
            upper = recent['upper']
            lower = recent['lower']
            
            # Calculate bandwidth as a percentage
            bandwidth = (upper - lower) / middle * 100
            
            if bandwidth > 20:
                return f"Bollinger Bands for {symbol} are wide (bandwidth: {bandwidth:.2f}%), indicating high volatility."
            elif bandwidth < 10:
                return f"Bollinger Bands for {symbol} are narrow (bandwidth: {bandwidth:.2f}%), suggesting a potential breakout may occur soon."
            else:
                return f"Bollinger Bands for {symbol} show moderate volatility (bandwidth: {bandwidth:.2f}%)."
                
        except Exception as e:
            logger.error(f"Error generating Bollinger Bands insight: {str(e)}")
            return f"Bollinger Bands analysis available for {symbol}."
    
    def _render_template(self, context):
        """Render the HTML report template with the provided context"""
        # Simple HTML template for the report
        template_str = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ title }}</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .header {
                    border-bottom: 2px solid #eee;
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                }
                .section {
                    margin-bottom: 30px;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    background-color: #f9f9f9;
                }
                .chart {
                    margin: 20px 0;
                    text-align: center;
                }
                .chart img {
                    max-width: 100%;
                    height: auto;
                }
                .insights {
                    margin: 20px 0;
                    padding: 15px;
                    background-color: #e6f7ff;
                    border-left: 4px solid #1890ff;
                    border-radius: 3px;
                }
                .news-article {
                    margin: 10px 0;
                    padding: 10px;
                    background-color: #fff;
                    border: 1px solid #eee;
                    border-radius: 3px;
                }
                .footer {
                    margin-top: 30px;
                    border-top: 1px solid #eee;
                    padding-top: 10px;
                    font-size: 0.8em;
                    color: #777;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ title }}</h1>
                <p>Generated on {{ timestamp }} | Symbols: {{ symbols }}</p>
                <p>Report Type: {{ report_type }}</p>
            </div>
            
            {% for section in sections %}
                <div class="section">
                    <h2>{{ section.title }}</h2>
                    
                    {% if section.type == 'technical_analysis' %}
                        {% for chart in section.charts %}
                            <div class="chart">
                                <img src="{{ chart }}" alt="Technical Chart">
                            </div>
                        {% endfor %}
                        
                        <div class="insights">
                            <h3>Insights:</h3>
                            <ul>
                                {% for insight in section.insights %}
                                    <li>{{ insight }}</li>
                                {% endfor %}
                            </ul>
                        </div>
                    {% endif %}
                    
                    {% if section.type == 'sentiment_analysis' %}
                        {% if section.chart %}
                            <div class="chart">
                                <img src="{{ section.chart }}" alt="Sentiment Chart">
                            </div>
                        {% endif %}
                        
                        <div class="insights">
                            <h3>Sentiment Insights:</h3>
                            <ul>
                                {% for insight in section.insights %}
                                    <li>{{ insight }}</li>
                                {% endfor %}
                            </ul>
                        </div>
                        
                        <h3>Recent News Articles:</h3>
                        {% for article in section.news_articles %}
                            <div class="news-article">
                                <h4>{{ article.title }}</h4>
                                <p>Source: {{ article.source }} | Date: {{ article.published_at }}</p>
                                <p>{{ article.content|truncate(200) }}</p>
                                {% if article.url %}
                                    <p><a href="{{ article.url }}" target="_blank">Read full article</a></p>
                                {% endif %}
                            </div>
                        {% endfor %}
                    {% endif %}
                </div>
            {% endfor %}
            
            <div class="footer">
                <p>This report was generated by the Financial AI Analysis Platform. The information provided is for informational purposes only and should not be considered as financial advice.</p>
            </div>
        </body>
        </html>
        """
        
        # Create Jinja2 template and render
        template = Template(template_str)
        html = template.render(**context)
        
        return html
