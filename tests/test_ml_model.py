"""
test_ml_model.py - MLModel modülü için birim testler

Bu dosya MLModel sınıfının tüm fonksiyonlarını test eder:
- Model eğitimi testleri
- Tahmin yapma testleri
- Model değerlendirme testleri
- Model kaydetme/yükleme testleri
- Hata durumu testleri
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
import sys
import os
import tempfile
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Ana proje klasörünü Python path'ine ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_model import MLModel
from config import Config


class TestMLModel(unittest.TestCase):
    """MLModel sınıfı için test sınıfı"""
    
    def setUp(self):
        """Her test öncesi çalışan setup metodu"""
        self.ml_model = MLModel()
        
        # Test için sample veri oluştur
        np.random.seed(42)
        n_samples = 1000
        n_features = 10
        
        # Feature matrix oluştur
        self.X_train = pd.DataFrame(
            np.random.randn(n_samples, n_features),
            columns=[f'feature_{i}' for i in range(n_features)]
        )
        
        # Binary target (BUY/SELL signals) oluştur
        self.y_train = np.random.choice([0, 1], size=n_samples, p=[0.6, 0.4])
        
        # Test verisi
        self.X_test = pd.DataFrame(
            np.random.randn(200, n_features),
            columns=[f'feature_{i}' for i in range(n_features)]
        )
        self.y_test = np.random.choice([0, 1], size=200, p=[0.6, 0.4])
    
    def test_init(self):
        """MLModel başlatma testi"""
        self.assertIsInstance(self.ml_model, MLModel)
        self.assertIsNotNone(self.ml_model.model)
        self.assertIsInstance(self.ml_model.model, RandomForestClassifier)
        self.assertIsNone(self.ml_model.scaler)
        self.assertEqual(len(self.ml_model.feature_names), 0)
    
    def test_prepare_features(self):
        """Özellik hazırlama testi"""
        result = self.ml_model.prepare_features(self.X_train)
        
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.shape[0], self.X_train.shape[0])
        
        # Scaler oluşturulmuş olmalı
        self.assertIsNotNone(self.ml_model.scaler)
        
        # Feature names kaydedilmiş olmalı
        self.assertEqual(len(self.ml_model.feature_names), self.X_train.shape[1])
        
        # Normalizasyon kontrolü (yaklaşık olarak mean=0, std=1)
        self.assertAlmostEqual(np.mean(result), 0, places=1)
        self.assertAlmostEqual(np.std(result), 1, places=1)
    
    def test_prepare_features_existing_scaler(self):
        """Mevcut scaler ile özellik hazırlama testi"""
        # İlk çağrı ile scaler oluştur
        self.ml_model.prepare_features(self.X_train)
        old_scaler = self.ml_model.scaler
        
        # İkinci çağrı
        result = self.ml_model.prepare_features(self.X_test)
        
        # Aynı scaler kullanılmalı
        self.assertIs(self.ml_model.scaler, old_scaler)
        self.assertEqual(result.shape[0], self.X_test.shape[0])
    
    def test_create_labels(self):
        """Label oluşturma testi"""
        # Sample price data
        prices = pd.Series([100, 102, 101, 105, 103, 108, 106])
        
        result = self.ml_model.create_labels(prices)
        
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(len(result), len(prices) - 1)  # Son fiyat için label yok
        
        # Binary labels (0 veya 1)
        self.assertTrue(all(label in [0, 1] for label in result))
    
    def test_create_labels_with_threshold(self):
        """Threshold ile label oluşturma testi"""
        # Belirgin fiyat değişiklikleri
        prices = pd.Series([100, 105, 95, 110, 90])  # %5+ değişimler
        
        result = self.ml_model.create_labels(prices, threshold=0.03)  # %3 threshold
        
        self.assertIsInstance(result, np.ndarray)
        # %3'ün üstündeki değişimler için labels
        expected_labels = [1, 0, 1, 0]  # +5%, -9.5%, +15.8%, -18.2%
        
        # En azından trend yönü doğru olmalı
        self.assertEqual(len(result), 4)
    
    def test_train_model(self):
        """Model eğitimi testi"""
        result = self.ml_model.train_model(self.X_train, self.y_train)
        
        self.assertTrue(result)
        
        # Model eğitilmiş olmalı
        self.assertTrue(hasattr(self.ml_model.model, 'feature_importances_'))
        
        # Feature importance'lar mevcut olmalı
        importances = self.ml_model.model.feature_importances_
        self.assertEqual(len(importances), self.X_train.shape[1])
        self.assertTrue(all(importance >= 0 for importance in importances))
    
    def test_train_model_empty_data(self):
        """Boş veri ile model eğitimi testi"""
        empty_X = pd.DataFrame()
        empty_y = np.array([])
        
        result = self.ml_model.train_model(empty_X, empty_y)
        
        self.assertFalse(result)
    
    def test_train_model_invalid_data(self):
        """Geçersiz veri ile model eğitimi testi"""
        # X ve y boyutları uyumsuz
        invalid_y = np.array([0, 1])  # Sadece 2 sample
        
        result = self.ml_model.train_model(self.X_train, invalid_y)
        
        self.assertFalse(result)
    
    def test_predict(self):
        """Tahmin yapma testi"""
        # Önce modeli eğit
        self.ml_model.train_model(self.X_train, self.y_train)
        
        # Tahmin yap
        predictions = self.ml_model.predict(self.X_test)
        
        self.assertIsInstance(predictions, np.ndarray)
        self.assertEqual(len(predictions), len(self.X_test))
        
        # Binary predictions (0 veya 1)
        self.assertTrue(all(pred in [0, 1] for pred in predictions))
    
    def test_predict_proba(self):
        """Olasılık tahmini testi"""
        # Önce modeli eğit
        self.ml_model.train_model(self.X_train, self.y_train)
        
        # Olasılık tahminleri
        probabilities = self.ml_model.predict_proba(self.X_test)
        
        self.assertIsInstance(probabilities, np.ndarray)
        self.assertEqual(probabilities.shape, (len(self.X_test), 2))
        
        # Olasılıklar 0-1 arasında olmalı
        self.assertTrue(np.all(probabilities >= 0))
        self.assertTrue(np.all(probabilities <= 1))
        
        # Her satır toplamı 1 olmalı
        row_sums = np.sum(probabilities, axis=1)
        np.testing.assert_array_almost_equal(row_sums, np.ones(len(self.X_test)))
    
    def test_predict_untrained_model(self):
        """Eğitilmemiş model ile tahmin testi"""
        predictions = self.ml_model.predict(self.X_test)
        
        self.assertIsNone(predictions)
        
        probabilities = self.ml_model.predict_proba(self.X_test)
        self.assertIsNone(probabilities)
    
    def test_evaluate_model(self):
        """Model değerlendirme testi"""
        # Modeli eğit
        self.ml_model.train_model(self.X_train, self.y_train)
        
        # Değerlendir
        metrics = self.ml_model.evaluate_model(self.X_test, self.y_test)
        
        self.assertIsInstance(metrics, dict)
        
        expected_metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']
        for metric in expected_metrics:
            self.assertIn(metric, metrics)
            self.assertGreaterEqual(metrics[metric], 0.0)
            self.assertLessEqual(metrics[metric], 1.0)
    
    def test_evaluate_model_untrained(self):
        """Eğitilmemiş model değerlendirme testi"""
        metrics = self.ml_model.evaluate_model(self.X_test, self.y_test)
        
        self.assertIsNone(metrics)
    
    def test_get_feature_importance(self):
        """Feature importance alma testi"""
        # Modeli eğit
        self.ml_model.train_model(self.X_train, self.y_train)
        
        importance = self.ml_model.get_feature_importance()
        
        self.assertIsInstance(importance, dict)
        self.assertEqual(len(importance), self.X_train.shape[1])
        
        # Tüm importance değerleri pozitif olmalı
        for feature, imp_value in importance.items():
            self.assertGreaterEqual(imp_value, 0.0)
        
        # Toplam yaklaşık 1 olmalı (normalized)
        total_importance = sum(importance.values())
        self.assertAlmostEqual(total_importance, 1.0, places=3)
    
    def test_get_feature_importance_untrained(self):
        """Eğitilmemiş model feature importance testi"""
        importance = self.ml_model.get_feature_importance()
        
        self.assertIsNone(importance)
    
    def test_save_model(self):
        """Model kaydetme testi"""
        # Modeli eğit
        self.ml_model.train_model(self.X_train, self.y_train)
        
        # Geçici dosya oluştur
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as tmp_file:
            model_path = tmp_file.name
        
        try:
            # Modeli kaydet
            result = self.ml_model.save_model(model_path)
            self.assertTrue(result)
            
            # Dosya oluşmuş olmalı
            self.assertTrue(os.path.exists(model_path))
            
            # Dosya yüklenebilir olmalı
            loaded_data = joblib.load(model_path)
            self.assertIsInstance(loaded_data, dict)
            self.assertIn('model', loaded_data)
            self.assertIn('scaler', loaded_data)
            self.assertIn('feature_names', loaded_data)
            
        finally:
            # Geçici dosyayı temizle
            if os.path.exists(model_path):
                os.unlink(model_path)
    
    def test_save_model_untrained(self):
        """Eğitilmemiş model kaydetme testi"""
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as tmp_file:
            model_path = tmp_file.name
        
        try:
            result = self.ml_model.save_model(model_path)
            self.assertFalse(result)
            
        finally:
            if os.path.exists(model_path):
                os.unlink(model_path)
    
    def test_load_model(self):
        """Model yükleme testi"""
        # Modeli eğit ve kaydet
        self.ml_model.train_model(self.X_train, self.y_train)
        
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as tmp_file:
            model_path = tmp_file.name
        
        try:
            # Kaydet
            self.ml_model.save_model(model_path)
            
            # Yeni MLModel instance oluştur
            new_ml_model = MLModel()
            
            # Modeli yükle
            result = new_ml_model.load_model(model_path)
            self.assertTrue(result)
            
            # Yüklenen model aynı tahminleri yapmalı
            original_predictions = self.ml_model.predict(self.X_test)
            loaded_predictions = new_ml_model.predict(self.X_test)
            
            np.testing.assert_array_equal(original_predictions, loaded_predictions)
            
        finally:
            if os.path.exists(model_path):
                os.unlink(model_path)
    
    def test_load_model_nonexistent_file(self):
        """Var olmayan dosya yükleme testi"""
        result = self.ml_model.load_model('nonexistent_model.joblib')
        
        self.assertFalse(result)
    
    def test_generate_signals(self):
        """Signal üretme testi"""
        # Modeli eğit
        self.ml_model.train_model(self.X_train, self.y_train)
        
        # Test verisi için signal üret
        signals = self.ml_model.generate_signals(self.X_test)
        
        self.assertIsInstance(signals, list)
        self.assertEqual(len(signals), len(self.X_test))
        
        # Her signal dict olmalı ve gerekli alanları içermeli
        for signal in signals:
            self.assertIsInstance(signal, dict)
            self.assertIn('signal', signal)
            self.assertIn('confidence', signal)
            self.assertIn('probability', signal)
            
            # Signal değerleri
            valid_signals = ['BUY', 'SELL', 'HOLD']
            self.assertIn(signal['signal'], valid_signals)
            
            # Confidence 0-1 arasında
            self.assertGreaterEqual(signal['confidence'], 0.0)
            self.assertLessEqual(signal['confidence'], 1.0)
            
            # Probability 0-1 arasında
            self.assertGreaterEqual(signal['probability'], 0.0)
            self.assertLessEqual(signal['probability'], 1.0)
    
    def test_generate_signals_untrained(self):
        """Eğitilmemiş model signal üretme testi"""
        signals = self.ml_model.generate_signals(self.X_test)
        
        self.assertIsNone(signals)
    
    def test_update_model(self):
        """Model güncelleme (incremental learning) testi"""
        # İlk eğitim
        self.ml_model.train_model(self.X_train, self.y_train)
        original_predictions = self.ml_model.predict(self.X_test)
        
        # Yeni veri ekle
        new_X = pd.DataFrame(
            np.random.randn(100, self.X_train.shape[1]),
            columns=self.X_train.columns
        )
        new_y = np.random.choice([0, 1], size=100)
        
        # Model güncelle
        result = self.ml_model.update_model(new_X, new_y)
        
        # Not: RandomForest incremental learning desteklemez,
        # bu yüzden yeniden eğitim yapılır
        self.assertTrue(result)
        
        # Yeni tahminler yapabilmeli
        new_predictions = self.ml_model.predict(self.X_test)
        self.assertIsInstance(new_predictions, np.ndarray)
    
    def test_cross_validate(self):
        """Cross validation testi"""
        scores = self.ml_model.cross_validate(self.X_train, self.y_train, cv=3)
        
        self.assertIsInstance(scores, dict)
        self.assertIn('mean_score', scores)
        self.assertIn('std_score', scores)
        self.assertIn('individual_scores', scores)
        
        # Skorlar 0-1 arasında olmalı
        self.assertGreaterEqual(scores['mean_score'], 0.0)
        self.assertLessEqual(scores['mean_score'], 1.0)
        
        # Individual scores liste olmalı
        self.assertIsInstance(scores['individual_scores'], list)
        self.assertEqual(len(scores['individual_scores']), 3)  # cv=3
    
    def test_hyperparameter_tuning(self):
        """Hiperparametre tuning testi"""
        # Küçük parameter grid (test süresini kısaltmak için)
        param_grid = {
            'n_estimators': [10, 20],
            'max_depth': [3, 5]
        }
        
        best_params = self.ml_model.hyperparameter_tuning(
            self.X_train, self.y_train, param_grid, cv=2
        )
        
        self.assertIsInstance(best_params, dict)
        
        # En iyi parametreler grid'de olmalı
        for param, value in best_params.items():
            if param in param_grid:
                self.assertIn(value, param_grid[param])
    
    def test_model_performance_tracking(self):
        """Model performans takibi testi"""
        # Modeli eğit
        self.ml_model.train_model(self.X_train, self.y_train)
        
        # Performans takibi başlat
        self.ml_model.start_performance_tracking()
        
        # Birkaç tahmin yap
        for i in range(10):
            single_sample = self.X_test.iloc[i:i+1]
            prediction = self.ml_model.predict(single_sample)
            
            # Gerçek sonucu simulate et
            actual = self.y_test[i]
            self.ml_model.track_prediction(prediction[0], actual)
        
        # Performans istatistiklerini al
        stats = self.ml_model.get_performance_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_predictions', stats)
        self.assertIn('accuracy', stats)
        self.assertIn('precision', stats)
        self.assertIn('recall', stats)
        
        self.assertEqual(stats['total_predictions'], 10)


class TestMLModelEdgeCases(unittest.TestCase):
    """MLModel sınıfı sınır durumları testleri"""
    
    def setUp(self):
        """Her test öncesi çalışan setup metodu"""
        self.ml_model = MLModel()
    
    def test_single_class_labels(self):
        """Tek sınıf label'ları ile eğitim testi"""
        # Sadece 0 değerleri
        X = pd.DataFrame(np.random.randn(100, 5))
        y = np.zeros(100)
        
        result = self.ml_model.train_model(X, y)
        
        # Bu durumda eğitim başarısız olmalı
        self.assertFalse(result)
    
    def test_very_small_dataset(self):
        """Çok küçük veri seti testi"""
        # 5 sample ile eğitim
        X = pd.DataFrame(np.random.randn(5, 3))
        y = np.array([0, 1, 0, 1, 0])
        
        result = self.ml_model.train_model(X, y)
        
        # Küçük veri ile de eğitim yapabilmeli
        self.assertTrue(result)
    
    def test_missing_features_prediction(self):
        """Eksik özellikler ile tahmin testi"""
        # Normal eğitim
        X_train = pd.DataFrame(np.random.randn(100, 5), 
                              columns=['f1', 'f2', 'f3', 'f4', 'f5'])
        y_train = np.random.choice([0, 1], 100)
        
        self.ml_model.train_model(X_train, y_train)
        
        # Eksik özellik ile test
        X_test_missing = pd.DataFrame(np.random.randn(10, 3),
                                     columns=['f1', 'f2', 'f3'])
        
        predictions = self.ml_model.predict(X_test_missing)
        
        # Eksik özellik durumunda None dönemeli
        self.assertIsNone(predictions)
    
    def test_extreme_values_handling(self):
        """Aşırı değerler ile test"""
        # Normal eğitim verisi
        X_train = pd.DataFrame(np.random.randn(100, 3))
        y_train = np.random.choice([0, 1], 100)
        
        self.ml_model.train_model(X_train, y_train)
        
        # Aşırı değerler ile test
        X_extreme = pd.DataFrame([[1e6, -1e6, 0], [0, 0, 1e10]])
        
        predictions = self.ml_model.predict(X_extreme)
        
        # Tahmin yapabilmeli (outlier'lar normalize edilir)
        self.assertIsInstance(predictions, np.ndarray)
        self.assertEqual(len(predictions), 2)


if __name__ == '__main__':
    # Test çalıştırma
    unittest.main(verbosity=2)
