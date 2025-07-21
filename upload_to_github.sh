#!/bin/bash

echo "🚀 Projeyi GitHub'a yükleme scripti"
echo "=================================="

# Git repository başlat
echo "📁 Git repository başlatılıyor..."
git init

# Remote repository ekle
echo "🔗 GitHub repository bağlantısı ekleniyor..."
git remote add origin https://github.com/ozgurgurgen/Borsa_AI.git

# Tüm dosyaları stage'e ekle
echo "📂 Dosyalar stage'e ekleniyor..."
git add .

# İlk commit
echo "💾 İlk commit yapılıyor..."
git commit -m "🎉 İlk commit: AI-FTB Trading Bot

✨ Özellikler:
- Python backend API sunucusu
- Flutter mobil uygulama
- Machine learning modeli
- Duygu analizi
- Risk yönetimi
- Gerçek zamanlı veri entegrasyonu
- Türk ve ABD hisse senetleri desteği

🛠️ Teknolojiler:
- Python 3.8+
- Flutter 3.0+
- Flask API
- scikit-learn
- TextBlob
- Yahoo Finance API

📱 Platform desteği:
- Web (Flutter Web)
- Android
- iOS
- Desktop"

# GitHub'a push
echo "⬆️ GitHub'a yükleniyor..."
git branch -M main
git push -u origin main

echo "✅ Proje başarıyla GitHub'a yüklendi!"
echo "🔗 Repository: https://github.com/ozgurgurgen/Borsa_AI"
