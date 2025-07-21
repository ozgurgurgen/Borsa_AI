# AI-FTB: Yapay Zeka Destekli Finansal Ticaret Botu

## 📊 Proje Hakkında

AI-FTB (AI-Powered Financial Trading Bot), Python tabanlı bir yapay zeka destekli finansal ticaret botudur. Geçmiş fiyat hareketlerini ve finansal haber metinlerini analiz ederek alım-satım sinyalleri üretir ve bu sinyallere dayanarak işlem kararları için öneriler sunar.

### 🎯 Ana Özellikler

- **Teknik Analiz**: RSI, MACD, Bollinger Bands, SMA ve diğer teknik göstergeler
- **Duygu Analizi**: Finansal haberlerin sentiment analizi (TextBlob)
- **Makine Öğrenimi**: RandomForest ve LogisticRegression modelleri
- **Risk Yönetimi**: Stop-loss, take-profit ve pozisyon büyüklüğü hesaplama
- **Backtest**: Tarihsel veriler üzerinde strateji performans testi
- **Modüler Yapı**: Temiz, okunabilir ve genişletilebilir kod yapısı
- **📱 Flutter Mobil Uygulama**: Modern, kullanıcı dostu mobil arayüz

## 🚀 Hızlı Başlangıç

### Gereksinimler

- Python 3.9 veya üzeri
- İnternet bağlantısı (veri çekme için)
- **Flutter SDK 3.10.0+ (Mobil uygulama için)**

### Kurulum

1. **Projeyi indirin:**
```bash
git clone <repository-url>
cd BorsAI
```

2. **Sanal ortam oluşturun (önerilen):**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\\Scripts\\activate  # Windows
```

3. **Gerekli paketleri yükleyin:**
```bash
pip install -r requirements.txt
```

4. **NLTK verilerini indirin (ilk çalıştırmada):**
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

### 📱 Mobil Uygulama Kurulumu

1. **Flutter SDK'yi kurun:**
   - [Flutter Kurulum Rehberi](https://flutter.dev/docs/get-started/install)

2. **Flutter bağımlılıklarını yükleyin:**
```bash
cd flutter_app
flutter pub get
```

### Kullanım

#### 🖥️ Python Backend (Konsol)

1. **Model Eğitimi ve Backtest (Varsayılan):**
```bash
python main.py
# veya
python main.py training
```

2. **Belirli Sembol Analizi:**
```bash
python main.py analysis AAPL
```

3. **Sistem Testleri:**
```bash
python main.py test
```

#### � Mobil Uygulama

1. **API Server'ı Başlatın:**
```bash
python api_server.py
```
Server http://localhost:8000 adresinde çalışacak.

2. **Flutter Uygulamasını Başlatın:**
```bash
# Windows
run_flutter_app.bat

# PowerShell
./run_flutter_app.ps1

# Manuel
cd flutter_app
flutter run
```

## �📁 Proje Yapısı

```
BorsAI/
├── 🐍 Python Backend
│   ├── config.py                 # Konfigürasyon ayarları
│   ├── logger.py                 # Merkezi loglama sistemi
│   ├── data_handler.py           # Veri çekme ve işleme
│   ├── feature_engineer.py       # Teknik göstergeler ve özellik mühendisliği
│   ├── news_sentiment_analyzer.py # Haber analizi ve duygu analizi
│   ├── ml_model.py               # Makine öğrenimi modelleri
│   ├── strategy_executor.py      # Ticaret stratejisi ve karar verme
│   ├── backtester.py             # Backtest ve performans analizi
│   ├── main.py                   # Ana program (konsol)
│   ├── api_server.py             # Flask API serveri
│   └── requirements.txt          # Python paket gereksinimleri
├── 📱 Flutter Mobil Uygulama
│   ├── lib/
│   │   ├── main.dart             # Ana uygulama
│   │   ├── models/               # Veri modelleri
│   │   ├── services/             # API servisleri
│   │   ├── screens/              # Ekranlar
│   │   └── widgets/              # UI bileşenleri
│   ├── pubspec.yaml              # Flutter bağımlılıkları
│   └── README.md                 # Flutter uygulama dokümantasyonu
├── 📂 Veri ve Çıktılar
│   ├── logs/                     # Log dosyaları
│   ├── data/                     # Çekilmiş ve işlenmiş veriler
│   └── models/                   # Eğitilmiş ML modelleri ve scalerlar
└── 🚀 Başlatma Scriptleri
    ├── run_flutter_app.bat       # Windows için mobil uygulama başlatıcı
    └── run_flutter_app.ps1       # PowerShell için mobil uygulama başlatıcı
