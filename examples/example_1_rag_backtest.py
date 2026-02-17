"""
Investment Masters Handbook - 示例 1: RAG 增強型回測

功能:
1. 從 RAG 規則庫中提取投資規則
2. 將規則轉換為交易信號
3. 回測規則驅動的投資策略
4. 對比不同投資人的規則效果

使用場景:
- 驗證 RAG 規則庫的實戰效果
- 比較不同投資人的規則質量
- 優化規則參數
"""

import pandas as pd
import numpy as np
from backtesting import Strategy
from services.backtest_platform import BacktestPlatform
from services.rag_service import query_vectorstore, load_vectorstore


# ============================================
# 策略 1: RAG 規則驅動策略
# ============================================
class RAGRuleStrategy(Strategy):
    """
    基於 RAG 規則庫的交易策略
    
    邏輯:
    1. 從向量庫中查詢與當前市場狀態匹配的規則
    2. 根據規則生成交易信號
    3. 執行交易
    """
    # 可優化參數
    top_k = 3  # 查詢前 K 個規則
    min_similarity = 0.6  # 最小相似度閾值
    signal_threshold = 0.7  # 信號強度閾值
    
    def init(self):
        """初始化"""
        # 加載向量庫
        try:
            self.vectorstore = load_vectorstore()
            print(f"✅ 向量庫加載成功")
        except Exception as e:
            print(f"⚠️ 向量庫加載失敗：{e}")
            self.vectorstore = None
        
        # 初始化信號指標
        self.signal_strength = self.I(lambda: pd.Series(0.0, index=self.data.index))
        self.rule_count = self.I(lambda: pd.Series(0, index=self.data.index))
    
    def _query_rules(self, market_state: dict) -> list:
        """
        查詢匹配的規則
        
        Args:
            market_state: 市場狀態字典
        
        Returns:
            匹配的規則列表
        """
        if self.vectorstore is None:
            return []
        
        # 構建查詢文本
        query_text = f"市場狀態：{market_state.get('regime', 'neutral')}"
        
        if market_state.get('vix'):
            query_text += f", VIX={market_state['vix']:.1f}"
        
        if market_state.get('inflation'):
            query_text += f", 通膨={market_state['inflation']:.1f}%"
        
        # 查詢規則
        try:
            results = query_vectorstore(
                self.vectorstore,
                query_text,
                k=self.top_k,
                filter_dict={"source_type": "rule"}
            )
            
            matched_rules = []
            for doc, score in results:
                if score < (1 - self.min_similarity):  # 轉換為相似度
                    matched_rules.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "similarity": 1 - score
                    })
            
            return matched_rules
        except Exception as e:
            print(f"⚠️ 查詢規則失敗：{e}")
            return []
    
    def _parse_signal(self, rules: list) -> float:
        """
        從規則中解析交易信號
        
        Args:
            rules: 匹配的規則列表
        
        Returns:
            信號強度 (-1 到 1)
        """
        if not rules:
            return 0.0
        
        # 簡單加權平均
        total_signal = 0.0
        total_weight = 0.0
        
        for rule in rules:
            similarity = rule["similarity"]
            content = rule["content"].lower()
            
            # 解析規則內容中的信號
            signal = 0.0
            
            if any(word in content for word in ["買入", "多頭", "加倉", "樂觀"]):
                signal = 1.0
            elif any(word in content for word in ["賣出", "空頭", "減倉", "悲觀"]):
                signal = -1.0
            elif any(word in content for word in ["持有", "觀望", "中性"]):
                signal = 0.0
            
            # 加權
            total_signal += signal * similarity
            total_weight += similarity
        
        if total_weight == 0:
            return 0.0
        
        return total_signal / total_weight
    
    def next(self):
        """交易邏輯"""
        # 構建市場狀態
        market_state = {
            "regime": "neutral",
            "vix": self.data.Close[-1] / self.data.Close.mean(),  # 簡化 VIX
        }
        
        # 查詢規則
        rules = self._query_rules(market_state)
        
        # 解析信號
        signal = self._parse_signal(rules)
        
        # 更新信號指標
        self.signal_strength[-1] = signal
        self.rule_count[-1] = len(rules)
        
        # 執行交易
        if signal > self.signal_threshold:
            if not self.position:
                self.buy()
        elif signal < -self.signal_threshold:
            if not self.position:
                self.sell()
        else:
            if self.position:
                self.position.close()


