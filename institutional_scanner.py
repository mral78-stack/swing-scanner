#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   🏛️ INSTITUTIONAL-GRADE SWING TRADE SCANNER v7.0                           ║
║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                      ║
║   Professional Scanner with Technical + Fundamental Analysis                 ║
║   Opportunity Rating: AAA (Highest) to D (Lowest)                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import logging
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
from functools import lru_cache
import hashlib
import pickle
import logging as std_logging
warnings.filterwarnings('ignore')

# Suppress yfinance verbose logging
yfinance_logger = std_logging.getLogger('yfinance')
yfinance_logger.setLevel(std_logging.WARNING)

# Import yfinance with error handling for Streamlit Cloud
try:
    import yfinance as yf
except ImportError as e:
    error_msg = (
        "yfinance is not installed.\n\n"
        "LOCAL FIX:\n"
        "  pip install yfinance\n\n"
        "STREAMLIT CLOUD FIX:\n"
        "  1. Ensure requirements.txt is in the ROOT directory\n"
        "  2. Verify requirements.txt contains: yfinance>=0.2.28\n"
        "  3. Commit and push to GitHub\n"
        "  4. Streamlit Cloud will reinstall dependencies\n"
        "  5. Check Settings → Dependencies in Streamlit Cloud dashboard\n"
        "  6. Try 'Clear cache and restart' if needed\n\n"
        f"Original error: {e}"
    )
    raise ImportError(error_msg) from e

# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 LOGGING & CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('InstitutionalScanner')

CACHE_DIR = "scanner_cache"
RESULTS_DIR = "scanner_results"
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 OPPORTUNITY RATING SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class OpportunityRating:
    """Institutional-grade opportunity rating"""
    grade: str  # AAA, AA, A, BBB, BB, B, CCC, CC, C, D
    score: float  # 0-100
    technical_score: float  # 0-50
    fundamental_score: float  # 0-30
    momentum_score: float  # 0-20
    risk_score: float  # 0-20 (lower is better)
    confidence: float  # 0-100
    recommendation: str
    key_strengths: List[str]
    key_risks: List[str]
    
    def __str__(self):
        return f"{self.grade} ({self.score:.1f}/100) - {self.recommendation}"

def calculate_opportunity_rating(
    technical_score: float,
    fundamental_score: float,
    momentum_score: float,
    risk_score: float,
    key_strengths: List[str],
    key_risks: List[str]
) -> OpportunityRating:
    """Calculate institutional-grade opportunity rating"""
    
    # Weighted total score
    total_score = (
        technical_score * 0.50 +      # 50% weight
        fundamental_score * 0.30 +    # 30% weight
        momentum_score * 0.20         # 20% weight
    )
    
    # Risk adjustment (penalize high risk)
    risk_adjustment = max(0, (20 - risk_score) / 20)  # Normalize risk
    adjusted_score = total_score * risk_adjustment
    
    # Confidence based on number of signals
    confidence = min(100, len(key_strengths) * 10 + (20 - len(key_risks)) * 5)
    
    # Grade assignment (institutional rating scale)
    if adjusted_score >= 90:
        grade = "AAA"
        recommendation = "EXCEPTIONAL BUY - Highest Quality Opportunity"
    elif adjusted_score >= 85:
        grade = "AA"
        recommendation = "STRONG BUY - High Quality Opportunity"
    elif adjusted_score >= 80:
        grade = "A"
        recommendation = "BUY - Good Quality Opportunity"
    elif adjusted_score >= 75:
        grade = "BBB"
        recommendation = "MODERATE BUY - Above Average Opportunity"
    elif adjusted_score >= 70:
        grade = "BB"
        recommendation = "WATCH - Average Opportunity"
    elif adjusted_score >= 65:
        grade = "B"
        recommendation = "CAUTIOUS - Below Average Opportunity"
    elif adjusted_score >= 60:
        grade = "CCC"
        recommendation = "AVOID - Poor Quality"
    elif adjusted_score >= 55:
        grade = "CC"
        recommendation = "AVOID - Very Poor Quality"
    elif adjusted_score >= 50:
        grade = "C"
        recommendation = "AVOID - Extremely Poor Quality"
    else:
        grade = "D"
        recommendation = "AVOID - Default Quality"
    
    return OpportunityRating(
        grade=grade,
        score=adjusted_score,
        technical_score=technical_score,
        fundamental_score=fundamental_score,
        momentum_score=momentum_score,
        risk_score=risk_score,
        confidence=confidence,
        recommendation=recommendation,
        key_strengths=key_strengths,
        key_risks=key_risks
    )

# ═══════════════════════════════════════════════════════════════════════════════
# 📈 INSTITUTIONAL TECHNICAL INDICATORS
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_williams_r(high: pd.Series, low: pd.Series, close: pd.Series, 
                         period: int = 14) -> float:
    """Williams %R - Momentum indicator"""
    highest_high = high.rolling(period).max()
    lowest_low = low.rolling(period).min()
    wr = -100 * ((highest_high - close) / (highest_high - lowest_low))
    return float(wr.iloc[-1])

def calculate_cci(high: pd.Series, low: pd.Series, close: pd.Series, 
                  period: int = 20) -> float:
    """Commodity Channel Index"""
    typical_price = (high + low + close) / 3
    sma_tp = typical_price.rolling(period).mean()
    mad = typical_price.rolling(period).apply(lambda x: np.abs(x - x.mean()).mean())
    cci = (typical_price - sma_tp) / (0.015 * mad)
    return float(cci.iloc[-1])

def calculate_mfi(high: pd.Series, low: pd.Series, close: pd.Series, 
                  volume: pd.Series, period: int = 14) -> float:
    """Money Flow Index"""
    typical_price = (high + low + close) / 3
    money_flow = typical_price * volume
    
    positive_flow = money_flow.where(typical_price > typical_price.shift(), 0).rolling(period).sum()
    negative_flow = money_flow.where(typical_price < typical_price.shift(), 0).rolling(period).sum()
    
    mfi = 100 - (100 / (1 + positive_flow / negative_flow))
    return float(mfi.iloc[-1])

