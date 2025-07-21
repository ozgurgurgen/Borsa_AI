"""
AI-FTB (AI-Powered Financial Trading Bot) News Sentiment Analyzer Module

Bu modül, finansal haberleri çeker, ön işler ve duygu analizi yaparak sayısal 
bir duygu skoru atar. TextBlob kullanarak basit, kurallara dayalı duygu analizi yapar.
"""

import pandas as pd
import numpy as np
import re
import json
from datetime import datetime, timedelta
from textblob import TextBlob
import requests
import config
import logger


def fetch_financial_news(query, start_date=None, end_date=None, api_key=None):
    """
    Belirli bir sorgu (şirket adı) ve tarih aralığı için finansal haberleri çeker.
    NewsAPI veya benzer bir servisi kullanır. API yoksa örnek veri döndürür.
    
    Args:
        query (str): Arama sorgusu (örn. şirket adı)
        start_date (str): Başlangıç tarihi ('YYYY-MM-DD' formatında)
        end_date (str): Bitiş tarihi ('YYYY-MM-DD' formatında)
        api_key (str): News API anahtarı
    
    Returns:
        list: Haber listesi [{'title': str, 'content': str, 'date': str, 'url': str}]
        None: Hata durumunda
        
    Raises:
        Exception: API çağrısı veya JSON parse hatalarında
    """
    try:
        # API anahtarını config'ten al
        if api_key is None:
            api_key = config.API_KEYS.get('NEWS_API_KEY', '')
            
        if not api_key or api_key == 'YOUR_NEWS_API_KEY_HERE':
            logger.log_warning("News API anahtarı bulunamadı, örnek veriler kullanılıyor")
            return _get_sample_news_data(query)
            
        # Tarih kontrolü
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        logger.log_info(f"Haberler çekiliyor: {query} ({start_date} - {end_date})")
        
        # NewsAPI URL'i oluştur
        base_url = "https://newsapi.org/v2/everything"
        params = {
            'q': query,
            'from': start_date,
            'to': end_date,
            'sortBy': 'relevancy',
            'language': 'en',
            'apiKey': api_key,
            'pageSize': 50  # Maksimum 50 haber
        }
        
        # API çağrısı yap
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') != 'ok':
            logger.log_error(f"News API hatası: {data.get('message', 'Bilinmeyen hata')}")
            return _get_sample_news_data(query)
            
        # Haberleri işle
        articles = data.get('articles', [])
        news_list = []
        
        for article in articles:
            # Gerekli alanları kontrol et
            if not article.get('title') or not article.get('description'):
                continue
                
            news_item = {
                'title': article.get('title', ''),
                'content': article.get('description', '') + ' ' + (article.get('content', '') or ''),
                'date': article.get('publishedAt', ''),
                'url': article.get('url', ''),
                'source': article.get('source', {}).get('name', '')
            }
            
            # İçerik temizle
            news_item['content'] = _clean_news_content(news_item['content'])
            
            if len(news_item['content']) > 50:  # Çok kısa içerikleri filtrele
                news_list.append(news_item)
                
        logger.log_info(f"{len(news_list)} haber çekildi ({query})")
        return news_list
        
    except requests.exceptions.RequestException as e:
        logger.log_error(f"News API bağlantı hatası: {e}")
        return _get_sample_news_data(query)
    except Exception as e:
        logger.log_error(f"Haber çekerken hata: {e}", exc_info=True)
        return _get_sample_news_data(query)


