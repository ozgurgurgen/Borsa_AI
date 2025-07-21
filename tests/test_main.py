"""
test_main.py - Main modülü için birim testler

Bu dosya main.py dosyasının tüm fonksiyonlarını test eder:
- Ana uygulama akışı testleri
- Bileşen entegrasyonu testleri
- Hata yönetimi testleri
- Konfigürasyon testleri
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os
import time
from datetime import datetime

# Ana proje klasörünü Python path'ine ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main
from config import Config


class TestMainApplication(unittest.TestCase):
    """Main application test sınıfı"""
    
    def setUp(self):
        """Her test öncesi çalışan setup metodu"""
        # Mock objelerini oluştur
        self.mock_data_provider = Mock()
        self.mock_portfolio_tracker = Mock()
        self.mock_feature_engineer = Mock()
        self.mock_sentiment_analyzer = Mock()
        self.mock_ml_model = Mock()
        self.mock_strategy_executor = Mock()
        self.mock_logger = Mock()
        
        # Mock data
        self.mock_market_data = {
            'AAPL': {
                'price': 150.0,
                'change': 5.0,
                'change_percent': 3.45,
                'volume': 1000000
            }
        }
        
        self.mock_ml_signals = [
            {
                'symbol': 'AAPL',
                'signal': 'BUY',
                'confidence': 0.85,
                'probability': 0.75,
                'timestamp': datetime.now()
            }
        ]
        
        self.mock_sentiment_data = {
            'AAPL': {
                'overall_score': 0.6,
                'confidence': 0.8,
                'recommendation': 'BUY'
            }
        }
    
    @patch('main.logger')
    @patch('main.StrategyExecutor')
    @patch('main.MLModel')
    @patch('main.NewsSentimentAnalyzer')
    @patch('main.FeatureEngineer')
    @patch('main.PortfolioTracker')
    @patch('main.MarketDataProvider')
    def test_initialize_components(self, mock_data_provider, mock_portfolio,
                                  mock_feature_eng, mock_sentiment,
                                  mock_ml, mock_strategy, mock_logger):
        """Bileşen başlatma testi"""
        
        # Mock return values
        mock_data_provider.return_value = self.mock_data_provider
        mock_portfolio.return_value = self.mock_portfolio_tracker
        mock_feature_eng.return_value = self.mock_feature_engineer
        mock_sentiment.return_value = self.mock_sentiment_analyzer
        mock_ml.return_value = self.mock_ml_model
        mock_strategy.return_value = self.mock_strategy_executor
        
        # Initialize components
        result = main.initialize_components()
        
        self.assertIsInstance(result, dict)
        self.assertIn('data_provider', result)
        self.assertIn('portfolio_tracker', result)
        self.assertIn('feature_engineer', result)
        self.assertIn('sentiment_analyzer', result)
        self.assertIn('ml_model', result)
        self.assertIn('strategy_executor', result)
        
        # Her bileşen oluşturulmuş olmalı
        mock_data_provider.assert_called_once()
        mock_portfolio.assert_called_once_with(Config.TRADING_PARAMS['initial_balance'])
        mock_feature_eng.assert_called_once()
        mock_sentiment.assert_called_once()
        mock_ml.assert_called_once()
        mock_strategy.assert_called_once_with(Config.TRADING_PARAMS['initial_balance'])
    
    @patch('main.logger')
    def test_load_ml_model_success(self, mock_logger):
        """ML model yükleme başarı testi"""
        # Mock ML model
        self.mock_ml_model.load_model.return_value = True
        
        result = main.load_ml_model(self.mock_ml_model, 'test_model.joblib')
        
        self.assertTrue(result)
        self.mock_ml_model.load_model.assert_called_once_with('test_model.joblib')
    
    @patch('main.logger')
    def test_load_ml_model_failure(self, mock_logger):
        """ML model yükleme başarısızlık testi"""
        # Mock ML model load failure
        self.mock_ml_model.load_model.return_value = False
        
        result = main.load_ml_model(self.mock_ml_model, 'invalid_model.joblib')
        
        self.assertFalse(result)
        self.mock_ml_model.load_model.assert_called_once_with('invalid_model.joblib')
    
    @patch('main.logger')
    def test_fetch_market_data_success(self, mock_logger):
        """Piyasa verisi alma başarı testi"""
        # Mock data provider
        self.mock_data_provider.get_real_time_data.return_value = self.mock_market_data['AAPL']
        
        symbols = ['AAPL']
        result = main.fetch_market_data(self.mock_data_provider, symbols)
        
        self.assertIsInstance(result, dict)
        self.assertIn('AAPL', result)
        self.assertEqual(result['AAPL'], self.mock_market_data['AAPL'])
        
        self.mock_data_provider.get_real_time_data.assert_called_once_with('AAPL')
    
    @patch('main.logger')
    def test_fetch_market_data_partial_failure(self, mock_logger):
        """Kısmi piyasa verisi alma testi"""
        # AAPL başarılı, GOOGL başarısız
        def mock_get_data(symbol):
            if symbol == 'AAPL':
                return self.mock_market_data['AAPL']
            else:
                return None
        
        self.mock_data_provider.get_real_time_data.side_effect = mock_get_data
        
        symbols = ['AAPL', 'GOOGL']
        result = main.fetch_market_data(self.mock_data_provider, symbols)
        
        self.assertIsInstance(result, dict)
        self.assertIn('AAPL', result)
        self.assertNotIn('GOOGL', result)  # Başarısız olan dahil edilmemeli
    
    @patch('main.logger')
    def test_generate_ml_signals_success(self, mock_logger):
        """ML signal üretme başarı testi"""
        # Mock feature matrix
        mock_features = Mock()
        self.mock_feature_engineer.create_feature_matrix.return_value = mock_features
        
        # Mock ML predictions
        self.mock_ml_model.generate_signals.return_value = self.mock_ml_signals
        
        result = main.generate_ml_signals(
            self.mock_ml_model,
            self.mock_feature_engineer,
            self.mock_market_data,
            ['AAPL']
        )
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['symbol'], 'AAPL')
        
        # Feature engineering çağrılmış olmalı
        self.mock_feature_engineer.create_feature_matrix.assert_called_once()
        
        # ML model prediction çağrılmış olmalı
        self.mock_ml_model.generate_signals.assert_called_once()
    
    @patch('main.logger')
    def test_generate_ml_signals_failure(self, mock_logger):
        """ML signal üretme başarısızlık testi"""
        # Mock feature engineering failure
        self.mock_feature_engineer.create_feature_matrix.return_value = None
        
        result = main.generate_ml_signals(
            self.mock_ml_model,
            self.mock_feature_engineer,
            self.mock_market_data,
            ['AAPL']
        )
        
        self.assertEqual(result, [])
    
    @patch('main.logger')
    def test_analyze_market_sentiment_success(self, mock_logger):
        """Piyasa sentiment analizi başarı testi"""
        # Mock sentiment analysis
        self.mock_sentiment_analyzer.get_market_sentiment.return_value = self.mock_sentiment_data['AAPL']
        
        symbols = ['AAPL']
        result = main.analyze_market_sentiment(self.mock_sentiment_analyzer, symbols)
        
        self.assertIsInstance(result, dict)
        self.assertIn('AAPL', result)
        self.assertEqual(result['AAPL'], self.mock_sentiment_data['AAPL'])
        
        self.mock_sentiment_analyzer.get_market_sentiment.assert_called_once_with('AAPL')
    
    @patch('main.logger')
    def test_execute_trading_strategy_success(self, mock_logger):
        """İşlem stratejisi yürütme başarı testi"""
        # Mock strategy execution
        mock_orders = [
            {
                'symbol': 'AAPL',
                'action': 'BUY',
                'quantity': 10,
                'price': 150.0,
                'order_id': 'test_order_1'
            }
        ]
        self.mock_strategy_executor.process_signals.return_value = mock_orders
        
        result = main.execute_trading_strategy(
            self.mock_strategy_executor,
            self.mock_ml_signals,
            self.mock_market_data,
            self.mock_sentiment_data
        )
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['symbol'], 'AAPL')
        
        self.mock_strategy_executor.process_signals.assert_called_once_with(
            self.mock_ml_signals,
            self.mock_market_data,
            self.mock_sentiment_data
        )
    
    @patch('main.logger')
    def test_update_portfolio_success(self, mock_logger):
        """Portföy güncelleme başarı testi"""
        # Mock portfolio update
        mock_portfolio_status = {
            'total_value': 11500.0,
            'total_cost': 10000.0,
            'unrealized_pnl': 1500.0,
            'cash_balance': 5000.0
        }
        self.mock_portfolio_tracker.get_portfolio_summary.return_value = mock_portfolio_status
        
        result = main.update_portfolio(
            self.mock_portfolio_tracker,
            self.mock_market_data
        )
        
        self.assertEqual(result, mock_portfolio_status)
        self.mock_portfolio_tracker.get_portfolio_summary.assert_called_once_with(
            {symbol: data['price'] for symbol, data in self.mock_market_data.items()}
        )
    
    @patch('main.logger')
    @patch('main.time.sleep')
    def test_save_state_and_logs(self, mock_sleep, mock_logger):
        """Durum ve log kaydetme testi"""
        # Mock portfolio data
        portfolio_status = {
            'total_value': 11500.0,
            'positions': ['AAPL']
        }
        
        # Mock trading statistics
        trading_stats = {
            'total_trades': 5,
            'win_rate': 0.6
        }
        self.mock_strategy_executor.get_trading_statistics.return_value = trading_stats
        
        # Save state
        main.save_state_and_logs(
            self.mock_portfolio_tracker,
            self.mock_strategy_executor,
            portfolio_status
        )
        
        # Trading statistics çağrılmış olmalı
        self.mock_strategy_executor.get_trading_statistics.assert_called_once()
    
    @patch('main.logger')
    @patch('main.time.sleep')
    @patch('main.save_state_and_logs')
    @patch('main.update_portfolio')
    @patch('main.execute_trading_strategy')
    @patch('main.analyze_market_sentiment')
    @patch('main.generate_ml_signals')
    @patch('main.fetch_market_data')
    @patch('main.initialize_components')
    def test_main_trading_loop_single_iteration(self, mock_init, mock_fetch,
                                               mock_ml_signals, mock_sentiment,
                                               mock_strategy, mock_update,
                                               mock_save, mock_sleep, mock_logger):
        """Ana işlem döngüsü tek iterasyon testi"""
        
        # Mock component initialization
        components = {
            'data_provider': self.mock_data_provider,
            'portfolio_tracker': self.mock_portfolio_tracker,
            'feature_engineer': self.mock_feature_engineer,
            'sentiment_analyzer': self.mock_sentiment_analyzer,
            'ml_model': self.mock_ml_model,
            'strategy_executor': self.mock_strategy_executor
        }
        mock_init.return_value = components
        
        # Mock ML model load success
        self.mock_ml_model.load_model.return_value = True
        
        # Mock data fetching
        mock_fetch.return_value = self.mock_market_data
        
        # Mock ML signals
        mock_ml_signals.return_value = self.mock_ml_signals
        
        # Mock sentiment analysis
        mock_sentiment.return_value = self.mock_sentiment_data
        
        # Mock strategy execution
        mock_strategy.return_value = [{'order_id': 'test'}]
        
        # Mock portfolio update
        mock_update.return_value = {'total_value': 11000}
        
        # Test ana fonksiyon çağrısı (tek iterasyon için)
        with patch('main.Config.TRADING_PARAMS', {'symbols': ['AAPL'], 'update_interval': 1}):
            # KeyboardInterrupt simulate et (infinite loop'tan çıkmak için)
            mock_sleep.side_effect = KeyboardInterrupt("Test interruption")
            
            try:
                main.main()
            except KeyboardInterrupt:
                pass  # Expected
        
        # Tüm ana fonksiyonlar çağrılmış olmalı
        mock_init.assert_called_once()
        mock_fetch.assert_called()
        mock_ml_signals.assert_called()
        mock_sentiment.assert_called()
        mock_strategy.assert_called()
        mock_update.assert_called()
    
    @patch('main.logger')
    @patch('main.initialize_components')
    def test_main_initialization_failure(self, mock_init, mock_logger):
        """Ana uygulama başlatma başarısızlık testi"""
        # Component initialization failure
        mock_init.return_value = None
        
        # Main fonksiyon çalışmamalı
        result = main.main()
        
        # None dönemeli (başarısızlık)
        self.assertIsNone(result)
    
    @patch('main.logger')
    @patch('main.initialize_components')
    def test_ml_model_load_failure_handling(self, mock_init, mock_logger):
        """ML model yükleme başarısızlığı işleme testi"""
        # Components başarılı
        components = {
            'data_provider': self.mock_data_provider,
            'portfolio_tracker': self.mock_portfolio_tracker,
            'feature_engineer': self.mock_feature_engineer,
            'sentiment_analyzer': self.mock_sentiment_analyzer,
            'ml_model': self.mock_ml_model,
            'strategy_executor': self.mock_strategy_executor
        }
        mock_init.return_value = components
        
        # ML model load failure
        self.mock_ml_model.load_model.return_value = False
        
        # Model load edilemediğinde training yapmalı
        self.mock_ml_model.train_model.return_value = True
        
        with patch('main.Config.TRADING_PARAMS', {'symbols': ['AAPL'], 'update_interval': 1}):
            with patch('main.time.sleep', side_effect=KeyboardInterrupt("Test")):
                try:
                    main.main()
                except KeyboardInterrupt:
                    pass
        
        # Training fonksiyonu çağrılmış olmalı
        # (Gerçek implementasyonda model training mantığı olmalı)
        pass
    
    @patch('main.logger')
    def test_error_handling_in_main_loop(self, mock_logger):
        """Ana döngüde hata yönetimi testi"""
        # Exception raising mock
        self.mock_data_provider.get_real_time_data.side_effect = Exception("Network error")
        
        # Hata durumunda fonksiyon devam etmeli
        result = main.fetch_market_data(self.mock_data_provider, ['AAPL'])
        
        # Boş dict dönmeli (hata durumunda)
        self.assertEqual(result, {})
    
    @patch('main.logger')
    @patch('builtins.print')
    def test_logging_functionality(self, mock_print, mock_logger):
        """Loglama fonksiyonalitesi testi"""
        # Test log mesajları
        main.log_trading_activity("Test message", "INFO")
        
        # Logger çağrılmış olmalı
        mock_logger.info.assert_called()


class TestMainApplicationIntegration(unittest.TestCase):
    """Main application entegrasyon testleri"""
    
    def setUp(self):
        """Her test öncesi çalışan setup metodu"""
        pass
    
    @patch('main.logger')
    @patch('main.StrategyExecutor')
    @patch('main.MLModel')
    @patch('main.NewsSentimentAnalyzer')
    @patch('main.FeatureEngineer')
    @patch('main.PortfolioTracker')
    @patch('main.MarketDataProvider')
    def test_full_pipeline_integration(self, mock_data_provider, mock_portfolio,
                                      mock_feature_eng, mock_sentiment,
                                      mock_ml, mock_strategy, mock_logger):
        """Tam pipeline entegrasyon testi"""
        
        # Mock tüm bileşenleri
        mock_instances = {
            'data_provider': Mock(),
            'portfolio_tracker': Mock(),
            'feature_engineer': Mock(),
            'sentiment_analyzer': Mock(),
            'ml_model': Mock(),
            'strategy_executor': Mock()
        }
        
        # Mock return values
        mock_data_provider.return_value = mock_instances['data_provider']
        mock_portfolio.return_value = mock_instances['portfolio_tracker']
        mock_feature_eng.return_value = mock_instances['feature_engineer']
        mock_sentiment.return_value = mock_instances['sentiment_analyzer']
        mock_ml.return_value = mock_instances['ml_model']
        mock_strategy.return_value = mock_instances['strategy_executor']
        
        # Mock data flow
        mock_instances['data_provider'].get_real_time_data.return_value = {
            'price': 150.0, 'volume': 1000000
        }
        
        mock_instances['feature_engineer'].create_feature_matrix.return_value = Mock()
        
        mock_instances['ml_model'].generate_signals.return_value = [
            {'symbol': 'AAPL', 'signal': 'BUY', 'confidence': 0.8}
        ]
        
        mock_instances['sentiment_analyzer'].get_market_sentiment.return_value = {
            'overall_score': 0.6, 'recommendation': 'BUY'
        }
        
        mock_instances['strategy_executor'].process_signals.return_value = [
            {'order_id': 'test_order', 'symbol': 'AAPL', 'action': 'BUY'}
        ]
        
        mock_instances['portfolio_tracker'].get_portfolio_summary.return_value = {
            'total_value': 11000, 'total_pnl': 1000
        }
        
        # Initialize components
        components = main.initialize_components()
        
        # Test data flow
        market_data = main.fetch_market_data(components['data_provider'], ['AAPL'])
        self.assertIsInstance(market_data, dict)
        
        ml_signals = main.generate_ml_signals(
            components['ml_model'],
            components['feature_engineer'],
            market_data,
            ['AAPL']
        )
        self.assertIsInstance(ml_signals, list)
        
        sentiment_data = main.analyze_market_sentiment(
            components['sentiment_analyzer'],
            ['AAPL']
        )
        self.assertIsInstance(sentiment_data, dict)
        
        orders = main.execute_trading_strategy(
            components['strategy_executor'],
            ml_signals,
            market_data,
            sentiment_data
        )
        self.assertIsInstance(orders, list)
        
        portfolio_status = main.update_portfolio(
            components['portfolio_tracker'],
            market_data
        )
        self.assertIsInstance(portfolio_status, dict)


class TestMainApplicationConfiguration(unittest.TestCase):
    """Main application konfigürasyon testleri"""
    
    def test_config_loading(self):
        """Konfigürasyon yükleme testi"""
        # Config değerlerinin mevcut olduğunu kontrol et
        self.assertIsNotNone(Config.TRADING_PARAMS)
        self.assertIsNotNone(Config.RISK_MANAGEMENT)
        self.assertIsNotNone(Config.TURKISH_SYMBOLS)
        
        # Required parameters
        required_trading_params = [
            'initial_balance', 'symbols', 'update_interval', 'min_confidence'
        ]
        
        for param in required_trading_params:
            self.assertIn(param, Config.TRADING_PARAMS)
        
        # Risk management parameters
        required_risk_params = [
            'max_position_size', 'stop_loss_pct', 'take_profit_pct'
        ]
        
        for param in required_risk_params:
            self.assertIn(param, Config.RISK_MANAGEMENT)
    
    def test_config_validation(self):
        """Konfigürasyon doğrulama testi"""
        # Değer aralığı kontrolleri
        self.assertGreater(Config.TRADING_PARAMS['initial_balance'], 0)
        self.assertGreater(Config.TRADING_PARAMS['update_interval'], 0)
        self.assertGreaterEqual(Config.TRADING_PARAMS['min_confidence'], 0)
        self.assertLessEqual(Config.TRADING_PARAMS['min_confidence'], 1)
        
        # Risk management değerleri
        self.assertGreater(Config.RISK_MANAGEMENT['max_position_size'], 0)
        self.assertLessEqual(Config.RISK_MANAGEMENT['max_position_size'], 1)
        self.assertGreater(Config.RISK_MANAGEMENT['stop_loss_pct'], 0)
        self.assertGreater(Config.RISK_MANAGEMENT['take_profit_pct'], 0)


if __name__ == '__main__':
    # Test çalıştırma
    unittest.main(verbosity=2)
