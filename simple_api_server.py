"""
Basit AI-FTB API Sunucusu - Hızlı Test İçin
"""

from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
import json

# Flask uygulamasını oluştur
app = Flask(__name__)
CORS(app)

# Bot durumu
bot_status = {
    'is_running': True,
    'last_update': datetime.now().isoformat(),
    'status': 'active',
    'message': 'Bot çalışıyor - Test Modu',
    'performance': {
        'total_return': 15.5,
        'daily_return': 2.3,
        'sharpe_ratio': 1.8,
        'max_drawdown': -5.2
    }
}

@app.route('/api/status', methods=['GET'])
def get_bot_status():
    """Bot durumunu döndürür"""
    bot_status['last_update'] = datetime.now().isoformat()
    return jsonify(bot_status)

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """Portföy bilgilerini döndürür"""
    portfolio = {
        'total_value': 150000.0,
        'day_change': 3500.0,
        'day_change_percent': 2.4,
        'positions': [
            {
                'symbol': 'AAPL',
                'quantity': 100,
                'current_price': 185.0,
                'value': 18500.0,
                'change': 250.0,
                'change_percent': 1.37
            },
            {
                'symbol': 'MSFT',
                'quantity': 50,
                'current_price': 380.0,
                'value': 19000.0,
                'change': 150.0,
                'change_percent': 0.79
            }
        ],
        'cash': 112500.0
    }
    return jsonify(portfolio)

@app.route('/api/signals', methods=['GET'])
def get_signals():
    """Son ticaret sinyallerini döndürür"""
    signals = [
        {
            'symbol': 'AAPL',
            'signal': 'BUY',
            'confidence': 0.85,
            'price': 185.0,
            'timestamp': datetime.now().isoformat(),
            'reason': 'Teknik analiz ve momentum sinyali'
        },
        {
            'symbol': 'GOOGL',
            'signal': 'HOLD',
            'confidence': 0.72,
            'price': 142.0,
            'timestamp': datetime.now().isoformat(),
            'reason': 'Karışık sinyal, bekleme önerisi'
        }
    ]
    return jsonify(signals)

@app.route('/api/news', methods=['GET'])
def get_news():
    """Finansal haberleri döndürür"""
    news = [
        {
            'title': 'Teknoloji Hisseleri Yükselişte',
            'summary': 'AI ve teknoloji sektörü güçlü performans gösteriyor...',
            'sentiment': 'positive',
            'timestamp': datetime.now().isoformat(),
            'source': 'Financial News'
        },
        {
            'title': 'Piyasa Genel Durumu',
            'summary': 'Günlük işlem hacmi artış gösteriyor...',
            'sentiment': 'neutral',
            'timestamp': datetime.now().isoformat(),
            'source': 'Market Update'
        }
    ]
    return jsonify(news)

@app.route('/api/health', methods=['GET'])
def health_check():
    """API sağlık kontrolü"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'AI-FTB API Server çalışıyor'
    })

@app.route('/api/stocks/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    """Hisse senedi verilerini döndürür"""
    from flask import request
    days = request.args.get('days', 30, type=int)
    
    # Örnek hisse senedi verisi
    stock_data = {
        'symbol': symbol,
        'current_price': 185.50 if symbol == 'AAPL' else 142.30,
        'change': 2.50,
        'change_percent': 1.37,
        'volume': 45234567,
        'market_cap': '2.85T',
        'pe_ratio': 29.8,
        'historical_data': [
            {
                'date': '2025-07-20',
                'open': 183.0,
                'high': 186.5,
                'low': 182.1,
                'close': 185.5,
                'volume': 45234567
            },
            {
                'date': '2025-07-19',
                'open': 181.2,
                'high': 184.3,
                'low': 180.8,
                'close': 183.0,
                'volume': 38745123
            }
        ]
    }
    return jsonify(stock_data)

@app.route('/api/sentiment/<symbol>', methods=['GET'])
def get_sentiment_data(symbol):
    """Duygu analizi verilerini döndürür"""
    from flask import request
    days = request.args.get('days', 30, type=int)
    
    sentiment_data = {
        'symbol': symbol,
        'overall_sentiment': 'positive',
        'sentiment_score': 0.75,
        'news_count': 25,
        'historical_sentiment': [
            {
                'date': '2025-07-20',
                'sentiment': 'positive',
                'score': 0.8,
                'news_count': 5
            },
            {
                'date': '2025-07-19',
                'sentiment': 'neutral',
                'score': 0.6,
                'news_count': 3
            }
        ]
    }
    return jsonify(sentiment_data)

@app.route('/api/news/<symbol>', methods=['GET'])
def get_stock_news(symbol):
    """Hisse senedi haberlerini döndürür"""
    from flask import request
    limit = request.args.get('limit', 50, type=int)
    
    news_data = [
        {
            'title': f'{symbol} Güçlü Performans Gösteriyor',
            'summary': f'{symbol} hissesi son günlerde yükseliş trendinde...',
            'sentiment': 'positive',
            'timestamp': datetime.now().isoformat(),
            'source': 'Financial Times',
            'url': 'https://example.com/news1'
        },
        {
            'title': f'{symbol} Piyasa Analizi',
            'summary': 'Uzmanlar pozitif öngörülerini koruyor...',
            'sentiment': 'positive',
            'timestamp': datetime.now().isoformat(),
            'source': 'Bloomberg',
            'url': 'https://example.com/news2'
        }
    ]
    return jsonify(news_data[:limit])

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Uygulama ayarlarını döndürür"""
    settings = {
        'risk_level': 'medium',
        'auto_trading': False,
        'notifications': True,
        'theme': 'light',
        'language': 'tr',
        'update_interval': 60,
        'trading_hours': {
            'start': '09:30',
            'end': '16:00'
        }
    }
    return jsonify(settings)

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Uygulama ayarlarını günceller"""
    from flask import request
    data = request.get_json()
    
    return jsonify({
        'status': 'success',
        'message': 'Ayarlar güncellendi',
        'updated_settings': data
    })

@app.route('/api/start', methods=['POST'])
def start_bot():
    """Bot'u başlatır"""
    global bot_status
    bot_status['is_running'] = True
    bot_status['status'] = 'active'
    bot_status['message'] = 'Bot başarıyla başlatıldı'
    bot_status['last_update'] = datetime.now().isoformat()
    
    return jsonify({
        'status': 'success',
        'message': 'Bot başlatıldı',
        'bot_status': bot_status
    })

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Bot'u durdurur"""
    global bot_status
    bot_status['is_running'] = False
    bot_status['status'] = 'paused'
    bot_status['message'] = 'Bot durduruldu'
    bot_status['last_update'] = datetime.now().isoformat()
    
    return jsonify({
        'status': 'success',
        'message': 'Bot durduruldu',
        'bot_status': bot_status
    })

