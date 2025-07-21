"""
AI-FTB (AI-Powered Financial Trading Bot) Main Module

Bu dosya, projenin ana yürütücü dosyasıdır. Yukarıdaki modülleri sırayla çağırarak 
botun akışını yönetir (veri çekme, model eğitimi, strateji çalıştırma, backtest).
"""

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime
import traceback

# Proje modüllerini import et
import config
import logger
import data_handler
import feature_engineer
import news_sentiment_analyzer
import ml_model
import strategy_executor
import backtester


def run_bot_training_and_backtest(symbols=None, start_date=None, end_date=None):
    """
    Botun eğitim ve backtest sürecini yönetir. Sırasıyla veri çekme, özellik 
    mühendisliği, model eğitimi, backtest yapma adımlarını çalıştırır.
    
    Args:
        symbols (list): İşlem yapılacak semboller
        start_date (str): Veri başlangıç tarihi
        end_date (str): Veri bitiş tarihi
    
    Returns:
        dict: Süreç sonuçları
        None: Hata durumunda
        
    Raises:
        Exception: Ana süreç hatalarında
    """
    try:
        logger.log_info("=== AI-FTB Bot Eğitim ve Backtest Süreci Başlıyor ===")
        
        # Parametreleri config'ten al
        if symbols is None:
            symbols = config.SYMBOLS
        if start_date is None:
            start_date = config.HISTORICAL_DATA_START_DATE
        if end_date is None:
            end_date = config.HISTORICAL_DATA_END_DATE
            
        logger.log_info(f"Semboller: {symbols}")
        logger.log_info(f"Tarih aralığı: {start_date} - {end_date}")
        
        results = {}
        
        # Her sembol için işlem yap
        for symbol in symbols:
            logger.log_info(f"\\n{'='*50}")
            logger.log_info(f"Sembol işleniyor: {symbol}")
            logger.log_info(f"{'='*50}")
            
            try:
                # 1. Veri Çekme
                logger.log_info(f"1. {symbol} için tarihsel veri çekiliyor...")
                raw_data = data_handler.fetch_historical_data(symbol, start_date, end_date)
                
                if raw_data is None or len(raw_data) < 100:
                    logger.log_warning(f"{symbol} için yetersiz veri, atlanıyor")
                    continue
                    
                logger.log_info(f"✅ Veri çekildi: {len(raw_data)} satır")
                
                # Veriyi kaydet
                data_handler.save_data(raw_data, 'raw_data', symbol)
                
                # 2. Teknik Göstergeler
                logger.log_info(f"2. {symbol} için teknik göstergeler hesaplanıyor...")
                enhanced_data = feature_engineer.add_technical_indicators(raw_data)
                
                if enhanced_data is None:
                    logger.log_error(f"{symbol} için teknik göstergeler hesaplanamadı")
                    continue
                    
                logger.log_info(f"✅ Teknik göstergeler eklendi: {len(enhanced_data.columns)} sütun")
                
                # 3. Hedef Değişken
                logger.log_info(f"3. {symbol} için hedef değişken oluşturuluyor...")
                enhanced_data = feature_engineer.create_target_variable(enhanced_data)
                
                if 'Target' not in enhanced_data.columns:
                    logger.log_error(f"{symbol} için hedef değişken oluşturulamadı")
                    continue
                    
                # 4. Özellik Ölçeklendirme
                logger.log_info(f"4. {symbol} için özellik ölçeklendirme...")
                normalized_data, scaler = feature_engineer.normalize_features(
                    enhanced_data, 
                    save_scaler=True, 
                    symbol=symbol
                )
                
                if normalized_data is None:
                    logger.log_error(f"{symbol} için özellik ölçeklendirme başarısız")
                    continue
                    
                logger.log_info(f"✅ Özellik ölçeklendirme tamamlandı")
                
                # Ölçeklendirilmiş veriyi kaydet
                data_handler.save_data(normalized_data, 'processed_data', symbol)
                
                # 5. ML Veri Hazırlama
                logger.log_info(f"5. {symbol} için ML verisi hazırlanıyor...")
                ml_data = ml_model.prepare_data_for_ml(normalized_data)
                
                if ml_data is None:
                    logger.log_error(f"{symbol} için ML verisi hazırlanamadı")
                    continue
                    
                X_train, X_test, y_train, y_test, feature_names = ml_data
                logger.log_info(f"✅ ML verisi hazırlandı: Eğitim={len(X_train)}, Test={len(X_test)}")
                
                # 6. Model Eğitimi
                logger.log_info(f"6. {symbol} için model eğitiliyor...")
                model = ml_model.train_model(X_train, y_train)
                
                if model is None:
                    logger.log_error(f"{symbol} için model eğitimi başarısız")
                    continue
                    
                logger.log_info(f"✅ Model eğitimi tamamlandı")
                
                # 7. Model Değerlendirme
                logger.log_info(f"7. {symbol} için model değerlendiriliyor...")
                performance = ml_model.evaluate_model(model, X_test, y_test)
                
                if performance is None:
                    logger.log_warning(f"{symbol} için model değerlendirme başarısız")
                    performance = {'accuracy': 0}
                    
                logger.log_info(f"✅ Model performansı: Accuracy={performance.get('accuracy', 0):.3f}")
                
                # 8. Model Kaydetme
                model_metadata = {
                    'symbol': symbol,
                    'feature_names': feature_names,
                    'performance': performance,
                    'training_data_size': len(X_train),
                    'training_date': datetime.now().isoformat()
                }
                
                ml_model.save_model(model, 'trained_model', symbol, model_metadata)
                logger.log_info(f"✅ Model kaydedildi")
                
                # 9. Backtest
                logger.log_info(f"8. {symbol} için backtest çalıştırılıyor...")
                backtest_result = backtester.run_backtest(
                    normalized_data,
                    model,
                    initial_capital=config.BACKTEST_INITIAL_CAPITAL
                )
                
                if backtest_result is None:
                    logger.log_error(f"{symbol} için backtest başarısız")
                    continue
                    
                logger.log_info(f"✅ Backtest tamamlandı: Getiri={backtest_result['total_return']:.1f}%")
                
                # 10. Performans Raporu
                logger.log_info(f"9. {symbol} için performans raporu oluşturuluyor...")
                performance_report = backtester.generate_performance_report(
                    backtest_result['trade_log'],
                    backtest_result['initial_capital'],
                    backtest_result['portfolio_history']
                )
                
                if performance_report:
                    logger.log_info(f"✅ Performans raporu: Not={performance_report.get('performance_grade', 'N/A')}")
                else:
                    logger.log_warning(f"{symbol} için performans raporu oluşturulamadı")
                    
                # Sonuçları kaydet
                results[symbol] = {
                    'data_rows': len(raw_data),
                    'model_accuracy': performance.get('accuracy', 0),
                    'backtest_return': backtest_result['total_return'],
                    'total_trades': backtest_result['total_trades'],
                    'performance_grade': performance_report.get('performance_grade', 'N/A') if performance_report else 'N/A',
                    'max_drawdown': performance_report.get('max_drawdown_percent', 0) if performance_report else 0,
                    'win_rate': performance_report.get('win_rate_percent', 0) if performance_report else 0
                }
                
                logger.log_info(f"✅ {symbol} işlemi tamamlandı")
                
            except Exception as e:
                logger.log_error(f"{symbol} işlemi sırasında hata: {e}", exc_info=True)
                results[symbol] = {'error': str(e)}
                continue
                
        # Genel özet
        logger.log_info(f"\\n{'='*60}")
        logger.log_info("GENEL ÖZET")
        logger.log_info(f"{'='*60}")
        
        successful_symbols = [s for s, r in results.items() if 'error' not in r]
        failed_symbols = [s for s, r in results.items() if 'error' in r]
        
        logger.log_info(f"Başarılı semboller ({len(successful_symbols)}): {successful_symbols}")
        if failed_symbols:
            logger.log_info(f"Başarısız semboller ({len(failed_symbols)}): {failed_symbols}")
            
        if successful_symbols:
            # En iyi performans
            best_symbol = max(successful_symbols, key=lambda s: results[s]['backtest_return'])
            best_return = results[best_symbol]['backtest_return']
            
            # Ortalama performans
            avg_return = np.mean([results[s]['backtest_return'] for s in successful_symbols])
            avg_accuracy = np.mean([results[s]['model_accuracy'] for s in successful_symbols])
            
            logger.log_info(f"En iyi performans: {best_symbol} ({best_return:+.1f}%)")
            logger.log_info(f"Ortalama getiri: {avg_return:+.1f}%")
            logger.log_info(f"Ortalama model doğruluğu: {avg_accuracy:.3f}")
            
        logger.log_info("=== Bot Eğitim ve Backtest Süreci Tamamlandı ===")
        
        return results
        
    except Exception as e:
        logger.log_error(f"Ana süreç hatası: {e}", exc_info=True)
        return None


