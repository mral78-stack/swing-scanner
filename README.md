# 🏛️ Institutional-Grade Swing Trade Scanner

Professional swing trading opportunity scanner for **US and Brazilian markets** with comprehensive technical and fundamental analysis.

## ⭐ Features

- **20+ Technical Indicators**: RSI, MACD, Stochastic, ADX, Ichimoku Cloud, and more
- **Comprehensive Fundamental Analysis**: Valuation, profitability, growth metrics
- **AAA-D Opportunity Rating System**: Clear, institutional-grade ratings
- **Market Regime Detection**: Bull, Bear, or Sideways market identification
- **Brazil Market Support**: Full B3 coverage with currency conversion
- **Streamlit Dashboard**: Interactive web interface
- **Parallel Processing**: 10x faster scanning (1-3 min for 500+ stocks)
- **GitHub Integration**: Automatic result tracking

## 🚀 Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Run Scanner
```bash
# Basic scan
python institutional_scanner.py --scan

# High-quality opportunities only (AAA-AA)
python institutional_scanner.py --scan --min-rating AA

# Maximum performance
python institutional_scanner.py --scan --max-workers 20 --min-rating A
```

### Launch Dashboard
```bash
streamlit run streamlit_institutional.py
```

## 📊 Opportunity Rating System

| Grade | Score | Recommendation |
|-------|-------|----------------|
| **AAA** | 90-100 | EXCEPTIONAL BUY |
| **AA** | 85-89 | STRONG BUY |
| **A** | 80-84 | BUY |
| **BBB** | 75-79 | MODERATE BUY |
| **BB-B** | 65-74 | WATCH/CAUTIOUS |
| **CCC-D** | <65 | AVOID |

## 📁 Files

- `institutional_scanner.py` - Main institutional-grade scanner ⭐
- `streamlit_institutional.py` - Interactive dashboard ⭐
- `stockmonitor_enhanced.py` - Enhanced scanner with parallel processing
- `stockmonitor.py` - Original scanner (TWS integration)

## 📚 Documentation

- [SCANNER_README.md](SCANNER_README.md) - Complete usage guide
- [INSTITUTIONAL_FEATURES.md](INSTITUTIONAL_FEATURES.md) - Feature documentation
- [QUICK_START.md](QUICK_START.md) - Quick setup guide
- [GITHUB_SETUP.md](GITHUB_SETUP.md) - GitHub repository setup

## 🎯 Usage Example

```python
from institutional_scanner import run_institutional_scan

# Run scan
results, tradeable, non_tradeable = run_institutional_scan(
    max_workers=15,
    min_rating='AA'
)

# Display top opportunities
for r in results[:10]:
    print(f"{r['Ticker']}: {r['Rating_Grade']} ({r['Rating_Score']:.1f})")
    print(f"  {r['Recommendation']}")
```

## 🔧 Requirements

- Python 3.8+
- See `requirements.txt` for dependencies

## 📈 Performance

- **Scan Time**: 1-3 minutes for 500+ stocks (with 10 workers)
- **Coverage**: US + Brazil markets
- **Accuracy**: Multi-factor analysis reduces false positives

## 🚀 Deployment

### Streamlit Cloud
1. Push to GitHub
2. Deploy on https://share.streamlit.io/
3. Set main file: `streamlit_institutional.py`

See [GITHUB_SETUP.md](GITHUB_SETUP.md) for detailed setup.

## 📝 License

Educational purposes only. Use at your own risk.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional technical indicators
- Machine learning integration
- More market coverage
- Real-time alerts

---

**Version**: 7.0  
**Status**: Production Ready ✅
