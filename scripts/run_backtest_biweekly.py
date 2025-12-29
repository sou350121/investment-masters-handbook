import os
import sys
import argparse
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from tools.backtest_engine import BacktestEngine
from tools.llm_bridge import LLMConfig
from tools.rag_core import load_vectorstore

def main():
    parser = argparse.ArgumentParser(description="Biweekly Allocation Backtest (LLM-in-loop)")
    parser.add_argument("--mode", choices=["A", "B", "AB"], default="A", help="Backtest mode: A (Committee), B (Signals), AB (Comparison)")
    parser.add_argument("--news_csv", type=str, help="Path to historical news briefs CSV")
    parser.add_argument("--signals_csv", type=str, help="Path to strategy signals CSV (for mode B/AB)")
    parser.add_argument("--start", type=str, default="2024-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, default="2024-12-31", help="End date (YYYY-MM-DD)")
    parser.add_argument("--tickers", type=str, default="SPY,SHY,GLD,BIL", help="Comma-separated tickers for Stocks,Bonds,Gold,Cash")
    parser.add_argument("--step_days", type=int, default=10, help="Rebalance every N trading days")
    
    # LLM Config
    parser.add_argument("--provider", type=str, default="openai", help="LLM provider")
    parser.add_argument("--model", type=str, default="gpt-4o", help="LLM model")
    parser.add_argument("--api_key_env", type=str, default="LLM_API_KEY", help="Env var for API key")
    
    parser.add_argument("--run_id", type=str, default=None, help="Unique ID for this run (defaults to timestamp)")
    parser.add_argument("--results_dir", type=str, default="results", help="Directory to save results")
    
    args = parser.parse_args()
    
    if not args.run_id:
        args.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    run_dir = os.path.join(args.results_dir, args.run_id)
    if not os.path.exists(run_dir):
        os.makedirs(run_dir)
        
    # 1. Initialize Engine & Config
    llm_cfg = LLMConfig(
        provider=args.provider,
        model=args.model,
        api_key=os.getenv(args.api_key_env)
    )
    engine = BacktestEngine(results_dir=args.results_dir, llm_config=llm_cfg)
    
    # 2. Load Prices
    tickers = [t.strip() for t in args.tickers.split(",") if t.strip()]
    if len(tickers) != 4:
        print("Error: --tickers must provide exactly 4 tickers in order: Stocks,Bonds,Gold,Cash")
        sys.exit(2)
    ticker_map = {"stocks": tickers[0], "bonds": tickers[1], "gold": tickers[2], "cash": tickers[3]}
    prices = engine.load_prices(tickers, args.start, args.end)
    
    # 3. Load Inputs
    news_data = pd.DataFrame()
    if args.mode in ["A", "AB"]:
        if not args.news_csv:
            print("Error: --news_csv is required for Mode A/AB")
            sys.exit(1)
        news_data = pd.read_csv(args.news_csv)
        
    signals_data = pd.DataFrame()
    if args.mode in ["B", "AB"]:
        if not args.signals_csv:
            print("Error: --signals_csv is required for Mode B/AB")
            sys.exit(1)
        signals_data = pd.read_csv(args.signals_csv)
        
    # Load Vectorstore for Committee
    vs = None
    if args.mode in ["A", "AB"]:
        persist_dir = str(PROJECT_ROOT / "vectorstore")
        if os.path.exists(persist_dir):
            vs = load_vectorstore(persist_dir)
        else:
            print(f"Warning: Vectorstore not found at {persist_dir}. Committee calls may fail or use default expert logic.")

    # 4. Run Backtests
    results = {}
    
    if args.mode in ["A", "AB"]:
        print("\n>>> Running Backtest A (Committee)...")
        curve_a, hist_a = engine.run_backtest_A(args.run_id, prices, news_data, vs, step_days=args.step_days, ticker_map=ticker_map)
        metrics_a = engine.compute_metrics(curve_a)
        
        curve_a.to_csv(os.path.join(run_dir, "equity_curve_A.csv"))
        hist_a.to_csv(os.path.join(run_dir, "history_A.csv"), index=False)
        with open(os.path.join(run_dir, "metrics_A.json"), "w") as f:
            json.dump(metrics_a, f, indent=2)
        results["A"] = metrics_a
        print(f"Mode A Sharpe: {metrics_a.get('sharpe_ratio', 0):.2f}")

    if args.mode in ["B", "AB"]:
        print("\n>>> Running Backtest B (Strategy Signals)...")
        curve_b, hist_b = engine.run_backtest_B(args.run_id, prices, signals_data, step_days=args.step_days, ticker_map=ticker_map)
        metrics_b = engine.compute_metrics(curve_b)
        
        curve_b.to_csv(os.path.join(run_dir, "equity_curve_B.csv"))
        hist_b.to_csv(os.path.join(run_dir, "history_B.csv"), index=False)
        with open(os.path.join(run_dir, "metrics_B.json"), "w") as f:
            json.dump(metrics_b, f, indent=2)
        results["B"] = metrics_b
        print(f"Mode B Sharpe: {metrics_b.get('sharpe_ratio', 0):.2f}")

    # 5. Generate Comparison
    if args.mode == "AB":
        comp_path = os.path.join(run_dir, "comparison.md")
        with open(comp_path, "w", encoding="utf-8") as f:
            f.write(f"# Backtest Comparison: {args.run_id}\n\n")
            f.write(f"- Range: {args.start} to {args.end}\n")
            f.write(f"- Frequency: every {args.step_days} trading days\n\n")
            
            f.write("## Performance Metrics\n\n")
            f.write("| Metric | Mode A (Committee) | Mode B (Signals) |\n")
            f.write("| :--- | :---: | :---: |\n")
            for m in ["total_return", "cagr", "volatility", "downside_volatility", "sharpe_ratio", "sortino_ratio", "max_drawdown"]:
                val_a = results["A"].get(m, 0)
                val_b = results["B"].get(m, 0)
                f.write(f"| {m} | {val_a:.4f} | {val_b:.4f} |\n")
                
        print(f"\nComparison report saved to {comp_path}")

if __name__ == "__main__":
    main()

