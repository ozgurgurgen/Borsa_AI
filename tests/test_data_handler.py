"""
test_data_handler.py - DataHandler modülü için birim testler

Bu dosya DataHandler sınıfının tüm fonksiyonlarını test eder:
- MarketDataProvider sınıfı testleri
- PortfolioTracker sınıfı testleri
- Veri alma ve işleme fonksiyonları testleri
- Hata durumu testleri
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Ana proje klasörünü Python path'ine ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_handler import MarketDataProvider, PortfolioTracker
from config import Config


class TestMarketDataProvider(unittest.TestCase):
    """MarketDataProvider sınıfı için test sınıfı"""
    
    def setUp(self):
        """Her test öncesi çalışan setup metodu"""
        self.provider = MarketDataProvider()
        
        # Mock veri oluştur
        self.mock_data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=100, freq='1H'),
            'open': np.random.uniform(100, 200, 100),
            'high': np.random.uniform(150, 250, 100),
            'low': np.random.uniform(50, 150, 100),
            'close': np.random.uniform(80, 220, 100),
            'volume': np.random.randint(1000, 10000, 100)
        })
    
    def test_init(self):
        """MarketDataProvider başlatma testi"""
        self.assertIsInstance(self.provider, MarketDataProvider)
        self.assertIn('market_data', self.provider.__dict__)
    
    @patch('data_handler.yf')
    def test_get_historical_data_success(self, mock_yf):
        """Başarılı geçmiş veri alma testi"""
        # Mock Yahoo Finance response
        mock_ticker = Mock()
        mock_ticker.history.return_value = self.mock_data
        mock_yf.Ticker.return_value = mock_ticker
        
        result = self.provider.get_historical_data("AAPL", "1d", "1y")
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        mock_yf.Ticker.assert_called_once_with("AAPL")
    
    @patch('data_handler.yf')
    def test_get_historical_data_failure(self, mock_yf):
        """Başarısız geçmiş veri alma testi"""
        # Mock hata durumu
        mock_yf.Ticker.side_effect = Exception("Bağlantı hatası")
        
        result = self.provider.get_historical_data("INVALID", "1d", "1y")
        
        self.assertTrue(result.empty)
    
    @patch('data_handler.yf')
    def test_get_real_time_data_success(self, mock_yf):
        """Başarılı gerçek zamanlı veri alma testi"""
        # Mock real-time data
        mock_ticker = Mock()
        mock_info = {
            'regularMarketPrice': 150.0,
            'regularMarketChange': 5.0,
            'regularMarketChangePercent': 3.45,
            'regularMarketVolume': 1000000
        }
        mock_ticker.info = mock_info
        mock_yf.Ticker.return_value = mock_ticker
        
        result = self.provider.get_real_time_data("AAPL")
        
        self.assertIsInstance(result, dict)
        self.assertIn('price', result)
        self.assertIn('change', result)
        self.assertEqual(result['price'], 150.0)
    
    @patch('data_handler.yf')
    def test_get_real_time_data_failure(self, mock_yf):
        """Başarısız gerçek zamanlı veri alma testi"""
        mock_yf.Ticker.side_effect = Exception("API hatası")
        
        result = self.provider.get_real_time_data("INVALID")
        
        self.assertIsNone(result)
    
    @patch('data_handler.yf')
    def test_get_market_overview_success(self, mock_yf):
        """Başarılı piyasa özeti alma testi"""
        # Mock multiple tickers
        mock_data_list = []
        for _ in range(len(Config.TURKISH_SYMBOLS)):
            mock_ticker = Mock()
            mock_ticker.info = {
                'regularMarketPrice': np.random.uniform(10, 100),
                'regularMarketChange': np.random.uniform(-5, 5),
                'regularMarketChangePercent': np.random.uniform(-10, 10),
                'regularMarketVolume': np.random.randint(100000, 1000000)
            }
            mock_data_list.append(mock_ticker)
        
        mock_yf.Ticker.side_effect = mock_data_list
        
        result = self.provider.get_market_overview()
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        # İlk elementin yapısını kontrol et
        if result:
            first_item = result[0]
            self.assertIn('symbol', first_item)
            self.assertIn('price', first_item)
    
    def test_calculate_technical_indicators(self):
        """Teknik gösterge hesaplama testi"""
        result = self.provider.calculate_technical_indicators(self.mock_data)
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('SMA_20', result.columns)
        self.assertIn('SMA_50', result.columns)
        self.assertIn('RSI', result.columns)
        self.assertIn('MACD', result.columns)
        
        # RSI değerlerinin 0-100 arasında olduğunu kontrol et
        rsi_values = result['RSI'].dropna()
        if not rsi_values.empty:
            self.assertTrue(all(0 <= val <= 100 for val in rsi_values))
    
    def test_calculate_technical_indicators_empty_data(self):
        """Boş veri ile teknik gösterge hesaplama testi"""
        empty_df = pd.DataFrame()
        result = self.provider.calculate_technical_indicators(empty_df)
        
        self.assertTrue(result.empty)


class TestPortfolioTracker(unittest.TestCase):
    """PortfolioTracker sınıfı için test sınıfı"""
    
    def setUp(self):
        """Her test öncesi çalışan setup metodu"""
        self.tracker = PortfolioTracker(initial_balance=10000.0)
    
    def test_init(self):
        """PortfolioTracker başlatma testi"""
        self.assertEqual(self.tracker.balance, 10000.0)
        self.assertEqual(len(self.tracker.positions), 0)
        self.assertEqual(len(self.tracker.transactions), 0)
    
    def test_add_position_new(self):
        """Yeni pozisyon ekleme testi"""
        result = self.tracker.add_position("AAPL", 10, 150.0, "BUY")
        
        self.assertTrue(result)
        self.assertIn("AAPL", self.tracker.positions)
        self.assertEqual(self.tracker.positions["AAPL"]["quantity"], 10)
        self.assertEqual(self.tracker.positions["AAPL"]["avg_price"], 150.0)
        self.assertEqual(len(self.tracker.transactions), 1)
    
    def test_add_position_existing_buy(self):
        """Mevcut pozisyona ekleme testi"""
        # İlk pozisyon
        self.tracker.add_position("AAPL", 10, 150.0, "BUY")
        
        # Aynı sembole ekleme
        result = self.tracker.add_position("AAPL", 5, 160.0, "BUY")
        
        self.assertTrue(result)
        self.assertEqual(self.tracker.positions["AAPL"]["quantity"], 15)
        # Ortalama fiyat hesaplaması: (10*150 + 5*160) / 15 = 153.33
        expected_avg = (10 * 150.0 + 5 * 160.0) / 15
        self.assertAlmostEqual(self.tracker.positions["AAPL"]["avg_price"], expected_avg, places=2)
    
    def test_add_position_sell(self):
        """Pozisyon satma testi"""
        # Önce al
        self.tracker.add_position("AAPL", 10, 150.0, "BUY")
        
        # Sonra sat
        result = self.tracker.add_position("AAPL", 5, 160.0, "SELL")
        
        self.assertTrue(result)
        self.assertEqual(self.tracker.positions["AAPL"]["quantity"], 5)
    
    def test_add_position_sell_more_than_owned(self):
        """Sahip olunan miktardan fazla satma testi"""
        self.tracker.add_position("AAPL", 5, 150.0, "BUY")
        
        # 10 adet satmaya çalış (sadece 5 adet var)
        result = self.tracker.add_position("AAPL", 10, 160.0, "SELL")
        
        self.assertFalse(result)
        self.assertEqual(self.tracker.positions["AAPL"]["quantity"], 5)
    
    def test_add_position_insufficient_balance(self):
        """Yetersiz bakiye ile alım testi"""
        # 10000 TL bakiye var, 100000 TL'lik alım yapmaya çalış
        result = self.tracker.add_position("AAPL", 1000, 150.0, "BUY")
        
        self.assertFalse(result)
        self.assertNotIn("AAPL", self.tracker.positions)
    
    def test_get_portfolio_value(self):
        """Portföy değeri hesaplama testi"""
        # Pozisyon ekle
        self.tracker.add_position("AAPL", 10, 150.0, "BUY")
        
        # Mock fiyat verisi
        current_prices = {"AAPL": 160.0}
        
        portfolio_value = self.tracker.get_portfolio_value(current_prices)
        
        expected_value = 10 * 160.0  # 10 adet * 160 TL
        self.assertEqual(portfolio_value, expected_value)
    
    def test_get_portfolio_value_no_prices(self):
        """Fiyat verisi olmadan portföy değeri testi"""
        self.tracker.add_position("AAPL", 10, 150.0, "BUY")
        
        portfolio_value = self.tracker.get_portfolio_value({})
        self.assertEqual(portfolio_value, 0.0)
    
    def test_get_portfolio_summary(self):
        """Portföy özeti alma testi"""
        # Pozisyonlar ekle
        self.tracker.add_position("AAPL", 10, 150.0, "BUY")
        self.tracker.add_position("GOOGL", 5, 200.0, "BUY")
        
        # Mock fiyat verisi
        current_prices = {"AAPL": 160.0, "GOOGL": 210.0}
        
        summary = self.tracker.get_portfolio_summary(current_prices)
        
        self.assertIn("total_value", summary)
        self.assertIn("total_cost", summary)
        self.assertIn("total_pnl", summary)
        self.assertIn("positions", summary)
        
        # Değerleri kontrol et
        expected_total_value = 10 * 160.0 + 5 * 210.0  # 1600 + 1050 = 2650
        expected_total_cost = 10 * 150.0 + 5 * 200.0   # 1500 + 1000 = 2500
        expected_pnl = expected_total_value - expected_total_cost  # 2650 - 2500 = 150
        
        self.assertEqual(summary["total_value"], expected_total_value)
        self.assertEqual(summary["total_cost"], expected_total_cost)
        self.assertEqual(summary["total_pnl"], expected_pnl)
    
    def test_get_transaction_history(self):
        """İşlem geçmişi alma testi"""
        self.tracker.add_position("AAPL", 10, 150.0, "BUY")
        self.tracker.add_position("GOOGL", 5, 200.0, "BUY")
        
        history = self.tracker.get_transaction_history()
        
        self.assertEqual(len(history), 2)
        self.assertIn("timestamp", history[0])
        self.assertIn("symbol", history[0])
        self.assertIn("action", history[0])
        self.assertIn("quantity", history[0])
        self.assertIn("price", history[0])
    
    def test_get_transaction_history_filtered(self):
        """Filtrelenmiş işlem geçmişi alma testi"""
        self.tracker.add_position("AAPL", 10, 150.0, "BUY")
        self.tracker.add_position("GOOGL", 5, 200.0, "BUY")
        
        history = self.tracker.get_transaction_history(symbol="AAPL")
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["symbol"], "AAPL")


class TestDataHandlerIntegration(unittest.TestCase):
    """DataHandler entegrasyon testleri"""
    
    def setUp(self):
        """Her test öncesi çalışan setup metodu"""
        self.market_provider = MarketDataProvider()
        self.portfolio_tracker = PortfolioTracker(10000.0)
    
    @patch('data_handler.yf')
    def test_full_workflow(self, mock_yf):
        """Tam iş akışı entegrasyon testi"""
        # Mock market data
        mock_ticker = Mock()
        mock_ticker.info = {
            'regularMarketPrice': 150.0,
            'regularMarketChange': 5.0,
            'regularMarketChangePercent': 3.45,
            'regularMarketVolume': 1000000
        }
        mock_yf.Ticker.return_value = mock_ticker
        
        # 1. Piyasa verisi al
        market_data = self.market_provider.get_real_time_data("AAPL")
        self.assertIsNotNone(market_data)
        
        # 2. Pozisyon aç
        price = market_data['price']
        success = self.portfolio_tracker.add_position("AAPL", 10, price, "BUY")
        self.assertTrue(success)
        
        # 3. Portföy değerini hesapla
        current_prices = {"AAPL": price + 10.0}  # 10 TL kar
        portfolio_value = self.portfolio_tracker.get_portfolio_value(current_prices)
        expected_value = 10 * (price + 10.0)
        self.assertEqual(portfolio_value, expected_value)
        
        # 4. Portföy özetini al
        summary = self.portfolio_tracker.get_portfolio_summary(current_prices)
        self.assertGreater(summary["total_pnl"], 0)  # Kar olmalı


if __name__ == '__main__':
    # Test çalıştırma
    unittest.main(verbosity=2)
