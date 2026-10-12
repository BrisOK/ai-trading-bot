# AI Trading Bot (Starter)

This is a minimal trading bot framework using:

- Python
- `ccxt` for exchange connectivity
- A simple SMA crossover strategy
- Configurable risk and runtime parameters via `config.yaml`

## Setup

bashCopy Codegit clone  <your-repo-url>
cd ai-trading-bot
python -m venv .venv
source .venv/bin/activate    # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp config.example.yaml config.yaml
# Edit config.yaml and add your API keys (testnet where possible)
python main.py
Use at your own risk. Always start with testnet / paper trading.Copy Code
---

## 13. Commit and (optionally) push to GitHub

bashCopy Codegit add .
git commit -m "Initial trading bot framework"

# If you already created a GitHub repo:
git remote add origin https://github.com/<your-username>/ai-trading-bot.git
git branch -M main
git push -u origin main

