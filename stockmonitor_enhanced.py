#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   🤖 ENHANCED SWING TRADE SCANNER v6.0 - OPTIMIZED FOR PERFORMANCE         ║
║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                      ║
║   High-Performance Scanner for US & BR Markets with GitHub Integration       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import threading
import queue
import time
import logging
import json
import os
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
import warnings
from functools import lru_cache
import hashlib
import pickle

# Suppress warnings
warnings.filterwarnings('ignore')

# Import yfinance for market data
import yfinance as yf
import requests

# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 LOGGING CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('EnhancedScanner')

# ═══════════════════════════════════════════════════════════════════════════════
# 📦 DATA PERSISTENCE & CACHING
# ═══════════════════════════════════════════════════════════════════════════════

CACHE_DIR = "scanner_cache"
RESULTS_DIR = "scanner_results"
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

def get_cache_key(ticker: str, market: str) -> str:
    """Generate cache key for ticker"""
    return hashlib.md5(f"{ticker}_{market}".encode()).hexdigest()

@lru_cache(maxsize=1000)
def get_cached_data(ticker: str, period: str = '1y') -> Optional[pd.DataFrame]:
    """Get cached stock data"""
    cache_file = os.path.join(CACHE_DIR, f"{get_cache_key(ticker, 'US')}_{period}.pkl")
    if os.path.exists(cache_file):
        try:
            # Check if cache is fresh (less than 5 minutes old)
            if time.time() - os.path.getmtime(cache_file) < 300:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
        except:
            pass
    return None

def cache_data(ticker: str, data: pd.DataFrame, period: str = '1y'):
    """Cache stock data"""
    cache_file = os.path.join(CACHE_DIR, f"{get_cache_key(ticker, 'US')}_{period}.pkl")
    try:
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)
    except:
        pass

def save_results_to_json(results: List[Dict], filename: str = None):
    """Save scan results to JSON file"""
    if filename is None:
        filename = f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    filepath = os.path.join(RESULTS_DIR, filename)
    
    # Convert datetime objects and other non-serializable types to strings
    serializable_results = []
    for r in results:
        serializable = {}
        for k, v in r.items():
            if isinstance(v, datetime):
                serializable[k] = v.isoformat()
            elif isinstance(v, bool) or (hasattr(v, '__class__') and 'bool' in str(type(v))):
                # Handle Python bool, numpy bool, pandas bool
                serializable[k] = bool(v)
            elif isinstance(v, (int, float, str, type(None))):
                # These are already JSON serializable
                serializable[k] = v
            elif isinstance(v, list):
                # Handle lists - convert non-serializable items
                serializable[k] = []
                for item in v:
                    if isinstance(item, (str, int, float, bool, type(None))):
                        serializable[k].append(item)
                    elif isinstance(item, datetime):
                        serializable[k].append(item.isoformat())
                    else:
                        serializable[k].append(str(item))
            elif isinstance(v, dict):
                # Handle nested dicts - recursively convert
                serializable[k] = {}
                for sub_k, sub_v in v.items():
                    if isinstance(sub_v, (str, int, float, bool, type(None))):
                        serializable[k][sub_k] = sub_v
                    elif isinstance(sub_v, datetime):
                        serializable[k][sub_k] = sub_v.isoformat()
                    else:
                        serializable[k][sub_k] = str(sub_v)
            else:
                # Convert everything else to string
                serializable[k] = str(v)
        serializable_results.append(serializable)
    
    with open(filepath, 'w') as f:
        json.dump(serializable_results, f, indent=2)
    
    logger.info(f"💾 Results saved to {filepath}")
    return filepath

def save_results_to_csv(results: List[Dict], filename: str = None):
    """Save scan results to CSV file"""
    if filename is None:
        filename = f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    filepath = os.path.join(RESULTS_DIR, filename)
    
    # Flatten results for CSV
    df_data = []
    for r in results:
        row = {k: v for k, v in r.items() if not isinstance(v, (list, dict))}
        row['Signals'] = ', '.join(r.get('Signals', []))
        df_data.append(row)
    
    df = pd.DataFrame(df_data)
    df.to_csv(filepath, index=False)
    
    logger.info(f"💾 Results saved to CSV: {filepath}")
    return filepath

