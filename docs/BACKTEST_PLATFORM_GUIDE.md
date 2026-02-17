# 輕量級回測平台使用指南

## 📋 概述

IMH 輕量級回測平台基於 **backtesting.py** 構建，提供簡單、快速、實用的策略回測功能。

### 設計理念

- ✅ **輕量級**: 基於 backtesting.py (~500KB),無複雜依賴
- ✅ **快速**: 向量化計算 + 事件驅動，回測速度快
- ✅ **實用**: 集成 Policy Gate 風險限制
- ✅ **簡單**: 清晰的 API + 交互式可視化

### 核心功能

| 功能 | 說明 |
|------|------|
| **策略回測** | 支持自定義策略，基於 OHLCV 數據 |
| **參數優化** | 網格搜索最優參數，支持多指標優化 |
| **風險管理** | 集成 Policy Gate 風險限制 |
| **績效評估** | Sharpe, Sortino, Max Drawdown 等 20+ 指標 |
| **交互式可視化** | Bokeh 交互式權益曲線圖表 |

---

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install backtesting
```

**依賴**:
- backtesting (0.6.5+)
- pandas
- numpy
- bokeh (可視化)

### 2. 準備數據

```python
import pandas as pd
import numpy as np

# 方法 1: 使用 backtesting.py 內置數據
from backtesting.test import GOOG
data = GOOG  # Google 股票數據 (2004-2013)

# 方法 2: 從 CSV 加載
data = pd.read_csv("your_data.csv", parse_dates=True, index_col=0)

# 方法 3: 從 Yahoo Finance 獲取
import yfinance as yf
data = yf.download("AAPL", start="2020-01-01", end="2023-12-31")

# 數據格式要求 (必須包含 OHLC)
#                Open    High     Low   Close    Volume
# 2004-08-19  100.00  104.06   95.96  100.34  22351900
# 2004-08-20  101.01  109.08  100.50  108.31  11428600
```

### 3. 定義策略

```python
from backtesting import Strategy
from backtesting.lib import crossover

class SmaCross(Strategy):
    """雙均線交叉策略"""
    n1 = 10  # 快均線周期
    n2 = 20  # 慢均線周期
    
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
```

### 4. 運行回測

```python
from backtesting import Backtest

# 創建回測實例
bt = Backtest(
    data,
    SmaCross,
    cash=10000,        # 初始資金
    commission=.002,   # 手續費 (0.2%)
    exclusive_orders=True  # 獨占訂單
)

# 運行回測
stats = bt.run(n1=10, n2=20)

# 打印結果
print(stats)
```

### 5. 查看結果

```python
# 打印摘要
print(stats)

# 輸出:
# Start                     2004-08-19 00:00:00
# End                       2013-03-01 00:00:00
# Duration                   3116 days 00:00:00
# Return [%]                             589.35
# Sharpe Ratio                             0.66
# Max. Drawdown [%]                      -33.08
# # Trades                                   93
# Win Rate [%]                            53.76
# ...

# 可視化 (Jupyter Notebook)
bt.plot()
```

---

## 📊 使用 IMH 回測平台

### 示例 1: 基本回測

```python
from services.backtest_platform import BacktestPlatform, SmaCross
from backtesting.test import GOOG

# 1. 創建平台
platform = BacktestPlatform(
    initial_cash=10000,
    commission=0.002
)

# 2. 準備數據
data = GOOG

# 3. 運行回測
stats = platform.run(
    strategy_class=SmaCross,
    data=data,
    strategy_params={"n1": 10, "n2": 20}
)

# 4. 查看結果
stats.print_summary()
```

### 示例 2: 參數優化

```python
# 參數網格
param_grid = {
    "n1": range(5, 21, 5),   # [5, 10, 15, 20]
    "n2": range(10, 41, 10)  # [10, 20, 30, 40]
}

# 運行優化
best_params, best_stats = platform.optimize(
    strategy_class=SmaCross,
    data=data,
    param_grid=param_grid,
    maximize="Sharpe Ratio"  # 最大化夏普比率
)

print(f"最優參數：{best_params}")
print(f"最優夏普比率：{best_stats['Sharpe Ratio']:.2f}")
```

### 示例 3: 多策略比較

```python
from services.backtest_platform import MeanReversion, MomentumBreakout

# 策略 1: 雙均線交叉
stats_sma = platform.run(SmaCross, data, {"n1": 10, "n2": 20})

