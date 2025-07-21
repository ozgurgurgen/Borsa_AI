"""
Config Modülü Test Dosyası
config.py modülünün tüm fonksiyonlarını ve değişkenlerini test eder.
"""

import pytest
import sys
import os

# Ana proje dizinini sys.path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


class TestConfig:
    """Config modülü test sınıfı"""

    def test_api_keys_structure(self):
        """API anahtarları yapısını test eder"""
        assert hasattr(config, 'API_KEYS')
        assert isinstance(config.API_KEYS, dict)
        assert 'NEWS_API_KEY' in config.API_KEYS
        assert 'ALPHA_VANTAGE_KEY' in config.API_KEYS

    def test_symbols_list(self):
        """Sembol listesini test eder"""
        assert hasattr(config, 'SYMBOLS')
        assert isinstance(config.SYMBOLS, list)
        assert len(config.SYMBOLS) > 0
        # Her sembol string olmalı
        for symbol in config.SYMBOLS:
            assert isinstance(symbol, str)
            assert len(symbol) > 0

    def test_historical_data_settings(self):
        """Tarihsel veri ayarlarını test eder"""
        assert hasattr(config, 'HISTORICAL_DATA_START_DATE')
        assert hasattr(config, 'HISTORICAL_DATA_END_DATE')
        assert hasattr(config, 'PRICE_TIMEFRAME')
        
        assert isinstance(config.HISTORICAL_DATA_START_DATE, str)
        assert isinstance(config.HISTORICAL_DATA_END_DATE, str)
        assert isinstance(config.PRICE_TIMEFRAME, str)
        
        # Tarih formatını kontrol et
        assert len(config.HISTORICAL_DATA_START_DATE) == 10  # YYYY-MM-DD
        assert len(config.HISTORICAL_DATA_END_DATE) == 10
        assert '-' in config.HISTORICAL_DATA_START_DATE
        assert '-' in config.HISTORICAL_DATA_END_DATE

    def test_ml_features_list(self):
        """ML özellikleri listesini test eder"""
        assert hasattr(config, 'ML_FEATURES')
        assert isinstance(config.ML_FEATURES, list)
        assert len(config.ML_FEATURES) > 0
        
        # Beklenen özellikler
        expected_features = ['RSI', 'MACD_Hist', 'SMA_20', 'SMA_50']
        for feature in expected_features:
            assert feature in config.ML_FEATURES

    def test_ml_model_settings(self):
        """ML model ayarlarını test eder"""
        assert hasattr(config, 'ML_MODEL_TYPE')
        assert hasattr(config, 'ML_MODEL_PARAMS')
        
        assert isinstance(config.ML_MODEL_TYPE, str)
        assert isinstance(config.ML_MODEL_PARAMS, dict)
        
        # Model tipi geçerli olmalı
        valid_models = ['RandomForestClassifier', 'LogisticRegression']
        assert config.ML_MODEL_TYPE in valid_models

    def test_sentiment_thresholds(self):
        """Duygu analizi eşiklerini test eder"""
        assert hasattr(config, 'SENTIMENT_THRESHOLD_POSITIVE')
        assert hasattr(config, 'SENTIMENT_THRESHOLD_NEGATIVE')
        
        assert isinstance(config.SENTIMENT_THRESHOLD_POSITIVE, (int, float))
        assert isinstance(config.SENTIMENT_THRESHOLD_NEGATIVE, (int, float))
        
        # Eşikler mantıklı aralıkta olmalı
        assert -1.0 <= config.SENTIMENT_THRESHOLD_NEGATIVE < 0
        assert 0 < config.SENTIMENT_THRESHOLD_POSITIVE <= 1.0
        assert config.SENTIMENT_THRESHOLD_NEGATIVE < config.SENTIMENT_THRESHOLD_POSITIVE

    def test_risk_management_settings(self):
        """Risk yönetimi ayarlarını test eder"""
        assert hasattr(config, 'RISK_PER_TRADE_PERCENT')
        assert hasattr(config, 'STOP_LOSS_PERCENT')
        assert hasattr(config, 'TAKE_PROFIT_PERCENT')
        
        assert isinstance(config.RISK_PER_TRADE_PERCENT, (int, float))
        assert isinstance(config.STOP_LOSS_PERCENT, (int, float))
        assert isinstance(config.TAKE_PROFIT_PERCENT, (int, float))
        
        # Risk yüzdeleri 0-1 arası olmalı
        assert 0 < config.RISK_PER_TRADE_PERCENT <= 1.0
        assert 0 < config.STOP_LOSS_PERCENT <= 1.0
        assert 0 < config.TAKE_PROFIT_PERCENT <= 1.0
        
        # Take profit > stop loss olmalı
        assert config.TAKE_PROFIT_PERCENT > config.STOP_LOSS_PERCENT

    def test_logging_settings(self):
        """Loglama ayarlarını test eder"""
        assert hasattr(config, 'LOG_FILE_PATH')
        assert hasattr(config, 'LOG_LEVEL')
        
        assert isinstance(config.LOG_FILE_PATH, str)
        assert isinstance(config.LOG_LEVEL, str)
        
        # Log level geçerli olmalı
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        assert config.LOG_LEVEL in valid_levels

    def test_path_settings(self):
        """Dosya yolu ayarlarını test eder"""
        assert hasattr(config, 'DATA_SAVE_PATH')
        assert hasattr(config, 'MODEL_SAVE_PATH')
        
        assert isinstance(config.DATA_SAVE_PATH, str)
        assert isinstance(config.MODEL_SAVE_PATH, str)
        
        # Yollar boş olmamalı
        assert len(config.DATA_SAVE_PATH.strip()) > 0
        assert len(config.MODEL_SAVE_PATH.strip()) > 0

    def test_technical_indicators_settings(self):
        """Teknik gösterge ayarlarını test eder"""
        assert hasattr(config, 'TECHNICAL_INDICATORS')
        assert isinstance(config.TECHNICAL_INDICATORS, dict)
        
        # Beklenen anahtarlar
        expected_keys = [
            'RSI_PERIOD', 'MACD_FAST', 'MACD_SLOW', 'MACD_SIGNAL',
            'SMA_SHORT_PERIOD', 'SMA_LONG_PERIOD', 'BB_PERIOD', 'BB_STD',
            'VOLATILITY_PERIOD'
        ]
        
        for key in expected_keys:
            assert key in config.TECHNICAL_INDICATORS
            assert isinstance(config.TECHNICAL_INDICATORS[key], (int, float))
            assert config.TECHNICAL_INDICATORS[key] > 0

    def test_backtest_settings(self):
        """Backtest ayarlarını test eder"""
        assert hasattr(config, 'BACKTEST_INITIAL_CAPITAL')
        assert hasattr(config, 'BACKTEST_COMMISSION')
        
        assert isinstance(config.BACKTEST_INITIAL_CAPITAL, (int, float))
        assert isinstance(config.BACKTEST_COMMISSION, (int, float))
        
        assert config.BACKTEST_INITIAL_CAPITAL > 0
        assert 0 <= config.BACKTEST_COMMISSION <= 1.0

    def test_news_search_keywords(self):
        """Haber arama anahtar kelimelerini test eder"""
        assert hasattr(config, 'NEWS_SEARCH_KEYWORDS')
        assert isinstance(config.NEWS_SEARCH_KEYWORDS, dict)
        
        # Her sembol için anahtar kelimeler olmalı
        for symbol in config.SYMBOLS:
            if symbol in config.NEWS_SEARCH_KEYWORDS:
                keywords = config.NEWS_SEARCH_KEYWORDS[symbol]
                assert isinstance(keywords, list)
                assert len(keywords) > 0
                for keyword in keywords:
                    assert isinstance(keyword, str)
                    assert len(keyword.strip()) > 0

    def test_feature_engineering_settings(self):
        """Feature engineering ayarlarını test eder"""
        assert hasattr(config, 'FEATURE_SCALING_METHOD')
        assert hasattr(config, 'TARGET_LOOKAHEAD_DAYS')
        
        assert isinstance(config.FEATURE_SCALING_METHOD, str)
        assert isinstance(config.TARGET_LOOKAHEAD_DAYS, int)
        
        # Scaling method geçerli olmalı
        valid_methods = ['StandardScaler', 'MinMaxScaler']
        assert config.FEATURE_SCALING_METHOD in valid_methods
        
        assert config.TARGET_LOOKAHEAD_DAYS > 0

    def test_turkish_symbols_if_exists(self):
        """Türk hisseleri varsa test eder"""
        if hasattr(config, 'TURKISH_SYMBOLS'):
            assert isinstance(config.TURKISH_SYMBOLS, list)
            for symbol in config.TURKISH_SYMBOLS:
                assert isinstance(symbol, str)
                assert len(symbol) > 0

    def test_risk_management_dict_if_exists(self):
        """Risk yönetimi dict'i varsa test eder"""
        if hasattr(config, 'RISK_MANAGEMENT'):
            assert isinstance(config.RISK_MANAGEMENT, dict)
            for key, value in config.RISK_MANAGEMENT.items():
                assert isinstance(key, str)
                assert isinstance(value, (int, float, str, bool))

    def test_config_main_execution(self):
        """Config'in main fonksiyonunu test eder"""
        # Bu test config.py'nin çalıştırılabilir olduğunu kontrol eder
        import subprocess
        import sys
        
        result = subprocess.run(
            [sys.executable, 'config.py'],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # Hata olmadan çalışmalı
        assert result.returncode == 0
        assert len(result.stdout) > 0
        
        # Türkçe karakterler için daha esnek kontrol
        output_lower = result.stdout.lower()
        assert any(word in output_lower for word in ['konfigürasyon', 'konfigurasyon', 'basarıyla', 'başarıyla', 'yuklendi', 'yüklendi'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
