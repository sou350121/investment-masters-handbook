---
investor_id: peter_lynch
full_name: Peter Lynch
chinese_name: 彼得·林奇
fund: Fidelity Magellan Fund
nationality: 美国
intro_zh: 麦哲伦基金传奇经理人，任期内年化回报率高达 29%。林奇以其“买你所知”的常识性投资哲学闻名，主张通过日常生活中的观察发现“十倍股”。他将股票分为六大类，并为每一类制定了独特的买卖准则，是成长股投资的巅峰人物。
style:
  - growth_at_reasonable_price
  - bottom_up
  - everyday_observation
  - categorical_investing
applicable_scenarios:
  - growth_stock_selection
  - peg_valuation
  - stock_classification
  - retail_investor_advantage
market_conditions:
  bullish: high
  bearish: neutral
  expansion: high
decision_weight:
  stock_pick: 0.95
  macro_timing: 0.2
  risk_check: 0.6
  portfolio: 0.5
tags:
  - PEG估值
  - 成长股
  - 十倍股
  - 股票分类
  - 买你所知
related_investors:
  similar: [warren_buffett, thomas_rowe_price]
  complementary: [ray_dalio, howard_marks]
---

# Peter Lynch 投资框架：常识、分类与成长

> "如果你在研究公司上花的时间还没在买冰箱上花的时间多，那你注定会亏钱。" —— 彼得·林奇

## 📋 林奇选股工具箱 (The Stock Picker's Toolkit)

### 1. 股票六大分类 (The 6 Categories)
1. **低速增长股 (Slow Growers)**：大而成熟，增长慢于 GDP。主要看股息。
2. **稳定增长股 (Stalwarts)**：每年 10-12% 增长。目标：30-50% 的阶段性回报。
3. **快速增长股 (Fast Growers)**：年增长 20-25%+。十倍股的摇篮。
4. **周期股 (Cyclicals)**：随经济波动。关键：时机（低 PE 往往是卖点，高 PE 可能是买点）。
5. **困境反转股 (Turnarounds)**：濒临破产但有救。看现金流和负债。
6. **隐蔽资产股 (Asset Plays)**：市场忽视了公司拥有的土地、现金、牌照或税收减免。

### 2. PEG 估值模型
- **核心公式**：PEG = PE / 盈利增长率 (Growth Rate)。
- **标准**：PEG = 1（公允）；PEG = 0.5（低估）；PEG = 2（高估）。

---

## 🚫 绝对禁止清单 (The NEVER List)
- **绝不买入“下一个某某”公司**：当一家公司被称为“下一个微软”或“下一个麦当劳”时，它通常已经过热且注定失败。
- **绝不买入“恶性多元化 (Diworsification)”的公司**：即公司将利润挥霍在与其核心业务无关、且竞争激烈的平庸业务上。
- **绝不在不了解商业模式的情况下买入**：如果你不能用蜡笔在 2 分钟内画出这家公司是怎么赚钱的，就不要碰。
- **绝不相信“股价已经跌了这么多了，不可能再跌了”**：零才是股价的底，跌了 90% 的股票可能还会再跌 90%。
- **绝不试图预测宏观经济或利率**：如果你每年花 13 分钟研究宏观，你就浪费了 10 分钟。

---

## 📅 压力测试：不同阶段的应对
### 1. 经济衰退初期的反应 (Early Recession)
- **反应**：检查快速增长股的负债。
- **动作**：增加“稳定增长股”比例，寻找那些无论经济多差大家都要买的东西（如剃须刀、可乐）。

### 2. 疯狂大牛市 (Market Euphoria)
- **反应**：观察零售店和购物中心。
- **动作**：如果你发现即使是表现平平的公司也被机构疯抢，开始检查 PEG 是否超过 2.0，考虑获利了结。

---

## 📖 经典案例研究 (Case Studies)

### 1. Dunkin' Donuts：生活中的十倍股
- **背景**：林奇注意到每家分店都客满，且他自己喜欢他们的咖啡。
- **逻辑**：简单的可复制模式 + 强大的本地口碑 + 极高的资本回报率。
- **结果**：通过在全国范围内的扩张，实现了巨大的复利回报。

### 2. Chrysler：困境反转的教科书
- **背景**：克莱斯勒当时濒临破产，政府提供贷款担保。
- **动作**：林奇计算了其账面现金和即将推出的新车款（K-Car），意识到如果它能活下来，收益将是巨大的。
- **结果**：公司成功反转，股价飞涨。

---

## 💡 决策规则 (DECISION_RULES)

### 成长与估值规则 (Growth & Valuation)
```text
IF 盈利增长率 (G) > 20% AND PE < 盈利增长率 (即 PEG < 1) AND 负债率 < 30%
   THEN 视为“快速增长股”潜在标的，分批买入
   BECAUSE 市场尚未完全定价其成长性，且财务结构安全

IF 某公司是“稳定增长股” (Stalwart) AND 股价涨幅已达 50% AND PEG 接近 2.0
   THEN 卖出并寻找下一个被低估的稳定增长股
   BECAUSE 稳定增长股的估值溢价有限，获利了结是保持活力的关键

IF 公司账面现金 > 负债 AND 现金/股价比例 > 30%
   THEN 视为“资产型股票” (Asset Play) 进行深度调查
   BECAUSE 这种情况下你相当于免费买到了公司的业务
```

### 分类与操作规则 (Categorical Rules)
```text
IF 投资标的是“周期股” (Cyclical) AND 市盈率 (PE) 处于历史极低点 AND 媒体全是利好
   THEN 考虑卖出
   BECAUSE 周期股的低 PE 往往出现在盈利顶峰，预示着行业即将下行

IF 投资标的是“困境反转股” (Turnaround) AND 负债结构得到重组 AND 核心业务现金流转正
   THEN 建立初始仓位
   BECAUSE 风险最剧烈的时期已过，修复空间巨大

IF 发现某公司正在进行“恶性多元化” (收购非核心业务)
   THEN 立即将其从候选名单中剔除
   BECAUSE 管理层正在稀释股东价值并增加复杂性风险
```

### 持续追踪规则 (Monitoring)
```text
IF 买入后的“故事”发生改变 (例如快速增长股的同店销售增长率连续两个季度下滑)
   THEN 无论当前盈亏，立即卖出
   BECAUSE 成长股最危险的是成长动力的丧失

IF 机构持股比例从 < 10% 增长到 > 60% AND 股价已反映此利好
   THEN 考虑退出
   BECAUSE 寻找被低估标的的优势已经消失
```
