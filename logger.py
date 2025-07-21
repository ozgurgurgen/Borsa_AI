"""
AI-FTB (AI-Powered Financial Trading Bot) Logger Module

Bu modül, botun tüm operasyonlarını (bilgi, hata, uyarı) merkezi bir şekilde 
kaydeder. Tüm diğer modüller loglama için bu modülü kullanır.
"""

import logging
import os
from datetime import datetime
import config


def setup_logger(log_file_path=None, log_level=None):
    """
    Loglama sistemini yapılandırır ve logger objesini döndürür.
    
    Args:
        log_file_path (str): Log dosyasının tam yolu. None ise config'ten alınır.
        log_level (str): Log seviyesi. None ise config'ten alınır.
    
    Returns:
        logging.Logger: Yapılandırılmış logger objesi
        
    Raises:
        Exception: Log dosyası oluşturulamadığında
    """
    try:
        # Parametreler config'ten alınır
        if log_file_path is None:
            log_file_path = config.LOG_FILE_PATH
        if log_level is None:
            log_level = config.LOG_LEVEL
            
        # Log dosyasının dizinini oluştur
        log_dir = os.path.dirname(log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Logger'ı yapılandır
        logger = logging.getLogger('AI_FTB')
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # Eğer handler'lar zaten varsa, temizle (çift kayıt önleme)
        if logger.handlers:
            logger.handlers.clear()
            
        # Dosya handler'ı oluştur
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setLevel(getattr(logging, log_level.upper()))
        
        # Konsol handler'ı oluştur
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))
        
        # Log formatını ayarla
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Handler'ları logger'a ekle
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
        
    except Exception as e:
        print(f"Logger kurulumu sırasında hata: {e}")
        raise


# Global logger instance - diğer modüller tarafından kullanılacak
logger = setup_logger()


def log_info(message):
    """
    Bilgi mesajlarını kaydeder.
    
    Args:
        message (str): Kaydedilecek bilgi mesajı
    """
    try:
        logger.info(message)
    except Exception as e:
        print(f"Info log yazılırken hata: {e}")


def log_warning(message):
    """
    Uyarı mesajlarını kaydeder.
    
    Args:
        message (str): Kaydedilecek uyarı mesajı
    """
    try:
        logger.warning(message)
    except Exception as e:
        print(f"Warning log yazılırken hata: {e}")


def log_error(message, exc_info=False):
    """
    Hata mesajlarını kaydeder.
    
    Args:
        message (str): Kaydedilecek hata mesajı
        exc_info (bool): True ise istisna bilgilerini de loglar
    """
    try:
        logger.error(message, exc_info=exc_info)
    except Exception as e:
        print(f"Error log yazılırken hata: {e}")


def log_debug(message):
    """
    Debug mesajlarını kaydeder.
    
    Args:
        message (str): Kaydedilecek debug mesajı
    """
    try:
        logger.debug(message)
    except Exception as e:
        print(f"Debug log yazılırken hata: {e}")


def log_critical(message):
    """
    Kritik hata mesajlarını kaydeder.
    
    Args:
        message (str): Kaydedilecek kritik hata mesajı
    """
    try:
        logger.critical(message)
    except Exception as e:
        print(f"Critical log yazılırken hata: {e}")


def log_trade_decision(symbol, decision, price, reason):
    """
    Ticaret kararlarını özel formatla loglar.
    
    Args:
        symbol (str): İşlem yapılan sembol
        decision (str): Alınan karar (BUY, SELL, HOLD)
        price (float): İşlem fiyatı
        reason (str): Karar gerekçesi
    """
    trade_message = f"TRADE - {symbol}: {decision} at ${price:.2f} - Reason: {reason}"
    log_info(trade_message)


def log_performance_metric(metric_name, value):
    """
    Performans metriklerini loglar.
    
    Args:
        metric_name (str): Metrik adı
        value (float): Metrik değeri
    """
    performance_message = f"PERFORMANCE - {metric_name}: {value}"
    log_info(performance_message)


if __name__ == "__main__":
    """
    Logger modülü test kodu
    """
    print("=== AI-FTB Logger Test ===")
    
    # Test mesajları
    log_info("Logger modülü test ediliyor...")
    log_debug("Bu bir debug mesajıdır")
    log_warning("Bu bir uyarı mesajıdır")
    log_error("Bu bir hata mesajıdır (test)")
    
    # Trade decision test
    log_trade_decision("AAPL", "BUY", 150.25, "ML signal: 1, Sentiment: 0.3")
    
    # Performance metric test
    log_performance_metric("Total Return", 15.5)
    log_performance_metric("Max Drawdown", -5.2)
    
    log_info("Logger test tamamlandı!")
    
    # Log dosyasının oluşturulduğunu kontrol et
    if os.path.exists(config.LOG_FILE_PATH):
        print(f"Log dosyası başarıyla oluşturuldu: {config.LOG_FILE_PATH}")
    else:
        print("Log dosyası oluşturulamadı!")
