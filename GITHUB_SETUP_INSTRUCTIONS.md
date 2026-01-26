# 🔗 GitHub Repository Connection Guide

## Current Status

Your repository is located at: `https://github.com/mral78-stack/stockmonitor`

The Git repository is in the **parent directory** (`/Users/angelolauri/Documents`), and your swing scanner files are in the `swing scanner/` subfolder.

---

## ✅ Recommended: Use Cursor's Source Control Panel

Since your GitHub profile is already linked to Cursor, the easiest way is:

1. **Open Cursor's Source Control Panel** (Ctrl/Cmd + Shift + G)
2. **Stage Files**: 
   - Add all files from `swing scanner/` folder
   - Or use the "+" button next to files
3. **Commit**: 
   - Write commit message: "Add swing scanner project with enhancements"
   - Click "Commit"
4. **Push**: 
   - Click "Push" or "Sync Changes"
   - Cursor will handle authentication automatically

---

## 🔧 Alternative: Command Line Setup

If you prefer command line, here are the steps:

### Step 1: Navigate to Parent Directory
```bash
cd /Users/angelolauri/Documents
```

### Step 2: Add Remote (if not already added)
```bash
git remote add origin https://github.com/mral78-stack/stockmonitor.git
# Or update existing:
git remote set-url origin https://github.com/mral78-stack/stockmonitor.git
```

### Step 3: Add Swing Scanner Files
```bash
git add "swing scanner/"
```

### Step 4: Commit
```bash
git commit -m "Add swing scanner project with all enhancements"
```

### Step 5: Push to GitHub
```bash
git push -u origin main
```

**Note**: If the repository already has content, you may need to:
```bash
git pull origin main --allow-unrelated-histories
# Then push:
git push -u origin main
```

---

## 📦 Files to Push

All files in `swing scanner/` folder:
- ✅ Core application files (7 Python files)
- ✅ Configuration (requirements.txt, .gitignore)
- ✅ Documentation (18+ markdown files)
- ✅ Test scripts

---

## 🔐 Authentication

If you get authentication errors:

### Option 1: GitHub CLI
```bash
gh auth login
```

### Option 2: Personal Access Token
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate token with `repo` scope
3. Use token as password when pushing

### Option 3: SSH (if configured)
```bash
git remote set-url origin git@github.com:mral78-stack/stockmonitor.git
```

---

## 🎯 Quick Start

**Easiest Method**: Use Cursor's Source Control Panel (recommended)

1. Open Source Control (Ctrl/Cmd + Shift + G)
2. Stage `swing scanner/` files
3. Commit with message
4. Push to GitHub

---

**Status**: Ready to connect! Use Cursor's Source Control panel for easiest setup.