def run_live_trading():
    """
    Canlı ticaret modunun ana giriş noktası.
    Şu an için placeholder - gelecekte gerçek broker entegrasyonu eklenecek.
    
    Returns:
        bool: Başarı durumu
    """
    try:
        logger.log_info("=== AI-FTB Canlı Ticaret Modu ===")
        logger.log_warning("Canlı ticaret modu henüz geliştirilmemiştir")
        logger.log_info("Bu modda şunlar yapılacak:")
        logger.log_info("1. Gerçek zamanlı veri çekme")
        logger.log_info("2. Kaydedilmiş modelleri yükleme")
        logger.log_info("3. Anlık sinyal üretme")
        logger.log_info("4. Risk yönetimi kontrolleri")
        logger.log_info("5. Broker API entegrasyonu")
        logger.log_info("6. Portföy izleme")
        
        # Gelecekte buraya canlı ticaret mantığı eklenecek:
        # - Real-time data feeds
        # - Model predictions
        # - Order management
        # - Position monitoring
        # - Risk controls
        
        return True
        
    except Exception as e:
        logger.log_error(f"Canlı ticaret hatası: {e}", exc_info=True)
        return False


def run_analysis_mode(symbol, analysis_type='full'):
    """
    Belirli bir sembol için analiz modu.
    
    Args:
        symbol (str): Analiz edilecek sembol
        analysis_type (str): Analiz tipi ('full', 'technical', 'sentiment', 'prediction')
    
    Returns:
        dict: Analiz sonuçları
    """
    try:
        logger.log_info(f"=== {symbol} Analiz Modu ({analysis_type}) ===")
        
        results = {}
        
        if analysis_type in ['full', 'technical']:
            # Teknik analiz
            logger.log_info("Teknik analiz yapılıyor...")
            data = data_handler.fetch_historical_data(symbol)
            if data is not None:
                enhanced_data = feature_engineer.add_technical_indicators(data)
                if enhanced_data is not None:
                    results['technical_analysis'] = {
                        'current_rsi': enhanced_data['RSI'].iloc[-1],
                        'current_macd': enhanced_data['MACD_Hist'].iloc[-1],
                        'trend_sma': 'UP' if enhanced_data['SMA_20'].iloc[-1] > enhanced_data['SMA_50'].iloc[-1] else 'DOWN'
                    }
                    logger.log_info(f"Teknik analiz tamamlandı: RSI={results['technical_analysis']['current_rsi']:.1f}")
                    
        if analysis_type in ['full', 'sentiment']:
            # Duygu analizi
            logger.log_info("Duygu analizi yapılıyor...")
            today = datetime.now().strftime('%Y-%m-%d')
            sentiment_data = news_sentiment_analyzer.get_news_sentiment_for_date(symbol, today)
            if sentiment_data:
                results['sentiment_analysis'] = sentiment_data
                logger.log_info(f"Duygu analizi tamamlandı: Skor={sentiment_data['sentiment_score']:.3f}")
                
        if analysis_type in ['full', 'prediction']:
            # Model tahmini
            logger.log_info("Model tahmini yapılıyor...")
            try:
                model_result = ml_model.load_model('trained_model', symbol)
                if model_result:
                    model, metadata = model_result
                    # Son veri ile tahmin yap
                    data = data_handler.load_data('processed_data', symbol)
                    if data is not None and len(data) > 0:
                        feature_names = metadata.get('feature_names', config.ML_FEATURES)
                        last_features = data[feature_names].iloc[-1:].fillna(0)
                        prediction = model.predict(last_features)[0]
                        
                        if hasattr(model, 'predict_proba'):
                            probability = model.predict_proba(last_features)[0, 1]
                        else:
                            probability = float(prediction)
                            
                        results['prediction'] = {
                            'signal': 'BUY' if prediction == 1 else 'SELL',
                            'probability': probability,
                            'confidence': 'HIGH' if abs(probability - 0.5) > 0.3 else 'LOW'
                        }
                        logger.log_info(f"Model tahmini: {results['prediction']['signal']} (P={probability:.3f})")
            except Exception as e:
                logger.log_warning(f"Model tahmini yapılamadı: {e}")
                
        return results
        
    except Exception as e:
        logger.log_error(f"Analiz modu hatası: {e}", exc_info=True)
        return {}


