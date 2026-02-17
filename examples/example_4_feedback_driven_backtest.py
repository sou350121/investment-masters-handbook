"""
Investment Masters Handbook - 示例 4: 反饋驅動的自適應回測

功能:
1. 使用反饋系統收集策略表現
2. 根據反饋動態調整策略參數
3. 自適應優化交易邏輯
4. 對比固定參數 vs 自適應參數

使用場景:
- 驗證反饋驅動的自適應優化效果
- 評估策略參數的時變特性
- 優化反饋閾值和調整頻率
"""

import pandas as pd
import numpy as np
from backtesting import Strategy
from services.backtest_platform import BacktestPlatform
from services.feedback_system import FeedbackCollector, FeedbackAnalyzer


# ============================================
# 策略 1: 固定參數策略 (基準)
# ============================================
class FixedParameterStrategy(Strategy):
    """
    固定參數策略
    
    邏輯:
    - 使用固定參數 (n1=10, n2=20)
    - 雙均線交叉信號
    """
    n1 = 10
    n2 = 20
    
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
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()


# ============================================
# 策略 2: 反饋驅動自適應策略
# ============================================
class FeedbackDrivenStrategy(Strategy):
    """
    反饋驅動的自適應策略
    
    邏輯:
    1. 收集最近 N 筆交易的反饋 (盈虧)
    2. 根據反饋調整參數:
       - 連續虧損 → 增加參數 (減少交易頻率)
       - 連續盈利 → 保持或減小參數
    3. 動態調整止損止盈
    """
    # 基礎參數
    base_n1 = 10
    base_n2 = 20
    
    # 自適應參數
    adaptive_window = 10  # 反饋窗口大小
    max_adjustment = 0.5  # 最大調整幅度
    
    def init(self):
        """初始化"""
        close = self.data.Close
        self.sma1 = self.I(lambda x: pd.Series(x).rolling(self.base_n1).mean(), close)
        self.sma2 = self.I(lambda x: pd.Series(x).rolling(self.base_n2).mean(), close)
        
        # 動態參數指標
        self.current_n1 = self.I(lambda: pd.Series(self.base_n1, index=self.data.index))
        self.current_n2 = self.I(lambda: pd.Series(self.base_n2, index=self.data.index))
        self.win_streak = self.I(lambda: pd.Series(0, index=self.data.index))
        self.loss_streak = self.I(lambda: pd.Series(0, index=self.data.index))
        
        # 反饋收集器
        self.feedback_collector = FeedbackCollector()
        self.feedback_analyzer = FeedbackAnalyzer(self.feedback_collector)
        
        # 交易記錄
        self.trade_history = []
        self.last_adjustment_index = 0
        self.adjustment_interval = 20  # 每 20 根 K 線調整一次
    
    def _analyze_recent_trades(self) -> tuple:
        """
        分析最近交易表現
        
        Returns:
            (win_rate, avg_profit, consecutive_losses)
        """
        if len(self.trade_history) < 5:
            return 0.5, 0.0, 0
        
        # 取最近 N 筆交易
        recent = self.trade_history[-self.adaptive_window:]
        
        # 計算勝率
        wins = sum(1 for t in recent if t["pnl"] > 0)
        win_rate = wins / len(recent)
        
        # 計算平均盈虧
        avg_profit = np.mean([t["pnl"] for t in recent])
        
        # 計算連續虧損
        consecutive_losses = 0
        for t in reversed(recent):
            if t["pnl"] < 0:
                consecutive_losses += 1
            else:
                break
        
        return win_rate, avg_profit, consecutive_losses
    
    def _adjust_parameters(self, win_rate: float, consecutive_losses: int):
        """
        根據反饋調整參數
        
        Args:
            win_rate: 勝率
            consecutive_losses: 連續虧損次數
        """
        # 計算調整係數
        if win_rate < 0.4 or consecutive_losses >= 3:
            # 表現差 → 增加參數 (減少交易)
            adjustment_factor = 1.0 + min(consecutive_losses * 0.1, self.max_adjustment)
        elif win_rate > 0.6:
            # 表現好 → 保持或略微減小參數
            adjustment_factor = 1.0 - 0.05
        else:
            # 表現一般 → 保持不變
            adjustment_factor = 1.0
        
        # 應用調整
        new_n1 = int(self.base_n1 * adjustment_factor)
        new_n2 = int(self.base_n2 * adjustment_factor)
        
        # 確保合理性
        new_n1 = max(5, min(new_n1, 50))
        new_n2 = max(10, min(new_n2, 100))
        new_n2 = max(new_n2, new_n1 + 5)  # n2 必須大於 n1
        
        return new_n1, new_n2
    
    def _record_trade(self, trade_type: str, entry_price: float, exit_price: float):
        """記錄交易"""
        pnl = (exit_price - entry_price) / entry_price
        if trade_type == "sell":
            pnl = -pnl
        
        self.trade_history.append({
            "type": trade_type,
            "entry": entry_price,
            "exit": exit_price,
            "pnl": pnl
        })
        
        # 提交反饋
        feedback_type = "thumbs_up" if pnl > 0 else "thumbs_down"
        rating = int(min(5, max(1, 3 + pnl * 10)))  # 根據盈虧轉換為 1-5 星
        
        self.feedback_collector.submit_feedback(
            session_id=f"trade_{len(self.trade_history)}",
            query=f"{trade_type} trade at {entry_price:.2f}",
            response_id=f"exit_{exit_price:.2f}",
            feedback_type=feedback_type,
            rating=rating,
            comment=f"PnL: {pnl:.2%}"
        )
    
    def next(self):
        """交易邏輯"""
        from backtesting.lib import crossover
        
        current_index = len(self.data) - 1
        
        # 定期調整參數
        if current_index - self.last_adjustment_index >= self.adjustment_interval:
            win_rate, avg_profit, consecutive_losses = self._analyze_recent_trades()
            new_n1, new_n2 = self._adjust_parameters(win_rate, consecutive_losses)
            
            # 更新指標
            self.current_n1[-1] = new_n1
            self.current_n2[-1] = new_n2
            self.win_streak[-1] = max(0, consecutive_losses if avg_profit < 0 else 0)
            self.loss_streak[-1] = consecutive_losses
            
            # 重新計算均線
            close = self.data.Close
            self.sma1 = self.I(lambda x: pd.Series(x).rolling(new_n1).mean(), close)
            self.sma2 = self.I(lambda x: pd.Series(x).rolling(new_n2).mean(), close)
            
            self.last_adjustment_index = current_index
        
        # 交易執行
        if crossover(self.sma1, self.sma2):
            if self.position and self.position.is_short:
                # 平空倉
                self._record_trade("sell", self.position.entry_price, self.data.Close[-1])
                self.position.close()
            
            # 開多倉
            self.buy()
            self.entry_price = self.data.Close[-1]
        
        elif crossover(self.sma2, self.sma1):
            if self.position and self.position.is_long:
                # 平多倉
                self._record_trade("buy", self.position.entry_price, self.data.Close[-1])
                self.position.close()
            
            # 開空倉
            self.sell()
            self.entry_price = self.data.Close[-1]


