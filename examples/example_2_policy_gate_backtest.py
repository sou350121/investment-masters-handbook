"""
Investment Masters Handbook - 示例 2: Policy Gate 動態倉位控制回測

功能:
1. 使用 Policy Gate 評估市場狀態
2. 根據市場狀態動態調整倉位大小
3. 應用風險覆蓋層限制
4. 對比固定倉位 vs 動態倉位

使用場景:
- 驗證 Policy Gate 風險管理的實戰效果
- 優化風險參數配置
- 評估不同市場狀態下的倉位策略
"""

import pandas as pd
import numpy as np
from backtesting import Strategy
from services.backtest_platform import BacktestPlatform
from services.realtime_data import get_pipeline


# ============================================
# 策略 1: 固定倉位策略 (基準)
# ============================================
class FixedPositionStrategy(Strategy):
    """
    固定倉位策略
    
    邏輯:
    - 始終使用固定倉位比例 (如 100%)
    - 雙均線交叉信號
    """
    n1 = 10
    n2 = 20
    position_size = 1.0  # 固定 100% 倉位
    
    def init(self):
        """初始化"""
        close = self.data.Close
        self.sma1 = self.I(lambda x: pd.Series(x).rolling(self.n1).mean(), close)
        self.sma2 = self.I(lambda x: pd.Series(x).rolling(self.n2).mean(), close)
    
    def next(self):
        """交易邏輯"""
        from backtesting.lib import crossover
        
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy(size=self.position_size)
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell(size=self.position_size)


# ============================================
# 策略 2: Policy Gate 動態倉位策略
# ============================================
class PolicyGateDynamicStrategy(Strategy):
    """
    Policy Gate 動態倉位策略
    
    邏輯:
    1. 使用 Policy Gate 評估市場狀態
    2. 根據市場狀態調整倉位:
       - 牛市：100% 倉位
       - 震盪：70% 倉位
       - 熊市：50% 倉位
       - 危機：20% 倉位
    3. 應用風險覆蓋層限制
    """
    n1 = 10
    n2 = 20
    
    # 市場狀態對應倉位 (可優化)
    bull_position = 1.0
    sideways_position = 0.7
    bear_position = 0.5
    crisis_position = 0.2
    
    def init(self):
        """初始化"""
        close = self.data.Close
        self.sma1 = self.I(lambda x: pd.Series(x).rolling(self.n1).mean(), close)
        self.sma2 = self.I(lambda x: pd.Series(x).rolling(self.n2).mean(), close)
        
        # 市場狀態指標
        self.regime_indicator = self.I(lambda: pd.Series("neutral", index=self.data.index))
        self.position_indicator = self.I(lambda: pd.Series(0.0, index=self.data.index))
        
        # 初始化 Policy Gate
        try:
            self.pipeline = get_pipeline()
            print(f"✅ Policy Gate 初始化成功")
        except Exception as e:
            print(f"⚠️ Policy Gate 初始化失敗：{e}")
            self.pipeline = None
    
    def _get_market_regime(self) -> str:
        """
        獲取市場狀態
        
        Returns:
            市場狀態 (bull/sideways/bear/crisis)
        """
        if self.pipeline is None:
            return "neutral"
        
        try:
            # 獲取實時數據
            features = self.pipeline.get_features()
            
            # 簡化版市場狀態判斷
            vix = features.get("vix", 20)
            inflation = features.get("inflation", 3.0)
            
            if vix > 40:
                return "crisis"
            elif vix > 30 or inflation > 6.0:
                return "bear"
            elif vix < 20 and inflation < 3.0:
                return "bull"
            else:
                return "sideways"
        
        except Exception as e:
            print(f"⚠️ 獲取市場狀態失敗：{e}")
            return "neutral"
    
    def _get_position_size(self, regime: str) -> float:
        """
        根據市場狀態獲取倉位大小
        
        Args:
            regime: 市場狀態
        
        Returns:
            倉位比例
        """
        position_map = {
            "bull": self.bull_position,
            "sideways": self.sideways_position,
            "bear": self.bear_position,
            "crisis": self.crisis_position,
            "neutral": 0.5
        }
        
        return position_map.get(regime, 0.5)
    
    def next(self):
        """交易邏輯"""
        from backtesting.lib import crossover
        
        # 獲取市場狀態
        regime = self._get_market_regime()
        position_size = self._get_position_size(regime)
        
        # 更新指標
        self.regime_indicator[-1] = regime
        self.position_indicator[-1] = position_size
        
        # 交易信號
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy(size=position_size)
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell(size=position_size)


