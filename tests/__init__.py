"""
AI-FTB Test Suite
Bu dosya pytest için boş bırakılmıştır.
"""

# Test discovery için boş dosya

def pytest_configure(config):
    """Pytest konfigürasyonu"""
    pass

def pytest_sessionstart(session):
    """Test session başladığında çalışır"""
    print("\n" + "="*50)
    print("🧪 AI-FTB Test Suite Başlatılıyor")
    print("="*50)

def pytest_sessionfinish(session, exitstatus):
    """Test session bittiğinde çalışır"""
    print("\n" + "="*50)
    if exitstatus == 0:
        print("✅ Tüm testler başarıyla tamamlandı!")
    else:
        print("❌ Bazı testler başarısız oldu!")
    print("="*50)
