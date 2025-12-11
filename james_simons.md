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
  - 統計套利
  - 數據驅動
  - 系統化
related_investors:
  similar: []
  complementary: []
---

# James Simons 投資框架

## QUICK_FACTS
- **基金**：Renaissance Technologies（旗艦 Medallion Fund）
- **規模**：$130B
- **核心風格**：數據驅動 + 統計套利 + 無情緒執行
- **最佳適用**：量化策略設計、系統化交易、風控原則

> **風格**：純量化、數據驅動、系統化交易

## 核心原則
1. **數據 > 直覺**：一切決策基於統計規律；不依賴主觀判斷。
2. **找微小優勢**：單筆勝率可能只有 50.5%，但高頻+大量交易累積優勢。
3. **模型迭代**：持續研究、測試、改進；沒有「完成」的策略。
4. **嚴格風控**：每筆交易風險極小；靠組合與頻率取勝。
5. **人才密度**：雇用數學家、物理學家、計算機科學家，而非傳統金融人。

## Medallion Fund 特點
| 維度 | 特徵 |
|------|------|
| 回報 | 1988-2018 年均 ~66%（扣費前），~39%（扣費後） |
| 策略 | 短線統計套利、均值回歸、模式識別 |
| 持倉 | 數千個小倉位，極度分散 |
| 週轉 | 極高，持倉週期從秒到天 |
| 封閉 | 只對員工開放；外部資金在 RIEF/RIDA |

## 量化策略框架（概念）
| 步驟 | 內容 |
|------|------|
| 1. 數據 | 清洗價格、成交量、基本面、另類數據 |
| 2. 信號 | 統計模型找預測性特徵 |
| 3. 組合 | 多信號加權、風險預算 |
| 4. 執行 | 最小化滑點、市場衝擊 |
| 5. 監控 | 實時風控、模型衰減檢測 |

## 快速檢查清單（量化策略設計）
- **數據品質？** 乾淨、無前視偏差、夠長？
- **過擬合風險？** 樣本外測試、多市場驗證？
- **交易成本？** 滑點、佣金是否被考慮？
- **容量限制？** 策略在多大資金規模下有效？
- **模型衰減？** 有無監控機制？何時停用？

## 對主觀投資者的啟發
- **紀律**：規則一旦制定就執行，不因情緒改變。
- **回測思維**：任何想法先歷史驗證。
- **小注多試**：不確定時小倉位測試。
- **承認無知**：不需要「理解」為什麼有效，只需確認統計顯著。

## 經典語錄
- "We don't hire people from Wall Street... we hire people who have done science."
- "Patterns are there, waiting to be discovered."
- "We're right 50.75% of the time... but we're 100% right 50.75% of the time."

## 風險警示
- 量化策略需要大量技術基礎設施。
- 過擬合是最大敵人。
- 策略容量有限；Medallion 只管理 ~$10B。
- 模型可能突然失效（regime change）。

## DECISION_RULES（決策規則）

### 策略設計規則
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

### 執行規則
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

### 風控規則
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

### 監控規則
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

## RED_FLAGS（危險信號）
- [ ] 過擬合（樣本內優秀，樣本外失敗）
- [ ] 容量達到上限
- [ ] 模型衰減（回報持續低於預期）
- [ ] 市場 regime change

---

## RELATED_INVESTORS（相關投資人）
- 純量化風格，與主觀投資人方法論不同

---

## TODO / 待補
- 均值回歸策略入門模板。
- 回測框架推薦（Backtrader, Zipline, vectorbt）。