# ═══════════════════════════════════════════════════════════════════════════════
# 🔄 GITHUB INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

# Import GitHub integration functions
try:
    from github_integration import setup_git_repo, commit_and_push_results
except ImportError:
    # Fallback if github_integration not available
    def setup_git_repo(repo_path: str = ".", remote_url: str = None):
        """Initialize git repository if not exists"""
        import subprocess
        
        if not os.path.exists(os.path.join(repo_path, ".git")):
            logger.info("📦 Initializing git repository...")
            subprocess.run(["git", "init"], cwd=repo_path, capture_output=True)
        
        if remote_url:
            result = subprocess.run(["git", "remote", "get-url", "origin"], 
                                  cwd=repo_path, capture_output=True)
            if result.returncode != 0:
                logger.info(f"🔗 Adding remote: {remote_url}")
                subprocess.run(["git", "remote", "add", "origin", remote_url], 
                             cwd=repo_path, capture_output=True)
    
    def commit_and_push_results(repo_path: str = ".", commit_message: str = None):
        """Commit and push results to GitHub"""
        import subprocess
        
        if commit_message is None:
            commit_message = f"Update scan results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        try:
            subprocess.run(["git", "add", RESULTS_DIR], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", commit_message], 
                          cwd=repo_path, check=True, capture_output=True)
            result = subprocess.run(["git", "push", "origin", "main"], 
                                  cwd=repo_path, capture_output=True)
            if result.returncode != 0:
                subprocess.run(["git", "push", "origin", "master"], 
                              cwd=repo_path, capture_output=True)
            logger.info("✅ Results pushed to GitHub")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Git push failed: {e}")
            return False

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 ENHANCED TECHNICAL ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, 
                        period: int = 14) -> Tuple[float, float]:
    """Calculate Stochastic Oscillator (%K and %D)"""
    lowest_low = low.rolling(period).min()
    highest_high = high.rolling(period).max()
    
    k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    d_percent = k_percent.rolling(3).mean()
    
    return float(k_percent.iloc[-1]), float(d_percent.iloc[-1])

def calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, 
                  period: int = 14) -> float:
    """Calculate Average Directional Index (ADX)"""
    # True Range
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # Directional Movement
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    
    # Smooth TR and DM
    atr = tr.rolling(period).mean()
    plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
    
    # ADX
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(period).mean()
    
    return float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else 0.0

def find_support_resistance(high: pd.Series, low: pd.Series, close: pd.Series, 
                           lookback: int = 20) -> Tuple[float, float]:
    """Find support and resistance levels"""
    recent_high = high.iloc[-lookback:].max()
    recent_low = low.iloc[-lookback:].min()
    
    # Find pivot points
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

def calculate_volume_profile(volume: pd.Series, close: pd.Series, 
                            bins: int = 20) -> Dict:
    """Calculate volume profile"""
    price_bins = np.linspace(close.min(), close.max(), bins)
    volume_dist = pd.cut(close, bins=price_bins, labels=False)
    
    volume_by_price = {}
    for i, vol in enumerate(volume):
        bin_idx = volume_dist.iloc[i] if not pd.isna(volume_dist.iloc[i]) else 0
        if bin_idx not in volume_by_price:
            volume_by_price[bin_idx] = 0
        volume_by_price[bin_idx] += vol
    
    # Find POC (Point of Control) - price level with highest volume
    poc_bin = max(volume_by_price, key=volume_by_price.get)
    poc_price = price_bins[poc_bin] if poc_bin < len(price_bins) else close.mean()
    
    return {
        'poc_price': float(poc_price),
        'volume_distribution': volume_by_price
    }

def calculate_obv(close: pd.Series, volume: pd.Series) -> float:
    """Calculate On-Balance Volume"""
    obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
    return float(obv.iloc[-1])

