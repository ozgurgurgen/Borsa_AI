@echo off
echo ============================================
echo AI-FTB Kurulum ve Calistirma Scripti
echo ============================================

echo.
echo 1. Python versiyonu kontrol ediliyor...
python --version
if errorlevel 1 (
    echo HATA: Python yuklu degil veya PATH'te tanimli degil!
    echo Lutfen Python 3.9+ yukleyip PATH'e ekleyin.
    pause
    exit /b 1
)

echo.
echo 2. Gerekli paketler yukleniyor...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo HATA: Paket yukleme basarisiz!
    echo Internet baglantinizi kontrol edin.
    pause
    exit /b 1
)

echo.
echo 3. NLTK verileri indiriliyor...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); print('NLTK verileri indirildi')"

echo.
echo 4. Kurulum testi yapiliyor...
python test_installation.py

if errorlevel 1 (
    echo HATA: Kurulum testi basarisiz!
    echo Lutfen hatalari duzeltin.
    pause
    exit /b 1
)

echo.
echo 5. Ana program baslatiliyor...
echo.
echo Mevcut seçenekler:
echo   1. Model egitimi ve backtest (varsayilan)
echo   2. AAPL analizi
echo   3. Test modu
echo.
choice /c 123 /m "Seciminizi yapin (1-3)"

if errorlevel 3 (
    echo Test modu calistiriliyor...
    python main.py test
) else if errorlevel 2 (
    echo AAPL analizi yapiliyor...
    python main.py analysis AAPL
) else (
    echo Model egitimi ve backtest calistiriliyor...
    python main.py training
)

echo.
echo ============================================
echo Program tamamlandi!
echo Log dosyalari: logs\bot_activity.log
echo ============================================
pause
