# 📈 Enhanced Swing Trade Scanner v6.0

A high-performance swing trading opportunity scanner for US and Brazilian (BR) stocks with advanced technical analysis, parallel processing, and automated GitHub integration.

## 🚀 Features

### Core Capabilities
- **Parallel Processing**: Scan hundreds of stocks simultaneously with configurable worker threads
- **Dual Market Support**: Comprehensive coverage of US and Brazilian (B3) markets
- **Advanced Technical Analysis**: 
  - RSI, MACD, Stochastic Oscillator
  - ADX (Average Directional Index) for trend strength
  - Support/Resistance level detection
  - Volume Profile analysis (POC - Point of Control)
  - On-Balance Volume (OBV)
  - Bollinger Bands with squeeze detection
  - Chart pattern recognition (Double Bottom, Head & Shoulders, Ascending Triangle)

### Data Management
- **Data Persistence**: Automatic saving to JSON and CSV formats
- **Caching System**: Intelligent caching to reduce API calls and improve performance
- **GitHub Integration**: Automatic commit and push of scan results to GitHub repositories

### Visualization
- **Streamlit Dashboard**: Interactive web dashboard with:
  - Real-time scanning
  - Market-specific views (US vs BR)
  - Sector breakdowns
  - Score distributions
  - Interactive charts and filters

## 📦 Installation

### Prerequisites
- Python 3.8+
- Git (for GitHub integration)

### Setup

1. **Clone or download the repository**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Create necessary directories**:
```bash
mkdir -p scanner_cache scanner_results
```

## 🎯 Usage

### Command Line Scanner

#### Basic Scan
```bash
python stockmonitor_enhanced.py --scan
```

#### Advanced Options
```bash
# Scan with custom settings
python stockmonitor_enhanced.py --scan \
    --max-workers 15 \
    --min-score 50 \
    --save-json \
    --save-csv

# Setup GitHub integration
python stockmonitor_enhanced.py --setup-git \
    --github-url https://github.com/yourusername/your-repo.git

# Scan and push to GitHub
python stockmonitor_enhanced.py --scan \
    --save-json \
    --save-csv \
    --github-push \
    --github-url https://github.com/yourusername/your-repo.git
```

### Streamlit Dashboard

Launch the interactive dashboard:
```bash
streamlit run streamlit_scanner.py
```

The dashboard will open in your browser at `http://localhost:8501`

#### Dashboard Features:
- **Run Scanner**: Execute scans with configurable settings
- **View Results**: Browse opportunities by market (US/BR)
- **Filter & Sort**: Filter by sector, score, tradeability
- **Visualizations**: Charts and graphs for analysis
- **Export**: Save results to JSON/CSV
- **GitHub Push**: Push results directly to your repository

## 📊 Scanner Scoring System

The scanner uses a comprehensive scoring algorithm that evaluates:

### Technical Indicators (Weighted)
- **Trend Analysis**: SMA crossovers, Golden Cross detection (+20 points)
- **Momentum**: RSI, Stochastic, MACD crossovers (+5 to +15 points)
- **Volume**: Volume surges, OBV trends (+5 to +12 points)
- **Volatility**: ATR analysis, Bollinger Squeeze (+5 to +8 points)
- **Support/Resistance**: Proximity to key levels (+5 to +8 points)
- **Chart Patterns**: Pattern recognition (+5 points per pattern)

### Fundamental Factors
- **Analyst Ratings**: Strong buy/buy recommendations (+10 points)
- **Institutional Ownership**: High institutional holding (+8 points)

### Score Thresholds
- **🟢 STRONG BUY**: Score ≥ 80
- **🟡 BUY**: Score ≥ 60
- **👀 WATCH**: Score ≥ 40
- **⚪ NEUTRAL**: Score < 40

## 🔧 Configuration

### Scanner Settings

Edit `stockmonitor_enhanced.py` to customize:

```python
# Parallel processing
max_workers = 10  # Number of concurrent workers

# Minimum score threshold
min_score = 30  # Minimum score to include in results

# Cache settings
CACHE_DIR = "scanner_cache"  # Cache directory
RESULTS_DIR = "scanner_results"  # Results directory
```

