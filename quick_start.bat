@echo off
chcp 65001 >nul
title AI-FTB Hızlı Başlatma
color 0E

echo 🚀 AI-FTB Hızlı Başlatma
echo ========================
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI"

echo 🐍 Backend baslatiliyor...
start "AI-FTB Backend" cmd /k "python simple_api_server.py"

echo 📱 Flutter hazirlaniyor...
cd flutter_app
timeout /t 3 /nobreak >nul

echo 🌐 Flutter Edge'de baslatiliyor...
start "AI-FTB Flutter" cmd /k "flutter run -d edge"

echo.
echo ✅ Iki pencere acildi:
echo    1. Backend API Server (localhost:8000)
echo    2. Flutter App (Edge tarayicisinda)
echo.
echo 💡 Her iki pencereyi acik tutun!
echo.
pause
