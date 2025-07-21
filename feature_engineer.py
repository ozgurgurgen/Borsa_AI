"""
AI-FTB (AI-Powered Financial Trading Bot) Feature Engineer Module

Bu modül, makine öğrenimi modeli için ham finansal verilerden anlamlı özellikler 
(teknik göstergeler) türetir ve bunları ölçeklendirir. Çeşitli teknik analiz 
göstergelerini hesaplar ve ML için hazırlar.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import os
import joblib
import config
import logger


def add_technical_indicators(dataframe):
    """
    DataFrame'e teknik analiz göstergelerini ekler. Basit Hareketli Ortalamalar (SMA), 
    Göreceli Güç Endeksi (RSI), MACD, Bollinger Bantları ve Volatilite hesaplar.
    
    Args:
        dataframe (pandas.DataFrame): OHLCV verisi içeren DataFrame
    
    Returns:
        pandas.DataFrame: Teknik göstergeler eklenmiş DataFrame
        None: Hata durumunda
        
    Raises:
        Exception: Hesaplama hatalarında
    """
    try:
        logger.log_info("Teknik göstergeler hesaplanıyor...")
        data = dataframe.copy()
        
        # Parametreleri config'ten al
        rsi_period = config.TECHNICAL_INDICATORS['RSI_PERIOD']
        macd_fast = config.TECHNICAL_INDICATORS['MACD_FAST']
        macd_slow = config.TECHNICAL_INDICATORS['MACD_SLOW']
        macd_signal = config.TECHNICAL_INDICATORS['MACD_SIGNAL']
        sma_short = config.TECHNICAL_INDICATORS['SMA_SHORT_PERIOD']
        sma_long = config.TECHNICAL_INDICATORS['SMA_LONG_PERIOD']
        bb_period = config.TECHNICAL_INDICATORS['BB_PERIOD']
        bb_std = config.TECHNICAL_INDICATORS['BB_STD']
        vol_period = config.TECHNICAL_INDICATORS['VOLATILITY_PERIOD']
        
        # 1. Basit Hareketli Ortalamalar (Simple Moving Averages)
        data[f'SMA_{sma_short}'] = data['Close'].rolling(window=sma_short).mean()
        data[f'SMA_{sma_long}'] = data['Close'].rolling(window=sma_long).mean()
        logger.log_debug(f"SMA {sma_short} ve {sma_long} hesaplandı")
        
        # 2. Göreceli Güç Endeksi (Relative Strength Index - RSI)
        data['RSI'] = calculate_rsi(data['Close'], rsi_period)
        logger.log_debug(f"RSI {rsi_period} periyot hesaplandı")
        
        # 3. MACD (Moving Average Convergence Divergence)
        macd_line, macd_signal_line, macd_histogram = calculate_macd(
            data['Close'], macd_fast, macd_slow, macd_signal
        )
        data['MACD'] = macd_line
        data['MACD_Signal'] = macd_signal_line
        data['MACD_Hist'] = macd_histogram
        logger.log_debug(f"MACD ({macd_fast}, {macd_slow}, {macd_signal}) hesaplandı")
        
        # 4. Bollinger Bantları (Bollinger Bands)
        bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(
            data['Close'], bb_period, bb_std
        )
        data['BB_Upper'] = bb_upper
        data['BB_Middle'] = bb_middle
        data['BB_Lower'] = bb_lower
        data['BB_Width'] = (bb_upper - bb_lower) / bb_middle  # Band genişliği
        data['BB_Position'] = (data['Close'] - bb_lower) / (bb_upper - bb_lower)  # Fiyatın bantlardaki pozisyonu
        logger.log_debug(f"Bollinger Bands ({bb_period}, {bb_std}) hesaplandı")
        
        # 5. Volatilite (Standart Sapma)
        data['Volatility'] = data['Close'].rolling(window=vol_period).std()
        logger.log_debug(f"Volatilite {vol_period} periyot hesaplandı")
        
        # 6. Hacim Değişimi (Volume Change)
        data['Volume_Change'] = data['Volume'].pct_change()
        data['Volume_SMA'] = data['Volume'].rolling(window=20).mean()
        data['Volume_Ratio'] = data['Volume'] / data['Volume_SMA']  # Ortalama hacme göre oran
        logger.log_debug("Hacim göstergeleri hesaplandı")
        
        # 7. Fiyat Değişim Oranları (Price Change Rates)
        data['Price_Change'] = data['Close'].pct_change()
        data['Price_Change_5d'] = data['Close'].pct_change(5)  # 5 günlük değişim
        data['High_Low_Ratio'] = (data['High'] - data['Low']) / data['Close']  # Günlük volatilite
        
        # 8. Momentum Göstergeleri
        data['Momentum_10'] = data['Close'] / data['Close'].shift(10) - 1  # 10 günlük momentum
        data['ROC_5'] = ((data['Close'] - data['Close'].shift(5)) / data['Close'].shift(5)) * 100  # Rate of Change
        
        # 9. Support/Resistance seviyeleri (basitleştirilmiş)
        data['Recent_High'] = data['High'].rolling(window=20).max()
        data['Recent_Low'] = data['Low'].rolling(window=20).min()
        data['Position_in_Range'] = (data['Close'] - data['Recent_Low']) / (data['Recent_High'] - data['Recent_Low'])
        
        # Sonsuz değerleri ve NaN'ları temizle
        data = data.replace([np.inf, -np.inf], np.nan)
        
        # İlk birkaç satır göstergeler hesaplanamadığı için NaN olacak
        initial_nan_count = data.isnull().sum().sum()
        logger.log_info(f"Teknik göstergeler eklendi. İlk {max(sma_long, rsi_period, bb_period)} satır NaN içerebilir.")
        
        return data
        
    except Exception as e:
        logger.log_error(f"Teknik göstergeler hesaplanırken hata: {e}", exc_info=True)
        return None


def calculate_rsi(prices, period=14):
    """
    Göreceli Güç Endeksi (RSI) hesaplar.
    RSI = 100 - (100 / (1 + RS))
    RS = Ortalama Kazanç / Ortalama Kayıp
    
    Args:
        prices (pandas.Series): Kapanış fiyatları
        period (int): Hesaplama periyodu
    
    Returns:
        pandas.Series: RSI değerleri (0-100 arası)
    """
    try:
        # Fiyat değişimlerini hesapla
        delta = prices.diff()
        
        # Kazanç ve kayıpları ayır
        gains = delta.where(delta > 0, 0)  # Pozitif değişimler
        losses = -delta.where(delta < 0, 0)  # Negatif değişimler (pozitif yapılır)
        
        # Ortalama kazanç ve kayıpları hesapla (Wilder's smoothing)
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()
        
        # RS (Relative Strength) hesapla
        rs = avg_gains / avg_losses
        
        # RSI hesapla
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
        
    except Exception as e:
        logger.log_error(f"RSI hesaplanırken hata: {e}")
        return pd.Series(index=prices.index, dtype=float)


def calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9):
    """
    MACD (Moving Average Convergence Divergence) hesaplar.
    MACD = EMA(fast) - EMA(slow)
    Signal = EMA(MACD, signal_period)
    Histogram = MACD - Signal
    
    Args:
        prices (pandas.Series): Kapanış fiyatları
        fast_period (int): Hızlı EMA periyodu
        slow_period (int): Yavaş EMA periyodu
        signal_period (int): Sinyal çizgisi EMA periyodu
    
    Returns:
        tuple: (macd_line, signal_line, histogram)
    """
    try:
        # Üstel Hareketli Ortalamaları hesapla
        ema_fast = prices.ewm(span=fast_period).mean()
        ema_slow = prices.ewm(span=slow_period).mean()
        
        # MACD çizgisini hesapla
        macd_line = ema_fast - ema_slow
        
        # Sinyal çizgisini hesapla
        signal_line = macd_line.ewm(span=signal_period).mean()
        
        # Histogramı hesapla
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
        
    except Exception as e:
        logger.log_error(f"MACD hesaplanırken hata: {e}")
        return pd.Series(index=prices.index, dtype=float), pd.Series(index=prices.index, dtype=float), pd.Series(index=prices.index, dtype=float)


def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """
    Bollinger Bantları hesaplar.
    Middle Band = SMA(period)
    Upper Band = Middle Band + (std_dev * standard_deviation)
    Lower Band = Middle Band - (std_dev * standard_deviation)
    
    Args:
        prices (pandas.Series): Kapanış fiyatları
        period (int): Hareketli ortalama periyodu
        std_dev (float): Standart sapma çarpanı
    
    Returns:
        tuple: (upper_band, middle_band, lower_band)
    """
    try:
        # Orta band (SMA)
        middle_band = prices.rolling(window=period).mean()
        
        # Standart sapma
        std = prices.rolling(window=period).std()
        
        # Üst ve alt bantlar
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        return upper_band, middle_band, lower_band
        
    except Exception as e:
        logger.log_error(f"Bollinger Bands hesaplanırken hata: {e}")
        return pd.Series(index=prices.index, dtype=float), pd.Series(index=prices.index, dtype=float), pd.Series(index=prices.index, dtype=float)


def normalize_features(dataframe, features_to_normalize=None, scaler_type=None, save_scaler=True, symbol=None):
    """
    Makine öğrenimi modeli için belirtilen özellikleri ölçeklendirir.
    StandardScaler veya MinMaxScaler kullanır.
    
    Args:
        dataframe (pandas.DataFrame): Ölçeklendirilecek veriler
        features_to_normalize (list): Ölçeklendirilecek özellik isimleri
        scaler_type (str): 'StandardScaler' veya 'MinMaxScaler'
        save_scaler (bool): Scaler'ı dosyaya kaydet
        symbol (str): Sembol adı (scaler dosya adı için)
    
    Returns:
        tuple: (normalized_dataframe, scaler_object)
        None: Hata durumunda
        
    Raises:
        Exception: Ölçeklendirme hatalarında
    """
    try:
        # Parametreleri config'ten al
        if features_to_normalize is None:
            features_to_normalize = config.ML_FEATURES
        if scaler_type is None:
            scaler_type = config.FEATURE_SCALING_METHOD
            
        data = dataframe.copy()
        
        # Ölçeklendirilecek özelliklerin mevcut olduğunu kontrol et
        available_features = [f for f in features_to_normalize if f in data.columns]
        missing_features = [f for f in features_to_normalize if f not in data.columns]
        
        if missing_features:
            logger.log_warning(f"Eksik özellikler: {missing_features}")
            
        if not available_features:
            logger.log_error("Ölçeklendirilecek özellik bulunamadı")
            return None, None
            
        logger.log_info(f"{scaler_type} ile {len(available_features)} özellik ölçeklendiriliyor...")
        
        # Scaler seç
        if scaler_type == 'StandardScaler':
            scaler = StandardScaler()
        elif scaler_type == 'MinMaxScaler':
            scaler = MinMaxScaler()
        else:
            logger.log_error(f"Geçersiz scaler tipi: {scaler_type}")
            return None, None
            
        # NaN değerleri geçici olarak 0 ile değiştir (scaler NaN'ı sevmez)
        data_for_scaling = data[available_features].fillna(0)
        
        # Ölçeklendirme uygula
        scaled_features = scaler.fit_transform(data_for_scaling)
        
        # Ölçeklendirilmiş verileri DataFrame'e geri koy
        for i, feature in enumerate(available_features):
            data[f'{feature}_scaled'] = scaled_features[:, i]
            
        # Scaler'ı kaydet
        if save_scaler and symbol:
            scaler_filename = f"{symbol}_{scaler_type.lower()}.joblib"
            scaler_path = os.path.join(config.MODEL_SAVE_PATH, scaler_filename)
            os.makedirs(os.path.dirname(scaler_path), exist_ok=True)
            joblib.dump(scaler, scaler_path)
            logger.log_info(f"Scaler kaydedildi: {scaler_path}")
            
        logger.log_info(f"Özellik ölçeklendirme tamamlandı: {len(available_features)} özellik")
        
        return data, scaler
        
    except Exception as e:
        logger.log_error(f"Özellik ölçeklendirme hatası: {e}", exc_info=True)
        return None, None


def load_scaler(symbol, scaler_type=None):
    """
    Kaydedilmiş scaler'ı yükler.
    
    Args:
        symbol (str): Sembol adı
        scaler_type (str): Scaler tipi
    
    Returns:
        sklearn scaler object: Yüklenen scaler
        None: Hata durumunda
    """
    try:
        if scaler_type is None:
            scaler_type = config.FEATURE_SCALING_METHOD
            
        scaler_filename = f"{symbol}_{scaler_type.lower()}.joblib"
        scaler_path = os.path.join(config.MODEL_SAVE_PATH, scaler_filename)
        
        if not os.path.exists(scaler_path):
            logger.log_warning(f"Scaler dosyası bulunamadı: {scaler_path}")
            return None
            
        scaler = joblib.load(scaler_path)
        logger.log_info(f"Scaler yüklendi: {scaler_path}")
        return scaler
        
    except Exception as e:
        logger.log_error(f"Scaler yüklenirken hata: {e}")
        return None


def create_target_variable(dataframe, lookahead_days=None):
    """
    Makine öğrenimi için hedef değişken oluşturur.
    Gelecekteki fiyat yönünü tahmin etmek için binary sınıflandırma hedefi.
    
    Args:
        dataframe (pandas.DataFrame): Fiyat verisi
        lookahead_days (int): Kaç gün sonrasına bakılacak
    
    Returns:
        pandas.DataFrame: Hedef değişken eklenmiş DataFrame
    """
    try:
        if lookahead_days is None:
            lookahead_days = config.TARGET_LOOKAHEAD_DAYS
            
        data = dataframe.copy()
        
        # Gelecekteki kapanış fiyatını al
        future_close = data['Close'].shift(-lookahead_days)
        
        # Hedef değişken: 1 = fiyat artacak, 0 = fiyat düşecek/sabit kalacak
        data['Target'] = (future_close > data['Close']).astype(int)
        
        # Son lookahead_days satırda hedef bilinmeyeceği için NaN olur
        valid_targets = data['Target'].notna().sum()
        logger.log_info(f"Hedef değişken oluşturuldu: {valid_targets} geçerli hedef")
        
        return data
        
    except Exception as e:
        logger.log_error(f"Hedef değişken oluşturulurken hata: {e}")
        return dataframe


def get_feature_importance_ranking(dataframe, target_column='Target'):
    """
    Özelliklerin hedef değişkenle korelasyonlarını hesaplar ve önem sırasını verir.
    
    Args:
        dataframe (pandas.DataFrame): Özellikler ve hedef içeren DataFrame
        target_column (str): Hedef değişken sütun adı
    
    Returns:
        pandas.DataFrame: Özellik önem sıralaması
    """
    try:
        if target_column not in dataframe.columns:
            logger.log_warning(f"Hedef sütun bulunamadı: {target_column}")
            return None
            
        # Sadece sayısal sütunları al
        numeric_cols = dataframe.select_dtypes(include=[np.number]).columns
        feature_cols = [col for col in numeric_cols if col != target_column and not col.endswith('_scaled')]
        
        if not feature_cols:
            logger.log_warning("Analiz edilecek özellik bulunamadı")
            return None
            
        # Korelasyonları hesapla
        correlations = []
        for feature in feature_cols:
            try:
                corr = dataframe[feature].corr(dataframe[target_column])
                if not np.isnan(corr):
                    correlations.append({
                        'feature': feature,
                        'correlation': abs(corr),  # Mutlak değer
                        'correlation_raw': corr
                    })
            except:
                continue
                
        # Sonuçları DataFrame'e çevir ve sırala
        importance_df = pd.DataFrame(correlations)
        importance_df = importance_df.sort_values('correlation', ascending=False)
        
        logger.log_info(f"En önemli 5 özellik: {importance_df.head()['feature'].tolist()}")
        
        return importance_df
        
    except Exception as e:
        logger.log_error(f"Özellik önem analizi hatası: {e}")
        return None


if __name__ == "__main__":
    """
    Feature Engineer modülü test kodu
    """
    print("=== AI-FTB Feature Engineer Test ===")
    
    # Test verisi oluştur (gerçek veriye benzer)
    import datetime
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    np.random.seed(42)
    
    # Basit rastgele fiyat verisi
    initial_price = 100
    returns = np.random.normal(0.001, 0.02, len(dates))  # Günlük getiri
    prices = [initial_price]
    for r in returns[1:]:
        prices.append(prices[-1] * (1 + r))
    
    test_data = pd.DataFrame({
        'Open': prices,
        'High': [p * (1 + np.random.uniform(0, 0.03)) for p in prices],
        'Low': [p * (1 - np.random.uniform(0, 0.03)) for p in prices],
        'Close': prices,
        'Volume': np.random.randint(1000000, 10000000, len(dates))
    }, index=dates)
    
    print(f"Test verisi oluşturuldu: {len(test_data)} satır")
    print(f"Fiyat aralığı: ${test_data['Close'].min():.2f} - ${test_data['Close'].max():.2f}")
    
    # Teknik göstergeler ekleme testi
    print("\n1. Teknik göstergeler ekleniyor...")
    enhanced_data = add_technical_indicators(test_data)
    
    if enhanced_data is not None:
        print(f"✅ Teknik göstergeler eklendi")
        print(f"📊 Toplam sütun sayısı: {len(enhanced_data.columns)}")
        print(f"📈 Yeni özellikler: {[col for col in enhanced_data.columns if col not in test_data.columns][:5]}...")
        
        # Hedef değişken oluşturma testi
        print("\n2. Hedef değişken oluşturuluyor...")
        enhanced_data = create_target_variable(enhanced_data)
        
        if 'Target' in enhanced_data.columns:
            target_dist = enhanced_data['Target'].value_counts()
            print(f"✅ Hedef değişken oluşturuldu")
            print(f"📊 Hedef dağılımı: {target_dist.to_dict()}")
            
            # Özellik ölçeklendirme testi
            print("\n3. Özellik ölçeklendirme...")
            test_features = ['RSI', 'MACD_Hist', 'SMA_20', 'Volume_Change']
            normalized_data, scaler = normalize_features(
                enhanced_data, test_features, save_scaler=False
            )
            
            if normalized_data is not None:
                print(f"✅ Özellik ölçeklendirme tamamlandı")
                scaled_cols = [col for col in normalized_data.columns if col.endswith('_scaled')]
                print(f"📊 Ölçeklendirilmiş özellikler: {scaled_cols}")
                
                # Özellik önem analizi testi
                print("\n4. Özellik önem analizi...")
                importance = get_feature_importance_ranking(normalized_data)
                
                if importance is not None:
                    print(f"✅ Özellik önem analizi tamamlandı")
                    print("📊 En önemli 5 özellik:")
                    for i, row in importance.head().iterrows():
                        print(f"   {row['feature']}: {row['correlation']:.3f}")
                else:
                    print("❌ Özellik önem analizi başarısız")
            else:
                print("❌ Özellik ölçeklendirme başarısız")
        else:
            print("❌ Hedef değişken oluşturulamadı")
    else:
        print("❌ Teknik göstergeler eklenemedi")
        
    print("\nFeature Engineer test tamamlandı!")
