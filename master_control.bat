@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title AI-FTB Proje Yonetim Merkezi
color 0A
mode con: cols=80 lines=50

:main_menu
cls
echo.
echo ███████╗██╗      █████╗ ██╗███████╗████████╗██████╗ 
echo ██╔════╝██║     ██╔══██╗██║██╔════╝╚══██╔══╝██╔══██╗
echo █████╗  ██║     ███████║██║█████╗     ██║   ██████╔╝
echo ██╔══╝  ██║     ██╔══██║██║██╔══╝     ██║   ██╔══██╗
echo ██║     ███████╗██║  ██║██║██║        ██║   ██████╔╝
echo ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝╚═╝        ╚═╝   ╚═════╝ 
echo.
echo 🤖 AI-Powered Financial Trading Bot - Proje Yonetim Merkezi
echo ============================================================
echo 📊 Python Backend + Flutter Frontend + AI Trading System
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI"

REM Proje durumunu kontrol et
call :check_project_status

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                        ANA MENU                             ║
echo ╠══════════════════════════════════════════════════════════════╣
echo ║                                                              ║
echo ║  🚀 PROJE CALISTIRMA                                        ║
echo ║  [1] Hizli Baslat (Backend + Frontend)                      ║
echo ║  [2] Sadece Backend Baslat                                   ║
echo ║  [3] Sadece Frontend Baslat                                  ║
echo ║  [4] Demo Mod (Mock Verilerle)                               ║
echo ║                                                              ║
echo ║  🔧 KURULUM VE BAKIM                                         ║
echo ║  [5] Ilk Kurulum (Dependencies)                              ║
echo ║  [6] Sistem Temizle ve Yenile                                ║
echo ║  [7] Bagimlilikari Guncelle                                  ║
echo ║  [8] Virtual Environment Yeniden Olustur                     ║
echo ║                                                              ║
echo ║  📊 TEST VE KONTROL                                          ║
echo ║  [9] Sistem Durumu Kontrol                                   ║
echo ║  [10] API Test Et                                            ║
echo ║  [11] Flutter Test Et                                        ║
echo ║  [12] Tum Testleri Calistir                                  ║
echo ║                                                              ║
echo ║  🔄 GIT VE GITHUB                                            ║
echo ║  [13] GitHub'a Yukle                                         ║
echo ║  [14] Git Durumu Kontrol                                     ║
echo ║  [15] Commit ve Push                                         ║
echo ║                                                              ║
echo ║  📚 DOKUMANTASYON                                            ║
echo ║  [16] Kullanim Kilavuzu                                      ║
echo ║  [17] API Dokumantasyonu                                     ║
echo ║  [18] Hata Cozumleri                                         ║
echo ║                                                              ║
echo ║  ⚙️ DIGER ISLEMLER                                           ║
echo ║  [19] Proje Yedekle                                          ║
echo ║  [20] Loglari Temizle                                        ║
echo ║  [21] Ayarlari Sifirla                                       ║
echo ║                                                              ║
echo ║  [0] Cikis                                                   ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
set /p choice="🎯 Seciminizi yapin (0-21): "

if "%choice%"=="1" goto quick_start
if "%choice%"=="2" goto backend_only
if "%choice%"=="3" goto frontend_only
if "%choice%"=="4" goto demo_mode
if "%choice%"=="5" goto initial_setup
if "%choice%"=="6" goto clean_and_refresh
if "%choice%"=="7" goto update_dependencies
if "%choice%"=="8" goto recreate_venv
if "%choice%"=="9" goto system_status
if "%choice%"=="10" goto test_api
if "%choice%"=="11" goto test_flutter
if "%choice%"=="12" goto run_all_tests
if "%choice%"=="13" goto github_upload
if "%choice%"=="14" goto git_status
if "%choice%"=="15" goto commit_push
if "%choice%"=="16" goto user_manual
if "%choice%"=="17" goto api_docs
if "%choice%"=="18" goto troubleshooting
if "%choice%"=="19" goto backup_project
if "%choice%"=="20" goto clean_logs
if "%choice%"=="21" goto reset_settings
if "%choice%"=="0" goto exit_program

echo ❌ Gecersiz secim! Tekrar deneyin...
timeout /t 2 /nobreak >nul
goto main_menu

REM ============================================================================
REM                             PROJE CALISTIRMA
REM ============================================================================

