# 架构决策 (ADR): S-0004 自动化投委会 (IC) 裁决引擎

## 背景
用户要求系统能像一个真实基金一样运作。这意味着系统不仅要检索知识，还要像 CIO 一样处理大师间的观点冲突，并给出最终的定量结论。

## 决策点

### 1. 动态权重矩阵 (Regime-Weight Matrix)
- **设计**：系统预设一套 Regime 到大师类别的权重映射：
    - `Crisis / Stagflation` -> Macro Experts (Dalio, Soros) 权重 0.8。
    - `Bull / Neutral` -> Value/Growth Experts (Buffett, Lynch) 权重 0.8。
- **实现**：裁决引擎在合成 `risk_multiplier` 时，根据当前识别的 Regime 自动调整各方意见的增益。

### 2. 自动裁决协议 (Auto-Adjudication)
- **方案**：采用「CIO 调停模式」。
- **逻辑**：AI 不再询问用户“你听谁的”，而是基于「基金生存第一原则」和当前「Regime 优先级」进行裁决。
- **示例**：若 Buffett 建议买入但 Dalio 警告流动性危机，在 Crisis 环境下，系统将自动偏向 Dalio，输出 `risk_multiplier < 1.0`。

### 3. 定量合成输出
- **数据结构**：
    ```json
    "ensemble_adjustment": {
        "final_multiplier_offset": -0.15,
        "primary_expert": "ray_dalio",
        "conflict_detected": true,
        "resolution": "Crisis regime prioritizes defensive macro over selective value."
    }
    ```

### 4. 输出分层（一级执行 / 二级溯源）
- **动机**：用户真正需要的是可执行的“股/债/金/现金”配比，而不是只能阅读的长篇辩论。
- **方案**：`/api/rag/ensemble` 输出拆分为两层：
  - `primary`：四类资产目标配比（sum=100）+ 一句话结论 + confidence
  - `secondary`：保留原有辩论/引用/裁决结构，作为审计与解释层
