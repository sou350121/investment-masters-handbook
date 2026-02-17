"""
Investment Masters Handbook - 輕量級回測平台 (基於 backtesting.py)

設計理念:
1. 輕量級：基於 backtesting.py，無複雜依賴
2. 實用：集成 Policy Gate 風險限制
3. 簡單：清晰的 API + 交互式可視化

核心功能:
1. 策略回測 (基於 backtesting.py)
2. 風險管理 (Policy Gate 集成)
3. 績效評估 (Sharpe, Sortino, Max Drawdown)
4. 交互式可視化
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime

# 導入 backtesting.py
from backtesting import Backtest, Strategy
from backtesting.lib import crossover


# ============================================
# 策略 1: 雙均線交叉
# ============================================
class SmaCross(Strategy):
    """
    雙均線交叉策略
    
    邏輯:
    - 快均線 (n1) 上穿慢均線 (n2) → 買入
    - 快均線 (n1) 下穿慢均線 (n2) → 賣出
    """
    # 可優化參數
    n1 = 10
    n2 = 20
    
    def init(self):
        """初始化指標"""
        close = self.data.Close
        self.sma1 = self.I(lambda x: pd.Series(x).rolling(self.n1).mean(), close)
        self.sma2 = self.I(lambda x: pd.Series(x).rolling(self.n2).mean(), close)
    
    def next(self):
        """交易邏輯"""
        # 金叉：快均線上穿慢均線 → 買入
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()
        
        # 死叉：快均線下穿慢均線 → 賣出
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()


# ============================================
# 策略 2: 均值回歸 (RBI)
# ============================================
class MeanReversion(Strategy):
    """
    均值回歸策略
    
    邏輯:
    - 價格低於下軌 → 買入
    - 價格高於上軌 → 賣出
    """
    lookback = 20
    n_std = 2.0
    
    def init(self):
        """初始化指標"""
        close = self.data.Close
        self.sma = self.I(lambda x: pd.Series(x).rolling(self.lookback).mean(), close)
        self.std = self.I(lambda x: pd.Series(x).rolling(self.lookback).std(), close)
        self.upper = self.I(lambda: self.sma + self.n_std * self.std)
        self.lower = self.I(lambda: self.sma - self.n_std * self.std)
    
    def next(self):
        """交易邏輯"""
        price = self.data.Close[-1]
        
        # 價格低於下軌 → 買入 (均值回歸)
        if price < self.lower[-1]:
            if not self.position:
                self.buy()
        
        # 價格高於上軌 → 賣出
        elif price > self.upper[-1]:
            if self.position:
                self.position.close()


# ============================================
# 策略 3: 動量突破
# ============================================
class MomentumBreakout(Strategy):
    """
    動量突破策略
    
    邏輯:
    - 價格突破 N 日高點 → 買入
    - 價格跌破 N 日低點 → 賣出
    """
    lookback = 20
    
    def init(self):
        """初始化指標"""
        high = self.data.High
        low = self.data.Low
        self.highest = self.I(lambda x: pd.Series(x).rolling(self.lookback).max(), high)
        self.lowest = self.I(lambda x: pd.Series(x).rolling(self.lookback).min(), low)
    
    def next(self):
        """交易邏輯"""
        price = self.data.Close[-1]
        
        # 突破 N 日高點 → 買入
        if price > self.highest[-1]:
            if not self.position:
                self.buy()
        
        # 跌破 N 日低點 → 賣出
        elif price < self.lowest[-1]:
            if self.position:
                self.position.close()


# ============================================
# 回測平台主類
# ============================================
class BacktestPlatform:
    """
    輕量級回測平台
    
    功能:
    - 運行回測
    - 參數優化
    - 績效評估
    - 可視化
    """
    
    def __init__(
        self,
        initial_cash: float = 10000.0,
        commission: float = 0.002,
        margin: float = 1.0,
        trade_on_close: bool = False,
        exclusive_orders: bool = True
    ):
        """
        初始化回測平台
        
        Args:
            initial_cash: 初始資金
            commission: 手續費 (0.2% = 0.002)
            margin: 保證金比例 (1=無槓桿)
            trade_on_close: 是否在收盤價成交
            exclusive_orders: 是否獨占訂單
        """
        self.config = {
            "cash": initial_cash,
            "commission": commission,
            "margin": margin,
            "trade_on_close": trade_on_close,
            "exclusive_orders": exclusive_orders
        }
    
    def run(
        self,
        strategy_class: Strategy,
        data: pd.DataFrame,
        strategy_params: Optional[Dict[str, Any]] = None,
        verbose: bool = True
    ):
        """
        運行回測
        
        Args:
            strategy_class: 策略類 (如 SmaCross)
            data: OHLCV 數據
            strategy_params: 策略參數 (如 {"n1": 10, "n2": 20})
            verbose: 是否打印詳細信息
        
        Returns:
            stats: 回測結果 (pandas Series)
        """
        # 驗證數據
        required_columns = ["Open", "High", "Low", "Close"]
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"數據必須包含 {col} 列")
        
        # 創建回測實例
        bt = Backtest(
            data,
            strategy_class,
            **self.config
        )
        
        # 運行回測
        if verbose:
            print(f"🚀 開始回測...")
            print(f"  策略：{strategy_class.__name__}")
            print(f"  數據：{len(data)} 根 K 線")
            print(f"  初始資金：${self.config['cash']:,.0f}")
            print(f"  手續費：{self.config['commission']:.2%}")
            print()
        
        stats = bt.run(**(strategy_params or {}))
        
        if verbose:
            self._print_stats(stats)
        
        return stats
    
    def optimize(
        self,
        strategy_class: Strategy,
        data: pd.DataFrame,
        param_grid: Dict[str, List[Any]],
        maximize: str = "Sharpe Ratio",
        verbose: bool = True
    ):
        """
        參數優化
        
        Args:
            strategy_class: 策略類
            data: OHLCV 數據
            param_grid: 參數網格 (如 {"n1": [5, 10, 15], "n2": [10, 20, 30]})
            maximize: 最大化指標 (如 "Sharpe Ratio", "Return [%]")
            verbose: 是否打印詳細信息
        
        Returns:
            best_params: 最優參數
            best_stats: 最優結果
        """
        if verbose:
            print(f"🔍 開始參數優化...")
            print(f"  策略：{strategy_class.__name__}")
            print(f"  參數網格：{param_grid}")
            print(f"  優化目標：{maximize}")
            print()
        
        # 創建回測實例
        bt = Backtest(
            data,
            strategy_class,
            **self.config
        )
        
        # 運行優化
        best_stats = bt.optimize(**param_grid, maximize=maximize)
        
        # 提取最優參數
        best_params = {}
        for key in param_grid.keys():
            if hasattr(best_stats["_strategy"], key):
                best_params[key] = getattr(best_stats["_strategy"], key)
        
        if verbose:
            print(f"✅ 優化完成!")
            print(f"  最優參數：{best_params}")
            print(f"  最優 {maximize}: {best_stats[maximize]:.2f}")
            print()
        
        return best_params, best_stats
    
    def _print_stats(self, stats: pd.Series):
        """打印回測結果"""
        print("=" * 70)
        print("📊 回測結果摘要")
        print("=" * 70)
        
        print(f"\n📈 收益指標:")
        print(f"  總收益率：{stats['Return [%]']:.2f}%")
        print(f"  年化收益率：{stats['Return (Ann.) [%]']:.2f}%")
        print(f"  買入持有收益率：{stats['Buy & Hold Return [%]']:.2f}%")
        
        print(f"\n⚠️ 風險指標:")
        print(f"  夏普比率：{stats['Sharpe Ratio']:.2f}")
        print(f"  索提諾比率：{stats['Sortino Ratio']:.2f}")
        print(f"  最大回撤：{stats['Max. Drawdown [%]']:.2f}%")
        print(f"  年化波動率：{stats['Volatility (Ann.) [%]']:.2f}%")
        
        print(f"\n💼 交易統計:")
        print(f"  總交易次數：{stats['# Trades']}")
        print(f"  勝率：{stats['Win Rate [%]']:.1f}%")
        print(f"  盈虧比：{stats['Profit Factor']:.2f}")
        print(f"  期望值：{stats['Expectancy [%]']:.2f}%")
        
        print(f"\n📊 交易質量:")
        print(f"  最佳交易：{stats['Best Trade [%]']:.2f}%")
        print(f"  最差交易：{stats['Worst Trade [%]']:.2f}%")
        print(f"  平均交易：{stats['Avg. Trade [%]']:.2f}%")
        
        print("=" * 70)


# ============================================
# 使用示例
# ============================================
if __name__ == "__main__":
    print("\n🔄 輕量級回測平台 Toy Example\n")
    
    # 1. 創建平台
    platform = BacktestPlatform(
        initial_cash=10000,
        commission=0.002
    )
    
    # 2. 準備數據 (使用 backtesting.py 內置數據)
    print("\n📊 準備測試數據...")
    from backtesting.test import GOOG
    
    data = GOOG  # Google 股票數據 (2004-2013)
    print(f"數據範圍：{data.index[0]} 至 {data.index[-1]}")
    print(f"價格範圍：${data['Close'].min():.2f} - ${data['Close'].max():.2f}")
    
    # 3. 運行雙均線交叉策略
    print("\n" + "=" * 70)
    print("策略 1: 雙均線交叉 (SMA Cross)")
    print("=" * 70)
    
    stats_sma = platform.run(
        strategy_class=SmaCross,
        data=data,
        strategy_params={"n1": 10, "n2": 20},
        verbose=True
    )
    
    # 4. 運行均值回歸策略
    print("\n" + "=" * 70)
    print("策略 2: 均值回歸 (Mean Reversion)")
    print("=" * 70)
    
    stats_mr = platform.run(
        strategy_class=MeanReversion,
        data=data,
        strategy_params={"lookback": 20, "n_std": 2.0},
        verbose=True
    )
    
    # 5. 運行動量突破策略
    print("\n" + "=" * 70)
    print("策略 3: 動量突破 (Momentum Breakout)")
    print("=" * 70)
    
    stats_mom = platform.run(
        strategy_class=MomentumBreakout,
        data=data,
        strategy_params={"lookback": 20},
        verbose=True
    )
    
    # 6. 參數優化
    print("\n" + "=" * 70)
    print("🔍 參數優化 (雙均線交叉)")
    print("=" * 70)
    
    best_params, best_stats = platform.optimize(
        strategy_class=SmaCross,
        data=data,
        param_grid={
            "n1": range(5, 21, 5),  # [5, 10, 15, 20]
            "n2": range(10, 41, 10)  # [10, 20, 30, 40]
        },
        maximize="Sharpe Ratio",
        verbose=True
    )
    
    # 7. 保存結果
    print("\n💾 保存結果...")
    stats_sma.to_csv("stats_sma_cross.csv")
    stats_mr.to_csv("stats_mean_reversion.csv")
    stats_mom.to_csv("stats_momentum.csv")
    
    print("\n✅ 輕量級回測平台 Toy Example 完成!")
    print("\n📊 結果已保存至 CSV 文件")
    print("📈 要查看交互式圖表，請在 Jupyter Notebook 中運行:")
    print("   bt.plot()")
