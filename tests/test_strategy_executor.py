"""
test_strategy_executor.py - Strategy Executor modülü için birim testler

Bu dosya strategy_executor modülündeki fonksiyonları test eder:
- Trade decision generation testleri
- Position size calculation testleri
- Risk management testleri
- Portfolio metrics testleri
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

from strategy_executor import (
    generate_trade_decision,
    calculate_position_size,
    apply_risk_management,
    validate_trade_decision,
    calculate_portfolio_metrics
)
import config


class TestStrategyExecutorFunctions(unittest.TestCase):
    """Strategy Executor fonksiyonları için test sınıfı"""
    
    def setUp(self):
        """Her test öncesi çalışan setup metodu"""
        # Test verileri
        self.test_price = 150.0
        self.test_portfolio_value = 10000.0
        self.test_ml_signal = 1
        self.test_sentiment_score = 0.3
        
    def test_generate_trade_decision_buy_signal(self):
        """AL sinyali üretme testleri"""
        # Güçlü AL sinyali - ML AL + Pozitif sentiment
        decision = generate_trade_decision(
            ml_signal=1,
            news_sentiment_score=0.3,
            current_price=self.test_price,
            current_portfolio_value=self.test_portfolio_value
        )
        
        self.assertEqual(decision['decision'], 'BUY')
        self.assertGreater(decision['confidence'], 0.5)
        self.assertIn('reasoning', decision)
        
    def test_generate_trade_decision_sell_signal(self):
        """SAT sinyali üretme testleri"""
        # Güçlü SAT sinyali - ML SAT + Negatif sentiment
        decision = generate_trade_decision(
            ml_signal=-1,
            news_sentiment_score=-0.3,
            current_price=self.test_price,
            current_portfolio_value=self.test_portfolio_value
        )
        
        self.assertEqual(decision['decision'], 'SELL')
        self.assertGreater(decision['confidence'], 0.5)
        self.assertIn('reasoning', decision)
        
    def test_generate_trade_decision_hold_signal(self):
        """HOLD sinyali üretme testleri"""
        # Çelişkili sinyal - ML AL ama negatif sentiment
        decision = generate_trade_decision(
            ml_signal=1,
            news_sentiment_score=-0.5,
            current_price=self.test_price,
            current_portfolio_value=self.test_portfolio_value
        )
        
        self.assertEqual(decision['decision'], 'HOLD')
        self.assertLess(decision['confidence'], 0.5)
        
    def test_generate_trade_decision_string_signals(self):
        """String formatındaki sinyaller testi"""
        # String formatında AL sinyali
        decision = generate_trade_decision(
            ml_signal='BUY',
            news_sentiment_score=0.2,
            current_price=self.test_price,
            current_portfolio_value=self.test_portfolio_value
        )
        
        self.assertEqual(decision['decision'], 'BUY')
        
    def test_calculate_position_size_valid_inputs(self):
        """Position size hesaplama - geçerli girdiler"""
        position_size = calculate_position_size(
            portfolio_value=10000.0,
            current_price=100.0,
            risk_per_trade_percent=1.0,
            decision_confidence=0.8
        )
        
        self.assertIsInstance(position_size, dict)
        self.assertIn('shares', position_size)
        self.assertIn('investment_amount', position_size)
        self.assertGreater(position_size['shares'], 0)
        
    def test_calculate_position_size_zero_portfolio(self):
        """Position size hesaplama - sıfır portföy"""
        position_size = calculate_position_size(
            portfolio_value=0.0,
            current_price=100.0,
            risk_per_trade_percent=1.0,
            decision_confidence=0.8
        )
        
        # Sıfır portföy için None döner
        self.assertIsNone(position_size)
        
    def test_apply_risk_management_valid_decision(self):
        """Risk yönetimi uygulaması - geçerli karar"""
        decision = {
            'decision': 'BUY',
            'confidence': 0.8,
            'reasoning': 'Test reasoning'
        }
        
        result = apply_risk_management(
            decision=decision,
            entry_price=100.0,
            current_price=105.0,
            position_status={'symbol': 'AAPL', 'shares': 100}
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('action', result)
        
    def test_validate_trade_decision_valid(self):
        """Trade decision validation - geçerli karar"""
        decision_data = {
            'decision': 'BUY',
            'confidence': 0.8,
            'symbol': 'AAPL',
            'price': 150.0,
            'timestamp': datetime.now()
        }
        
        result = validate_trade_decision(
            decision_data=decision_data,
            market_hours=True
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('is_valid', result)
        
    def test_calculate_portfolio_metrics_profit(self):
        """Portföy metrikleri hesaplama - kârlı pozisyonlar"""
        positions = [
            {'symbol': 'AAPL', 'shares': 100, 'entry_price': 140.0},
            {'symbol': 'MSFT', 'shares': 50, 'entry_price': 280.0}
        ]
        
        current_prices = {
            'AAPL': 150.0,  # 10$ kâr
            'MSFT': 300.0   # 20$ kâr
        }
        
        metrics = calculate_portfolio_metrics(positions, current_prices)
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('total_value', metrics)
        self.assertIn('total_pnl', metrics)
        self.assertGreater(metrics['total_pnl'], 0)  # Kârlı olmalı
        
    def test_calculate_portfolio_metrics_empty_positions(self):
        """Portföy metrikleri hesaplama - boş pozisyonlar"""
        positions = []
        current_prices = {}
        
        metrics = calculate_portfolio_metrics(positions, current_prices)
        
        self.assertEqual(metrics['total_value'], 0)
        self.assertEqual(metrics['total_pnl'], 0)
        
    @patch('strategy_executor.logger')
    def test_generate_trade_decision_with_logging(self, mock_logger):
        """Trade decision generation - loglama testi"""
        decision = generate_trade_decision(
            ml_signal=1,
            news_sentiment_score=0.2,
            current_price=150.0,
            current_portfolio_value=10000.0
        )
        
        # Logger'ın çağrıldığını kontrol et
        mock_logger.log_debug.assert_called()


if __name__ == '__main__':
    unittest.main()