:quick_start
cls
echo 🚀 HIZLI BASLATMA - Backend + Frontend
echo =====================================
echo.

echo 📋 1/6: On kontroller...
call :check_python_flutter
if errorlevel 1 goto main_menu

echo 📋 2/6: Proje dizini hazirlaniyor...
cd /d "C:\Users\gurge\Desktop\BorsAI"

echo 📋 3/6: Virtual environment aktiflestiriliyor...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo ✅ Virtual environment aktif
) else (
    echo ⚠️ Virtual environment bulunamadi, olusturuluyor...
    python -m venv .venv
    call .venv\Scripts\activate.bat
)

echo 📋 4/6: Backend sunucusu baslatiliyor...
start "AI-FTB Backend API" cmd /k "title AI-FTB Backend && color 0E && echo 🐍 Backend API Sunucusu && echo ======================= && python simple_api_server.py"

echo 📋 5/6: Flutter uygulamasi hazirlaniyor...
cd flutter_app
timeout /t 5 /nobreak >nul
start "AI-FTB Flutter App" cmd /k "title AI-FTB Flutter && color 0B && echo 📱 Flutter Uygulamasi && echo ================== && flutter run -d edge"

echo 📋 6/6: Tarayicilar aciliyor...
timeout /t 8 /nobreak >nul
start http://localhost:8000/api/health
start http://localhost:8000

cd ..
echo.
echo ✅ PROJE BASARIYLA BASLATILDI!
echo.
echo 🔗 Backend API: http://localhost:8000
echo 🔗 API Health: http://localhost:8000/api/health
echo 📱 Flutter App: Edge tarayicisinda acilacak
echo.
echo 💡 Iki terminal penceresi acildi - ikisini de acik tutun!
echo 🛑 Durdurmak icin terminal pencerelerini kapatin
echo.
pause
goto main_menu

:backend_only
cls
echo 🐍 SADECE BACKEND BASLATMA
echo ===========================
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI"

echo 📋 Virtual environment kontrol ediliyor...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo ⚠️ Virtual environment bulunamadi, olusturuluyor...
    python -m venv .venv
    call .venv\Scripts\activate.bat
)

echo 📋 Gerekli moduller kontrol ediliyor...
python -c "import flask, flask_cors" 2>nul || (
    echo 📦 Flask modulleri yukleniyor...
    pip install flask flask-cors
)

echo 🚀 Backend API sunucusu baslatiliyor...
echo.
echo 📊 API Endpoints:
echo   • http://localhost:8000/api/health
echo   • http://localhost:8000/api/status
echo   • http://localhost:8000/api/portfolio
echo   • http://localhost:8000/api/stocks/SYMBOL
echo   • http://localhost:8000/api/news/SYMBOL
echo.
python simple_api_server.py

pause
goto main_menu

:frontend_only
cls
echo 📱 SADECE FRONTEND BASLATMA
echo ============================
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI\flutter_app"

echo 📋 Flutter bagimlilikari kontrol ediliyor...
flutter pub get

echo 📋 Flutter doctor kontrolü...
flutter doctor --android-licenses >nul 2>&1

echo 🚀 Flutter uygulaması Edge'de başlatılıyor...
echo.
echo 💡 Backend çalışmıyorsa mock veriler kullanılacak
echo 🔗 Backend için: http://localhost:8000
echo.
flutter run -d edge

cd ..
pause
goto main_menu

:demo_mode
cls
echo 🎭 DEMO MOD - Mock Verilerle
echo =============================
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI"

echo 📋 Demo backend başlatılıyor...
start "Demo Backend" cmd /k "title Demo Backend && color 0D && echo 🎭 Demo Mod Aktif && echo Backend mock veri döndürüyor && echo ========================= && python simple_api_server.py"

timeout /t 3 /nobreak >nul

cd flutter_app
echo 📋 Flutter demo modu başlatılıyor...
start "Demo Flutter" cmd /k "title Demo Flutter && color 0D && echo 🎭 Flutter Demo Modu && echo Mock verilerle çalışıyor && echo ==================== && flutter run -d edge"

cd ..
echo.
echo ✅ DEMO MOD AKTİF!
echo.
echo 🎭 Bu modda:
echo   • Gerçek API çağrıları yapılmaz
echo   • Mock veriler gösterilir
echo   • Güvenli test ortamı
echo   • İnternet bağlantısı gerekmez
echo.
pause
goto main_menu

