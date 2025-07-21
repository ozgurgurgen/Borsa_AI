@echo off
title AI-FTB Proje Başlatma
color 0A
cls

echo.
echo ███████╗██╗      █████╗ ██╗      ███████╗████████╗██╗██╗     
echo ██╔════╝██║     ██╔══██╗██║      ██╔════╝╚══██╔══╝██║██║     
echo █████╗  ██║     ███████║██║█████╗█████╗     ██║   ██║██║     
echo ██╔══╝  ██║     ██╔══██║██║╚════╝██╔══╝     ██║   ██║██║     
echo ██║     ███████╗██║  ██║██║      ██║        ██║   ██║███████╗
echo ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝      ╚═╝        ╚═╝   ╚═╝╚══════╝
echo.
echo 🤖 AI-FTB: AI-Powered Financial Trading Bot
echo 📊 Python Backend + Flutter Frontend
echo.
echo ========================================
echo         PROJE BAŞLATMA MENÜSÜ
echo ========================================
echo.
echo [1] 🔥 Tam Proje Başlat (Backend + Frontend)
echo [2] 🐍 Sadece Backend API Başlat
echo [3] 📱 Sadece Flutter Uygulaması Başlat
echo [4] 🔧 Sistem Kontrolü
echo [5] 📚 Dokümantasyon Görüntüle
echo [6] 🚪 Çıkış
echo.
set /p choice="Seçiminizi yapın (1-6): "

if "%choice%"=="1" goto full_start
if "%choice%"=="2" goto backend_only
if "%choice%"=="3" goto frontend_only
if "%choice%"=="4" goto system_check
if "%choice%"=="5" goto documentation
if "%choice%"=="6" goto exit
goto menu

:full_start
echo.
echo 🔥 TAM PROJE BAŞLATILIYOR...
echo ========================================
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI"

echo 📝 1/4: Sistem kontrolleri...
call :check_python
call :check_flutter
call :check_dependencies

echo.
echo 🐍 2/4: Backend API sunucusu başlatılıyor...
start "AI-FTB Backend" cmd /k "call start_api_server.bat"

echo 📱 3/4: Flutter uygulaması hazırlanıyor...
timeout /t 5 /nobreak >nul
cd flutter_app
start "AI-FTB Frontend" cmd /k "flutter run -d edge"

echo 🌐 4/4: Tarayıcılar açılıyor...
timeout /t 10 /nobreak >nul
start http://localhost:8000/api/health
start http://localhost:8000

echo.
echo ✅ TÜM SİSTEMLER AKTİF!
echo.
echo 📊 Backend API: http://localhost:8000
echo 📱 Flutter App: Edge'de açılacak
echo 🔧 API Health: http://localhost:8000/api/health
echo.
echo 💡 Her iki pencereyi açık tutun!
echo ❌ Kapatmak için pencereleri kapatın
echo.
pause
goto menu

:backend_only
echo.
echo 🐍 BACKEND API SUNUCUSU BAŞLATILIYOR...
echo ========================================
cd /d "C:\Users\gurge\Desktop\BorsAI"
call start_api_server.bat
goto menu

:frontend_only
echo.
echo 📱 FLUTTER UYGULAMASI BAŞLATILIYOR...
echo ========================================
cd /d "C:\Users\gurge\Desktop\BorsAI\flutter_app"

echo Bağımlılıklar kontrol ediliyor...
flutter pub get

echo Flutter uygulaması Edge'de başlatılıyor...
flutter run -d edge
goto menu

:system_check
echo.
echo 🔧 SİSTEM KONTROLÜ
echo ========================================
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI"

echo 📊 Python Kontrolü:
python --version 2>nul && echo ✅ Python yüklü || echo ❌ Python bulunamadı

echo.
echo 📊 Flutter Kontrolü:
flutter --version 2>nul && echo ✅ Flutter yüklü || echo ❌ Flutter bulunamadı

echo.
echo 📊 Virtual Environment:
if exist ".venv" (echo ✅ Virtual environment mevcut) else (echo ❌ Virtual environment bulunamadı)

echo.
echo 📊 API Sunucu Durumu:
curl -s http://localhost:8000/health >nul 2>&1 && echo ✅ Backend aktif || echo ❌ Backend çalışmıyor

echo.
echo 📊 Flutter App Dizini:
if exist "flutter_app" (echo ✅ Flutter app mevcut) else (echo ❌ Flutter app bulunamadı)

echo.
echo 📊 Gerekli Dosyalar:
if exist "simple_api_server.py" (echo ✅ API server mevcut) else (echo ❌ API server bulunamadı)
if exist "requirements.txt" (echo ✅ Requirements mevcut) else (echo ❌ Requirements bulunamadı)
if exist "flutter_app\pubspec.yaml" (echo ✅ Flutter config mevcut) else (echo ❌ Flutter config bulunamadı)

echo.
pause
goto menu

:documentation
echo.
echo 📚 DOKÜMANTASYON
echo ========================================
echo.
echo 📖 README.md dosyasını görüntülüyor...
start notepad README.md
echo.
echo 📖 API Dokümantasyonu:
start notepad API_SUNUCU_BAŞLATMA_REHBERİ.md
echo.
echo 📖 Flutter Rehberi:
start notepad FLUTTER_KURULUM_REHBERI.md
echo.
pause
goto menu

:check_python
python --version >nul 2>&1 || (
    echo ❌ Python bulunamadı! Python 3.8+ gerekli.
    pause
    exit /b 1
)
echo ✅ Python mevcut

:check_flutter
flutter --version >nul 2>&1 || (
    echo ❌ Flutter bulunamadı! Flutter 3.0+ gerekli.
    pause
    exit /b 1
)
echo ✅ Flutter mevcut

:check_dependencies
if not exist ".venv" (
    echo ⚠️ Virtual environment bulunamadı, oluşturuluyor...
    python -m venv .venv
)
echo ✅ Virtual environment hazır

:exit
echo.
echo 👋 AI-FTB'den çıkılıyor...
echo Teşekkürler!
timeout /t 2 /nobreak >nul
exit

:menu
echo.
goto :eof
