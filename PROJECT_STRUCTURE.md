# 📁 Swing Scanner Project Structure

## Folder Organization

All swing scanner project files have been moved to the **`swing scanner/`** folder.

---

## 📦 Files in This Folder

### Core Application Files (7 files)
```
✅ streamlit_institutional.py          # Main Streamlit dashboard
✅ institutional_scanner.py            # Core institutional-grade scanner
✅ data_sources.py                     # Multi-source data fetcher
✅ market_tickers.py                   # Ticker definitions (633 tickers)
✅ stockmonitor_enhanced.py            # Enhanced scanner
✅ stockmonitor_scanner_only.py        # Simple scanner version
✅ streamlit_scanner.py                # Basic dashboard
```

### Configuration Files (2 files)
```
✅ requirements.txt                    # Python dependencies
✅ .gitignore                          # Git ignore rules
```

### Documentation Files (18 files)
```
✅ README.md                           # Main project documentation
✅ QUICK_START.md                      # Quick start guide
✅ STREAMLIT_DEPLOYMENT_CHECKLIST.md  # Deployment guide
✅ INSTITUTIONAL_FEATURES.md          # Feature documentation
✅ CLEAN_SCANNER_GUIDE.md             # Architecture guide
✅ STREAMLIT_CLOUD_FIX.md             # Troubleshooting guide
✅ MULTI_SOURCE_DATA_SETUP.md         # Multi-source API setup
✅ MULTI_SOURCE_SUMMARY.md            # Multi-source quick reference
✅ STREAMLIT_DEBUG_FIXES.md           # Debug fixes documentation
✅ IBKR_REMOVAL_SUMMARY.md            # IBKR removal documentation
✅ TICKER_COVERAGE_ANALYSIS.md        # Ticker coverage analysis
✅ TICKER_EXPANSION_SUMMARY.md        # Ticker expansion summary
✅ ESSENTIAL_DOCS_FOR_REPO.md         # Essential docs guide
✅ ESSENTIAL_FILES_FOR_REPO.md        # Essential files guide
✅ GITHUB_REPO_FILE_LIST.md           # GitHub file list
✅ REPO_UPLOAD_CHECKLIST.md           # Upload checklist
✅ JSON_SERIALIZATION_FIX.md          # JSON fix documentation
✅ SCANNER_README.md                  # Scanner readme
```

### Test Files (1 file)
```
✅ test_yfinance.py                    # yfinance test script
```

---

## 📊 Summary

**Total Files**: 28 files
- **Python Files**: 7
- **Documentation**: 18
- **Configuration**: 2
- **Test Scripts**: 1

---

## 🚀 Quick Start

### Run Scanner
```bash
cd "swing scanner"
python institutional_scanner.py --scan --min-rating B
```

### Run Streamlit Dashboard
```bash
cd "swing scanner"
streamlit run streamlit_institutional.py
```

---

## 📝 Notes

- All project files are now organized in one folder
- Original `stockmonitor.py` (with TWS) remains in parent directory
- Other unrelated projects remain in parent directory
- This folder is ready for Git repository initialization

---

**Status**: ✅ All swing scanner files organized in `swing scanner/` folder
