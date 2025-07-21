@echo off
echo =================================
echo AI-FTB Flutter Uygulamasi Baslat
echo =================================
echo.

REM Python backend'i kontrol et
echo 1. Backend kontrol ediliyor...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Backend calisimiyor! Once api_server.py'yi calistirin:
    echo    python api_server.py
    echo.
    pause
    exit /b 1
)

echo ✅ Backend hazir (http://localhost:8000)
echo.

REM Flutter dizinine git
cd flutter_app

REM Flutter kurulumunu kontrol et
echo 2. Flutter kontrol ediliyor...
flutter --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Flutter bulunamadi! Flutter SDK'yi kurun.
    echo    https://flutter.dev/docs/get-started/install
    pause
    exit /b 1
)

echo ✅ Flutter hazir
echo.

REM Dependencies yükle
echo 3. Dependencies yukleniyor...
flutter pub get
if %errorlevel% neq 0 (
    echo ❌ Dependencies yuklenemedi!
    pause
    exit /b 1
)

echo ✅ Dependencies yuklendi
echo.

REM Uygulamayı başlat
echo 4. Uygulama baslatiliyor...
echo.
echo 📱 AI-FTB mobil uygulamasi baslatiliyor...
echo 🔗 Backend: http://localhost:8000
echo.

flutter run

echo.
echo Uygulama kapatildi.
pause
