import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from tools.backtest_engine import BacktestEngine

def test_calendar_generation():
    engine = BacktestEngine(results_dir="results_test")
    # 25 trading days
    dates = pd.date_range("2024-01-01", periods=25, freq="B")
    calendar = engine.build_rebalance_calendar(dates, step_trading_days=10)
    
    assert len(calendar) == 3
    assert calendar[0] == dates[0]
    assert calendar[1] == dates[10]
    assert calendar[2] == dates[20]

def test_execution_simulation():
    engine = BacktestEngine(results_dir="results_test")
    current = {"stocks": 60, "bonds": 20, "gold": 10, "cash": 10}
    target = {"stocks": 70, "bonds": 10, "gold": 10, "cash": 10}
    
    stages = engine.simulate_execution(current, target, exec_mode="two_stage")
    assert len(stages) == 2
    
    # T0 (60% of delta)
    # stocks delta = 10, 60% = 6. 60 + 6 = 66
    # bonds delta = -10, 60% = -6. 20 - 6 = 14
    t0 = stages[0]
    assert pytest.approx(t0["stocks"]) == 66.0
    assert pytest.approx(t0["bonds"]) == 14.0
    assert pytest.approx(sum(t0.values())) == 100.0
    
    # T1 (Target)
    assert stages[1] == target

def test_metrics_calculation():
    engine = BacktestEngine(results_dir="results_test")
    # Linear growth
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    equity = pd.Series(np.linspace(1.0, 1.1, 100), index=dates)
    
    metrics = engine.compute_metrics(equity)
    assert metrics["total_return"] == pytest.approx(0.1)
    assert metrics["max_drawdown"] == 0.0 # No drawdown in linear growth
    assert metrics["cagr"] > 0

def test_mode_b_mapping():
    engine = BacktestEngine(results_dir="results_test")
    
    # Fake data
    dates = pd.date_range("2024-01-01", periods=20, freq="B")
    prices = pd.DataFrame({
        "SPY": np.ones(20),
        "SHY": np.ones(20),
        "GLD": np.ones(20),
        "BIL": np.ones(20)
    }, index=dates)
    
    signals = pd.DataFrame([
        {"as_of_date": "2024-01-01", "risk_bias": 1.0},
        {"as_of_date": "2024-01-15", "risk_bias": -1.0}
    ])
    
    curve, hist = engine.run_backtest_B("test_run", prices, signals, step_days=10)
    
    # i=0 (2024-01-01) rebalance to risk_bias=1.0
    # risk_bias=1.0 -> stocks=80, bonds=10, gold=5, cash=5
    assert hist.iloc[0]["allocation"]["stocks"] == 80
    
    # i=10 (2024-01-15 approx) rebalance to risk_bias=-1.0
    # risk_bias=-1.0 -> stocks=20, bonds=30, gold=15, cash=35
    assert hist.iloc[1]["allocation"]["stocks"] == 20