# 策略 2: 均值回歸
stats_mr = platform.run(MeanReversion, data, {"lookback": 20, "n_std": 2.0})

# 策略 3: 動量突破
stats_mom = platform.run(MomentumBreakout, data, {"lookback": 20})

# 比較結果
comparison = pd.DataFrame({
    "SMA Cross": stats_sma.to_dict(),
    "Mean Reversion": stats_mr.to_dict(),
    "Momentum": stats_mom.to_dict()
})

print(comparison.loc[["Return [%]", "Sharpe Ratio", "Max. Drawdown [%]"]])
```

---

## 📈 內置策略庫

### 1. 雙均線交叉 (SmaCross)

**邏輯**:
- 快均線 (n1) 上穿慢均線 (n2) → 買入
- 快均線 (n1) 下穿慢均線 (n2) → 賣出

**參數**:
- `n1`: 快均線周期 (默认 10)
- `n2`: 慢均線周期 (默认 20)

**適用市場**: 趨勢市場

```python
class SmaCross(Strategy):
    n1 = 10
    n2 = 20
    
    def init(self):
        close = self.data.Close
        self.sma1 = self.I(lambda x: pd.Series(x).rolling(self.n1).mean(), close)
        self.sma2 = self.I(lambda x: pd.Series(x).rolling(self.n2).mean(), close)
    
    def next(self):
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()
```

---

### 2. 均值回歸 (MeanReversion)

**邏輯**:
- 價格低於下軌 (SMA - n_std × STD) → 買入
- 價格高於上軌 (SMA + n_std × STD) → 賣出

**參數**:
- `lookback`: 回顧周期 (默认 20)
- `n_std`: 標準差倍數 (默认 2.0)

**適用市場**: 震盪市場

```python
class MeanReversion(Strategy):
    lookback = 20
    n_std = 2.0
    
    def init(self):
        close = self.data.Close
        self.sma = self.I(lambda x: pd.Series(x).rolling(self.lookback).mean(), close)
        self.std = self.I(lambda x: pd.Series(x).rolling(self.lookback).std(), close)
        self.upper = self.I(lambda: self.sma + self.n_std * self.std)
        self.lower = self.I(lambda: self.sma - self.n_std * self.std)
    
    def next(self):
        price = self.data.Close[-1]
        
        if price < self.lower[-1]:
            if not self.position:
                self.buy()
        elif price > self.upper[-1]:
            if self.position:
                self.position.close()
```

---

### 3. 動量突破 (MomentumBreakout)

**邏輯**:
- 價格突破 N 日高點 → 買入
- 價格跌破 N 日低點 → 賣出

**參數**:
- `lookback`: 回顧周期 (默认 20)

**適用市場**: 突破行情

```python
class MomentumBreakout(Strategy):
    lookback = 20
    
    def init(self):
        high = self.data.High
        low = self.data.Low
        self.highest = self.I(lambda x: pd.Series(x).rolling(self.lookback).max(), high)
        self.lowest = self.I(lambda x: pd.Series(x).rolling(self.lookback).min(), low)
    
    def next(self):
        price = self.data.Close[-1]
        
        if price > self.highest[-1]:
            if not self.position:
                self.buy()
        elif price < self.lowest[-1]:
            if self.position:
                self.position.close()
```

---

## 📊 績效指標說明

### 收益指標

| 指標 | 說明 | 計算方式 | 優秀標準 |
|------|------|---------|---------|
| **總收益率** | 策略總收益 | (期末權益 - 期初權益) / 期初權益 × 100% | > 50% |
| **年化收益率** | 年化平均收益 | 總收益率 / 天數 × 252 | > 15% |
| **買入持有收益率** | 基準收益率 | (期末價格 - 期初價格) / 期初價格 × 100% | - |

### 風險指標

| 指標 | 說明 | 計算方式 | 優秀標準 |
|------|------|---------|---------|
| **夏普比率** | 風險調整後收益 | (年化收益 - 無風險利率) / 年化波動率 | > 1.0 |
| **索提諾比率** | 只考慮下行風險 | (年化收益 - 無風險利率) / 下行波動率 | > 1.5 |
| **最大回撤** | 最大虧損幅度 | (權益峰值 - 權益谷值) / 權益峰值 × 100% | < -20% |
| **年化波動率** | 價格波動程度 | 日收益率標準差 × √252 | < 30% |

### 交易統計

| 指標 | 說明 | 計算方式 | 優秀標準 |
|------|------|---------|---------|
| **總交易次數** | 總交易筆數 | - | > 30 (統計顯著) |
| **勝率** | 盈利交易比例 | 盈利交易數 / 總交易數 × 100% | > 50% |
| **盈虧比** | 平均盈利/平均虧損 | 總盈利 / 總虧損 | > 2.0 |
| **期望值** | 平均每筆交易收益 | 總收益 / 總交易數 | > 1% |

---

## 🔧 高級功能

### 1. 自定義策略

```python
from backtesting import Strategy

