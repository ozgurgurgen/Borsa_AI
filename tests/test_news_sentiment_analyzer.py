"""
test_news_sentiment_analyzer.py - NewsSentimentAnalyzer modülü için birim testler

Bu dosya NewsSentimentAnalyzer sınıfının tüm fonksiyonlarını test eder:
- Haber alma testleri
- Sentiment analizi testleri
- Puan hesaplama testleri
- Hata durumu testleri
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from datetime import datetime, timedelta

# Ana proje klasörünü Python path'ine ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from news_sentiment_analyzer import NewsSentimentAnalyzer
from config import Config


class TestNewsSentimentAnalyzer(unittest.TestCase):
    """NewsSentimentAnalyzer sınıfı için test sınıfı"""
    
    def setUp(self):
        """Her test öncesi çalışan setup metodu"""
        self.analyzer = NewsSentimentAnalyzer()
        
        # Mock haber verileri
        self.mock_news_data = [
            {
                'title': 'Şirket güçlü çeyreklik sonuçlar açıkladı',
                'summary': 'Şirket beklentileri aşan kazanç ve gelir rakamları açıkladı.',
                'published': datetime.now() - timedelta(hours=2),
                'source': 'Test News',
                'url': 'https://test.com/news1'
            },
            {
                'title': 'Piyasada düşüş endişesi',
                'summary': 'Uzmanlar yakın dönemde piyasada düşüş olabileceği konusunda uyardı.',
                'published': datetime.now() - timedelta(hours=1),
                'source': 'Test News',
                'url': 'https://test.com/news2'
            },
            {
                'title': 'Teknoloji sektöründe büyüme',
                'summary': 'Teknoloji şirketleri bu çeyrekte güçlü büyüme gösterdi.',
                'published': datetime.now() - timedelta(minutes=30),
                'source': 'Test News',
                'url': 'https://test.com/news3'
            }
        ]
    
    def test_init(self):
        """NewsSentimentAnalyzer başlatma testi"""
        self.assertIsInstance(self.analyzer, NewsSentimentAnalyzer)
        self.assertIn('news_cache', self.analyzer.__dict__)
        self.assertIn('sentiment_cache', self.analyzer.__dict__)
    
    @patch('news_sentiment_analyzer.feedparser')
    def test_fetch_rss_news_success(self, mock_feedparser):
        """RSS haber alma başarı testi"""
        # Mock RSS response
        mock_feed = Mock()
        mock_feed.entries = [
            Mock(
                title='Test News Title',
                summary='Test news summary content.',
                published_parsed=(2024, 1, 15, 10, 30, 0, 0, 0, 0),
                link='https://test.com/news'
            )
        ]
        mock_feedparser.parse.return_value = mock_feed
        
        result = self.analyzer.fetch_rss_news('https://test-rss.com/feed')
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        # İlk haberin yapısını kontrol et
        news_item = result[0]
        self.assertIn('title', news_item)
        self.assertIn('summary', news_item)
        self.assertIn('published', news_item)
        self.assertIn('url', news_item)
    
    @patch('news_sentiment_analyzer.feedparser')
    def test_fetch_rss_news_failure(self, mock_feedparser):
        """RSS haber alma başarısızlık testi"""
        # Mock hata durumu
        mock_feedparser.parse.side_effect = Exception("RSS parsing error")
        
        result = self.analyzer.fetch_rss_news('https://invalid-rss.com/feed')
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
    
    @patch('news_sentiment_analyzer.requests')
    def test_fetch_news_api_success(self, mock_requests):
        """News API haber alma başarı testi"""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'articles': [
                {
                    'title': 'API News Title',
                    'description': 'API news description.',
                    'publishedAt': '2024-01-15T10:30:00Z',
                    'url': 'https://api-news.com/article',
                    'source': {'name': 'API News Source'}
                }
            ]
        }
        mock_requests.get.return_value = mock_response
        
        result = self.analyzer.fetch_news_api('technology', 'test_api_key')
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        # Haber yapısını kontrol et
        news_item = result[0]
        self.assertIn('title', news_item)
        self.assertIn('summary', news_item)
        self.assertIn('published', news_item)
    
    @patch('news_sentiment_analyzer.requests')
    def test_fetch_news_api_failure(self, mock_requests):
        """News API haber alma başarısızlık testi"""
        # Mock API hatası
        mock_response = Mock()
        mock_response.status_code = 401
        mock_requests.get.return_value = mock_response
        
        result = self.analyzer.fetch_news_api('technology', 'invalid_key')
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
    
    def test_analyze_sentiment_positive(self):
        """Pozitif sentiment analizi testi"""
        positive_text = "Bu harika bir gelişme! Şirket çok başarılı bir performans gösterdi."
        
        result = self.analyzer.analyze_sentiment(positive_text)
        
        self.assertIsInstance(result, dict)
        self.assertIn('compound', result)
        self.assertIn('positive', result)
        self.assertIn('negative', result)
        self.assertIn('neutral', result)
        
        # Pozitif metin için compound score pozitif olmalı
        self.assertGreater(result['compound'], 0)
        self.assertGreater(result['positive'], result['negative'])
    
    def test_analyze_sentiment_negative(self):
        """Negatif sentiment analizi testi"""
        negative_text = "Bu kötü bir durum. Şirket başarısız oldu ve kayıplar arttı."
        
        result = self.analyzer.analyze_sentiment(negative_text)
        
        self.assertIsInstance(result, dict)
        
        # Negatif metin için compound score negatif olmalı
        self.assertLess(result['compound'], 0)
        self.assertGreater(result['negative'], result['positive'])
    
    def test_analyze_sentiment_neutral(self):
        """Nötr sentiment analizi testi"""
        neutral_text = "Şirket bu çeyrek normal performans gösterdi."
        
        result = self.analyzer.analyze_sentiment(neutral_text)
        
        self.assertIsInstance(result, dict)
        
        # Nötr metin için compound score sıfıra yakın olmalı
        self.assertLessEqual(abs(result['compound']), 0.5)
    
    def test_analyze_sentiment_empty_text(self):
        """Boş metin sentiment analizi testi"""
        result = self.analyzer.analyze_sentiment("")
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['compound'], 0.0)
        self.assertEqual(result['positive'], 0.0)
        self.assertEqual(result['negative'], 0.0)
        self.assertEqual(result['neutral'], 1.0)
    
    def test_classify_sentiment(self):
        """Sentiment sınıflandırma testi"""
        # Pozitif
        positive_score = 0.6
        self.assertEqual(self.analyzer.classify_sentiment(positive_score), 'positive')
        
        # Negatif
        negative_score = -0.6
        self.assertEqual(self.analyzer.classify_sentiment(negative_score), 'negative')
        
        # Nötr
        neutral_score = 0.0
        self.assertEqual(self.analyzer.classify_sentiment(neutral_score), 'neutral')
        
        # Sınır değerler
        self.assertEqual(self.analyzer.classify_sentiment(0.05), 'neutral')
        self.assertEqual(self.analyzer.classify_sentiment(-0.05), 'neutral')
        self.assertEqual(self.analyzer.classify_sentiment(0.1), 'positive')
        self.assertEqual(self.analyzer.classify_sentiment(-0.1), 'negative')
    
    def test_calculate_sentiment_score(self):
        """Sentiment skorları hesaplama testi"""
        result = self.analyzer.calculate_sentiment_score(self.mock_news_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('overall_score', result)
        self.assertIn('positive_count', result)
        self.assertIn('negative_count', result)
        self.assertIn('neutral_count', result)
        self.assertIn('total_news', result)
        self.assertIn('confidence', result)
        
        # Toplam haber sayısı doğru olmalı
        self.assertEqual(result['total_news'], len(self.mock_news_data))
        
        # Sayılar toplamı toplam habere eşit olmalı
        total_classified = (result['positive_count'] + 
                          result['negative_count'] + 
                          result['neutral_count'])
        self.assertEqual(total_classified, result['total_news'])
        
        # Overall score -1 ile 1 arasında olmalı
        self.assertGreaterEqual(result['overall_score'], -1.0)
        self.assertLessEqual(result['overall_score'], 1.0)
        
        # Confidence 0 ile 1 arasında olmalı
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)
    
    def test_calculate_sentiment_score_empty_news(self):
        """Boş haber listesi sentiment skoru testi"""
        result = self.analyzer.calculate_sentiment_score([])
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['overall_score'], 0.0)
        self.assertEqual(result['total_news'], 0)
        self.assertEqual(result['confidence'], 0.0)
    
    @patch.object(NewsSentimentAnalyzer, 'fetch_rss_news')
    @patch.object(NewsSentimentAnalyzer, 'fetch_news_api')
    def test_get_market_sentiment(self, mock_api, mock_rss):
        """Piyasa sentiment'i alma testi"""
        # Mock veri dönüş değerleri
        mock_rss.return_value = self.mock_news_data[:2]
        mock_api.return_value = self.mock_news_data[2:]
        
        result = self.analyzer.get_market_sentiment('AAPL')
        
        self.assertIsInstance(result, dict)
        self.assertIn('symbol', result)
        self.assertIn('sentiment_score', result)
        self.assertIn('news_count', result)
        self.assertIn('last_updated', result)
        
        # Sembol doğru olmalı
        self.assertEqual(result['symbol'], 'AAPL')
        
        # Haber sayısı pozitif olmalı
        self.assertGreater(result['news_count'], 0)
    
    def test_filter_news_by_relevance(self):
        """Haber relevans filtreleme testi"""
        symbol = 'AAPL'
        
        # İlgili ve ilgisiz haberler
        news_data = [
            {
                'title': 'Apple announces new iPhone',
                'summary': 'Apple revealed exciting new features.',
                'published': datetime.now(),
                'url': 'https://test.com/apple1'
            },
            {
                'title': 'Google updates search algorithm',
                'summary': 'Google made changes to search.',
                'published': datetime.now(),
                'url': 'https://test.com/google1'
            },
            {
                'title': 'AAPL stock rises after earnings',
                'summary': 'Apple stock performed well.',
                'published': datetime.now(),
                'url': 'https://test.com/apple2'
            }
        ]
        
        result = self.analyzer.filter_news_by_relevance(news_data, symbol)
        
        self.assertIsInstance(result, list)
        
        # Apple ile ilgili haberler filtrelenmiş olmalı
        for news in result:
            title_text = (news['title'] + ' ' + news['summary']).lower()
            self.assertTrue('apple' in title_text or 'aapl' in title_text)
    
    def test_filter_news_by_date(self):
        """Tarih ile haber filtreleme testi"""
        # Farklı tarihli haberler
        old_news = {
            'title': 'Old news',
            'summary': 'This is old news.',
            'published': datetime.now() - timedelta(days=5),
            'url': 'https://test.com/old'
        }
        
        recent_news = {
            'title': 'Recent news',
            'summary': 'This is recent news.',
            'published': datetime.now() - timedelta(hours=1),
            'url': 'https://test.com/recent'
        }
        
        news_data = [old_news, recent_news]
        hours_limit = 24
        
        result = self.analyzer.filter_news_by_date(news_data, hours_limit)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)  # Sadece son 24 saatteki haber
        self.assertEqual(result[0]['title'], 'Recent news')
    
    def test_cache_functionality(self):
        """Cache fonksiyonalitesi testi"""
        # İlk çağrı
        text = "Test sentiment analysis"
        result1 = self.analyzer.analyze_sentiment(text)
        
        # İkinci çağrı (cache'den gelecek)
        result2 = self.analyzer.analyze_sentiment(text)
        
        # Sonuçlar aynı olmalı
        self.assertEqual(result1, result2)
        
        # Cache'de olmalı
        self.assertIn(text, self.analyzer.sentiment_cache)
    
    def test_get_sentiment_summary(self):
        """Sentiment özeti alma testi"""
        result = self.analyzer.get_sentiment_summary(self.mock_news_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('summary', result)
        self.assertIn('recommendation', result)
        self.assertIn('confidence_level', result)
        self.assertIn('key_factors', result)
        
        # Recommendation değerleri
        valid_recommendations = ['BUY', 'SELL', 'HOLD']
        self.assertIn(result['recommendation'], valid_recommendations)
        
        # Key factors liste olmalı
        self.assertIsInstance(result['key_factors'], list)
    
    def test_multilingual_sentiment(self):
        """Çok dilli sentiment analizi testi"""
        # Türkçe metin
        turkish_text = "Bu çok iyi bir gelişme ve güzel haberler var."
        result_tr = self.analyzer.analyze_sentiment(turkish_text)
        
        # İngilizce metin
        english_text = "This is great news and excellent development."
        result_en = self.analyzer.analyze_sentiment(english_text)
        
        # Her iki sonuç da pozitif olmalı
        self.assertGreater(result_tr['compound'], 0)
        self.assertGreater(result_en['compound'], 0)
    
    def test_error_handling(self):
        """Hata yönetimi testleri"""
        # None değer ile test
        result_none = self.analyzer.analyze_sentiment(None)
        self.assertIsInstance(result_none, dict)
        
        # Çok uzun metin ile test
        very_long_text = "Bu çok uzun bir metin. " * 1000
        result_long = self.analyzer.analyze_sentiment(very_long_text)
        self.assertIsInstance(result_long, dict)
        
        # Özel karakterler ile test
        special_text = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        result_special = self.analyzer.analyze_sentiment(special_text)
        self.assertIsInstance(result_special, dict)


class TestNewsSentimentAnalyzerIntegration(unittest.TestCase):
    """NewsSentimentAnalyzer entegrasyon testleri"""
    
    def setUp(self):
        """Her test öncesi çalışan setup metodu"""
        self.analyzer = NewsSentimentAnalyzer()
    
    @patch.object(NewsSentimentAnalyzer, 'fetch_rss_news')
    @patch.object(NewsSentimentAnalyzer, 'fetch_news_api')
    def test_full_workflow(self, mock_api, mock_rss):
        """Tam iş akışı entegrasyon testi"""
        # Mock haber verileri
        mock_news = [
            {
                'title': 'Company reports strong earnings',
                'summary': 'Excellent quarterly results exceeded expectations.',
                'published': datetime.now() - timedelta(hours=1),
                'url': 'https://test.com/earnings'
            }
        ]
        
        mock_rss.return_value = mock_news
        mock_api.return_value = []
        
        # Tam workflow çalıştır
        sentiment_data = self.analyzer.get_market_sentiment('TEST')
        
        self.assertIsInstance(sentiment_data, dict)
        self.assertIn('sentiment_score', sentiment_data)
        self.assertGreater(sentiment_data['news_count'], 0)
        
        # Sentiment summary al
        summary = self.analyzer.get_sentiment_summary(mock_news)
        self.assertIsInstance(summary, dict)
        self.assertIn('recommendation', summary)


if __name__ == '__main__':
    # Test çalıştırma
    unittest.main(verbosity=2)
