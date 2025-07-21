@echo off
chcp 65001 >nul
title GitHub Upload Script
color 0A

echo.
echo 🚀 AI-FTB Projesini GitHub'a Yukleme
echo =====================================
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI"

echo 📁 Git repository baslatiliyor...
git init
if errorlevel 1 (
    echo ❌ Git init hatasi!
    pause
    exit /b 1
)

echo.
echo 🔗 GitHub repository baglantisi ekleniyor...
git remote add origin https://github.com/ozgurgurgen/Borsa_AI.git
if errorlevel 1 (
    echo ⚠️ Remote zaten mevcut olabilir, devam ediliyor...
)

echo.
echo 📂 Dosyalar stage'e ekleniyor...
git add .
if errorlevel 1 (
    echo ❌ Git add hatasi!
    pause
    exit /b 1
)

echo.
echo 💾 Ilk commit yapiliyor...
git commit -m "🎉 Ilk commit: AI-FTB Trading Bot - Python Backend + Flutter Frontend ile yapay zeka destekli finansal ticaret botu"
if errorlevel 1 (
    echo ❌ Commit hatasi!
    pause
    exit /b 1
)

echo.
echo ⬆️ GitHub'a yukleniyor...
git branch -M main
git push -u origin main
if errorlevel 1 (
    echo ❌ Push hatasi! GitHub repository'sinin olusturuldugu emin olun.
    echo 🔗 Repository: https://github.com/ozgurgurgen/Borsa_AI
    pause
    exit /b 1
)

echo.
echo ✅ Proje basarıyla GitHub'a yuklendi!
echo 🔗 Repository: https://github.com/ozgurgurgen/Borsa_AI
echo.
echo 📊 Yuklenen dosyalar:
echo - Python backend (API sunucusu)
echo - Flutter frontend (mobil uygulama)
echo - Machine learning modeli
echo - Dokumantasyon
echo - Konfigurasyon dosyalari
echo.
pause
