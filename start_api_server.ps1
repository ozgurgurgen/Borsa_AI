# AI-FTB API Sunucusu Başlatıcısı
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI-FTB API Sunucusu Başlatılıyor..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectPath = "c:\Users\gurge\Desktop\BorsAI"
Set-Location $projectPath
Write-Host "📁 Dizin: $projectPath" -ForegroundColor Green
Write-Host ""

Write-Host "🐍 Python Virtual Environment aktif ediliyor..." -ForegroundColor Yellow
$env:PATH = "$projectPath\.venv\Scripts;$env:PATH"
Write-Host ""

Write-Host "📦 Flask kontrol ediliyor..." -ForegroundColor Yellow
try {
    & "$projectPath\.venv\Scripts\python.exe" -c "import flask; print('✅ Flask yüklü')"
} catch {
    Write-Host "❌ Flask yüklü değil, yükleniyor..." -ForegroundColor Red
    & "$projectPath\.venv\Scripts\pip.exe" install flask flask-cors
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 API Sunucusu başlatılıyor..." -ForegroundColor Green
Write-Host "📡 URL: http://localhost:8000" -ForegroundColor Blue
Write-Host "🔗 Health: http://localhost:8000/api/health" -ForegroundColor Blue
Write-Host "🌐 Flutter'da kullanım için hazır!" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    & "$projectPath\.venv\Scripts\python.exe" "$projectPath\simple_api_server.py"
} catch {
    Write-Host "❌ API Sunucusu başlatılamadı: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "API Sunucusu durduruldu." -ForegroundColor Yellow
Read-Host "Devam etmek için Enter'a basın"