# ============================================
# 策略 3: 反饋 + Policy Gate 混合策略
# ============================================
class FeedbackPolicyGateStrategy(Strategy):
    """
    反饋驅動 + Policy Gate 混合策略
    
    邏輯:
    1. Policy Gate 評估市場狀態
    2. 反饋系統調整參數
    3. 綜合兩者決策
    """
    base_n1 = 10
    base_n2 = 20
    
    def init(self):
        """初始化"""
        close = self.data.Close
        self.sma1 = self.I(lambda x: pd.Series(x).rolling(self.base_n1).mean(), close)
        self.sma2 = self.I(lambda x: pd.Series(x).rolling(self.base_n2).mean(), close)
        
        # 市場狀態指標
        self.market_regime = self.I(lambda: pd.Series("neutral", index=self.data.index))
        self.feedback_score = self.I(lambda: pd.Series(0.5, index=self.data.index))
        
        # 初始化組件
        self.feedback_collector = FeedbackCollector()
        
        try:
            from services.realtime_data import get_pipeline
            self.pipeline = get_pipeline()
        except:
            self.pipeline = None
        
        self.trade_history = []
        self.last_adjustment_index = 0
        self.adjustment_interval = 20
    
    def _get_market_regime(self) -> str:
        """獲取市場狀態"""
        if self.pipeline is None:
            return "neutral"
        
        try:
            features = self.pipeline.get_features()
            vix = features.get("vix", 20)
            
            if vix > 40:
                return "crisis"
            elif vix > 30:
                return "bear"
            elif vix < 20:
                return "bull"
            else:
                return "sideways"
        except:
            return "neutral"
    
    def _analyze_feedback(self) -> float:
        """分析反饋得分"""
        if len(self.trade_history) < 3:
            return 0.5
        
        recent = self.trade_history[-10:]
        wins = sum(1 for t in recent if t["pnl"] > 0)
        return wins / len(recent)
    
    def next(self):
        """交易邏輯"""
        from backtesting.lib import crossover
        
        current_index = len(self.data) - 1
        
        # 獲取市場狀態
        regime = self._get_market_regime()
        self.market_regime[-1] = regime
        
        # 分析反饋
        feedback_score = self._analyze_feedback()
        self.feedback_score[-1] = feedback_score
        
        # 根據市場狀態和反饋調整倉位
        if regime in ["crisis", "bear"]:
            position_size = 0.3  # 低倉位
        elif regime == "sideways":
            position_size = 0.5 + (feedback_score - 0.5) * 0.4  # 中等倉位
        else:  # bull
            position_size = 0.8 + feedback_score * 0.2  # 高倉位
        
        # 定期調整參數
        if current_index - self.last_adjustment_index >= self.adjustment_interval:
            if feedback_score < 0.4:
                # 表現差 → 增加參數
                new_n1 = min(20, self.base_n1 + 2)
                new_n2 = min(40, self.base_n2 + 2)
            elif feedback_score > 0.6:
                # 表現好 → 減小參數
                new_n1 = max(5, self.base_n1 - 1)
                new_n2 = max(10, self.base_n2 - 1)
            else:
                new_n1, new_n2 = self.base_n1, self.base_n2
            
            # 重新計算均線
            close = self.data.Close
            self.sma1 = self.I(lambda x: pd.Series(x).rolling(new_n1).mean(), close)
            self.sma2 = self.I(lambda x: pd.Series(x).rolling(new_n2).mean(), close)
            
            self.last_adjustment_index = current_index
        
        # 交易執行
        if crossover(self.sma1, self.sma2):
            if self.position:
                self.position.close()
            self.buy(size=position_size)
        
        elif crossover(self.sma2, self.sma1):
            if self.position:
                self.position.close()
            self.sell(size=position_size)


