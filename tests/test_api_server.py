"""
test_api_server.py - API Server modülü için birim testler

Bu dosya Flask API server'ının tüm endpoint'lerini test eder:
- API endpoint testleri
- CORS testleri
- Error handling testleri
- JSON response testleri
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os
from datetime import datetime

# Ana proje klasörünü Python path'ine ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Flask app'i import et
import api_server
from config import Config


class TestAPIServer(unittest.TestCase):
    """API Server test sınıfı"""
    
    def setUp(self):
        """Her test öncesi çalışan setup metodu"""
        # Test client oluştur
        api_server.app.config['TESTING'] = True
        self.app = api_server.app.test_client()
        self.app.testing = True
        
        # Mock components oluştur
        api_server.components = {
            'data_provider': Mock(),
            'portfolio_tracker': Mock(),
            'sentiment_analyzer': Mock(),
            'strategy_executor': Mock(),
            'ml_model': Mock()
        }
        
        # Mock data
        self.mock_market_data = {
            'AAPL': {
                'price': 150.0,
                'change': 5.0,
                'change_percent': 3.45,
                'volume': 1000000,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        self.mock_portfolio_data = {
            'total_value': 11500.0,
            'total_cost': 10000.0,
            'unrealized_pnl': 1500.0,
            'cash_balance': 5000.0,
            'positions': [
                {
                    'symbol': 'AAPL',
                    'quantity': 10,
                    'avg_price': 145.0,
                    'current_price': 150.0,
                    'pnl': 50.0
                }
            ]
        }
        
        self.mock_signals = [
            {
                'symbol': 'AAPL',
                'signal': 'BUY',
                'confidence': 0.85,
                'timestamp': datetime.now().isoformat(),
                'price': 150.0
            }
        ]
        
        self.mock_news_data = [
            {
                'title': 'Apple reports strong quarterly earnings',
                'summary': 'Apple exceeded expectations with revenue growth.',
                'timestamp': datetime.now().isoformat(),
                'sentiment': 'positive',
                'score': 0.8
            }
        ]
    
    def test_home_endpoint(self):
        """Ana sayfa endpoint testi"""
        response = self.app.get('/')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('version', data)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'running')
    
    def test_health_endpoint(self):
        """Health check endpoint testi"""
        response = self.app.get('/api/health')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('timestamp', data)
        self.assertIn('components', data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_market_data_endpoint_success(self):
        """Market data endpoint başarı testi"""
        # Mock market data provider
        api_server.components['data_provider'].get_real_time_data.return_value = self.mock_market_data['AAPL']
        
        response = self.app.get('/api/market-data/AAPL')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('symbol', data)
        self.assertIn('price', data)
        self.assertIn('change', data)
        self.assertEqual(data['symbol'], 'AAPL')
        self.assertEqual(data['price'], 150.0)
        
        # Mock çağrıldığını kontrol et
        api_server.components['data_provider'].get_real_time_data.assert_called_once_with('AAPL')
    
    def test_market_data_endpoint_not_found(self):
        """Market data endpoint bulunamama testi"""
        # Mock data provider None dönsün
        api_server.components['data_provider'].get_real_time_data.return_value = None
        
        response = self.app.get('/api/market-data/INVALID')
        
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('message', data)
    
    def test_market_overview_endpoint(self):
        """Market overview endpoint testi"""
        # Mock market overview data
        mock_overview = [
            {
                'symbol': 'AAPL',
                'price': 150.0,
                'change': 5.0,
                'change_percent': 3.45
            },
            {
                'symbol': 'GOOGL',
                'price': 2500.0,
                'change': -25.0,
                'change_percent': -1.0
            }
        ]
        
        api_server.components['data_provider'].get_market_overview.return_value = mock_overview
        
        response = self.app.get('/api/market-overview')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('overview', data)
        self.assertIn('timestamp', data)
        self.assertIsInstance(data['overview'], list)
        self.assertEqual(len(data['overview']), 2)
    
    def test_portfolio_endpoint(self):
        """Portfolio endpoint testi"""
        # Mock portfolio data
        api_server.components['portfolio_tracker'].get_portfolio_summary.return_value = self.mock_portfolio_data
        
        response = self.app.get('/api/portfolio')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('total_value', data)
        self.assertIn('positions', data)
        self.assertEqual(data['total_value'], 11500.0)
        self.assertIsInstance(data['positions'], list)
    
    def test_signals_endpoint(self):
        """Trading signals endpoint testi"""
        # Mock ML model signals
        api_server.components['ml_model'].generate_signals.return_value = self.mock_signals
        
        response = self.app.get('/api/signals')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('signals', data)
        self.assertIn('timestamp', data)
        self.assertIsInstance(data['signals'], list)
        self.assertEqual(len(data['signals']), 1)
        
        signal = data['signals'][0]
        self.assertIn('symbol', signal)
        self.assertIn('signal', signal)
        self.assertIn('confidence', signal)
    
    def test_signals_endpoint_symbol_filter(self):
        """Specific symbol için signals endpoint testi"""
        # Mock signals for specific symbol
        filtered_signals = [s for s in self.mock_signals if s['symbol'] == 'AAPL']
        api_server.components['ml_model'].generate_signals.return_value = filtered_signals
        
        response = self.app.get('/api/signals/AAPL')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('signals', data)
        
        # Tüm signaller AAPL için olmalı
        for signal in data['signals']:
            self.assertEqual(signal['symbol'], 'AAPL')
    
    def test_news_endpoint(self):
        """News endpoint testi"""
        # Mock sentiment analyzer
        api_server.components['sentiment_analyzer'].get_recent_news.return_value = self.mock_news_data
        
        response = self.app.get('/api/news')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('news', data)
        self.assertIn('timestamp', data)
        self.assertIsInstance(data['news'], list)
        
        if data['news']:
            news_item = data['news'][0]
            self.assertIn('title', news_item)
            self.assertIn('summary', news_item)
            self.assertIn('sentiment', news_item)
    
    def test_sentiment_endpoint(self):
        """Sentiment analysis endpoint testi"""
        # Mock sentiment data
        mock_sentiment = {
            'overall_score': 0.6,
            'confidence': 0.8,
            'recommendation': 'BUY',
            'news_count': 10,
            'positive_count': 6,
            'negative_count': 2,
            'neutral_count': 2
        }
        
        api_server.components['sentiment_analyzer'].get_market_sentiment.return_value = mock_sentiment
        
        response = self.app.get('/api/sentiment/AAPL')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('symbol', data)
        self.assertIn('sentiment', data)
        self.assertEqual(data['symbol'], 'AAPL')
        
        sentiment = data['sentiment']
        self.assertIn('overall_score', sentiment)
        self.assertIn('recommendation', sentiment)
        self.assertEqual(sentiment['recommendation'], 'BUY')
    
    def test_trading_statistics_endpoint(self):
        """Trading statistics endpoint testi"""
        # Mock trading statistics
        mock_stats = {
            'total_trades': 25,
            'profitable_trades': 15,
            'win_rate': 0.6,
            'total_pnl': 2500.0,
            'avg_profit': 250.0,
            'avg_loss': -150.0,
            'sharpe_ratio': 1.2,
            'max_drawdown': -0.08
        }
        
        api_server.components['strategy_executor'].get_trading_statistics.return_value = mock_stats
        
        response = self.app.get('/api/trading-stats')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('statistics', data)
        
        stats = data['statistics']
        self.assertIn('total_trades', stats)
        self.assertIn('win_rate', stats)
        self.assertEqual(stats['total_trades'], 25)
        self.assertEqual(stats['win_rate'], 0.6)
    
    def test_start_bot_endpoint(self):
        """Bot başlatma endpoint testi"""
        response = self.app.post('/api/bot/start')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('status', data)
    
    def test_stop_bot_endpoint(self):
        """Bot durdurma endpoint testi"""
        response = self.app.post('/api/bot/stop')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('status', data)
    
    def test_bot_status_endpoint(self):
        """Bot durumu endpoint testi"""
        response = self.app.get('/api/bot/status')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('uptime', data)
        self.assertIn('last_update', data)
    
    def test_cors_headers(self):
        """CORS headers testi"""
        # OPTIONS request (preflight)
        response = self.app.options('/api/health')
        
        self.assertEqual(response.status_code, 200)
        
        # CORS headers kontrolü
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertIn('Access-Control-Allow-Methods', response.headers)
        self.assertIn('Access-Control-Allow-Headers', response.headers)
    
    def test_error_handling_500(self):
        """500 Internal Server Error handling testi"""
        # Mock exception
        api_server.components['data_provider'].get_real_time_data.side_effect = Exception("Database error")
        
        response = self.app.get('/api/market-data/AAPL')
        
        self.assertEqual(response.status_code, 500)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('message', data)
    
    def test_invalid_symbol_format(self):
        """Geçersiz sembol formatı testi"""
        response = self.app.get('/api/market-data/invalid_symbol_123')
        
        # Geçersiz format için 400 Bad Request olmalı
        self.assertIn(response.status_code, [400, 404])
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_json_response_format(self):
        """JSON response formatı testi"""
        response = self.app.get('/api/health')
        
        self.assertEqual(response.content_type, 'application/json')
        
        # Valid JSON olduğunu kontrol et
        try:
            json.loads(response.data)
        except json.JSONDecodeError:
            self.fail("Response is not valid JSON")
    
    def test_missing_components_handling(self):
        """Eksik component'ler ile hata yönetimi testi"""
        # Components'ı None yap
        original_components = api_server.components
        api_server.components = None
        
        try:
            response = self.app.get('/api/portfolio')
            
            self.assertEqual(response.status_code, 503)  # Service Unavailable
            
            data = json.loads(response.data)
            self.assertIn('error', data)
            
        finally:
            # Restore components
            api_server.components = original_components
    
    def test_concurrent_requests_handling(self):
        """Eşzamanlı istek işleme testi"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = self.app.get('/api/health')
            results.append(response.status_code)
        
        # 5 eşzamanlı istek
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join()
        
        # Tüm istekler başarılı olmalı
        self.assertEqual(len(results), 5)
        self.assertTrue(all(status == 200 for status in results))


class TestAPIServerIntegration(unittest.TestCase):
    """API Server entegrasyon testleri"""
    
    def setUp(self):
        """Her test öncesi çalışan setup metodu"""
        api_server.app.config['TESTING'] = True
        self.app = api_server.app.test_client()
        
        # Real-like mock setup
        self.setup_realistic_mocks()
    
    def setup_realistic_mocks(self):
        """Gerçekçi mock setup"""
        api_server.components = {
            'data_provider': Mock(),
            'portfolio_tracker': Mock(),
            'sentiment_analyzer': Mock(),
            'strategy_executor': Mock(),
            'ml_model': Mock()
        }
        
        # Realistic data flows
        api_server.components['data_provider'].get_real_time_data.return_value = {
            'price': 150.0,
            'change': 5.0,
            'change_percent': 3.45,
            'volume': 1000000
        }
        
        api_server.components['portfolio_tracker'].get_portfolio_summary.return_value = {
            'total_value': 11500.0,
            'cash_balance': 5000.0,
            'positions': [
                {'symbol': 'AAPL', 'quantity': 10, 'pnl': 100.0}
            ]
        }
    
    def test_full_api_workflow(self):
        """Tam API workflow testi"""
        # 1. Health check
        health_response = self.app.get('/api/health')
        self.assertEqual(health_response.status_code, 200)
        
        # 2. Market data
        market_response = self.app.get('/api/market-data/AAPL')
        self.assertEqual(market_response.status_code, 200)
        
        # 3. Portfolio
        portfolio_response = self.app.get('/api/portfolio')
        self.assertEqual(portfolio_response.status_code, 200)
        
        # 4. Trading stats
        stats_response = self.app.get('/api/trading-stats')
        self.assertEqual(stats_response.status_code, 200)
        
        # Her response JSON formatında olmalı
        responses = [health_response, market_response, portfolio_response, stats_response]
        for response in responses:
            self.assertEqual(response.content_type, 'application/json')
            
            # Valid JSON check
            try:
                json.loads(response.data)
            except json.JSONDecodeError:
                self.fail(f"Response is not valid JSON: {response.data}")
    
    def test_api_data_consistency(self):
        """API veri tutarlılığı testi"""
        # Aynı endpoint'e birden fazla istek
        responses = []
        for _ in range(3):
            response = self.app.get('/api/portfolio')
            responses.append(json.loads(response.data))
        
        # Tüm response'lar aynı yapıda olmalı
        first_response = responses[0]
        for response in responses[1:]:
            self.assertEqual(set(response.keys()), set(first_response.keys()))


class TestAPIServerPerformance(unittest.TestCase):
    """API Server performans testleri"""
    
    def setUp(self):
        """Her test öncesi çalışan setup metodu"""
        api_server.app.config['TESTING'] = True
        self.app = api_server.app.test_client()
        
        # Mock components
        api_server.components = {
            'data_provider': Mock(),
            'portfolio_tracker': Mock(),
            'sentiment_analyzer': Mock(),
            'strategy_executor': Mock(),
            'ml_model': Mock()
        }
    
    def test_response_time(self):
        """Response süresi testi"""
        import time
        
        start_time = time.time()
        response = self.app.get('/api/health')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Response süresi 1 saniyeden az olmalı
        self.assertLess(response_time, 1.0)
        self.assertEqual(response.status_code, 200)
    
    def test_memory_usage(self):
        """Bellek kullanımı testi"""
        import gc
        
        # Memory cleanup
        gc.collect()
        
        # Multiple requests
        for _ in range(100):
            response = self.app.get('/api/health')
            self.assertEqual(response.status_code, 200)
        
        # Cleanup after test
        gc.collect()
        
        # Test passes if no memory errors occurred


if __name__ == '__main__':
    # Test çalıştırma
    unittest.main(verbosity=2)
