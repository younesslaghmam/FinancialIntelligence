from flask import render_template, request, jsonify, redirect, url_for, flash
from app import db
from models import MarketData, TechnicalIndicator, NewsArticle, SentimentAnalysis, Report
from orchestrator import Orchestrator
import logging

logger = logging.getLogger(__name__)
orchestrator = Orchestrator()

def register_routes(app):
    
    @app.route('/')
    def index():
        """Home page with system overview"""
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard with market data and insights"""
        return render_template('dashboard.html')
    
    @app.route('/analysis', methods=['GET', 'POST'])
    def analysis():
        """Technical analysis view"""
        if request.method == 'POST':
            symbol = request.form.get('symbol', '').upper()
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            indicators = request.form.getlist('indicators')
            
            if not symbol:
                flash('Please enter a valid symbol', 'danger')
                return redirect(url_for('analysis'))
            
            # Trigger analysis agent
            try:
                results = orchestrator.run_technical_analysis(symbol, start_date, end_date, indicators)
                return render_template('analysis.html', results=results, symbol=symbol)
            except Exception as e:
                logger.error(f"Analysis error: {str(e)}")
                flash(f'Analysis error: {str(e)}', 'danger')
                return render_template('analysis.html')
        
        return render_template('analysis.html')
    
    @app.route('/sentiment', methods=['GET', 'POST'])
    def sentiment():
        """Sentiment analysis view"""
        if request.method == 'POST':
            symbol = request.form.get('symbol', '').upper()
            days = int(request.form.get('days', 7))
            
            if not symbol:
                flash('Please enter a valid symbol', 'danger')
                return redirect(url_for('sentiment'))
            
            # Trigger sentiment analysis
            try:
                results = orchestrator.run_sentiment_analysis(symbol, days)
                return render_template('sentiment.html', results=results, symbol=symbol)
            except Exception as e:
                logger.error(f"Sentiment analysis error: {str(e)}")
                flash(f'Sentiment analysis error: {str(e)}', 'danger')
                return render_template('sentiment.html')
        
        return render_template('sentiment.html')
    
    @app.route('/reports', methods=['GET', 'POST'])
    def reports():
        """Reports view and generation"""
        if request.method == 'POST':
            symbols = request.form.get('symbols', '').upper().split(',')
            report_type = request.form.get('report_type', 'comprehensive')
            title = request.form.get('title', f'Report for {", ".join(symbols)}')
            
            if not symbols or symbols[0] == '':
                flash('Please enter at least one symbol', 'danger')
                return redirect(url_for('reports'))
            
            # Generate report
            try:
                report_id = orchestrator.generate_report(title, symbols, report_type)
                return redirect(url_for('view_report', report_id=report_id))
            except Exception as e:
                logger.error(f"Report generation error: {str(e)}")
                flash(f'Report generation error: {str(e)}', 'danger')
                return render_template('reports.html')
        
        # Get existing reports
        reports = Report.query.order_by(Report.created_at.desc()).all()
        return render_template('reports.html', reports=reports)
    
    @app.route('/reports/<int:report_id>')
    def view_report(report_id):
        """View a specific report"""
        report = Report.query.get_or_404(report_id)
        return render_template('view_report.html', report=report)
    
    @app.route('/api/market_data/<symbol>')
    def api_market_data(symbol):
        """API endpoint for market data"""
        symbol = symbol.upper()
        days = request.args.get('days', 30, type=int)
        
        try:
            data = orchestrator.get_market_data(symbol, days)
            return jsonify({"success": True, "data": data})
        except Exception as e:
            logger.error(f"Market data API error: {str(e)}")
            return jsonify({"success": False, "error": str(e)})
    
    @app.route('/api/indicators/<symbol>/<indicator>')
    def api_indicator(symbol, indicator):
        """API endpoint for technical indicators"""
        symbol = symbol.upper()
        days = request.args.get('days', 30, type=int)
        params = request.args.get('params', '')
        
        try:
            data = orchestrator.get_indicator_data(symbol, indicator, days, params)
            return jsonify({"success": True, "data": data})
        except Exception as e:
            logger.error(f"Indicator API error: {str(e)}")
            return jsonify({"success": False, "error": str(e)})