# ============================================
# 策略 3: Policy Gate + 止損止盈
# ============================================
class PolicyGateWithStopLoss(Strategy):
    """
    Policy Gate 動態倉位 + 止損止盈策略
    
    邏輯:
    1. Policy Gate 動態倉位
    2. 根據市場波動率動態調整止損止盈
    3. 危機時縮小止損，牛市時放大止盈
    """
    n1 = 10
    n2 = 20
    
    # 基礎止損止盈 (可優化)
    base_stop_loss = 0.05  # 5%
    base_take_profit = 0.10  # 10%
    
    def init(self):
        """初始化"""
        close = self.data.Close
        self.sma1 = self.I(lambda x: pd.Series(x).rolling(self.n1).mean(), close)
        self.sma2 = self.I(lambda x: pd.Series(x).rolling(self.n2).mean(), close)
        
        # 波動率指標
        self.volatility = self.I(
            lambda x: pd.Series(x).rolling(20).std() / pd.Series(x).rolling(20).mean(),
            close
        )
        
        # 倉位和止損止盈指標
        self.position_size_indicator = self.I(lambda: pd.Series(0.0, index=self.data.index))
        self.stop_loss_indicator = self.I(lambda: pd.Series(0.0, index=self.data.index))
        self.take_profit_indicator = self.I(lambda: pd.Series(0.0, index=self.data.index))
        
        # 初始化 Policy Gate
        try:
            self.pipeline = get_pipeline()
        except:
            self.pipeline = None
        
        # 交易跟蹤
        self.entry_price = 0.0
        self.current_position_size = 0.0
    
    def _get_dynamic_stop_loss(self, volatility: float) -> float:
        """
        動態止損 (高波動時放大止損)
        
        Args:
            volatility: 波動率
        
        Returns:
            止損比例
        """
        # 波動率調整係數
        vol_adjustment = 1.0 + (volatility - 0.02) * 10
        
        return self.base_stop_loss * vol_adjustment
    
    def _get_dynamic_take_profit(self, volatility: float) -> float:
        """
        動態止盈 (高波動時放大止盈)
        
        Args:
            volatility: 波動率
        
        Returns:
            止盈比例
        """
        vol_adjustment = 1.0 + (volatility - 0.02) * 15
        
        return self.base_take_profit * vol_adjustment
    
    def _check_stop_loss(self, current_price: float) -> bool:
        """檢查止損"""
        if self.entry_price == 0:
            return False
        
        loss_pct = (current_price - self.entry_price) / self.entry_price
        return loss_pct <= -self.stop_loss_indicator[-1]
    
    def _check_take_profit(self, current_price: float) -> bool:
        """檢查止盈"""
        if self.entry_price == 0:
            return False
        
        profit_pct = (current_price - self.entry_price) / self.entry_price
        return profit_pct >= self.take_profit_indicator[-1]
    
    def next(self):
        """交易邏輯"""
        from backtesting.lib import crossover
        
        current_price = self.data.Close[-1]
        current_vol = self.volatility[-1]
        
        # 獲取市場狀態和倉位
        if self.pipeline:
            try:
                features = self.pipeline.get_features()
                vix = features.get("vix", 20)
                
                if vix > 40:
                    position_size = 0.2
                elif vix > 30:
                    position_size = 0.5
                elif vix < 20:
                    position_size = 1.0
                else:
                    position_size = 0.7
            except:
                position_size = 0.5
        else:
            position_size = 0.5
        
        # 動態止損止盈
        stop_loss = self._get_dynamic_stop_loss(current_vol)
        take_profit = self._get_dynamic_take_profit(current_vol)
        
        # 更新指標
        self.position_size_indicator[-1] = position_size
        self.stop_loss_indicator[-1] = stop_loss
        self.take_profit_indicator[-1] = take_profit
        
        # 檢查止損止盈
        if self.position:
            if self._check_stop_loss(current_price):
                self.position.close()
                self.entry_price = 0.0
            elif self._check_take_profit(current_price):
                self.position.close()
                self.entry_price = 0.0
        
        # 開倉信號
        if not self.position:
            if crossover(self.sma1, self.sma2):
                self.buy(size=position_size)
                self.entry_price = current_price
            elif crossover(self.sma2, self.sma1):
                self.sell(size=position_size)
                self.entry_price = current_price


