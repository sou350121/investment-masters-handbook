import os
import json
import hashlib
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from tools.llm_bridge import LLMConfig, LLMBridge
from tools.rag_core import ensemble_reasoning, TieredEnsembleResponse

class BacktestEngine:
    def __init__(self, results_dir: str = "results", llm_config: Optional[LLMConfig] = None):
        self.results_dir = results_dir
        self.llm_config = llm_config
        self.bridge = LLMBridge(llm_config) if llm_config else None
        
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
            
    def load_prices(self, tickers: List[str], start: str, end: str) -> pd.DataFrame:
        """Fetch historical prices for tickers."""
        print(f"Fetching prices for {tickers} from {start} to {end}...")
        data = yf.download(tickers, start=start, end=end, progress=False)
        if 'Close' in data:
            return data['Close']
        return data

    def build_rebalance_calendar(self, prices_index: pd.DatetimeIndex, step_trading_days: int = 10) -> List[datetime]:
        """Generate a list of rebalance dates every N trading days."""
        return [prices_index[i] for i in range(0, len(prices_index), step_trading_days)]

    @staticmethod
    def default_ticker_map() -> Dict[str, str]:
        """
        Default bucket -> ticker mapping.

        We default bonds to short-duration treasuries (SHY) for better stability
        under tightening regimes; cash uses BIL as a practical proxy.
        """
        return {"stocks": "SPY", "bonds": "SHY", "gold": "GLD", "cash": "BIL"}

    def _get_cache_path(self, run_id: str, date_str: str, prompt_hash: str) -> str:
        cache_dir = os.path.join(self.results_dir, run_id, "llm_cache")
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        return os.path.join(cache_dir, f"{date_str}_{prompt_hash}.json")

    def committee_decide_allocation(
        self, 
        run_id: str,
        as_of_date: datetime, 
        brief_text: str, 
        current_allocation: Dict[str, float],
        vectorstore: Any,
        experts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Call committee logic with caching."""
        date_str = as_of_date.strftime("%Y-%m-%d")
        # Simplified hash of brief + date + current_alloc for cache key
        cache_key = f"{brief_text}_{date_str}_{json.dumps(current_allocation, sort_keys=True)}"
        prompt_hash = hashlib.md5(cache_key.encode()).hexdigest()
        
        cache_path = self._get_cache_path(run_id, date_str, prompt_hash)
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Format the brief as a query for the committee
        query = f"Market situation as of {date_str}: {brief_text}. Current allocation: {current_allocation}. Please provide a biweekly allocation recommendation."
        
        # Call the refactored run_ensemble_committee
        from tools.rag_core import run_ensemble_committee
        result = run_ensemble_committee(
            vectorstore=vectorstore,
            query=query,
            bridge=self.bridge,
            top_k_experts=3
        )
        
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        return result

    def simulate_execution(
        self, 
        current_alloc: Dict[str, float], 
        target_alloc: Dict[str, float], 
        exec_mode: str = "two_stage"
    ) -> List[Dict[str, float]]:
        """
        Simulate execution over one or more days.
        Returns a list of daily allocations during the transition.
        """
        if exec_mode == "instant":
            return [target_alloc]
        
        # two_stage: T0 60%, T1 40%
        t0_alloc = {}
        for k in current_alloc:
            diff = target_alloc.get(k, 0) - current_alloc[k]
            t0_alloc[k] = current_alloc[k] + diff * 0.6
            
        # Ensure sum is 100 or 1.0 depending on format
        s = sum(t0_alloc.values())
        if s != 0:
            t0_alloc = {k: v / s * 100 for k, v in t0_alloc.items()}
            
        return [t0_alloc, target_alloc]

    def compute_metrics(self, equity_curve: pd.Series) -> Dict[str, float]:
        """Compute standard performance metrics."""
        # Avoid future pandas default fill behavior changes.
        returns = equity_curve.pct_change(fill_method=None).dropna()
        if len(returns) == 0:
            return {}
            
        total_return = equity_curve.iloc[-1] / equity_curve.iloc[0] - 1
        days = (equity_curve.index[-1] - equity_curve.index[0]).days
        cagr = (1 + total_return) ** (365.25 / days) - 1 if days > 0 else 0
        
        vol = returns.std() * np.sqrt(252)
        sharpe = (cagr - 0.03) / vol if vol > 0 else 0 # Assume 3% risk-free

        # Sortino ratio (downside deviation, MAR=0, risk-free=3% annual)
        # Downside deviation: sqrt(mean(min(0, r - MAR)^2)) * sqrt(252)
        mar_daily = 0.0
        downside = np.minimum(0.0, returns.values - mar_daily)
        downside_dev = float(np.sqrt(np.mean(np.square(downside))) * np.sqrt(252)) if len(downside) > 0 else 0.0
        sortino = (cagr - 0.03) / downside_dev if downside_dev > 0 else 0.0
        
        drawdown = 1 - equity_curve / equity_curve.cummax()
        max_dd = drawdown.max()
        
        return {
            "total_return": float(total_return),
            "cagr": float(cagr),
            "volatility": float(vol),
            "sharpe_ratio": float(sharpe),
            "downside_volatility": float(downside_dev),
            "sortino_ratio": float(sortino),
            "max_drawdown": float(max_dd)
        }

    def run_backtest_A(
        self,
        run_id: str,
        prices: pd.DataFrame,
        news_data: pd.DataFrame,
        vectorstore: Any,
        step_days: int = 10,
        initial_alloc: Dict[str, float] = None,
        ticker_map: Optional[Dict[str, str]] = None,
    ) -> Tuple[pd.Series, pd.DataFrame]:
        """Run Backtest Mode A: Committee driven."""
        if initial_alloc is None:
            initial_alloc = {"stocks": 60, "bonds": 20, "gold": 10, "cash": 10}
            
        calendar = self.build_rebalance_calendar(prices.index, step_days)
        current_alloc = initial_alloc
        
        equity = 1.0
        equity_curve = pd.Series(index=prices.index, dtype=float)
        history = []
        
        ticker_map = ticker_map or self.default_ticker_map()
        
        # Fill missing values if any
        prices = prices.ffill()
        
        for i, date in enumerate(prices.index):
            if i > 0:
                # Update equity based on daily returns
                day_return = 0
                for bucket, ticker in ticker_map.items():
                    if ticker in prices.columns:
                        ret = prices[ticker].iloc[i] / prices[ticker].iloc[i-1] - 1
                        day_return += (current_alloc.get(bucket, 0) / 100.0) * ret
                equity *= (1 + day_return)
            
            equity_curve.iloc[i] = equity
            
            if date in calendar:
                # Rebalance
                # Find the latest news brief available as of this date
                date_str = date.strftime("%Y-%m-%d")
                available_news = news_data[news_data['as_of_date'] <= date_str]
                if not available_news.empty:
                    brief = available_news.iloc[-1]['brief_text']
                    
                    # LLM Committee Decision
                    decision = self.committee_decide_allocation(run_id, date, brief, current_alloc, vectorstore)
                    target_alloc = decision.get("primary", {}).get("target_allocation", current_alloc)
                    
                    # For simplicity in this backtest loop, we use instant execution or skip T0/T1 
                    # as we are in a daily loop. A more precise sim would handle T0/T1 transitions.
                    current_alloc = target_alloc
                    
                    history.append({
                        "date": date,
                        "brief": brief,
                        "allocation": target_alloc,
                        "equity": equity
                    })
                    
        return equity_curve, pd.DataFrame(history)

    def run_backtest_B(
        self,
        run_id: str,
        prices: pd.DataFrame,
        signals_data: pd.DataFrame,
        step_days: int = 10,
        initial_alloc: Dict[str, float] = None,
        ticker_map: Optional[Dict[str, str]] = None,
    ) -> Tuple[pd.Series, pd.DataFrame]:
        """Run Backtest Mode B: Strategy Signal driven."""
        if initial_alloc is None:
            initial_alloc = {"stocks": 60, "bonds": 20, "gold": 10, "cash": 10}
            
        calendar = self.build_rebalance_calendar(prices.index, step_days)
        current_alloc = initial_alloc
        
        equity = 1.0
        equity_curve = pd.Series(index=prices.index, dtype=float)
        history = []
        
        ticker_map = ticker_map or self.default_ticker_map()
        
        prices = prices.ffill()
        
        for i, date in enumerate(prices.index):
            if i > 0:
                day_return = 0
                for bucket, ticker in ticker_map.items():
                    if ticker in prices.columns:
                        ret = prices[ticker].iloc[i] / prices[ticker].iloc[i-1] - 1
                        day_return += (current_alloc.get(bucket, 0) / 100.0) * ret
                equity *= (1 + day_return)
            
            equity_curve.iloc[i] = equity
            
            if date in calendar:
                date_str = date.strftime("%Y-%m-%d")
                available_signals = signals_data[signals_data['as_of_date'] <= date_str]
                if not available_signals.empty:
                    signal = available_signals.iloc[-1]
                    risk_bias = float(signal.get('risk_bias', 0))
                    
                    # Simple mapping logic: 
                    # risk_bias=1.0 -> stocks=80, bonds=10, gold=5, cash=5
                    # risk_bias=-1.0 -> stocks=20, bonds=30, gold=15, cash=35
                    # Mid point (0.0): 50/20/10/20
                    
                    if risk_bias >= 0:
                        # scale from 0..1 to 50..80
                        stocks = 50 + 30 * risk_bias
                        bonds = 20 - 10 * risk_bias
                        gold = 10 - 5 * risk_bias
                        cash = 20 - 15 * risk_bias
                    else:
                        # scale from 0..-1 to 50..20
                        rb = abs(risk_bias)
                        stocks = 50 - 30 * rb
                        bonds = 20 + 10 * rb
                        gold = 10 + 5 * rb
                        cash = 20 + 15 * rb
                        
                    target_alloc = {
                        "stocks": round(stocks),
                        "bonds": round(bonds),
                        "gold": round(gold),
                        "cash": round(cash)
                    }
                    
                    # Normalize sum to 100
                    s = sum(target_alloc.values())
                    if s != 100:
                        diff = 100 - s
                        target_alloc["cash"] += diff
                        
                    current_alloc = target_alloc
                    
                    history.append({
                        "date": date,
                        "risk_bias": risk_bias,
                        "allocation": target_alloc,
                        "equity": equity
                    })
                    
        return equity_curve, pd.DataFrame(history)