def calculate_aroon(high: pd.Series, low: pd.Series, period: int = 14) -> Tuple[float, float]:
    """Aroon Indicator - Trend strength"""
    aroon_up = ((period - high.rolling(period).apply(lambda x: period - 1 - x.argmax())) / period) * 100
    aroon_down = ((period - low.rolling(period).apply(lambda x: period - 1 - x.argmin())) / period) * 100
    return float(aroon_up.iloc[-1]), float(aroon_down.iloc[-1])

def calculate_ichimoku(high: pd.Series, low: pd.Series, close: pd.Series) -> Dict:
    """Ichimoku Cloud - Comprehensive trend analysis"""
    # Tenkan-sen (Conversion Line)
    period1_high = high.rolling(9).max()
    period1_low = low.rolling(9).min()
    tenkan_sen = (period1_high + period1_low) / 2
    
    # Kijun-sen (Base Line)
    period2_high = high.rolling(26).max()
    period2_low = low.rolling(26).min()
    kijun_sen = (period2_high + period2_low) / 2
    
    # Senkou Span A (Leading Span A)
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
    
    # Senkou Span B (Leading Span B)
    period3_high = high.rolling(52).max()
    period3_low = low.rolling(52).min()
    senkou_span_b = ((period3_high + period3_low) / 2).shift(26)
    
    # Chikou Span (Lagging Span)
    chikou_span = close.shift(-26)
    
    current_price = close.iloc[-1]
    cloud_top = max(senkou_span_a.iloc[-1], senkou_span_b.iloc[-1])
    cloud_bottom = min(senkou_span_a.iloc[-1], senkou_span_b.iloc[-1])
    
    # Position relative to cloud
    above_cloud = current_price > cloud_top
    in_cloud = cloud_bottom <= current_price <= cloud_top
    below_cloud = current_price < cloud_bottom
    
    return {
        'tenkan_sen': float(tenkan_sen.iloc[-1]),
        'kijun_sen': float(kijun_sen.iloc[-1]),
        'senkou_span_a': float(senkou_span_a.iloc[-1]),
        'senkou_span_b': float(senkou_span_b.iloc[-1]),
        'cloud_top': float(cloud_top),
        'cloud_bottom': float(cloud_bottom),
        'above_cloud': above_cloud,
        'in_cloud': in_cloud,
        'below_cloud': below_cloud,
        'cloud_bullish': above_cloud and senkou_span_a.iloc[-1] > senkou_span_b.iloc[-1]
    }

def calculate_fibonacci_levels(high: pd.Series, low: pd.Series, 
                               lookback: int = 60) -> Dict:
    """Calculate Fibonacci retracement levels"""
    recent_high = high.iloc[-lookback:].max()
    recent_low = low.iloc[-lookback:].min()
    diff = recent_high - recent_low
    
    levels = {
        '0.0': recent_high,
        '0.236': recent_high - (diff * 0.236),
        '0.382': recent_high - (diff * 0.382),
        '0.500': recent_high - (diff * 0.500),
        '0.618': recent_high - (diff * 0.618),
        '0.786': recent_high - (diff * 0.786),
        '1.0': recent_low
    }
    
    return levels

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """Calculate Sharpe Ratio (annualized)"""
    if len(returns) < 2:
        return 0.0
    excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
    if excess_returns.std() == 0:
        return 0.0
    sharpe = (excess_returns.mean() * 252) / (excess_returns.std() * np.sqrt(252))
    return float(sharpe)

def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """Calculate Sortino Ratio (downside risk only)"""
    if len(returns) < 2:
        return 0.0
    excess_returns = returns - (risk_free_rate / 252)
    downside_returns = excess_returns[excess_returns < 0]
    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return 0.0
    sortino = (excess_returns.mean() * 252) / (downside_returns.std() * np.sqrt(252))
    return float(sortino)

def calculate_max_drawdown(close: pd.Series) -> Tuple[float, float]:
    """Calculate Maximum Drawdown"""
    cumulative = (1 + close.pct_change()).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_dd = float(drawdown.min())
    max_dd_pct = max_dd * 100
    return max_dd, max_dd_pct

def calculate_calmar_ratio(returns: pd.Series, max_drawdown: float) -> float:
    """Calculate Calmar Ratio (annual return / max drawdown)"""
    if max_drawdown == 0:
        return 0.0
    annual_return = returns.mean() * 252
    calmar = annual_return / abs(max_drawdown)
    return float(calmar)

def calculate_vwap(high: pd.Series, low: pd.Series, close: pd.Series, 
                   volume: pd.Series, period: int = 20) -> Tuple[float, float]:
    """
    Calculate Volume Weighted Average Price (VWAP)
    Returns: (VWAP value, distance from current price in %)
    """
    typical_price = (high + low + close) / 3
    cumulative_tp_volume = (typical_price * volume).rolling(period).sum()
    cumulative_volume = volume.rolling(period).sum()
    vwap = cumulative_tp_volume / cumulative_volume
    
    current_vwap = float(vwap.iloc[-1])
    current_price = float(close.iloc[-1])
    distance_pct = ((current_price - current_vwap) / current_vwap) * 100
    
    return current_vwap, distance_pct