# ============================================
# 主程序
# ============================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("📊 Policy Gate 動態倉位控制回測示例")
    print("=" * 70)
    
    # 1. 準備數據
    print("\n📊 準備測試數據...")
    from backtesting.test import GOOG
    data = GOOG
    
    print(f"數據範圍：{data.index[0]} 至 {data.index[-1]}")
    
    # 2. 創建平台
    platform = BacktestPlatform(
        initial_cash=10000,
        commission=0.002
    )
    
    # 3. 運行固定倉位策略 (基準)
    print("\n" + "=" * 70)
    print("策略 1: 固定倉位策略 (基準)")
    print("=" * 70)
    
    stats_fixed = platform.run(
        strategy_class=FixedPositionStrategy,
        data=data,
        strategy_params={
            "n1": 10,
            "n2": 20,
            "position_size": 1.0
        },
        verbose=True
    )
    
    # 4. 運行 Policy Gate 動態倉位策略
    print("\n" + "=" * 70)
    print("策略 2: Policy Gate 動態倉位策略")
    print("=" * 70)
    
    stats_dynamic = platform.run(
        strategy_class=PolicyGateDynamicStrategy,
        data=data,
        strategy_params={
            "n1": 10,
            "n2": 20,
            "bull_position": 1.0,
            "sideways_position": 0.7,
            "bear_position": 0.5,
            "crisis_position": 0.2
        },
        verbose=True
    )
    
    # 5. 運行 Policy Gate + 止損止盈策略
    print("\n" + "=" * 70)
    print("策略 3: Policy Gate + 止損止盈策略")
    print("=" * 70)
    
    stats_sl_tp = platform.run(
        strategy_class=PolicyGateWithStopLoss,
        data=data,
        strategy_params={
            "n1": 10,
            "n2": 20,
            "base_stop_loss": 0.05,
            "base_take_profit": 0.10
        },
        verbose=True
    )
    
    # 6. 對比結果
    print("\n" + "=" * 70)
    print("📊 策略對比")
    print("=" * 70)
    
    comparison = pd.DataFrame({
        "固定倉位": stats_fixed.to_dict(),
        "動態倉位": stats_dynamic.to_dict(),
        "動態 + 止損止盈": stats_sl_tp.to_dict()
    })
    
    # 關鍵指標對比
    key_metrics = [
        "Return [%]",
        "Sharpe Ratio",
        "Max. Drawdown [%]",
        "Win Rate [%]",
        "# Trades"
    ]
    
    print("\n關鍵指標對比:")
    print(comparison.loc[key_metrics].to_string())
    
    # 7. 保存結果
    print("\n💾 保存結果...")
    stats_fixed.to_csv("stats_fixed_position.csv")
    stats_dynamic.to_csv("stats_dynamic_position.csv")
    stats_sl_tp.to_csv("stats_policy_gate_sl_tp.csv")
    
    comparison.to_csv("strategy_comparison.csv")
    
    print("  ✅ 所有結果已保存")
    
    print("\n✅ Policy Gate 動態倉位控制回測示例完成!")
    print("\n📊 分析建議:")
    print("  - 對比動態倉位是否降低最大回撤")
    print("  - 檢查止損止盈是否提高勝率")
    print("  - 評估風險調整後收益 (Sharpe Ratio)")