def detect_chart_patterns(high: pd.Series, low: pd.Series, close: pd.Series) -> List[str]:
    """Detect common chart patterns"""
    patterns = []
    
    # Double bottom pattern
    if len(close) >= 20:
        recent_lows = low.iloc[-20:].nsmallest(2)
        if len(recent_lows) == 2:
            low1, low2 = recent_lows.iloc[0], recent_lows.iloc[1]
            if abs(low1 - low2) / low1 < 0.02:  # Within 2%
                patterns.append("Double Bottom")
    
    # Head and shoulders (simplified)
    if len(high) >= 30:
        recent_highs = high.iloc[-30:].nlargest(3)
        if len(recent_highs) == 3:
            # Check if middle high is highest
            sorted_highs = sorted(recent_highs.values)
            if sorted_highs[1] > sorted_highs[0] and sorted_highs[1] > sorted_highs[2]:
                patterns.append("Head & Shoulders")
    
    # Ascending triangle
    if len(high) >= 20:
        recent_high = high.iloc[-20:].max()
        recent_low = low.iloc[-20:].min()
        if abs(recent_high - high.iloc[-1]) / recent_high < 0.01:
            if low.iloc[-1] > recent_low * 1.05:
                patterns.append("Ascending Triangle")
    
    return patterns

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 ENHANCED STOCK ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_single_stock_enhanced(ticker: str, sector: str = 'Unknown', 
                                   market: str = 'US') -> Optional[Dict]:
    """Enhanced stock analysis with additional indicators"""
    try:
        # Try cache first
        data = get_cached_data(ticker)
        stock = None
        if data is None:
            stock = yf.Ticker(ticker)
            data = stock.history(period='1y')
            if data.empty or len(data) < 60:
                return None
            cache_data(ticker, data)
        
        # Get info if we have stock object, otherwise try to fetch
        if stock is None:
            stock = yf.Ticker(ticker)
        try:
            info = stock.info
        except:
            info = {}
        close = data['Close']
        high = data['High']
        low = data['Low']
        volume = data['Volume']
        open_price = data['Open']
        
        current_close = float(close.iloc[-1])
        prev_close = float(close.iloc[-2])
        
        # Basic indicators (from original)
        sma_50 = float(close.rolling(50).mean().iloc[-1])
        sma_200 = float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else np.nan
        
        # RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = float((100 - (100 / (1 + rs))).iloc[-1])
        
        # MACD
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd = float(macd_line.iloc[-1])
        macd_signal = float(signal_line.iloc[-1])
        macd_crossover = macd > macd_signal and float(macd_line.iloc[-2]) <= float(signal_line.iloc[-2])
        
        # Volume ratio
        avg_volume = float(volume.iloc[-21:-1].mean())
        current_volume = float(volume.iloc[-1])
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        # ATR
        tr = np.maximum(high - low, np.maximum(abs(high - close.shift()), abs(low - close.shift())))
        atr = float(tr.rolling(14).mean().iloc[-1])
        atr_pct = (atr / current_close) * 100
        
        # NEW: Enhanced indicators
        stoch_k, stoch_d = calculate_stochastic(high, low, close)
        adx = calculate_adx(high, low, close)
        support, resistance = find_support_resistance(high, low, close)
        volume_profile = calculate_volume_profile(volume, close)
        obv = calculate_obv(close, volume)
        patterns = detect_chart_patterns(high, low, close)
        
        # Distance to support/resistance
        dist_to_support = ((current_close - support) / support) * 100
        dist_to_resistance = ((resistance - current_close) / current_close) * 100
        
        # Weekly and monthly changes
        weekly_change = ((current_close / float(close.iloc[-6])) - 1) * 100 if len(close) >= 6 else 0
        monthly_change = ((current_close / float(close.iloc[-22])) - 1) * 100 if len(close) >= 22 else 0
        
        # Bollinger Bands
        bb_sma = close.rolling(20).mean()
        bb_std = close.rolling(20).std()
        bb_upper = bb_sma + (bb_std * 2)
        bb_lower = bb_sma - (bb_std * 2)
        bb_width = (float(bb_upper.iloc[-1]) - float(bb_lower.iloc[-1])) / float(bb_sma.iloc[-1])
        bb_squeeze = bb_width < 0.1
        bb_position = (current_close - float(bb_lower.iloc[-1])) / (float(bb_upper.iloc[-1]) - float(bb_lower.iloc[-1]))
        
        # Enhanced scoring
        score = 0
        signals = []
        
        # Trend signals
        if current_close > sma_50:
            score += 10
            signals.append('Above 50 SMA')
        
        breakout_50 = current_close > sma_50 and prev_close <= float(close.rolling(50).mean().iloc[-2])
        if breakout_50:
            score += 15
            signals.append('🚀 Breakout 50 SMA')
        
        if not np.isnan(sma_200) and current_close > sma_200:
            score += 10
            signals.append('Above 200 SMA')
        
        # Golden cross
        if not np.isnan(sma_200) and len(close) >= 201:
            prev_sma_50 = float(close.rolling(50).mean().iloc[-2])
            prev_sma_200 = float(close.rolling(200).mean().iloc[-2])
            if sma_50 > sma_200 and prev_sma_50 <= prev_sma_200:
                score += 20
                signals.append('🌟 Golden Cross!')
        
        # RSI
        if rsi < 30:
            score += 15
            signals.append(f'RSI Oversold ({rsi:.1f})')
        elif 50 < rsi < 70:
            score += 5
            signals.append(f'RSI Bullish ({rsi:.1f})')
        elif rsi > 70:
            score -= 8
            signals.append(f'⚠️ RSI Overbought ({rsi:.1f})')
        
        # MACD
        if macd_crossover:
            score += 15
            signals.append('🔄 MACD Crossover')
        elif macd > macd_signal:
            score += 5
            signals.append('MACD Bullish')
        
        # NEW: Stochastic
        if stoch_k < 20 and stoch_d < 20:
            score += 10
            signals.append(f'Stoch Oversold (K:{stoch_k:.1f}, D:{stoch_d:.1f})')
        elif stoch_k > 80 and stoch_d > 80:
            score -= 5
            signals.append(f'⚠️ Stoch Overbought')
        
        # NEW: ADX (trend strength)
        if adx > 25:
            score += 8
            signals.append(f'Strong Trend (ADX:{adx:.1f})')
        elif adx < 20:
            score -= 3
            signals.append(f'Weak Trend (ADX:{adx:.1f})')
        
        # Volume
        if volume_ratio > 1.5:
            score += 12
            signals.append(f'📊 Volume Surge ({volume_ratio:.1f}x)')
        elif volume_ratio > 1.0:
            score += 5
        
        # NEW: OBV trend
        obv_trend = obv > float(calculate_obv(close.iloc[:-5], volume.iloc[:-5])) if len(close) > 5 else False
        if obv_trend:
            score += 5
            signals.append('OBV Rising')
        
        # NEW: Support/Resistance
        if dist_to_support < 2:
            score += 8
            signals.append(f'Near Support (${support:.2f})')
        if dist_to_resistance < 2:
            score -= 5
            signals.append(f'Near Resistance (${resistance:.2f})')
        
        # NEW: Chart patterns
        if patterns:
            score += len(patterns) * 5
            signals.extend([f'Pattern: {p}' for p in patterns])
        
        # Volatility
        if 1 < atr_pct < 5:
            score += 5
            signals.append('ATR Favorable')
        elif atr_pct >= 5:
            score -= 5
            signals.append(f'⚠️ High ATR ({atr_pct:.1f}%)')
        
        # Bollinger Squeeze
        if bb_squeeze:
            score += 8
            signals.append('🔧 BB Squeeze')
        
        # NEW: BB position
        if bb_position < 0.2:
            score += 5
            signals.append('Near BB Lower')
        elif bb_position > 0.8:
            score -= 3
        
        # Analyst rating
        rec = info.get('recommendationKey', 'hold')
        if rec in ['strong_buy', 'buy']:
            score += 10
            signals.append(f'👔 Analyst: {rec}')
        elif rec == 'sell':
            score -= 8
            signals.append(f'👔 Analyst: {rec}')
        
        # Institutional ownership
        inst = info.get('heldPercentInstitutions', 0)
        if inst and inst > 0.6:
            score += 8
            signals.append(f'🏛️ High Inst ({inst*100:.0f}%)')
        
        # Momentum
        if weekly_change > 5:
            score += 10
            signals.append(f'📈 Weekly +{weekly_change:.1f}%')
        elif weekly_change > 2:
            score += 5
        elif weekly_change < -5:
            score -= 5
        
        # Rating
        if score >= 80:
            rating = '🟢 STRONG BUY'
        elif score >= 60:
            rating = '🟡 BUY'
        elif score >= 40:
            rating = '👀 WATCH'
        else:
            rating = '⚪ NEUTRAL'
        
        return {
            'Ticker': ticker,
            'Company': info.get('shortName', ticker)[:25] if info else ticker,
            'Market': market,
            'Sector': sector,
            'Close': round(current_close, 2),
            'Change%': round(((current_close / prev_close) - 1) * 100, 2),
            'Week%': round(weekly_change, 2),
            'Month%': round(monthly_change, 2),
            'RSI': round(rsi, 1),
            'Stoch_K': round(stoch_k, 1),
            'Stoch_D': round(stoch_d, 1),
            'ADX': round(adx, 1),
            'MACD': round(macd, 3),
            'Volume_Ratio': round(volume_ratio, 2),
            'ATR%': round(atr_pct, 2),
            'Support': round(support, 2),
            'Resistance': round(resistance, 2),
            'Dist_Support%': round(dist_to_support, 2),
            'Dist_Resistance%': round(dist_to_resistance, 2),
            'OBV': round(obv, 0),
            'BB_Position': round(bb_position, 2),
            'Patterns': patterns,
            'Score': score,
            'Rating': rating,
            'Signals': signals,
            'SMA_50': round(sma_50, 2),
            'SMA_200': round(sma_200, 2) if not np.isnan(sma_200) else None,
            'Timestamp': datetime.now().isoformat(),
        }
        
    except Exception as e:
        logger.debug(f"Error analyzing {ticker}: {e}")
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 PARALLEL SCANNER
# ═══════════════════════════════════════════════════════════════════════════════

