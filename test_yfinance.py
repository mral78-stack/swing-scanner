#!/usr/bin/env python3
"""
Quick test script to verify yfinance installation
"""

import sys

print("Python version:", sys.version)
print("\n" + "="*60)
print("Testing yfinance import...")
print("="*60)

try:
    import yfinance as yf
    print("✅ yfinance imported successfully")
    print(f"   Version: {yf.__version__ if hasattr(yf, '__version__') else 'unknown'}")
    
    # Quick test
    print("\nTesting data fetch...")
    ticker = yf.Ticker("AAPL")
    info = ticker.info
    print("✅ Successfully fetched data for AAPL")
    print(f"   Company: {info.get('shortName', 'N/A')}")
    
except ImportError as e:
    print("❌ yfinance import failed!")
    print(f"   Error: {e}")
    print("\nTo fix:")
    print("  pip install yfinance")
    sys.exit(1)
except Exception as e:
    print(f"⚠️  yfinance imported but test failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✅ All tests passed!")
print("="*60)
