# AI-FTB Proje Dokümantasyonu

## 📋 İçindekiler

1. [Proje Özeti](#proje-özeti)
2. [Mimari Tasarım](#mimari-tasarım)
3. [Modül Detayları](#modül-detayları)
4. [Algoritma Açıklamaları](#algoritma-açıklamaları)
5. [Performans Metrikleri](#performans-metrikleri)
6. [Geliştirme Rehberi](#geliştirme-rehberi)
7. [Sık Sorulan Sorular](#sık-sorulan-sorular)

## 🎯 Proje Özeti

### Amaç
AI-FTB, geçmiş fiyat hareketlerini ve finansal haber metinlerini analiz ederek yapay zeka destekli alım-satım sinyalleri üreten bir finansal ticaret botudur.

### Temel Prensipler
- **Modülerlik**: Her işlev ayrı modülde
- **Temizlik**: PEP 8 uyumlu, okunabilir kod
- **Güvenilirlik**: Kapsamlı hata yönetimi
- **Şeffaflık**: Detaylı loglama ve raporlama
- **Genişletilebilirlik**: Yeni özellik eklemesi kolay

### Teknoloji Stack
- **Dil**: Python 3.9+
- **ML**: scikit-learn (RandomForest, LogisticRegression)
- **Veri**: pandas, numpy, yfinance
- **NLP**: TextBlob, NLTK
- **Loglama**: Python logging
- **Dosya**: CSV, JSON, joblib

## 🏗️ Mimari Tasarım

### Genel Akış
```
Veri Çekme → Özellik Mühendisliği → ML Eğitimi → Strateji → Backtest → Rapor
```

### Katman Yapısı
```
┌─────────────────────────────────────────────────────────────┐
│                     Ana Program (main.py)                   │
├─────────────────────────────────────────────────────────────┤
│  Strateji Katmanı (strategy_executor.py, backtester.py)    │
├─────────────────────────────────────────────────────────────┤
│  ML Katmanı (ml_model.py, feature_engineer.py)             │
├─────────────────────────────────────────────────────────────┤
│  Veri Katmanı (data_handler.py, news_sentiment_analyzer.py)│
├─────────────────────────────────────────────────────────────┤
│  Altyapı Katmanı (config.py, logger.py)                   │
└─────────────────────────────────────────────────────────────┘
```

### Veri Akışı
```
Yahoo Finance → Raw Data → Technical Indicators → ML Features → Model → Signals → Trading Decisions → Performance Report
      ↓              ↓                ↓              ↓         ↓        ↓               ↓
News Sources → Text Data → Sentiment Analysis → Sentiment Score ─┘    Risk Management ─┘
```

## 📚 Modül Detayları

### 1. config.py - Konfigürasyon Yönetimi

**Amaç**: Tüm bot ayarlarını merkezi yönetim

**Ana Bileşenler**:
- `SYMBOLS`: İşlem sembolleri
- `ML_MODEL_TYPE`: Model seçimi
- `RISK_PER_TRADE_PERCENT`: Risk yönetimi
- `TECHNICAL_INDICATORS`: Gösterge parametreleri

**Kullanım**:
```python
import config
symbols = config.SYMBOLS
risk = config.RISK_PER_TRADE_PERCENT
```

### 2. logger.py - Loglama Sistemi

**Amaç**: Merkezi loglama ve hata takibi

**Ana Fonksiyonlar**:
- `setup_logger()`: Logger kurulumu
- `log_info()`, `log_error()`: Mesaj loglama
- `log_trade_decision()`: Ticaret kararlarını logla

**Özellikler**:
- Dosya ve konsol çıktısı
- Timestamp ve fonksiyon bilgisi
- Farklı log seviyeleri (DEBUG, INFO, WARNING, ERROR)

### 3. data_handler.py - Veri Yönetimi

**Amaç**: Finansal veri çekme ve ön işleme

**Ana Fonksiyonlar**:
- `fetch_historical_data()`: yfinance ile veri çekme
- `save_data()`, `load_data()`: Veri kaydetme/yükleme
- `validate_data_quality()`: Veri kalite kontrolü

**Veri İşleme Adımları**:
1. API'den raw veri çekme
2. Eksik veri doldurma (forward/backward fill)
3. Negatif değer kontrolü
4. Datetime index doğrulama
5. CSV formatında kaydetme

### 4. feature_engineer.py - Özellik Mühendisliği

**Amaç**: Ham veriden ML özellikleri türetme

**Teknik Göstergeler**:
- **RSI (Relative Strength Index)**: 14 periyot
- **MACD**: 12/26/9 parametreleri
- **Bollinger Bands**: 20 periyot, 2 std
- **SMA**: 20 ve 50 periyot
- **Volatilite**: 14 periyot standart sapma

**Özellik Ölçeklendirme**:
- StandardScaler veya MinMaxScaler
- Eğitim verisi üzerinde fit
- Test verisine transform
- Scaler kaydetme/yükleme

### 5. news_sentiment_analyzer.py - Duygu Analizi

**Amaç**: Haber metinlerinden duygu skoru çıkarma

**İş Akışı**:
1. Haber çekme (API veya mock data)
2. Metin temizleme (HTML, URL kaldırma)
3. Ön işleme (küçük harf, noktalama)
4. TextBlob ile duygu analizi
5. Sayısal skor (-1.0 ile 1.0 arası)

**Duygu Skoru Hesaplama**:
```python
polarity = TextBlob(text).sentiment.polarity
# -1.0: Çok negatif
#  0.0: Nötr
# +1.0: Çok pozitif
```

### 6. ml_model.py - Makine Öğrenimi

**Amaç**: ML modeli eğitimi ve tahmin

**Desteklenen Modeller**:
- **RandomForestClassifier**: Ensemble method
- **LogisticRegression**: Linear classifier

**Model Eğitimi**:
1. Veri hazırlama (X, y ayrımı)
2. Train/test split (80/20)
3. Model eğitimi
4. Cross-validation (5-fold)
5. Performance değerlendirme
6. Model kaydetme

**Tahmin Süreci**:
- Binary sınıflandırma (1: Fiyat artacak, 0: Düşecek)
- Olasılık tahmini
- Sinyal dönüşümü (BUY/SELL/HOLD)

### 7. strategy_executor.py - Strateji Yürütme

**Amaç**: ML sinyali + duygu skorunu birleştirme

**Karar Matrisi**:
```
ML=1, Sentiment>0.2  → BUY  (Güven: 0.8+)
ML=-1, Sentiment<-0.2 → SELL (Güven: 0.8+)
ML=1, Sentiment>0    → BUY  (Güven: 0.6+)
ML=-1, Sentiment<0   → SELL (Güven: 0.6+)
Çelişkili sinyaller  → HOLD (Güven: 0.3)
```

**Risk Yönetimi**:
- **Pozisyon Büyüklüğü**: (Portföy × Risk%) / Stop Loss%
- **Stop Loss**: Giriş fiyatının %2 altı
- **Take Profit**: Giriş fiyatının %4 üstü

### 8. backtester.py - Performans Testi

**Amaç**: Tarihsel veriler üzerinde strateji simülasyonu

**Backtest Süreci**:
1. Günlük veri döngüsü
2. Her gün için ML tahmini
3. Duygu skoru alımı
4. Strateji kararı
5. Risk yönetimi kontrolü
6. Sanal işlem gerçekleştirme
7. Portföy değeri güncelleme

**Performans Metrikleri**:
- Toplam getiri (%)
- Maksimum düşüş (%)
- Sharpe ratio
- Kazanma oranı (%)
- Profit factor

## 🧮 Algoritma Açıklamaları

### RSI Hesaplama
```python
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)
    
    avg_gains = gains.rolling(window=period).mean()
    avg_losses = losses.rolling(window=period).mean()
    
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    return rsi
```

### MACD Hesaplama
```python
def calculate_macd(prices, fast=12, slow=26, signal=9):
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram
```

### Duygu Skoru Hesaplama
```python
def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    
    # Objektif metinlerde duygu skorunu azalt
    if subjectivity < 0.1:
        polarity *= 0.5
        
    return polarity
```

### Pozisyon Büyüklüğü Hesaplama
```python
def calculate_position_size(portfolio_value, current_price, risk_percent, stop_loss_percent):
    risk_amount = portfolio_value * risk_percent
    max_investment = risk_amount / stop_loss_percent
    shares = int(max_investment / current_price)
    return shares
```

## 📊 Performans Metrikleri

### Getiri Metrikleri

**Toplam Getiri**:
```
Total Return = (Final Value - Initial Capital) / Initial Capital × 100
```

**Yıllık Getiri**:
```
Annualized Return = (Final Value / Initial Capital)^(365/Days) - 1
```

### Risk Metrikleri

**Maksimum Düşüş**:
```
Max Drawdown = Min((Portfolio Value - Running Max) / Running Max)
```

**Sharpe Ratio**:
```
Sharpe Ratio = (Average Daily Return × 252) / (Daily Return Std × √252)
```

**Volatilite**:
```
Volatility = Daily Return Std × √252 × 100
```

### İşlem Metrikleri

**Kazanma Oranı**:
```
Win Rate = Winning Trades / Total Trades × 100
```

**Profit Factor**:
```
Profit Factor = Gross Profit / Gross Loss
```

### Performans Notu Hesaplama
```python
def calculate_performance_grade(total_return, max_drawdown, win_rate, sharpe_ratio):
    score = 0
    
    # Getiri (40% ağırlık)
    if total_return >= 20: score += 40
    elif total_return >= 15: score += 35
    elif total_return >= 10: score += 30
    
    # Risk (30% ağırlık)  
    if max_drawdown >= -5: score += 30
    elif max_drawdown >= -10: score += 25
    
    # Kazanma oranı (20% ağırlık)
    if win_rate >= 60: score += 20
    elif win_rate >= 55: score += 18
    
    # Sharpe ratio (10% ağırlık)
    if sharpe_ratio >= 2.0: score += 10
    elif sharpe_ratio >= 1.5: score += 8
    
    # Not hesaplama
    if score >= 90: return 'A+'
    elif score >= 85: return 'A'
    # ... devamı
```

## 🛠️ Geliştirme Rehberi

### Yeni Teknik Gösterge Ekleme

1. **Gösterge Fonksiyonu Yazma**:
```python
def calculate_stochastic(high, low, close, period=14):
    lowest_low = low.rolling(window=period).min()
    highest_high = high.rolling(window=period).max()
    
    k_percent = ((close - lowest_low) / (highest_high - lowest_low)) * 100
    d_percent = k_percent.rolling(window=3).mean()
    
    return k_percent, d_percent
```

2. **Ana Fonksiyona Ekleme**:
```python
def add_technical_indicators(dataframe):
    # Mevcut göstergeler...
    
    # Yeni gösterge
    data['Stoch_K'], data['Stoch_D'] = calculate_stochastic(
        data['High'], data['Low'], data['Close']
    )
```

3. **Config'e Ekleme**:
```python
ML_FEATURES = [..., 'Stoch_K', 'Stoch_D']
```

### Yeni ML Modeli Ekleme

1. **Model Import**:
```python
from sklearn.svm import SVC
```

2. **Model Seçimi**:
```python
elif model_type == 'SVC':
    model = SVC(**params)
```

3. **Config Parametreleri**:
```python
ML_MODEL_TYPE = 'SVC'
ML_MODEL_PARAMS = {'C': 1.0, 'kernel': 'rbf'}
```

### Yeni Duygu Analizi Kaynağı

1. **API Entegrasyonu**:
```python
def fetch_twitter_sentiment(query, date):
    # Twitter API çağrısı
    tweets = twitter_api.search(query, date)
    sentiments = [analyze_sentiment(tweet) for tweet in tweets]
    return np.mean(sentiments)
```

2. **Ana Fonksiyona Ekleme**:
```python
def get_news_sentiment_for_date(symbol, date):
    news_sentiment = fetch_financial_news(symbol, date)
    twitter_sentiment = fetch_twitter_sentiment(symbol, date)
    
    # Ağırlıklı ortalama
    combined_sentiment = (news_sentiment * 0.7 + twitter_sentiment * 0.3)
    return combined_sentiment
```

### Yeni Strateji Kuralı

1. **Karar Mantığı Genişletme**:
```python
def generate_trade_decision(ml_signal, news_sentiment, volume_spike=False):
    # Mevcut mantık...
    
    # Yeni kural: Yüksek hacim AL sinyalini güçlendirir
    if volume_spike and ml_signal == 1:
        confidence *= 1.2
        reasoning_parts.append("Yüksek hacim AL sinyalini destekliyor")
```

## ❓ Sık Sorulan Sorular

### Genel Sorular

**S: Bot gerçek parayla işlem yapıyor mu?**
C: Hayır, sadece simülasyon ve analiz yapar. Gerçek işlem entegrasyonu mevcut değil.

**S: Hangi piyasalarda çalışır?**
C: yfinance'in desteklediği tüm piyasalarda (ABD, Avrupa, Asya hisse senetleri).

**S: Ne kadar veri gerekli?**
C: Minimum 100 günlük tarihsel veri öneriliyor, ideal olarak 1+ yıl.

### Teknik Sorular

**S: Model ne kadar sıklıkla yeniden eğitilmeli?**
C: Piyasa koşullarına bağlı olarak ayda bir veya çeyrek yılda bir.

**S: Hangi teknik göstergeler en etkili?**
C: Feature importance analizi ile belirlenir, genellikle RSI ve MACD öne çıkar.

**S: Duygu analizi ne kadar doğru?**
C: TextBlob basit bir araçtır, %60-70 doğruluk. İleri seviye için BERT kullanılabilir.

### Performans Sorular

**S: Tipik backtest getirisi nedir?**
C: Piyasa koşullarına göre değişir, %5-20 yıllık getiri makul beklenti.

**S: Maximum drawdown ne olmalı?**
C: %10'un altında ideal, %20'nin üstü riskli kabul edilir.

**S: Kaç sembolde test etmeliyim?**
C: Çeşitlilik için en az 5-10 farklı sektörden sembol önerilir.

### Hata Giderme

**S: "Import error" alıyorum**
C: `pip install -r requirements.txt` komutunu çalıştırın.

**S: Veri çekilmiyor**
C: İnternet bağlantısını kontrol edin, sembol adlarının doğru olduğundan emin olun.

**S: Model eğitimi çok yavaş**
C: Daha az veri kullanın veya model karmaşıklığını azaltın.

### Geliştime Soruları

**S: Kendi stratejimi nasıl eklerim?**
C: `strategy_executor.py` dosyasındaki `generate_trade_decision()` fonksiyonunu düzenleyin.

**S: Yeni veri kaynağı nasıl eklerim?**
C: `data_handler.py` dosyasına yeni fonksiyon ekleyin ve `main.py`'da çağırın.

**S: Real-time trading nasıl implement edilir?**
C: Broker API entegrasyonu gerekir (Alpaca, Interactive Brokers vb.).

---

Bu dokümantasyon projenin teknik detaylarını kapsamlı şekilde açıklamaktadır. Geliştirme sırasında referans olarak kullanılabilir.
