"""
AI-FTB (AI-Powered Financial Trading Bot) Data Handler Module

Bu modül, finansal piyasalardan geçmiş fiyat ve hacim verilerini güvenilir bir şekilde 
çeker ve temel ön işlemeden geçirir. yfinance kütüphanesini kullanarak 
tarihsel OHLCV verilerini alır.
"""

import pandas as pd
import yfinance as yf
import os
from datetime import datetime, timedelta
import config
import logger


def fetch_historical_data(symbol, start_date=None, end_date=None, timeframe=None):
    """
    Belirli bir sembol için tarihsel OHLCV (Açılış, En Yüksek, En Düşük, Kapanış, Hacim) 
    verilerini yfinance kullanarak çeker.
    
    Args:
        symbol (str): İşlem sembolü (örn. 'AAPL', 'MSFT')
        start_date (str): Başlangıç tarihi ('YYYY-MM-DD' formatında)
        end_date (str): Bitiş tarihi ('YYYY-MM-DD' formatında)
        timeframe (str): Veri zaman dilimi ('1d', '1h', '1m' vb.)
    
    Returns:
        pandas.DataFrame: Temizlenmiş, datetime indeksli OHLCV verisi
        None: Hata durumunda
        
    Raises:
        Exception: API çağrısı veya veri işleme hatalarında
    """
    try:
        # Parametreleri config'ten al eğer verilmemişse
        if start_date is None:
            start_date = config.HISTORICAL_DATA_START_DATE
        if end_date is None:
            end_date = config.HISTORICAL_DATA_END_DATE
        if timeframe is None:
            timeframe = config.PRICE_TIMEFRAME
            
        logger.log_info(f"Veri çekiliyor: {symbol} ({start_date} - {end_date}, {timeframe})")
        
        # yfinance ile veri çek
        ticker = yf.Ticker(symbol)
        data = ticker.history(
            start=start_date,
            end=end_date,
            interval=timeframe,
            auto_adjust=True,  # Bölünme ve temettü ayarlamaları otomatik yapılır
            prepost=True       # Piyasa öncesi ve sonrası veriler dahil edilir
        )
        
        # Veri kontrolü
        if data.empty:
            logger.log_warning(f"Sembol {symbol} için veri bulunamadı")
            return None
            
        # Sütun adlarını standartlaştır (yfinance bazen farklı isimler kullanır)
        data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        # Index'in datetime formatında olduğundan emin ol
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index)
            
        # Eksik verileri önceki geçerli değerle doldur (forward fill)
        data_before_fill = data.isnull().sum().sum()
        data = data.ffill()
        data_after_fill = data.isnull().sum().sum()
        
        if data_before_fill > 0:
            logger.log_info(f"{symbol}: {data_before_fill} eksik veri forward fill ile dolduruldu")
            
        # Hala eksik veriler varsa (ilk satırlar), backward fill kullan
        if data_after_fill > 0:
            data = data.bfill()
            final_missing = data.isnull().sum().sum()
            if final_missing > 0:
                logger.log_warning(f"{symbol}: {final_missing} veri hala eksik")
                
        # Verinin geçerliliğini kontrol et
        if len(data) < 50:  # En az 50 günlük veri gerekli
            logger.log_warning(f"{symbol}: Yetersiz veri ({len(data)} gün)")
            return None
            
        # Negatif fiyatları kontrol et
        if (data[['Open', 'High', 'Low', 'Close']] <= 0).any().any():
            logger.log_warning(f"{symbol}: Negatif veya sıfır fiyat değerleri tespit edildi")
            # Negatif değerleri bir önceki geçerli değerle değiştir
            data[data <= 0] = None
            data = data.ffill()
            
        logger.log_info(f"{symbol}: {len(data)} günlük veri başarıyla çekildi")
        return data
        
    except Exception as e:
        logger.log_error(f"Veri çekerken hata ({symbol}): {e}", exc_info=True)
        return None


def save_data(dataframe, filename, symbol=None):
    """
    DataFrame'i belirtilen dosyaya CSV formatında kaydeder.
    
    Args:
        dataframe (pandas.DataFrame): Kaydedilecek veri
        filename (str): Dosya adı (uzantı olmadan)
        symbol (str): Sembol adı (dosya adına eklenir)
    
    Returns:
        bool: Başarı durumu
        
    Raises:
        Exception: Dosya yazma hatalarında
    """
    try:
        # Dosya yolunu oluştur
        if symbol:
            filename = f"{symbol}_{filename}"
        file_path = os.path.join(config.DATA_SAVE_PATH, f"{filename}.csv")
        
        # Dizini oluştur
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Veriyi kaydet
        dataframe.to_csv(file_path, index=True)
        logger.log_info(f"Veri kaydedildi: {file_path}")
        return True
        
    except Exception as e:
        logger.log_error(f"Veri kaydederken hata: {e}", exc_info=True)
        return False