class MyCustomStrategy(Strategy):
    # 定義可優化參數
    param1 = 10
    param2 = 0.05
    
    def init(self):
        """初始化指標 (只執行一次)"""
        # 預計算所有指標
        self.indicator1 = self.I(lambda: self.data.Close.rolling(self.param1).mean())
        self.indicator2 = self.I(lambda: (self.data.Close - self.indicator1) / self.indicator1)
    
    def next(self):
        """交易邏輯 (每根 K 線執行)"""
        # 訪問當前數據
        price = self.data.Close[-1]
        signal = self.indicator2[-1]
        
        # 交易邏輯
        if signal < -self.param2:
            self.buy()
        elif signal > self.param2:
            self.sell()
```

### 2. 風險管理集成

```python
from services.backtest_platform import BacktestPlatform, RiskManager

# 創建平台
platform = BacktestPlatform(initial_cash=10000)

# 創建風險管理器
risk_manager = RiskManager(platform.config)

# 應用 Policy Gate 風險限制
risk_manager.apply_policy_gate_constraints(
    regime="bear",  # 熊市
    risk_overlay={
        "multipliers": {"position_size": 0.5},
        "absolute": {"max_drawdown": 0.15}
    }
)

# 運行回測時應用風險限制
# (需要在策略中調用 risk_manager.calculate_position_size)
```

### 3. 止損止盈

```python
class StrategyWithStopLoss(Strategy):
    stop_loss = 0.05  # 5% 止損
    take_profit = 0.10  # 10% 止盈
    
    def next(self):
        if self.position:
            # 檢查止損止盈
            if self.position.is_long:
                if self.data.Close[-1] <= self.position.entry_price * (1 - self.stop_loss):
                    self.position.close()  # 止損
                elif self.data.Close[-1] >= self.position.entry_price * (1 + self.take_profit):
                    self.position.close()  # 止盈
        
        # 開倉邏輯
        if self.should_enter():
            self.buy()
```

### 4. 多品種回測

```python
from backtesting.test import GOOG, AAPL, MSFT

# 準備多個品種數據
data_dict = {
    "GOOG": GOOG,
    "AAPL": AAPL,
    "MSFT": MSFT
}

# 分別回測
results = {}
for symbol, data in data_dict.items():
    stats = platform.run(SmaCross, data, {"n1": 10, "n2": 20})
    results[symbol] = stats

# 比較結果
comparison = pd.DataFrame({
    symbol: stats.to_dict() for symbol, stats in results.items()
})
```

---

## 🐛 故障排查

### 問題 1: 數據格式錯誤

**症狀**: `ValueError: 數據必須包含 Open, High, Low, Close 列`

**解決**:
```python
# 檢查數據列
print(data.columns)

# 確保包含 OHLC
required_columns = ["Open", "High", "Low", "Close"]
for col in required_columns:
    if col not in data.columns:
        raise ValueError(f"缺少 {col} 列")
```

### 問題 2: 保證金不足警告

**症狀**: `UserWarning: Broker canceled the relative-sized order due to insufficient margin`

**解決**:
```python
# 增加初始資金
bt = Backtest(data, Strategy, cash=50000)  # 增加到 50000

# 或降低槓桿
bt = Backtest(data, Strategy, margin=2.0)  # 50% 保證金
```

### 問題 3: 優化時間過長

**症狀**: 參數優化運行數小時

**解決**:
```python
# 減少參數網格
param_grid = {
    "n1": range(5, 21, 5),   # 從 16 個減少到 4 個
    "n2": range(10, 41, 10)  # 從 40 個減少到 4 個
}