# ═══════════════════════════════════════════════════════════════════════════════
# 💼 FUNDAMENTAL ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_fundamentals(info: Dict, market: str = 'US') -> Tuple[float, List[str], List[str]]:
    """
    Comprehensive fundamental analysis
    Returns: (score, strengths, risks)
    """
    score = 0.0
    strengths = []
    risks = []
    
    # Market Cap Analysis
    market_cap = info.get('marketCap', 0)
    if market_cap > 10_000_000_000:  # > $10B
        score += 3
        strengths.append("Large Cap - Institutional Quality")
    elif market_cap > 2_000_000_000:  # > $2B
        score += 2
        strengths.append("Mid Cap")
    elif market_cap < 300_000_000:  # < $300M
        score -= 2
        risks.append("Micro Cap - Higher Risk")
    
    # Valuation Metrics
    pe_ratio = info.get('trailingPE', None)
    if pe_ratio:
        if 10 < pe_ratio < 25:
            score += 3
            strengths.append(f"Reasonable P/E ({pe_ratio:.1f})")
        elif pe_ratio < 10:
            score += 2
            strengths.append(f"Low P/E ({pe_ratio:.1f}) - Value Play")
        elif pe_ratio > 50:
            score -= 2
            risks.append(f"High P/E ({pe_ratio:.1f}) - Overvalued")
    
    # Price to Book
    pb_ratio = info.get('priceToBook', None)
    if pb_ratio:
        if pb_ratio < 3:
            score += 2
            strengths.append(f"Low P/B ({pb_ratio:.2f})")
        elif pb_ratio > 10:
            score -= 1
            risks.append(f"High P/B ({pb_ratio:.2f})")
    
    # Profitability
    profit_margins = info.get('profitMargins', None)
    if profit_margins:
        if profit_margins > 0.20:  # > 20%
            score += 4
            strengths.append(f"High Profit Margin ({profit_margins*100:.1f}%)")
        elif profit_margins > 0.10:  # > 10%
            score += 2
            strengths.append(f"Good Profit Margin ({profit_margins*100:.1f}%)")
        elif profit_margins < 0:
            score -= 3
            risks.append(f"Negative Profit Margin ({profit_margins*100:.1f}%)")
    
    # Revenue Growth
    revenue_growth = info.get('revenueGrowth', None)
    if revenue_growth:
        if revenue_growth > 0.20:  # > 20%
            score += 3
            strengths.append(f"Strong Revenue Growth ({revenue_growth*100:.1f}%)")
        elif revenue_growth > 0.10:  # > 10%
            score += 2
            strengths.append(f"Good Revenue Growth ({revenue_growth*100:.1f}%)")
        elif revenue_growth < -0.10:  # < -10%
            score -= 2
            risks.append(f"Declining Revenue ({revenue_growth*100:.1f}%)")
    
    # Earnings Growth
    earnings_growth = info.get('earningsGrowth', None)
    if earnings_growth:
        if earnings_growth > 0.25:  # > 25%
            score += 3
            strengths.append(f"Strong Earnings Growth ({earnings_growth*100:.1f}%)")
        elif earnings_growth < -0.20:  # < -20%
            score -= 2
            risks.append(f"Declining Earnings ({earnings_growth*100:.1f}%)")
    
    # Debt Analysis
    debt_to_equity = info.get('debtToEquity', None)
    if debt_to_equity:
        if debt_to_equity < 30:
            score += 2
            strengths.append(f"Low Debt/Equity ({debt_to_equity:.1f})")
        elif debt_to_equity > 100:
            score -= 2
            risks.append(f"High Debt/Equity ({debt_to_equity:.1f})")
    
    # Current Ratio (Liquidity)
    current_ratio = info.get('currentRatio', None)
    if current_ratio:
        if current_ratio > 2.0:
            score += 2
            strengths.append(f"Strong Liquidity (Current Ratio: {current_ratio:.2f})")
        elif current_ratio < 1.0:
            score -= 2
            risks.append(f"Weak Liquidity (Current Ratio: {current_ratio:.2f})")
    
    # Return on Equity
    roe = info.get('returnOnEquity', None)
    if roe:
        if roe > 0.20:  # > 20%
            score += 3
            strengths.append(f"High ROE ({roe*100:.1f}%)")
        elif roe > 0.15:  # > 15%
            score += 2
            strengths.append(f"Good ROE ({roe*100:.1f}%)")
        elif roe < 0:
            score -= 2
            risks.append(f"Negative ROE ({roe*100:.1f}%)")
    
    # Return on Assets
    roa = info.get('returnOnAssets', None)
    if roa:
        if roa > 0.10:  # > 10%
            score += 2
            strengths.append(f"Strong ROA ({roa*100:.1f}%)")
        elif roa < 0:
            score -= 1
            risks.append(f"Negative ROA ({roa*100:.1f}%)")
    
    # Institutional Ownership
    inst_ownership = info.get('heldPercentInstitutions', None)
    if inst_ownership:
        if inst_ownership > 0.70:  # > 70%
            score += 2
            strengths.append(f"High Institutional Ownership ({inst_ownership*100:.0f}%)")
        elif inst_ownership < 0.20:  # < 20%
            score -= 1
            risks.append(f"Low Institutional Ownership ({inst_ownership*100:.0f}%)")
    
    # Analyst Recommendations
    recommendation = info.get('recommendationKey', 'hold')
    if recommendation == 'strong_buy':
        score += 3
        strengths.append("Analyst: Strong Buy")
    elif recommendation == 'buy':
        score += 2
        strengths.append("Analyst: Buy")
    elif recommendation == 'sell' or recommendation == 'strong_sell':
        score -= 3
        risks.append(f"Analyst: {recommendation.title()}")
    
    # Forward P/E (if available)
    forward_pe = info.get('forwardPE', None)
    if forward_pe and pe_ratio:
        if forward_pe < pe_ratio:
            score += 1
            strengths.append("Forward P/E Lower - Earnings Growth Expected")
    
    # Normalize score to 0-30 range
    normalized_score = min(30, max(0, score))
    
    return normalized_score, strengths, risks

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 MARKET REGIME DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