# ============================================
# 主程序
# ============================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🔄 反饋驅動的自適應回測示例")
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
    
    # 3. 運行固定參數策略 (基準)
    print("\n" + "=" * 70)
    print("策略 1: 固定參數策略 (基準)")
    print("=" * 70)
    
    stats_fixed = platform.run(
        strategy_class=FixedParameterStrategy,
        data=data,
        strategy_params={"n1": 10, "n2": 20},
        verbose=True
    )
    
    # 4. 運行反饋驅動策略
    print("\n" + "=" * 70)
    print("策略 2: 反饋驅動自適應策略")
    print("=" * 70)
    
    stats_feedback = platform.run(
        strategy_class=FeedbackDrivenStrategy,
        data=data,
        strategy_params={
            "base_n1": 10,
            "base_n2": 20,
            "adaptive_window": 10,
            "max_adjustment": 0.5
        },
        verbose=True
    )
    
    # 5. 運行反饋 + Policy Gate 混合策略
    print("\n" + "=" * 70)
    print("策略 3: 反饋 + Policy Gate 混合策略")
    print("=" * 70)
    
    stats_hybrid = platform.run(
        strategy_class=FeedbackPolicyGateStrategy,
        data=data,
        strategy_params={
            "base_n1": 10,
            "base_n2": 20
        },
        verbose=True
    )
    
    # 6. 對比結果
    print("\n" + "=" * 70)
    print("📊 策略對比")
    print("=" * 70)
    
    comparison = pd.DataFrame({
        "固定參數": stats_fixed.to_dict(),
        "反饋驅動": stats_feedback.to_dict(),
        "反饋+PolicyGate": stats_hybrid.to_dict()
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
    stats_fixed.to_csv("stats_fixed_parameter.csv")
    stats_feedback.to_csv("stats_feedback_driven.csv")
    stats_hybrid.to_csv("stats_feedback_policygate.csv")
    
    comparison.to_csv("feedback_strategy_comparison.csv")
    
    print("  ✅ 所有結果已保存")
    
    print("\n✅ 反饋驅動的自適應回測示例完成!")
    print("\n📊 分析建議:")
    print("  - 對比自適應策略是否優於固定參數")
    print("  - 檢查反饋機制是否降低最大回撤")
    print("  - 評估混合策略的風險調整後收益")
