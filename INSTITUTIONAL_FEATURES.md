# 🏛️ Institutional-Grade Scanner Features

## Overview

The institutional scanner (`institutional_scanner.py`) provides professional-grade analysis with a comprehensive rating system from **AAA (Highest Quality)** to **D (Lowest Quality)**.

## 🎯 Opportunity Rating System

### Rating Grades

| Grade | Score Range | Recommendation | Description |
|-------|------------|----------------|-------------|
| **AAA** | 90-100 | EXCEPTIONAL BUY | Highest Quality Opportunity |
| **AA** | 85-89 | STRONG BUY | High Quality Opportunity |
| **A** | 80-84 | BUY | Good Quality Opportunity |
| **BBB** | 75-79 | MODERATE BUY | Above Average Opportunity |
| **BB** | 70-74 | WATCH | Average Opportunity |
| **B** | 65-69 | CAUTIOUS | Below Average Opportunity |
| **CCC** | 60-64 | AVOID | Poor Quality |
| **CC** | 55-59 | AVOID | Very Poor Quality |
| **C** | 50-54 | AVOID | Extremely Poor Quality |
| **D** | 0-49 | AVOID | Default Quality |

### Scoring Components

**Total Score = 100 points (weighted)**

1. **Technical Analysis (50 points - 50% weight)**
   - Moving averages (SMA 20, 50, 200)
   - Golden Cross detection
   - RSI, MACD, Stochastic
   - ADX (trend strength)
   - Williams %R, CCI, MFI
   - Aroon Indicator
   - Ichimoku Cloud
   - Support/Resistance levels
   - Volume analysis (OBV, Volume Ratio)
   - Chart patterns

2. **Fundamental Analysis (30 points - 30% weight)**
   - Market capitalization
   - Valuation metrics (P/E, P/B)
   - Profitability (margins, ROE, ROA)
   - Growth metrics (revenue, earnings)
   - Debt analysis (Debt/Equity)
   - Liquidity (Current Ratio)
   - Institutional ownership
   - Analyst recommendations

3. **Momentum Analysis (20 points - 20% weight)**
   - Weekly/Monthly price changes
   - Rate of Change (ROC)
   - Relative strength vs market
   - Price momentum indicators

4. **Risk Assessment (20 points - lower is better)**
   - Volatility (ATR)
   - Maximum Drawdown
   - Sharpe Ratio
   - Sortino Ratio
   - Beta
   - Risk-adjusted returns

## 📊 Technical Indicators

### Momentum Indicators
- **RSI (Relative Strength Index)**: Overbought/oversold conditions
- **Stochastic Oscillator**: %K and %D lines
- **MACD**: Trend and momentum
- **Williams %R**: Momentum oscillator
- **CCI (Commodity Channel Index)**: Cyclical trends
- **MFI (Money Flow Index)**: Volume-weighted RSI

### Trend Indicators
- **Moving Averages**: SMA 20, 50, 200
- **ADX (Average Directional Index)**: Trend strength
- **Aroon Indicator**: Trend direction and strength
- **Ichimoku Cloud**: Comprehensive trend analysis

### Volume Indicators
- **Volume Ratio**: Current vs average volume
- **OBV (On-Balance Volume)**: Volume flow
- **Volume Profile**: POC (Point of Control)

### Support/Resistance
- **Automatic Detection**: Pivot point analysis
- **Fibonacci Levels**: Retracement levels
- **Distance Calculation**: Proximity to key levels

## 💼 Fundamental Analysis

### Valuation Metrics
- **P/E Ratio**: Price-to-Earnings
- **P/B Ratio**: Price-to-Book
- **Forward P/E**: Future earnings expectations

### Profitability
- **Profit Margins**: Net profit margin
- **ROE (Return on Equity)**: Shareholder returns
- **ROA (Return on Assets)**: Asset efficiency

### Growth Metrics
- **Revenue Growth**: Year-over-year growth
- **Earnings Growth**: Profit growth rate

### Financial Health
- **Debt/Equity Ratio**: Leverage analysis
- **Current Ratio**: Liquidity position
- **Market Cap**: Company size classification

### Market Sentiment
- **Institutional Ownership**: Smart money interest
- **Analyst Recommendations**: Professional opinions

## 📈 Market Regime Detection