def detect_market_regime(data: pd.DataFrame, lookback: int = 60) -> Dict:
    """
    Detect market regime: Bull, Bear, or Sideways
    """
    close = data['Close']
    volume = data['Volume']
    
    # Price trend
    sma_20 = close.rolling(20).mean()
    sma_50 = close.rolling(50).mean()
    price_change = (close.iloc[-1] / close.iloc[-lookback] - 1) * 100
    
    # Volatility
    returns = close.pct_change()
    volatility = returns.rolling(20).std() * np.sqrt(252) * 100  # Annualized
    
    # Volume trend
    avg_volume = volume.rolling(20).mean()
    volume_trend = (avg_volume.iloc[-1] / avg_volume.iloc[-20] - 1) * 100
    
    # Determine regime
    if price_change > 10 and close.iloc[-1] > sma_50.iloc[-1] and sma_20.iloc[-1] > sma_50.iloc[-1]:
        regime = "BULL"
        confidence = min(100, 50 + abs(price_change))
    elif price_change < -10 and close.iloc[-1] < sma_50.iloc[-1] and sma_20.iloc[-1] < sma_50.iloc[-1]:
        regime = "BEAR"
        confidence = min(100, 50 + abs(price_change))
    else:
        regime = "SIDEWAYS"
        confidence = 100 - abs(price_change)
    
    return {
        'regime': regime,
        'confidence': confidence,
        'price_change_pct': price_change,
        'volatility': float(volatility.iloc[-1]),
        'volume_trend_pct': volume_trend,
        'above_sma50': close.iloc[-1] > sma_50.iloc[-1],
        'sma20_above_sma50': sma_20.iloc[-1] > sma_50.iloc[-1]
    }

# ═══════════════════════════════════════════════════════════════════════════════
# 🇧🇷 BRAZIL MARKET ENHANCEMENTS
# ═══════════════════════════════════════════════════════════════════════════════

def get_usd_brl_rate() -> float:
    """Get current USD/BRL exchange rate"""
    try:
        ticker = yf.Ticker("USDBRL=X")
        data = ticker.history(period='1d')
        if not data.empty:
            return float(data['Close'].iloc[-1])
    except:
        pass
    # Fallback rate
    return 5.0

def convert_brl_to_usd(brl_value: float, rate: float = None) -> float:
    """Convert BRL to USD"""
    if rate is None:
        rate = get_usd_brl_rate()
    return brl_value / rate

def get_b3_sector_info(ticker: str) -> Dict:
    """Get B3-specific sector information"""
    # B3 sector mapping (simplified - can be expanded)
    sector_map = {
        'ITUB': 'Banks',
        'BBDC': 'Banks',
        'PETR': 'Oil & Gas',
        'VALE': 'Mining',
        'MGLU': 'Retail',
        'ABEV': 'Beverages',
    }
    
    ticker_base = ticker.replace('.SA', '').replace('3', '').replace('4', '')
    sector = sector_map.get(ticker_base, 'Unknown')
    
    return {
        'sector': sector,
        'exchange': 'B3',
        'currency': 'BRL'
    }