# ============================================
# 策略 2: 投資人規則混合策略
# ============================================
class InvestorBlendStrategy(Strategy):
    """
    混合多個投資人規則的策略
    
    邏輯:
    1. 從不同投資人 (達利歐、索羅斯等) 的規則庫中查詢
    2. 根據投資人權重混合信號
    3. 執行交易
    """
    # 投資人權重 (可優化)
    dalio_weight = 0.4
    soros_weight = 0.3
    lynch_weight = 0.3
    
    def init(self):
        """初始化"""
        try:
            self.vectorstore = load_vectorstore()
            print(f"✅ 向量庫加載成功")
        except Exception as e:
            print(f"⚠️ 向量庫加載失敗：{e}")
            self.vectorstore = None
        
        # 初始化各投資人信號
        self.dalio_signal = self.I(lambda: pd.Series(0.0, index=self.data.index))
        self.soros_signal = self.I(lambda: pd.Series(0.0, index=self.data.index))
        self.lynch_signal = self.I(lambda: pd.Series(0.0, index=self.data.index))
        self.blend_signal = self.I(lambda: pd.Series(0.0, index=self.data.index))
    
    def _query_investor_rules(self, investor_id: str, market_state: dict) -> float:
        """
        查詢特定投資人的規則
        
        Args:
            investor_id: 投資人 ID
            market_state: 市場狀態
        
        Returns:
            信號強度
        """
        if self.vectorstore is None:
            return 0.0
        
        # 構建查詢
        query_text = f"投資人：{investor_id}, 市場狀態：{market_state.get('regime', 'neutral')}"
        
        try:
            results = query_vectorstore(
                self.vectorstore,
                query_text,
                k=3,
                filter_dict={"investor_id": investor_id}
            )
            
            if not results:
                return 0.0
            
            # 計算加權信號
            total_signal = 0.0
            total_weight = 0.0
            
            for doc, score in results:
                similarity = 1 - score
                content = doc.page_content.lower()
                
                signal = 0.0
                if any(word in content for word in ["買入", "多頭", "加倉"]):
                    signal = 1.0
                elif any(word in content for word in ["賣出", "空頭", "減倉"]):
                    signal = -1.0
                
                total_signal += signal * similarity
                total_weight += similarity
            
            return total_signal / total_weight if total_weight > 0 else 0.0
        
        except Exception as e:
            print(f"⚠️ 查詢失敗：{e}")
            return 0.0
    
    def next(self):
        """交易邏輯"""
        market_state = {"regime": "neutral"}
        
        # 查詢各投資人信號
        dalio_sig = self._query_investor_rules("dalio", market_state)
        soros_sig = self._query_investor_rules("soros", market_state)
        lynch_sig = self._query_investor_rules("lynch", market_state)
        
        # 更新指標
        self.dalio_signal[-1] = dalio_sig
        self.soros_signal[-1] = soros_sig
        self.lynch_signal[-1] = lynch_sig
        
        # 混合信號
        blend_sig = (
            dalio_sig * self.dalio_weight +
            soros_sig * self.soros_weight +
            lynch_sig * self.lynch_weight
        )
        self.blend_signal[-1] = blend_sig
        
        # 執行交易
        if blend_sig > 0.5:
            if not self.position:
                self.buy()
        elif blend_sig < -0.5:
            if not self.position:
                self.sell()
        else:
            if self.position:
                self.position.close()


# ============================================
# 主程序
# ============================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("📊 RAG 增強型回測示例")
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
    
    # 3. 運行 RAG 規則策略
    print("\n" + "=" * 70)
    print("策略 1: RAG 規則驅動策略")
    print("=" * 70)
    
    try:
        stats_rag = platform.run(
            strategy_class=RAGRuleStrategy,
            data=data,
            strategy_params={
                "top_k": 3,
                "min_similarity": 0.6,
                "signal_threshold": 0.7
            },
            verbose=True
        )
    except Exception as e:
        print(f"⚠️ RAG 策略回測失敗：{e}")
        print("  可能原因：向量庫未初始化")
        print("  跳過此策略...")
    
    # 4. 運行投資人混合策略
    print("\n" + "=" * 70)
    print("策略 2: 投資人規則混合策略")
    print("=" * 70)
    
    try:
        stats_blend = platform.run(
            strategy_class=InvestorBlendStrategy,
            data=data,
            strategy_params={
                "dalio_weight": 0.4,
                "soros_weight": 0.3,
                "lynch_weight": 0.3
            },
            verbose=True
        )
    except Exception as e:
        print(f"⚠️ 混合策略回測失敗：{e}")
        print("  跳過此策略...")
    
    # 5. 對比基準策略 (雙均線交叉)
    print("\n" + "=" * 70)
    print("策略 3: 基準策略 (雙均線交叉)")
    print("=" * 70)
    
    from services.backtest_platform import SmaCross
    stats_sma = platform.run(
        strategy_class=SmaCross,
        data=data,
        strategy_params={"n1": 10, "n2": 20},
        verbose=True
    )
    
    # 6. 保存結果
    print("\n💾 保存結果...")
    try:
        stats_rag.to_csv("stats_rag_strategy.csv")
        print("  ✅ RAG 策略結果已保存")
    except:
        print("  ⚠️ RAG 策略結果未保存")
    
    try:
        stats_blend.to_csv("stats_blend_strategy.csv")
        print("  ✅ 混合策略結果已保存")
    except:
        print("  ⚠️ 混合策略結果未保存")
    
    stats_sma.to_csv("stats_sma_baseline.csv")
    print("  ✅ 基準策略結果已保存")
    
    print("\n✅ RAG 增強型回測示例完成!")
    print("\n📊 對比分析:")
    print("  - 查看 CSV 文件比較各策略績效")
    print("  - 關注 RAG 策略是否跑贏基準")
    print("  - 分析不同投資人規則的貢獻度")
