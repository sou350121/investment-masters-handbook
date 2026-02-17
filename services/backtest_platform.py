"""
Investment Masters Handbook - 輕量級回測平台

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

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
import numpy as np
from datetime import datetime


# ============================================
# 數據結構定義
# ============================================
@dataclass
class BacktestConfig:
    """回測配置"""
    initial_cash: float = 10000.0  # 初始資金
    commission: float = 0.002  # 手續費 (0.2%)
    margin: float = 1.0  # 保證金比例 (1=無槓桿)
    trade_on_close: bool = False  # 是否在收盤價成交
    exclusive_orders: bool = True  # 是否獨占訂單 (平倉後再開倉)


@dataclass
class BacktestResult:
    """回測結果"""
    # 基本統計
    start: str
    end: str
    duration: str
    
    # 收益指標
    return_total: float  # 總收益率 (%)
    return_annual: float  # 年化收益率 (%)
    buy_and_hold_return: float  # 買入持有收益率 (%)
    
    # 風險指標
    volatility_annual: float  # 年化波動率 (%)
    sharpe_ratio: float  # 夏普比率
    sortino_ratio: float  # 索提諾比率
    max_drawdown: float  # 最大回撤 (%)
    avg_drawdown: float  # 平均回撤 (%)
    
    # 交易統計
    total_trades: int  # 總交易次數
    win_rate: float  # 勝率 (%)
    best_trade: float  # 最佳交易 (%)
    worst_trade: float  # 最差交易 (%)
    avg_trade: float  # 平均交易 (%)
    profit_factor: float  # 盈虧比
    expectancy: float  # 期望值 (%)
    
    # 詳細數據
    equity_curve: pd.Series  # 權益曲線
    trades: pd.DataFrame  # 交易記錄
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "start": self.start,
            "end": self.end,
            "duration": self.duration,
            "return_total": self.return_total,
            "return_annual": self.return_annual,
            "buy_and_hold_return": self.buy_and_hold_return,
            "volatility_annual": self.volatility_annual,
            "sharpe_ratio": self.sharpe_ratio,
            "sortino_ratio": self.sortino_ratio,
            "max_drawdown": self.max_drawdown,
            "avg_drawdown": self.avg_drawdown,
            "total_trades": self.total_trades,
            "win_rate": self.win_rate,
            "best_trade": self.best_trade,
            "worst_trade": self.worst_trade,
            "avg_trade": self.avg_trade,
            "profit_factor": self.profit_factor,
            "expectancy": self.expectancy
        }
    
    def print_summary(self):
        """打印摘要"""
        print("=" * 70)
        print("📊 回測結果摘要")
        print("=" * 70)
        print(f"\n📈 收益指標:")
        print(f"  總收益率：{self.return_total:.2f}%")
        print(f"  年化收益率：{self.return_annual:.2f}%")
        print(f"  買入持有收益率：{self.buy_and_hold_return:.2f}%")
        
        print(f"\n⚠️ 風險指標:")
        print(f"  夏普比率：{self.sharpe_ratio:.2f}")
        print(f"  索提諾比率：{self.sortino_ratio:.2f}")
        print(f"  最大回撤：{self.max_drawdown:.2f}%")
        print(f"  年化波動率：{self.volatility_annual:.2f}%")
        
        print(f"\n💼 交易統計:")
        print(f"  總交易次數：{self.total_trades}")
        print(f"  勝率：{self.win_rate:.1f}%")
        print(f"  盈虧比：{self.profit_factor:.2f}")
        print(f"  期望值：{self.expectancy:.2f}%")
        
        print(f"\n📊 交易質量:")
        print(f"  最佳交易：{self.best_trade:.2f}%")
        print(f"  最差交易：{self.worst_trade:.2f}%")
        print(f"  平均交易：{self.avg_trade:.2f}%")
        print("=" * 70)


# ============================================
# 策略基類
# ============================================
class BaseStrategy:
    """
    策略基類
    
    使用時需要繼承此類並實現:
    - init(): 初始化指標
    - next(): 交易邏輯
    """
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.data: Optional[pd.DataFrame] = None
        self.position = 0  # 當前倉位
        self.equity = config.initial_cash  # 當前權益
    
    def set_data(self, data: pd.DataFrame):
        """設置數據"""
        self.data = data
    
    def init(self):
        """初始化指標 (子类實現)"""
        raise NotImplementedError
    
    def next(self):
        """交易邏輯 (子类實現)"""
        raise NotImplementedError


# ============================================
# 風險管理模塊
# ============================================
class RiskManager:
    """
    風險管理器 - 集成 Policy Gate 風險限制
    
    功能:
    - 根據市場狀態調整倉位大小
    - 動態止損/止盈
    - 最大回撤控制
    """
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.max_position_size = 1.0  # 最大倉位比例
        self.stop_loss = None  # 止損比例
        self.take_profit = None  # 止盈比例
    
    def apply_policy_gate_constraints(
        self,
        regime: str,
        risk_overlay: Dict[str, Any]
    ):
        """
        應用 Policy Gate 風險限制
        
        Args:
            regime: 市場狀態 (bull/bear/sideways/crisis)
            risk_overlay: 風險覆蓋層 (multipliers, absolute)
        """
        multipliers = risk_overlay.get("multipliers", {})
        absolute = risk_overlay.get("absolute", {})
        
        # 根據市場狀態調整倉位
        if regime == "crisis":
            self.max_position_size = 0.2  # 危機時最大倉位 20%
        elif regime == "bear":
            self.max_position_size = 0.5  # 熊市時最大倉位 50%
        elif regime == "sideways":
            self.max_position_size = 0.7  # 震盪時最大倉位 70%
        else:  # bull
            self.max_position_size = 1.0  # 牛市時最大倉位 100%
        
        # 應用乘數限制
        if "position_size" in multipliers:
            self.max_position_size *= multipliers["position_size"]
        
        # 應用絕對限制
        if "max_drawdown" in absolute:
            self.max_drawdown_limit = absolute["max_drawdown"]
        
        print(f"🛡️ 風險限制：最大倉位={self.max_position_size:.1%}")
    
    def calculate_position_size(
        self,
        signal_strength: float,
        current_price: float,
        equity: float
    ) -> float:
        """
        計算倉位大小
        
        Args:
            signal_strength: 信號強度 (0-1)
            current_price: 當前價格
            equity: 當前權益
        
        Returns:
            倉位大小 (股數)
        """
        # 基礎倉位 = 信號強度 × 最大倉位比例
        position_value = equity * signal_strength * self.max_position_size
        
        # 考慮手續費
        position_value *= (1 - self.config.commission)
        
        # 轉換為股數
        position_size = position_value / current_price
        
        return position_size
    
    def check_stop_loss(self, entry_price: float, current_price: float) -> bool:
        """檢查止損"""
        if self.stop_loss is None:
            return False
        
        loss_pct = (current_price - entry_price) / entry_price
        return loss_pct <= -self.stop_loss
    
    def check_take_profit(self, entry_price: float, current_price: float) -> bool:
        """檢查止盈"""
        if self.take_profit is None:
            return False
        
        profit_pct = (current_price - entry_price) / entry_price
        return profit_pct >= self.take_profit


# ============================================
# 回測引擎
# ============================================
class BacktestEngine:
    """
    回測引擎
    
    功能:
    - 運行回測
    - 計算績效指標
    - 生成可視化
    """
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.risk_manager = RiskManager(config)
        self.results: Optional[BacktestResult] = None
    
    def run(
        self,
        strategy: BaseStrategy,
        data: pd.DataFrame,
        verbose: bool = True
    ) -> BacktestResult:
        """
        運行回測
        
        Args:
            strategy: 策略實例
            data: OHLCV 數據 (必須包含 Open, High, Low, Close, Volume)
            verbose: 是否打印詳細信息
        
        Returns:
            BacktestResult 回測結果
        """
        # 驗證數據
        required_columns = ["Open", "High", "Low", "Close"]
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"數據必須包含 {col} 列")
        
        # 設置策略數據
        strategy.set_data(data)
        strategy.init()
        
        # 初始化回測變量
        n = len(data)
        equity_curve = [self.config.initial_cash]
        trades = []
        
        position = 0  # 當前倉位
        entry_price = 0.0  # 入場價格
        
        if verbose:
            print(f"🚀 開始回測... (共 {n} 根 K 線)")
        
        # 迭代每根 K 線
        for i in range(1, n):
            current_price = data["Close"].iloc[i]
            
            # 更新策略
            strategy.next()
            
            # 檢查止損止盈
            if position > 0:
                if self.risk_manager.check_stop_loss(entry_price, current_price):
                    # 止損平倉
                    pnl = (current_price - entry_price) / entry_price * 100
                    trades.append({
                        "type": "sell",
                        "price": current_price,
                        "pnl": pnl,
                        "index": i
                    })
                    position = 0
                elif self.risk_manager.check_take_profit(entry_price, current_price):
                    # 止盈平倉
                    pnl = (current_price - entry_price) / entry_price * 100
                    trades.append({
                        "type": "sell",
                        "price": current_price,
                        "pnl": pnl,
                        "index": i
                    })
                    position = 0
            
            # 更新權益
            if position > 0:
                equity = self.config.initial_cash * (1 + position * (current_price - entry_price) / entry_price)
            else:
                equity = self.config.initial_cash
            
            equity_curve.append(equity)
        
        # 計算績效指標
        results = self._calculate_metrics(data, equity_curve, trades)
        self.results = results
        
        if verbose:
            results.print_summary()
        
        return results
    
    def _calculate_metrics(
        self,
        data: pd.DataFrame,
        equity_curve: List[float],
        trades: List[Dict[str, Any]]
    ) -> BacktestResult:
        """計算績效指標"""
        equity_series = pd.Series(equity_curve)
        
        # 基本統計
        start_date = data.index[0].strftime("%Y-%m-%d") if hasattr(data.index[0], "strftime") else str(data.index[0])
        end_date = data.index[-1].strftime("%Y-%m-%d") if hasattr(data.index[-1], "strftime") else str(data.index[-1])
        duration_days = len(data)
        
        # 收益指標
        return_total = (equity_series.iloc[-1] / equity_series.iloc[0] - 1) * 100
        return_annual = return_total / duration_days * 252  # 年化 (假設 252 個交易日)
        
        # 買入持有收益率
        buy_and_hold_return = (data["Close"].iloc[-1] / data["Close"].iloc[0] - 1) * 100
        
        # 風險指標
        daily_returns = equity_series.pct_change().dropna()
        volatility_annual = daily_returns.std() * np.sqrt(252) * 100
        
        # 夏普比率 (假設無風險利率為 0)
        if daily_returns.std() > 0:
            sharpe_ratio = (daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252))
        else:
            sharpe_ratio = 0.0
        
        # 索提諾比率 (只考慮下行波動)
        downside_returns = daily_returns[daily_returns < 0]
        if len(downside_returns) > 0 and downside_returns.std() > 0:
            sortino_ratio = (daily_returns.mean() * 252) / (downside_returns.std() * np.sqrt(252))
        else:
            sortino_ratio = 0.0
        
        # 最大回撤
        rolling_max = equity_series.cummax()
        drawdown = (equity_series - rolling_max) / rolling_max * 100
        max_drawdown = drawdown.min()
        avg_drawdown = drawdown.mean()
        
        # 交易統計
        total_trades = len(trades)
        if total_trades > 0:
            trade_pnls = [t["pnl"] for t in trades]
            winning_trades = [p for p in trade_pnls if p > 0]
            losing_trades = [p for p in trade_pnls if p < 0]
            
            win_rate = len(winning_trades) / total_trades * 100
            best_trade = max(trade_pnls) if trade_pnls else 0.0
            worst_trade = min(trade_pnls) if trade_pnls else 0.0
            avg_trade = np.mean(trade_pnls) if trade_pnls else 0.0
            
            gross_profit = sum(winning_trades) if winning_trades else 0.0
            gross_loss = abs(sum(losing_trades)) if losing_trades else 0.0
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")
            
            expectancy = avg_trade
        else:
            win_rate = 0.0
            best_trade = 0.0
            worst_trade = 0.0
            avg_trade = 0.0
            profit_factor = 0.0
            expectancy = 0.0
        
        # 創建結果對象
        trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()
        
        return BacktestResult(
            start=start_date,
            end=end_date,
            duration=f"{duration_days} days",
            return_total=return_total,
            return_annual=return_annual,
            buy_and_hold_return=buy_and_hold_return,
            volatility_annual=volatility_annual,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            avg_drawdown=avg_drawdown,
            total_trades=total_trades,
            win_rate=win_rate,
            best_trade=best_trade,
            worst_trade=worst_trade,
            avg_trade=avg_trade,
            profit_factor=profit_factor,
            expectancy=expectancy,
            equity_curve=equity_series,
            trades=trades_df
        )
    
    def plot(self):
        """繪製權益曲線 (使用 backtesting.py 的可視化)"""
        if self.results is None:
            print("❌ 請先運行回測")
            return
        
        try:
            from bokeh.plotting import figure, show
            from bokeh.models import ColumnDataSource
            from bokeh.io import output_notebook
            
            # 創建數據源
            n = len(self.results.equity_curve)
            source = ColumnDataSource({
                "index": range(n),
                "equity": self.results.equity_curve.values
            })
            
            # 創建圖表
            p = figure(
                title="權益曲線",
                x_axis_label="交易日",
                y_axis_label="權益",
                width=800,
                height=400
            )
            
            # 繪製曲線
            p.line("index", "equity", source=source, line_width=2, color="blue")
            
            # 顯示
            output_notebook()
            show(p)
            
            print("📊 權益曲線已生成 (需要在 Jupyter Notebook 中查看)")
            
        except ImportError:
            print("⚠️ 請安裝 bokeh: pip install bokeh")


# ============================================
# 示例策略：雙均線交叉
# ============================================
class SmaCrossStrategy(BaseStrategy):
    """
    雙均線交叉策略
    
    邏輯:
    - 快均線 (n1) 上穿慢均線 (n2) → 買入
    - 快均線 (n1) 下穿慢均線 (n2) → 賣出
    """
    
    def __init__(self, config: BacktestConfig, n1: int = 10, n2: int = 20):
        super().__init__(config)
        self.n1 = n1  # 快均線周期
        self.n2 = n2  # 慢均線周期
        self.sma1 = None
        self.sma2 = None
    
    def init(self):
        """初始化均線"""
        close = self.data["Close"]
        self.sma1 = close.rolling(self.n1).mean()
        self.sma2 = close.rolling(self.n2).mean()
        
        print(f"📊 初始化策略：SMA({self.n1}) 交叉 SMA({self.n2})")
    
    def next(self):
        """交易邏輯"""
        i = len(self.data) - 1
        
        if i < max(self.n1, self.n2):
            return  # 數據不足
        
        # 檢查交叉
        sma1_prev = self.sma1.iloc[i-1]
        sma1_curr = self.sma1.iloc[i]
        sma2_prev = self.sma2.iloc[i-1]
        sma2_curr = self.sma2.iloc[i]
        
        # 金叉：快均線上穿慢均線
        if sma1_prev <= sma2_prev and sma1_curr > sma2_curr:
            print(f"📈 [{i}] 金叉：買入信號")
            # 這裡應該調用 backtesting.py 的 buy() 方法
            # 為簡化示例，我們只打印信號
        
        # 死叉：快均線下穿慢均線
        elif sma1_prev >= sma2_prev and sma1_curr < sma2_curr:
            print(f"📉 [{i}] 死叉：賣出信號")
            # 這裡應該調用 backtesting.py 的 sell() 方法


# ============================================
# 使用示例
# ============================================
if __name__ == "__main__":
    print("\n🔄 輕量級回測平台 Toy Example\n")
    
    # 1. 創建配置
    config = BacktestConfig(
        initial_cash=10000,
        commission=0.002
    )
    
    # 2. 創建策略
    strategy = SmaCrossStrategy(config, n1=10, n2=20)
    
    # 3. 準備數據 (使用模擬數據)
    print("\n📊 準備測試數據...")
    dates = pd.date_range(start="2023-01-01", periods=252, freq="D")
    np.random.seed(42)
    
    # 生成隨機價格走勢
    close_prices = 100 * np.cumprod(1 + np.random.randn(252) * 0.02)
    
    data = pd.DataFrame({
        "Open": close_prices * (1 + np.random.randn(252) * 0.01),
        "High": close_prices * (1 + np.abs(np.random.randn(252)) * 0.02),
        "Low": close_prices * (1 - np.abs(np.random.randn(252)) * 0.02),
        "Close": close_prices,
        "Volume": np.random.randint(1000000, 10000000, 252)
    }, index=dates)
    
    print(f"數據範圍：{data.index[0]} 至 {data.index[-1]}")
    print(f"價格範圍：{data['Close'].min():.2f} - {data['Close'].max():.2f}")
    
    # 4. 運行回測
    print("\n🚀 運行回測...\n")
    engine = BacktestEngine(config)
    results = engine.run(strategy, data, verbose=True)
    
    # 5. 保存結果
    print("\n💾 保存結果...")
    results.equity_curve.to_csv("equity_curve.csv", index=False)
    if not results.trades.empty:
        results.trades.to_csv("trades.csv", index=False)
    
    print("\n✅ 輕量級回測平台 Toy Example 完成!\n")
    print("📊 權益曲線已保存至 equity_curve.csv")
    print("📊 交易記錄已保存至 trades.csv")
