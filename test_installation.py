"""
AI-FTB Kurulum ve Test Scripti

Bu script projenin doğru kurulduğunu ve temel fonksiyonlarının çalıştığını test eder.
"""

import sys
import os
import importlib

def test_python_version():
    """Python versiyonunu kontrol et"""
    print("🐍 Python Versiyonu Kontrolü:")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("   ❌ Python 3.9+ gereklidir!")
        return False
    else:
        print("   ✅ Python versiyonu uygun")
        return True

def test_required_packages():
    """Gerekli paketlerin yüklü olup olmadığını kontrol et"""
    print("\n📦 Paket Kontrolü:")
    
    required_packages = {
        'pandas': 'pandas',
        'numpy': 'numpy', 
        'sklearn': 'scikit-learn',
        'yfinance': 'yfinance',
        'textblob': 'textblob',
        'requests': 'requests',
        'joblib': 'joblib'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        try:
            importlib.import_module(package)
            print(f"   ✅ {pip_name}")
        except ImportError:
            print(f"   ❌ {pip_name} - Eksik!")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\n   Eksik paketleri yüklemek için:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    else:
        print("   ✅ Tüm gerekli paketler yüklü")
        return True

def test_project_structure():
    """Proje dosyalarının varlığını kontrol et"""
    print("\n📁 Proje Yapısı Kontrolü:")
    
    required_files = [
        'config.py',
        'logger.py', 
        'data_handler.py',
        'feature_engineer.py',
        'news_sentiment_analyzer.py',
        'ml_model.py',
        'strategy_executor.py',
        'backtester.py',
        'main.py',
        'requirements.txt'
    ]
    
    required_dirs = ['logs', 'data', 'models']
    
    missing_files = []
    
    # Dosya kontrolü
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - Eksik!")
            missing_files.append(file)
    
    # Dizin kontrolü
    for dir in required_dirs:
        if os.path.exists(dir):
            print(f"   ✅ {dir}/")
        else:
            print(f"   ❌ {dir}/ - Eksik!")
            os.makedirs(dir, exist_ok=True)
            print(f"   ℹ️  {dir}/ oluşturuldu")
    
    if missing_files:
        return False
    else:
        print("   ✅ Tüm proje dosyaları mevcut")
        return True

def test_module_imports():
    """Proje modüllerinin import edilebilirliğini test et"""
    print("\n🔧 Modül Import Testi:")
    
    modules = [
        'config',
        'logger',
        'data_handler',
        'feature_engineer', 
        'news_sentiment_analyzer',
        'ml_model',
        'strategy_executor',
        'backtester'
    ]
    
    import_errors = []
    
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"   ✅ {module}")
        except Exception as e:
            print(f"   ❌ {module} - Hata: {str(e)[:50]}...")
            import_errors.append(module)
    
    if import_errors:
        return False
    else:
        print("   ✅ Tüm modüller başarıyla import edildi")
        return True

def test_basic_functionality():
    """Temel fonksiyonaliteyi test et"""
    print("\n⚡ Temel Fonksiyon Testi:")
    
    try:
        # Config testi
        import config
        assert len(config.SYMBOLS) > 0, "SYMBOLS listesi boş"
        assert config.RISK_PER_TRADE_PERCENT > 0, "Risk yüzdesi geçersiz"
        print("   ✅ Config modülü")
        
        # Logger testi
        import logger
        logger.log_info("Test log mesajı")
        print("   ✅ Logger modülü")
        
        # Data handler testi (network gerektirmez)
        import data_handler
        print("   ✅ Data handler modülü")
        
        # Feature engineer testi
        import feature_engineer
        print("   ✅ Feature engineer modülü")
        
        print("   ✅ Temel fonksiyonlar çalışıyor")
        return True
        
    except Exception as e:
        print(f"   ❌ Temel fonksiyon hatası: {e}")
        return False

def run_simple_demo():
    """Basit demo çalıştır"""
    print("\n🚀 Basit Demo:")
    
    try:
        import numpy as np
        import pandas as pd
        from datetime import datetime, timedelta
        
        # Basit veri oluştur
        dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
        data = pd.DataFrame({
            'Close': [100 + i + np.random.randn() for i in range(len(dates))],
            'Volume': [1000000 + np.random.randint(-100000, 100000) for _ in range(len(dates))]
        }, index=dates)
        
        print(f"   ✅ Test verisi oluşturuldu: {len(data)} satır")
        
        # Feature engineer test
        import feature_engineer
        
        # Basit SMA hesaplama
        data['SMA_5'] = data['Close'].rolling(5).mean()
        print("   ✅ Basit teknik gösterge hesaplandı")
        
        # TextBlob test
        from textblob import TextBlob
        test_text = "The stock market is performing well today"
        sentiment = TextBlob(test_text).sentiment.polarity
        print(f"   ✅ Duygu analizi testi: {sentiment:.3f}")
        
        print("   ✅ Demo başarıyla tamamlandı!")
        return True
        
    except Exception as e:
        print(f"   ❌ Demo hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("=" * 60)
    print("🤖 AI-FTB KURULUM VE TEST SCRİPTİ")
    print("=" * 60)
    
    all_tests_passed = True
    
    # Test sırası
    tests = [
        ("Python Versiyonu", test_python_version),
        ("Gerekli Paketler", test_required_packages),
        ("Proje Yapısı", test_project_structure),
        ("Modül Import", test_module_imports),
        ("Temel Fonksiyonlar", test_basic_functionality),
        ("Basit Demo", run_simple_demo)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if not result:
                all_tests_passed = False
        except Exception as e:
            print(f"\n❌ {test_name} testi sırasında hata: {e}")
            all_tests_passed = False
    
    # Sonuç
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 TÜM TESTLER BAŞARILI!")
        print("\nProje kullanıma hazır. Başlamak için:")
        print("   python main.py")
        print("   veya")
        print("   python main.py analysis AAPL")
    else:
        print("❌ BAZI TESTLER BAŞARISIZ!")
        print("\nLütfen yukarıdaki hataları düzeltip tekrar deneyin.")
        print("Yardım için README.md dosyasını inceleyin.")
    
    print("=" * 60)
    
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
