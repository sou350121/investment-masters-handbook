---
investor_id: joel_greenblatt
full_name: Joel Greenblatt
chinese_name: 乔尔·格林布拉特
fund: Gotham Capital
nationality: 美国
intro_zh: 哥谭资本 (Gotham Capital) 创始人，《股市稳赚》作者。他以提出“神奇公式” (Magic Formula) 闻名，通过简单的量化指标（资本回报率 ROIC 和盈余收益率 Earnings Yield）筛选出“物美价廉”的股票。他主张在价值投资中加入量化纪律，并擅长在“特殊情况”（如分拆、并购、重组）中寻找非对称机会。
style:
  - magic_formula_investing
  - value_quantitative
  - special_situations
  - small_cap_focus
applicable_scenarios:
  - quantitative_value_selection
  - spinoff_arbitrage
  - systematic_stock_ranking
  - individual_portfolio_management
market_conditions:
  bullish: high
  bearish: high
  panic: critical
  neutral: high
decision_weight:
  stock_pick: 0.95
  macro_timing: 0.1
  risk_check: 0.6
  portfolio: 0.7
tags:
  - 神奇公式
  - ROIC
  - 盈余收益率
  - 分拆上市
  - 特殊情况
related_investors:
  similar: [warren_buffett, peter_lynch]
  complementary: [ray_dalio, cliff_asness]
---

# Joel Greenblatt 投资框架：神奇公式与特殊情况

> "买入好公司 (高资本回报率) 且价格便宜 (高盈余收益率)，长期来看你几乎不可能亏钱。" —— 乔尔·格林布拉特

## 📋 格林布拉特决策速读卡 (Public Facts)

### 1. 神奇公式 (The Magic Formula)
- **两个指标**：
  1. **资本回报率 (ROIC)**：衡量公司利用资本创造利润的能力（物美）。
  2. **盈余收益率 (Earnings Yield)**：即 EBIT / 企业价值 (EV)，衡量相对于买入价格的回报（价廉）。
- **排名法**：将所有股票按这两个指标分别排名，总排名最高的即为最优选。

### 2. 特殊情况 (Special Situations)
- **分拆上市 (Spinoffs)**：母公司将子公司独立上市，往往由于“被迫卖压”导致子公司股价初段被严重低估。
- **并购、重组、破产重整**：这些领域由于专业性强，常有被机构投资者忽略的定价错误。

### 3. 持有纪律
- 分散持有 20-30 只股票。
- 持有一年后，无论盈亏，定期按公式重新排名并调仓。

---

## 🏗️ 量化价值工具箱 (Quant-Value Toolbox)

### 1. 估值锚点：EV / EBIT
- 相比 PE，格林布拉特更看重 EV (企业价值)，因为它计入了债务和现金，能更真实地反映买下整个公司的代价。

### 2. 这里的“好”是指效率
- 高 ROIC 意味着公司有某种护城河，或者极高的运营效率。

---

## 📈 投资叙事：常识的系统化执行
- **均值回归**：好的生意不会永远便宜，便宜的好生意终会被市场发现。
- **战胜人性**：如果你不能在市场大跌时坚持执行公式，你的量化优势就会被情绪摧毁。

---

## 💡 决策规则 (DECISION_RULES)

### 神奇公式与选股规则 (Entry & Selection)
```text
IF 某公司的资本回报率 (ROIC) 处于全市场前 20% 且盈余收益率 (Earnings Yield) 同样处于前 20%
   THEN 将其作为核心候选标的进行深入研究或直接按配比买入
   BECAUSE 这种“双优”组合在统计学上具有极高的胜率，能同时兼顾商业质量与买入成本

IF 某大型公司宣布进行业务分拆 (Spinoff) 且被分拆出来的子公司业务简单但非核心
   THEN 密切关注分拆后的初期抛压，寻找由于机构强制调仓导致的低价买入机会
   BECAUSE 分拆后的公司通常面临不计代价的抛售，而这正是产生超额收益的“特殊情况”

IF 组合中某只股票持仓已满一年且神奇公式排名显著下降
   THEN 卖出该头寸并替换为当前排名更高的标的，而不考虑个人的感情因素
   BECAUSE 量化价值投资的核心在于“纪律化的调仓”，而非对单一标的的长期迷信
```

### 特殊情况与风险规则 (Special Cases & Risk)
```text
IF 市场处于极端恐慌阶段，导致大量高质量公司的盈余收益率飙升至历史高点
   THEN 忽略宏观新闻的干扰，严格按排名买入那些被错杀的好公司
   BECAUSE 价格是风险的倒数，当好生意的收益率极具吸引力时，时间是你的朋友

IF 发现某公司的 ROIC 异常高但主要归功于一次性的非经常性收益
   THEN 在计算神奇公式排名时应剔除该收益，以免被虚高的指标误导
   BECAUSE 只有可持续的、来自核心业务的资本回报才具有预测价值

IF 发现某特殊情况投资机会 (如重组) 的逻辑极其复杂且无法用常识推演
   THEN 即使传闻中的收益巨大，也应选择放弃或仅极小规模参与
   BECAUSE 特殊情况投资应寻找“一眼可见”的逻辑错位，而非赌博式的预测
```