# 或使用更少的數據
data_short = data.iloc[:500]  # 只使用前 500 根 K 線
```

---

## 📁 文件結構

```
investment-masters-handbook/
├── services/
│   └── backtest_platform.py      # 回測平台核心代碼
├── examples/
│   └── toy_example_backtest.py   # Toy Example
├── docs/
│   └── BACKTEST_PLATFORM_GUIDE.md  # 使用文檔 (本文件)
└── outputs/
    ├── stats_sma_cross.csv       # 回測結果
    ├── stats_mean_reversion.csv
    └── stats_momentum.csv
```

---

## 🎯 最佳實踐

### 1. 數據質量

**建議**:
- ✅ 使用復權數據 (避免分紅/拆導致的跳空)
- ✅ 確保數據連續 (無缺失交易日)
- ✅ 價格 > 0 (無負值或零值)

**檢查**:
```python
# 檢查缺失值
print(data.isnull().sum())

# 檢查價格
assert (data["Close"] > 0).all(), "存在非正價格"

# 檢查連續性
date_diff = data.index.to_series().diff()
print(f"最大間隔：{date_diff.max().days} 天")
```

### 2. 避免過度擬合

**建議**:
- ✅ 使用樣本外數據驗證
- ✅ 參數數量 < 交易次數 / 10
- ✅ 避免過度優化

**示例**:
```python
# 分割數據
train_data = data.iloc[:2000]  # 訓練集
test_data = data.iloc[2000:]   # 測試集

# 在訓練集優化
best_params, _ = platform.optimize(SmaCross, train_data, param_grid)

# 在測試集驗證
stats = platform.run(SmaCross, test_data, best_params)
```

### 3. 績效評估

**建議**:
- ✅ 對比基準 (買入持有)
- ✅ 考慮交易成本
- ✅ 檢查最大回撤

**示例**:
```python
# 回測結果
stats = platform.run(SmaCross, data)

# 對比基準
print(f"策略收益：{stats['Return [%]']:.2f}%")
print(f"基準收益：{stats['Buy & Hold Return [%]']:.2f}%")
print(f"超額收益：{stats['Return [%]'] - stats['Buy & Hold Return [%]']:.2f}%")

# 檢查風險
print(f"夏普比率：{stats['Sharpe Ratio']:.2f}")
print(f"最大回撤：{stats['Max. Drawdown [%]']:.2f}%")
```

---

## 📊 示例輸出

### 回測結果摘要

```
======================================================================
📊 回測結果摘要
======================================================================

📈 收益指標:
  總收益率：589.35%
  年化收益率：25.42%
  買入持有收益率：703.46%

⚠️ 風險指標:
  夏普比率：0.66
  索提諾比率：1.30
  最大回撤：-33.08%
  年化波動率：38.43%

💼 交易統計:
  總交易次數：93
  勝率：53.8%
  盈虧比：2.13
  期望值：6.91%

📊 交易質量:
  最佳交易：57.12%
  最差交易：-16.63%
  平均交易：1.96%
======================================================================
```

### 參數優化結果

```
🔍 開始參數優化...
  策略：SmaCross
  參數網格：{'n1': [5, 10, 15, 20], 'n2': [10, 20, 30, 40]}
  優化目標：Sharpe Ratio

✅ 優化完成!
  最優參數：{'n1': 10, 'n2': 20}
  最優 Sharpe Ratio: 0.60
```

---

## 🎉 總結

**輕量級回測平台**提供:

✅ **極簡設計**: 基於 backtesting.py, API 清晰  
✅ **快速回測**: 向量化計算 + 事件驅動  
✅ **實用策略**: 3 個內置策略 (SMA Cross, Mean Reversion, Momentum)  
✅ **參數優化**: 網格搜索 + 多指標優化  
✅ **風險管理**: Policy Gate 集成  

**核心理念**: 
> "回測不在複雜，而在實用。每個策略都應該經得起歷史檢驗。"

**下一步**:
- 集成到 Policy Gate API
- 添加更多策略模板
- 支持多品種組合回測

---

## 📚 相關文件

- **核心代碼**: [`services/backtest_platform.py`](file:///d:/Project_dev/investment-masters-handbook/services/backtest_platform.py)
- **Toy Example**: [`examples/toy_example_backtest.py`](file:///d:/Project_dev/investment-masters-handbook/examples/toy_example_backtest.py)
- **backtesting.py 文檔**: https://kernc.github.io/backtesting.py/
