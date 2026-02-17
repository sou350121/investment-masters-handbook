"""
Investment Masters Handbook - 示例 3: 多 Agent 協作回測

功能:
1. 使用多 Agent 系統進行市場分析
2. RegimeAnalyst 識別市場狀態
3. RiskManager 評估風險
4. PortfolioOptimizer 優化資產配置
5. 基於 Agent 協作信號執行交易

使用場景:
- 驗證多 Agent 協作的實戰效果
- 對比單一 Agent vs 多 Agent 決策
- 優化 Agent 權重配置
"""

import pandas as pd
import numpy as np
from backtesting import Strategy
from services.backtest_platform import BacktestPlatform
from agents.multi_agent_system import (
    RegimeAnalystAgent,
    RiskManagerAgent,
    PortfolioOptimizerAgent,
    MultiAgentCoordinator,
    MarketData
)


# ============================================
# 策略 1: 單一 Agent 策略 (RegimeAnalyst)
# ============================================
class SingleAgentStrategy(Strategy):
    """
    單一 Agent 策略 (僅使用 RegimeAnalyst)
    
    邏輯:
    1. RegimeAnalyst 識別市場狀態
    2. 根據市場狀態執行交易
    """
    n1 = 10
    n2 = 20
    
    def init(self):
        """初始化"""
        close = self.data.Close
        self.sma1 = self.I(lambda x: pd.Series(x).rolling(self.n1).mean(), close)
        self.sma2 = self.I(lambda x: pd.Series(x).rolling(self.n2).mean(), close)
        
        # 市場狀態指標
        self.regime_signal = self.I(lambda: pd.Series("unknown", index=self.data.index))
        self.regime_confidence = self.I(lambda: pd.Series(0.0, index=self.data.index))
        
        # 初始化 Agent
        self.regime_analyst = RegimeAnalystAgent()
    
    def next(self):
        """交易邏輯"""
        from backtesting.lib import crossover
        
        # 準備市場數據
        market_data = MarketData(
            spy_price=self.data.Close[-1],
            spy_ma_200=self.data.Close.rolling(200).mean().iloc[-1] if len(self.data) >= 200 else self.data.Close[-1],
            vix=self.data.Close[-1] / self.data.Close.mean() * 20,  # 簡化 VIX
            inflation_rate=3.0,  # 默認值
            interest_rate=5.0,  # 默認值
            yield_curve_spread=0.5  # 默認值
        )
        
        # Agent 分析
        regime_result = self.regime_analyst.analyze(market_data)
        
        # 更新指標
        self.regime_signal[-1] = regime_result.regime.value
        self.regime_confidence[-1] = regime_result.confidence
        
        # 根據市場狀態交易
        regime = regime_result.regime.value
        
        if crossover(self.sma1, self.sma2):
            if regime in ["bull", "recovery"]:
                self.buy(size=1.0)
            elif regime == "sideways":
                self.buy(size=0.5)
            # 熊市和危機不買入
        elif crossover(self.sma2, self.sma1):
            self.position.close()


# ============================================
# 策略 2: 雙 Agent 協作 (Regime + Risk)
# ============================================
class DualAgentStrategy(Strategy):
    """
    雙 Agent 協作策略 (RegimeAnalyst + RiskManager)
    
    邏輯:
    1. RegimeAnalyst 識別市場狀態
    2. RiskManager 評估風險並給出倉位建議
    3. 綜合兩個 Agent 的意見執行交易
    """
    n1 = 10
    n2 = 20
    
    def init(self):
        """初始化"""
        close = self.data.Close
        self.sma1 = self.I(lambda x: pd.Series(x).rolling(self.n1).mean(), close)
        self.sma2 = self.I(lambda x: pd.Series(x).rolling(self.n2).mean(), close)
        
        # 指標
        self.regime_signal = self.I(lambda: pd.Series("unknown", index=self.data.index))
        self.risk_level = self.I(lambda: pd.Series("medium", index=self.data.index))
        self.position_size_signal = self.I(lambda: pd.Series(0.0, index=self.data.index))
        
        # 初始化 Agent
        self.regime_analyst = RegimeAnalystAgent()
        self.risk_manager = RiskManagerAgent()
    
    def next(self):
        """交易邏輯"""
        from backtesting.lib import crossover
        
        # 準備市場數據
        market_data = MarketData(
            spy_price=self.data.Close[-1],
            spy_ma_200=self.data.Close.rolling(200).mean().iloc[-1] if len(self.data) >= 200 else self.data.Close[-1],
            vix=self.data.Close[-1] / self.data.Close.mean() * 20,
            inflation_rate=3.0,
            interest_rate=5.0,
            yield_curve_spread=0.5
        )
        
        # Agent 1: 市場狀態分析
        regime_result = self.regime_analyst.analyze(market_data)
        
        # Agent 2: 風險評估
        risk_assessment = self.risk_manager.assess(regime_result, market_data)
        
        # 更新指標
        self.regime_signal[-1] = regime_result.regime.value
        self.risk_level[-1] = risk_assessment.risk_level
        self.position_size_signal[-1] = risk_assessment.suggested_position
        
        # 綜合決策
        position_size = risk_assessment.suggested_position
        
        if crossover(self.sma1, self.sma2):
            # 只在低風險或中風險時買入
            if risk_assessment.risk_level in ["low", "medium"]:
                self.buy(size=position_size)
        elif crossover(self.sma2, self.sma1):
            self.position.close()