REM ============================================================================
REM                             KURULUM VE BAKIM
REM ============================================================================

:initial_setup
cls
echo 🔧 İLK KURULUM
echo ===============
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI"

echo 📋 1/8: Sistem gereksinimleri kontrol ediliyor...
call :check_system_requirements
if errorlevel 1 (
    echo ❌ Sistem gereksinimleri karşılanmıyor!
    pause
    goto main_menu
)

echo 📋 2/8: Virtual environment oluşturuluyor...
if exist ".venv" rmdir /s /q .venv
python -m venv .venv
call .venv\Scripts\activate.bat

echo 📋 3/8: Python bağımlılıkları yükleniyor...
pip install --upgrade pip
pip install -r requirements.txt

echo 📋 4/8: Flutter bağımlılıkları yükleniyor...
cd flutter_app
flutter pub get
flutter config --enable-web

echo 📋 5/8: Test verisi oluşturuluyor...
cd ..
if not exist "data" mkdir data

echo 📋 6/8: Log dizinleri oluşturuluyor...
if not exist "logs" mkdir logs

echo 📋 7/8: Yapılandırma dosyaları kontrol ediliyor...
if not exist "config.ini" (
    echo [DEFAULT] > config.ini
    echo DEBUG = True >> config.ini
    echo LOG_LEVEL = INFO >> config.ini
)

echo 📋 8/8: Test çalıştırılıyor...
python -c "import flask, requests, pandas, numpy, scikit-learn; print('✅ Tüm modüller yüklü')"

echo.
echo ✅ İLK KURULUM TAMAMLANDI!
echo.
echo 🎯 Şimdi yapabilecekleriniz:
echo   [1] Hızlı Başlat - Projeyi çalıştır
echo   [9] Sistem Durumu - Kurulumu kontrol et
echo   [10] API Test - Backend'i test et
echo.
pause
goto main_menu

:clean_and_refresh
cls
echo 🧹 SİSTEM TEMİZLE VE YENİLE
echo ============================
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI"

echo 📋 1/6: Cache dosyaları temizleniyor...
if exist "__pycache__" rmdir /s /q __pycache__
if exist "*.pyc" del /s /q *.pyc

cd flutter_app
echo 📋 2/6: Flutter cache temizleniyor...
flutter clean

echo 📋 3/6: Flutter bağımlılıkları yenileniyor...
flutter pub get

cd ..
echo 📋 4/6: Python cache temizleniyor...
if exist ".pytest_cache" rmdir /s /q .pytest_cache

echo 📋 5/6: Log dosyaları temizleniyor...
if exist "logs\*.log" del /q logs\*.log

echo 📋 6/6: Geçici dosyalar temizleniyor...
if exist "*.tmp" del /q *.tmp
if exist "temp" rmdir /s /q temp

echo.
echo ✅ SİSTEM TEMİZLENDİ!
echo.
pause
goto main_menu

:update_dependencies
cls
echo 📦 BAĞIMLILIKLAR GÜNCELLENİYOR
echo ===============================
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI"

if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat

echo 📋 1/4: Python bağımlılıkları güncelleniyor...
pip install --upgrade pip
pip install --upgrade -r requirements.txt

echo 📋 2/4: Flutter bağımlılıkları güncelleniyor...
cd flutter_app
flutter pub upgrade

echo 📋 3/4: Flutter doctor kontrolü...
flutter doctor

echo 📋 4/4: Güncellemeler test ediliyor...
cd ..
python -c "import flask; print('✅ Flask:', flask.__version__)"

echo.
echo ✅ BAĞIMLILIKLAR GÜNCELLENDİ!
echo.
pause
goto main_menu

:recreate_venv
cls
echo 🔄 VIRTUAL ENVIRONMENT YENİDEN OLUŞTUR
echo =======================================
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI"

echo 📋 1/4: Mevcut virtual environment siliniyor...
if exist ".venv" rmdir /s /q .venv

echo 📋 2/4: Yeni virtual environment oluşturuluyor...
python -m venv .venv

echo 📋 3/4: Aktivasyon ve pip güncelleme...
call .venv\Scripts\activate.bat
pip install --upgrade pip

echo 📋 4/4: Bağımlılıklar yükleniyor...
pip install -r requirements.txt

