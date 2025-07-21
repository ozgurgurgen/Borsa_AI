@echo off
chcp 65001 >nul
title AI-FTB API Sunucusu
echo ========================================
echo AI-FTB API Sunucusu Baslatiliyor...
echo ========================================
echo.

cd /d "c:\Users\gurge\Desktop\BorsAI"
echo Dizin: %CD%
echo.

echo Virtual environment aktif ediliyor...
call .venv\Scripts\activate.bat
echo.

echo Flask kontrol ediliyor...
python -c "import flask; print('✅ Flask yuklu')" 2>nul || (
    echo ❌ Flask yuklu degil, yukleniyor...
    pip install flask flask-cors
)
echo.

echo ========================================
echo 🚀 API Sunucusu baslatiliyor...
echo 📡 URL: http://localhost:8000
echo 🔗 Health: http://localhost:8000/api/health
echo ========================================
echo.

python simple_api_server.py

echo.
echo API Sunucusu durduruldu.
pause
