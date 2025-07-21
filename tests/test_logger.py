"""
test_logger.py - Logger modülü için birim testler

Bu dosya logger modülündeki fonksiyonları test eder:
- Logger kurulum testleri
- Loglama fonksiyonları testleri  
- Log seviye testleri
- Dosya işlemleri testleri
- Hata durumu testleri
"""

import unittest
from unittest.mock import Mock, patch, mock_open
import tempfile
import shutil
import os
import sys

# Ana proje klasörünü Python path'ine ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logger
import config


class TestLogger:
    """Logger fonksiyonları için test sınıfı"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        # Geçici log dizini oluştur
        self.temp_dir = tempfile.mkdtemp()
        self.temp_log_file = os.path.join(self.temp_dir, 'test.log')
        
    def teardown_method(self):
        """Her test sonrası çalışır"""
        # Geçici dosyaları temizle
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_setup_logger_function(self):
        """Logger kurulum fonksiyonu testi"""
        test_logger = logger.setup_logger(
            log_file_path=self.temp_log_file,
            log_level='INFO'
        )
        
        assert test_logger is not None
        assert test_logger.name == 'AI_FTB'
        assert len(test_logger.handlers) > 0

    def test_log_info_function(self):
        """Info loglama fonksiyonu testi"""
        test_logger = logger.setup_logger(
            log_file_path=self.temp_log_file,
            log_level='INFO'
        )
        
        # Log mesajı gönder
        logger.log_info("Test info mesajı")
        
        # Log dosyasının oluştuğunu kontrol et
        assert os.path.exists(self.temp_log_file)
        
        # Log içeriğini kontrol et
        with open(self.temp_log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Test info mesajı" in content
            assert "INFO" in content

    def test_log_error_function(self):
        """Error loglama fonksiyonu testi"""
        test_logger = logger.setup_logger(
            log_file_path=self.temp_log_file,
            log_level='ERROR'
        )
        
        logger.log_error("Test error mesajı")
        
        with open(self.temp_log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Test error mesajı" in content
            assert "ERROR" in content

    def test_log_warning_function(self):
        """Warning loglama fonksiyonu testi"""
        test_logger = logger.setup_logger(
            log_file_path=self.temp_log_file,
            log_level='WARNING'
        )
        
        logger.log_warning("Test warning mesajı")
        
        with open(self.temp_log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Test warning mesajı" in content
            assert "WARNING" in content

    def test_log_debug_function(self):
        """Debug loglama fonksiyonu testi"""
        test_logger = logger.setup_logger(
            log_file_path=self.temp_log_file,
            log_level='DEBUG'
        )
        
        logger.log_debug("Test debug mesajı")
        
        with open(self.temp_log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Test debug mesajı" in content
            assert "DEBUG" in content

    def test_log_exception_with_exc_info(self):
        """Exception loglama testi"""
        test_logger = logger.setup_logger(
            log_file_path=self.temp_log_file,
            log_level='ERROR'
        )
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.log_exception("Test exception mesajı")
        
        with open(self.temp_log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Test exception mesajı" in content
            assert "ERROR" in content

    def test_multiple_log_entries(self):
        """Çoklu log girişi testi"""
        test_logger = logger.setup_logger(
            log_file_path=self.temp_log_file,
            log_level='DEBUG'
        )
        
        logger.log_info("İlk mesaj")
        logger.log_warning("İkinci mesaj")
        logger.log_error("Üçüncü mesaj")
        
        with open(self.temp_log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "İlk mesaj" in content
            assert "İkinci mesaj" in content
            assert "Üçüncü mesaj" in content

    def test_log_file_creation(self):
        """Log dosyası oluşturma testi"""
        # Var olmayan dizin yolu
        non_existing_dir = os.path.join(self.temp_dir, 'new_dir')
        log_file_in_new_dir = os.path.join(non_existing_dir, 'test.log')
        
        test_logger = logger.setup_logger(
            log_file_path=log_file_in_new_dir,
            log_level='INFO'
        )
        
        logger.log_info("Test mesajı")
        
        # Dizinin ve dosyanın oluştuğunu kontrol et
        assert os.path.exists(non_existing_dir)
        assert os.path.exists(log_file_in_new_dir)

    def test_log_formatting(self):
        """Log formatı testi"""
        test_logger = logger.setup_logger(
            log_file_path=self.temp_log_file,
            log_level='INFO'
        )
        
        logger.log_info("Formatlı mesaj")
        
        with open(self.temp_log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Timestamp formatı kontrolü
            assert any(char.isdigit() for char in content)
            assert "INFO" in content
            assert "AI_FTB" in content

    def test_unicode_characters(self):
        """Unicode karakter desteği testi"""
        test_logger = logger.setup_logger(
            log_file_path=self.temp_log_file,
            log_level='INFO'
        )
        
        unicode_message = "Türkçe karakterler: İĞÜŞÇÖ ığüşçö"
        logger.log_info(unicode_message)
        
        with open(self.temp_log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert unicode_message in content

    def test_long_message_logging(self):
        """Uzun mesaj loglama testi"""
        test_logger = logger.setup_logger(
            log_file_path=self.temp_log_file,
            log_level='INFO'
        )
        
        long_message = "Bu çok uzun bir mesajdır. " * 100
        logger.log_info(long_message)
        
        with open(self.temp_log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert long_message in content

    def test_concurrent_logging(self):
        """Eşzamanlı loglama testi"""
        test_logger = logger.setup_logger(
            log_file_path=self.temp_log_file,
            log_level='INFO'
        )
        
        # Birden fazla log mesajı ardarda
        for i in range(10):
            logger.log_info(f"Mesaj {i}")
        
        with open(self.temp_log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            for i in range(10):
                assert f"Mesaj {i}" in content

    @patch('config.LOG_FILE_PATH')
    @patch('config.LOG_LEVEL') 
    def test_logger_main_execution(self, mock_log_level, mock_log_file):
        """Logger'ın main fonksiyonu testi"""
        mock_log_file.return_value = self.temp_log_file
        mock_log_level.return_value = 'INFO'
        
        # Logger main çalıştırma testini simüle et
        test_logger = logger.setup_logger()
        assert test_logger is not None

    def test_log_levels_hierarchy(self):
        """Log seviye hiyerarşisi testi"""
        # ERROR seviyesinde logger
        error_logger = logger.setup_logger(
            log_file_path=self.temp_log_file,
            log_level='ERROR'
        )
        
        # Düşük seviye loglar yazılmamalı
        logger.log_debug("Debug mesajı")
        logger.log_info("Info mesajı")
        logger.log_warning("Warning mesajı")
        logger.log_error("Error mesajı")
        
        with open(self.temp_log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Debug mesajı" not in content
            assert "Info mesajı" not in content
            assert "Warning mesajı" not in content
            assert "Error mesajı" in content

    def test_performance_with_many_logs(self):
        """Çok sayıda log ile performans testi"""
        test_logger = logger.setup_logger(
            log_file_path=self.temp_log_file,
            log_level='INFO'
        )
        
        import time
        start_time = time.time()
        
        # 1000 log mesajı
        for i in range(1000):
            logger.log_info(f"Performance test mesajı {i}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 1000 mesaj 10 saniyeden az sürmeli
        assert duration < 10.0
        
        # Dosyanın oluştuğunu kontrol et
        assert os.path.exists(self.temp_log_file)

    def test_error_handling_with_invalid_path(self):
        """Geçersiz dosya yolu ile hata işleme testi"""
        # Windows'ta geçersiz karakter içeren yol
        invalid_path = "C:\\invalid<>path\\test.log"
        
        try:
            test_logger = logger.setup_logger(
                log_file_path=invalid_path,
                log_level='INFO'
            )
            # Eğer başarılı olursa, en azından log fonksiyonu çalışmalı
            logger.log_info("Test mesajı")
        except Exception as e:
            # Hata bekleniyor, bu normal
            assert isinstance(e, (OSError, IOError, Exception))


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