# ═══════════════════════════════════════════════════════════════════════════════
# 🎯 COMPREHENSIVE STOCK ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_stock_institutional(ticker: str, sector: str = 'Unknown', 
                                market: str = 'US') -> Optional[Dict]:
    """
    Institutional-grade comprehensive stock analysis
    """
    try:
        # Try multi-source data fetcher with fallbacks
        try:
            from data_sources import fetch_stock_data, get_stock_info
            USE_MULTI_SOURCE = True
        except ImportError:
            # Fallback to yfinance only if data_sources not available
            USE_MULTI_SOURCE = False
            import yfinance as yf
        
        if USE_MULTI_SOURCE:
            # Use multi-source fetcher with automatic fallbacks
            data = fetch_stock_data(
                ticker,
                period='1y',
                use_alphavantage=True,  # Enable if API key in env
                use_polygon=True,      # Enable if API key in env
                use_iexcloud=True      # Enable if API key in env
            )
            
            if data is None or data.empty or len(data) < 60:
                return None
            
            # Get stock info
            info = get_stock_info(ticker)
        else:
            # Original yfinance-only approach with retry logic
            stock = yf.Ticker(ticker)
            
            # Add retry logic for Yahoo Finance API issues (401, rate limits, etc.)
            max_retries = 2
            data = None
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    data = stock.history(period='1y', timeout=10)
                    if data is not None and not data.empty and len(data) >= 60:
                        break
                    elif data is None or data.empty:
                        # No data available - likely delisted or invalid ticker
                        return None
                except Exception as e:
                    last_error = e
                    error_str = str(e).lower()
                    
                    # Handle specific Yahoo Finance errors
                    if "401" in error_str or "unauthorized" in error_str:
                        # Rate limit or auth issue - retry with delay
                        if attempt < max_retries - 1:
                            import time
                            time.sleep(1.0)  # Wait before retry
                            continue
                    elif "delisted" in error_str or "no data found" in error_str:
                        # Stock is delisted - skip silently
                        return None
                    elif attempt < max_retries - 1:
                        # Other errors - retry once
                        import time
                        time.sleep(0.5)
                        continue
                    else:
                        # Final attempt failed - log at debug level only
                        logger.debug(f"{ticker}: Data fetch failed: {e}")
                        return None
            
            # Final check
            if data is None or data.empty or len(data) < 60:
                return None
            
            # Get stock info
            info = stock.info
        
        # Data and info are now available (from either multi-source or yfinance-only)
        close = data['Close']
        high = data['High']
        low = data['Low']
        volume = data['Volume']
        open_price = data['Open']
        
        current_close = float(close.iloc[-1])
        prev_close = float(close.iloc[-2])
        
        # Calculate returns
        returns = close.pct_change().dropna()
        
        # ═══════════════════════════════════════════════════════════════════
        # TECHNICAL ANALYSIS (50 points max)
        # ═══════════════════════════════════════════════════════════════════
        
        technical_score = 0.0
        technical_signals = []
        technical_risks = []
        
        # Moving Averages
        sma_20 = close.rolling(20).mean()
        sma_50 = close.rolling(50).mean()
        sma_200 = close.rolling(200).mean() if len(close) >= 200 else None
        
        if current_close > sma_50.iloc[-1]:
            technical_score += 3
            technical_signals.append("Above 50 SMA")
        
        if sma_200 is not None and current_close > sma_200.iloc[-1]:
            technical_score += 3
            technical_signals.append("Above 200 SMA")
        
        # Golden Cross
        if sma_200 is not None and len(close) >= 201:
            prev_sma_50 = sma_50.iloc[-2]
            prev_sma_200 = sma_200.iloc[-2]
            if sma_50.iloc[-1] > sma_200.iloc[-1] and prev_sma_50 <= prev_sma_200:
                technical_score += 5
                technical_signals.append("🌟 Golden Cross")
        
        # RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = float((100 - (100 / (1 + rs))).iloc[-1])
        
        if rsi < 30:
            technical_score += 4
            technical_signals.append(f"RSI Oversold ({rsi:.1f})")
        elif 50 < rsi < 70:
            technical_score += 2
            technical_signals.append(f"RSI Bullish ({rsi:.1f})")
        elif rsi > 70:
            technical_score -= 3
            technical_risks.append(f"RSI Overbought ({rsi:.1f})")
        
        # MACD
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd = float(macd_line.iloc[-1])
        macd_signal = float(signal_line.iloc[-1])
        macd_crossover = macd > macd_signal and float(macd_line.iloc[-2]) <= float(signal_line.iloc[-2])
        
        if macd_crossover:
            technical_score += 4
            technical_signals.append("MACD Bullish Crossover")
        elif macd > macd_signal:
            technical_score += 2
            technical_signals.append("MACD Above Signal")
        
        # Stochastic
        stoch_k, stoch_d = calculate_stochastic(high, low, close)
        if stoch_k < 20 and stoch_d < 20:
            technical_score += 3
            technical_signals.append(f"Stoch Oversold (K:{stoch_k:.1f})")
        elif stoch_k > 80:
            technical_score -= 2
            technical_risks.append(f"Stoch Overbought (K:{stoch_k:.1f})")
        
        # ADX
        adx = calculate_adx(high, low, close)
        if adx > 25:
            technical_score += 3
            technical_signals.append(f"Strong Trend (ADX:{adx:.1f})")
        elif adx < 20:
            technical_score -= 1
            technical_risks.append(f"Weak Trend (ADX:{adx:.1f})")
        
        # Williams %R
        williams_r = calculate_williams_r(high, low, close)
        if williams_r < -80:
            technical_score += 2
            technical_signals.append(f"Williams %R Oversold ({williams_r:.1f})")
        elif williams_r > -20:
            technical_score -= 1
            technical_risks.append(f"Williams %R Overbought ({williams_r:.1f})")
        
        # CCI
        cci = calculate_cci(high, low, close)
        if cci < -100:
            technical_score += 2
            technical_signals.append(f"CCI Oversold ({cci:.1f})")
        elif cci > 100:
            technical_score -= 1
            technical_risks.append(f"CCI Overbought ({cci:.1f})")
        
        # Money Flow Index
        mfi = calculate_mfi(high, low, close, volume)
        if mfi < 20:
            technical_score += 2
            technical_signals.append(f"MFI Oversold ({mfi:.1f})")
        elif mfi > 80:
            technical_score -= 1
            technical_risks.append(f"MFI Overbought ({mfi:.1f})")
        
        # Aroon
        aroon_up, aroon_down = calculate_aroon(high, low)
        if aroon_up > 70:
            technical_score += 2
            technical_signals.append(f"Strong Uptrend (Aroon:{aroon_up:.1f})")
        elif aroon_down > 70:
            technical_score -= 2
            technical_risks.append(f"Strong Downtrend (Aroon:{aroon_down:.1f})")
        
        # Ichimoku Cloud
        ichimoku = calculate_ichimoku(high, low, close)
        if ichimoku['cloud_bullish']:
            technical_score += 3
            technical_signals.append("Ichimoku Cloud Bullish")
        elif ichimoku['below_cloud']:
            technical_score -= 2
            technical_risks.append("Below Ichimoku Cloud")
        
        # Support/Resistance
        support, resistance = find_support_resistance(high, low, close)
        dist_to_support = ((current_close - support) / support) * 100
        if dist_to_support < 2:
            technical_score += 2
            technical_signals.append(f"Near Support (${support:.2f})")
        
        # Volume Analysis
        avg_volume = volume.iloc[-21:-1].mean()
        volume_ratio = volume.iloc[-1] / avg_volume if avg_volume > 0 else 0
        if volume_ratio > 1.5:
            technical_score += 3
            technical_signals.append(f"Volume Surge ({volume_ratio:.1f}x)")
        elif volume_ratio > 1.0:
            technical_score += 1
        
        # VWAP (Volume Weighted Average Price)
        vwap, vwap_distance = calculate_vwap(high, low, close, volume)
        if current_close > vwap:
            technical_score += 2
            technical_signals.append(f"Above VWAP ({vwap_distance:+.1f}%)")
        elif current_close < vwap and abs(vwap_distance) < 1:
            technical_score += 1
            technical_signals.append(f"Near VWAP ({vwap_distance:+.1f}%)")
        elif current_close < vwap and abs(vwap_distance) > 2:
            technical_score -= 1
            technical_risks.append(f"Below VWAP ({vwap_distance:+.1f}%)")
        
        # OBV
        obv = calculate_obv(close, volume)
        obv_trend = obv > float(calculate_obv(close.iloc[:-5], volume.iloc[:-5])) if len(close) > 5 else False
        if obv_trend:
            technical_score += 2
            technical_signals.append("OBV Rising")
        
        # Normalize technical score to 0-50
        technical_score = min(50, max(0, technical_score))
        
        # ═══════════════════════════════════════════════════════════════════
        # FUNDAMENTAL ANALYSIS (30 points max)
        # ═══════════════════════════════════════════════════════════════════
        
        fundamental_score, fundamental_strengths, fundamental_risks = analyze_fundamentals(info, market)
        
        # ═══════════════════════════════════════════════════════════════════
        # MOMENTUM ANALYSIS (20 points max)
        # ═══════════════════════════════════════════════════════════════════
        
        momentum_score = 0.0
        momentum_signals = []
        
        # Price momentum
        weekly_change = ((current_close / float(close.iloc[-6])) - 1) * 100 if len(close) >= 6 else 0
        monthly_change = ((current_close / float(close.iloc[-22])) - 1) * 100 if len(close) >= 22 else 0
        
        if weekly_change > 5:
            momentum_score += 3
            momentum_signals.append(f"Weekly +{weekly_change:.1f}%")
        elif weekly_change > 2:
            momentum_score += 1
        
        if monthly_change > 10:
            momentum_score += 4
            momentum_signals.append(f"Monthly +{monthly_change:.1f}%")
        elif monthly_change > 5:
            momentum_score += 2
        
        # Rate of Change
        roc_10 = ((current_close / float(close.iloc[-10])) - 1) * 100 if len(close) >= 10 else 0
        if roc_10 > 10:
            momentum_score += 3
            momentum_signals.append(f"10D ROC: +{roc_10:.1f}%")
        
        # Relative Strength (vs market - simplified)
        if market == 'US':
            # Compare to SPY
            try:
                spy = yf.Ticker("SPY")
                spy_data = spy.history(period='1y')
                if not spy_data.empty:
                    spy_return = (spy_data['Close'].iloc[-1] / spy_data['Close'].iloc[-22] - 1) * 100 if len(spy_data) >= 22 else 0
                    relative_strength = monthly_change - spy_return
                    if relative_strength > 5:
                        momentum_score += 3
                        momentum_signals.append(f"Outperforming Market (+{relative_strength:.1f}%)")
            except:
                pass
        
        # Normalize momentum score to 0-20
        momentum_score = min(20, max(0, momentum_score))
        
        # ═══════════════════════════════════════════════════════════════════
        # RISK ANALYSIS (20 points max - lower is better)
        # ═══════════════════════════════════════════════════════════════════
        
        risk_score = 0.0  # Start with 0 risk
        risk_factors = []
        
        # Volatility
        atr = float(np.maximum(high - low, np.maximum(abs(high - close.shift()), abs(low - close.shift()))).rolling(14).mean().iloc[-1])
        atr_pct = (atr / current_close) * 100
        
        if atr_pct > 8:
            risk_score += 5
            risk_factors.append(f"High Volatility (ATR: {atr_pct:.1f}%)")
        elif atr_pct > 5:
            risk_score += 2
        
        # Maximum Drawdown
        max_dd, max_dd_pct = calculate_max_drawdown(close)
        if abs(max_dd_pct) > 30:
            risk_score += 4
            risk_factors.append(f"Large Max Drawdown ({max_dd_pct:.1f}%)")
        elif abs(max_dd_pct) > 20:
            risk_score += 2
        
        # Sharpe Ratio
        sharpe = calculate_sharpe_ratio(returns)
        if sharpe < 0:
            risk_score += 3
            risk_factors.append(f"Negative Sharpe Ratio ({sharpe:.2f})")
        elif sharpe < 0.5:
            risk_score += 1
        
        # Beta (if available)
        beta = info.get('beta', None)
        if beta:
            if beta > 1.5:
                risk_score += 3
                risk_factors.append(f"High Beta ({beta:.2f})")
            elif beta < 0.5:
                risk_score += 1
                risk_factors.append(f"Low Beta ({beta:.2f}) - Low Volatility")
        
        # Normalize risk score (0-20, lower is better)
        risk_score = min(20, max(0, risk_score))
        
        # ═══════════════════════════════════════════════════════════════════
        # MARKET REGIME
        # ═══════════════════════════════════════════════════════════════════
        
        market_regime = detect_market_regime(data)
        
        # ═══════════════════════════════════════════════════════════════════
        # OPPORTUNITY RATING
        # ═══════════════════════════════════════════════════════════════════
        
        all_strengths = technical_signals + fundamental_strengths + momentum_signals
        all_risks = technical_risks + fundamental_risks + risk_factors
        
        rating = calculate_opportunity_rating(
            technical_score=technical_score,
            fundamental_score=fundamental_score,
            momentum_score=momentum_score,
            risk_score=risk_score,
            key_strengths=all_strengths,
            key_risks=all_risks
        )
        
        # ═══════════════════════════════════════════════════════════════════
        # BRAZIL MARKET SPECIFIC
        # ═══════════════════════════════════════════════════════════════════
        
        brl_rate = None
        price_usd = current_close
        if market == 'Brazil':
            brl_rate = get_usd_brl_rate()
            price_usd = convert_brl_to_usd(current_close, brl_rate)
            b3_info = get_b3_sector_info(ticker)
        else:
            b3_info = {}
        
        # ═══════════════════════════════════════════════════════════════════
        # COMPILE RESULTS
        # ═══════════════════════════════════════════════════════════════════
        
        result = {
            'Ticker': ticker,
            'Company': info.get('shortName', ticker)[:30] if info else ticker,
            'Market': market,
            'Sector': sector,
            
            # Price Data
            'Close': round(current_close, 2),
            'Close_USD': round(price_usd, 2) if market == 'Brazil' else round(current_close, 2),
            'Change%': round(((current_close / prev_close) - 1) * 100, 2),
            'Week%': round(weekly_change, 2),
            'Month%': round(monthly_change, 2),
            
            # Technical Indicators
            'RSI': round(rsi, 1),
            'MACD': round(macd, 3),
            'Stoch_K': round(stoch_k, 1),
            'Stoch_D': round(stoch_d, 1),
            'ADX': round(adx, 1),
            'Williams_R': round(williams_r, 1),
            'CCI': round(cci, 1),
            'MFI': round(mfi, 1),
            'Aroon_Up': round(aroon_up, 1),
            'Aroon_Down': round(aroon_down, 1),
            'Volume_Ratio': round(volume_ratio, 2),
            'VWAP': round(vwap, 2),
            'VWAP_Distance%': round(vwap_distance, 2),
            'ATR%': round(atr_pct, 2),
            'Support': round(support, 2),
            'Resistance': round(resistance, 2),
            
            # Risk Metrics
            'Sharpe_Ratio': round(sharpe, 2),
            'Max_Drawdown%': round(max_dd_pct, 2),
            'Beta': round(beta, 2) if beta else None,
            
            # Market Regime
            'Market_Regime': market_regime['regime'],
            'Regime_Confidence': round(market_regime['confidence'], 1),
            
            # Scores
            'Technical_Score': round(technical_score, 1),
            'Fundamental_Score': round(fundamental_score, 1),
            'Momentum_Score': round(momentum_score, 1),
            'Risk_Score': round(risk_score, 1),
            
            # Opportunity Rating
            'Rating_Grade': rating.grade,
            'Rating_Score': round(rating.score, 1),
            'Rating_Confidence': round(rating.confidence, 1),
            'Recommendation': rating.recommendation,
            
            # Signals
            'Key_Strengths': all_strengths[:10],  # Top 10
            'Key_Risks': all_risks[:10],  # Top 10
            
            # Additional Data
            'SMA_50': round(sma_50.iloc[-1], 2) if sma_50 is not None else None,
            'SMA_200': round(sma_200.iloc[-1], 2) if sma_200 is not None else None,
            'Ichimoku_Cloud_Bullish': ichimoku['cloud_bullish'],
            'BRL_Rate': round(brl_rate, 2) if brl_rate else None,
            'B3_Info': b3_info,
            'Timestamp': datetime.now().isoformat(),
        }
        
        return result
        
    except Exception as e:
        # Suppress common yfinance errors (delisted, 401, etc.) - log at debug level only
        error_str = str(e).lower()
        if any(keyword in error_str for keyword in ['delisted', 'no data found', '401', 'unauthorized', 'crumb']):
            logger.debug(f"{ticker}: {e}")
        else:
            logger.debug(f"Error analyzing {ticker}: {e}")
        return None

