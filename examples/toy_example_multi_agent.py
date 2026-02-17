"""
多 Agent 系統 Toy Example - 實際運行演示

場景：比較三種不同市場環境下的 Agent 決策
1. 牛市 (2021 年)
2. 熊市 (2022 年)
3. 危機 (2020 年 3 月)
"""

import sys
from pathlib import Path

# 添加項目根目錄到 Python 路徑
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from agents.multi_agent_system import (
    MultiAgentCoordinator,
    MarketData,
    MarketRegime
)


def print_separator(title: str):
    """打印分隔線"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def analyze_scenario(name: str, market_data: MarketData, coordinator: MultiAgentCoordinator):
    """分析一個市場情境"""
    
    print_separator(f"📊 情境：{name}")
    
    # 打印輸入數據
    print("\n📈 輸入數據:")
    print(f"  VIX: {market_data.vix}")
    print(f"  S&P500 價格：${market_data.spy_price}")
    print(f"  S&P500 200 日均線：${market_data.spy_ma_200}")
    print(f"  通膨率：{market_data.inflation}%")
    print(f"  聯邦基金利率：{market_data.rates}%")
    print(f"  10 年期國債收益率：{market_data.treasury_10y}%")
    
    # 執行分析
    result = coordinator.analyze(market_data)
    
    # 打印市場狀態識別
    print("\n🎯 市場狀態識別:")
    regime = result['market_regime']
    print(f"  狀態：{regime['regime'].upper()}")
    print(f"  信心度：{regime['confidence']:.1%}")
    print(f"  判斷依據:")
    for evidence in regime['evidence']:
        print(f"    - {evidence}")
    
    # 打印風險評估
    print("\n⚠️ 風險評估:")
    risk = result['risk_assessment']
    status = "✅ 批准" if risk['approved'] else "❌ 拒絕"
    print(f"  決策：{status}")
    print(f"  風險預算：{risk['risk_budget']:.1%}")
    print(f"  風險乘數：{risk['risk_multiplier']:.2f}x")
    print(f"  最大持倉：{risk['max_position']:.1%}")
    print(f"  止損建議：{risk['stop_loss']:.1%}")
    print(f"  風險建議:")
    for suggestion in risk['suggestions']:
        print(f"    {suggestion}")
    
    # 打印資產配置
    print("\n💼 資產配置建議:")
    alloc = result['portfolio_allocation']
    print(f"  🟢 股票：{alloc['stocks']:.1%}")
    print(f"  🔵 債券：{alloc['bonds']:.1%}")
    print(f"  🟡 黃金：{alloc['gold']:.1%}")
    print(f"  ⚪ 現金：{alloc['cash']:.1%}")
    print(f"\n  預期指標:")
    print(f"    預期年化回報：{alloc['expected_return']:.1%}")
    print(f"    預期波動率：{alloc['expected_volatility']:.1%}")
    print(f"    夏普比率：{alloc['sharpe_ratio']:.2f}")
    
    # 打印元數據
    print("\n📋 元數據:")
    meta = result['metadata']
    print(f"  VIX: {meta['vix']}")
    print(f"  通膨：{meta['inflation']}%")
    print(f"  利率：{meta['rates']}%")
    
    return result


def main():
    """主函數"""
    
    print("\n" + "🤖 " * 20)
    print("多 Agent 系統 Toy Example - 實際運行")
    print("🤖 " * 20)
    
    # 創建協調器
    coordinator = MultiAgentCoordinator()
    
    # ============================================
    # 情境 1: 牛市 (2021 年環境) - 價格遠高於均線
    # ============================================
    bull_market = MarketData(
        vix=12.0,           # 低波動率
        spy_price=500.0,    # 遠高於均線 (>15%)
        spy_ma_200=400.0,
        inflation=2.0,      # 溫和通膨
        rates=0.5,          # 低利率
        treasury_10y=1.5
    )
    
    result_bull = analyze_scenario("牛市 (2021 年環境)", bull_market, coordinator)
    
    # ============================================
    # 情境 2: 震盪市 (2023 年環境)
    # ============================================
    sideways_market = MarketData(
        vix=18.0,           # 中等波動率
        spy_price=440.0,    # 接近均線
        spy_ma_200=430.0,
        inflation=3.5,      # 中等通膨
        rates=4.0,          # 中性利率
        treasury_10y=4.0
    )
    
    result_sideways = analyze_scenario("震盪市 (2023 年環境)", sideways_market, coordinator)
    
    # ============================================
    # 情境 3: 熊市 (2022 年環境) - 價格遠低於均線
    # ============================================
    bear_market = MarketData(
        vix=32.0,           # 高波動率 (>30)
        spy_price=350.0,    # 遠低於均線 (<-15%)
        spy_ma_200=420.0,
        inflation=6.5,      # 高通膨
        rates=3.5,          # 升息周期
        treasury_10y=3.8
    )
    
    result_bear = analyze_scenario("熊市 (2022 年環境)", bear_market, coordinator)
    
    # ============================================
    # 情境 4: 危機 (2020 年 3 月)
    # ============================================
    crisis_market = MarketData(
        vix=82.0,           # 極高波動率
        spy_price=240.0,    # 遠低於均線
        spy_ma_200=320.0,
        inflation=0.5,      # 通縮壓力
        rates=0.0,          # 零利率
        treasury_10y=0.7
    )
    
    result_crisis = analyze_scenario("危機模式 (2020 年 3 月)", crisis_market, coordinator)
    
    # ============================================
    # 綜合比較
    # ============================================
    print_separator("📊 綜合比較")
    
    print("\n📈 資產配置對比:")
    print(f"{'情境':<15} {'股票':>8} {'債券':>8} {'黃金':>8} {'現金':>8} {'預期回報':>10}")
    print("-" * 65)
    print(f"{'牛市':<15} {result_bull['portfolio_allocation']['stocks']:>7.1%} {result_bull['portfolio_allocation']['bonds']:>7.1%} {result_bull['portfolio_allocation']['gold']:>7.1%} {result_bull['portfolio_allocation']['cash']:>7.1%} {result_bull['portfolio_allocation']['expected_return']:>9.1%}")
    print(f"{'震盪市':<15} {result_sideways['portfolio_allocation']['stocks']:>7.1%} {result_sideways['portfolio_allocation']['bonds']:>7.1%} {result_sideways['portfolio_allocation']['gold']:>7.1%} {result_sideways['portfolio_allocation']['cash']:>7.1%} {result_sideways['portfolio_allocation']['expected_return']:>9.1%}")
    print(f"{'熊市':<15} {result_bear['portfolio_allocation']['stocks']:>7.1%} {result_bear['portfolio_allocation']['bonds']:>7.1%} {result_bear['portfolio_allocation']['gold']:>7.1%} {result_bear['portfolio_allocation']['cash']:>7.1%} {result_bear['portfolio_allocation']['expected_return']:>9.1%}")
    print(f"{'危機':<15} {result_crisis['portfolio_allocation']['stocks']:>7.1%} {result_crisis['portfolio_allocation']['bonds']:>7.1%} {result_crisis['portfolio_allocation']['gold']:>7.1%} {result_crisis['portfolio_allocation']['cash']:>7.1%} {result_crisis['portfolio_allocation']['expected_return']:>9.1%}")
    
    print("\n⚠️ 風險乘數對比:")
    print(f"  牛市：{result_bull['risk_assessment']['risk_multiplier']:.2f}x")
    print(f"  震盪市：{result_sideways['risk_assessment']['risk_multiplier']:.2f}x")
    print(f"  熊市：{result_bear['risk_assessment']['risk_multiplier']:.2f}x")
    print(f"  危機：{result_crisis['risk_assessment']['risk_multiplier']:.2f}x")
    
    print("\n🎯 市場狀態識別:")
    print(f"  牛市：{result_bull['market_regime']['regime']} (信心：{result_bull['market_regime']['confidence']:.1%})")
    print(f"  震盪市：{result_sideways['market_regime']['regime']} (信心：{result_sideways['market_regime']['confidence']:.1%})")
    print(f"  熊市：{result_bear['market_regime']['regime']} (信心：{result_bear['market_regime']['confidence']:.1%})")
    print(f"  危機：{result_crisis['market_regime']['regime']} (信心：{result_crisis['market_regime']['confidence']:.1%})")
    
    print("\n" + "✅ " * 20)
    print("多 Agent 系統 Toy Example 運行完成!")
    print("✅ " * 20 + "\n")


if __name__ == "__main__":
    main()
