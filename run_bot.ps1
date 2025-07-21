#!/usr/bin/env pwsh

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "AI-FTB Kurulum ve Çalıştırma Scripti" -ForegroundColor Cyan  
Write-Host "============================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "1. Python versiyonu kontrol ediliyor..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ HATA: Python yüklü değil veya PATH'te tanımlı değil!" -ForegroundColor Red
    Write-Host "Lütfen Python 3.9+ yükleyip PATH'e ekleyin." -ForegroundColor Red
    Read-Host "Devam etmek için Enter'a basın"
    exit 1
}

Write-Host ""
Write-Host "2. Gerekli paketler yükleniyor..." -ForegroundColor Yellow

try {
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    Write-Host "✅ Paketler başarıyla yüklendi" -ForegroundColor Green
} catch {
    Write-Host "❌ HATA: Paket yükleme başarısız!" -ForegroundColor Red
    Write-Host "İnternet bağlantınızı kontrol edin." -ForegroundColor Red
    Read-Host "Devam etmek için Enter'a basın"
    exit 1
}

Write-Host ""
Write-Host "3. NLTK verileri indiriliyor..." -ForegroundColor Yellow

try {
    python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); print('✅ NLTK verileri indirildi')"
} catch {
    Write-Host "⚠️  NLTK verileri indirilemedi (opsiyonel)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "4. Kurulum testi yapılıyor..." -ForegroundColor Yellow

try {
    python test_installation.py
    Write-Host "✅ Kurulum testi başarılı" -ForegroundColor Green
} catch {
    Write-Host "❌ HATA: Kurulum testi başarısız!" -ForegroundColor Red
    Write-Host "Lütfen hataları düzeltin." -ForegroundColor Red
    Read-Host "Devam etmek için Enter'a basın"
    exit 1
}

Write-Host ""
Write-Host "5. Ana program başlatılıyor..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Mevcut seçenekler:" -ForegroundColor Cyan
Write-Host "  1. Model eğitimi ve backtest (varsayılan)" -ForegroundColor White
Write-Host "  2. AAPL analizi" -ForegroundColor White
Write-Host "  3. Test modu" -ForegroundColor White
Write-Host "  4. Özel sembol analizi" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Seçiminizi yapın (1-4, Enter=1)"

switch ($choice) {
    "2" {
        Write-Host "AAPL analizi yapılıyor..." -ForegroundColor Green
        python main.py analysis AAPL
    }
    "3" {
        Write-Host "Test modu çalıştırılıyor..." -ForegroundColor Green
        python main.py test
    }
    "4" {
        $symbol = Read-Host "Analiz edilecek sembolü girin (örn: MSFT)"
        Write-Host "$symbol analizi yapılıyor..." -ForegroundColor Green
        python main.py analysis $symbol
    }
    default {
        Write-Host "Model eğitimi ve backtest çalıştırılıyor..." -ForegroundColor Green
        python main.py training
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Program tamamlandı!" -ForegroundColor Green
Write-Host "Log dosyaları: logs\bot_activity.log" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

Read-Host "Çıkmak için Enter'a basın"