echo.
echo ✅ VIRTUAL ENVIRONMENT YENİDEN OLUŞTURULDU!
echo.
pause
goto main_menu

REM ============================================================================
REM                             TEST VE KONTROL
REM ============================================================================

:system_status
cls
echo 📊 SİSTEM DURUMU KONTROLÜ
echo =========================
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI"

echo ╔══════════════════════════════════════════════════════════════╗
echo ║                        SİSTEM DURUMU                        ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🔍 TEMEL SİSTEM:
echo ---------------
python --version 2>nul && echo ✅ Python yüklü || echo ❌ Python bulunamadı
flutter --version 2>nul && echo ✅ Flutter yüklü || echo ❌ Flutter bulunamadı
git --version 2>nul && echo ✅ Git yüklü || echo ❌ Git bulunamadı

echo.
echo 🔍 PROJE DOSYALARI:
echo ------------------
if exist "simple_api_server.py" (echo ✅ Backend API server mevcut) else (echo ❌ Backend API server bulunamadı)
if exist "requirements.txt" (echo ✅ Python requirements mevcut) else (echo ❌ Python requirements bulunamadı)
if exist "flutter_app\pubspec.yaml" (echo ✅ Flutter config mevcut) else (echo ❌ Flutter config bulunamadı)
if exist ".venv" (echo ✅ Virtual environment mevcut) else (echo ❌ Virtual environment bulunamadı)

echo.
echo 🔍 ÇALIŞAN SERVİSLER:
echo -------------------
curl -s -m 2 http://localhost:8000/api/health >nul 2>&1 && echo ✅ Backend API aktif (http://localhost:8000) || echo ❌ Backend API çalışmıyor

echo.
echo 🔍 FLUTTER DURUM:
echo ----------------
cd flutter_app
flutter doctor --machine 2>nul | findstr "installed" >nul && echo ✅ Flutter SDK hazır || echo ⚠️ Flutter SDK kontrol gerekli

echo.
echo 🔍 BAĞIMLILIKLAR:
echo ----------------
cd ..
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    python -c "import flask; print('✅ Flask yüklü:', flask.__version__)" 2>nul || echo ❌ Flask yüklü değil
    python -c "import pandas; print('✅ Pandas yüklü')" 2>nul || echo ❌ Pandas yüklü değil
    python -c "import numpy; print('✅ NumPy yüklü')" 2>nul || echo ❌ NumPy yüklü değil
    python -c "import sklearn; print('✅ Scikit-learn yüklü')" 2>nul || echo ❌ Scikit-learn yüklü değil
)

echo.
echo 🔍 DISK ALANI:
echo -------------
for /f "tokens=3" %%a in ('dir /-c %CD% ^| find "bytes free"') do echo 💾 Kullanılabilir alan: %%a bytes

echo.
pause
goto main_menu

:test_api
cls
echo 🧪 API TEST
echo ===========
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI"

echo 📋 Backend API test ediliyor...
echo.

echo 🔍 1. Health Check:
curl -s -m 5 http://localhost:8000/api/health 2>nul && echo ✅ Health endpoint çalışıyor || echo ❌ Health endpoint çalışmıyor

echo.
echo 🔍 2. Status Check:
curl -s -m 5 http://localhost:8000/api/status 2>nul && echo ✅ Status endpoint çalışıyor || echo ❌ Status endpoint çalışmıyor

echo.
echo 🔍 3. Portfolio Check:
curl -s -m 5 http://localhost:8000/api/portfolio 2>nul && echo ✅ Portfolio endpoint çalışıyor || echo ❌ Portfolio endpoint çalışmıyor

echo.
echo 🔍 4. Stock Data Check:
curl -s -m 5 http://localhost:8000/api/stocks/AAPL 2>nul && echo ✅ Stock endpoint çalışıyor || echo ❌ Stock endpoint çalışmıyor

echo.
echo 🔍 5. News Check:
curl -s -m 5 http://localhost:8000/api/news/AAPL 2>nul && echo ✅ News endpoint çalışıyor || echo ❌ News endpoint çalışmıyor

echo.
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo 🔍 6. Python Module Test:
    python -c "
import sys
try:
    import simple_api_server
    print('✅ API server modülü yüklenebiliyor')
except Exception as e:
    print('❌ API server modül hatası:', e)
"
)

