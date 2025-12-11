# 投资决策框架摘要（LLM 专用）

> 浓缩版投资大师智慧，适用于 System Prompt 或快速参考。

---

## 一、投资人速查表

| ID | 投资人 | 基金 | 核心一句话 | 适用场景 | 决策权重 |
|----|--------|------|-----------|----------|----------|
| `warren_buffett` | Warren Buffett | Berkshire | 护城河+安全边际+长期持有 | 选股估值 | stock:0.95, risk:0.7 |
| `charlie_munger` | Charlie Munger | Berkshire | 逆向思考+避免愚蠢 | 决策检查 | risk:0.95, stock:0.8 |
| `ray_dalio` | Ray Dalio | Bridgewater | 经济四象限+风险平价 | 资产配置 | portfolio:0.95, macro:0.9 |
| `stanley_druckenmiller` | Stanley Druckenmiller | Duquesne | 流动性决定一切 | 宏观择时 | macro:0.95, portfolio:0.7 |
| `george_soros` | George Soros | Quantum | 反身性+攻击失衡 | 货币/极端事件 | macro:0.9, risk:0.7 |
| `howard_marks` | Howard Marks | Oaktree | 周期位置决定行动 | 风险评估 | risk:0.9, macro:0.7 |
| `peter_lynch` | Peter Lynch | Magellan | 买你懂的+PEG<1 | 成长股 | stock:0.9 |
| `seth_klarman` | Seth Klarman | Baupost | 深度价值+极端耐心 | 冷门资产 | stock:0.85, risk:0.8 |
| `michael_burry` | Michael Burry | Scion | 逆向深挖+不从众 | 泡沫/特殊情况 | risk:0.8, stock:0.7 |
| `carl_icahn` | Carl Icahn | Icahn Ent | 股东行动+解锁价值 | 公司治理 | stock:0.7 |
| `james_simons` | James Simons | Renaissance | 数据驱动+无情绪 | 量化策略 | systematic:0.9 |
| `ed_thorp` | Ed Thorp | Princeton Newport | 凯利公式+套利 | 仓位管理 | risk:0.8 |
| `cliff_asness` | Cliff Asness | AQR | 因子投资+价值动量 | 组合构建 | portfolio:0.8 |
| `greg_abel` | Greg Abel | BHE | 长周期资本配置 | 公用事业 | stock:0.6 |

---

## 二、核心决策规则（IF-THEN 格式）

### 买入规则
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

### 卖出/不买规则
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

### 宏观/仓位规则
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

## 三、经济四象限配置（Dalio）

| 环境 | 增长 | 通膨 | 偏好资产 |
|------|------|------|----------|
| 温和扩张 | ↑ | ↓ | 股票、公司债 |
| 过热 | ↑ | ↑ | 商品、TIPS、新兴股票 |
| 滞胀 | ↓ | ↑ | 商品、黄金、TIPS |
| 衰退/通缩 | ↓ | ↓ | 长期国债、现金 |

---

## 四、周期位置判断（Marks）

| 阶段 | 特征 | 行动 |
|------|------|------|
| 底部 | 信用冻结、恐慌抛售、估值极低 | 积极进场 |
| 复苏 | 利差收窄、风险偏好回升 | 持有优质高β |
| 过热 | 杠杆激增、低质资产热捧、散户涌入 | 减码/防守 |
| 下行 | 违约攀升、去杠杆、信用收紧 | 保留弹药 |

---

## 五、决策品质检查（Munger）

### 心理偏误自查
| 偏误 | 表现 | 解法 |
|------|------|------|
| 确认偏误 | 只看利好 | 主动找反驳论点 |
| 过度自信 | 我比市场聪明 | 市场知道什么我不知道的？ |
| 从众效应 | 大家都在买 | 独立思考，我的判断是什么？ |
| 锚定效应 | 被成本价锚定 | 忘记成本，重新评估 |
| FOMO | 怕错过 | 这符合我的标准吗？ |

### 决策前五问
1. **我在能力圈内吗？** 能 2 句话解释清楚吗？
2. **有安全边际吗？** 最坏情况能接受吗？
3. **周期在哪个位置？** 该进攻还是防守？
4. **流动性趋势如何？** 净流动性上升还是下降？
5. **有心理偏误吗？** 是理性决策还是情绪决策？

---

## 六、关键指标速查

| 指标 | 公式/含义 | 阈值 | 来源 |
|------|----------|------|------|
| **盈余收益率** | E/P (倒数 P/E) | > 国债 × 1.5 = 便宜 | Buffett |
| **FCF Yield** | FCF/市值 | > 8% = 机会 | Buffett |
| **PEG** | P/E ÷ 增速 | < 1 便宜, > 2 贵 | Lynch |
| **ROIC** | 资本回报率 | > 15% 持续 = 好生意 | Buffett |
| **净流动性** | Fed B/S − TGA − RRP | 上升 = 风险偏好 | Druckenmiller |
| **信用利差** | 高收益-国债 | 扩大 = 风险上升 | Marks |
| **VIX** | 恐惧指数 | > 30 恐慌, < 15 自满 | Burry |
| **市值/GDP** | Buffett 指标 | > 150% = 泡沫风险 | Buffett |

---

## 七、情境快速路由

### 市场恐慌时
**咨询顺序**：Howard Marks → Seth Klarman → Warren Buffett
**关键问题**：
- 这是流动性危机还是偿付危机？
- 央行有救市意愿和能力吗？
- 哪些资产被无差别抛售？

### 市场狂热时
**咨询顺序**：Charlie Munger → Howard Marks → Michael Burry
**关键问题**：
- 我是不是在 FOMO？
- 估值用什么逻辑都合理化了吗？
- 新手大量进场了吗？

### 经济衰退时
**咨询顺序**：Ray Dalio → Howard Marks → Seth Klarman
**关键问题**：
- 处于哪个象限？增长↓ + 通膨↑ or ↓？
- 违约开始了吗？
- 央行政策空间如何？

### 利率转向时
**咨询顺序**：Stanley Druckenmiller → Ray Dalio → Peter Lynch
**关键问题**：
- Fed 转向信号确认了吗？
- 是预防性降息还是衰退式降息？
- 市场定价了多少降息？

---

## 八、经典语录（可引用）

> "价格是你付出的，价值是你得到的。" — **Buffett**

> "如果我知道我会死在哪里，我就永远不去那里。" — **Munger**

> "流动性推动市场，而非基本面。" — **Druckenmiller**

> "周期意识是投资最重要的事。" — **Marks**

> "最大的风险是永久亏损，而非波动。" — **Marks**

> "市场不断在不确定中波动，靠押注意外赚钱。" — **Soros**

> "Know what you own, and know why you own it." — **Lynch**

> "长期导向是投资者最大的优势。" — **Klarman**

---

## 九、决策工作流（标准流程）

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

## 十、快速参考映射

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
> 1. 根据用户问题类型，从「快速参考映射」找到相关投资人
> 2. 应用对应的「决策规则」给出 IF-THEN 判断
> 3. 用「决策品质检查」验证建议的合理性
> 4. 必要时引用「经典语录」增强说服力