# ============================================
# 策略 3: 三 Agent 協作 (完整系統)
# ============================================
class MultiAgentCoordinatorStrategy(Strategy):
    """
    完整多 Agent 協作策略
    
    邏輯:
    1. RegimeAnalyst 識別市場狀態
    2. RiskManager 評估風險
    3. PortfolioOptimizer 優化配置
    4. Coordinator 綜合決策
    """
    n1 = 10
    n2 = 20
    
    # Coordinator 權重 (可優化)
    regime_weight = 0.4
    risk_weight = 0.4
    optimizer_weight = 0.2
    
    def init(self):
        """初始化"""
        close = self.data.Close
        self.sma1 = self.I(lambda x: pd.Series(x).rolling(self.n1).mean(), close)
        self.sma2 = self.I(lambda x: pd.Series(x).rolling(self.n2).mean(), close)
        
        # 指標
        self.regime_signal = self.I(lambda: pd.Series("unknown", index=self.data.index))
        self.risk_level = self.I(lambda: pd.Series("medium", index=self.data.index))
        self.optimal_allocation = self.I(lambda: pd.Series(0.0, index=self.data.index))
        self.final_decision = self.I(lambda: pd.Series(0.0, index=self.data.index))
        
        # 初始化 Coordinator
        self.coordinator = MultiAgentCoordinator()
    
    def next(self):
        """交易邏輯"""
        from backtesting.lib import crossover
        
        # 準備市場數據
        market_data = MarketData(
            spy_price=self.data.Close[-1],
            spy_ma_200=self.data.Close.rolling(200).mean().iloc[-1] if len(self.data) >= 200 else self.data.Close[-1],
            vix=self.data.Close[-1] / self.data.Close.mean() * 20,
            inflation_rate=3.0,
            interest_rate=5.0,
            yield_curve_spread=0.5
        )
        
        # Coordinator 綜合分析
        decision = self.coordinator.make_decision(market_data)
        
        # 更新指標
        self.regime_signal[-1] = decision.regime_result.regime.value
        self.risk_level[-1] = decision.risk_assessment.risk_level
        self.optimal_allocation[-1] = decision.portfolio_allocation.get("equity", 0.0)
        self.final_decision[-1] = decision.final_decision
        
        # 執行交易
        position_size = decision.portfolio_allocation.get("equity", 0.5)
        
        if crossover(self.sma1, self.sma2):
            if decision.final_decision > 0.3:  # 積極信號
                self.buy(size=position_size)
        elif crossover(self.sma2, self.sma1):
            self.position.close()


# ============================================
# 策略 4: 動態 Agent 權重策略
# ============================================
class DynamicAgentWeightStrategy(Strategy):
    """
    動態 Agent 權重策略
    
    邏輯:
    1. 根據市場波動率動態調整 Agent 權重
    2. 高波動時更重視 RiskManager
    3. 低波動時更重視 RegimeAnalyst
    """
    n1 = 10
    n2 = 20
    
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
        
        # 動態權重指標
        self.regime_weight = self.I(lambda: pd.Series(0.0, index=self.data.index))
        self.risk_weight = self.I(lambda: pd.Series(0.0, index=self.data.index))
        
        # 初始化 Agent
        self.coordinator = MultiAgentCoordinator()
    
    def next(self):
        """交易邏輯"""
        from backtesting.lib import crossover
        
        current_vol = self.volatility[-1]
        
        # 動態調整權重
        # 高波動時：RiskManager 權重增加
        # 低波動時：RegimeAnalyst 權重增加
        if current_vol > 0.03:  # 高波動
            regime_w = 0.2
            risk_w = 0.6
        elif current_vol > 0.015:  # 中波動
            regime_w = 0.4
            risk_w = 0.4
        else:  # 低波動
            regime_w = 0.6
            risk_w = 0.2
        
        optimizer_w = 1.0 - regime_w - risk_w
        
        # 更新權重
        self.coordinator.regime_weight = regime_w
        self.coordinator.risk_weight = risk_w
        self.coordinator.optimizer_weight = optimizer_w
        
        self.regime_weight[-1] = regime_w
        self.risk_weight[-1] = risk_w
        
        # 準備市場數據
        market_data = MarketData(
            spy_price=self.data.Close[-1],
            spy_ma_200=self.data.Close.rolling(200).mean().iloc[-1] if len(self.data) >= 200 else self.data.Close[-1],
            vix=self.data.Close[-1] / self.data.Close.mean() * 20,
            inflation_rate=3.0,
            interest_rate=5.0,
            yield_curve_spread=0.5
        )
        
        # Coordinator 決策
        decision = self.coordinator.make_decision(market_data)
        
        # 執行交易
        position_size = decision.portfolio_allocation.get("equity", 0.5)
        
        if crossover(self.sma1, self.sma2):
            if decision.final_decision > 0.3:
                self.buy(size=position_size)
        elif crossover(self.sma2, self.sma1):
            self.position.close()


