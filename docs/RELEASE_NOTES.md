# 发布日志 & 推文模板

> 每次更新的详细记录和社交媒体推文模板

---

## v1.5.1 - 2024-12-14

### 更新内容

#### 📚 RAG 完整指南

**新增 700+ 行 RAG 使用指南**：`guides/rag_guide.md`

核心内容：
- 📖 **RAG 概念介绍**：什么是 RAG？为什么需要 RAG？
- 🏗️ **架构图示**：知识来源 → 处理流程 → 查询流程（Mermaid）
- ⚡ **快速开始**：3 步骤即可使用
- 🎯 **核心功能**：投资者文档检索、决策规则检索、混合检索
- 🚀 **高级用法**：多轮对话 RAG、按投资者过滤、NOFX 集成
- 💼 **实战场景**：
  - 场景 1：投资决策辅助（特斯拉估值分析）
  - 场景 2：市场情绪判断（VIX 极低信号）
  - 场景 3：风险检查（满仓风险评估）
- ⚙️ **性能优化**：Embedding 选择、向量库持久化、分块策略
- 💡 **最佳实践**：检索参数调优、多投资者融合、实时数据结合
- ❓ **常见问题**：速度慢、结果不相关、中文查询、NOFX 集成

**新增指南索引**：`guides/README.md`
- 5 个核心指南对比表
- 快速导航（按使用场景）
- 使用流程建议（Mermaid 流程图）
- 常见问题解答

#### 🎯 AI500 文档优化

**Prompt 优化**：`prompts/nofx_ai500_master.md`
- ✅ 添加版本元信息
- ✅ 新增 3 个实战场景：
  - 启动期进场（AIUSDT 案例）
  - 止盈时机（XYZUSDT 案例）
  - 不操作（ABCUSDT 案例）
- ✅ 精简重复内容（做多条件引用）

**映射文档优化**：`strategies/INVESTOR_MAPPING.md`
- ✅ ASCII 图表 → Mermaid 流程图
- ✅ 信号矩阵改为表格格式
- ✅ 6 项量化条件编号化

### 推文模板

```
Investment Masters Handbook v1.5.1 更新

📚 新增 RAG 完整指南（700+ 行）
🎯 架构图示、实战场景、性能优化全覆盖
🚀 AI500 文档优化：3 个真实交易场景
📊 Mermaid 图表替代 ASCII，移动端友好

从概念到实战，手把手教你用 RAG 检索投资大师智慧 👇
github.com/sou350121/investment-masters-handbook

#RAG #AI #投资 #OpenSource
```

---

## v1.5.0 - 2024-12-14

### 更新内容

#### 🎰 NOFX AI500 投资人适配

**核心功能**：将 5 位传奇投资人的智慧融合到 AI500 量化交易

| 大师 | 贡献 | AI500 应用 |
|------|------|------------|
| **George Soros** | 反身性理论 | OI↑+价格↑=自我强化拉盘 |
| **Stanley Druckenmiller** | 流动性至上 | OI排名=资金热度 |
| **Ed Thorp** | 凯利公式 | 置信度→仓位映射 |
| **Howard Marks** | 周期意识 | 不追高，等回调 |
| **James Simons** | 量化执行 | K线+OI信号矩阵 |

**新增文件**：
- `prompts/nofx_ai500_master.md` - AI500 专用融合 Prompt
- `strategies/INVESTOR_MAPPING.md` - 投资人适配说明
- `strategies/nofx_ai500_quantified.json` v2.0 - 策略配置

**信号矩阵**：
```
         价格上涨              价格下跌
      ┌─────────────┐      ┌─────────────┐
OI↑   │ ⭐⭐⭐⭐⭐     │      │ 🔴🔴🔴       │
      │ 主力做局      │      │ 空头入场     │
      └─────────────┘      └─────────────┘
      ┌─────────────┐      ┌─────────────┐
OI↓   │ ⚠️⚠️         │      │ 🔴🔴         │
      │ 主力出货      │      │ 资金离场     │
      └─────────────┘      └─────────────┘
```

### 推文模板

