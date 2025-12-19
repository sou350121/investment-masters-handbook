# 发布日志 & 推文模板

> 每次更新的详细记录和社交媒体推文模板

---

## v1.6.0 - 2024-12-14

### 更新内容

#### 🌐 现代化 Web 界面发布
- **全平台支持**：基于 Next.js 15 构建，完美适配桌面与移动端。
- **大师目录**：Google 风格搜索，快速定位 17 位传奇投资人。
- **结构化展示**：将交易规则按 `kind`（入场/出场/风控）分类展示，告别文档堆砌。
- **Ask AI 实验室**：在网页端直接对大师提问，集成最新 RAG 技术。

#### 🧠 RAG 生产级 API (FastAPI)
- **高性能后端**：新增 Python FastAPI 服务，支持异步并发检索。
- **元数据增强**：检索结果带 `start_index` 精确偏移量，支持“字符级”引用追踪。
- **自动持久化**：向量库自动构建并保存至 `./vectorstore`，启动秒开。

#### 🛠️ 开发者工程化升级
- **核心剥离**：RAG 逻辑抽离至 `tools/rag_core.py`，实现 CLI 与 API 共用。
- **跨平台一致性**：强制 LF 行尾规范，消除无意义的 Git Diff。

### 推文模板（单条版）

```
Investment Masters Handbook v1.6.0 重磅更新！🚀

本想做个文档库，结果不小心做出了个 Web App + RAG API：

🌐 现代化 Web 界面：Google 风格搜索 17 位大师智慧
🧠 RAG 智能问答：支持字符级溯源，拒绝 AI 幻觉
📊 规则结构化：入场/出场/风控规则分类一目了然
🛠️ 生产级 API：FastAPI 驱动，轻松集成交易机器人

复现传奇大脑，让投资更有据可查 👇
github.com/sou350121/investment-masters-handbook

#AI投资 #RAG #Nextjs #OpenSource
```

---

## v1.5.1 - 2024-12-14

### 更新内容

#### 🔐 安全与可运维（今日追加）

- **移除 NOFX 硬编码 Token**
  - `strategies/nofx_ai500_quantified.json` 中的 URL 认证参数改为环境变量占位符：`${NOFX_AUTH_TOKEN}`
  - 新增安全文档 `docs/SECURITY.md`：解释“为什么不能硬编码 token”、以及 Windows/macOS/Linux 的环境变量设置与 Token 轮换流程
  - 新增 `strategies/README.md`：策略目录的环境变量使用说明

#### 🧰 RAG 示例可用性（今日追加）

- `examples/rag_langchain.py` 新增 `--load/-l`：加载已保存的向量库（避免每次重建）
- 依赖检查补齐 `sentence-transformers`，并同步更新：
  - `examples/README.md`
  - `guides/rag_guide.md`

#### 🎯 RAG 检索质量提升（今日追加）

- 投资者文档分块（chunking）：按标题/段落切分 `investors/*.md`
- 输出结果附带引用溯源信息：`source + rule_id/chunk_id + title_hint`（可定位原文片段）
- **RAG CLI 增强功能 (v1.5.1)**：
  - **字符偏移溯源**：支持显示精确到字符的 `start_index`
  - **高级过滤器**：可按大师 ID、规则类型、来源类型进行组合过滤
  - **JSON 格式支持**：方便第三方工具集成
  - **分块动态配置**：可根据需求微调检索片段的长度

#### 🧼 工程一致性（今日追加）

- 新增 `.gitattributes`、`.editorconfig`：统一 LF 行尾与基础格式，减少跨平台无意义 diff

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

### 推文模板（Thread 格式）

**1/ 引子 - 什么是 RAG**
```
Investment Masters Handbook v1.5.1 更新 🎉

新增 700+ 行 RAG 完整指南

什么是 RAG？为什么你的投资 AI 需要它？

一条 Thread 讲清楚 👇

#RAG #AI #投资 #OpenSource
```

**2/ 问题 - 传统 LLM 的局限**
```
2/ 传统 LLM 的三大痛点：

❌ 幻觉：编造看似专业的投资建议
❌ 过时：训练数据截止日期前的知识
❌ 通用：缺乏专业投资人的深度智慧

你问它"特斯拉值得买吗？"
它可能给你一堆通用理论，但没有巴菲特的能力圈检查，也没有 Lynch 的 PEG 计算。
```

