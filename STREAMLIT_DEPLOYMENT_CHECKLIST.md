# ✅ Streamlit Cloud Deployment Checklist

## Pre-Deployment

### 1. Verify requirements.txt
- [ ] File exists in **root directory** of repository
- [ ] Contains `yfinance>=0.2.28`
- [ ] All dependencies listed
- [ ] No syntax errors

### 2. Test Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Test yfinance
python test_yfinance.py

# Test Streamlit app
streamlit run streamlit_institutional.py
```

### 3. Verify File Structure
```
your-repo/
├── requirements.txt              ← Must be here
├── streamlit_institutional.py   ← Main app
├── institutional_scanner.py      ← Scanner module
├── market_tickers.py             ← Ticker definitions
└── ...
```

## Deployment Steps

### 1. Push to GitHub
```bash
git add requirements.txt
git add streamlit_institutional.py
git add institutional_scanner.py
git commit -m "Fix yfinance dependency"
git push
```

### 2. Streamlit Cloud Setup
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Select your repository
3. Set **Main file path**: `streamlit_institutional.py`
4. Click **Deploy**

### 3. Monitor Deployment
- Watch logs for dependency installation
- Look for: `Installing dependencies...`
- Verify: `Successfully installed yfinance-...`

## Troubleshooting

### If yfinance Still Missing

1. **Check Logs**
   - Streamlit Cloud → Your App → Logs
   - Look for installation errors

2. **Clear Cache**
   - Settings → Advanced → Clear cache and restart

3. **Verify requirements.txt**
   - Must be in root (not in subdirectory)
   - Must have `yfinance>=0.2.28`

4. **Check Python Version**
   - Streamlit Cloud uses Python 3.11
   - yfinance requires 3.7+ (should work)

5. **Try Explicit Version**
   ```txt
   yfinance==0.2.28
   ```

## Verification

After deployment:

1. **Open app** - Should load without errors
2. **Check dependencies** - Settings → Dependencies
3. **Run scan** - Should work if yfinance installed
4. **Check logs** - No import errors

## Files to Deploy

Essential files:
- ✅ `requirements.txt` (root)
- ✅ `streamlit_institutional.py`
- ✅ `institutional_scanner.py`
- ✅ `market_tickers.py`
- ✅ `stockmonitor_enhanced.py` (if used)

Optional:
- `stockmonitor_scanner_only.py`
- `streamlit_scanner.py`
- Documentation files

## Quick Fix Commands

```bash
# Test locally
python test_yfinance.py

# Verify requirements.txt
cat requirements.txt | grep yfinance

# Check file location
ls -la requirements.txt  # Should be in root
```

---

**Status**: Ready for deployment  
**Next**: Push to GitHub and deploy on Streamlit Cloud
