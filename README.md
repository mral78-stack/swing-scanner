# swing-scanner

[![CI](https://github.com/mral78-stack/swing-scanner/actions/workflows/ci.yml/badge.svg)](https://github.com/mral78-stack/swing-scanner/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

A swing-trading opportunity scanner for **US and Brazilian (B3)** equities, combining technical, fundamental, momentum, and risk metrics into a single AAA→D rating per ticker.

The project is built on free data sources (`yfinance` by default, with optional fallback to Alpha Vantage, Polygon.io and IEX Cloud) and ships a [Streamlit](https://streamlit.io) dashboard for interactive exploration.

> **Status:** personal / educational project, single maintainer. Not financial advice. Use at your own risk.

---

## Install

Requires Python 3.10+.

```bash
git clone https://github.com/mral78-stack/swing-scanner.git
cd swing-scanner
pip install -r requirements.txt
```

## Run

```bash
# CLI scan (all tickers, default rating threshold)
python institutional_scanner.py --scan

# Filter to AA+ opportunities, 20 parallel workers
python institutional_scanner.py --scan --min-rating AA --max-workers 20

# Interactive dashboard
streamlit run streamlit_institutional.py
```

The scanner caches results under `scanner_cache/` and writes structured output to `scanner_results/` (both git-ignored).

## What it does

For each ticker it computes:

| Component       | Weight | Examples |
|-----------------|--------|----------|
| Technical       | 50%    | SMA 20/50/200, RSI, MACD, Stochastic, ADX, Ichimoku, Aroon, OBV, MFI, support/resistance |
| Fundamental     | 30%    | P/E, P/B, ROE, ROA, debt/equity, current ratio, revenue/earnings growth, institutional ownership |
| Momentum        | 20%    | Weekly/monthly returns, ROC, relative strength vs. benchmark |
| Risk (penalty)  | —      | ATR, max drawdown, Sharpe, Sortino, Calmar, beta |

Components are blended into a **0–100 score** mapped to a rating (`AAA`/`AA`/`A`/`BBB`/`BB`/`B`/`CCC`/`CC`/`C`/`D`). A market-regime classifier (BULL / BEAR / SIDEWAYS) is reported alongside the rating to contextualize the signal.

See [FEATURES.md](FEATURES.md) for the full indicator list and scoring breakdown.

## Data sources

`yfinance` is the default source and works out of the box for both US and B3 tickers. Optional fallback sources are wired in for resilience — see [DATA_SOURCES.md](DATA_SOURCES.md) for setup.

| Source | Required key | Markets | Free tier |
|--------|--------------|---------|-----------|
| yfinance | — | US, B3 | unlimited (best-effort) |
| Alpha Vantage | `ALPHA_VANTAGE_API_KEY` | US | 500/day |
| Polygon.io | `POLYGON_API_KEY` | US | 5/min |
| IEX Cloud | `IEX_CLOUD_API_KEY` | US | 50k msg/month |

## Project layout

```
.
├── institutional_scanner.py      # CLI entrypoint, scoring engine
├── stockmonitor_enhanced.py      # Older scanner kept for reference
├── stockmonitor_scanner_only.py  # Scanner-only build (no GitHub auto-push)
├── data_sources.py               # Multi-source data adapter with fallback chain
├── market_tickers.py             # US + B3 ticker universes
├── streamlit_institutional.py    # Dashboard (institutional scanner)
├── streamlit_scanner.py          # Dashboard (legacy)
├── test_yfinance.py              # Smoke test for the yfinance dependency
├── FEATURES.md
├── DATA_SOURCES.md
└── requirements.txt
```

## Contributing

PRs and issues welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE).
