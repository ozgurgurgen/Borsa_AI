"""
AI-FTB (AI-Powered Financial Trading Bot) Backtester Module

Bu modül, geliştirilen stratejinin (ML + Haber + Karar Mantığı + Risk Yönetimi) 
geçmiş veriler üzerinde simülasyonunu yaparak performansını değerlendirir.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import config
import logger


def run_backtest(data_dataframe, ml_model_instance, sentiment_analyzer_instance=None, 
                initial_capital=None, start_date=None, end_date=None):
    """
    Geçmiş veri üzerinde strateji backtesti yapar. Her adımda ML modelinden 
    sinyal alır, haber duygu skorunu alır ve strategy_executor ile kararları uygular.
    
    Args:
        data_dataframe (pandas.DataFrame): Teknik göstergeler eklenmiş tarihsel veri
        ml_model_instance: Eğitilmiş ML modeli
        sentiment_analyzer_instance: Duygu analizi instance'ı (opsiyonel)
        initial_capital (float): Başlangıç sermayesi
        start_date (str): Backtest başlangıç tarihi
        end_date (str): Backtest bitiş tarihi
    
    Returns:
        dict: {
            'trade_log': pandas.DataFrame,
            'portfolio_history': pandas.DataFrame,
            'final_portfolio_value': float,
            'total_return': float,
            'total_trades': int
        }
        None: Hata durumunda
        
    Raises:
        Exception: Backtest simülasyonu hatalarında
    """
    try:
        # Parametreleri ayarla
        if initial_capital is None:
            initial_capital = config.BACKTEST_INITIAL_CAPITAL
            
        commission_rate = config.BACKTEST_COMMISSION
        
        logger.log_info(f"Backtest başlıyor: Sermaye=${initial_capital:,.0f}, Komisyon=%{commission_rate*100:.1f}")
        
        # Veriyi temizle ve tarih aralığını filtrele
        data = data_dataframe.copy().dropna()
        
        if start_date:
            data = data[data.index >= start_date]
        if end_date:
            data = data[data.index <= end_date]
            
        if len(data) < 50:
            logger.log_error("Backtest için yetersiz veri")
            return None
            
        logger.log_info(f"Backtest periyodu: {data.index.min()} - {data.index.max()} ({len(data)} gün)")
        
        # Backtest değişkenleri
        portfolio_value = initial_capital
        cash = initial_capital
        positions = {}  # {symbol: {'shares': int, 'entry_price': float, 'entry_date': date}}
        trade_log = []
        portfolio_history = []
        
        # ML özelliklerini hazırla
        ml_features = config.ML_FEATURES.copy()
        scaled_features = [f"{feature}_scaled" for feature in ml_features]
        all_features = ml_features + scaled_features
        available_features = [f for f in all_features if f in data.columns]
        
        if not available_features:
            logger.log_error("ML özellikleri bulunamadı")
            return None
            
        # Her gün için simülasyon
        for i, (date, row) in enumerate(data.iterrows()):
            current_price = row['Close']
            
            # İlk birkaç günde yeterli veri olmayabilir
            if i < max(20, len(available_features)):
                continue
                
            try:
                # ML tahmini yap
                feature_vector = row[available_features].values.reshape(1, -1)
                
                # NaN kontrolü
                if np.isnan(feature_vector).any():
                    continue
                    
                ml_prediction = ml_model_instance.predict(feature_vector)[0]
                
                # Olasılık tahmini (varsa)
                if hasattr(ml_model_instance, 'predict_proba'):
                    ml_probability = ml_model_instance.predict_proba(feature_vector)[0, 1]
                else:
                    ml_probability = float(ml_prediction)
                    
                # Duygu skoru al (simülasyon için basit yöntem)
                if sentiment_analyzer_instance:
                    # Gerçek uygulamada sentiment_analyzer_instance.get_news_sentiment_for_date(symbol, date) çağrılır
                    sentiment_score = _simulate_sentiment_score(date, current_price, i)
                else:
                    sentiment_score = _simulate_sentiment_score(date, current_price, i)
                    
                # Ek faktörler
                additional_factors = {
                    'volatility': row.get('Volatility', 0.02),
                    'volume_ratio': row.get('Volume_Ratio', 1.0)
                }
                
                # Strategy executor'dan karar al
                from strategy_executor import generate_trade_decision, calculate_position_size, apply_risk_management
                
                trade_decision = generate_trade_decision(
                    ml_prediction,
                    sentiment_score,
                    current_price,
                    portfolio_value,
                    additional_factors
                )
                
                decision = trade_decision['decision']
                confidence = trade_decision['confidence']
                
                # Mevcut pozisyonlar için risk yönetimi
                for symbol, position in list(positions.items()):
                    risk_result = apply_risk_management(
                        decision,
                        position['entry_price'],
                        current_price,
                        position
                    )
                    
                    if risk_result['action'] in ['CLOSE_STOP_LOSS', 'CLOSE_TAKE_PROFIT']:
                        # Pozisyonu kapat
                        shares = position['shares']
                        entry_price = position['entry_price']
                        
                        # Satış işlemi
                        sale_value = shares * current_price
                        commission = sale_value * commission_rate
                        net_proceeds = sale_value - commission
                        
                        cash += net_proceeds
                        
                        # Trade log kaydet
                        pnl = net_proceeds - (shares * entry_price)
                        pnl_percent = (pnl / (shares * entry_price)) * 100
                        
                        trade_log.append({
                            'date': date,
                            'symbol': symbol,
                            'action': 'SELL',
                            'shares': shares,
                            'price': current_price,
                            'value': sale_value,
                            'commission': commission,
                            'pnl': pnl,
                            'pnl_percent': pnl_percent,
                            'reason': risk_result['reason'],
                            'portfolio_value': cash
                        })
                        
                        logger.log_info(f"{date}: {risk_result['action']} - {symbol} {shares} hisse ${current_price:.2f} (P&L: ${pnl:.2f})")
                        
                        # Pozisyonu sil
                        del positions[symbol]
                        
                # Yeni pozisyon açma
                if decision in ['BUY', 'SELL'] and confidence >= 0.5:
                    position_calc = calculate_position_size(
                        portfolio_value,
                        current_price,
                        decision_confidence=confidence
                    )
                    
                    if position_calc and position_calc['shares'] > 0:
                        shares = position_calc['shares']
                        investment = position_calc['investment_amount']
                        commission = investment * commission_rate
                        total_cost = investment + commission
                        
                        if total_cost <= cash and 'AAPL' not in positions:  # Basit sembol örneği
                            # Pozisyon aç
                            cash -= total_cost
                            
                            positions['AAPL'] = {
                                'shares': shares,
                                'entry_price': current_price,
                                'entry_date': date,
                                'type': 'LONG' if decision == 'BUY' else 'SHORT'
                            }
                            
                            trade_log.append({
                                'date': date,
                                'symbol': 'AAPL',
                                'action': decision,
                                'shares': shares,
                                'price': current_price,
                                'value': investment,
                                'commission': commission,
                                'pnl': 0,
                                'pnl_percent': 0,
                                'reason': trade_decision['reasoning'],
                                'portfolio_value': cash
                            })
                            
                            logger.log_debug(f"{date}: {decision} - AAPL {shares} hisse ${current_price:.2f} (Güven: {confidence:.2f})")
                            
                # Portföy değerini hesapla
                total_position_value = sum(pos['shares'] * current_price for pos in positions.values())
                portfolio_value = cash + total_position_value
                
                # Portföy geçmişi kaydet
                portfolio_history.append({
                    'date': date,
                    'cash': cash,
                    'positions_value': total_position_value,
                    'total_value': portfolio_value,
                    'num_positions': len(positions),
                    'daily_return': ((portfolio_value / initial_capital) - 1) * 100
                })
                
            except Exception as e:
                logger.log_error(f"Backtest günlük işlem hatası ({date}): {e}")
                continue
                
        # Tüm pozisyonları kapat (backtest sonu)
        final_date = data.index[-1]
        final_price = data['Close'].iloc[-1]
        
        for symbol, position in positions.items():
            shares = position['shares']
            sale_value = shares * final_price
            commission = sale_value * commission_rate
            net_proceeds = sale_value - commission
            
            cash += net_proceeds
            
            pnl = net_proceeds - (shares * position['entry_price'])
            pnl_percent = (pnl / (shares * position['entry_price'])) * 100
            
            trade_log.append({
                'date': final_date,
                'symbol': symbol,
                'action': 'SELL',
                'shares': shares,
                'price': final_price,
                'value': sale_value,
                'commission': commission,
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'reason': 'Backtest sonu pozisyon kapatma',
                'portfolio_value': cash
            })
            
        # Sonuçları DataFrame'e çevir
        trade_log_df = pd.DataFrame(trade_log)
        portfolio_history_df = pd.DataFrame(portfolio_history)
        
        if not portfolio_history_df.empty:
            portfolio_history_df = portfolio_history_df.set_index('date')
            
        final_portfolio_value = cash
        total_return = ((final_portfolio_value / initial_capital) - 1) * 100
        
        result = {
            'trade_log': trade_log_df,
            'portfolio_history': portfolio_history_df,
            'final_portfolio_value': final_portfolio_value,
            'total_return': total_return,
            'total_trades': len(trade_log_df),
            'initial_capital': initial_capital
        }
        
        logger.log_info(f"Backtest tamamlandı: Final değer=${final_portfolio_value:,.0f}, Toplam getiri={total_return:.1f}%, İşlem sayısı={len(trade_log_df)}")
        
        return result
        
    except Exception as e:
        logger.log_error(f"Backtest hatası: {e}", exc_info=True)
        return None


def _simulate_sentiment_score(date, price, index):
    """
    Backtest için basit duygu skoru simülasyonu.
    
    Args:
        date: Tarih
        price: Fiyat
        index: Gün indeksi
    
    Returns:
        float: Simüle edilmiş duygu skoru
    """
    # Basit simülasyon: fiyat trendine ve rastgele faktöre dayalı
    np.random.seed(hash(str(date)) % 1000000)  # Deterministik ama varyasyonlu
    
    # Trend faktörü (son 5 günün trendi)
    trend_factor = np.sin(index / 10) * 0.3
    
    # Rastgele haber faktörü
    random_factor = np.random.normal(0, 0.2)
    
    # Fiyat momentum faktörü
    momentum_factor = (price % 10 - 5) / 50
    
    sentiment = np.clip(trend_factor + random_factor + momentum_factor, -1.0, 1.0)
    
    return sentiment


def generate_performance_report(trade_log, initial_capital, portfolio_history=None):
    """
    Trade log verisini kullanarak toplam kar/zarar, maksimum düşüş, işlem sayısı, 
    kazanma oranı, ortalama işlem karı/zararı gibi detaylı performans raporu oluşturur.
    
    Args:
        trade_log (pandas.DataFrame): İşlem günlüğü
        initial_capital (float): Başlangıç sermayesi
        portfolio_history (pandas.DataFrame): Portföy geçmişi
    
    Returns:
        dict: Performans metrikleri
        None: Hata durumunda
        
    Raises:
        Exception: Rapor hesaplama hatalarında
    """
    try:
        logger.log_info("Performans raporu oluşturuluyor...")
        
        if trade_log.empty:
            logger.log_warning("Boş trade log, rapor oluşturulamadı")
            return None
            
        # Sadece kapanış işlemlerini al (PNL hesabı için)
        closing_trades = trade_log[trade_log['action'] == 'SELL'].copy()
        
        if closing_trades.empty:
            logger.log_warning("Kapanış işlemi bulunamadı")
            return {'total_trades': 0, 'total_return': 0}
            
        # Temel metrikler
        total_trades = len(closing_trades)
        winning_trades = len(closing_trades[closing_trades['pnl'] > 0])
        losing_trades = len(closing_trades[closing_trades['pnl'] < 0])
        
        total_pnl = closing_trades['pnl'].sum()
        total_commission = trade_log['commission'].sum()
        
        # Getiri metrikleri
        final_value = initial_capital + total_pnl - total_commission
        total_return_pct = ((final_value / initial_capital) - 1) * 100
        
        # İşlem istatistikleri
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        avg_win = closing_trades[closing_trades['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = closing_trades[closing_trades['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
        avg_trade = closing_trades['pnl'].mean()
        
        # Risk metrikleri
        largest_win = closing_trades['pnl'].max()
        largest_loss = closing_trades['pnl'].min()
        
        # Profit Factor (brüt kar / brüt zarar)
        gross_profit = closing_trades[closing_trades['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(closing_trades[closing_trades['pnl'] < 0]['pnl'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Portföy geçmişi analizi
        max_drawdown_pct = 0
        max_portfolio_value = initial_capital
        annualized_return = 0
        sharpe_ratio = 0
        volatility = 0
        
        if portfolio_history is not None and not portfolio_history.empty:
            # Maksimum düşüş hesaplama
            portfolio_values = portfolio_history['total_value']
            running_max = portfolio_values.expanding().max()
            drawdowns = (portfolio_values - running_max) / running_max * 100
            max_drawdown_pct = drawdowns.min()
            
            # Yıllık getiri
            days = len(portfolio_history)
            if days > 0:
                annualized_return = ((final_value / initial_capital) ** (365 / days) - 1) * 100
                
            # Günlük getiriler
            if 'daily_return' in portfolio_history.columns:
                daily_returns = portfolio_history['daily_return'].pct_change().dropna()
                if len(daily_returns) > 1:
                    volatility = daily_returns.std() * np.sqrt(252) * 100  # Yıllık volatilite
                    avg_daily_return = daily_returns.mean()
                    if volatility > 0:
                        sharpe_ratio = (avg_daily_return * 252) / (volatility / 100)
                        
        # Ay bazlı performans
        monthly_returns = _calculate_monthly_returns(trade_log, initial_capital)
        
        # Performans raporu
        performance_report = {
            # Temel metrikler
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return_dollar': total_pnl,
            'total_return_percent': total_return_pct,
            'total_commission': total_commission,
            'net_profit': total_pnl - total_commission,
            
            # İşlem istatistikleri
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate_percent': win_rate,
            
            # Ortalama işlem metrikleri
            'avg_trade': avg_trade,
            'avg_winning_trade': avg_win,
            'avg_losing_trade': avg_loss,
            'largest_winning_trade': largest_win,
            'largest_losing_trade': largest_loss,
            
            # Risk metrikleri
            'profit_factor': profit_factor,
            'max_drawdown_percent': max_drawdown_pct,
            'annualized_return_percent': annualized_return,
            'volatility_percent': volatility,
            'sharpe_ratio': sharpe_ratio,
            
            # Ek metrikler
            'gross_profit': gross_profit,
            'gross_loss': gross_loss,
            'monthly_returns': monthly_returns,
            
            # Performans değerlendirmesi
            'performance_grade': _calculate_performance_grade(total_return_pct, max_drawdown_pct, win_rate, sharpe_ratio)
        }
        
        # Raporu logla
        logger.log_info("=== BACKTEST PERFORMANS RAPORU ===")
        logger.log_info(f"Başlangıç Sermayesi: ${initial_capital:,.0f}")
        logger.log_info(f"Final Değer: ${final_value:,.0f}")
        logger.log_info(f"Toplam Getiri: {total_return_pct:+.2f}%")
        logger.log_info(f"Yıllık Getiri: {annualized_return:+.2f}%")
        logger.log_info(f"Maksimum Düşüş: {max_drawdown_pct:.2f}%")
        logger.log_info(f"Toplam İşlem: {total_trades}")
        logger.log_info(f"Kazanma Oranı: {win_rate:.1f}%")
        logger.log_info(f"Profit Factor: {profit_factor:.2f}")
        logger.log_info(f"Sharpe Ratio: {sharpe_ratio:.2f}")
        logger.log_info(f"Volatilite: {volatility:.1f}%")
        logger.log_info(f"Performans Notu: {performance_report['performance_grade']}")
        
        return performance_report
        
    except Exception as e:
        logger.log_error(f"Performans raporu hatası: {e}", exc_info=True)
        return None


def _calculate_monthly_returns(trade_log, initial_capital):
    """
    Aylık getiri hesaplama yardımcı fonksiyonu.
    
    Args:
        trade_log (pandas.DataFrame): İşlem günlüğü
        initial_capital (float): Başlangıç sermayesi
    
    Returns:
        dict: Aylık getiriler
    """
    try:
        if trade_log.empty:
            return {}
            
        trade_log['year_month'] = pd.to_datetime(trade_log['date']).dt.to_period('M')
        monthly_pnl = trade_log.groupby('year_month')['pnl'].sum()
        
        monthly_returns = {}
        for month, pnl in monthly_pnl.items():
            return_pct = (pnl / initial_capital) * 100
            monthly_returns[str(month)] = return_pct
            
        return monthly_returns
        
    except:
        return {}


def _calculate_performance_grade(total_return, max_drawdown, win_rate, sharpe_ratio):
    """
    Performans notunu hesaplar.
    
    Args:
        total_return (float): Toplam getiri yüzdesi
        max_drawdown (float): Maksimum düşüş yüzdesi
        win_rate (float): Kazanma oranı yüzdesi
        sharpe_ratio (float): Sharpe oranı
    
    Returns:
        str: Performans notu (A+, A, B+, B, C+, C, D, F)
    """
    try:
        score = 0
        
        # Getiri skoru (40% ağırlık)
        if total_return >= 20:
            score += 40
        elif total_return >= 15:
            score += 35
        elif total_return >= 10:
            score += 30
        elif total_return >= 5:
            score += 20
        elif total_return >= 0:
            score += 10
            
        # Risk skoru (30% ağırlık)
        if max_drawdown >= -5:
            score += 30
        elif max_drawdown >= -10:
            score += 25
        elif max_drawdown >= -15:
            score += 20
        elif max_drawdown >= -20:
            score += 15
        elif max_drawdown >= -30:
            score += 10
            
        # Kazanma oranı skoru (20% ağırlık)
        if win_rate >= 60:
            score += 20
        elif win_rate >= 55:
            score += 18
        elif win_rate >= 50:
            score += 15
        elif win_rate >= 45:
            score += 12
        elif win_rate >= 40:
            score += 8
            
        # Sharpe ratio skoru (10% ağırlık)
        if sharpe_ratio >= 2.0:
            score += 10
        elif sharpe_ratio >= 1.5:
            score += 8
        elif sharpe_ratio >= 1.0:
            score += 6
        elif sharpe_ratio >= 0.5:
            score += 4
        elif sharpe_ratio >= 0:
            score += 2
            
        # Not hesaplama
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'B+'
        elif score >= 75:
            return 'B'
        elif score >= 70:
            return 'C+'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'
            
    except:
        return 'N/A'


if __name__ == "__main__":
    """
    Backtester modülü test kodu
    """
    print("=== AI-FTB Backtester Test ===")
    
    # Test için basit mock model
    class MockMLModel:
        def predict(self, X):
            # Basit strateji: pozitif trend varsa 1, negatif varsa 0
            return [1 if np.random.random() > 0.4 else 0]
            
        def predict_proba(self, X):
            prob = np.random.random()
            return [[1-prob, prob]]
    
    # Test verisi oluştur
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    np.random.seed(42)
    
    # Basit fiyat simülasyonu
    initial_price = 100
    returns = np.random.normal(0.001, 0.02, len(dates))
    prices = [initial_price]
    for r in returns[1:]:
        prices.append(prices[-1] * (1 + r))
    
    test_data = pd.DataFrame({
        'Open': prices,
        'High': [p * (1 + np.random.uniform(0, 0.02)) for p in prices],
        'Low': [p * (1 - np.random.uniform(0, 0.02)) for p in prices],
        'Close': prices,
        'Volume': np.random.randint(1000000, 5000000, len(dates)),
        'RSI': np.random.uniform(20, 80, len(dates)),
        'MACD_Hist': np.random.normal(0, 0.3, len(dates)),
        'SMA_20': [p * (1 + np.random.uniform(-0.01, 0.01)) for p in prices],
        'Volume_Change': np.random.normal(0, 0.2, len(dates)),
        'Volatility': np.random.uniform(0.01, 0.04, len(dates)),
        'Volume_Ratio': np.random.uniform(0.5, 2.0, len(dates))
    }, index=dates)
    
    print(f"Test verisi oluşturuldu: {len(test_data)} gün")
    print(f"Fiyat aralığı: ${min(prices):.2f} - ${max(prices):.2f}")
    
    # Mock model
    mock_model = MockMLModel()
    
    # Backtest çalıştır
    print("\\n1. Backtest çalıştırılıyor...")
    backtest_result = run_backtest(
        test_data,
        mock_model,
        initial_capital=100000
    )
    
    if backtest_result:
        print(f"✅ Backtest tamamlandı")
        print(f"📊 Final değer: ${backtest_result['final_portfolio_value']:,.0f}")
        print(f"📈 Toplam getiri: {backtest_result['total_return']:+.1f}%")
        print(f"🔢 Toplam işlem: {backtest_result['total_trades']}")
        
        # Performans raporu
        print("\\n2. Performans raporu oluşturuluyor...")
        performance = generate_performance_report(
            backtest_result['trade_log'],
            backtest_result['initial_capital'],
            backtest_result['portfolio_history']
        )
        
        if performance:
            print("✅ Performans raporu oluşturuldu")
            print(f"🏆 Performans notu: {performance['performance_grade']}")
            print(f"📊 Kazanma oranı: {performance['win_rate_percent']:.1f}%")
            print(f"📉 Maksimum düşüş: {performance['max_drawdown_percent']:.1f}%")
            print(f"⚡ Sharpe ratio: {performance['sharpe_ratio']:.2f}")
            
            # Trade log özeti
            if not backtest_result['trade_log'].empty:
                print("\\n3. İşlem özeti:")
                trades_by_action = backtest_result['trade_log']['action'].value_counts()
                print(f"   İşlem dağılımı: {trades_by_action.to_dict()}")
                
                if 'pnl' in backtest_result['trade_log'].columns:
                    profitable_trades = len(backtest_result['trade_log'][backtest_result['trade_log']['pnl'] > 0])
                    print(f"   Karlı işlemler: {profitable_trades}/{len(backtest_result['trade_log'])}")
        else:
            print("❌ Performans raporu oluşturulamadı")
    else:
        print("❌ Backtest başarısız")
        
    print("\\nBacktester test tamamlandı!")
