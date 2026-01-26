# 🚀 Quick Start Guide - Enhanced Swing Trade Scanner

## Installation (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Create Directories
```bash
mkdir -p scanner_cache scanner_results
```

### Step 3: Test Scanner
```bash
python stockmonitor_enhanced.py --scan --min-score 50
```

## Basic Usage

### Run a Scan
```bash
# Basic scan
python stockmonitor_enhanced.py --scan

# With options
python stockmonitor_enhanced.py --scan \
    --max-workers 15 \
    --min-score 60 \
    --save-json \
    --save-csv
```

### Launch Dashboard
```bash
streamlit run streamlit_scanner.py
```
Then open `http://localhost:8501` in your browser.

## GitHub Setup (Optional)

### Step 1: Create GitHub Repository
1. Go to GitHub and create a new repository
2. Copy the repository URL (e.g., `https://github.com/username/repo.git`)

### Step 2: Setup Git
```bash
python stockmonitor_enhanced.py --setup-git \
    --github-url https://github.com/username/repo.git
```

### Step 3: Initial Commit
```bash
git add .
git commit -m "Initial commit"
git push -u origin main
```

### Step 4: Auto-push Scans
```bash
python stockmonitor_enhanced.py --scan \
    --save-json \
    --github-push
```

## Streamlit Cloud Deployment

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add Streamlit dashboard"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to https://streamlit.io/cloud
2. Connect your GitHub account
3. Select your repository
4. Deploy!

### Step 3: Configure
- **Main file**: `streamlit_scanner.py`
- **Python version**: 3.8+
- **Requirements**: Auto-detected from `requirements.txt`

## Common Commands

```bash
# Quick scan (no save)
python stockmonitor_enhanced.py --scan

# Full scan with export
python stockmonitor_enhanced.py --scan --save-json --save-csv

# Scan and push to GitHub
python stockmonitor_enhanced.py --scan --save-json --github-push

# High-performance scan (20 workers)
python stockmonitor_enhanced.py --scan --max-workers 20

# Dashboard
streamlit run streamlit_scanner.py
```

## Troubleshooting

### Import Errors
```bash
# Make sure all dependencies are installed
pip install --upgrade -r requirements.txt
```

### Git Push Fails
```bash
# Check git configuration
git config user.name
git config user.email

# Setup if needed
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Cache Issues
```bash
# Clear cache
rm -rf scanner_cache/*
```

### Performance Issues
- Reduce `--max-workers` if system is slow
- Increase cache TTL for less frequent updates
- Run scans during off-peak hours

## Next Steps

1. **Read Full Documentation**: See `SCANNER_README.md`
2. **Review Improvements**: See `IMPROVEMENTS_SUMMARY.md`
3. **Customize Settings**: Edit `stockmonitor_enhanced.py`
4. **Explore Dashboard**: Launch Streamlit and explore features

## Support

- Check `SCANNER_README.md` for detailed documentation
- Review `IMPROVEMENTS_SUMMARY.md` for technical details
- Check code comments for implementation details

---

**Happy Scanning! 📈**
