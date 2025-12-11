# 投資決策框架摘要（LLM 專用）

> 濃縮版投資大師智慧，適用於 System Prompt 或快速參考。

---

## 一、投資人速查表

| ID | 投資人 | 基金 | 核心一句話 | 適用場景 | 決策權重 |
|----|--------|------|-----------|----------|----------|
| `warren_buffett` | Warren Buffett | Berkshire | 護城河+安全邊際+長期持有 | 選股估值 | stock:0.95, risk:0.7 |
| `charlie_munger` | Charlie Munger | Berkshire | 逆向思考+避免愚蠢 | 決策檢查 | risk:0.95, stock:0.8 |
| `ray_dalio` | Ray Dalio | Bridgewater | 經濟四象限+風險平價 | 資產配置 | portfolio:0.95, macro:0.9 |
| `stanley_druckenmiller` | Stanley Druckenmiller | Duquesne | 流動性決定一切 | 宏觀擇時 | macro:0.95, portfolio:0.7 |
| `george_soros` | George Soros | Quantum | 反身性+攻擊失衡 | 貨幣/極端事件 | macro:0.9, risk:0.7 |
| `howard_marks` | Howard Marks | Oaktree | 週期位置決定行動 | 風險評估 | risk:0.9, macro:0.7 |
| `peter_lynch` | Peter Lynch | Magellan | 買你懂的+PEG<1 | 成長股 | stock:0.9 |
| `seth_klarman` | Seth Klarman | Baupost | 深度價值+極端耐心 | 冷門資產 | stock:0.85, risk:0.8 |
| `michael_burry` | Michael Burry | Scion | 逆向深挖+不從眾 | 泡沫/特殊情況 | risk:0.8, stock:0.7 |
| `carl_icahn` | Carl Icahn | Icahn Ent | 股東行動+解鎖價值 | 公司治理 | stock:0.7 |
| `james_simons` | James Simons | Renaissance | 數據驅動+無情緒 | 量化策略 | systematic:0.9 |
| `ed_thorp` | Ed Thorp | Princeton Newport | 凱利公式+套利 | 倉位管理 | risk:0.8 |
| `cliff_asness` | Cliff Asness | AQR | 因子投資+價值動量 | 組合構建 | portfolio:0.8 |
| `greg_abel` | Greg Abel | BHE | 長週期資本配置 | 公用事業 | stock:0.6 |

---

## 二、核心決策規則（IF-THEN 格式）

### 買入規則
```
IF 盈餘收益率 > 10Y國債 × 1.5 AND 護城河完好
   THEN 考慮買入 (Buffett)
   
IF PEG < 0.8 AND 增速可持續 5年+
   THEN 成長股機會 (Lynch)
   
IF 便宜因為被動拋售 AND 基本面未變
   THEN 深入研究 (Klarman)
   
IF 短期負面新聞 AND 護城河未損 AND 股價下跌 > 30%
   THEN 機會窗口 (Buffett)
```

### 賣出/不買規則
```
IF 護城河被侵蝕 AND 無改善跡象
   THEN 賣出 (Buffett)
   
IF 無法用 2 句話解釋商業模式
   THEN 不買 (Munger) - 能力圈外
   
IF 估值需要「信仰」才能合理化
   THEN 不買 (Munger) - 投機
   
IF 買入論點不再成立
   THEN 立即止損 (Soros)
```

### 宏觀/倉位規則
```
IF 淨流動性上升 AND 估值合理
   THEN 做多風險資產 (Druckenmiller)
   
IF 恐慌拋售 + 估值極低 + 信用凍結
   THEN 底部接近，準備買入 (Marks)
   
IF 槓桿激增 + 散戶湧入 + 「這次不一樣」
   THEN 頂部接近，減倉 (Marks, Munger)
   
IF 確信度 90%+ AND 深度研究
   THEN 重倉 10-25% (Druckenmiller)
   
IF 確信度 < 50%
   THEN 小倉位或不做 (Druckenmiller)
```

---

## 三、經濟四象限配置（Dalio）

| 環境 | 增長 | 通膨 | 偏好資產 |
|------|------|------|----------|
| 溫和擴張 | ↑ | ↓ | 股票、公司債 |
| 過熱 | ↑ | ↑ | 商品、TIPS、新興股票 |
| 滯脹 | ↓ | ↑ | 商品、黃金、TIPS |
| 衰退/通縮 | ↓ | ↓ | 長期國債、現金 |

---

## 四、週期位置判斷（Marks）

| 階段 | 特徵 | 行動 |
|------|------|------|
| 底部 | 信用凍結、恐慌拋售、估值極低 | 積極進場 |
| 復甦 | 利差收窄、風險偏好回升 | 持有優質高β |
| 過熱 | 槓桿激增、低質資產熱捧、散戶湧入 | 減碼/防守 |
| 下行 | 違約攀升、去槓桿、信用收緊 | 保留彈藥 |

---

## 五、決策品質檢查（Munger）

