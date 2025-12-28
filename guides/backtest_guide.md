# Backtest Guide (Biweekly LLM-in-loop)

This guide explains how to run biweekly backtests using the Investment Masters Handbook committee and strategy signals.

## 1. Overview

The backtest engine simulates a portfolio rebalanced every **10 trading days** (approx. biweekly). It supports two primary modes:
- **Mode A (Committee)**: Uses the LLM committee to decide allocations based on historical news briefs.
- **Mode B (Signals)**: Uses quantitative strategy signals (risk_bias) to decide allocations.
- **Mode AB**: Runs both modes and generates a comparison report.

## 2. Requirements

- Python 3.10+
- `pandas`, `numpy`, `yfinance`
- LLM API Key (OpenAI, OpenRouter, etc.)
- A populated vectorstore (run `python scripts/generate_artifacts.py` first)

## 3. Preparing Inputs

### News Briefs (`news.csv`)
Create a CSV with the following columns:
- `as_of_date`: YYYY-MM-DD
- `brief_text`: The market context for that period.

Example:
```csv
as_of_date,brief_text
2024-01-02,"Strong tech momentum, but inflation remains a concern."
2024-01-16,"VIX at 12, market breadth improving, Fed remains hawkish."
```

### Strategy Signals (`signals.csv`)
- `as_of_date`: YYYY-MM-DD
- `risk_bias`: -1.0 to 1.0

## 4. Running the Backtest

```bash
# Set your API key
export LLM_API_KEY=sk-...

# Run A/B comparison
python scripts/run_backtest_biweekly.py \
  --mode AB \
  --news_csv data/historical_news.csv \
  --signals_csv data/strategy_signals.csv \
  --start 2024-01-01 \
  --end 2024-06-30
```

### Arguments
- `--tickers`: Comma-separated list (default: `SPY,IEF,GLD,BIL`).
- `--step_days`: Rebalancing interval in trading days (default: `10`).
- `--model`: LLM model to use (default: `gpt-4o`).
- `--results_dir`: Where to save outputs (default: `results`).

## 5. Caching and Cost Control

Committee calls are automatically cached in `results/<run_id>/llm_cache/`. 
If you restart a backtest with the same `run_id`, it will skip existing cached results to save costs.

## 6. Analyzing Results

Results are saved in `results/<run_id>/`:
- `equity_curve_A.csv`: Daily portfolio value for Mode A.
- `metrics_A.json`: Performance summary (Sharpe, CAGR, etc.).
- `comparison.md`: A markdown report comparing Mode A and B.

