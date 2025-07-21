# AI-FTB Flutter Mobil Uygulaması

Bu dizin, AI-FTB (AI Destekli Finansal Ticaret Botu) için Flutter ile geliştirilmiş mobil uygulamayı içerir.

## Özellikler

### 📱 Ana Ekranlar
- **Ana Sayfa**: Bot durumu, portföy özeti ve hızlı erişim
- **Dashboard**: Detaylı grafikler ve analiz sonuçları
- **Portföy**: Pozisyonlar, kar/zarar ve işlem geçmişi
- **Haberler**: Finansal haberler ve duygu analizi sonuçları
- **Ayarlar**: Bot konfigürasyonu ve uygulama ayarları

### 🎯 Temel Fonksiyonlar
- **Real-time Bot Kontrolü**: Bot'u başlatma/durdurma
- **Portföy Takibi**: Anlık portföy değeri ve performans
- **Grafik Analizi**: Fiyat ve duygu analizi grafikleri
- **Haber İzleme**: Duygu skorlu finansal haberler
- **Risk Yönetimi**: Detaylı risk ayarları
- **Trading Sinyalleri**: ML modeli tarafından üretilen sinyaller

### 🔧 Teknik Özellikler
- **State Management**: Riverpod
- **HTTP İstekleri**: Dio & HTTP
- **Grafikler**: FL Chart & Syncfusion
- **Material Design**: Modern ve kullanıcı dostu arayüz
- **Mock Data**: Backend hazır olmadığında mock veri desteği
- **Responsive Design**: Tablet ve telefon desteği

## Kurulum

### 1. Gereksinimler
```bash
# Flutter SDK (3.10.0+)
flutter --version

# Dart SDK dahil
dart --version
```

### 2. Bağımlılıkları Yükle
```bash
cd flutter_app
flutter pub get
```

### 3. Python Backend'i Başlat
```bash
# Ana dizinde
python api_server.py
```
Backend http://localhost:8000 adresinde çalışacak.

### 4. Flutter Uygulamasını Çalıştır
```bash
# flutter_app dizininde
flutter run
```

## API Endpoints

Backend servisi aşağıdaki endpoint'leri sağlar:

### Bot Kontrolü
- `GET /api/status` - Bot durumu
- `POST /api/start` - Bot'u başlat
- `POST /api/stop` - Bot'u durdur

### Veri Endpoints
- `GET /api/portfolio` - Portföy verileri
- `GET /api/stocks/<symbol>?days=30` - Hisse verileri
- `GET /api/sentiment/<symbol>?days=7` - Duygu analizi
- `GET /api/news/<symbol>?limit=20` - Finansal haberler
- `GET /api/signals?limit=10` - Trading sinyalleri

### Ayarlar
- `GET /api/settings` - Bot ayarları
- `PUT /api/settings` - Ayarları güncelle

### Diğer
- `POST /api/backtest` - Backtest çalıştır
- `GET /health` - Sağlık kontrolü

## Ekran Görüntüleri

### Ana Sayfa
- Bot durumu kartı (açık/kapalı, performans)
- Portföy özeti (toplam değer, günlük değişim)
- Piyasa genel bakış (hisse fiyatları)
- Son sinyaller listesi
- Hızlı erişim butonları

### Dashboard
- Fiyat grafikleri (zaman serisi)
- Duygu analizi grafikleri
- Teknik göstergeler
- Detaylı sinyal listesi

### Portföy
- Toplam portföy değeri ve getiri
- Pozisyon detayları (hisse, kar/zarar)
- Son işlemler geçmişi
- Performance metrikleri

### Haberler
- Finansal haber listesi
- Duygu skorları (pozitif/negatif/nötr)
- Haber detay modal'ı
- Sembol bazlı filtreleme

### Ayarlar
- Risk yönetimi parametreleri
- Duygu analizi eşikleri
- ML model seçimi
- Uygulama ayarları
- Tehlikeli işlemler (reset/clear)

## Dosya Yapısı

```
lib/
├── main.dart              # Ana uygulama
├── models/
│   └── trading_models.dart # Veri modelleri
├── services/
│   └── api_service.dart   # Backend iletişimi
├── screens/
│   ├── home_screen.dart   # Ana sayfa
│   ├── dashboard_screen.dart # Grafik paneli
│   ├── portfolio_screen.dart # Portföy
│   ├── news_screen.dart   # Haberler
│   └── settings_screen.dart # Ayarlar
└── widgets/
    ├── status_card.dart   # Bot durum kartı
    ├── portfolio_summary_card.dart # Portföy özeti
    ├── recent_signals_card.dart # Son sinyaller
    └── market_overview_card.dart # Piyasa genel bakış
```

## Kullanım

### 1. Backend'i Başlat
```bash
python api_server.py
```

### 2. Uygulamayı Aç
- Ana sayfa otomatik yüklenir
- Bot durumunu kontrol et
- Gerekirse bot'u başlat

### 3. Verileri İncele
- Dashboard'da grafikler
- Portföy'de pozisyonlar
- Haberler'de duygu analizi
- Ayarlar'da risk parametreleri

## Geliştirme

### Mock Data
Backend'e bağlanılamadığında uygulama otomatik olarak mock veri kullanır:
- `MockDataService.getMockStockData()`
- `MockDataService.getMockNews()`
- `MockDataService.getMockPortfolio()`
- `MockDataService.getMockBotStatus()`

### State Management
Riverpod kullanarak:
- Global state yönetimi
- Provider pattern
- Dependency injection

### Tema ve Tasarım
- Material Design 3
- Koyu/açık tema desteği
- Responsive layout
- Accessibility özellikleri

## Sorun Giderme

### Backend Bağlantı Sorunu
```
Error: Backend'e bağlanılamıyor
```
**Çözüm**: `api_server.py`'nin çalıştığından emin olun.

### Veri Yüklenmiyor
```
Veri yüklenirken hata oluştu
```
**Çözüm**: İnternet bağlantısını kontrol edin, refresh butonuna basın.

### Build Hatası
```
pub get failed
```
**Çözüm**: `flutter clean && flutter pub get`

## Gelecek Özellikler

- [ ] Push notification desteği
- [ ] Offline mod
- [ ] Grafik export (PDF/PNG)
- [ ] Çoklu portföy desteği
- [ ] Advanced charting (candlestick)
- [ ] Real-time WebSocket data
- [ ] Biometric authentication
- [ ] Watchlist özelliği
- [ ] Price alerts
- [ ] Social trading

## Lisans

Bu proje AI-FTB ana projesi ile aynı lisansa sahiptir.

---

**Not**: Bu mobil uygulama eğitim ve demo amaçlıdır. Gerçek trading'de kullanmadan önce kapsamlı test edilmelidir.
