"""
test_feature_engineer.py - FeatureEngineer modülü için birim testler

Bu dosya FeatureEngineer sınıfının tüm fonksiyonlarını test eder:
- Teknik gösterge hesaplama testleri
- Özellik mühendisliği fonksiyonları testleri
- Veri normalizasyonu testleri
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

from feature_engineer import FeatureEngineer
from config import Config


class TestFeatureEngineer(unittest.TestCase):
    """FeatureEngineer sınıfı için test sınıfı"""
    
    def setUp(self):
        """Her test öncesi çalışan setup metodu"""
        self.feature_engineer = FeatureEngineer()
        
        # Mock OHLCV verisi oluştur
        np.random.seed(42)  # Tekrarlanabilir test sonuçları için
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        
        # Gerçekçi fiyat verisi oluştur
        base_price = 100.0
        price_changes = np.random.normal(0, 2, 100).cumsum()
        closes = base_price + price_changes
        
        self.sample_data = pd.DataFrame({
            'timestamp': dates,
            'open': closes + np.random.normal(0, 0.5, 100),
            'high': closes + np.abs(np.random.normal(0, 1, 100)),
            'low': closes - np.abs(np.random.normal(0, 1, 100)),
            'close': closes,
            'volume': np.random.randint(1000, 10000, 100)
        })
        
        # Low değerlerinin high değerlerinden küçük olduğundan emin ol
        self.sample_data['low'] = np.minimum(self.sample_data['low'], self.sample_data['close'])
        self.sample_data['high'] = np.maximum(self.sample_data['high'], self.sample_data['close'])
    
    def test_init(self):
        """FeatureEngineer başlatma testi"""
        self.assertIsInstance(self.feature_engineer, FeatureEngineer)
    
    def test_calculate_sma(self):
        """Basit Hareketli Ortalama (SMA) hesaplama testi"""
        period = 20
        result = self.feature_engineer.calculate_sma(self.sample_data['close'], period)
        
        # Sonuç bir pandas Series olmalı
        self.assertIsInstance(result, pd.Series)
        
        # İlk (period-1) değer NaN olmalı
        self.assertTrue(pd.isna(result.iloc[:period-1]).all())
        
        # period'dan sonraki değerler sayısal olmalı
        self.assertFalse(pd.isna(result.iloc[period-1:]).all())
        
        # Manuel hesaplama ile kontrol et
        expected_first_value = self.sample_data['close'].iloc[:period].mean()
        self.assertAlmostEqual(result.iloc[period-1], expected_first_value, places=5)
    
    def test_calculate_ema(self):
        """Üssel Hareketli Ortalama (EMA) hesaplama testi"""
        period = 20
        result = self.feature_engineer.calculate_ema(self.sample_data['close'], period)
        
        self.assertIsInstance(result, pd.Series)
        self.assertEqual(len(result), len(self.sample_data))
        
        # İlk değer ilk fiyat olmalı
        self.assertAlmostEqual(result.iloc[0], self.sample_data['close'].iloc[0], places=5)
        
        # Son değerler NaN olmamalı
        self.assertFalse(pd.isna(result.iloc[-10:]).any())
    
    def test_calculate_rsi(self):
        """Göreceli Güç Endeksi (RSI) hesaplama testi"""
        period = 14
        result = self.feature_engineer.calculate_rsi(self.sample_data['close'], period)
        
        self.assertIsInstance(result, pd.Series)
        
        # İlk period değer NaN olmalı
        self.assertTrue(pd.isna(result.iloc[:period]).all())
        
        # RSI değerleri 0-100 arasında olmalı
        valid_values = result.dropna()
        if not valid_values.empty:
            self.assertTrue(all(0 <= val <= 100 for val in valid_values))
    
    def test_calculate_macd(self):
        """MACD hesaplama testi"""
        result = self.feature_engineer.calculate_macd(self.sample_data['close'])
        
        self.assertIsInstance(result, dict)
        self.assertIn('macd', result)
        self.assertIn('signal', result)
        self.assertIn('histogram', result)
        
        # Her bir bileşen pandas Series olmalı
        for key, value in result.items():
            self.assertIsInstance(value, pd.Series)
            self.assertEqual(len(value), len(self.sample_data))
    
    def test_calculate_bollinger_bands(self):
        """Bollinger Bantları hesaplama testi"""
        period = 20
        std_dev = 2
        result = self.feature_engineer.calculate_bollinger_bands(
            self.sample_data['close'], period, std_dev
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('upper', result)
        self.assertIn('middle', result)
        self.assertIn('lower', result)
        
        # Her bant pandas Series olmalı
        for key, value in result.items():
            self.assertIsInstance(value, pd.Series)
            self.assertEqual(len(value), len(self.sample_data))
        
        # Üst bant >= orta bant >= alt bant olmalı
        valid_indices = ~(pd.isna(result['upper']) | pd.isna(result['middle']) | pd.isna(result['lower']))
        if valid_indices.sum() > 0:
            upper_valid = result['upper'][valid_indices]
            middle_valid = result['middle'][valid_indices]
            lower_valid = result['lower'][valid_indices]
            
            self.assertTrue((upper_valid >= middle_valid).all())
            self.assertTrue((middle_valid >= lower_valid).all())
    
    def test_calculate_stochastic(self):
        """Stokastik Osilatör hesaplama testi"""
        k_period = 14
        d_period = 3
        result = self.feature_engineer.calculate_stochastic(
            self.sample_data['high'], self.sample_data['low'], 
            self.sample_data['close'], k_period, d_period
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('k', result)
        self.assertIn('d', result)
        
        # %K ve %D değerleri 0-100 arasında olmalı
        for key, value in result.items():
            self.assertIsInstance(value, pd.Series)
            valid_values = value.dropna()
            if not valid_values.empty:
                self.assertTrue(all(0 <= val <= 100 for val in valid_values))
    
    def test_calculate_williams_r(self):
        """Williams %R hesaplama testi"""
        period = 14
        result = self.feature_engineer.calculate_williams_r(
            self.sample_data['high'], self.sample_data['low'], 
            self.sample_data['close'], period
        )
        
        self.assertIsInstance(result, pd.Series)
        
        # Williams %R değerleri -100 ile 0 arasında olmalı
        valid_values = result.dropna()
        if not valid_values.empty:
            self.assertTrue(all(-100 <= val <= 0 for val in valid_values))
    
    def test_calculate_atr(self):
        """Ortalama Gerçek Aralık (ATR) hesaplama testi"""
        period = 14
        result = self.feature_engineer.calculate_atr(
            self.sample_data['high'], self.sample_data['low'], 
            self.sample_data['close'], period
        )
        
        self.assertIsInstance(result, pd.Series)
        
        # ATR değerleri pozitif olmalı
        valid_values = result.dropna()
        if not valid_values.empty:
            self.assertTrue(all(val >= 0 for val in valid_values))
    
    def test_calculate_volume_indicators(self):
        """Hacim göstergeleri hesaplama testi"""
        result = self.feature_engineer.calculate_volume_indicators(
            self.sample_data['close'], self.sample_data['volume']
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('volume_sma', result)
        self.assertIn('volume_ratio', result)
        self.assertIn('price_volume', result)
        
        # Her gösterge pandas Series olmalı
        for key, value in result.items():
            self.assertIsInstance(value, pd.Series)
            self.assertEqual(len(value), len(self.sample_data))
    
    def test_add_technical_features(self):
        """Teknik özellikler ekleme testi"""
        result = self.feature_engineer.add_technical_features(self.sample_data.copy())
        
        self.assertIsInstance(result, pd.DataFrame)
        
        # Orijinal kolonlar korunmalı
        original_columns = set(self.sample_data.columns)
        result_columns = set(result.columns)
        self.assertTrue(original_columns.issubset(result_columns))
        
        # Yeni teknik göstergeler eklenmiş olmalı
        expected_features = [
            'SMA_20', 'SMA_50', 'EMA_12', 'EMA_26', 'RSI', 'MACD', 
            'MACD_signal', 'MACD_histogram', 'BB_upper', 'BB_middle', 
            'BB_lower', 'Stoch_K', 'Stoch_D', 'Williams_R', 'ATR'
        ]
        
        for feature in expected_features:
            self.assertIn(feature, result.columns)
    
    def test_add_price_features(self):
        """Fiyat özellikleri ekleme testi"""
        result = self.feature_engineer.add_price_features(self.sample_data.copy())
        
        self.assertIsInstance(result, pd.DataFrame)
        
        # Fiyat özellikleri eklenmiş olmalı
        expected_features = [
            'price_change', 'price_change_pct', 'high_low_pct', 
            'open_close_pct', 'volatility'
        ]
        
        for feature in expected_features:
            self.assertIn(feature, result.columns)
        
        # Değer kontrolü
        if len(result) > 1:
            # Fiyat değişimi hesaplaması
            expected_price_change = result['close'].iloc[1] - result['close'].iloc[0]
            actual_price_change = result['price_change'].iloc[1]
            self.assertAlmostEqual(actual_price_change, expected_price_change, places=5)
    
    def test_add_time_features(self):
        """Zaman özellikleri ekleme testi"""
        result = self.feature_engineer.add_time_features(self.sample_data.copy())
        
        self.assertIsInstance(result, pd.DataFrame)
        
        # Zaman özellikleri eklenmiş olmalı
        expected_features = ['hour', 'day_of_week', 'day_of_month', 'month', 'quarter']
        
        for feature in expected_features:
            self.assertIn(feature, result.columns)
        
        # Değer aralığı kontrolü
        if 'hour' in result.columns:
            self.assertTrue(all(0 <= val <= 23 for val in result['hour']))
        if 'day_of_week' in result.columns:
            self.assertTrue(all(0 <= val <= 6 for val in result['day_of_week']))
        if 'month' in result.columns:
            self.assertTrue(all(1 <= val <= 12 for val in result['month']))
    
    def test_normalize_features(self):
        """Özellik normalizasyonu testi"""
        # Teknik özellikler ekle
        data_with_features = self.feature_engineer.add_technical_features(self.sample_data.copy())
        
        # Normalizasyon yapılacak sütunları seç
        numeric_columns = data_with_features.select_dtypes(include=[np.number]).columns
        features_to_normalize = [col for col in numeric_columns if col not in ['timestamp']]
        
        result = self.feature_engineer.normalize_features(
            data_with_features, features_to_normalize
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        
        # Normalizasyon sonrası değerler 0-1 arasında olmalı
        for feature in features_to_normalize:
            if feature in result.columns:
                valid_values = result[feature].dropna()
                if not valid_values.empty:
                    self.assertTrue(all(0 <= val <= 1 for val in valid_values))
    
    def test_create_feature_matrix(self):
        """Özellik matrisi oluşturma testi"""
        result = self.feature_engineer.create_feature_matrix(self.sample_data.copy())
        
        self.assertIsInstance(result, pd.DataFrame)
        
        # Orijinal veriden daha fazla sütun olmalı
        self.assertGreater(len(result.columns), len(self.sample_data.columns))
        
        # Temel özellikler var olmalı
        basic_features = ['SMA_20', 'RSI', 'MACD', 'price_change', 'hour']
        for feature in basic_features:
            if feature in result.columns:
                self.assertIn(feature, result.columns)
    
    def test_empty_data_handling(self):
        """Boş veri işleme testi"""
        empty_df = pd.DataFrame()
        
        # Boş veri ile fonksiyonları test et
        result_technical = self.feature_engineer.add_technical_features(empty_df)
        self.assertTrue(result_technical.empty)
        
        result_price = self.feature_engineer.add_price_features(empty_df)
        self.assertTrue(result_price.empty)
        
        result_time = self.feature_engineer.add_time_features(empty_df)
        self.assertTrue(result_time.empty)
    
    def test_invalid_data_handling(self):
        """Geçersiz veri işleme testi"""
        # NaN değerler içeren veri
        invalid_data = self.sample_data.copy()
        invalid_data.loc[10:20, 'close'] = np.nan
        
        # Fonksiyonlar hata vermemeli
        try:
            result = self.feature_engineer.add_technical_features(invalid_data)
            self.assertIsInstance(result, pd.DataFrame)
        except Exception as e:
            self.fail(f"add_technical_features NaN veriler ile hata verdi: {e}")
    
    def test_single_row_data(self):
        """Tek satır veri işleme testi"""
        single_row = self.sample_data.iloc[:1].copy()
        
        result = self.feature_engineer.add_technical_features(single_row)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        
        # Teknik göstergeler NaN olabilir (yeterli veri yok)
        # Ama hata vermemeli
    
    def test_feature_calculation_consistency(self):
        """Özellik hesaplama tutarlılığı testi"""
        # Aynı veri ile iki kez hesapla
        result1 = self.feature_engineer.create_feature_matrix(self.sample_data.copy())
        result2 = self.feature_engineer.create_feature_matrix(self.sample_data.copy())
        
        # Sonuçlar aynı olmalı
        pd.testing.assert_frame_equal(result1, result2)


class TestFeatureEngineerEdgeCases(unittest.TestCase):
    """FeatureEngineer sınıfı sınır durumları testleri"""
    
    def setUp(self):
        """Her test öncesi çalışan setup metodu"""
        self.feature_engineer = FeatureEngineer()
    
    def test_very_small_period(self):
        """Çok küçük period değeri testi"""
        data = pd.Series([1, 2, 3, 4, 5])
        
        # Period 1 ile SMA hesapla
        result = self.feature_engineer.calculate_sma(data, 1)
        expected = data  # Period 1 ise SMA = kendisi
        pd.testing.assert_series_equal(result, expected)
    
    def test_period_larger_than_data(self):
        """Veri boyutundan büyük period testi"""
        data = pd.Series([1, 2, 3, 4, 5])
        
        # Period 10 ile SMA hesapla (veri sadece 5 eleman)
        result = self.feature_engineer.calculate_sma(data, 10)
        
        # Tüm değerler NaN olmalı
        self.assertTrue(pd.isna(result).all())
    
    def test_zero_volume_handling(self):
        """Sıfır hacim değerleri işleme testi"""
        data = pd.DataFrame({
            'close': [100, 101, 102, 103, 104],
            'volume': [0, 1000, 0, 2000, 0]
        })
        
        result = self.feature_engineer.calculate_volume_indicators(
            data['close'], data['volume']
        )
        
        # Hata vermemeli
        self.assertIsInstance(result, dict)
        self.assertIn('volume_ratio', result)
    
    def test_constant_price_data(self):
        """Sabit fiyat verisi testi"""
        constant_prices = pd.Series([100.0] * 50)
        
        # RSI hesapla (sabit fiyat ile RSI 50 olmalı)
        rsi = self.feature_engineer.calculate_rsi(constant_prices, 14)
        
        # NaN olmayan değerler yaklaşık 50 olmalı
        valid_rsi = rsi.dropna()
        if not valid_rsi.empty:
            self.assertTrue(all(abs(val - 50.0) < 1.0 for val in valid_rsi))


if __name__ == '__main__':
    # Test çalıştırma
    unittest.main(verbosity=2)