```

## ⚙️ Konfigürasyon

`config.py` dosyasında aşağıdaki ayarları değiştirebilirsiniz:

### Temel Ayarlar
```python
# İşlem yapılacak semboller
SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']

# Veri aralığı
HISTORICAL_DATA_START_DATE = '2020-01-01'
HISTORICAL_DATA_END_DATE = '2024-12-31'

# Risk yönetimi
RISK_PER_TRADE_PERCENT = 0.01  # %1 risk
STOP_LOSS_PERCENT = 0.02       # %2 stop loss
TAKE_PROFIT_PERCENT = 0.04     # %4 take profit
```

### ML Model Ayarları
```python
# Model tipi
ML_MODEL_TYPE = 'RandomForestClassifier'  # veya 'LogisticRegression'

# Model parametreleri
ML_MODEL_PARAMS = {
    'n_estimators': 100,
    'max_depth': 10,
    'random_state': 42
}
```

### Duygu Analizi Ayarları
```python
# Duygu eşikleri
SENTIMENT_THRESHOLD_POSITIVE = 0.2
SENTIMENT_THRESHOLD_NEGATIVE = -0.2

# News API ayarları (opsiyonel)
API_KEYS = {
    'NEWS_API_KEY': 'YOUR_API_KEY_HERE'
}
```

## 📈 Modüller Detayı

### 1. Data Handler (`data_handler.py`)
- **Amaç**: Finansal veri çekme ve ön işleme
- **Özellikler**:
  - yfinance ile tarihsel OHLCV verisi çekme
  - Veri temizleme ve doğrulama
  - CSV formatında kaydetme/yükleme
  - Güncel fiyat bilgisi alma

### 2. Feature Engineer (`feature_engineer.py`)
- **Amaç**: Teknik göstergeler ve ML özellikleri
- **Özellikler**:
  - RSI, MACD, Bollinger Bands hesaplama
  - Hareketli ortalamalar (SMA)
  - Volatilite ve hacim göstergeleri
  - Özellik ölçeklendirme (StandardScaler/MinMaxScaler)

### 3. News Sentiment Analyzer (`news_sentiment_analyzer.py`)
- **Amaç**: Haber analizi ve duygu skoru
- **Özellikler**:
  - News API entegrasyonu (opsiyonel)
  - TextBlob ile duygu analizi
  - Metin ön işleme
  - Tarihsel duygu skorları

### 4. ML Model (`ml_model.py`)
- **Amaç**: Makine öğrenimi modelleri
- **Özellikler**:
  - RandomForest ve LogisticRegression
  - Cross-validation
  - Hiperparametre optimizasyonu (GridSearch)
  - Model kaydetme/yükleme
  - Performans değerlendirme

### 5. Strategy Executor (`strategy_executor.py`)
- **Amaç**: Ticaret kararları ve risk yönetimi
- **Özellikler**:
  - ML sinyali + duygu skorunu birleştirme
  - Pozisyon büyüklüğü hesaplama
  - Stop-loss/Take-profit kontrolü
  - Portföy metrikleri

### 6. Backtester (`backtester.py`)
- **Amaç**: Strateji performans testi
- **Özellikler**:
  - Tarihsel simülasyon
  - Detaylı performans metrikleri
  - Maximum drawdown hesaplama
  - Sharpe ratio ve diğer risk metrikleri
  - Trade log ve portföy geçmişi

## 📊 Örnek Kullanım Senaryoları

### Senaryo 1: Temel Backtest
```python
# config.py'de SYMBOLS = ['AAPL'] ayarlayın
python main.py training
```

**Beklenen Çıktı:**
- AAPL için veri çekilir
- Teknik göstergeler hesaplanır
- ML modeli eğitilir
- Backtest çalıştırılır
- Performans raporu oluşturulur

### Senaryo 2: Çoklu Sembol Analizi
```python
# config.py'de SYMBOLS = ['AAPL', 'MSFT', 'GOOGL'] ayarlayın
python main.py training
```

**Beklenen Çıktı:**
- Her sembol için ayrı model eğitilir
- Karşılaştırmalı performans raporu
- En iyi performans gösteren sembol

### Senaryo 3: Anlık Analiz
```python
python main.py analysis AAPL full
```

**Beklenen Çıktı:**
- Güncel teknik göstergeler
- Duygu analizi
- Model tahmini
- Önerilen işlem sinyali

## 📋 Performans Metrikleri

Bot aşağıdaki metrikleri hesaplar:

### Getiri Metrikleri
- **Toplam Getiri**: Yüzde ve dolar bazında
- **Yıllık Getiri**: Annualized return
- **Aylık Getiriler**: Ay bazında performans

### Risk Metrikleri
- **Maximum Drawdown**: En büyük kayıp yüzdesi
- **Volatilite**: Günlük getiri standart sapması
- **Sharpe Ratio**: Risk-adjusted return

### İşlem Metrikleri
- **Toplam İşlem Sayısı**: Alım/satım işlemleri
- **Kazanma Oranı**: Karlı işlem yüzdesi
- **Profit Factor**: Brüt kar / Brüt zarar
- **Ortalama İşlem**: Ortalama kar/zarar

### Performans Notu
Bot performansını A+ ile F arası notlarla değerlendirir:
- **A+/A**: Mükemmel performans (>85 puan)
- **B+/B**: İyi performans (75-85 puan)
- **C+/C**: Orta performans (60-75 puan)
- **D**: Zayıf performans (50-60 puan)
- **F**: Başarısız performans (<50 puan)

## 🛠️ Geliştirme Rehberi

### Yeni Teknik Gösterge Ekleme

1. `feature_engineer.py` dosyasında yeni fonksiyon yazın:
```python
def calculate_your_indicator(prices, period=14):
    # Hesaplama mantığı
    return indicator_values
