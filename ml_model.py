"""
AI-FTB (AI-Powered Financial Trading Bot) Machine Learning Model Module

Bu modül, makine öğrenimi modelini eğitir, kaydeder, yükler ve alım-satım 
sinyalleri üretir. Scikit-learn kütüphanesini kullanarak sınıflandırma 
modelleri oluşturur.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
import joblib
import os
from datetime import datetime
import config
import logger


def prepare_data_for_ml(dataframe, target_column_name='Target', test_size=0.2):
    """
    DataFrame'i makine öğrenimi için X (özellikler) ve y (hedef) olarak ayırır.
    Hedef olarak bir sonraki günün kapanış fiyatının artıp artmayacağını 
    (1 artış, 0 düşüş/sabit) binary sınıflandırma problemi olarak tanımlar.
    
    Args:
        dataframe (pandas.DataFrame): Özellikler ve hedef içeren veri
        target_column_name (str): Hedef değişken sütun adı
        test_size (float): Test verisi oranı (0.0-1.0 arası)
    
    Returns:
        tuple: (X_train, X_test, y_train, y_test, feature_names)
        None: Hata durumunda
        
    Raises:
        Exception: Veri hazırlama hatalarında
    """
    try:
        logger.log_info("Veri ML için hazırlanıyor...")
        
        # Hedef sütununu kontrol et
        if target_column_name not in dataframe.columns:
            logger.log_error(f"Hedef sütun bulunamadı: {target_column_name}")
            return None
            
        # ML özelliklerini config'ten al ve mevcut olanları filtrele
        ml_features = config.ML_FEATURES.copy()
        
        # Ölçeklendirilmiş özellikleri de dahil et
        scaled_features = [f"{feature}_scaled" for feature in ml_features]
        all_possible_features = ml_features + scaled_features
        
        # Mevcut özellikleri bul
        available_features = [f for f in all_possible_features if f in dataframe.columns]
        
        if not available_features:
            logger.log_error("Kullanılabilir ML özelliği bulunamadı")
            return None
            
        logger.log_info(f"Kullanılacak özellikler ({len(available_features)}): {available_features}")
        
        # Veriyi temizle - NaN içeren satırları kaldır
        clean_data = dataframe[available_features + [target_column_name]].dropna()
        
        if len(clean_data) < 100:  # Minimum veri kontrolü
            logger.log_error(f"Yetersiz temiz veri: {len(clean_data)} satır")
            return None
            
        # X (özellikler) ve y (hedef) olarak ayır
        X = clean_data[available_features]
        y = clean_data[target_column_name]
        
        # Hedef değişkenin dağılımını kontrol et
        target_distribution = y.value_counts()
        logger.log_info(f"Hedef dağılımı: {target_distribution.to_dict()}")
        
        # Çok dengesiz veri uyarısı
        min_class_ratio = target_distribution.min() / target_distribution.sum()
        if min_class_ratio < 0.1:
            logger.log_warning(f"Dengesiz veri seti: En az sınıf oranı {min_class_ratio:.2%}")
            
        # Eğitim-test ayrımı
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=test_size, 
            random_state=42, 
            stratify=y  # Sınıf dağılımını korur
        )
        
        logger.log_info(f"Veri bölümü: Eğitim={len(X_train)}, Test={len(X_test)}")
        logger.log_info(f"Eğitim hedef dağılımı: {y_train.value_counts().to_dict()}")
        
        return X_train, X_test, y_train, y_test, available_features
        
    except Exception as e:
        logger.log_error(f"Veri hazırlama hatası: {e}", exc_info=True)
        return None


def train_model(X_train, y_train, model_type=None, params=None, use_grid_search=False):
    """
    Belirtilen model tipi ve parametrelerle makine öğrenimi modelini eğitir.
    GridSearchCV ile hiperparametre optimizasyonu yapabilir.
    
    Args:
        X_train (pandas.DataFrame): Eğitim özellikleri
        y_train (pandas.Series): Eğitim hedefleri
        model_type (str): Model tipi ('RandomForestClassifier', 'LogisticRegression')
        params (dict): Model parametreleri
        use_grid_search (bool): Hiperparametre optimizasyonu yapılsın mı
    
    Returns:
        sklearn model object: Eğitilmiş model
        None: Hata durumunda
        
    Raises:
        Exception: Model eğitimi hatalarında
    """
    try:
        # Parametreleri config'ten al
        if model_type is None:
            model_type = config.ML_MODEL_TYPE
        if params is None:
            params = config.ML_MODEL_PARAMS.copy()
            
        logger.log_info(f"{model_type} modeli eğitiliyor...")
        logger.log_info(f"Model parametreleri: {params}")
        
        # Model seçimi
        if model_type == 'RandomForestClassifier':
            model = RandomForestClassifier(**params)
        elif model_type == 'LogisticRegression':
            model = LogisticRegression(**params)
        else:
            logger.log_error(f"Desteklenmeyen model tipi: {model_type}")
            return None
            
        # Grid Search ile hiperparametre optimizasyonu
        if use_grid_search:
            logger.log_info("Hiperparametre optimizasyonu yapılıyor...")
            
            if model_type == 'RandomForestClassifier':
                param_grid = {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [5, 10, 15, None],
                    'min_samples_split': [2, 5, 10]
                }
            elif model_type == 'LogisticRegression':
                param_grid = {
                    'C': [0.1, 1.0, 10.0],
                    'penalty': ['l1', 'l2'],
                    'solver': ['liblinear', 'saga']
                }
            else:
                param_grid = {}
                
            if param_grid:
                grid_search = GridSearchCV(
                    model, param_grid, 
                    cv=5, scoring='accuracy', 
                    n_jobs=-1, verbose=1
                )
                grid_search.fit(X_train, y_train)
                model = grid_search.best_estimator_
                logger.log_info(f"En iyi parametreler: {grid_search.best_params_}")
                logger.log_info(f"En iyi CV skoru: {grid_search.best_score_:.4f}")
            else:
                model.fit(X_train, y_train)
        else:
            # Normal eğitim
            model.fit(X_train, y_train)
            
        # Cross-validation ile model performansını değerlendir
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        logger.log_info(f"Cross-validation accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Özellik önemlerini logla (varsa)
        if hasattr(model, 'feature_importances_'):
            feature_importance = pd.DataFrame({
                'feature': X_train.columns,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            logger.log_info("En önemli 5 özellik:")
            for _, row in feature_importance.head().iterrows():
                logger.log_info(f"  {row['feature']}: {row['importance']:.4f}")
                
        logger.log_info("Model eğitimi tamamlandı")
        return model
        
    except Exception as e:
        logger.log_error(f"Model eğitimi hatası: {e}", exc_info=True)
        return None


def predict_signal(model, X_test, threshold=0.5):
    """
    Eğitilmiş modeli kullanarak yeni verilere dayanarak alım-satım sinyalleri 
    tahmin eder. Model çıktısını AL/BEKLE/SAT sinyallerine dönüştürür.
    
    Args:
        model: Eğitilmiş sklearn modeli
        X_test (pandas.DataFrame): Test özellikleri
        threshold (float): Karar eşiği (0.0-1.0 arası)
    
    Returns:
        tuple: (predictions, probabilities, signals)
        None: Hata durumunda
        
    Raises:
        Exception: Tahmin hatalarında
    """
    try:
        logger.log_info(f"{len(X_test)} örnek için sinyal tahmini yapılıyor...")
        
        # Tahmin yap
        predictions = model.predict(X_test)
        
        # Olasılık tahmini (varsa)
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(X_test)[:, 1]  # Pozitif sınıf olasılığı
        else:
            probabilities = predictions.astype(float)
            
        # Sinyallere dönüştür
        signals = []
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            if prob >= threshold + 0.2:  # Yüksek güven ile AL
                signal = 'BUY'
            elif prob <= threshold - 0.2:  # Yüksek güven ile SAT
                signal = 'SELL'
            elif pred == 1 and prob >= threshold:  # Orta güven ile AL
                signal = 'BUY'
            elif pred == 0 and prob <= threshold:  # Orta güven ile SAT
                signal = 'SELL'
            else:
                signal = 'HOLD'  # Belirsizlik durumunda bekle
                
            signals.append(signal)
            
        # Sinyal dağılımını logla
        signal_counts = pd.Series(signals).value_counts()
        logger.log_info(f"Sinyal dağılımı: {signal_counts.to_dict()}")
        
        return predictions, probabilities, signals
        
    except Exception as e:
        logger.log_error(f"Sinyal tahmini hatası: {e}", exc_info=True)
        return None


def evaluate_model(model, X_test, y_test):
    """
    Modelin performansını çeşitli metriklerle değerlendirir ve detaylı 
    rapor oluşturur.
    
    Args:
        model: Eğitilmiş sklearn modeli
        X_test (pandas.DataFrame): Test özellikleri
        y_test (pandas.Series): Test hedefleri
    
    Returns:
        dict: Performans metrikleri
        None: Hata durumunda
        
    Raises:
        Exception: Değerlendirme hatalarında
    """
    try:
        logger.log_info("Model performansı değerlendiriliyor...")
        
        # Tahminler
        y_pred = model.predict(X_test)
        
        # Olasılık tahminleri (varsa)
        if hasattr(model, 'predict_proba'):
            y_prob = model.predict_proba(X_test)[:, 1]
        else:
            y_prob = y_pred.astype(float)
            
        # Temel metrikler
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        # ROC AUC (binary classification için)
        try:
            roc_auc = roc_auc_score(y_test, y_prob)
        except:
            roc_auc = 0.5
            
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        
        # Sonuçları logla
        logger.log_info("=== Model Performans Raporu ===")
        logger.log_info(f"Accuracy: {accuracy:.4f}")
        logger.log_info(f"Precision: {precision:.4f}")
        logger.log_info(f"Recall: {recall:.4f}")
        logger.log_info(f"F1-Score: {f1:.4f}")
        logger.log_info(f"ROC AUC: {roc_auc:.4f}")
        logger.log_info(f"Confusion Matrix:\\n{cm}")
        
        # Detaylı classification report
        class_report = classification_report(y_test, y_pred, output_dict=True)
        logger.log_info("Detaylı sınıf raporu:")
        for class_name, metrics in class_report.items():
            if isinstance(metrics, dict):
                logger.log_info(f"  {class_name}: Precision={metrics.get('precision', 0):.3f}, Recall={metrics.get('recall', 0):.3f}, F1={metrics.get('f1-score', 0):.3f}")
                
        # Performans metriklerini dict olarak döndür
        performance_metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'roc_auc': roc_auc,
            'confusion_matrix': cm.tolist(),
            'classification_report': class_report,
            'test_samples': len(y_test)
        }
        
        return performance_metrics
        
    except Exception as e:
        logger.log_error(f"Model değerlendirme hatası: {e}", exc_info=True)
        return None


def save_model(model, filename, symbol=None, metadata=None):
    """
    Eğitilmiş modeli joblib kullanarak dosyaya kaydeder.
    Model ile birlikte metadata da kaydedilir.
    
    Args:
        model: Eğitilmiş sklearn modeli
        filename (str): Dosya adı (uzantı olmadan)
        symbol (str): Sembol adı (dosya adına eklenir)
        metadata (dict): Model hakkında ek bilgiler
    
    Returns:
        bool: Başarı durumu
        
    Raises:
        Exception: Dosya kaydetme hatalarında
    """
    try:
        # Dosya yolunu oluştur
        if symbol:
            filename = f"{symbol}_{filename}"
            
        model_path = os.path.join(config.MODEL_SAVE_PATH, f"{filename}.joblib")
        metadata_path = os.path.join(config.MODEL_SAVE_PATH, f"{filename}_metadata.json")
        
        # Dizini oluştur
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Modeli kaydet
        joblib.dump(model, model_path)
        
        # Metadata kaydet
        if metadata is None:
            metadata = {}
            
        metadata.update({
            'model_type': type(model).__name__,
            'save_date': datetime.now().isoformat(),
            'file_path': model_path
        })
        
        import json
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        logger.log_info(f"Model kaydedildi: {model_path}")
        logger.log_info(f"Metadata kaydedildi: {metadata_path}")
        
        return True
        
    except Exception as e:
        logger.log_error(f"Model kaydetme hatası: {e}", exc_info=True)
        return False


def load_model(filename, symbol=None):
    """
    Kaydedilmiş modeli dosyadan yükler.
    
    Args:
        filename (str): Dosya adı (uzantı olmadan)
        symbol (str): Sembol adı (dosya adından çıkarılır)
    
    Returns:
        tuple: (model, metadata)
        None: Hata durumunda
        
    Raises:
        Exception: Dosya okuma hatalarında
    """
    try:
        # Dosya yolunu oluştur
        if symbol:
            filename = f"{symbol}_{filename}"
            
        model_path = os.path.join(config.MODEL_SAVE_PATH, f"{filename}.joblib")
        metadata_path = os.path.join(config.MODEL_SAVE_PATH, f"{filename}_metadata.json")
        
        if not os.path.exists(model_path):
            logger.log_warning(f"Model dosyası bulunamadı: {model_path}")
            return None
            
        # Modeli yükle
        model = joblib.load(model_path)
        
        # Metadata yükle
        metadata = {}
        if os.path.exists(metadata_path):
            import json
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                
        logger.log_info(f"Model yüklendi: {model_path}")
        logger.log_info(f"Model tipi: {metadata.get('model_type', 'Bilinmiyor')}")
        
        return model, metadata
        
    except Exception as e:
        logger.log_error(f"Model yükleme hatası: {e}", exc_info=True)
        return None


def model_feature_analysis(model, feature_names):
    """
    Model özellik analizini yapar ve önem sıralaması oluşturur.
    
    Args:
        model: Eğitilmiş sklearn modeli
        feature_names (list): Özellik isimleri
    
    Returns:
        pandas.DataFrame: Özellik önem sıralaması
    """
    try:
        if not hasattr(model, 'feature_importances_'):
            logger.log_warning("Model özellik önem değerleri desteklemiyor")
            return None
            
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Normalize et (yüzdelik)
        importance_df['importance_pct'] = (importance_df['importance'] / importance_df['importance'].sum()) * 100
        
        logger.log_info("Özellik önem analizi:")
        for _, row in importance_df.head(10).iterrows():
            logger.log_info(f"  {row['feature']}: {row['importance']:.4f} ({row['importance_pct']:.1f}%)")
            
        return importance_df
        
    except Exception as e:
        logger.log_error(f"Özellik analizi hatası: {e}")
        return None


if __name__ == "__main__":
    """
    ML Model modülü test kodu
    """
    print("=== AI-FTB ML Model Test ===")
    
    # Test verisi oluştur
    np.random.seed(42)
    n_samples = 1000
    
    # Özellikleri simüle et
    feature_data = {
        'RSI': np.random.uniform(20, 80, n_samples),
        'MACD_Hist': np.random.normal(0, 0.5, n_samples),
        'SMA_20': np.random.uniform(90, 110, n_samples),
        'Volume_Change': np.random.normal(0, 0.3, n_samples),
        'BB_Upper': np.random.uniform(105, 115, n_samples),
        'Volatility': np.random.uniform(0.1, 0.5, n_samples)
    }
    
    # Hedef değişken (örnek mantık: RSI > 70 ise 0, RSI < 30 ise 1, diğerleri rastgele)
    target = []
    for i in range(n_samples):
        if feature_data['RSI'][i] > 70:
            target.append(0)  # Aşırı alım, düşüş beklentisi
        elif feature_data['RSI'][i] < 30:
            target.append(1)  # Aşırı satım, yükseliş beklentisi
        else:
            target.append(np.random.choice([0, 1], p=[0.5, 0.5]))
            
    # DataFrame oluştur
    test_df = pd.DataFrame(feature_data)
    test_df['Target'] = target
    
    print(f"Test verisi oluşturuldu: {len(test_df)} satır, {len(test_df.columns)-1} özellik")
    print(f"Hedef dağılımı: {pd.Series(target).value_counts().to_dict()}")
    
    # Veri hazırlama testi
    print("\\n1. Veri ML için hazırlanıyor...")
    ml_data = prepare_data_for_ml(test_df)
    
    if ml_data:
        X_train, X_test, y_train, y_test, feature_names = ml_data
        print(f"✅ Veri hazırlandı: Eğitim={len(X_train)}, Test={len(X_test)}")
        
        # Model eğitimi testi
        print("\\n2. Model eğitiliyor...")
        model = train_model(X_train, y_train)
        
        if model:
            print("✅ Model eğitimi tamamlandı")
            
            # Model değerlendirme testi
            print("\\n3. Model değerlendiriliyor...")
            performance = evaluate_model(model, X_test, y_test)
            
            if performance:
                print(f"✅ Model performansı: Accuracy={performance['accuracy']:.3f}")
                
                # Sinyal tahmini testi
                print("\\n4. Sinyal tahminleri...")
                prediction_result = predict_signal(model, X_test)
                
                if prediction_result:
                    predictions, probabilities, signals = prediction_result
                    signal_counts = pd.Series(signals).value_counts()
                    print(f"✅ Sinyal tahminleri: {signal_counts.to_dict()}")
                    
                    # Model kaydetme testi
                    print("\\n5. Model kaydediliyor...")
                    metadata = {
                        'performance': performance,
                        'feature_names': feature_names,
                        'test_date': datetime.now().isoformat()
                    }
                    
                    if save_model(model, 'test_model', 'TEST', metadata):
                        print("✅ Model kaydedildi")
                        
                        # Model yükleme testi
                        print("\\n6. Model yükleniyor...")
                        loaded_result = load_model('test_model', 'TEST')
                        
                        if loaded_result:
                            loaded_model, loaded_metadata = loaded_result
                            print("✅ Model yüklendi")
                            print(f"📊 Yüklenen model tipi: {loaded_metadata.get('model_type')}")
                        else:
                            print("❌ Model yüklenemedi")
                    else:
                        print("❌ Model kaydedilemedi")
                else:
                    print("❌ Sinyal tahminleri başarısız")
            else:
                print("❌ Model değerlendirme başarısız")
        else:
            print("❌ Model eğitimi başarısız")
    else:
        print("❌ Veri hazırlama başarısız")
        
    print("\\nML Model test tamamlandı!")
