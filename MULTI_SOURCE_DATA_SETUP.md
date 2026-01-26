# 📊 Multi-Source Financial Data Setup

## Overview

The scanner now supports **multiple financial data APIs** with automatic fallback, ensuring maximum ticker coverage even when primary sources fail.

## Data Sources (Priority Order)

### 1. **yfinance** (Primary) ⭐
- **Cost**: Free
- **API Key**: Not required
- **Rate Limits**: None (but may throttle)
- **Coverage**: US + International stocks
- **Status**: Always enabled

### 2. **Alpha Vantage** (Fallback 1)
- **Cost**: Free tier available
- **API Key**: Required (free at https://www.alphavantage.co/support/#api-key)
- **Rate Limits**: 5 calls/minute, 500 calls/day
- **Coverage**: US stocks only
- **Status**: Enabled if API key provided

### 3. **Polygon.io** (Fallback 2)
- **Cost**: Free tier available
- **API Key**: Required (free at https://polygon.io/)
- **Rate Limits**: 5 calls/minute
- **Coverage**: US stocks only
- **Status**: Enabled if API key provided

### 4. **IEX Cloud** (Fallback 3)
- **Cost**: Free tier available
- **API Key**: Required (free at https://iexcloud.io/)
- **Rate Limits**: 50,000 messages/month
- **Coverage**: US stocks only
- **Status**: Enabled if API key provided

### 5. **Yahoo Finance Direct** (Last Resort)
- **Cost**: Free
- **API Key**: Not required
- **Rate Limits**: None (but may throttle)
- **Coverage**: US + International
- **Status**: Always enabled as last resort

---

## Setup Instructions

### Option 1: Use yfinance Only (Default)
**No setup required!** The scanner works out of the box with yfinance.

### Option 2: Add Fallback APIs (Recommended)

#### Step 1: Get Free API Keys

1. **Alpha Vantage**:
   - Visit: https://www.alphavantage.co/support/#api-key
   - Sign up for free API key
   - Copy your API key

2. **Polygon.io** (Optional):
   - Visit: https://polygon.io/
   - Sign up for free tier
   - Copy your API key

3. **IEX Cloud** (Optional):
   - Visit: https://iexcloud.io/
   - Sign up for free tier
   - Copy your API key

#### Step 2: Set Environment Variables

**For Local Development:**
```bash
# Add to your ~/.bashrc or ~/.zshrc
export ALPHA_VANTAGE_API_KEY="your_key_here"
export POLYGON_API_KEY="your_key_here"  # Optional
export IEX_CLOUD_API_KEY="your_key_here"  # Optional
```

**For Streamlit Cloud:**
1. Go to your app settings
2. Click "Secrets" (or "Environment Variables")
3. Add:
   ```toml
   ALPHA_VANTAGE_API_KEY = "your_key_here"
   POLYGON_API_KEY = "your_key_here"
   IEX_CLOUD_API_KEY = "your_key_here"
   ```

#### Step 3: Verify Setup

Test the multi-source fetcher:
```bash
python data_sources.py
```

---

## How It Works

### Automatic Fallback Chain

When fetching data for a ticker:

1. **Try yfinance** (primary)
   - ✅ Success → Return data
   - ❌ Fail → Try next source

2. **Try Alpha Vantage** (if API key available)
   - ✅ Success → Return data
   - ❌ Fail → Try next source

3. **Try Polygon.io** (if API key available)
   - ✅ Success → Return data
   - ❌ Fail → Try next source

4. **Try IEX Cloud** (if API key available)
   - ✅ Success → Return data
   - ❌ Fail → Try next source

5. **Try Yahoo Finance Direct** (last resort)
   - ✅ Success → Return data
   - ❌ Fail → Skip ticker (log at DEBUG level)

### Benefits

- **Higher Success Rate**: If one API fails, others can succeed
- **Better Coverage**: Some APIs may have data for delisted/inactive stocks
- **Rate Limit Handling**: Automatic delays between API calls
- **Graceful Degradation**: Works even if no API keys are provided

---

## Usage

### In Code

The scanner automatically uses multi-source fetching:

```python
from data_sources import fetch_stock_data

# Automatically tries all available sources
data = fetch_stock_data('AAPL')
```

### In Scanner

The `institutional_scanner.py` automatically uses multi-source fetching if `data_sources.py` is available. No code changes needed!

---

## Rate Limits & Best Practices

### Alpha Vantage
- **Limit**: 5 calls/minute, 500/day
- **Strategy**: Scanner adds 0.2s delay between calls
- **Tip**: Use for critical fallback only

### Polygon.io
- **Limit**: 5 calls/minute
- **Strategy**: Scanner adds 0.2s delay between calls
- **Tip**: Good for real-time data

### IEX Cloud
- **Limit**: 50,000 messages/month
- **Strategy**: Efficient for batch scanning
- **Tip**: Best for high-volume scanning

### Recommendations

1. **Start with yfinance only** - It's free and works for most stocks
2. **Add Alpha Vantage** - Good free tier, helps with delisted stocks
3. **Add others as needed** - If you hit rate limits or need more coverage

---

## Troubleshooting

### "All sources failed for ticker"
- **Cause**: Ticker may be delisted, invalid, or all APIs are down
- **Solution**: This is expected for some tickers - scanner will skip them

### "API key not found"
- **Cause**: Environment variable not set
- **Solution**: Set API key in environment or Streamlit Cloud secrets

### Rate Limit Errors
- **Cause**: Too many API calls too quickly
- **Solution**: Scanner automatically adds delays, but you may need to reduce parallel workers

### Brazilian Stocks (.SA)
- **Note**: Most APIs (Alpha Vantage, Polygon, IEX) only support US stocks
- **Solution**: yfinance handles BR stocks, so they'll use yfinance or fail gracefully

---

## Files

- **`data_sources.py`**: Multi-source data fetcher module
- **`institutional_scanner.py`**: Updated to use multi-source fetching
- **`requirements.txt`**: No additional dependencies needed (uses existing `requests`)

---

## Cost Summary

| Source | Free Tier | Paid Tier |
|--------|-----------|-----------|
| yfinance | ✅ Unlimited | N/A |
| Alpha Vantage | ✅ 500 calls/day | $49.99/month (unlimited) |
| Polygon.io | ✅ 5 calls/min | $99/month (unlimited) |
| IEX Cloud | ✅ 50k messages/month | $9/month (1M messages) |

**Recommendation**: Start with free tiers - they're sufficient for most scanning needs!

---

## Next Steps

1. ✅ **Test locally**: `python data_sources.py`
2. ✅ **Add API keys** (optional but recommended)
3. ✅ **Deploy to Streamlit Cloud** with secrets configured
4. ✅ **Monitor logs** to see which sources are being used

---

**Status**: ✅ Multi-source support implemented  
**Default**: Works with yfinance only (no setup needed)  
**Enhanced**: Add API keys for better coverage