**3/ 什么是 RAG**
```
3/ RAG = Retrieval-Augmented Generation
    检索 + 增强 + 生成

简单说：
在 AI 回答前，先从你的知识库里找相关内容

传统 LLM：问题 → AI → 答案
RAG 增强：问题 → 检索知识库 → AI + 知识 → 答案

知识库 = 17 位投资大师的智慧 📚
```

**4/ RAG 的价值**
```
4/ RAG 带来什么？

✅ 准确性：基于真实文档，可溯源
✅ 时效性：知识库实时更新
✅ 专业性：17 位大师 + 232 条规则
✅ 可控性：你决定 AI 学什么

举例：
你问"市场暴跌怎么办？"
RAG 会检索：
- Marks 的周期位置判断
- Buffett 的恐慌时买入
- Klarman 的安全边际
```

**5/ 实战场景 1 - 投资决策**
```
5/ 实战场景 1：投资决策辅助

问题："特斯拉 P/E 60，PEG 1.8，值得买吗？"

RAG 检索会返回：
📊 Lynch 的 PEG < 1 规则（警告！）
🎯 Buffett 的能力圈检查
🧠 Munger 的估值偏误清单

AI 基于这些大师智慧给出建议，而不是瞎猜。
```

**6/ 实战场景 2 - 风险检查**
```
6/ 实战场景 2：风险检查

问题："我想满仓一只成长股"

RAG 检索会返回：
⚠️ Thorp 的凯利公式（仓位不超过 25%）
🛡️ Klarman 的安全边际要求
🚨 Munger 的决策偏误清单

相当于 3 位大师同时给你风险提醒！
```

**7/ 如何使用 - 3 步上手**
```
7/ 如何使用？3 步上手

步骤 1：安装依赖
pip install langchain chromadb pyyaml

步骤 2：单次查询
python examples/rag_langchain.py "市场恐慌怎么办？"

步骤 3：交互模式
python examples/rag_langchain.py --interactive

就这么简单！
```

**8/ 高级用法 - 按投资者过滤**
```
8/ 高级用法：按投资者过滤

只想听巴菲特的建议？

vectorstore.similarity_search(
    "护城河分析",
    filter={"investor_id": "warren_buffett"}
)

或者只看宏观大师的观点：
- Soros（反身性）
- Druckenmiller（流动性）
- Dalio（债务周期）
```

**9/ NOFX AI500 集成**
```
9/ 量化交易者的福音 🎰

RAG 已集成到 NOFX AI500 策略

实时检索：
- Soros 反身性理论（OI+价格自我强化）
- Druckenmiller 流动性（OI 排名=资金热度）
- Thorp 凯利公式（置信度→仓位）

把大师智慧变成可执行的交易信号！
```

**10/ 性能优化建议**
```
10/ 性能优化 Tips ⚡

🔸 持久化向量库（首次慢，后续快）
🔸 使用 --rules-only（只加载规则，更快）
🔸 选择合适的 Embedding 模型：
  - 开发：HuggingFace MiniLM（免费）
  - 生产：OpenAI ada-002（高精度）
  - 中文：BGE-large-zh（中文优化）
```

**11/ 无需 RAG 的简化方案**
```
11/ 不想搭 RAG？还有简化方案

方案 1：直接加载规则
import json
rules = json.load("decision_rules.json")

方案 2：作为 System Prompt
system_prompt = open("llm_summary.md").read()

方案 3：关键词搜索
simple_keyword_search("护城河")

选择适合你的！
```

**12/ CTA - 完整指南**
```
12/ 完整的 RAG 指南在这里 👇

✅ 700+ 行完整教程
✅ 架构图 + 代码示例
✅ 3 个实战场景
✅ 性能优化 + 常见问题

github.com/sou350121/investment-masters-handbook/blob/main/guides/rag_guide.md

把 17 位投资大师的智慧装进你的 AI 🚀

#RAG #AI #投资 #OpenSource
```

---

### 推文模板（单条版）

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