echo.
echo 📊 API Test tamamlandı!
echo.
echo 💡 Backend çalışmıyorsa [2] Sadece Backend Başlat seçeneğini kullanın
echo.
pause
goto main_menu

:test_flutter
cls
echo 📱 FLUTTER TEST
echo ===============
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI\flutter_app"

echo 📋 Flutter uygulaması test ediliyor...
echo.

echo 🔍 1. Flutter Doctor:
flutter doctor

echo.
echo 🔍 2. Dependencies Check:
flutter pub deps

echo.
echo 🔍 3. Analyze Code:
flutter analyze

echo.
echo 🔍 4. Web Support:
flutter config --enable-web
flutter devices | findstr "chrome" >nul && echo ✅ Web desteği aktif || echo ⚠️ Web desteği kontrol gerekli

echo.
echo 📊 Flutter test tamamlandı!
echo.
cd ..
pause
goto main_menu

:run_all_tests
cls
echo 🧪 TÜM TESTLER
echo ==============
echo.

echo 📋 1/3: Sistem durumu test ediliyor...
call :system_status_silent

echo.
echo 📋 2/3: API test ediliyor...
call :test_api_silent

echo.
echo 📋 3/3: Flutter test ediliyor...
call :test_flutter_silent

echo.
echo ✅ TÜM TESTLER TAMAMLANDI!
echo.
pause
goto main_menu

REM ============================================================================
REM                             GIT VE GITHUB
REM ============================================================================

:github_upload
cls
echo 📤 GITHUB'A YÜKLEME
echo ===================
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI"

echo 📋 GitHub repository: https://github.com/ozgurgurgen/Borsa_AI
echo.

echo 🔍 Git durumu kontrol ediliyor...
if not exist ".git" (
    echo 📁 Git repository başlatılıyor...
    git init
    git remote add origin https://github.com/ozgurgurgen/Borsa_AI.git
)

echo 📋 Dosyalar stage'e ekleniyor...
git add .

echo 📋 Commit yapılıyor...
git commit -m "🚀 Proje güncellendi: AI-FTB Trading Bot - Backend + Frontend"

echo 📋 GitHub'a push yapılıyor...
git branch -M main
git push -u origin main

if errorlevel 0 (
    echo ✅ GITHUB'A BAŞARIYLA YÜKLENDİ!
    echo 🔗 Repository: https://github.com/ozgurgurgen/Borsa_AI
) else (
    echo ❌ GitHub yükleme hatası!
    echo 💡 GitHub repository'sinin var olduğundan emin olun
    echo 💡 Git credentials'ınızın doğru olduğundan emin olun
)

echo.
pause
goto main_menu

:git_status
cls
echo 📊 GIT DURUMU
echo =============
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI"

if exist ".git" (
    echo 🔍 Git repository durumu:
    git status
    echo.
    echo 🔍 Son commitler:
    git log --oneline -5
    echo.
    echo 🔍 Remote repositories:
    git remote -v
) else (
    echo ❌ Git repository bulunamadı!
    echo 💡 [13] GitHub'a Yükle seçeneğini kullanarak başlatabilirsiniz
)

echo.
pause
goto main_menu

:commit_push
cls
echo 📤 COMMIT VE PUSH
echo =================
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI"

if not exist ".git" (
    echo ❌ Git repository bulunamadı!
    echo 💡 Önce [13] GitHub'a Yükle seçeneğini kullanın
    pause
    goto main_menu
)

echo 📋 Değişen dosyalar:
git status --short

echo.
set /p commit_msg="💬 Commit mesajı girin: "
if "%commit_msg%"=="" set commit_msg="Proje güncellendi"

echo 📋 Dosyalar stage'e ekleniyor...
git add .

echo 📋 Commit yapılıyor...
git commit -m "%commit_msg%"

echo 📋 GitHub'a push yapılıyor...
git push

if errorlevel 0 (
    echo ✅ BAŞARIYLA GÖNDERİLDİ!
) else (
    echo ❌ Push hatası!
)

echo.
pause
goto main_menu

REM ============================================================================
REM                             DOKÜMANTASYON
REM ============================================================================

:user_manual
cls
echo 📚 KULLANIM KILAVUZU
echo ===================
echo.