def _get_sample_news_data(query):
    """
    API olmadığında kullanılacak örnek haber verisi.
    
    Args:
        query (str): Arama sorgusu
    
    Returns:
        list: Örnek haber listesi
    """
    sample_news = [
        {
            'title': f'{query} Reports Strong Q4 Earnings',
            'content': f'{query} announced better-than-expected quarterly earnings, driven by strong revenue growth and improved operational efficiency. The company exceeded analyst expectations.',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'url': 'https://example.com/news1',
            'source': 'Financial Times'
        },
        {
            'title': f'{query} Faces Market Challenges',
            'content': f'{query} is navigating through challenging market conditions with increased competition and regulatory pressures affecting its business operations.',
            'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'url': 'https://example.com/news2',
            'source': 'Reuters'
        },
        {
            'title': f'{query} Announces New Product Launch',
            'content': f'{query} unveiled its latest innovation in technology, promising to revolutionize the industry with cutting-edge features and improved user experience.',
            'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'url': 'https://example.com/news3',
            'source': 'TechCrunch'
        }
    ]
    
    logger.log_info(f"Örnek haber verisi kullanılıyor: {len(sample_news)} haber")
    return sample_news


def _clean_news_content(content):
    """
    Haber içeriğinden gereksiz karakterleri ve HTML etiketlerini temizler.
    
    Args:
        content (str): Ham haber içeriği
    
    Returns:
        str: Temizlenmiş haber içeriği
    """
    if not content:
        return ""
        
    # HTML etiketlerini kaldır
    content = re.sub(r'<[^>]+>', '', content)
    
    # URL'leri kaldır
    content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)
    
    # Fazla boşlukları temizle
    content = re.sub(r'\\s+', ' ', content)
    
    # Özel karakterleri temizle
    content = re.sub(r'[^\\w\\s.,!?;:-]', '', content)
    
    return content.strip()


def preprocess_news_text(text):
    """
    Haber metinlerini NLP için temizler. Küçük harfe çevirme, noktalama 
    işaretlerini kaldırma ve temel temizlik işlemlerini yapar.
    
    Args:
        text (str): Ham haber metni
    
    Returns:
        str: Ön işlemden geçmiş metin
        
    Raises:
        Exception: Metin işleme hatalarında
    """
    try:
        if not text or not isinstance(text, str):
            return ""
            
        # Temel temizlik
        text = _clean_news_content(text)
        
        # Küçük harfe çevir
        text = text.lower()
        
        # Noktalama işaretlerini koru (duygu analizi için önemli)
        # Sadece gereksiz karakterleri kaldır
        text = re.sub(r'[^a-zA-Z0-9\\s.,!?;:-]', '', text)
        
        # Çoklu boşlukları tek boşluğa çevir
        text = re.sub(r'\\s+', ' ', text)
        
        # Başındaki ve sonundaki boşlukları kaldır
        text = text.strip()
        
        return text
        
    except Exception as e:
        logger.log_error(f"Metin ön işleme hatası: {e}")
        return ""


def analyze_sentiment(text):
    """
    Önceden işlenmiş metne TextBlob kullanarak duygu analizi uygular.
    -1.0 (çok negatif) ile 1.0 (çok pozitif) arası sayısal duygu skoru döndürür.
    
    Args:
        text (str): Analiz edilecek metin
    
    Returns:
        float: Duygu skoru (-1.0 ile 1.0 arası)
        
    Raises:
        Exception: Duygu analizi hatalarında
    """
    try:
        if not text or not isinstance(text, str):
            return 0.0
            
        # TextBlob ile duygu analizi yap
        blob = TextBlob(text)
        
        # Polarity değeri -1 ile 1 arasında
        # -1: Çok negatif, 0: Nötr, 1: Çok pozitif
        polarity = blob.sentiment.polarity
        
        # Subjectivity değeri de mevcut (0: Objektif, 1: Sübjektif)
        subjectivity = blob.sentiment.subjectivity
        
        # Eğer metin çok objektifse (subjectivity < 0.1), duygu skorunu azalt
        if subjectivity < 0.1:
            polarity *= 0.5
            
        # Değeri sınırlar içinde tut
        polarity = max(-1.0, min(1.0, polarity))
        
        return float(polarity)
        
    except Exception as e:
        logger.log_error(f"Duygu analizi hatası: {e}")
        return 0.0