def main():
    """
    Ana program giriş noktası. Komut satırı argümanlarını işler ve 
    ilgili modu çalıştırır.
    """
    try:
        logger.log_info("AI-FTB Bot başlatılıyor...")
        
        # Komut satırı argümanlarını kontrol et
        mode = 'training'  # Varsayılan mod
        
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()
            
        logger.log_info(f"Çalışma modu: {mode}")
        
        if mode == 'training' or mode == 'backtest':
            # Eğitim ve backtest modu
            results = run_bot_training_and_backtest()
            
            if results:
                successful_count = len([r for r in results.values() if 'error' not in r])
                logger.log_info(f"Süreç tamamlandı: {successful_count}/{len(results)} sembol başarılı")
            else:
                logger.log_error("Eğitim süreci başarısız")
                
        elif mode == 'live':
            # Canlı ticaret modu
            run_live_trading()
            
        elif mode == 'analysis':
            # Analiz modu
            symbol = sys.argv[2] if len(sys.argv) > 2 else 'AAPL'
            analysis_type = sys.argv[3] if len(sys.argv) > 3 else 'full'
            
            results = run_analysis_mode(symbol, analysis_type)
            print(f"\\n{symbol} analiz sonuçları:")
            for key, value in results.items():
                print(f"{key}: {value}")
                
        elif mode == 'test':
            # Test modu - tüm modülleri test et
            logger.log_info("Test modu çalıştırılıyor...")
            test_all_modules()
            
        else:
            print("Kullanım:")
            print("python main.py [training|live|analysis|test]")
            print("  training  - Model eğitimi ve backtest (varsayılan)")
            print("  live      - Canlı ticaret modu")
            print("  analysis  - Tekil sembol analizi")
            print("  test      - Tüm modülleri test et")
            
    except KeyboardInterrupt:
        logger.log_info("Program kullanıcı tarafından durduruldu")
    except Exception as e:
        logger.log_error(f"Ana program hatası: {e}", exc_info=True)
        print(f"Hata: {e}")
        return 1
        
    return 0