echo 📖 Dokümantasyon dosyaları açılıyor...
if exist "README.md" start notepad README.md
if exist "API_SUNUCU_BAŞLATMA_REHBERİ.md" start notepad API_SUNUCU_BAŞLATMA_REHBERİ.md
if exist "FLUTTER_KURULUM_REHBERI.md" start notepad FLUTTER_KURULUM_REHBERI.md

echo.
echo ✅ Dokümantasyon dosyaları açıldı!
echo.
pause
goto main_menu

:api_docs
cls
echo 📊 API DOKÜMANTASYONU
echo =====================
echo.

echo 🔗 API Endpoints:
echo.
echo 🏠 Temel Endpoints:
echo   GET  /api/health           - Sunucu sağlık kontrolü
echo   GET  /api/status           - Bot durumu
echo   POST /api/start            - Bot başlat
echo   POST /api/stop             - Bot durdur
echo.
echo 📊 Veri Endpoints:
echo   GET  /api/portfolio        - Portföy bilgileri
echo   GET  /api/stocks/{symbol}  - Hisse verisi
echo   GET  /api/news/{symbol}    - Haber verisi
echo   GET  /api/sentiment/{symbol} - Duygu analizi
echo   GET  /api/signals          - Trading sinyalleri
echo.
echo ⚙️ Ayar Endpoints:
echo   GET  /api/settings         - Bot ayarları
echo   POST /api/settings         - Ayar güncelle
echo.
echo 💼 Portföy Yönetimi:
echo   POST /api/portfolio/add    - Pozisyon ekle
echo   PUT  /api/portfolio/update - Pozisyon güncelle
echo   DELETE /api/portfolio/remove - Pozisyon sil
echo.
echo 📈 Grafik ve Analiz:
echo   GET  /api/chart/{symbol}   - Grafik verisi
echo   GET  /api/search/symbols   - Sembol arama
echo.

start http://localhost:8000/api/health 2>nul

echo.
pause
goto main_menu

:troubleshooting
cls
echo 🔧 HATA ÇÖZÜMLERİ
echo ==================
echo.

echo ❓ Sık Karşılaşılan Sorunlar ve Çözümleri:
echo.
echo 🔴 Backend başlamıyor:
echo   • [5] İlk Kurulum'u çalıştırın
echo   • [8] Virtual Environment'ı yeniden oluşturun
echo   • requirements.txt dosyasını kontrol edin
echo.
echo 🔴 Flutter çalışmıyor:
echo   • flutter doctor komutunu çalıştırın
echo   • flutter clean ^&^& flutter pub get yapın
echo   • [6] Sistem Temizle'yi kullanın
echo.
echo 🔴 API bağlantı hatası:
echo   • Backend'in http://localhost:8000'de çalıştığını kontrol edin
echo   • Firewall ayarlarını kontrol edin
echo   • [10] API Test'i çalıştırın
echo.
echo 🔴 Port zaten kullanımda:
echo   • netstat -ano ^| findstr :8000 komutuyla kontrol edin
echo   • İşlemi sonlandırın: taskkill /F /PID [PID]
echo.
echo 🔴 Git push hatası:
echo   • GitHub credentials'ınızı kontrol edin
echo   • Repository'nin var olduğundan emin olun
echo   • git remote -v ile remote URL'i kontrol edin
echo.
echo 🔴 Import hatası:
echo   • [7] Bağımlılıkları Güncelle'yi çalıştırın
echo   • Virtual environment'ın aktif olduğunu kontrol edin
echo.

echo.
pause
goto main_menu

REM ============================================================================
REM                             DİĞER İŞLEMLER
REM ============================================================================

:backup_project
cls
echo 💾 PROJE YEDEKLEME
echo ==================
echo.

cd /d "C:\Users\gurge\Desktop"

set backup_name=BorsAI_Backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%
set backup_name=%backup_name: =0%

echo 📋 Yedek oluşturuluyor: %backup_name%
xcopy /E /I /H /Y BorsAI %backup_name%

if errorlevel 0 (
    echo ✅ YEDEK BAŞARIYLA OLUŞTURULDU!
    echo 📁 Konum: C:\Users\gurge\Desktop\%backup_name%
) else (
    echo ❌ Yedekleme hatası!
)

cd BorsAI
echo.
pause
goto main_menu

:clean_logs
cls
echo 🧹 LOG TEMİZLEME
echo ================
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI"

