"""
AI-FTB (AI-Powered Financial Trading Bot) Configuration Module

Bu modül, botun tüm yapılandırma parametrelerini merkezi olarak tutar.
Tüm ayarları buradan değiştirerek bot davranışını kontrol edebilirsiniz.
"""

# API Anahtarları - Gerektiğinde doldurulacak
API_KEYS = {
    'NEWS_API_KEY': 'YOUR_NEWS_API_KEY_HERE',  # NewsAPI için anahtar
    'ALPHA_VANTAGE_KEY': 'YOUR_ALPHA_VANTAGE_KEY_HERE'  # İsteğe bağlı
}

# İşlem Yapılacak Finansal Enstrümanlar
SYMBOLS = [
    'AAPL',  # Apple Inc.
    'MSFT',  # Microsoft Corporation
    'GOOGL', # Alphabet Inc.
    'TSLA',  # Tesla Inc.
    'AMZN'   # Amazon.com Inc.
]

# Türk Hisseleri için alternatif semboller (isteğe bağlı)
TURKISH_SYMBOLS = [
    'THYAO.IS',  # Türk Hava Yolları
    'BIMAS.IS',  # BİM Mağazalar
    'AKBNK.IS',  # Akbank
    'GARAN.IS',  # Garanti BBVA
    'SAHOL.IS'   # Sabancı Holding
]

# Tarihsel Veri Ayarları
HISTORICAL_DATA_START_DATE = '2020-01-01'  # Geçmiş veri başlangıç tarihi
HISTORICAL_DATA_END_DATE = '2024-12-31'    # Geçmiş veri bitiş tarihi
PRICE_TIMEFRAME = '1d'  # Fiyat verisi zaman dilimi (1d=günlük, 1h=saatlik)

# Makine Öğrenimi Özellikleri
ML_FEATURES = [
    'RSI',           # Relative Strength Index
    'MACD_Hist',     # MACD Histogram
    'SMA_20',        # 20 günlük basit hareketli ortalama
    'SMA_50',        # 50 günlük basit hareketli ortalama
    'Volume_Change', # Hacim değişimi
    'BB_Upper',      # Bollinger Bands üst band
    'BB_Lower',      # Bollinger Bands alt band
    'Volatility'     # Volatilite göstergesi
]

# Makine Öğrenimi Model Ayarları
ML_MODEL_TYPE = 'RandomForestClassifier'  # 'LogisticRegression', 'RandomForestClassifier'
ML_MODEL_PARAMS = {
    'n_estimators': 100,     # Ağaç sayısı (RandomForest için)
    'max_depth': 10,         # Maksimum derinlik
    'random_state': 42,      # Rastgelelik kontrolü
    'min_samples_split': 5   # Bölünme için minimum örnek sayısı
}

# Alternatif model parametreleri (LogisticRegression için)
# ML_MODEL_PARAMS = {
#     'C': 1.0,                # Regularization strength
#     'random_state': 42,
#     'max_iter': 1000
# }

# Duygu Analizi Eşik Değerleri (TextBlob polarity: -1.0 ile 1.0 arası)
SENTIMENT_THRESHOLD_POSITIVE = 0.2   # Bu değerin üstü pozitif duygu
SENTIMENT_THRESHOLD_NEGATIVE = -0.2  # Bu değerin altı negatif duygu

# Risk Yönetimi Ayarları
RISK_PER_TRADE_PERCENT = 0.01  # Her işlemde portföyün %1'i riske edilir
STOP_LOSS_PERCENT = 0.02       # %2 zarar durumunda pozisyon kapatılır
TAKE_PROFIT_PERCENT = 0.04     # %4 kar durumunda pozisyon kapatılır

# Gelişmiş Risk Yönetimi
RISK_MANAGEMENT = {
    'MAX_POSITIONS': 5,              # Maksimum eş zamanlı pozisyon sayısı
    'MAX_PORTFOLIO_RISK': 0.05,      # Toplam portföy riski (%5)
    'TRAILING_STOP_PERCENT': 0.015,  # Trailing stop (%1.5)
    'MAX_DAILY_LOSS': 0.03,          # Günlük maksimum kayıp (%3)
    'POSITION_SIZE_METHOD': 'KELLY', # 'FIXED', 'PERCENT', 'KELLY'
    'CORRELATION_LIMIT': 0.7         # Pozisyonlar arası maksimum korelasyon
}

# Loglama Ayarları
LOG_FILE_PATH = './logs/bot_activity.log'
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Veri Kaydetme Ayarları
DATA_SAVE_PATH = './data/'
MODEL_SAVE_PATH = './models/'

# Teknik Gösterge Parametreleri
TECHNICAL_INDICATORS = {
    'RSI_PERIOD': 14,        # RSI hesaplama periyodu
    'MACD_FAST': 12,         # MACD hızlı EMA periyodu
    'MACD_SLOW': 26,         # MACD yavaş EMA periyodu
    'MACD_SIGNAL': 9,        # MACD sinyal çizgisi periyodu
    'SMA_SHORT_PERIOD': 20,  # Kısa vadeli SMA periyodu
    'SMA_LONG_PERIOD': 50,   # Uzun vadeli SMA periyodu
    'BB_PERIOD': 20,         # Bollinger Bands periyodu
    'BB_STD': 2,             # Bollinger Bands standart sapma çarpanı
    'VOLATILITY_PERIOD': 14  # Volatilite hesaplama periyodu
}

# Backtest Ayarları
BACKTEST_INITIAL_CAPITAL = 100000  # Başlangıç sermayesi ($100,000)
BACKTEST_COMMISSION = 0.001        # İşlem komisyonu (%0.1)

# Haber Çekme Ayarları
NEWS_SEARCH_KEYWORDS = {
    'AAPL': ['Apple', 'iPhone', 'Mac', 'Tim Cook'],
    'MSFT': ['Microsoft', 'Windows', 'Azure', 'Satya Nadella'],
    'GOOGL': ['Google', 'Alphabet', 'Android', 'Sundar Pichai'],
    'TSLA': ['Tesla', 'Elon Musk', 'electric vehicle', 'SpaceX'],
    'AMZN': ['Amazon', 'AWS', 'Jeff Bezos', 'e-commerce']
}

# Feature Engineering Ayarları
FEATURE_SCALING_METHOD = 'StandardScaler'  # 'MinMaxScaler', 'StandardScaler'
TARGET_LOOKAHEAD_DAYS = 1  # Kaç gün sonrasının fiyat yönü tahmin edilecek

if __name__ == "__main__":
    """
    Config modülü test kodu
    """
    print("=== AI-FTB Konfigürasyon Test ===")
    print(f"İşlem sembolleri: {SYMBOLS}")
    print(f"ML model tipi: {ML_MODEL_TYPE}")
    print(f"ML özellikleri: {ML_FEATURES}")
    print(f"Risk yüzdesi: {RISK_PER_TRADE_PERCENT * 100}%")
    print(f"Stop loss: {STOP_LOSS_PERCENT * 100}%")
    print(f"Take profit: {TAKE_PROFIT_PERCENT * 100}%")
    print(f"Pozitif duygu eşiği: {SENTIMENT_THRESHOLD_POSITIVE}")
    print(f"Negatif duygu eşiği: {SENTIMENT_THRESHOLD_NEGATIVE}")
    print("Konfigürasyon başarıyla yüklendi!")