### 心理偏誤自查
| 偏誤 | 表現 | 解法 |
|------|------|------|
| 確認偏誤 | 只看利好 | 主動找反駁論點 |
| 過度自信 | 我比市場聰明 | 市場知道什麼我不知道的？ |
| 從眾效應 | 大家都在買 | 獨立思考，我的判斷是什麼？ |
| 錨定效應 | 被成本價錨定 | 忘記成本，重新評估 |
| FOMO | 怕錯過 | 這符合我的標準嗎？ |

### 決策前五問
1. **我在能力圈內嗎？** 能 2 句話解釋清楚嗎？
2. **有安全邊際嗎？** 最壞情況能接受嗎？
3. **週期在哪個位置？** 該進攻還是防守？
4. **流動性趨勢如何？** 淨流動性上升還是下降？
5. **有心理偏誤嗎？** 是理性決策還是情緒決策？

---

## 六、關鍵指標速查

| 指標 | 公式/含義 | 閾值 | 來源 |
|------|----------|------|------|
| **盈餘收益率** | E/P (倒數 P/E) | > 國債 × 1.5 = 便宜 | Buffett |
| **FCF Yield** | FCF/市值 | > 8% = 機會 | Buffett |
| **PEG** | P/E ÷ 增速 | < 1 便宜, > 2 貴 | Lynch |
| **ROIC** | 資本回報率 | > 15% 持續 = 好生意 | Buffett |
| **淨流動性** | Fed B/S − TGA − RRP | 上升 = 風險偏好 | Druckenmiller |
| **信用利差** | 高收益-國債 | 擴大 = 風險上升 | Marks |
| **VIX** | 恐懼指數 | > 30 恐慌, < 15 自滿 | Burry |
| **市值/GDP** | Buffett 指標 | > 150% = 泡沫風險 | Buffett |

---

## 七、情境快速路由

### 市場恐慌時
**諮詢順序**：Howard Marks → Seth Klarman → Warren Buffett
**關鍵問題**：
- 這是流動性危機還是償付危機？
- 央行有救市意願和能力嗎？
- 哪些資產被無差別拋售？

### 市場狂熱時
**諮詢順序**：Charlie Munger → Howard Marks → Michael Burry
**關鍵問題**：
- 我是不是在 FOMO？
- 估值用什麼邏輯都合理化了嗎？
- 新手大量進場了嗎？

### 經濟衰退時
**諮詢順序**：Ray Dalio → Howard Marks → Seth Klarman
**關鍵問題**：
- 處於哪個象限？增長↓ + 通膨↑ or ↓？
- 違約開始了嗎？
- 央行政策空間如何？

### 利率轉向時
**諮詢順序**：Stanley Druckenmiller → Ray Dalio → Peter Lynch
**關鍵問題**：
- Fed 轉向信號確認了嗎？
- 是預防性降息還是衰退式降息？
- 市場定價了多少降息？

---

## 八、經典語錄（可引用）

> "價格是你付出的，價值是你得到的。" — **Buffett**

> "如果我知道我會死在哪裡，我就永遠不去那裡。" — **Munger**

> "流動性推動市場，而非基本面。" — **Druckenmiller**

> "週期意識是投資最重要的事。" — **Marks**

> "最大的風險是永久虧損，而非波動。" — **Marks**

> "市場不斷在不確定中波動，靠押注意外賺錢。" — **Soros**

> "Know what you own, and know why you own it." — **Lynch**

> "長期導向是投資者最大的優勢。" — **Klarman**

---

## 九、決策工作流（標準流程）

```
[1] 宏觀定位
    ├── 經濟象限？(Dalio)
    ├── 流動性趨勢？(Druckenmiller)
    └── 週期位置？(Marks)
           ↓
[2] 標的篩選
    ├── 護城河？(Buffett)
    ├── 估值合理？(Buffett/Lynch)
    └── 安全邊際？(Klarman)
           ↓
[3] 決策檢查
    ├── 能力圈內？(Munger)
    ├── 心理偏誤？(Munger)
    └── 最壞情況？(Munger)
           ↓
[4] 倉位執行
    ├── 確信度 → 倉位 (Druckenmiller)
    ├── 止損點 (Soros)
    └── 組合風險 (Dalio)
```

---

## 十、快速參考映射

```yaml
選股問題:
  護城河評估: [warren_buffett, charlie_munger]
  成長股估值: [peter_lynch]
  深度價值: [seth_klarman, michael_burry]
  
宏觀問題:
  週期定位: [ray_dalio, howard_marks]
  流動性: [stanley_druckenmiller]
  貨幣匯率: [george_soros]
  
風險問題:
  心理偏誤: [charlie_munger]
  泡沫識別: [charlie_munger, michael_burry]
  止損決策: [george_soros]
  
配置問題:
  資產配置: [ray_dalio]
  現金比例: [seth_klarman, howard_marks]
  集中分散: [warren_buffett(集中), ray_dalio(分散)]
```

---

> **LLM 使用提示**：
> 1. 根據用戶問題類型，從「快速參考映射」找到相關投資人
> 2. 應用對應的「決策規則」給出 IF-THEN 判斷
> 3. 用「決策品質檢查」驗證建議的合理性
> 4. 必要時引用「經典語錄」增強說服力