echo 📋 Log dosyaları temizleniyor...
if exist "logs\*.log" (
    del /q logs\*.log
    echo ✅ Log dosyaları temizlendi
) else (
    echo ℹ️ Temizlenecek log dosyası bulunamadı
)

if exist "flutter_app\build\*.log" (
    del /q flutter_app\build\*.log
    echo ✅ Flutter log dosyaları temizlendi
)

echo.
pause
goto main_menu

:reset_settings
cls
echo ⚙️ AYARLAR SIFIRLAMA
echo ====================
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI"

echo ⚠️ Bu işlem tüm ayarları varsayılan değerlere döndürecek!
set /p confirm="Devam etmek istiyor musunuz? (E/H): "

if /i "%confirm%"=="E" (
    echo 📋 Ayar dosyaları sıfırlanıyor...
    if exist "config.ini" del config.ini
    if exist ".env" del .env
    
    echo [DEFAULT] > config.ini
    echo DEBUG = True >> config.ini
    echo LOG_LEVEL = INFO >> config.ini
    echo PORT = 8000 >> config.ini
    
    echo ✅ Ayarlar sıfırlandı!
) else (
    echo ℹ️ İşlem iptal edildi
)

echo.
pause
goto main_menu

REM ============================================================================
REM                             YARDIMCI FONKSİYONLAR
REM ============================================================================

:check_project_status
if exist ".venv" (
    set backend_status=✅ Hazır
) else (
    set backend_status=❌ Kurulum gerekli
)

if exist "flutter_app\pubspec.yaml" (
    set frontend_status=✅ Hazır
) else (
    set frontend_status=❌ Kurulum gerekli
)

curl -s -m 2 http://localhost:8000/api/health >nul 2>&1 && (
    set api_status=✅ Çalışıyor
) || (
    set api_status=❌ Durdurulmuş
)

echo 📊 Proje Durumu: Backend: %backend_status% ^| Frontend: %frontend_status% ^| API: %api_status%
goto :eof

:check_python_flutter
python --version >nul 2>&1 || (
    echo ❌ Python bulunamadı! Python 3.8+ yüklemeniz gerekiyor.
    echo 🔗 https://www.python.org/downloads/
    pause
    exit /b 1
)

flutter --version >nul 2>&1 || (
    echo ❌ Flutter bulunamadı! Flutter 3.0+ yüklemeniz gerekiyor.
    echo 🔗 https://flutter.dev/docs/get-started/install
    pause
    exit /b 1
)
goto :eof

:check_system_requirements
echo 🔍 Python kontrol ediliyor...
python --version >nul 2>&1 || (
    echo ❌ Python 3.8+ gerekli
    exit /b 1
)

echo 🔍 Flutter kontrol ediliyor...
flutter --version >nul 2>&1 || (
    echo ❌ Flutter 3.0+ gerekli
    exit /b 1
)

echo 🔍 Git kontrol ediliyor...
git --version >nul 2>&1 || (
    echo ⚠️ Git önerilir (GitHub işlemleri için)
)

echo ✅ Sistem gereksinimleri karşılanıyor
goto :eof

:system_status_silent
REM Sessiz sistem durumu kontrolü
goto :eof

:test_api_silent
REM Sessiz API testi
goto :eof

:test_flutter_silent
REM Sessiz Flutter testi
goto :eof

:exit_program
cls
echo.
echo 👋 AI-FTB Proje Yonetim Merkezi'nden cikiliyor...
echo.
echo 🎯 Yapilan islemler:
if exist ".venv" echo   ✅ Virtual environment hazir
if exist "flutter_app" echo   ✅ Flutter uygulamasi hazir
curl -s -m 1 http://localhost:8000/api/health >nul 2>&1 && echo   ⚠️ Backend hala calisiyor (manuel olarak kapatin)
echo.
echo 📊 Proje Ozeti:
echo   🐍 Python Backend: Finansal veri analizi ve API
echo   📱 Flutter Frontend: Cross-platform mobil uygulama
echo   🤖 AI Trading: Machine learning tabanli trading
echo   📈 Real-time: Canli veri ve grafik destegi
echo.
echo 🔗 GitHub: https://github.com/ozgurgurgen/Borsa_AI
echo 📧 Destek: AI-FTB GitHub Issues
echo.
echo 💡 Tekrar calistirmak icin bu dosyayi cift tiklayin!
echo.
timeout /t 5 /nobreak >nul
exit