def run_scanner_analysis_parallel(max_workers: int = 10) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Run scanner with parallel processing for better performance
    """
    # Import from market_tickers to avoid ib_insync import issues
    try:
        from market_tickers import US_SECTORS, BRAZIL_SECTORS
    except ImportError:
        # Fallback: try importing from stockmonitor (may fail in Streamlit)
        try:
            from stockmonitor import US_SECTORS, BRAZIL_SECTORS
        except (ImportError, RuntimeError):
            # If both fail, define minimal sets
            US_SECTORS = {'Technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']}
            BRAZIL_SECTORS = {'Banks': ['ITUB4.SA', 'BBDC4.SA']}
    
    all_results = []
    tradeable_results = []
    non_tradeable_results = []
    
    # Flatten all tickers
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
    
    logger.info(f"🔍 Scanning {len(us_tickers)} US + {len(br_tickers)} BR = {total} total stocks (parallel, {max_workers} workers)...")
    
    # Process in parallel
    completed = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ticker = {
            executor.submit(analyze_single_stock_enhanced, ticker, sector, market): (ticker, sector, market)
            for ticker, sector, market in all_tickers
        }
        
        for future in as_completed(future_to_ticker):
            ticker, sector, market = future_to_ticker[future]
            try:
                result = future.result(timeout=30)
                
                if result and result['Score'] >= 30:
                    all_results.append(result)
                    
                    # IBKR tradeability check removed - assume all US stocks are tradeable
                    if market == 'US':
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
    
    # Sort by score
    all_results.sort(key=lambda x: x['Score'], reverse=True)
    tradeable_results.sort(key=lambda x: x['Score'], reverse=True)
    non_tradeable_results.sort(key=lambda x: x['Score'], reverse=True)
    
    logger.info(f"✅ Found {len(all_results)} opportunities ({len(tradeable_results)} tradeable, {len(non_tradeable_results)} not tradeable)")
    
    return all_results, tradeable_results, non_tradeable_results

# ═══════════════════════════════════════════════════════════════════════════════
# 🎯 MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point for enhanced scanner"""
    parser = argparse.ArgumentParser(
        description='Enhanced Swing Trade Scanner with Parallel Processing',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--scan', action='store_true', help='Run scanner')
    parser.add_argument('--max-workers', type=int, default=10, help='Number of parallel workers')
    parser.add_argument('--min-score', type=int, default=30, help='Minimum score to include')
    parser.add_argument('--save-json', action='store_true', help='Save results to JSON')
    parser.add_argument('--save-csv', action='store_true', help='Save results to CSV')
    parser.add_argument('--github-push', action='store_true', help='Push results to GitHub')
    parser.add_argument('--github-url', type=str, help='GitHub repository URL')
    parser.add_argument('--setup-git', action='store_true', help='Setup git repository')
    
    args = parser.parse_args()
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   🤖 ENHANCED SWING TRADE SCANNER v6.0                                       ║
║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                      ║
║   High-Performance Parallel Scanner                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    if args.setup_git and args.github_url:
        setup_git_repo(remote_url=args.github_url)
        logger.info("✅ Git repository setup complete")
        return
    
    if args.scan:
        logger.info("🚀 Starting enhanced scanner...")
        start_time = time.time()
        
        # Run parallel scan
        all_results, tradeable_results, non_tradeable_results = run_scanner_analysis_parallel(
            max_workers=args.max_workers
        )
        
        elapsed = time.time() - start_time
        logger.info(f"⏱️ Scan completed in {elapsed:.2f} seconds")
        
        # Filter by min score
        filtered_results = [r for r in all_results if r['Score'] >= args.min_score]
        us_results = [r for r in filtered_results if r['Market'] == 'US']
        br_results = [r for r in filtered_results if r['Market'] == 'Brazil']
        
        # Display results
        print(f"\n{'═'*80}")
        print(f"🇺🇸 TOP 20 USA (Score >= {args.min_score})")
        print(f"{'═'*80}")
        print(f"{'#':>2} {'Ticker':<8} {'Price':>10} {'24h':>8} {'Week':>8} {'Score':>6} {'Rating':<15}")
        print(f"{'─'*80}")
        
        for i, r in enumerate(us_results[:20], 1):
            print(f"{i:>2} {r['Ticker']:<8} ${r['Close']:>8.2f} {r['Change%']:>+7.2f}% {r['Week%']:>+7.2f}% {r['Score']:>6} {r['Rating']:<15}")
        
        print(f"\n{'═'*80}")
        print(f"🇧🇷 TOP 20 BRAZIL (Score >= {args.min_score})")
        print(f"{'═'*80}")
        print(f"{'#':>2} {'Ticker':<12} {'Price':>10} {'24h':>8} {'Week':>8} {'Score':>6} {'Rating':<15}")
        print(f"{'─'*80}")
        
        for i, r in enumerate(br_results[:20], 1):
            ticker = r['Ticker'].replace('.SA', '')
            print(f"{i:>2} {ticker:<12} R${r['Close']:>7.2f} {r['Change%']:>+7.2f}% {r['Week%']:>+7.2f}% {r['Score']:>6} {r['Rating']:<15}")
        
        # Save results
        if args.save_json:
            save_results_to_json(filtered_results)
        
        if args.save_csv:
            save_results_to_csv(filtered_results)
        
        # GitHub push
        if args.github_push:
            commit_and_push_results()
        
        print(f"\n{'═'*80}")
        print(f"📊 SUMMARY")
        print(f"{'═'*80}")
        print(f"   Total scanned: {len(all_results)}")
        print(f"   US stocks: {len(us_results)}")
        print(f"   BR stocks: {len(br_results)}")
        print(f"   Tradeable: {len(tradeable_results)}")
        print(f"   Scan time: {elapsed:.2f}s")
        print(f"{'═'*80}\n")
    else:
        print("Usage:")
        print("  python stockmonitor_enhanced.py --scan --save-json --save-csv")
        print("  python stockmonitor_enhanced.py --scan --github-push --github-url <url>")
        print("  python stockmonitor_enhanced.py --setup-git --github-url <url>")
        print("\nUse --help for all options.")


if __name__ == "__main__":
    main()
