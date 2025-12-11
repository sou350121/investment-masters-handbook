---
investor_id: james_simons
full_name: James Simons
chinese_name: 詹姆斯·西蒙斯
fund: Renaissance Technologies
aum: "$130B"
style:
  - quantitative
  - systematic
  - high_frequency
  - data_driven
applicable_scenarios:
  - quant_strategy_design
  - systematic_trading
  - backtesting_principles
  - risk_management
market_conditions:
  all_conditions: neutral
decision_weight:
  stock_pick: 0.2
  macro_timing: 0.2
  risk_check: 0.6
  portfolio: 0.4
tags:
  - 量化
  - 统计套利
  - 数据驱动
  - 系统化
related_investors:
  similar: []
  complementary: []
---

# James Simons 投资框架

## QUICK_FACTS
- **基金**：Renaissance Technologies（旗舰 Medallion Fund）
- **规模**：$130B
- **核心风格**：数据驱动 + 统计套利 + 无情绪执行
- **最佳适用**：量化策略设计、系统化交易、风控原则

> **风格**：纯量化、数据驱动、系统化交易

## 核心原则
1. **数据 > 直觉**：一切决策基于统计规律；不依赖主观判断。
2. **找微小优势**：单笔胜率可能只有 50.5%，但高频+大量交易累积优势。
3. **模型迭代**：持续研究、测试、改进；没有「完成」的策略。
4. **严格风控**：每笔交易风险极小；靠组合与频率取胜。
5. **人才密度**：雇用数学家、物理学家、计算机科学家，而非传统金融人。

## Medallion Fund 特点
| 维度 | 特征 |
|------|------|
| 回报 | 1988-2018 年均 ~66%（扣费前），~39%（扣费后） |
| 策略 | 短线统计套利、均值回归、模式识别 |
| 持仓 | 数千个小仓位，极度分散 |
| 周转 | 极高，持仓周期从秒到天 |
| 封闭 | 只对员工开放；外部资金在 RIEF/RIDA |

## 量化策略框架（概念）
| 步骤 | 内容 |
|------|------|
| 1. 数据 | 清洗价格、成交量、基本面、另类数据 |
| 2. 信号 | 统计模型找预测性特征 |
| 3. 组合 | 多信号加权、风险预算 |
| 4. 执行 | 最小化滑点、市场冲击 |
| 5. 监控 | 实时风控、模型衰减检测 |

## 快速检查清单（量化策略设计）
- **数据品质？** 干净、无前视偏差、够长？
- **过拟合风险？** 样本外测试、多市场验证？
- **交易成本？** 滑点、佣金是否被考虑？
- **容量限制？** 策略在多大资金规模下有效？
- **模型衰减？** 有无监控机制？何时停用？

## 对主观投资者的启发
- **纪律**：规则一旦制定就执行，不因情绪改变。
- **回测思维**：任何想法先历史验证。
- **小注多试**：不确定时小仓位测试。
- **承认无知**：不需要「理解」为什么有效，只需确认统计显著。

## 经典语录
- "We don't hire people from Wall Street... we hire people who have done science."
- "Patterns are there, waiting to be discovered."
- "We're right 50.75% of the time... but we're 100% right 50.75% of the time."

## 风险警示
- 量化策略需要大量技术基础设施。
- 过拟合是最大敌人。
- 策略容量有限；Medallion 只管理 ~$10B。
- 模型可能突然失效（regime change）。

## DECISION_RULES（决策规则）

### 策略设计规则
```
IF 數據乾淨 + 無前視偏差 + 夠長
   THEN 可以開始研究
   BECAUSE 數據品質是基礎

IF 樣本外測試 + 多市場驗證通過
   THEN 減少過擬合風險
   BECAUSE 泛化能力確認

IF 考慮滑點 + 佣金後仍有正期望
   THEN 策略可行
   BECAUSE 真實成本

IF 策略容量 > 預期資金規模
   THEN 可以部署
   BECAUSE 容量限制
```

### 执行规则
```
IF 規則制定完成
   THEN 嚴格執行，不因情緒改變
   BECAUSE 紀律是量化核心

IF 有想法
   THEN 先歷史回測
   BECAUSE 驗證優先

IF 不確定
   THEN 小倉位測試
   BECAUSE 小注多試

IF 統計顯著
   THEN 可以執行（不需要「理解」為什麼）
   BECAUSE 數據 > 直覺
```

### 风控规则
```
IF 模型衰減信號
   THEN 減倉或停用
   BECAUSE 市場 regime change

IF 單筆風險 > 閾值
   THEN 不執行
   BECAUSE 嚴格風控

IF 組合風險 > 預算
   THEN 再平衡
   BECAUSE 控制整體風險
```

### 监控规则
```
IF 策略上線
   THEN 實時監控 + 模型衰減檢測
   BECAUSE 持續驗證

IF 回報偏離預期
   THEN 檢查模型 + 數據
   BECAUSE 及時發現問題

IF 模型持續失效
   THEN 停用 + 重新研究
   BECAUSE 沒有永久有效的策略
```

---

## RED_FLAGS（危险信号）
- [ ] 过拟合（样本内优秀，样本外失败）
- [ ] 容量达到上限
- [ ] 模型衰减（回报持续低于预期）
- [ ] 市场 regime change

---

## RELATED_INVESTORS（相关投资人）
- 纯量化风格，与主观投资人方法论不同

---

## TODO / 待补
- 均值回归策略入门模板。
- 回测框架推荐（Backtrader, Zipline, vectorbt）。


