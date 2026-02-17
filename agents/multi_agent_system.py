"""
Investment Masters Handbook - 精簡多 Agent 系統

設計理念:
1. 避免過度複雜：不使用重型框架 (AutoGen/CrewAI)
2. 職責清晰：每個 Agent 只負責一個專業領域
3. 輕量級：基於簡單類和方法，無需複雜配置
4. 可組合：Agent 之間通過標準接口協作

核心 Agent (3 個):
1. RegimeAnalyst: 市場狀態識別
2. RiskManager: 風險管理與校驗
3. PortfolioOptimizer: 資產配置優化
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass
from enum import Enum


# ============================================
# 數據結構定義
# ============================================
class MarketRegime(Enum):
    """市場狀態"""
    BULL = "bull"  # 牛市
    BEAR = "bear"  # 熊市
    SIDEWAYS = "sideways"  # 震盪
    CRISIS = "crisis"  # 危機


@dataclass
class MarketData:
    """市場數據"""
    vix: float  # VIX 波動率
    spy_price: float  # S&P500 價格
    spy_ma_200: float  # 200 日均線
    inflation: float  # 通膨率
    rates: float  # 利率
    treasury_10y: float  # 10 年期國債收益率


@dataclass
class RegimeResult:
    """市場狀態識別結果"""
    regime: MarketRegime
    confidence: float
    evidence: List[str]


@dataclass
class RiskAssessment:
    """風險評估結果"""
    approved: bool
    risk_budget: float  # 風險預算 (0-1)
    risk_multiplier: float  # 風險乘數
    max_position: float  # 最大持倉比例
    stop_loss: float  # 建議止損
    suggestions: List[str]


@dataclass
class PortfolioAllocation:
    """資產配置結果"""
    stocks: float  # 股票
    bonds: float  # 債券
    gold: float  # 黃金
    cash: float  # 現金
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float


# ============================================
# Agent 1: 市場狀態識別
# ============================================
class RegimeAnalystAgent:
    """
    市場狀態識別 Agent
    
    使用簡化版 HMM 或基於規則的方法識別市場狀態
    """
    
    def __init__(self):
        # HMM 模型 (可選，進階功能)
        self.hmm_model = None
        self._trained = False
    
    def identify_regime(self, market_data: MarketData) -> RegimeResult:
        """
        識別當前市場狀態
        
        Args:
            market_data: 市場數據
        
        Returns:
            市場狀態識別結果
        """
        # 方法 1: 基於規則 (立即可用)
        regime, confidence, evidence = self._rule_based_regime(market_data)
        
        # 方法 2: HMM (需要訓練數據，可選)
        # if self._trained:
        #     regime, confidence = self._hmm_predict(market_data)
        
        return RegimeResult(
            regime=regime,
            confidence=confidence,
            evidence=evidence
        )
    
    def _rule_based_regime(self, data: MarketData) -> Tuple[MarketRegime, float, List[str]]:
        """
        基於規則的市場狀態判斷 (簡化但實用)
        
        規則:
        - VIX > 40: 危機模式
        - VIX > 30 或 價格 < 200MA * 0.8: 熊市
        - 價格 > 200MA * 1.2: 牛市
        - 其他：震盪
        """
        evidence = []
        
        # 危機模式
        if data.vix > 40:
            evidence.append(f"VIX 處於極高水平 ({data.vix:.1f})")
            evidence.append("市場處於恐慌狀態")
            return MarketRegime.CRISIS, 0.9, evidence
        
        # 熊市
        if data.vix > 30 or (data.spy_price < data.spy_ma_200 * 0.85):
            if data.vix > 30:
                evidence.append(f"VIX 處於高水平 ({data.vix:.1f})")
            if data.spy_price < data.spy_ma_200 * 0.85:
                evidence.append(f"價格低於 200 日均線 {((data.spy_price/data.spy_ma_200)-1)*100:.1f}%")
            return MarketRegime.BEAR, 0.75, evidence
        
        # 牛市
        if data.spy_price > data.spy_ma_200 * 1.15:
            evidence.append(f"價格高於 200 日均線 {((data.spy_price/data.spy_ma_200)-1)*100:.1f}%")
            evidence.append("市場處於上升趨勢")
            return MarketRegime.BULL, 0.7, evidence
        
        # 震盪
        evidence.append(f"價格在 200 日均線附近 ({((data.spy_price/data.spy_ma_200)-1)*100:.1f}%)")
        evidence.append("市場無明確趨勢")
        return MarketRegime.SIDEWAYS, 0.6, evidence
    
    def train(self, historical_data: np.ndarray):
        """
        訓練 HMM 模型 (進階功能)
        
        Args:
            historical_data: 歷史數據 (n_samples, n_features)
        """
        try:
            from hmmlearn import hmm
            
            # 特徵：收益率、波動率、相關性
            self.hmm_model = hmm.GaussianHMM(
                n_components=4,
                covariance_type="diag",
                n_iter=100
            )
            
            self.hmm_model.fit(historical_data)
            self._trained = True
            
            print("✅ HMM 模型訓練完成")
            
        except ImportError:
            print("⚠️ 未安裝 hmmlearn，使用基於規則的方法")
        except Exception as e:
            print(f"⚠️ HMM 訓練失敗：{e}")


# ============================================
# Agent 2: 風險管理
# ============================================
class RiskManagerAgent:
    """
    風險管理 Agent
    
    負責:
    - 校驗投資提議是否符合風險預算
    - 計算風險乘數
    - 提供風險建議
    """
    
    def __init__(self):
        # 各市場狀態的風險預算
        self.regime_budgets = {
            MarketRegime.BULL: 1.0,
            MarketRegime.SIDEWAYS: 0.7,
            MarketRegime.BEAR: 0.4,
            MarketRegime.CRISIS: 0.2
        }
        
        # 默認風險參數
        self.base_stop_loss = 0.08  # 8% 止損
        self.base_max_position = 0.20  # 20% 最大持倉
    
    def validate_proposal(self, 
                         proposed_risk: float,
                         regime: MarketRegime,
                         portfolio_state: Optional[Dict[str, float]] = None) -> RiskAssessment:
        """
        校驗投資提議
        
        Args:
            proposed_risk: 提議的風險水平 (0-1)
            regime: 市場狀態
            portfolio_state: 當前持倉狀態
        
        Returns:
            風險評估結果
        """
        # 計算風險預算
        risk_budget = self.regime_budgets.get(regime, 0.5)
        
        # 計算風險乘數
        risk_multiplier = risk_budget / proposed_risk if proposed_risk > 0 else 1.0
        
        # 判斷是否批准
        approved = proposed_risk <= risk_budget
        
        # 計算最大持倉和止損
        max_position = self.base_max_position * risk_multiplier
        stop_loss = self.base_stop_loss * (2 - risk_multiplier)  # 風險越高，止損越緊
        
        # 生成建議
        suggestions = self._generate_suggestions(approved, regime, risk_multiplier)
        
        return RiskAssessment(
            approved=approved,
            risk_budget=risk_budget,
            risk_multiplier=risk_multiplier,
            max_position=max_position,
            stop_loss=stop_loss,
            suggestions=suggestions
        )
    
    def _generate_suggestions(self, 
                             approved: bool,
                             regime: MarketRegime,
                             risk_multiplier: float) -> List[str]:
        """生成風險建議"""
        suggestions = []
        
        if not approved:
            suggestions.append("⚠️ 提議風險超過預算，建議降低倉位")
            suggestions.append(f"建議風險乘數：{risk_multiplier:.2f}")
        
        if regime == MarketRegime.CRISIS:
            suggestions.append("🔴 危機模式：建議持有現金，等待機會")
        elif regime == MarketRegime.BEAR:
            suggestions.append("🔴 熊市：防禦為主，增加債券配置")
        elif regime == MarketRegime.BULL:
            suggestions.append("🟢 牛市：可積極參與，但設置止損")
        else:
            suggestions.append("🟡 震盪：區間操作，避免追高殺低")
        
        return suggestions


# ============================================
# Agent 3: 資產配置優化
# ============================================
class PortfolioOptimizerAgent:
    """
    資產配置優化 Agent
    
    使用均值 - 方差模型或簡化版配置規則
    """
    
    def __init__(self):
        # 資產類別
        self.assets = ["stocks", "bonds", "gold", "cash"]
        
        # 預期回報 (年化，可根據市場狀態調整)
        self.base_returns = {
            "stocks": 0.08,
            "bonds": 0.03,
            "gold": 0.05,
            "cash": 0.02
        }
        
        # 預期波動率
        self.base_volatilities = {
            "stocks": 0.15,
            "bonds": 0.05,
            "gold": 0.10,
            "cash": 0.00
        }
    
    def optimize(self, 
                regime: MarketRegime,
                risk_budget: float) -> PortfolioAllocation:
        """
        優化資產配置
        
        Args:
            regime: 市場狀態
            risk_budget: 風險預算
        
        Returns:
            最優資產配置
        """
        # 方法 1: 基於規則的配置 (簡化版)
        allocation = self._rule_based_allocation(regime, risk_budget)
        
        # 方法 2: 均值 - 方差優化 (進階版，可選)
        # allocation = self._mean_variance_optimization(regime, risk_budget)
        
        return allocation
    
    def _rule_based_allocation(self, 
                               regime: MarketRegime,
                               risk_budget: float) -> PortfolioAllocation:
        """
        基於規則的資產配置 (實用版)
        """
        # 基礎配置比例
        base_allocations = {
            MarketRegime.BULL: {"stocks": 0.70, "bonds": 0.15, "gold": 0.05, "cash": 0.10},
            MarketRegime.SIDEWAYS: {"stocks": 0.50, "bonds": 0.25, "gold": 0.10, "cash": 0.15},
            MarketRegime.BEAR: {"stocks": 0.30, "bonds": 0.40, "gold": 0.15, "cash": 0.15},
            MarketRegime.CRISIS: {"stocks": 0.15, "bonds": 0.30, "gold": 0.20, "cash": 0.35}
        }
        
        # 獲取基礎配置
        base = base_allocations.get(regime, base_allocations[MarketRegime.SIDEWAYS])
        
        # 根據風險預算微調
        adjustment = (risk_budget - 0.5) * 0.4  # -0.2 to +0.2
        
        stocks = max(0.05, min(0.95, base["stocks"] + adjustment))
        bonds = max(0.05, min(0.95, base["bonds"] - adjustment * 0.5))
        gold = max(0.05, min(0.30, base["gold"] - adjustment * 0.3))
        cash = 1.0 - stocks - bonds - gold  # 確保總和為 1
        
        # 計算預期指標
        expected_return = (
            stocks * self.base_returns["stocks"] +
            bonds * self.base_returns["bonds"] +
            gold * self.base_returns["gold"] +
            cash * self.base_returns["cash"]
        )
        
        expected_volatility = stocks * self.base_volatilities["stocks"]  # 簡化
        
        sharpe = (expected_return - self.base_returns["cash"]) / expected_volatility if expected_volatility > 0 else 0
        
        return PortfolioAllocation(
            stocks=stocks,
            bonds=bonds,
            gold=gold,
            cash=cash,
            expected_return=expected_return,
            expected_volatility=expected_volatility,
            sharpe_ratio=sharpe
        )


# ============================================
# Agent 協調器
# ============================================
class MultiAgentCoordinator:
    """
    多 Agent 協調器
    
    協調 3 個 Agent 完成完整決策流程:
    1. 市場狀態識別
    2. 風險評估
    3. 資產配置
    """
    
    def __init__(self):
        self.regime_analyst = RegimeAnalystAgent()
        self.risk_manager = RiskManagerAgent()
        self.portfolio_optimizer = PortfolioOptimizerAgent()
    
    def analyze(self, market_data: MarketData) -> Dict[str, Any]:
        """
        完整分析流程
        
        Args:
            market_data: 市場數據
        
        Returns:
            完整分析結果
        """
        # Step 1: 市場狀態識別
        regime_result = self.regime_analyst.identify_regime(market_data)
        
        # Step 2: 風險評估
        risk_assessment = self.risk_manager.validate_proposal(
            proposed_risk=0.5,  # 假設中等風險
            regime=regime_result.regime
        )
        
        # Step 3: 資產配置
        allocation = self.portfolio_optimizer.optimize(
            regime=regime_result.regime,
            risk_budget=risk_assessment.risk_budget
        )
        
        # 整合結果
        return {
            "market_regime": {
                "regime": regime_result.regime.value,
                "confidence": regime_result.confidence,
                "evidence": regime_result.evidence
            },
            "risk_assessment": {
                "approved": risk_assessment.approved,
                "risk_budget": risk_assessment.risk_budget,
                "risk_multiplier": risk_assessment.risk_multiplier,
                "max_position": risk_assessment.max_position,
                "stop_loss": risk_assessment.stop_loss,
                "suggestions": risk_assessment.suggestions
            },
            "portfolio_allocation": {
                "stocks": allocation.stocks,
                "bonds": allocation.bonds,
                "gold": allocation.gold,
                "cash": allocation.cash,
                "expected_return": allocation.expected_return,
                "expected_volatility": allocation.expected_volatility,
                "sharpe_ratio": allocation.sharpe_ratio
            },
            "metadata": {
                "vix": market_data.vix,
                "inflation": market_data.inflation,
                "rates": market_data.rates
            }
        }


# ============================================
# 使用示例
# ============================================
if __name__ == "__main__":
    # 創建協調器
    coordinator = MultiAgentCoordinator()
    
    # 模擬市場數據
    market_data = MarketData(
        vix=15.2,
        spy_price=450.0,
        spy_ma_200=420.0,
        inflation=3.2,
        rates=4.5,
        treasury_10y=4.2
    )
    
    # 執行分析
    result = coordinator.analyze(market_data)
    
    # 輸出結果
    print("\n📊 市場狀態分析:")
    print(f"  狀態：{result['market_regime']['regime']}")
    print(f"  信心：{result['market_regime']['confidence']:.1%}")
    print(f"  證據：{', '.join(result['market_regime']['evidence'])}")
    
    print("\n⚠️ 風險評估:")
    print(f"  批准：{result['risk_assessment']['approved']}")
    print(f"  風險預算：{result['risk_assessment']['risk_budget']:.1%}")
    print(f"  風險乘數：{result['risk_assessment']['risk_multiplier']:.2f}")
    print(f"  建議：{', '.join(result['risk_assessment']['suggestions'])}")
    
    print("\n💼 資產配置:")
    print(f"  股票：{result['portfolio_allocation']['stocks']:.1%}")
    print(f"  債券：{result['portfolio_allocation']['bonds']:.1%}")
    print(f"  黃金：{result['portfolio_allocation']['gold']:.1%}")
    print(f"  現金：{result['portfolio_allocation']['cash']:.1%}")
    print(f"  預期回報：{result['portfolio_allocation']['expected_return']:.1%}")
    print(f"  夏普比率：{result['portfolio_allocation']['sharpe_ratio']:.2f}")
