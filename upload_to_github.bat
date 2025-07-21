@echo off
title GitHub Upload Script
color 0A

echo.
echo 🚀 AI-FTB Projesini GitHub'a Yükleme
echo =====================================
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI"

echo 📁 Git repository başlatılıyor...
git init
if errorlevel 1 (
    echo ❌ Git init hatası!
    pause
    exit /b 1
)

echo.
echo 🔗 GitHub repository bağlantısı ekleniyor...
git remote add origin https://github.com/ozgurgurgen/Borsa_AI.git
if errorlevel 1 (
    echo ⚠️ Remote zaten mevcut olabilir, devam ediliyor...
)

echo.
echo 📂 Dosyalar stage'e ekleniyor...
git add .
if errorlevel 1 (
    echo ❌ Git add hatası!
    pause
    exit /b 1
)

echo.
echo 💾 İlk commit yapılıyor...
git commit -m "🎉 İlk commit: AI-FTB Trading Bot - Python Backend + Flutter Frontend ile yapay zeka destekli finansal ticaret botu"
if errorlevel 1 (
    echo ❌ Commit hatası!
    pause
    exit /b 1
)

echo.
echo ⬆️ GitHub'a yükleniyor...
git branch -M main
git push -u origin main
if errorlevel 1 (
    echo ❌ Push hatası! GitHub repository'sinin oluşturulduğundan emin olun.
    echo 🔗 Repository: https://github.com/ozgurgurgen/Borsa_AI
    pause
    exit /b 1
)

echo.
echo ✅ Proje başarıyla GitHub'a yüklendi!
echo 🔗 Repository: https://github.com/ozgurgurgen/Borsa_AI
echo.
echo 📊 Yüklenen dosyalar:
echo - Python backend (API sunucusu)
echo - Flutter frontend (mobil uygulama)
echo - Machine learning modeli
echo - Dokümantasyon
echo - Konfigürasyon dosyaları
echo.
pause
