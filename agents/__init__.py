"""
Investment Masters Handbook - Agents Package

精簡多 Agent 系統
"""

from .multi_agent_system import (
    # 數據結構
    MarketRegime,
    MarketData,
    RegimeResult,
    RiskAssessment,
    PortfolioAllocation,
    
    # Agent 類
    RegimeAnalystAgent,
    RiskManagerAgent,
    PortfolioOptimizerAgent,
    MultiAgentCoordinator,
)

__all__ = [
    # 數據結構
    "MarketRegime",
    "MarketData",
    "RegimeResult",
    "RiskAssessment",
    "PortfolioAllocation",
    
    # Agent 類
    "RegimeAnalystAgent",
    "RiskManagerAgent",
    "PortfolioOptimizerAgent",
    "MultiAgentCoordinator",
]
