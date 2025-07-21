"""
test_backtester.py - Backtester modülü için birim testler

Bu dosya Backtester sınıfının tüm fonksiyonlarını test eder:
- Backtest çalıştırma testleri
- Performans metrikler hesaplama testleri
- Rapor oluşturma testleri
- Veri yönetimi testleri
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

from backtester import Backtester
from config import Config


class TestBacktester(unittest.TestCase):
    """Backtester sınıfı için test sınıfı"""
    
    def setUp(self):
        """Her test öncesi çalışan setup metodu"""
        self.backtester = Backtester(
            initial_balance=10000.0,
            start_date='2024-01-01',
            end_date='2024-12-31'
        )
        
        # Mock historical data oluştur
        dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
        np.random.seed(42)
        
        # Gerçekçi fiyat serisi oluştur
        n_days = len(dates)
        price_changes = np.random.normal(0.001, 0.02, n_days)  # %0.1 ortalama, %2 volatilite
        
        base_price = 100.0
        prices = [base_price]
        for change in price_changes[1:]:
            new_price = prices[-1] * (1 + change)
            prices.append(max(new_price, 10.0))  # Minimum fiyat 10 TL
        
        self.mock_historical_data = pd.DataFrame({
            'timestamp': dates,
            'open': [p * np.random.uniform(0.99, 1.01) for p in prices],
            'high': [p * np.random.uniform(1.01, 1.05) for p in prices],
            'low': [p * np.random.uniform(0.95, 0.99) for p in prices],
            'close': prices,
            'volume': np.random.randint(10000, 100000, n_days)
        })
        
        # Mock trading signals
        self.mock_signals = []
        for i in range(0, len(dates), 10):  # Her 10 günde bir signal
            if i < len(dates):
                signal_type = np.random.choice(['BUY', 'SELL', 'HOLD'], p=[0.4, 0.3, 0.3])
                self.mock_signals.append({
                    'timestamp': dates[i],
                    'symbol': 'TEST',
                    'signal': signal_type,
                    'confidence': np.random.uniform(0.6, 0.9),
                    'price': prices[i]
                })
    
    def test_init(self):
        """Backtester başlatma testi"""
        self.assertIsInstance(self.backtester, Backtester)
        self.assertEqual(self.backtester.initial_balance, 10000.0)
        self.assertEqual(self.backtester.current_balance, 10000.0)
        self.assertEqual(len(self.backtester.trades), 0)
        self.assertEqual(len(self.backtester.portfolio), 0)
    
    def test_load_historical_data_success(self):
        """Başarılı geçmiş veri yükleme testi"""
        with patch.object(self.backtester, '_fetch_data') as mock_fetch:
            mock_fetch.return_value = self.mock_historical_data
            
            result = self.backtester.load_historical_data(['TEST'])
            
            self.assertTrue(result)
            self.assertIn('TEST', self.backtester.historical_data)
            self.assertIsInstance(self.backtester.historical_data['TEST'], pd.DataFrame)
    
    def test_load_historical_data_failure(self):
        """Başarısız geçmiş veri yükleme testi"""
        with patch.object(self.backtester, '_fetch_data') as mock_fetch:
            mock_fetch.return_value = pd.DataFrame()  # Boş DataFrame
            
            result = self.backtester.load_historical_data(['INVALID'])
            
            self.assertFalse(result)
    
    def test_execute_trade_buy(self):
        """Alım işlemi yürütme testi"""
        trade_signal = {
            'timestamp': datetime(2024, 6, 15),
            'symbol': 'TEST',
            'signal': 'BUY',
            'confidence': 0.8,
            'price': 105.0
        }
        
        result = self.backtester.execute_trade(trade_signal)
        
        self.assertTrue(result)
        
        # Portfolio'da pozisyon oluşmuş olmalı
        self.assertIn('TEST', self.backtester.portfolio)
        self.assertGreater(self.backtester.portfolio['TEST']['quantity'], 0)
        
        # Bakiye azalmış olmalı
        self.assertLess(self.backtester.current_balance, self.backtester.initial_balance)
        
        # Trade kayıt edilmiş olmalı
        self.assertEqual(len(self.backtester.trades), 1)
        self.assertEqual(self.backtester.trades[0]['action'], 'BUY')
    
    def test_execute_trade_sell(self):
        """Satım işlemi yürütme testi"""
        # Önce bir pozisyon oluştur
        self.backtester.portfolio['TEST'] = {
            'quantity': 50,
            'avg_price': 100.0,
            'total_cost': 5000.0
        }
        self.backtester.current_balance = 5000.0  # Kalan bakiye
        
        trade_signal = {
            'timestamp': datetime(2024, 6, 20),
            'symbol': 'TEST',
            'signal': 'SELL',
            'confidence': 0.7,
            'price': 110.0
        }
        
        result = self.backtester.execute_trade(trade_signal)
        
        self.assertTrue(result)
        
        # Pozisyon satılmış olmalı
        self.assertEqual(self.backtester.portfolio['TEST']['quantity'], 0)
        
        # Bakiye artmış olmalı
        expected_income = 50 * 110.0
        expected_balance = 5000.0 + expected_income
        self.assertEqual(self.backtester.current_balance, expected_balance)
        
        # Trade kayıt edilmiş olmalı
        self.assertEqual(len(self.backtester.trades), 1)
        self.assertEqual(self.backtester.trades[0]['action'], 'SELL')
    
    def test_execute_trade_sell_no_position(self):
        """Pozisyon olmadan satım işlemi testi"""
        trade_signal = {
            'timestamp': datetime(2024, 6, 15),
            'symbol': 'TEST',
            'signal': 'SELL',
            'confidence': 0.8,
            'price': 105.0
        }
        
        result = self.backtester.execute_trade(trade_signal)
        
        # Pozisyon olmadığı için satış yapılamamalı
        self.assertFalse(result)
        self.assertEqual(len(self.backtester.trades), 0)
    
    def test_execute_trade_insufficient_balance(self):
        """Yetersiz bakiye ile alım işlemi testi"""
        # Bakiyeyi düşük yap
        self.backtester.current_balance = 100.0
        
        trade_signal = {
            'timestamp': datetime(2024, 6, 15),
            'symbol': 'TEST',
            'signal': 'BUY',
            'confidence': 0.8,
            'price': 1000.0  # Çok pahalı
        }
        
        result = self.backtester.execute_trade(trade_signal)
        
        # Yetersiz bakiye nedeniyle alım yapılamamalı
        self.assertFalse(result)
        self.assertEqual(len(self.backtester.trades), 0)
    
    def test_calculate_position_size(self):
        """Pozisyon boyutu hesaplama testi"""
        # Risk tabanlı pozisyon boyutu
        price = 100.0
        confidence = 0.8
        risk_per_trade = 0.02  # %2
        
        position_size = self.backtester.calculate_position_size(
            price, confidence, risk_per_trade
        )
        
        self.assertIsInstance(position_size, int)
        self.assertGreater(position_size, 0)
        
        # Maksimum pozisyon kontrolü
        max_investment = self.backtester.current_balance * Config.RISK_MANAGEMENT['max_position_size']
        max_quantity = int(max_investment / price)
        self.assertLessEqual(position_size, max_quantity)
    
    def test_calculate_position_size_high_confidence(self):
        """Yüksek confidence ile pozisyon boyutu testi"""
        size_low = self.backtester.calculate_position_size(100.0, 0.5, 0.02)
        size_high = self.backtester.calculate_position_size(100.0, 0.9, 0.02)
        
        # Yüksek confidence daha büyük pozisyon olmalı
        self.assertGreaterEqual(size_high, size_low)
    
    def test_run_backtest(self):
        """Backtest çalıştırma testi"""
        # Historical data yükle
        self.backtester.historical_data['TEST'] = self.mock_historical_data
        
        # Backtest çalıştır
        with patch.object(self.backtester, 'generate_signals') as mock_signals:
            mock_signals.return_value = self.mock_signals
            
            results = self.backtester.run_backtest(['TEST'])
        
        self.assertIsInstance(results, dict)
        self.assertIn('total_return', results)
        self.assertIn('total_trades', results)
        self.assertIn('win_rate', results)
        self.assertIn('max_drawdown', results)
        self.assertIn('sharpe_ratio', results)
        
        # Trade'ler yapılmış olmalı
        self.assertGreater(len(self.backtester.trades), 0)
    
    def test_calculate_performance_metrics(self):
        """Performans metrikleri hesaplama testi"""
        # Mock trade history oluştur
        self.backtester.trades = [
            {
                'timestamp': datetime(2024, 1, 15),
                'symbol': 'TEST',
                'action': 'BUY',
                'quantity': 10,
                'price': 100.0,
                'pnl': 0
            },
            {
                'timestamp': datetime(2024, 1, 25),
                'symbol': 'TEST',
                'action': 'SELL',
                'quantity': 10,
                'price': 110.0,
                'pnl': 100.0
            },
            {
                'timestamp': datetime(2024, 2, 5),
                'symbol': 'TEST',
                'action': 'BUY',
                'quantity': 15,
                'price': 95.0,
                'pnl': 0
            },
            {
                'timestamp': datetime(2024, 2, 15),
                'symbol': 'TEST',
                'action': 'SELL',
                'quantity': 15,
                'price': 90.0,
                'pnl': -75.0
            }
        ]
        
        # Portfolio value history
        self.backtester.portfolio_values = [
            {'timestamp': datetime(2024, 1, 1), 'total_value': 10000},
            {'timestamp': datetime(2024, 1, 15), 'total_value': 10000},
            {'timestamp': datetime(2024, 1, 25), 'total_value': 11000},
            {'timestamp': datetime(2024, 2, 5), 'total_value': 11000},
            {'timestamp': datetime(2024, 2, 15), 'total_value': 10925}
        ]
        
        metrics = self.backtester.calculate_performance_metrics()
        
        self.assertIsInstance(metrics, dict)
        
        # Temel metrikler
        self.assertIn('total_return', metrics)
        self.assertIn('total_trades', metrics)
        self.assertIn('profitable_trades', metrics)
        self.assertIn('win_rate', metrics)
        self.assertIn('total_pnl', metrics)
        self.assertIn('max_drawdown', metrics)
        self.assertIn('sharpe_ratio', metrics)
        self.assertIn('calmar_ratio', metrics)
        
        # Değer kontrolü
        self.assertEqual(metrics['total_trades'], 4)
        self.assertEqual(metrics['profitable_trades'], 1)
        self.assertEqual(metrics['win_rate'], 0.25)  # 1/4
        self.assertEqual(metrics['total_pnl'], 25.0)  # 100 - 75
    
    def test_calculate_max_drawdown(self):
        """Maksimum düşüş hesaplama testi"""
        # Portfolio value serisi
        portfolio_values = [10000, 11000, 10500, 12000, 9000, 9500, 13000]
        
        max_drawdown = self.backtester.calculate_max_drawdown(portfolio_values)
        
        self.assertIsInstance(max_drawdown, float)
        self.assertLessEqual(max_drawdown, 0)  # Negatif veya sıfır olmalı
        
        # Bu seride maksimum drawdown 12000'den 9000'e düşüş: -25%
        expected_drawdown = (9000 - 12000) / 12000
        self.assertAlmostEqual(max_drawdown, expected_drawdown, places=3)
    
    def test_calculate_sharpe_ratio(self):
        """Sharpe oranı hesaplama testi"""
        # Günlük getiri serisi
        returns = [0.02, -0.01, 0.03, -0.015, 0.025, 0.01, -0.02]
        
        sharpe_ratio = self.backtester.calculate_sharpe_ratio(returns)
        
        self.assertIsInstance(sharpe_ratio, float)
        
        # Pozitif ortalama getiri için Sharpe pozitif olmalı
        avg_return = np.mean(returns)
        if avg_return > 0:
            self.assertGreater(sharpe_ratio, 0)
    
    def test_generate_trading_report(self):
        """İşlem raporu oluşturma testi"""
        # Mock data ekle
        self.backtester.trades = [
            {
                'timestamp': datetime(2024, 1, 15),
                'symbol': 'TEST',
                'action': 'BUY',
                'quantity': 10,
                'price': 100.0,
                'pnl': 0
            }
        ]
        
        self.backtester.portfolio_values = [
            {'timestamp': datetime(2024, 1, 1), 'total_value': 10000},
            {'timestamp': datetime(2024, 1, 31), 'total_value': 10500}
        ]
        
        report = self.backtester.generate_trading_report()
        
        self.assertIsInstance(report, dict)
        self.assertIn('summary', report)
        self.assertIn('performance_metrics', report)
        self.assertIn('trade_analysis', report)
        self.assertIn('monthly_returns', report)
        
        # Summary kontrolü
        summary = report['summary']
        self.assertIn('backtest_period', summary)
        self.assertIn('initial_balance', summary)
        self.assertIn('final_balance', summary)
        self.assertIn('total_return_pct', summary)
    
    def test_export_results(self):
        """Sonuç export etme testi"""
        # Mock data
        self.backtester.trades = [
            {
                'timestamp': datetime(2024, 1, 15),
                'symbol': 'TEST',
                'action': 'BUY',
                'quantity': 10,
                'price': 100.0,
                'pnl': 0
            }
        ]
        
        # Geçici dosya adı
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp_file:
            export_path = tmp_file.name
        
        try:
            result = self.backtester.export_results(export_path)
            self.assertTrue(result)
            
            # Dosya oluşmuş olmalı
            self.assertTrue(os.path.exists(export_path))
            
            # JSON formatında okunabilir olmalı
            import json
            with open(export_path, 'r', encoding='utf-8') as f:
                exported_data = json.load(f)
            
            self.assertIsInstance(exported_data, dict)
            self.assertIn('trades', exported_data)
            
        finally:
            # Geçici dosyayı temizle
            if os.path.exists(export_path):
                os.unlink(export_path)
    
    def test_optimize_parameters(self):
        """Parametre optimizasyonu testi"""
        # Parameter grid
        param_grid = {
            'risk_per_trade': [0.01, 0.02, 0.03],
            'min_confidence': [0.6, 0.7, 0.8]
        }
        
        # Historical data yükle
        self.backtester.historical_data['TEST'] = self.mock_historical_data
        
        with patch.object(self.backtester, 'generate_signals') as mock_signals:
            mock_signals.return_value = self.mock_signals[:5]  # Küçük signal seti
            
            best_params = self.backtester.optimize_parameters(['TEST'], param_grid)
        
        self.assertIsInstance(best_params, dict)
        self.assertIn('best_params', best_params)
        self.assertIn('best_return', best_params)
        self.assertIn('optimization_results', best_params)
        
        # Best params grid'de olmalı
        for param, value in best_params['best_params'].items():
            if param in param_grid:
                self.assertIn(value, param_grid[param])
    
    def test_compare_strategies(self):
        """Strateji karşılaştırma testi"""
        # İki farklı strateji konfigürasyonu
        strategy_configs = {
            'aggressive': {
                'risk_per_trade': 0.03,
                'min_confidence': 0.6
            },
            'conservative': {
                'risk_per_trade': 0.01,
                'min_confidence': 0.8
            }
        }
        
        # Historical data yükle
        self.backtester.historical_data['TEST'] = self.mock_historical_data
        
        with patch.object(self.backtester, 'generate_signals') as mock_signals:
            mock_signals.return_value = self.mock_signals[:5]
            
            comparison = self.backtester.compare_strategies(['TEST'], strategy_configs)
        
        self.assertIsInstance(comparison, dict)
        
        # Her strateji için sonuç olmalı
        for strategy_name in strategy_configs.keys():
            self.assertIn(strategy_name, comparison)
            
            strategy_result = comparison[strategy_name]
            self.assertIn('total_return', strategy_result)
            self.assertIn('sharpe_ratio', strategy_result)
            self.assertIn('max_drawdown', strategy_result)


class TestBacktesterAdvanced(unittest.TestCase):
    """Backtester gelişmiş özellik testleri"""
    
    def setUp(self):
        """Her test öncesi çalışan setup metodu"""
        self.backtester = Backtester(initial_balance=25000.0)
    
    def test_multi_symbol_backtest(self):
        """Çoklu sembol backtest testi"""
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        
        # Her sembol için mock data
        for symbol in symbols:
            dates = pd.date_range('2024-01-01', '2024-06-30', freq='D')
            prices = 100 + np.random.randn(len(dates)).cumsum()
            
            self.backtester.historical_data[symbol] = pd.DataFrame({
                'timestamp': dates,
                'close': prices,
                'volume': np.random.randint(10000, 100000, len(dates))
            })
        
        # Multi-symbol signals
        multi_signals = []
        for i, symbol in enumerate(symbols):
            multi_signals.append({
                'timestamp': datetime(2024, 3, 15 + i),
                'symbol': symbol,
                'signal': 'BUY',
                'confidence': 0.8
            })
        
        with patch.object(self.backtester, 'generate_signals') as mock_signals:
            mock_signals.return_value = multi_signals
            
            results = self.backtester.run_backtest(symbols)
        
        self.assertIsInstance(results, dict)
        
        # Portfolio'da birden fazla sembol olmalı
        symbol_count = sum(1 for symbol in symbols 
                          if symbol in self.backtester.portfolio 
                          and self.backtester.portfolio[symbol]['quantity'] > 0)
        self.assertGreater(symbol_count, 0)
    
    def test_transaction_cost_impact(self):
        """İşlem maliyeti etkisi testi"""
        # Commission'lu ve commission'suz backtest karşılaştırması
        
        # Commission'suz
        backtester_no_commission = Backtester(
            initial_balance=10000.0,
            commission_rate=0.0
        )
        
        # Commission'lu
        backtester_with_commission = Backtester(
            initial_balance=10000.0,
            commission_rate=0.001  # %0.1
        )
        
        # Aynı trade'leri her ikisinde de yap
        trade_signal = {
            'timestamp': datetime(2024, 6, 15),
            'symbol': 'TEST',
            'signal': 'BUY',
            'confidence': 0.8,
            'price': 100.0
        }
        
        result1 = backtester_no_commission.execute_trade(trade_signal)
        result2 = backtester_with_commission.execute_trade(trade_signal)
        
        self.assertTrue(result1)
        self.assertTrue(result2)
        
        # Commission'lu backtester'da bakiye daha az olmalı
        self.assertLess(
            backtester_with_commission.current_balance,
            backtester_no_commission.current_balance
        )
    
    def test_slippage_simulation(self):
        """Kayma (slippage) simülasyonu testi"""
        # Slippage'lı backtester
        backtester_with_slippage = Backtester(
            initial_balance=10000.0,
            slippage_rate=0.001  # %0.1
        )
        
        trade_signal = {
            'timestamp': datetime(2024, 6, 15),
            'symbol': 'TEST',
            'signal': 'BUY',
            'confidence': 0.8,
            'price': 100.0
        }
        
        result = backtester_with_slippage.execute_trade(trade_signal)
        self.assertTrue(result)
        
        # Trade'de slippage uygulanmış olmalı
        executed_trade = backtester_with_slippage.trades[0]
        expected_price_with_slippage = 100.0 * (1 + 0.001)  # BUY için + slippage
        
        self.assertAlmostEqual(
            executed_trade['executed_price'],
            expected_price_with_slippage,
            places=3
        )


class TestBacktesterErrorHandling(unittest.TestCase):
    """Backtester hata yönetimi testleri"""
    
    def setUp(self):
        """Her test öncesi çalışan setup metodu"""
        self.backtester = Backtester()
    
    def test_empty_historical_data(self):
        """Boş geçmiş veri testi"""
        result = self.backtester.run_backtest(['INVALID_SYMBOL'])
        
        # Boş veri ile backtest çalışmamalı
        self.assertIsNone(result)
    
    def test_invalid_date_range(self):
        """Geçersiz tarih aralığı testi"""
        backtester_invalid = Backtester(
            start_date='2024-12-31',
            end_date='2024-01-01'  # End < Start
        )
        
        # Geçersiz tarih aralığı ile çalışmamalı
        self.assertIsNone(backtester_invalid.start_date)
    
    def test_corrupted_signal_data(self):
        """Bozuk signal verisi testi"""
        corrupted_signals = [
            {'symbol': 'TEST'},  # Signal yok
            {'signal': 'BUY'},   # Symbol yok
            {'symbol': 'TEST', 'signal': 'INVALID'},  # Geçersiz signal
            None,  # Null signal
        ]
        
        # Bozuk signaller işlenmemeli
        valid_trades = 0
        for signal in corrupted_signals:
            if signal:
                result = self.backtester.execute_trade(signal)
                if result:
                    valid_trades += 1
        
        self.assertEqual(valid_trades, 0)
    
    def test_extreme_market_conditions(self):
        """Aşırı piyasa koşulları testi"""
        # Çok volatil piyasa verisi
        extreme_data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=10, freq='D'),
            'close': [100, 50, 200, 25, 400, 10, 500, 5, 1000, 1],  # Aşırı volatilite
            'volume': [1000000] * 10
        })
        
        self.backtester.historical_data['EXTREME'] = extreme_data
        
        # Aşırı koşullarda da çalışmalı
        trade_signal = {
            'timestamp': datetime(2024, 1, 5),
            'symbol': 'EXTREME',
            'signal': 'BUY',
            'confidence': 0.8,
            'price': 400.0
        }
        
        result = self.backtester.execute_trade(trade_signal)
        
        # Risk yönetimi devreye girmeli ama hata vermemeli
        self.assertIsInstance(result, bool)


if __name__ == '__main__':
    # Test çalıştırma
    unittest.main(verbosity=2)