### Market Coverage

The scanner includes comprehensive ticker lists for:

**US Markets:**
- AI/Semiconductors
- Software/Cloud
- Consumer Tech
- Energy/Nuclear
- Renewable Energy
- Space/Defense
- Fintech
- Banks/Financial
- Biotech
- Healthcare
- Mining/Metals
- Industrial
- Retail/Consumer
- Real Estate

**Brazilian Markets (B3):**
- Bancos BR
- Financeiras BR
- Petróleo BR
- Mineração BR
- Papel/Celulose BR
- Varejo BR
- Alimentos BR
- Energia BR
- Saneamento BR
- Transporte BR
- Construção BR
- Tech/Telecom BR
- Saúde BR
- Industrial BR

## 📁 File Structure

```
.
├── stockmonitor.py              # Original scanner (TWS integration)
├── stockmonitor_enhanced.py     # Enhanced scanner with parallel processing
├── streamlit_scanner.py         # Streamlit dashboard
├── requirements.txt             # Python dependencies
├── SCANNER_README.md            # This file
├── scanner_cache/               # Cached stock data
└── scanner_results/             # Scan results (JSON/CSV)
```

## 🔄 GitHub Integration

### Setup

1. **Create a GitHub repository** (or use existing)

2. **Initialize git in your project**:
```bash
git init
git remote add origin https://github.com/yourusername/your-repo.git
```

3. **Configure scanner**:
```bash
python stockmonitor_enhanced.py --setup-git \
    --github-url https://github.com/yourusername/your-repo.git
```

### Automatic Updates

The scanner can automatically commit and push results:

```bash
python stockmonitor_enhanced.py --scan \
    --save-json \
    --github-push
```

Results will be committed with timestamp and pushed to the `main` or `master` branch.

### Manual Push

```python
from stockmonitor_enhanced import commit_and_push_results

commit_and_push_results(
    commit_message="Update scan results - 2025-01-25"
)
```

## 📈 Performance

### Benchmarks
- **Sequential Scan**: ~15-20 minutes for 500+ stocks
- **Parallel Scan (10 workers)**: ~2-3 minutes for 500+ stocks
- **Parallel Scan (20 workers)**: ~1-2 minutes for 500+ stocks

### Optimization Tips
1. Use appropriate `max_workers` based on your system (CPU cores)
2. Enable caching to reduce API calls
3. Run scans during off-peak hours for better API response times
4. Filter by minimum score to reduce result set size

## 🛠️ Advanced Usage

### Custom Analysis

Extend the scanner with custom indicators:

```python
from stockmonitor_enhanced import analyze_single_stock_enhanced

result = analyze_single_stock_enhanced(
    ticker="AAPL",
    sector="Technology",
    market="US"
)

print(f"Score: {result['Score']}")
print(f"Signals: {result['Signals']}")
```

### Batch Processing

```python
from stockmonitor_enhanced import run_scanner_analysis_parallel

all_results, tradeable, non_tradeable = run_scanner_analysis_parallel(
    max_workers=15
)

# Filter and process
high_score = [r for r in all_results if r['Score'] >= 80]
```

## ⚠️ Important Notes

1. **Rate Limiting**: Be mindful of API rate limits when scanning large numbers of stocks
2. **Data Accuracy**: Results are based on available market data - always verify before trading
3. **Paper Trading**: Test thoroughly before using with real money
4. **GitHub Credentials**: Ensure git is configured with proper credentials for automatic pushes

## 🔐 Security

- Never commit sensitive API keys or credentials
- Use environment variables for sensitive data
- Review `.gitignore` to exclude cache and sensitive files

## 📝 License

This project is for educational purposes. Use at your own risk.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional technical indicators
- Machine learning integration
- Real-time alerts
- Backtesting capabilities
- More market coverage

## 📧 Support

For issues or questions, please open an issue on GitHub.

---

**Version**: 6.0  
**Last Updated**: January 2025  
**Author**: Enhanced Scanner Team