def get_news_sentiment_for_date(symbol, date, days_back=3):
    """
    Belirli bir sembol ve tarih için ilgili haberleri çekip, duygu analizi yapıp 
    ortalama duygu skorunu döndürür.
    
    Args:
        symbol (str): İşlem sembolü (örn. 'AAPL')
        date (str veya datetime): İlgili tarih
        days_back (int): Kaç gün geriye gidilerek haber aranacak
    
    Returns:
        dict: {'sentiment_score': float, 'news_count': int, 'confidence': float}
        None: Hata durumunda
        
    Raises:
        Exception: Haber çekme veya analiz hatalarında
    """
    try:
        # Tarihi datetime objesine çevir
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d')
            
        # Arama tarih aralığını belirle
        end_date = date.strftime('%Y-%m-%d')
        start_date = (date - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        # Sembol için arama sorgularını config'ten al
        search_queries = config.NEWS_SEARCH_KEYWORDS.get(symbol, [symbol])
        
        all_sentiments = []
        total_news_count = 0
        
        # Her arama sorgusu için haberleri çek
        for query in search_queries:
            news_list = fetch_financial_news(query, start_date, end_date)
            
            if not news_list:
                continue
                
            # Her haber için duygu analizi yap
            for news in news_list:
                # Başlık ve içeriği birleştir
                full_text = f"{news['title']} {news['content']}"
                
                # Metni ön işleme tabi tut
                processed_text = preprocess_news_text(full_text)
                
                if len(processed_text) > 20:  # Çok kısa metinleri filtrele
                    sentiment = analyze_sentiment(processed_text)
                    all_sentiments.append(sentiment)
                    total_news_count += 1
                    
        # Sonuçları hesapla
        if not all_sentiments:
            logger.log_warning(f"Duygu analizi için haber bulunamadı ({symbol}, {date})")
            return {
                'sentiment_score': 0.0,
                'news_count': 0,
                'confidence': 0.0
            }
            
        # Ortalama duygu skorunu hesapla
        avg_sentiment = np.mean(all_sentiments)
        
        # Güven skorunu hesapla (haber sayısına ve duygu dağılımına bağlı)
        sentiment_std = np.std(all_sentiments) if len(all_sentiments) > 1 else 0
        confidence = min(1.0, total_news_count / 10) * (1 - sentiment_std / 2)
        
        result = {
            'sentiment_score': float(avg_sentiment),
            'news_count': total_news_count,
            'confidence': float(confidence)
        }
        
        logger.log_info(f"Duygu analizi ({symbol}, {date}): Score={avg_sentiment:.3f}, Count={total_news_count}, Confidence={confidence:.3f}")
        
        return result
        
    except Exception as e:
        logger.log_error(f"Tarihsel duygu analizi hatası ({symbol}, {date}): {e}", exc_info=True)
        return None


def batch_sentiment_analysis(symbols, start_date, end_date):
    """
    Birden fazla sembol için belirli tarih aralığında toplu duygu analizi yapar.
    
    Args:
        symbols (list): Sembol listesi
        start_date (str): Başlangıç tarihi
        end_date (str): Bitiş tarihi
    
    Returns:
        pandas.DataFrame: Tarih-sembol-duygu skoru tablosu
    """
    try:
        logger.log_info(f"Toplu duygu analizi başlıyor: {len(symbols)} sembol, {start_date} - {end_date}")
        
        results = []
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        for date in date_range:
            for symbol in symbols:
                sentiment_data = get_news_sentiment_for_date(symbol, date)
                
                if sentiment_data:
                    results.append({
                        'Date': date,
                        'Symbol': symbol,
                        'Sentiment_Score': sentiment_data['sentiment_score'],
                        'News_Count': sentiment_data['news_count'],
                        'Confidence': sentiment_data['confidence']
                    })
                    
        # DataFrame oluştur
        df = pd.DataFrame(results)
        
        if not df.empty:
            df = df.set_index(['Date', 'Symbol'])
            logger.log_info(f"Toplu duygu analizi tamamlandı: {len(df)} kayıt")
        else:
            logger.log_warning("Toplu duygu analizinde veri bulunamadı")
            
        return df
        
    except Exception as e:
        logger.log_error(f"Toplu duygu analizi hatası: {e}")
        return pd.DataFrame()


def sentiment_summary_stats(sentiment_scores):
    """
    Duygu skorları için özet istatistikler hesaplar.
    
    Args:
        sentiment_scores (list): Duygu skorları listesi
    
    Returns:
        dict: Özet istatistikler
    """
    try:
        if not sentiment_scores:
            return {'count': 0}
            
        scores = np.array(sentiment_scores)
        
        # Pozitif, negatif, nötr sayıları
        positive_count = np.sum(scores > config.SENTIMENT_THRESHOLD_POSITIVE)
        negative_count = np.sum(scores < config.SENTIMENT_THRESHOLD_NEGATIVE)
        neutral_count = len(scores) - positive_count - negative_count
        
        stats = {
            'count': len(scores),
            'mean': float(np.mean(scores)),
            'median': float(np.median(scores)),
            'std': float(np.std(scores)),
            'min': float(np.min(scores)),
            'max': float(np.max(scores)),
            'positive_count': int(positive_count),
            'negative_count': int(negative_count),
            'neutral_count': int(neutral_count),
            'positive_ratio': float(positive_count / len(scores)),
            'negative_ratio': float(negative_count / len(scores))
        }
        
        return stats
        
    except Exception as e:
        logger.log_error(f"Duygu istatistik hatası: {e}")
        return {'count': 0}


if __name__ == "__main__":
    """
    News Sentiment Analyzer modülü test kodu
    """
    print("=== AI-FTB News Sentiment Analyzer Test ===")
    
    # Test metinleri
    test_texts = [
        "Apple reports record quarterly earnings, beating analyst expectations significantly.",
        "Tesla faces challenges with production delays and regulatory scrutiny.",
        "Microsoft announces innovative cloud services expansion worldwide.",
        "The market shows mixed signals amid economic uncertainty.",
        "Google's parent company Alphabet exceeds revenue projections this quarter."
    ]
    
    # Duygu analizi testi
    print("\\n1. Duygu analizi test ediliyor...")
    sentiments = []
    
    for i, text in enumerate(test_texts, 1):
        processed = preprocess_news_text(text)
        sentiment = analyze_sentiment(processed)
        sentiments.append(sentiment)
        
        print(f"   Text {i}: {sentiment:+.3f} - {text[:50]}...")
        
    # Özet istatistikler
    print("\\n2. Duygu istatistikleri:")
    stats = sentiment_summary_stats(sentiments)
    print(f"   Ortalama: {stats.get('mean', 0):.3f}")
    print(f"   Pozitif: {stats.get('positive_count', 0)}/{stats.get('count', 0)}")
    print(f"   Negatif: {stats.get('negative_count', 0)}/{stats.get('count', 0)}")
    
    # Haber çekme testi
    print("\\n3. Örnek haber çekme...")
    news = fetch_financial_news('AAPL')
    
    if news:
        print(f"   ✅ {len(news)} haber çekildi")
        print(f"   📰 İlk haber: {news[0]['title'][:50]}...")
        
        # İlk haber için duygu analizi
        first_news_sentiment = analyze_sentiment(
            preprocess_news_text(news[0]['title'] + ' ' + news[0]['content'])
        )
        print(f"   📊 İlk haber duygusu: {first_news_sentiment:+.3f}")
    else:
        print("   ❌ Haber çekilemedi")
        
    # Tarihsel duygu analizi testi
    print("\\n4. Tarihsel duygu analizi...")
    today = datetime.now().strftime('%Y-%m-%d')
    historical_sentiment = get_news_sentiment_for_date('AAPL', today)
    
    if historical_sentiment:
        print(f"   ✅ Tarihsel analiz tamamlandı")
        print(f"   📊 Duygu skoru: {historical_sentiment['sentiment_score']:+.3f}")
        print(f"   📰 Haber sayısı: {historical_sentiment['news_count']}")
        print(f"   🎯 Güven skoru: {historical_sentiment['confidence']:.3f}")
    else:
        print("   ❌ Tarihsel analiz başarısız")
        
    print("\\nNews Sentiment Analyzer test tamamlandı!")