### Regimes
- **BULL**: Uptrending market (price > SMAs, positive momentum)
- **BEAR**: Downtrending market (price < SMAs, negative momentum)
- **SIDEWAYS**: Range-bound market

### Confidence Level
- Based on price change magnitude
- SMA relationships
- Volume trends

## 🇧🇷 Brazil Market Enhancements

### Currency Conversion
- **USD/BRL Rate**: Real-time exchange rate
- **Price Conversion**: BRL to USD for comparison
- **Automatic Updates**: Daily rate fetching

### B3-Specific Data
- **Sector Mapping**: B3 sector classification
- **Exchange Information**: B3-specific metadata
- **Currency Tagging**: BRL currency identification

## 🎯 Risk Metrics

### Performance Ratios
- **Sharpe Ratio**: Risk-adjusted returns
- **Sortino Ratio**: Downside risk only
- **Calmar Ratio**: Return vs max drawdown

### Drawdown Analysis
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Drawdown Percentage**: Risk assessment

### Volatility
- **ATR (Average True Range)**: Volatility measure
- **Beta**: Market correlation

## 🚀 Usage Examples

### Command Line
```bash
# Basic scan
python institutional_scanner.py --scan

# High-quality opportunities only
python institutional_scanner.py --scan --min-rating AA

# Maximum performance
python institutional_scanner.py --scan --max-workers 20
```

### Python API
```python
from institutional_scanner import run_institutional_scan

results, tradeable, non_tradeable = run_institutional_scan(
    max_workers=15,
    min_rating='A'
)

# Filter AAA opportunities
aaa_opportunities = [r for r in results if r['Rating_Grade'] == 'AAA']
```

### Streamlit Dashboard
```bash
streamlit run streamlit_institutional.py
```

## 📊 Output Format

### JSON Structure
```json
{
  "Ticker": "AAPL",
  "Company": "Apple Inc.",
  "Market": "US",
  "Rating_Grade": "AA",
  "Rating_Score": 87.5,
  "Technical_Score": 42.3,
  "Fundamental_Score": 26.8,
  "Momentum_Score": 18.4,
  "Risk_Score": 3.2,
  "Recommendation": "STRONG BUY - High Quality Opportunity",
  "Key_Strengths": ["Above 200 SMA", "High ROE", "Strong Revenue Growth"],
  "Key_Risks": ["High P/E Ratio"],
  "Market_Regime": "BULL",
  "Regime_Confidence": 85.3
}
```

## 🔍 Filtering Options

### By Rating
- Minimum rating grade (AAA to D)
- Score thresholds
- Confidence levels

### By Market
- US stocks only
- Brazil stocks only
- Both markets

### By Tradeability
- IBKR tradeable stocks
- All stocks

### By Sector
- Filter by specific sectors
- Sector performance analysis

## 📈 Performance Metrics

### Scanner Performance
- **Scan Time**: 2-5 minutes for 500+ stocks (with 10 workers)
- **Accuracy**: Multi-factor analysis reduces false positives
- **Coverage**: US + Brazil markets

### Analysis Depth
- **20+ Technical Indicators**
- **15+ Fundamental Metrics**
- **5+ Risk Metrics**
- **Market Regime Detection**

## 🎓 Best Practices

1. **Rating Interpretation**
   - Focus on AAA-AA rated opportunities for highest quality
   - Use BBB-B for diversification
   - Avoid CCC-D rated stocks

2. **Risk Management**
   - Check Risk_Score (lower is better)
   - Review Max_Drawdown for volatility
   - Consider Market_Regime context

3. **Fundamental Validation**
   - Verify Fundamental_Score > 20 for quality
   - Check for negative growth or profitability
   - Review debt levels

4. **Technical Confirmation**
   - Look for Technical_Score > 35
   - Confirm trend alignment (above SMAs)
   - Check volume confirmation

## 🔄 Updates & Maintenance

- **Daily Scans**: Run daily for fresh opportunities
- **Weekly Reviews**: Analyze rating changes
- **Monthly Reports**: Track performance by rating

## 📚 Additional Resources

- See `SCANNER_README.md` for general usage
- See `IMPROVEMENTS_SUMMARY.md` for technical details
- See `QUICK_START.md` for setup instructions

---

**Version**: 7.0  
**Last Updated**: January 2025  
**Status**: Production Ready ✅