@app.route('/api/portfolio/add', methods=['POST'])
def add_portfolio_position():
    """Portföye yeni pozisyon ekler"""
    from flask import request
    data = request.get_json()
    
    symbol = data.get('symbol')
    quantity = data.get('quantity', 0)
    price = data.get('price', 0)
    
    return jsonify({
        'status': 'success',
        'message': f'{symbol} pozisyonu eklendi',
        'position': {
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'value': quantity * price
        }
    })

@app.route('/api/portfolio/update', methods=['PUT'])
def update_portfolio_position():
    """Portföy pozisyonunu günceller"""
    from flask import request
    data = request.get_json()
    
    symbol = data.get('symbol')
    quantity = data.get('quantity', 0)
    
    return jsonify({
        'status': 'success',
        'message': f'{symbol} pozisyonu güncellendi',
        'updated_position': {
            'symbol': symbol,
            'quantity': quantity
        }
    })

@app.route('/api/portfolio/remove', methods=['DELETE'])
def remove_portfolio_position():
    """Portföy pozisyonunu siler"""
    from flask import request
    data = request.get_json()
    
    symbol = data.get('symbol')
    
    return jsonify({
        'status': 'success',
        'message': f'{symbol} pozisyonu silindi',
        'removed_symbol': symbol
    })

@app.route('/api/symbols/search', methods=['GET'])
def search_symbols():
    """Hisse senedi sembolleri arar"""
    from flask import request
    query = request.args.get('query', '')
    
    # Örnek sembol listesi (gerçek uygulamada API'den gelecek)
    all_symbols = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'sector': 'Technology'},
        {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'sector': 'Technology'},
        {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'sector': 'Technology'},
        {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'sector': 'Automotive'},
        {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'sector': 'E-commerce'},
        {'symbol': 'NVDA', 'name': 'NVIDIA Corp.', 'sector': 'Technology'},
        {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'sector': 'Technology'},
        {'symbol': 'NFLX', 'name': 'Netflix Inc.', 'sector': 'Entertainment'},
        {'symbol': 'AMD', 'name': 'Advanced Micro Devices', 'sector': 'Technology'},
        {'symbol': 'INTC', 'name': 'Intel Corp.', 'sector': 'Technology'},
        # Türk hisseleri
        {'symbol': 'THYAO.IS', 'name': 'Türk Hava Yolları', 'sector': 'Airlines'},
        {'symbol': 'BIST100.IS', 'name': 'BIST 100 Endeksi', 'sector': 'Index'},
        {'symbol': 'AKBNK.IS', 'name': 'Akbank', 'sector': 'Banking'},
        {'symbol': 'GARAN.IS', 'name': 'Garanti BBVA', 'sector': 'Banking'},
    ]
    
    # Query'ye göre filtrele
    if query:
        filtered_symbols = [
            s for s in all_symbols 
            if query.upper() in s['symbol'].upper() or query.upper() in s['name'].upper()
        ]
    else:
        filtered_symbols = all_symbols[:10]  # İlk 10'u göster
    
    return jsonify(filtered_symbols)

@app.route('/api/chart/<symbol>', methods=['GET'])
def get_chart_data(symbol):
    """Detaylı grafik verilerini döndürür"""
    from flask import request
    days = request.args.get('days', 30, type=int)
    
    import random
    from datetime import datetime, timedelta
    
    # Örnek grafik verisi oluştur
    chart_data = []
    base_price = 150.0 if symbol == 'AAPL' else 100.0
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i)).strftime('%Y-%m-%d')
        
        # Rastgele fiyat hareketleri
        change = random.uniform(-0.05, 0.05)
        base_price *= (1 + change)
        
        chart_data.append({
            'date': date,
            'open': round(base_price * 0.99, 2),
            'high': round(base_price * 1.02, 2),
            'low': round(base_price * 0.98, 2),
            'close': round(base_price, 2),
            'volume': random.randint(1000000, 50000000)
        })
    
    return jsonify({
        'symbol': symbol,
        'data': chart_data,
        'indicators': {
            'sma_20': round(base_price * 0.98, 2),
            'sma_50': round(base_price * 0.96, 2),
            'rsi': random.randint(30, 70),
            'macd': round(random.uniform(-2, 2), 2)
        }
    })

if __name__ == '__main__':
    print("🚀 AI-FTB API Sunucusu başlatılıyor...")
    print("📡 URL: http://localhost:8000")
    print("🔗 Health Check: http://localhost:8000/api/health")
    
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        threaded=True
    )
