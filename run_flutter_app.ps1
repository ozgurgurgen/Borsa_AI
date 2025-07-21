# =================================
# AI-FTB Flutter Uygulaması Başlat
# =================================

Write-Host "=================================" -ForegroundColor Cyan
Write-Host "AI-FTB Flutter Uygulamasi Baslat" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Python backend'i kontrol et
Write-Host "1. Backend kontrol ediliyor..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "✅ Backend hazir (http://localhost:8000)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend calisimiyor! Once api_server.py'yi calistirin:" -ForegroundColor Red
    Write-Host "   python api_server.py" -ForegroundColor White
    Write-Host ""
    Read-Host "Devam etmek icin Enter'a basin"
    exit 1
}

Write-Host ""

# Flutter dizinine git
Set-Location "flutter_app"

# Flutter kurulumunu kontrol et
Write-Host "2. Flutter kontrol ediliyor..." -ForegroundColor Yellow

try {
    $flutterVersion = flutter --version 2>$null
    Write-Host "✅ Flutter hazir" -ForegroundColor Green
} catch {
    Write-Host "❌ Flutter bulunamadi! Flutter SDK'yi kurun." -ForegroundColor Red
    Write-Host "   https://flutter.dev/docs/get-started/install" -ForegroundColor White
    Read-Host "Devam etmek icin Enter'a basin"
    exit 1
}

Write-Host ""

# Dependencies yükle
Write-Host "3. Dependencies yukleniyor..." -ForegroundColor Yellow

try {
    flutter pub get
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies yuklendi" -ForegroundColor Green
    } else {
        throw "Dependencies yuklenemedi"
    }
} catch {
    Write-Host "❌ Dependencies yuklenemedi!" -ForegroundColor Red
    Read-Host "Devam etmek icin Enter'a basin"
    exit 1
}

Write-Host ""

# Uygulamayı başlat
Write-Host "4. Uygulama baslatiliyor..." -ForegroundColor Yellow
Write-Host ""
Write-Host "📱 AI-FTB mobil uygulamasi baslatiliyor..." -ForegroundColor Cyan
Write-Host "🔗 Backend: http://localhost:8000" -ForegroundColor White
Write-Host ""

flutter run

Write-Host ""
Write-Host "Uygulama kapatildi." -ForegroundColor Yellow
Read-Host "Devam etmek icin Enter'a basin"