# Import helper functions (define if not available)
try:
    from stockmonitor_enhanced import (
        calculate_stochastic,
        calculate_adx,
        find_support_resistance,
        calculate_obv,
        get_cached_data,
        cache_data
    )
except ImportError:
    # Define fallback functions
    def calculate_stochastic(high, low, close, period=14):
        lowest_low = low.rolling(period).min()
        highest_high = high.rolling(period).max()
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(3).mean()
        return float(k_percent.iloc[-1]), float(d_percent.iloc[-1])
    
    def calculate_adx(high, low, close, period=14):
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        atr = tr.rolling(period).mean()
        plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(period).mean()
        return float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else 0.0
    
    def find_support_resistance(high, low, close, lookback=20):
        recent_high = high.iloc[-lookback:].max()
        recent_low = low.iloc[-lookback:].min()
        highs = []
        lows = []
        for i in range(lookback, len(high) - 1):
            if high.iloc[i] > high.iloc[i-1] and high.iloc[i] > high.iloc[i+1]:
                highs.append(high.iloc[i])
            if low.iloc[i] < low.iloc[i-1] and low.iloc[i] < low.iloc[i+1]:
                lows.append(low.iloc[i])
        resistance = np.percentile(highs, 75) if highs else recent_high
        support = np.percentile(lows, 25) if lows else recent_low
        return float(support), float(resistance)
    
    def calculate_obv(close, volume):
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return float(obv.iloc[-1])
    
    def get_cached_data(ticker, period='1y'):
        return None
    
    def cache_data(ticker, data, period='1y'):
        pass

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 PARALLEL SCANNER
# ═══════════════════════════════════════════════════════════════════════════════

