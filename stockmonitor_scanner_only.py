#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   🔍 SWING TRADE SCANNER - SCANNER ONLY (No Trading Execution)              ║
║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                      ║
║   Pure Scanner for US & BR Markets - No IBKR/TWS Required                   ║
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
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings

warnings.filterwarnings('ignore')

# Import yfinance for market data
import yfinance as yf

# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 LOGGING CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('StockScanner')

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 MARKET TICKER DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Import from market_tickers if available, otherwise define here
try:
    from market_tickers import US_SECTORS, BRAZIL_SECTORS
except ImportError:
    # Fallback definitions (minimal set)
    US_SECTORS = {
        'Technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA'],
        'Finance': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
    }
    BRAZIL_SECTORS = {
        'Banks': ['ITUB4.SA', 'BBDC4.SA', 'BBAS3.SA'],
        'Energy': ['PETR4.SA', 'ELET3.SA'],
    }

# ═══════════════════════════════════════════════════════════════════════════════
# 🔍 STOCK ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_single_stock(ticker: str, sector: str = 'Unknown', market: str = 'US') -> Optional[Dict]:
    """Analyze a single stock with technical analysis"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period='1y')
        
        if data.empty or len(data) < 60:
            return None
        
        info = stock.info
        close = data['Close']
        high = data['High']
        low = data['Low']
        volume = data['Volume']
        
        current_close = float(close.iloc[-1])
        prev_close = float(close.iloc[-2])
        
        # Calculate indicators
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
        
        # Weekly and monthly changes
        weekly_change = ((current_close / float(close.iloc[-6])) - 1) * 100 if len(close) >= 6 else 0
        monthly_change = ((current_close / float(close.iloc[-22])) - 1) * 100 if len(close) >= 22 else 0
        
        # Score calculation
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
        
        # Volume
        if volume_ratio > 1.5:
            score += 12
            signals.append(f'📊 Volume Surge ({volume_ratio:.1f}x)')
        elif volume_ratio > 1.0:
            score += 5
        
        # Volatility
        if 1 < atr_pct < 5:
            score += 5
            signals.append('ATR Favorable')
        elif atr_pct >= 5:
            score -= 5
            signals.append(f'⚠️ High ATR ({atr_pct:.1f}%)')
        
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
            'MACD': round(macd, 3),
            'Volume_Ratio': round(volume_ratio, 2),
            'ATR%': round(atr_pct, 2),
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

def run_scanner_analysis(max_workers: int = 10, min_score: int = 30) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Run the stock scanner and return results for both markets.
    No IBKR/TWS required - pure scanner only.
    
    Returns:
        Tuple of (all_results, us_results, br_results)
    """
    all_results = []
    us_results = []
    br_results = []
    
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
            executor.submit(analyze_single_stock, ticker, sector, market): (ticker, sector, market)
            for ticker, sector, market in all_tickers
        }
        
        for future in as_completed(future_to_ticker):
            ticker, sector, market = future_to_ticker[future]
            try:
                result = future.result(timeout=30)
                
                if result and result['Score'] >= min_score:
                    all_results.append(result)
                    
                    if market == 'US':
                        us_results.append(result)
                    else:
                        br_results.append(result)
                
                completed += 1
                if completed % 50 == 0:
                    logger.info(f"   Progress: {completed}/{total} ({completed*100//total}%)")
                    
            except Exception as e:
                completed += 1
                logger.debug(f"Error processing {ticker}: {e}")
                continue
    
    # Sort by score
    all_results.sort(key=lambda x: x['Score'], reverse=True)
    us_results.sort(key=lambda x: x['Score'], reverse=True)
    br_results.sort(key=lambda x: x['Score'], reverse=True)
    
    logger.info(f"✅ Found {len(all_results)} opportunities ({len(us_results)} US, {len(br_results)} BR)")
    
    return all_results, us_results, br_results

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Swing Trade Scanner (Scanner Only - No Trading)',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--scan', action='store_true', help='Run scanner')
    parser.add_argument('--max-workers', type=int, default=10, help='Number of parallel workers')
    parser.add_argument('--min-score', type=int, default=30, help='Minimum score to include')
    parser.add_argument('--save-json', action='store_true', help='Save results to JSON')
    parser.add_argument('--save-csv', action='store_true', help='Save results to CSV')
    
    args = parser.parse_args()
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   🔍 SWING TRADE SCANNER - SCANNER ONLY                                    ║
║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                      ║
║   Pure Scanner - No Trading Execution Required                               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    if args.scan:
        logger.info("🚀 Starting scanner...")
        start_time = datetime.now()
        
        all_results, us_results, br_results = run_scanner_analysis(
            max_workers=args.max_workers,
            min_score=args.min_score
        )
        
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"⏱️ Scan completed in {elapsed:.2f} seconds")
        
        # Display results
        print(f"\n{'═'*80}")
        print(f"🇺🇸 TOP 20 USA (Score >= {args.min_score})")
        print(f"{'═'*80}")
        print(f"{'#':>2} {'Ticker':<8} {'Price':>10} {'24h':>8} {'Week':>8} {'Month':>8} {'Score':>6} {'Rating':<15}")
        print(f"{'─'*80}")
        
        for i, r in enumerate(us_results[:20], 1):
            print(f"{i:>2} {r['Ticker']:<8} ${r['Close']:>8.2f} {r['Change%']:>+7.2f}% {r['Week%']:>+7.2f}% {r['Month%']:>+7.2f}% {r['Score']:>6} {r['Rating']:<15}")
        
        if not us_results:
            print("   No US stocks found with score >= " + str(args.min_score))
        
        print(f"\n{'═'*80}")
        print(f"🇧🇷 TOP 20 BRAZIL (Score >= {args.min_score})")
        print(f"{'═'*80}")
        print(f"{'#':>2} {'Ticker':<12} {'Price':>10} {'24h':>8} {'Week':>8} {'Month':>8} {'Score':>6} {'Rating':<15}")
        print(f"{'─'*80}")
        
        for i, r in enumerate(br_results[:20], 1):
            ticker = r['Ticker'].replace('.SA', '')
            print(f"{i:>2} {ticker:<12} R${r['Close']:>7.2f} {r['Change%']:>+7.2f}% {r['Week%']:>+7.2f}% {r['Month%']:>+7.2f}% {r['Score']:>6} {r['Rating']:<15}")
        
        if not br_results:
            print("   No BR stocks found with score >= " + str(args.min_score))
        
        # Save results
        if args.save_json:
            os.makedirs('scanner_results', exist_ok=True)
            filename = f"scanner_results/scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(all_results, f, indent=2)
            logger.info(f"💾 Results saved to {filename}")
        
        if args.save_csv:
            os.makedirs('scanner_results', exist_ok=True)
            filename = f"scanner_results/scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df = pd.DataFrame(all_results)
            df.to_csv(filename, index=False)
            logger.info(f"💾 Results saved to {filename}")
        
        # Summary
        print(f"\n{'═'*80}")
        print(f"📊 SUMMARY")
        print(f"{'═'*80}")
        print(f"   Total scanned: {len(all_results)}")
        print(f"   US stocks: {len(us_results)}")
        print(f"   BR stocks: {len(br_results)}")
        print(f"   Scan time: {elapsed:.2f}s")
        print(f"{'═'*80}\n")
    else:
        print("Usage:")
        print("  python stockmonitor_scanner_only.py --scan")
        print("  python stockmonitor_scanner_only.py --scan --min-score 60 --save-json --save-csv")
        print("\nUse --help for all options.")


if __name__ == "__main__":
    main()
