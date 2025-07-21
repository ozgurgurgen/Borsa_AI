# UTF-8 Karakter Düzeltmeleri

## 🔧 Yapılan Düzeltmeler

### 1. UTF-8 Kod Sayfası Ayarı
Tüm .bat dosyalarının başına eklendi:
```batch
@echo off
chcp 65001 >nul
```

### 2. Düzeltilen Dosyalar
- ✅ `upload_to_github.bat` - GitHub yükleme scripti
- ✅ `quick_start.bat` - Hızlı başlatma scripti 
- ✅ `create_shortcuts.bat` - Masaüstü kısayol oluşturucu
- ✅ `master_control.bat` - Ana kontrol menüsü
- ✅ `start_api_server.bat` - API sunucu başlatıcı
- ✅ `flutter_app/restart_flutter.bat` - Flutter restart scripti

### 3. Değiştirilen Karakterler

#### Türkçe Karakterler → ASCII Eşdeğerleri:
- `ı` → `i`
- `ç` → `c`
- `ğ` → `g`
- `ö` → `o`
- `ş` → `s`
- `ü` → `u`
- `İ` → `I`
- `Ç` → `C`
- `Ğ` → `G`
- `Ö` → `O`
- `Ş` → `S`
- `Ü` → `U`

#### Örnekler:
- başlatılıyor → baslatiliyor
- yükleme → yukleme
- güncelle → guncelle
- özelleştir → ozellestir
- değiştir → degistir
- çalıştır → calistir
- bağımlılık → bagimlilik
- işlem → islem
- ücretsiz → ucretsiz

### 4. Korunan Öğeler
- 🎯 Emojiler korundu (UTF-8 desteğiyle çalışır)
- 📊 ASCII box characters korundu
- 🔗 URL'ler ve path'ler korundu
- 💻 Komut satırı parametreleri korundu

### 5. Test Dosyası
`UTF8_TEST.bat` oluşturuldu - karakterlerin doğru görüntülendiğini test eder.

## 🎯 Sonuç

Artık tüm .bat dosyaları Windows'ta karakter bozukluğu olmadan çalışacak:
- ✅ Konsol çıktıları düzgün görünür
- ✅ Menüler düzgün çalışır
- ✅ Türkçe metinler okunabilir
- ✅ Emojiler korunur

## 🔧 Kullanım

1. **Test**: `UTF8_TEST.bat` çalıştırarak kontrol edin
2. **Ana Menü**: `master_control.bat` ile merkezi erişim
3. **Hızlı Başlat**: `quick_start.bat` ile direkt çalıştırma

## 📝 Not

- Windows Terminal ve PowerShell UTF-8'i daha iyi destekler
- Eski CMD pencerelerinde bazı karakterler farklı görünebilir
- Emoji'ler modern terminallerde en iyi çalışır