def run_institutional_scan(max_workers: int = 10, 
                          min_rating: str = 'B') -> Tuple[List[Dict], List[Dict], List[Dict], Dict]:
    """
    Run institutional-grade scanner with parallel processing
    """
    # Import from market_tickers to avoid ib_insync import issues in Streamlit
    try:
        from market_tickers import US_SECTORS, BRAZIL_SECTORS
    except ImportError:
        # Fallback: try importing from stockmonitor (may fail in Streamlit)
        try:
            from stockmonitor import US_SECTORS, BRAZIL_SECTORS
        except (ImportError, RuntimeError):
            # If both fail, define minimal sets
            logger.warning("Could not import sector definitions, using minimal set")
            US_SECTORS = {'Technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']}
            BRAZIL_SECTORS = {'Banks': ['ITUB4.SA', 'BBDC4.SA']}
    
    all_results = []
    tradeable_results = []
    non_tradeable_results = []
    
    # Flatten tickers
    us_tickers = []
    for sector, tickers in US_SECTORS.items():
        for ticker in tickers:
            us_tickers.append((ticker, sector, 'US'))
    
    br_tickers = []
    for sector, tickers in BRAZIL_SECTORS.items():
        for ticker in tickers:
            br_tickers.append((ticker, sector, 'Brazil'))
    
    all_tickers = us_tickers + br_tickers
    total = len(all_tickers)
    
    logger.info(f"🏛️ Institutional Scan: {len(us_tickers)} US + {len(br_tickers)} BR = {total} stocks (parallel, {max_workers} workers)...")
    
    # Rating order for filtering
    rating_order = {'AAA': 10, 'AA': 9, 'A': 8, 'BBB': 7, 'BB': 6, 'B': 5, 
                    'CCC': 4, 'CC': 3, 'C': 2, 'D': 1}
    min_rating_value = rating_order.get(min_rating, 5)
    
    # Process in parallel
    completed = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ticker = {
            executor.submit(analyze_stock_institutional, ticker, sector, market): (ticker, sector, market)
            for ticker, sector, market in all_tickers
        }
        
        for future in as_completed(future_to_ticker):
            ticker, sector, market = future_to_ticker[future]
            try:
                result = future.result(timeout=45)
                
                if result:
                    rating_value = rating_order.get(result.get('Rating_Grade', 'D'), 1)
                    
                    if rating_value >= min_rating_value:
                        all_results.append(result)
                        
                        if market == 'US':
                            # IBKR tradeability check removed - assume all US stocks are tradeable
                            result['IBKR_Tradeable'] = True
                            tradeable_results.append(result)
                        else:
                            result['IBKR_Tradeable'] = False
                            result['IBKR_Note'] = 'BR market - separate session'
                            non_tradeable_results.append(result)
                
                completed += 1
                if completed % 50 == 0:
                    logger.info(f"   Progress: {completed}/{total} ({completed*100//total}%)")
                    
            except Exception as e:
                completed += 1
                logger.debug(f"Error processing {ticker}: {e}")
                continue
    
    # Sort by rating score
    all_results.sort(key=lambda x: x.get('Rating_Score', 0), reverse=True)
    tradeable_results.sort(key=lambda x: x.get('Rating_Score', 0), reverse=True)
    non_tradeable_results.sort(key=lambda x: x.get('Rating_Score', 0), reverse=True)
    
    logger.info(f"✅ Found {len(all_results)} opportunities (Rating >= {min_rating})")
    logger.info(f"   Tradeable: {len(tradeable_results)}, Non-tradeable: {len(non_tradeable_results)}")
    
    # Debug: Show rating distribution if no results
    if len(all_results) == 0:
        logger.warning(f"⚠️ No results found with rating >= {min_rating}")
        logger.info(f"   This may indicate:")
        logger.info(f"   - All stocks scored below {min_rating} threshold")
        logger.info(f"   - Many stocks may have failed data retrieval")
        logger.info(f"   - Try lowering min_rating to 'D' to see all results")
    
    # Group by sector for reporting
    sector_groups = {}
    for result in all_results:
        sector = result.get('Sector', 'Unknown')
        if sector not in sector_groups:
            sector_groups[sector] = []
        sector_groups[sector].append(result)
    
    # Sort each sector group by rating score
    for sector in sector_groups:
        sector_groups[sector].sort(key=lambda x: x.get('Rating_Score', 0), reverse=True)
    
    logger.info(f"📊 Opportunities by sector: {len(sector_groups)} sectors")
    for sector, opps in sorted(sector_groups.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        logger.info(f"   {sector}: {len(opps)} opportunities")
    
    return all_results, tradeable_results, non_tradeable_results, sector_groups

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Institutional-Grade Scanner')
    parser.add_argument('--scan', action='store_true', help='Run scanner')
    parser.add_argument('--max-workers', type=int, default=10, help='Parallel workers')
    parser.add_argument('--min-rating', type=str, default='B', 
                       choices=['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC', 'CC', 'C', 'D'],
                       help='Minimum rating grade')
    parser.add_argument('--save-json', action='store_true', help='Save to JSON')
    parser.add_argument('--save-csv', action='store_true', help='Save to CSV')
    
    args = parser.parse_args()
    
    if args.scan:
        results, tradeable, non_tradeable, sector_groups = run_institutional_scan(
            max_workers=args.max_workers,
            min_rating=args.min_rating
        )
        
        if args.save_json:
            from stockmonitor_enhanced import save_results_to_json
            save_results_to_json(results)
        
        if args.save_csv:
            from stockmonitor_enhanced import save_results_to_csv
            save_results_to_csv(results)
        
        # Display top opportunities
        print(f"\n{'═'*100}")
        print(f"🏛️ TOP INSTITUTIONAL OPPORTUNITIES (Rating >= {args.min_rating})")
        print(f"{'═'*100}")
        print(f"{'#':>2} {'Grade':<5} {'Ticker':<8} {'Score':>6} {'Tech':>5} {'Fund':>5} {'Mom':>5} {'Risk':>5} {'Company':<25}")
        print(f"{'─'*100}")
        
        for i, r in enumerate(results[:20], 1):
            print(f"{i:>2} {r['Rating_Grade']:<5} {r['Ticker']:<8} {r['Rating_Score']:>6.1f} "
                  f"{r['Technical_Score']:>5.1f} {r['Fundamental_Score']:>5.1f} "
                  f"{r['Momentum_Score']:>5.1f} {r['Risk_Score']:>5.1f} {r['Company']:<25}")
        
        # Display sector breakdown
        print(f"\n{'═'*100}")
        print(f"📊 OPPORTUNITIES BY SECTOR")
        print(f"{'═'*100}")
        print(f"{'Sector':<40} {'Count':>6} {'Avg Score':>10} {'Top Grade':>10}")
        print(f"{'─'*100}")
        
        for sector, opps in sorted(sector_groups.items(), key=lambda x: len(x[1]), reverse=True)[:15]:
            avg_score = sum(o.get('Rating_Score', 0) for o in opps) / len(opps) if opps else 0
            top_grade = max([o.get('Rating_Grade', 'D') for o in opps], 
                          key=lambda x: ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC', 'CC', 'C', 'D'].index(x)) if opps else 'D'
            print(f"{sector[:38]:<40} {len(opps):>6} {avg_score:>10.1f} {top_grade:>10}")
