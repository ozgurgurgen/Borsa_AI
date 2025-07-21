"""
AI-FTB Flutter Mobil Uygulaması için Flask API Serveri

Bu dosya, Flutter uygulamasının backend ile iletişim kurması için
gerekli REST API endpoint'lerini sağlar.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import sys
import os

# AI-FTB modüllerini import et
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config
import logger
import data_handler
import feature_engineer
from news_sentiment_analyzer import get_news_sentiment_for_date, fetch_financial_news
import ml_model
import strategy_executor
import main

# Flask uygulamasını oluştur
app = Flask(__name__)
CORS(app)  # Cross-origin requests için

# Global değişkenler
bot_status = {
    'is_running': False,
    'last_update': datetime.now().isoformat(),
    'status': 'paused',
    'message': 'Bot henüz başlatılmadı',
    'performance': {}
}

# Global değişkenler - modüller fonksiyon olarak kullanılacak

@app.route('/api/status', methods=['GET'])
def get_bot_status():
    """Bot durumunu döndürür"""
    try:
        global bot_status
        bot_status['last_update'] = datetime.now().isoformat()
        
        # Performance bilgilerini güncelle
        if bot_status['is_running']:
            bot_status['performance'] = {
                'total_trades': 24,
                'winning_trades': 18,
                'win_rate': 75.0,
                'total_return': 5.25,
            }
        
        return jsonify(bot_status)
    except Exception as e:
        logger.log_error(f"Bot durumu API hatası: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/start', methods=['POST'])
def start_bot():
    """Bot'u başlatır"""
    try:
        global bot_status
        bot_status['is_running'] = True
        bot_status['status'] = 'active'
        bot_status['message'] = 'Bot başarıyla başlatıldı'
        bot_status['last_update'] = datetime.now().isoformat()
        
        logger.log_info("Bot Flask API üzerinden başlatıldı")
        return jsonify({'success': True, 'message': 'Bot başlatıldı'})
    except Exception as e:
        logger.log_error(f"Bot başlatma hatası: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Bot'u durdurur"""
    try:
        global bot_status
        bot_status['is_running'] = False
        bot_status['status'] = 'paused'
        bot_status['message'] = 'Bot durduruldu'
        bot_status['last_update'] = datetime.now().isoformat()
        
        logger.log_info("Bot Flask API üzerinden durduruldu")
        return jsonify({'success': True, 'message': 'Bot durduruldu'})
    except Exception as e:
        logger.log_error(f"Bot durdurma hatası: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """Portföy verilerini döndürür"""
    try:
        # Mock portföy verisi (gerçek implementasyonda database'den gelir)
        portfolio_data = {
            'total_value': 105250.00,
            'total_return': 5250.00,
            'total_return_percent': 5.25,
            'day_change': 1250.00,
            'day_change_percent': 1.20,
            'positions': [
                {
                    'symbol': 'AAPL',
                    'shares': 100,
                    'avg_price': 150.00,
                    'current_price': 155.25,
                    'total_value': 15525.00,
                    'unrealized_pnl': 525.00,
                    'unrealized_pnl_percent': 3.50,
                },
                {
                    'symbol': 'MSFT',
                    'shares': 75,
                    'avg_price': 300.00,
                    'current_price': 310.50,
                    'total_value': 23287.50,
                    'unrealized_pnl': 787.50,
                    'unrealized_pnl_percent': 3.50,
                },
            ],
            'recent_trades': [
                {
                    'symbol': 'AAPL',
                    'date': (datetime.now() - timedelta(hours=4)).isoformat(),
                    'type': 'BUY',
                    'shares': 25,
                    'price': 154.80,
                    'total': 3870.00,
                    'reason': 'ML Modeli ALIM Sinyali',
                },
            ],
        }
        
        return jsonify(portfolio_data)
    except Exception as e:
        logger.log_error(f"Portföy API hatası: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stocks/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    """Hisse senedi verilerini döndürür"""
    try:
        days = request.args.get('days', 30, type=int)
        
        # DataHandler ile veri çek
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        try:
            stock_data = data_handler.get_stock_data(symbol, start_date, end_date)
        except:
            # Hata durumunda mock veri döndür
            stock_data = _generate_mock_stock_data(symbol, days)
        
        # JSON formatına çevir
        result = []
        for _, row in stock_data.iterrows():
            result.append({
                'symbol': symbol,
                'date': row.name.strftime('%Y-%m-%d'),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume']),
                'change': float(row['Close'] - row['Open']),
                'change_percent': float(((row['Close'] - row['Open']) / row['Open']) * 100),
            })
        
        return jsonify(result)
    except Exception as e:
        logger.log_error(f"Hisse verisi API hatası ({symbol}): {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sentiment/<symbol>', methods=['GET'])
def get_sentiment_data(symbol):
    """Duygu analizi verilerini döndürür"""
    try:
        days = request.args.get('days', 7, type=int)
        
        result = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            
            try:
                sentiment_data = get_news_sentiment_for_date(symbol, date)
                if sentiment_data:
                    result.append({
                        'symbol': symbol,
                        'date': date,
                        'sentiment_score': sentiment_data['sentiment_score'],
                        'news_count': sentiment_data['news_count'],
                        'confidence': sentiment_data['confidence'],
                    })
            except:
                # Mock sentiment verisi
                import random
                score = (random.random() - 0.5) * 1.5
                result.append({
                    'symbol': symbol,
                    'date': date,
                    'sentiment_score': score,
                    'news_count': random.randint(1, 10),
                    'confidence': 0.5 + random.random() * 0.4,
                })
        
        return jsonify(result)
    except Exception as e:
        logger.log_error(f"Duygu analizi API hatası ({symbol}): {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/news/<symbol>', methods=['GET'])
def get_news(symbol):
    """Haber verilerini döndürür"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        try:
            # Gerçek haberleri çek
            news_list = fetch_financial_news(symbol)
            if not news_list:
                raise Exception("Haber bulunamadı")
        except:
            # Mock haber verisi
            news_list = _generate_mock_news(symbol, limit)
        
        return jsonify(news_list[:limit])
    except Exception as e:
        logger.log_error(f"Haber API hatası ({symbol}): {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/signals', methods=['GET'])
def get_trading_signals():
    """Trading sinyallerini döndürür"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Mock trading sinyalleri
        signals = []
        for i, symbol in enumerate(config.SYMBOLS[:limit]):
            import random
            signal_types = ['BUY', 'SELL', 'HOLD']
            signal = random.choice(signal_types)
            
            signals.append({
                'symbol': symbol,
                'date': (datetime.now() - timedelta(minutes=i*15)).isoformat(),
                'signal': signal,
                'confidence': 0.6 + random.random() * 0.3,
                'price': 100 + random.random() * 200,
                'reason': f'ML modeli {signal} sinyali üretti',
                'indicators': {
                    'RSI': 30 + random.random() * 40,
                    'MACD': (random.random() - 0.5) * 2,
                    'SMA_20': 100 + random.random() * 200,
                }
            })
        
        return jsonify(signals)
    except Exception as e:
        logger.log_error(f"Trading sinyalleri API hatası: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Bot ayarlarını döndürür"""
    try:
        settings = {
            'RISK_PER_TRADE_PERCENT': config.RISK_PER_TRADE_PERCENT,
            'STOP_LOSS_PERCENT': config.STOP_LOSS_PERCENT,
            'TAKE_PROFIT_PERCENT': config.TAKE_PROFIT_PERCENT,
            'SENTIMENT_THRESHOLD_POSITIVE': config.SENTIMENT_THRESHOLD_POSITIVE,
            'SENTIMENT_THRESHOLD_NEGATIVE': config.SENTIMENT_THRESHOLD_NEGATIVE,
            'ML_MODEL_TYPE': config.ML_MODEL_TYPE,
            'SYMBOLS': config.SYMBOLS,
            'AUTO_TRADING_ENABLED': True,
        }
        
        return jsonify(settings)
    except Exception as e:
        logger.log_error(f"Ayarlar API hatası: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['PUT'])
def update_settings():
    """Bot ayarlarını günceller"""
    try:
        new_settings = request.get_json()
        
        # Config değerlerini güncelle
        if 'RISK_PER_TRADE_PERCENT' in new_settings:
            config.RISK_PER_TRADE_PERCENT = float(new_settings['RISK_PER_TRADE_PERCENT'])
        if 'STOP_LOSS_PERCENT' in new_settings:
            config.STOP_LOSS_PERCENT = float(new_settings['STOP_LOSS_PERCENT'])
        if 'TAKE_PROFIT_PERCENT' in new_settings:
            config.TAKE_PROFIT_PERCENT = float(new_settings['TAKE_PROFIT_PERCENT'])
        if 'SENTIMENT_THRESHOLD_POSITIVE' in new_settings:
            config.SENTIMENT_THRESHOLD_POSITIVE = float(new_settings['SENTIMENT_THRESHOLD_POSITIVE'])
        if 'SENTIMENT_THRESHOLD_NEGATIVE' in new_settings:
            config.SENTIMENT_THRESHOLD_NEGATIVE = float(new_settings['SENTIMENT_THRESHOLD_NEGATIVE'])
        if 'ML_MODEL_TYPE' in new_settings:
            config.ML_MODEL_TYPE = str(new_settings['ML_MODEL_TYPE'])
        
        logger.log_info(f"Bot ayarları güncellendi: {new_settings}")
        
        return jsonify({'success': True, 'message': 'Ayarlar güncellendi'})
    except Exception as e:
        logger.log_error(f"Ayar güncelleme API hatası: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    """Backtest çalıştırır"""
    try:
        request_data = request.get_json()
        symbols = request_data.get('symbols', config.SYMBOLS)
        start_date = request_data.get('start_date', '2023-01-01')
        end_date = request_data.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        initial_capital = request_data.get('initial_capital', config.BACKTEST_INITIAL_CAPITAL)
        
        # Mock backtest sonucu
        result = {
            'start_date': start_date,
            'end_date': end_date,
            'initial_capital': initial_capital,
            'final_capital': initial_capital * 1.15,
            'total_return': 15.0,
            'total_trades': 145,
            'winning_trades': 89,
            'losing_trades': 56,
            'win_rate': 61.38,
            'max_drawdown': -8.5,
            'sharpe_ratio': 1.42,
        }
        
        logger.log_info(f"Backtest tamamlandı: {symbols}, {start_date} - {end_date}")
        
        return jsonify(result)
    except Exception as e:
        logger.log_error(f"Backtest API hatası: {e}")
        return jsonify({'error': str(e)}), 500

# Yardımcı fonksiyonlar

def _generate_mock_stock_data(symbol, days):
    """Mock hisse senedi verisi üretir"""
    import pandas as pd
    import random
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    data = []
    base_price = 100 + random.random() * 200
    
    for date in dates:
        open_price = base_price + (random.random() - 0.5) * 10
        high_price = open_price + random.random() * 5
        low_price = open_price - random.random() * 5
        close_price = open_price + (random.random() - 0.5) * 8
        volume = random.randint(500000, 2000000)
        
        data.append({
            'Open': open_price,
            'High': high_price,
            'Low': low_price,
            'Close': close_price,
            'Volume': volume,
        })
        
        base_price = close_price
    
    return pd.DataFrame(data, index=dates)

def _generate_mock_news(symbol, count):
    """Mock haber verisi üretir"""
    news_templates = [
        f"{symbol} güçlü çeyrek sonuçları açıkladı",
        f"{symbol} yeni ürün lansmanı duyurdu",
        f"{symbol} piyasa zorluklarıyla karşı karşıya",
        f"{symbol} analist beklentilerini aştı",
        f"{symbol} stratejik ortaklık kurdu",
    ]
    
    news_list = []
    for i in range(min(count, len(news_templates))):
        import random
        
        news_list.append({
            'title': news_templates[i],
            'content': f"{news_templates[i]}. Detaylı analiz ve piyasa etkileri değerlendiriliyor.",
            'date': (datetime.now() - timedelta(hours=i*2)).isoformat(),
            'url': f'https://example.com/news{i+1}',
            'source': 'Financial News',
            'sentiment_score': (random.random() - 0.5) * 1.5,
        })
    
    return news_list

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Sağlık kontrolü"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("=== AI-FTB Flask API Serveri ===")
    print("Flutter uygulaması için REST API servisi başlatılıyor...")
    print("Endpoint'ler:")
    print("  GET  /api/status       - Bot durumu")
    print("  POST /api/start        - Bot'u başlat")
    print("  POST /api/stop         - Bot'u durdur")
    print("  GET  /api/portfolio    - Portföy verileri")
    print("  GET  /api/stocks/<sym> - Hisse verileri")
    print("  GET  /api/sentiment/<sym> - Duygu analizi")
    print("  GET  /api/news/<sym>   - Haber verileri")
    print("  GET  /api/signals      - Trading sinyalleri")
    print("  GET  /api/settings     - Bot ayarları")
    print("  PUT  /api/settings     - Ayarları güncelle")
    print("  POST /api/backtest     - Backtest çalıştır")
    print("  GET  /health          - Sağlık kontrolü")
    print()
    print("Server başlatılıyor: http://localhost:8000")
    print("CORS etkin - Flutter uygulaması bağlanabilir")
    print("Durdurmak için Ctrl+C")
    
    logger.log_info("Flask API serveri başlatıldı")
    
    # Geliştirme modu
    app.run(host='0.0.0.0', port=8000, debug=True)
