"""
AI-FTB (AI-Powered Financial Trading Bot) Strategy Executor Module

Bu modül, makine öğrenimi sinyallerini, haber duygu skorlarını ve risk yönetimi 
kurallarını birleştirerek nihai alım-satım kararlarını (öneri olarak) üretir.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import config
import logger


def generate_trade_decision(ml_signal, news_sentiment_score, current_price, current_portfolio_value, 
                          additional_factors=None):
    """
    ML modelinden gelen sinyal ile haber duygu skorunu config'daki eşik değerlerine 
    göre birleştirir ve nihai ticaret kararını verir.
    
    Args:
        ml_signal (int or str): ML modelinden gelen sinyal (1/'BUY', 0/'HOLD', -1/'SELL')
        news_sentiment_score (float): Haber duygu skoru (-1.0 ile 1.0 arası)
        current_price (float): Anlık fiyat
        current_portfolio_value (float): Mevcut portföy değeri
        additional_factors (dict): Ek karar faktörleri
    
    Returns:
        dict: {'decision': str, 'confidence': float, 'reasoning': str}
        
    Raises:
        Exception: Karar hesaplama hatalarında
    """
    try:
        logger.log_debug(f"Karar hesaplanıyor: ML={ml_signal}, Sentiment={news_sentiment_score:.3f}, Price=${current_price:.2f}")
        
        # ML sinyalini standartlaştır
        if isinstance(ml_signal, str):
            if ml_signal == 'BUY':
                ml_numeric = 1
            elif ml_signal == 'SELL':
                ml_numeric = -1
            else:
                ml_numeric = 0
        else:
            ml_numeric = ml_signal
            
        # Config'ten eşik değerleri al
        pos_threshold = config.SENTIMENT_THRESHOLD_POSITIVE
        neg_threshold = config.SENTIMENT_THRESHOLD_NEGATIVE
        
        # Karar mantığı
        decision = 'HOLD'
        confidence = 0.5
        reasoning_parts = []
        
        # Güçlü AL sinyali
        if (ml_numeric == 1 and news_sentiment_score >= pos_threshold):
            decision = 'BUY'
            confidence = 0.8 + min(0.2, (news_sentiment_score - pos_threshold) * 2)
            reasoning_parts.append(f"ML AL sinyali + Pozitif haber duygusu ({news_sentiment_score:.2f})")
            
        # Güçlü SAT sinyali  
        elif (ml_numeric == -1 and news_sentiment_score <= neg_threshold):
            decision = 'SELL'
            confidence = 0.8 + min(0.2, abs(news_sentiment_score - neg_threshold) * 2)
            reasoning_parts.append(f"ML SAT sinyali + Negatif haber duygusu ({news_sentiment_score:.2f})")
            
        # Orta seviye AL sinyali
        elif (ml_numeric == 1 and news_sentiment_score >= 0):
            decision = 'BUY'
            confidence = 0.6 + (news_sentiment_score * 0.2)
            reasoning_parts.append(f"ML AL sinyali + Nötr/pozitif haber duygusu ({news_sentiment_score:.2f})")
            
        # Orta seviye SAT sinyali
        elif (ml_numeric == -1 and news_sentiment_score <= 0):
            decision = 'SELL'  
            confidence = 0.6 + abs(news_sentiment_score * 0.2)
            reasoning_parts.append(f"ML SAT sinyali + Nötr/negatif haber duygusu ({news_sentiment_score:.2f})")
            
        # Çelişkili sinyaller - ML AL, Haber Negatif
        elif (ml_numeric == 1 and news_sentiment_score < neg_threshold):
            decision = 'HOLD'
            confidence = 0.3
            reasoning_parts.append(f"Çelişkili sinyal: ML AL ama negatif haber ({news_sentiment_score:.2f})")
            
        # Çelişkili sinyaller - ML SAT, Haber Pozitif
        elif (ml_numeric == -1 and news_sentiment_score > pos_threshold):
            decision = 'HOLD'
            confidence = 0.3
            reasoning_parts.append(f"Çelişkili sinyal: ML SAT ama pozitif haber ({news_sentiment_score:.2f})")
            
        # ML HOLD sinyali
        elif ml_numeric == 0:
            # Çok güçlü haber duygusu varsa ona göre karar ver
            if news_sentiment_score >= pos_threshold + 0.3:
                decision = 'BUY'
                confidence = 0.6
                reasoning_parts.append(f"ML HOLD ama çok pozitif haber ({news_sentiment_score:.2f})")
            elif news_sentiment_score <= neg_threshold - 0.3:
                decision = 'SELL'
                confidence = 0.6
                reasoning_parts.append(f"ML HOLD ama çok negatif haber ({news_sentiment_score:.2f})")
            else:
                decision = 'HOLD'
                confidence = 0.4
                reasoning_parts.append(f"ML HOLD + nötr haber duygusu ({news_sentiment_score:.2f})")
                
        # Ek faktörleri değerlendir
        if additional_factors:
            volatility = additional_factors.get('volatility', 0)
            volume_ratio = additional_factors.get('volume_ratio', 1)
            
            # Yüksek volatilite uyarısı
            if volatility > 0.05:  # %5'ten fazla günlük volatilite
                confidence *= 0.8
                reasoning_parts.append("Yüksek volatilite nedeniyle güven azaltıldı")
                
            # Düşük hacim uyarısı
            if volume_ratio < 0.5:  # Normal hacmin yarısından az
                confidence *= 0.9
                reasoning_parts.append("Düşük hacim nedeniyle güven azaltıldı")
                
            # Yüksek hacim avantajı
            elif volume_ratio > 2.0:  # Normal hacmin 2 katından fazla
                confidence = min(1.0, confidence * 1.1)
                reasoning_parts.append("Yüksek hacim nedeniyle güven artırıldı")
                
        # Güven skorunu sınırla
        confidence = max(0.1, min(1.0, confidence))
        
        reasoning = "; ".join(reasoning_parts)
        
        result = {
            'decision': decision,
            'confidence': confidence,
            'reasoning': reasoning
        }
        
        logger.log_info(f"Karar: {decision} (Güven: {confidence:.2f}) - {reasoning}")
        
        return result
        
    except Exception as e:
        logger.log_error(f"Karar hesaplama hatası: {e}", exc_info=True)
        return {
            'decision': 'HOLD',
            'confidence': 0.0,
            'reasoning': f"Hata nedeniyle HOLD: {str(e)}"
        }


def calculate_position_size(portfolio_value, current_price, risk_per_trade_percent=None, decision_confidence=1.0):
    """
    Risk yüzdesine ve anlık fiyata göre işlem başına pozisyon büyüklüğünü 
    (lot veya hisse adedi) hesaplar.
    
    Args:
        portfolio_value (float): Mevcut portföy değeri
        current_price (float): Anlık hisse fiyatı
        risk_per_trade_percent (float): İşlem başına risk yüzdesi (0.0-1.0 arası)
        decision_confidence (float): Karar güven skoru (0.0-1.0 arası)
    
    Returns:
        dict: {'shares': int, 'investment_amount': float, 'risk_amount': float}
        None: Hata durumunda
        
    Raises:
        Exception: Pozisyon hesaplama hatalarında
    """
    try:
        # Risk yüzdesini config'ten al
        if risk_per_trade_percent is None:
            risk_per_trade_percent = config.RISK_PER_TRADE_PERCENT
            
        logger.log_debug(f"Pozisyon hesaplanıyor: Portföy=${portfolio_value:.2f}, Fiyat=${current_price:.2f}, Risk=%{risk_per_trade_percent*100:.1f}")
        
        # Giriş kontrolleri
        if portfolio_value <= 0:
            logger.log_error("Geçersiz portföy değeri")
            return None
            
        if current_price <= 0:
            logger.log_error("Geçersiz hisse fiyatı")
            return None
            
        if risk_per_trade_percent <= 0 or risk_per_trade_percent > 1:
            logger.log_error("Geçersiz risk yüzdesi")
            return None
            
        # Risk miktarını hesapla
        base_risk_amount = portfolio_value * risk_per_trade_percent
        
        # Güven skoruna göre risk miktarını ayarla
        # Düşük güven = daha az risk, Yüksek güven = normal risk
        adjusted_risk_amount = base_risk_amount * decision_confidence
        
        # Maksimum yatırım miktarını hesapla (stop loss'u göz önünde bulundurarak)
        stop_loss_percent = config.STOP_LOSS_PERCENT
        
        # Stop loss seviyesinde kaybedilecek miktar = risk miktarı olmalı
        # Yatırım miktarı * stop_loss_percent = adjusted_risk_amount
        # Yatırım miktarı = adjusted_risk_amount / stop_loss_percent
        max_investment = adjusted_risk_amount / stop_loss_percent
        
        # Portföyün maksimum %20'si (güvenlik sınırı)
        portfolio_limit = portfolio_value * 0.2
        investment_amount = min(max_investment, portfolio_limit)
        
        # Satın alınacak hisse adedini hesapla
        shares = int(investment_amount / current_price)
        
        # Gerçek yatırım miktarını hesapla (tam hisse sayısına göre)
        actual_investment = shares * current_price
        
        # Gerçek risk miktarını hesapla
        actual_risk = actual_investment * stop_loss_percent
        
        # Minimum pozisyon kontrolü
        if shares < 1:
            logger.log_warning("Hesaplanan pozisyon 1 hisseden az, işlem yapılmayacak")
            return {
                'shares': 0,
                'investment_amount': 0.0,
                'risk_amount': 0.0,
                'reason': 'Minimum pozisyon altında'
            }
            
        result = {
            'shares': shares,
            'investment_amount': actual_investment,
            'risk_amount': actual_risk,
            'portfolio_percentage': (actual_investment / portfolio_value) * 100,
            'risk_percentage': (actual_risk / portfolio_value) * 100
        }
        
        logger.log_info(f"Pozisyon: {shares} hisse, Yatırım=${actual_investment:.2f} ({result['portfolio_percentage']:.1f}%), Risk=${actual_risk:.2f} ({result['risk_percentage']:.2f}%)")
        
        return result
        
    except Exception as e:
        logger.log_error(f"Pozisyon hesaplama hatası: {e}", exc_info=True)
        return None


def apply_risk_management(decision, entry_price, current_price, position_status, 
                         stop_loss_percent=None, take_profit_percent=None):
    """
    Belirlenen stop_loss_percent ve take_profit_percent seviyelerine göre 
    mevcut bir pozisyonun kapatılıp kapatılmayacağını kontrol eder.
    
    Args:
        decision (str): Mevcut karar ('BUY', 'SELL', 'HOLD')
        entry_price (float): Pozisyona giriş fiyatı
        current_price (float): Anlık fiyat
        position_status (dict): Mevcut pozisyon durumu
        stop_loss_percent (float): Zarar durdurma yüzdesi
        take_profit_percent (float): Kar alma yüzdesi
    
    Returns:
        dict: {'action': str, 'reason': str, 'pnl_percent': float}
        
    Raises:
        Exception: Risk hesaplama hatalarında
    """
    try:
        # Parametreleri config'ten al
        if stop_loss_percent is None:
            stop_loss_percent = config.STOP_LOSS_PERCENT
        if take_profit_percent is None:
            take_profit_percent = config.TAKE_PROFIT_PERCENT
            
        # Mevcut pozisyon kontrolü
        if not position_status or position_status.get('shares', 0) == 0:
            return {
                'action': 'NONE',
                'reason': 'Açık pozisyon yok',
                'pnl_percent': 0.0
            }
            
        position_type = position_status.get('type', 'LONG')  # LONG veya SHORT
        shares = position_status.get('shares', 0)
        
        if entry_price <= 0 or current_price <= 0:
            logger.log_error("Geçersiz fiyat değerleri")
            return {'action': 'NONE', 'reason': 'Geçersiz fiyat', 'pnl_percent': 0.0}
            
        # Kar/zarar yüzdesini hesapla
        if position_type == 'LONG':
            pnl_percent = (current_price - entry_price) / entry_price
        else:  # SHORT pozisyon
            pnl_percent = (entry_price - current_price) / entry_price
            
        logger.log_debug(f"Risk kontrolü: Tip={position_type}, Giriş=${entry_price:.2f}, Güncel=${current_price:.2f}, P&L={pnl_percent:.2%}")
        
        # Stop Loss kontrolü
        if pnl_percent <= -stop_loss_percent:
            return {
                'action': 'CLOSE_STOP_LOSS',
                'reason': f'Stop loss seviyesi aşıldı ({pnl_percent:.2%})',
                'pnl_percent': pnl_percent * 100
            }
            
        # Take Profit kontrolü
        if pnl_percent >= take_profit_percent:
            return {
                'action': 'CLOSE_TAKE_PROFIT',
                'reason': f'Take profit seviyesi ulaşıldı ({pnl_percent:.2%})',
                'pnl_percent': pnl_percent * 100
            }
            
        # Trailing Stop Loss (opsiyonel - %50 kar varsa stop loss'u giriş fiyatına çek)
        if pnl_percent >= (take_profit_percent * 0.5):
            # Bu durumda stop loss seviyesini güncellemek için sinyal ver
            # Gerçek uygulamada trailing stop mantığı burada olabilir
            pass
            
        # Risk seviyesinde değil
        return {
            'action': 'NONE',
            'reason': f'Normal seviyede (P&L: {pnl_percent:.2%})',
            'pnl_percent': pnl_percent * 100
        }
        
    except Exception as e:
        logger.log_error(f"Risk yönetimi hatası: {e}", exc_info=True)
        return {'action': 'NONE', 'reason': f'Hata: {str(e)}', 'pnl_percent': 0.0}


def calculate_portfolio_metrics(positions, current_prices):
    """
    Mevcut portföy için genel metrikleri hesaplar.
    
    Args:
        positions (list): Açık pozisyonlar listesi
        current_prices (dict): Sembollerin güncel fiyatları
    
    Returns:
        dict: Portföy metrikleri
    """
    try:
        if not positions:
            return {
                'total_value': 0.0,
                'total_pnl': 0.0,
                'total_pnl_percent': 0.0,
                'position_count': 0,
                'winning_positions': 0,
                'losing_positions': 0
            }
            
        total_value = 0.0
        total_cost = 0.0
        winning_positions = 0
        losing_positions = 0
        
        for position in positions:
            symbol = position.get('symbol')
            shares = position.get('shares', 0)
            entry_price = position.get('entry_price', 0)
            current_price = current_prices.get(symbol, entry_price)
            
            position_value = shares * current_price
            position_cost = shares * entry_price
            position_pnl = position_value - position_cost
            
            total_value += position_value
            total_cost += position_cost
            
            if position_pnl > 0:
                winning_positions += 1
            elif position_pnl < 0:
                losing_positions += 1
                
        total_pnl = total_value - total_cost
        total_pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        metrics = {
            'total_value': total_value,
            'total_cost': total_cost,
            'total_pnl': total_pnl,
            'total_pnl_percent': total_pnl_percent,
            'position_count': len(positions),
            'winning_positions': winning_positions,
            'losing_positions': losing_positions,
            'win_rate': (winning_positions / len(positions) * 100) if positions else 0
        }
        
        logger.log_info(f"Portföy: ${total_value:.2f}, P&L=${total_pnl:.2f} ({total_pnl_percent:.1f}%), Win Rate={metrics['win_rate']:.1f}%")
        
        return metrics
        
    except Exception as e:
        logger.log_error(f"Portföy metrik hatası: {e}")
        return {'total_value': 0.0, 'total_pnl': 0.0}


def validate_trade_decision(decision_data, market_hours=True, portfolio_constraints=None):
    """
    Ticaret kararının geçerliliğini kontrol eder.
    
    Args:
        decision_data (dict): Karar verisi
        market_hours (bool): Piyasa açık mı
        portfolio_constraints (dict): Portföy kısıtları
    
    Returns:
        dict: Geçerlilik sonucu
    """
    try:
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Piyasa saati kontrolü
        if not market_hours:
            validation_result['warnings'].append("Piyasa kapalı - işlem sıraya alınacak")
            
        # Güven skoru kontrolü
        confidence = decision_data.get('confidence', 0)
        if confidence < 0.3:
            validation_result['warnings'].append(f"Düşük güven skoru: {confidence:.2f}")
        elif confidence < 0.1:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Çok düşük güven skoru: {confidence:.2f}")
            
        # Portföy kısıtları kontrolü
        if portfolio_constraints:
            max_positions = portfolio_constraints.get('max_positions', 10)
            current_positions = portfolio_constraints.get('current_positions', 0)
            
            if current_positions >= max_positions:
                validation_result['is_valid'] = False
                validation_result['errors'].append("Maksimum pozisyon sayısına ulaşıldı")
                
        return validation_result
        
    except Exception as e:
        logger.log_error(f"Karar geçerlilik kontrolü hatası: {e}")
        return {'is_valid': False, 'errors': [str(e)]}


if __name__ == "__main__":
    """
    Strategy Executor modülü test kodu
    """
    print("=== AI-FTB Strategy Executor Test ===")
    
    # Test senaryoları
    test_scenarios = [
        {
            'name': 'Güçlü AL sinyali',
            'ml_signal': 1,
            'sentiment': 0.4,
            'price': 150.0,
            'portfolio': 10000
        },
        {
            'name': 'Güçlü SAT sinyali',
            'ml_signal': -1,
            'sentiment': -0.4,
            'price': 150.0,
            'portfolio': 10000
        },
        {
            'name': 'Çelişkili sinyal',
            'ml_signal': 1,
            'sentiment': -0.3,
            'price': 150.0,
            'portfolio': 10000
        },
        {
            'name': 'HOLD sinyali',
            'ml_signal': 0,
            'sentiment': 0.1,
            'price': 150.0,
            'portfolio': 10000
        }
    ]
    
    print("\\n1. Karar senaryoları test ediliyor...")
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\\n   Senaryo {i}: {scenario['name']}")
        
        decision = generate_trade_decision(
            scenario['ml_signal'],
            scenario['sentiment'],
            scenario['price'],
            scenario['portfolio']
        )
        
        print(f"   Karar: {decision['decision']}")
        print(f"   Güven: {decision['confidence']:.2f}")
        print(f"   Gerekçe: {decision['reasoning']}")
        
        # Pozisyon büyüklüğü hesapla
        if decision['decision'] in ['BUY', 'SELL']:
            position = calculate_position_size(
                scenario['portfolio'],
                scenario['price'],
                decision_confidence=decision['confidence']
            )
            
            if position and position['shares'] > 0:
                print(f"   Pozisyon: {position['shares']} hisse (${position['investment_amount']:.2f})")
            else:
                print("   Pozisyon: İşlem yapılmayacak")
                
    # Risk yönetimi testi
    print("\\n2. Risk yönetimi test ediliyor...")
    
    # Test pozisyonu
    test_position = {
        'symbol': 'AAPL',
        'shares': 100,
        'type': 'LONG'
    }
    
    risk_scenarios = [
        {'entry': 100.0, 'current': 95.0, 'name': 'Zarar durumu'},
        {'entry': 100.0, 'current': 105.0, 'name': 'Kar durumu'},
        {'entry': 100.0, 'current': 98.0, 'name': 'Stop loss seviyesi'},
        {'entry': 100.0, 'current': 104.0, 'name': 'Take profit seviyesi'}
    ]
    
    for scenario in risk_scenarios:
        print(f"\\n   {scenario['name']}:")
        risk_result = apply_risk_management(
            'HOLD',
            scenario['entry'],
            scenario['current'],
            test_position
        )
        
        print(f"   Aksiyon: {risk_result['action']}")
        print(f"   Gerekçe: {risk_result['reason']}")
        print(f"   P&L: {risk_result['pnl_percent']:.2f}%")
        
    # Portföy metrikleri testi
    print("\\n3. Portföy metrikleri test ediliyor...")
    
    test_positions = [
        {'symbol': 'AAPL', 'shares': 100, 'entry_price': 150.0},
        {'symbol': 'MSFT', 'shares': 50, 'entry_price': 300.0},
        {'symbol': 'GOOGL', 'shares': 25, 'entry_price': 2500.0}
    ]
    
    test_current_prices = {
        'AAPL': 155.0,
        'MSFT': 295.0,
        'GOOGL': 2600.0
    }
    
    portfolio_metrics = calculate_portfolio_metrics(test_positions, test_current_prices)
    print(f"   Toplam değer: ${portfolio_metrics['total_value']:.2f}")
    print(f"   Toplam P&L: ${portfolio_metrics['total_pnl']:.2f} ({portfolio_metrics['total_pnl_percent']:.1f}%)")
    print(f"   Kazanan pozisyonlar: {portfolio_metrics['winning_positions']}/{portfolio_metrics['position_count']}")
    
    print("\\nStrategy Executor test tamamlandı!")