```

2. `add_technical_indicators()` fonksiyonuna ekleyin:
```python
data['Your_Indicator'] = calculate_your_indicator(data['Close'])
```

3. `config.py`'de ML_FEATURES listesine ekleyin:
```python
ML_FEATURES = [..., 'Your_Indicator']
```

### Yeni ML Modeli Ekleme

1. `ml_model.py` dosyasında `train_model()` fonksiyonuna yeni model tipini ekleyin:
```python
elif model_type == 'YourNewModel':
    model = YourNewModel(**params)
```

2. `config.py`'de model tipini ayarlayın:
```python
ML_MODEL_TYPE = 'YourNewModel'
```

### Yeni Strateji Kuralı Ekleme

1. `strategy_executor.py` dosyasında `generate_trade_decision()` fonksiyonunu güncelleyin:
```python
# Yeni karar mantığı
if your_condition:
    decision = 'BUY'
    confidence = 0.8
    reasoning_parts.append("Your reasoning")
```

## 🔧 Sorun Giderme

### Sık Karşılaşılan Sorunlar

1. **Import Hataları**
   ```bash
   pip install -r requirements.txt
   ```

2. **Veri Çekme Hataları**
   - İnternet bağlantısını kontrol edin
   - Sembol adlarının doğru olduğundan emin olun
   - yfinance sunucu durumunu kontrol edin

3. **Model Eğitimi Hataları**
   - Yeterli veri olup olmadığını kontrol edin (min 100 gün)
   - NaN değerleri kontrol edin
   - Özellik isimlerinin config ile uyumlu olduğundan emin olun

4. **Bellek Sorunları**
   - Daha az sembol ile test edin
   - Veri aralığını kısaltın
   - Model karmaşıklığını azaltın

### Log Dosyaları

Detaylı hata bilgileri için `logs/bot_activity.log` dosyasını kontrol edin.

### Debug Modu

Daha detaylı loglar için `config.py`'de:
```python
LOG_LEVEL = 'DEBUG'
```

## ⚠️ Önemli Uyarılar

1. **Yatırım Tavsiyesi Değildir**: Bu bot eğitim amaçlıdır, gerçek yatırım kararları için kullanmayın.

2. **Risk Yönetimi**: Gerçek işlemlerde mutlaka stop-loss ve pozisyon büyüklüğü kontrolü yapın.

3. **Backtest Sınırları**: Geçmiş performans gelecek performansı garanti etmez.

4. **API Sınırları**: Haber API'lerinin kullanım sınırları olabilir.

5. **Piyasa Saatleri**: Gerçek uygulamada piyasa saatlerini dikkate alın.

## 📚 Ek Kaynaklar

- [yfinance Dokümantasyonu](https://pypi.org/project/yfinance/)
- [scikit-learn Rehberi](https://scikit-learn.org/stable/user_guide.html)
- [TextBlob Dokümantasyonu](https://textblob.readthedocs.io/)
- [Pandas Dokümantasyonu](https://pandas.pydata.org/docs/)

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje eğitim amaçlıdır. Ticari kullanım öncesi geliştirici ile iletişime geçin.

## 📞 İletişim

Sorularınız için:
- GitHub Issues bölümünü kullanın
- Detaylı hata raporları için log dosyalarını ekleyin
- Yeni özellik önerileri için enhancement label'ı kullanın

---

**Başarılı trading! 📈**