def load_data(filename, symbol=None):
    """
    Belirtilen dosyadan veriyi CSV formatında yükler.
    
    Args:
        filename (str): Dosya adı (uzantı olmadan)
        symbol (str): Sembol adı (dosya adından çıkarılır)
    
    Returns:
        pandas.DataFrame: Yüklenen veri
        None: Hata durumunda
        
    Raises:
        Exception: Dosya okuma hatalarında
    """
    try:
        # Dosya yolunu oluştur
        if symbol:
            filename = f"{symbol}_{filename}"
        file_path = os.path.join(config.DATA_SAVE_PATH, f"{filename}.csv")
        
        if not os.path.exists(file_path):
            logger.log_warning(f"Dosya bulunamadı: {file_path}")
            return None
            
        # Veriyi yükle
        data = pd.read_csv(file_path, index_col=0, parse_dates=True)
        logger.log_info(f"Veri yüklendi: {file_path} ({len(data)} satır)")
        return data
        
    except Exception as e:
        logger.log_error(f"Veri yüklerken hata: {e}", exc_info=True)
        return None


def get_latest_price(symbol):
    """
    Belirli bir sembol için en güncel fiyat bilgisini alır.
    
    Args:
        symbol (str): İşlem sembolü
    
    Returns:
        dict: {'price': float, 'change': float, 'change_percent': float}
        None: Hata durumunda
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # Son 5 günlük veriyi al (güncel fiyat için)
        data = ticker.history(period="5d")
        if data.empty:
            return None
            
        current_price = data['Close'].iloc[-1]
        previous_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
        
        change = current_price - previous_price
        change_percent = (change / previous_price) * 100 if previous_price != 0 else 0
        
        return {
            'price': float(current_price),
            'change': float(change),
            'change_percent': float(change_percent)
        }
        
    except Exception as e:
        logger.log_error(f"Güncel fiyat alırken hata ({symbol}): {e}")
        return None


def validate_data_quality(dataframe, symbol):
    """
    Veri kalitesini kontrol eder ve raporlar.
    
    Args:
        dataframe (pandas.DataFrame): Kontrol edilecek veri
        symbol (str): Sembol adı
    
    Returns:
        dict: Kalite raporu
    """
    try:
        report = {
            'symbol': symbol,
            'total_rows': len(dataframe),
            'date_range': {
                'start': dataframe.index.min().strftime('%Y-%m-%d'),
                'end': dataframe.index.max().strftime('%Y-%m-%d')
            },
            'missing_values': dataframe.isnull().sum().to_dict(),
            'negative_values': (dataframe < 0).sum().to_dict(),
            'duplicate_dates': dataframe.index.duplicated().sum(),
            'volume_zeros': (dataframe['Volume'] == 0).sum() if 'Volume' in dataframe.columns else 0
        }
        
        # Kalite skorunu hesapla
        quality_issues = (
            sum(report['missing_values'].values()) +
            sum(report['negative_values'].values()) +
            report['duplicate_dates'] +
            report['volume_zeros']
        )
        
        report['quality_score'] = max(0, 100 - (quality_issues / len(dataframe) * 100))
        
        logger.log_info(f"Veri kalitesi ({symbol}): {report['quality_score']:.1f}/100")
        
        return report
        
    except Exception as e:
        logger.log_error(f"Veri kalitesi kontrolünde hata ({symbol}): {e}")
        return None


if __name__ == "__main__":
    """
    Data Handler modülü test kodu
    """
    print("=== AI-FTB Data Handler Test ===")
    
    # Test sembolü
    test_symbol = 'AAPL'
    
    # Veri çekme testi
    print(f"\n1. {test_symbol} için veri çekiliyor...")
    data = fetch_historical_data(test_symbol, '2023-01-01', '2023-12-31')
    
    if data is not None:
        print(f"✅ Veri başarıyla çekildi: {len(data)} satır")
        print(f"📊 Veri aralığı: {data.index.min()} - {data.index.max()}")
        print(f"📈 Son kapanış fiyatı: ${data['Close'].iloc[-1]:.2f}")
        
        # Veri kalitesi testi
        print("\n2. Veri kalitesi kontrol ediliyor...")
        quality_report = validate_data_quality(data, test_symbol)
        if quality_report:
            print(f"✅ Kalite skoru: {quality_report['quality_score']:.1f}/100")
            
        # Veri kaydetme testi
        print("\n3. Veri kaydediliyor...")
        if save_data(data, 'historical_data', test_symbol):
            print("✅ Veri başarıyla kaydedildi")
            
            # Veri yükleme testi
            print("\n4. Veri yükleniyor...")
            loaded_data = load_data('historical_data', test_symbol)
            if loaded_data is not None:
                print(f"✅ Veri başarıyla yüklendi: {len(loaded_data)} satır")
            else:
                print("❌ Veri yüklenemedi")
        else:
            print("❌ Veri kaydedilemedi")
            
        # Güncel fiyat testi
        print("\n5. Güncel fiyat alınıyor...")
        current_price = get_latest_price(test_symbol)
        if current_price:
            print(f"✅ Güncel fiyat: ${current_price['price']:.2f}")
            print(f"📊 Değişim: {current_price['change']:+.2f} ({current_price['change_percent']:+.2f}%)")
        else:
            print("❌ Güncel fiyat alınamadı")
            
    else:
        print("❌ Veri çekilemedi")
        
    print("\nData Handler test tamamlandı!")
