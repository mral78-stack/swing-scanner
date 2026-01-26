# 📦 Repository Upload Checklist

## ⭐ **ESSENTIAL FILES** (Must Upload)

### Core Application Files
- [x] `streamlit_institutional.py` - Main Streamlit dashboard
- [x] `institutional_scanner.py` - Core scanner engine
- [x] `market_tickers.py` - Ticker definitions (US & BR)
- [x] `stockmonitor_enhanced.py` - Enhanced scanner (if used)
- [x] `requirements.txt` - Python dependencies ⚠️ **MUST BE IN ROOT**

### Essential Documentation
- [x] `README.md` - Main project documentation
- [ ] `QUICK_START.md` - Quick start guide
- [ ] `STREAMLIT_DEPLOYMENT_CHECKLIST.md` - Deployment guide

### Configuration
- [x] `.gitignore` - Git ignore rules

---

## 📋 **RECOMMENDED FILES** (Should Upload)

### Documentation
- [ ] `INSTITUTIONAL_FEATURES.md` - Feature documentation
- [ ] `CLEAN_SCANNER_GUIDE.md` - Architecture guide
- [ ] `STREAMLIT_CLOUD_FIX.md` - Troubleshooting guide

### Optional Scripts
- [ ] `stockmonitor_scanner_only.py` - Simple scanner version
- [ ] `streamlit_scanner.py` - Basic dashboard (alternative)

---

## ❌ **OPTIONAL FILES** (Can Skip)

### Development/History Docs
- [ ] `COMPLETE_UPGRADE_SUMMARY.md` - Too detailed
- [ ] `IMPROVEMENTS_SUMMARY.md` - Dev notes
- [ ] `FIXES_APPLIED.md` - Dev tracking
- [ ] `GITHUB_SETUP.md` - One-time setup
- [ ] `CURSOR_GIT_INSTRUCTIONS.md` - Editor-specific
- [ ] `VISUAL_IMPROVEMENTS.md` - Historical notes
- [ ] `IBKR_REMOVAL_SUMMARY.md` - Can be in README

### Test/Dev Scripts
- [ ] `test_yfinance.py` - Test script
- [ ] `deploy_streamlit.sh` - Deployment script
- [ ] `push_to_github.sh` - Git helper
- [ ] `github_integration.py` - Helper module

### Other Files (Not Scanner Related)
- [ ] `stockmonitor.py` - Original with TWS (keep local)
- [ ] `app.py`, `app_enhanced.py` - Other projects
- [ ] All other `.py` files not related to scanner

---

## 🎯 **MINIMAL UPLOAD SET** (Recommended)

### Files to Upload:
```
✅ streamlit_institutional.py
✅ institutional_scanner.py
✅ market_tickers.py
✅ stockmonitor_enhanced.py
✅ requirements.txt
✅ README.md
✅ QUICK_START.md
✅ STREAMLIT_DEPLOYMENT_CHECKLIST.md
✅ .gitignore
```

### Optional but Helpful:
```
📝 INSTITUTIONAL_FEATURES.md
📝 CLEAN_SCANNER_GUIDE.md
📝 STREAMLIT_CLOUD_FIX.md
```

---

## 🚀 **Quick Upload Command**

```bash
# Essential files
git add streamlit_institutional.py \
        institutional_scanner.py \
        market_tickers.py \
        stockmonitor_enhanced.py \
        requirements.txt \
        README.md \
        QUICK_START.md \
        STREAMLIT_DEPLOYMENT_CHECKLIST.md \
        .gitignore

# Optional helpful docs
git add INSTITUTIONAL_FEATURES.md \
        CLEAN_SCANNER_GUIDE.md \
        STREAMLIT_CLOUD_FIX.md

# Commit and push
git commit -m "Add essential scanner files and documentation"
git push
```

---

## 📁 **Final Repository Structure**

```
stockmonitor/
├── README.md                          ⭐ Main doc
├── requirements.txt                   ⭐ Dependencies
├── QUICK_START.md                     ⭐ Quick start
├── STREAMLIT_DEPLOYMENT_CHECKLIST.md  ⭐ Deployment
├── INSTITUTIONAL_FEATURES.md          📝 Features
├── CLEAN_SCANNER_GUIDE.md             📝 Architecture
├── STREAMLIT_CLOUD_FIX.md             📝 Troubleshooting
│
├── streamlit_institutional.py         ⭐ Main app
├── institutional_scanner.py           ⭐ Scanner
├── market_tickers.py                  ⭐ Tickers
├── stockmonitor_enhanced.py           ⭐ Enhanced
│
└── .gitignore                          ⭐ Git config
```

---

**Total Essential Files**: 9 files  
**Total Recommended Files**: 12 files  
**Keep it simple**: Upload the 9 essential files + 3 recommended docs = **12 files total**