def test_all_modules():
    """
    Tüm modüllerin temel işlevlerini test eder.
    """
    try:
        logger.log_info("=== TÜM MODÜL TESTLERİ ===")
        
        test_results = {}
        
        # Config testi
        try:
            logger.log_info("Config modülü test ediliyor...")
            assert len(config.SYMBOLS) > 0
            assert config.RISK_PER_TRADE_PERCENT > 0
            test_results['config'] = 'PASS'
            logger.log_info("✅ Config testi başarılı")
        except Exception as e:
            test_results['config'] = f'FAIL: {e}'
            logger.log_error(f"❌ Config testi başarısız: {e}")
            
        # Data handler testi
        try:
            logger.log_info("Data handler test ediliyor...")
            test_data = data_handler.fetch_historical_data('AAPL', '2023-01-01', '2023-01-31')
            assert test_data is not None
            test_results['data_handler'] = 'PASS'
            logger.log_info("✅ Data handler testi başarılı")
        except Exception as e:
            test_results['data_handler'] = f'FAIL: {e}'
            logger.log_error(f"❌ Data handler testi başarısız: {e}")
            
        # Feature engineer testi
        try:
            logger.log_info("Feature engineer test ediliyor...")
            if 'data_handler' in test_results and test_results['data_handler'] == 'PASS':
                enhanced = feature_engineer.add_technical_indicators(test_data)
                assert enhanced is not None
                assert 'RSI' in enhanced.columns
                test_results['feature_engineer'] = 'PASS'
                logger.log_info("✅ Feature engineer testi başarılı")
            else:
                test_results['feature_engineer'] = 'SKIP: Data handler başarısız'
        except Exception as e:
            test_results['feature_engineer'] = f'FAIL: {e}'
            logger.log_error(f"❌ Feature engineer testi başarısız: {e}")
            
        # Test sonuçlarını göster
        logger.log_info("\\n=== TEST SONUÇLARI ===")
        for module, result in test_results.items():
            status_icon = "✅" if result == 'PASS' else "❌" if 'FAIL' in result else "⏭️"
            logger.log_info(f"{status_icon} {module}: {result}")
            
    except Exception as e:
        logger.log_error(f"Modül test hatası: {e}", exc_info=True)


if __name__ == "__main__":
    """
    Program giriş noktası
    """
    exit_code = main()
    sys.exit(exit_code)