# ============================================
# 主程序
# ============================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🤖 多 Agent 協作回測示例")
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
    
    # 3. 運行單一 Agent 策略
    print("\n" + "=" * 70)
    print("策略 1: 單一 Agent (RegimeAnalyst)")
    print("=" * 70)
    
    try:
        stats_single = platform.run(
            strategy_class=SingleAgentStrategy,
            data=data,
            strategy_params={"n1": 10, "n2": 20},
            verbose=True
        )
    except Exception as e:
        print(f"⚠️ 單一 Agent 策略失敗：{e}")
        stats_single = None
    
    # 4. 運行雙 Agent 策略
    print("\n" + "=" * 70)
    print("策略 2: 雙 Agent 協作 (Regime + Risk)")
    print("=" * 70)
    
    try:
        stats_dual = platform.run(
            strategy_class=DualAgentStrategy,
            data=data,
            strategy_params={"n1": 10, "n2": 20},
            verbose=True
        )
    except Exception as e:
        print(f"⚠️ 雙 Agent 策略失敗：{e}")
        stats_dual = None
    
    # 5. 運行完整多 Agent 策略
    print("\n" + "=" * 70)
    print("策略 3: 完整多 Agent 協作")
    print("=" * 70)
    
    try:
        stats_multi = platform.run(
            strategy_class=MultiAgentCoordinatorStrategy,
            data=data,
            strategy_params={
                "n1": 10,
                "n2": 20,
                "regime_weight": 0.4,
                "risk_weight": 0.4,
                "optimizer_weight": 0.2
            },
            verbose=True
        )
    except Exception as e:
        print(f"⚠️ 多 Agent 策略失敗：{e}")
        stats_multi = None
    
    # 6. 運行動態權重策略
    print("\n" + "=" * 70)
    print("策略 4: 動態 Agent 權重")
    print("=" * 70)
    
    try:
        stats_dynamic = platform.run(
            strategy_class=DynamicAgentWeightStrategy,
            data=data,
            strategy_params={"n1": 10, "n2": 20},
            verbose=True
        )
    except Exception as e:
        print(f"⚠️ 動態權重策略失敗：{e}")
        stats_dynamic = None
    
    # 7. 對比結果
    print("\n" + "=" * 70)
    print("📊 策略對比")
    print("=" * 70)
    
    # 收集有效結果
    valid_stats = {}
    if stats_single is not None:
        valid_stats["單一 Agent"] = stats_single.to_dict()
    if stats_dual is not None:
        valid_stats["雙 Agent"] = stats_dual.to_dict()
    if stats_multi is not None:
        valid_stats["多 Agent"] = stats_multi.to_dict()
    if stats_dynamic is not None:
        valid_stats["動態權重"] = stats_dynamic.to_dict()
    
    if valid_stats:
        comparison = pd.DataFrame(valid_stats)
        
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
        
        # 8. 保存結果
        print("\n💾 保存結果...")
        
        if stats_single is not None:
            stats_single.to_csv("stats_single_agent.csv")
        if stats_dual is not None:
            stats_dual.to_csv("stats_dual_agent.csv")
        if stats_multi is not None:
            stats_multi.to_csv("stats_multi_agent.csv")
        if stats_dynamic is not None:
            stats_dynamic.to_csv("stats_dynamic_weight.csv")
        
        comparison.to_csv("agent_strategy_comparison.csv")
        
        print("  ✅ 所有結果已保存")
    else:
        print("  ⚠️ 沒有有效的回測結果")
    
    print("\n✅ 多 Agent 協作回測示例完成!")
    print("\n📊 分析建議:")
    print("  - 對比多 Agent 是否優於單一 Agent")
    print("  - 檢查動態權重是否提高風險調整後收益")
    print("  - 評估 Agent 協作的邊際貢獻")
