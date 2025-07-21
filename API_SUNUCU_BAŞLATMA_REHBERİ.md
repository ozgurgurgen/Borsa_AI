🚀 **API SUNUCUSU BAŞLATMA REHBERİ** 🚀

## ❌ **Sorun:**
Flutter uygulaması çalışıyor ama backend API'sine bağlanamıyor:
```
XMLHttpRequest error., uri=http://localhost:8000/api/...
```

## ✅ **Çözüm:**

### **1. Hızlı Başlatma (ÇİFT TIKLA):**
```
📁 c:\Users\gurge\Desktop\BorsAI\start_api_server.bat
```
Bu dosyayı Windows Explorer'da bulup **çift tıklayın**.

### **2. Manuel Komut:**
Yeni bir **Command Prompt** açın ve:
```cmd
cd "c:\Users\gurge\Desktop\BorsAI"
.\.venv\Scripts\python.exe simple_api_server.py
```

### **3. PowerShell ile:**
```powershell
cd "c:\Users\gurge\Desktop\BorsAI"
.\.venv\Scripts\python.exe simple_api_server.py
```

## 🎯 **Başarı Kontrolleri:**

### **API Sunucusu Çalıştı mı?**
Tarayıcıda test edin:
- http://localhost:8000/api/health
- http://localhost:8000/api/status
- http://localhost:8000/api/portfolio

### **Flutter Bağlantısı:**
API çalıştıktan sonra Flutter uygulamasında:
- ✅ Hisse verileri yüklenecek
- ✅ Portföy bilgileri görünecek  
- ✅ Haberler listelenecek
- ✅ Bot kontrolleri çalışacak

## 📋 **Eklenen Endpoint'ler:**

```
✅ GET  /api/stocks/{symbol}?days=30     # Hisse verileri
✅ GET  /api/sentiment/{symbol}?days=30  # Duygu analizi  
✅ GET  /api/signals?limit=20           # Ticaret sinyalleri
✅ GET  /api/portfolio                  # Portföy
✅ GET  /api/news/{symbol}?limit=50     # Haberler
✅ GET  /api/settings                   # Ayarlar
✅ POST /api/start                      # Bot başlat
✅ POST /api/stop                       # Bot durdur
✅ GET  /api/health                     # Sağlık kontrolü
```

## 🚨 **Acil Çözüm:**

**start_api_server.bat** dosyasını **çift tıklayın**!

Siyah bir pencere açılacak ve şu mesajları göreceksiniz:
```
🚀 AI-FTB API Sunucusu başlatılıyor...
📡 URL: http://localhost:8000
🔗 Health Check: http://localhost:8000/api/health
```

Bu pencereyi açık bırakın. Flutter uygulaması artık çalışacak! 🎉
