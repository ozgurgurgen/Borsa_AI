@echo off
chcp 65001 >nul
title Flutter App - Temiz Baslatma
color 0B

echo 📱 Flutter Uygulamasi - Temiz Baslatma
echo ========================================
echo.

cd /d "C:\Users\gurge\Desktop\BorsAI\flutter_app"

echo 🧹 1/5: Flutter cache temizleniyor...
flutter clean

echo 📦 2/5: Bagimliliklar yukleniyor...
flutter pub get

echo 🔧 3/5: Flutter doctor kontrolu...
flutter doctor

echo 🌐 4/5: Web destegi aktif ediliyor...
flutter config --enable-web

echo 🚀 5/5: Edge'de baslatiliyor...
flutter run -d edge

echo.
echo ✅ Flutter uygulamasi baslatildi!
pause
