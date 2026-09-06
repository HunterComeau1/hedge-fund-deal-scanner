# Hedge Fund Deal Scanner

A standalone Streamlit research app that ranks stocks by a hedge-fund-style **Deal Score** designed to separate genuinely attractive businesses from simple "cheap" stocks and value traps.

## v0.1 scoring model

The composite score is 0–100:

- Valuation — 25%
- Business Quality — 20%
- Growth — 15%
- Financial Health — 15%
- Cash Flow — 10%
- Estimate Revisions — 5%
- Ownership — 5%
- Market / Catalyst — 5%

A separate **Value Trap Risk** score (0–100, lower is better) penalizes deteriorating fundamentals.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Current data source

v0.1 uses `yfinance` so the project can run without paid API keys. The data layer is isolated so we can later swap in a stronger fundamentals provider.

## Roadmap

1. Sector/industry-relative valuation normalization
2. Historical valuation percentiles
3. Analyst estimate revision engine
4. Insider and institutional ownership scoring
5. DCF / reverse-DCF fair value
6. Bear / base / bull scenario valuation
7. AI investment thesis generation
8. Larger stock universes and scheduled scans
9. Historical backtest of Deal Score buckets
10. Portfolio/watchlist tools

> Research tool only. Scores are not investment advice.