```
Investment Masters Handbook v1.5.0 更新

🎰 新增 AI500 量化大师 Prompt
🧠 融合 Soros、Druckenmiller、Thorp、Marks、Simons 五位传奇
📊 K线+OI 信号矩阵，置信度→仓位自动映射

把反身性、流动性、凯利公式变成 NOFX 可执行策略 👇
github.com/sou350121/investment-masters-handbook

#量化交易 #AI500 #NOFX #OpenSource
```

---

## v1.2.0 - 2024-12-13

### 更新内容

#### ✨ 用户体验优化
- 5 分钟快速入门指南
- 速查卡片 `guides/quick_reference.md`

#### 🛠️ 开发者工具
- 规则引擎 CLI `tools/rule_query.py`
- RAG 集成示例 `examples/rag_langchain.py`

#### 🇨🇳 中国投资人
- 段永平：买股票就是买公司、不懂不做

### 推文模板

```
Investment Masters Handbook v1.2.0 更新

✨ 新增 5 分钟快速入门 + 速查卡片
🛠️ 规则引擎 CLI + RAG 集成示例
🇨🇳 加入段永平（买股票就是买公司）
📊 232 条 IF-THEN 规则

github.com/sou350121/investment-masters-handbook

#投资 #AI #OpenSource
```

---

## v1.1.0 - 2024-12-12

### 更新内容

#### 🏗️ 工程化架构
- SSOT 架构 + CI 自动校验
- 187 条 IF-THEN 规则机读格式

#### 🇨🇳 中国投资人
- 邱国鹭：品牌/渠道/成本三把刀
- 冯柳：弱者体系、赔率优先于胜率

### 推文模板

```
Investment Masters Handbook v1.1.0 更新

✨ 新增 SSOT 架构 + CI 自动校验
🇨🇳 加入邱国鹭、冯柳两位中国投资大师
📊 187 条 IF-THEN 规则，一行命令即可导入NOFX

把巴菲特、芒格、达利奥的智慧变成可执行代码 👇
github.com/sou350121/investment-masters-handbook

#投资 #AI #OpenSource
```

---

## v1.0.0 - 2024-12-11

### 更新内容

#### 🎉 初始版本
- 14 位传奇投资人框架
- 200+ IF-THEN 决策规则
- 6 个 AI 角色 Prompt
- 决策路由系统

### 推文模板

```
🎉 Investment Masters Handbook 发布！

把巴菲特、芒格、索罗斯、达利奥等 14 位投资大师的智慧变成：
📊 200+ IF-THEN 决策规则
🤖 6 个 AI 角色 Prompt
🔀 智能决策路由

开源免费 👇
github.com/sou350121/investment-masters-handbook

#投资 #AI #OpenSource
```

---

## 统计汇总

| 版本 | 日期 | 投资人 | IF-THEN 规则 | Prompt 角色 |
|------|------|--------|--------------|-------------|
| v1.5.0 | 2024-12-14 | 17 | 232 | 7 |
| v1.2.0 | 2024-12-13 | 17 | 232 | 6 |
| v1.1.0 | 2024-12-12 | 16 | 187 | 6 |
| v1.0.0 | 2024-12-11 | 14 | 150+ | 6 |

---

## 推文写作指南

### 格式模板

```
Investment Masters Handbook vX.X.X 更新

[emoji] [核心功能 1]
[emoji] [核心功能 2]
[emoji] [核心功能 3]

[一句话总结价值] 👇
github.com/sou350121/investment-masters-handbook

#投资 #AI #OpenSource [其他相关标签]
```

### 常用 Emoji

| 类型 | Emoji |
|------|-------|
| 新功能 | ✨ 🚀 🎰 |
| 中国投资人 | 🇨🇳 |
| 数据/统计 | 📊 📈 |
| 工具 | 🛠️ 🔧 |
| AI/智能 | 🧠 🤖 |
| 警告/风险 | ⚠️ 🔴 |
| 成功/推荐 | ⭐ ✅ |
| 代码/开源 | 💻 |

### 标签建议

- 通用：`#投资 #AI #OpenSource`
- 量化：`#量化交易 #Quant`
- 加密：`#加密货币 #Crypto #NOFX #AI500`
- 价值投资：`#价值投资 #巴菲特`
