#!/usr/bin/env python3
"""
Multi-Source Financial Data Fetcher
Supports multiple APIs as fallbacks for robust data retrieval
"""

import logging
import time
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import requests

logger = logging.getLogger('DataSources')

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 DATA SOURCE 1: YAHOO FINANCE (yfinance) - Primary
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_yfinance(ticker: str, period: str = '1y') -> pd.DataFrame | None:
    """Fetch data from Yahoo Finance via yfinance"""
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, timeout=10)
        
        if data is not None and not data.empty and len(data) >= 60:
            return data
        return None
    except Exception as e:
        logger.debug(f"yfinance failed for {ticker}: {e}")
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 DATA SOURCE 2: ALPHA VANTAGE - Fallback
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_alphavantage(ticker: str, api_key: str | None = None) -> pd.DataFrame | None:
    """
    Fetch data from Alpha Vantage
    Free tier: 5 API calls per minute, 500 calls per day
    Get free API key: https://www.alphavantage.co/support/#api-key
    """
    if not api_key:
        # Try to get from environment or use demo key (limited)
        import os
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if not api_key:
            return None  # Skip if no API key
    
    try:
        # Remove .SA suffix for Alpha Vantage (US stocks only)
        clean_ticker = ticker.replace('.SA', '')
        
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': clean_ticker,
            'apikey': api_key,
            'outputsize': 'full',  # Get up to 20 years of data
            'datatype': 'json'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'Error Message' in data or 'Note' in data:
            logger.debug(f"Alpha Vantage error for {ticker}: {data.get('Error Message', data.get('Note'))}")
            return None
        
        if 'Time Series (Daily)' not in data:
            return None
        
        # Convert to DataFrame
        time_series = data['Time Series (Daily)']
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        # Rename columns to match yfinance format
        df = df.rename(columns={
            '1. open': 'Open',
            '2. high': 'High',
            '3. low': 'Low',
            '4. close': 'Close',
            '5. adjusted close': 'Close',  # Use adjusted close
            '6. volume': 'Volume'
        })
        
        # Select and convert columns
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
        
        # Filter to last year if needed
        if len(df) > 252:
            df = df.iloc[-252:]
        
        if len(df) >= 60:
            return df
        
        return None
    except Exception as e:
        logger.debug(f"Alpha Vantage failed for {ticker}: {e}")
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 DATA SOURCE 3: POLYGON.IO - Fallback
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_polygon(ticker: str, api_key: str | None = None) -> pd.DataFrame | None:
    """
    Fetch data from Polygon.io
    Free tier: 5 API calls per minute
    Get free API key: https://polygon.io/
    """
    if not api_key:
        import os
        api_key = os.getenv('POLYGON_API_KEY')
        if not api_key:
            return None
    
    try:
        # Remove .SA suffix for Polygon (US stocks only)
        clean_ticker = ticker.replace('.SA', '')
        
        # Get data for last year
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        url = f"https://api.polygon.io/v2/aggs/ticker/{clean_ticker}/range/1/day/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
        params = {
            'adjusted': 'true',
            'sort': 'asc',
            'limit': 50000,
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') != 'OK' or 'results' not in data:
            return None
        
        # Convert to DataFrame
        results = data['results']
        df_data = []
        for bar in results:
            df_data.append({
                'Open': bar['o'],
                'High': bar['h'],
                'Low': bar['l'],
                'Close': bar['c'],
                'Volume': bar['v'],
                'Timestamp': pd.to_datetime(bar['t'], unit='ms')
            })
        
        df = pd.DataFrame(df_data)
        df.set_index('Timestamp', inplace=True)
        df = df.sort_index()
        
        if len(df) >= 60:
            return df
        
        return None
    except Exception as e:
        logger.debug(f"Polygon.io failed for {ticker}: {e}")
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 DATA SOURCE 4: IEX CLOUD - Fallback
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_iexcloud(ticker: str, api_key: str | None = None) -> pd.DataFrame | None:
    """
    Fetch data from IEX Cloud
    Free tier: 50,000 messages per month
    Get free API key: https://iexcloud.io/
    """
    if not api_key:
        import os
        api_key = os.getenv('IEX_CLOUD_API_KEY')
        if not api_key:
            return None
    
    try:
        # Remove .SA suffix for IEX Cloud (US stocks only)
        clean_ticker = ticker.replace('.SA', '')
        
        url = f"https://cloud.iexapis.com/stable/stock/{clean_ticker}/chart/1y"
        params = {
            'token': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data or len(data) == 0:
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df = df.sort_index()
        
        # Rename columns
        df = df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        })
        
        # Select required columns
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
        
        if len(df) >= 60:
            return df
        
        return None
    except Exception as e:
        logger.debug(f"IEX Cloud failed for {ticker}: {e}")
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 DATA SOURCE 5: YAHOO FINANCE DIRECT (Web Scraping Fallback)
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_yahoo_direct(ticker: str) -> pd.DataFrame | None:
    """
    Direct Yahoo Finance web scraping as last resort
    Note: This is less reliable and may violate ToS - use sparingly
    """
    try:
        import yfinance as yf
        # Try alternative method
        stock = yf.Ticker(ticker)
        
        # Try different periods
        for period in ['1y', '6mo', '3mo']:
            try:
                data = stock.history(period=period, timeout=15)
                if data is not None and not data.empty and len(data) >= 60:
                    return data
            except:
                continue
        
        return None
    except Exception as e:
        logger.debug(f"Yahoo direct failed for {ticker}: {e}")
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 MULTI-SOURCE DATA FETCHER WITH FALLBACKS
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_stock_data(ticker: str, 
                    period: str = '1y',
                    use_alphavantage: bool = True,
                    use_polygon: bool = True,
                    use_iexcloud: bool = True,
                    alphavantage_key: str | None = None,
                    polygon_key: str | None = None,
                    iexcloud_key: str | None = None) -> pd.DataFrame | None:
    """
    Fetch stock data with automatic fallback to multiple sources
    
    Priority order:
    1. yfinance (primary - free, no API key needed)
    2. Alpha Vantage (if API key provided)
    3. Polygon.io (if API key provided)
    4. IEX Cloud (if API key provided)
    5. Yahoo Finance direct (last resort)
    
    Args:
        ticker: Stock ticker symbol
        period: Data period (for yfinance)
        use_alphavantage: Enable Alpha Vantage fallback
        use_polygon: Enable Polygon.io fallback
        use_iexcloud: Enable IEX Cloud fallback
        alphavantage_key: Alpha Vantage API key (or set ALPHA_VANTAGE_API_KEY env var)
        polygon_key: Polygon.io API key (or set POLYGON_API_KEY env var)
        iexcloud_key: IEX Cloud API key (or set IEX_CLOUD_API_KEY env var)
    
    Returns:
        DataFrame with OHLCV data or None if all sources fail
    """
    sources_tried = []
    
    # 1. Try yfinance first (primary - no API key needed)
    logger.debug(f"Trying yfinance for {ticker}...")
    data = fetch_yfinance(ticker, period)
    if data is not None:
        logger.debug(f"✅ yfinance succeeded for {ticker}")
        return data
    sources_tried.append("yfinance")
    
    # 2. Try Alpha Vantage (if enabled and key available)
    if use_alphavantage:
        logger.debug(f"Trying Alpha Vantage for {ticker}...")
        data = fetch_alphavantage(ticker, alphavantage_key)
        if data is not None:
            logger.debug(f"✅ Alpha Vantage succeeded for {ticker}")
            return data
        sources_tried.append("alphavantage")
        time.sleep(0.2)  # Rate limit: 5 calls/min
    
    # 3. Try Polygon.io (if enabled and key available)
    if use_polygon:
        logger.debug(f"Trying Polygon.io for {ticker}...")
        data = fetch_polygon(ticker, polygon_key)
        if data is not None:
            logger.debug(f"✅ Polygon.io succeeded for {ticker}")
            return data
        sources_tried.append("polygon")
        time.sleep(0.2)  # Rate limit: 5 calls/min
    
    # 4. Try IEX Cloud (if enabled and key available)
    if use_iexcloud:
        logger.debug(f"Trying IEX Cloud for {ticker}...")
        data = fetch_iexcloud(ticker, iexcloud_key)
        if data is not None:
            logger.debug(f"✅ IEX Cloud succeeded for {ticker}")
            return data
        sources_tried.append("iexcloud")
    
    # 5. Last resort: Try Yahoo Finance direct with different methods
    logger.debug(f"Trying Yahoo Finance direct for {ticker}...")
    data = fetch_yahoo_direct(ticker)
    if data is not None:
        logger.debug(f"✅ Yahoo Finance direct succeeded for {ticker}")
        return data
    sources_tried.append("yahoo_direct")
    
    # All sources failed
    logger.debug(f"❌ All sources failed for {ticker}: {sources_tried}")
    return None

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 GET STOCK INFO (Company Information)
# ═══════════════════════════════════════════════════════════════════════════════

def get_stock_info(ticker: str) -> dict | None:
    """Get stock info/company information"""
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info = stock.info
        return info if info else None
    except Exception as e:
        logger.debug(f"Failed to get info for {ticker}: {e}")
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# 🧪 TEST FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Test with a few tickers
    test_tickers = ['AAPL', 'MSFT', 'GOOGL']
    
    for ticker in test_tickers:
        print(f"\n{'='*60}")
        print(f"Testing {ticker}")
        print(f"{'='*60}")
        
        data = fetch_stock_data(ticker)
        if data is not None:
            print(f"✅ Success! Got {len(data)} days of data")
            print(f"   Latest close: ${data['Close'].iloc[-1]:.2f}")
        else:
            print("❌ Failed to fetch data")
