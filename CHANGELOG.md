# 更新日志 (Changelog)

本项目的所有重要更新都会记录在这里。

---

## [1.8.0] - 2025-12-27

### 🧠 深度会诊进化：NOFX 模式 & 角色化辩论

本次更新深度参考了 `nofx` 项目的多 Agent 协作与安全模式，将“大师深度会诊”从简单的 RAG 检索升级为具有角色个性的智能辩论引擎，并引入了“钥匙随身带”的安全架构。

#### 🛡️ NOFX 安全架构 (Bring Your Own Key)
- **钥匙随身带模式**：支持在前端直接填入 OpenRouter 或 OpenAI 的 API Key。
- **本地持久化**：API Key 仅加密保存在浏览器的 `localStorage` 中，后端不存储，请求时通过 `Authorization: Bearer` 透传，确保隐私安全。
- **智能防呆**：前端能自动识别 `sk-or-...` 等 Key 类型并给出正确的配置提示。
- **后端动态加载**：后端 RAG 服务现在支持动态切换 API Key，实现真正的多租户/单兵作战兼容。

#### 🎭 角色化辩论引擎 (Expert Personas)
- **人格映射**：为 20+ 位投资大师配置了专属的“人格卡片”（如 Ray Dalio 是宏观分析师，Warren Buffett 是价值发现者）。
- **结构化推理**：采用 `<reasoning>` 思考链 + `<json>` 定量输出的辩论模式。
- **定量裁决进化**：委员会不再只给文字建议，还会输出 `final_multiplier_offset` (-0.50 到 +0.50)，直接对风险乘数进行定量微调。

#### 🎨 深度会诊 UX 增强
- **会诊工作台**：重构右侧聊天抽屉，新增醒目的“普通问答”与“大师深度会诊”切换按钮。
- **Token 登录中心**：新增 NOFX 风格的登录面板，支持保存/清除 Access Token。
- **交互式 Tooltip**：新增悬浮提示功能，解释 Token 与 API Key 的安全存储机制。
- **响应式加载**：后端向量库改为异步初始化，秒开网页，无需等待大数据量索引加载。

#### 🛠️ 工程与核心工具
- **LLM Bridge 增强**：`llm_bridge.py` 新增对 Claude (Anthropic API) 的原生支持，并优化了 JSON 提取算法（兼容各种 Markdown 围栏）。
- **并发服务优化**：FastAPI 后端引入 `asyncio.to_thread` 处理耗时的向量库加载，显著提升服务可用性。

---

## [1.8.1] - 2025-12-28

### 🎯 Deep Reasoning 输出更可执行：一级/二级输出

- **/api/rag/ensemble 结构升级**：输出拆分为两层：
  - `primary`：四类资产目标配比（stocks/bonds/gold/cash，sum=100）+ 一句话结论 + `confidence`
  - `secondary`：保留原有辩论/溯源输出（experts/opinions/citations/ensemble_adjustment/metadata）
- **Web UI 默认展示一级输出**：一眼看到“股/债/金/现金”目标配比，二级输出可展开查看证据链与分歧。
- **测试更新**：`tests/test_ensemble.py` 覆盖 tiered response 结构与配比 sum=100 约束。

### 📚 文档与可读性

- **README 排版升级**：参考 TradeVoyage 风格，强化导航、快速开始、API 段落与项目结构展示（并同步修正投资人数/规则数等统计口径）。

## [1.8.2] - 2025-12-29

### 📈 Sortino 优化：默认参数“出厂即最优”（以 SHY 为债券底盘）

- **默认债券 proxy 调整**：回测与执行代理默认使用 `SHY`（短久期国债）替代 `IEF`，作为更稳健的 bonds 底盘（可用 `--tickers` 覆盖）。
- **allocator 参数写入配置**：将最佳 Sortino 网格搜索结果写入 `config/reasoning_config.yaml` 的 `allocation_policy`（objective=sortino），并同步更新 neutral base。
- **可解释性增强**：`/api/rag/ensemble` 的 `secondary.metadata` 新增 `primary_allocator_policy` 快照，方便前端展示“系统用的到底是哪组参数”。

### 🎨 Web 前端同步升级

- **Token 登录修复**：允许保存 `sk-or-...` 等 LLM API Key（NOFX BYOK），并提示其仅本地保存、请求时透传后端不落盘。
- **执行代理更明确**：一级输出旁展示默认 ETF 代理（SPY/SHY/GLD/BIL），并在二级输出中展示 allocator policy 与 `disagreement_score`。

## [1.7.0] - 2025-12-23

### 🚀 重磅更新：场景沙盒 (Scenario Sandbox) & 首页 UX 革命

本次更新将 IMH 从一个静态文档库彻底转变为一个功能完备的交互式投研平台，并极大地优化了在复杂环境下的运行稳定性。

#### 🛡️ 场景沙盒 (Scenario Sandbox)
- **预设场景翻倍**：从 3 个扩展至 **8 个** 经典历史压力情景（如 2008 金融危机、2020 疫情、2022 加息潮等）。
- **自动化回归校验**：实现 `api/policy/validate_all` 接口，支持一键对比所有场景的实际输出与大师原则的预期值。
- **智能交互**：
  - 新增场景**搜索与标签过滤**功能。
  - **Tooltip 预览**：悬停即可查看各场景的详细背景与期望指标。
  - **一键加载调试**：点击场景 Chip 自动填充参数并切换至护栏调试页。

#### 🎨 现代化首页 UX 重构
- **Tabs 标签化导航**：引入吸顶式 Tabs 导航栏（大师列表、场景沙盒、风控护栏、关于手册），彻底告别单页滚动。
- **Hero 搜索中心**：新增沉浸式头部设计与大尺寸搜索框，显著提升首屏品牌感与易用性。
- **大师名录增强**：重新设计了 17 位大师卡片，增加 HSL 色相哈希头像背景，支持更清晰的简介展示。
- **题库中心**：按类别（选股、宏观、风险、配置）整理了大师题库，支持一键点击提问。

#### 🛠️ 工程与系统稳定性
- **端口迁移 (8000 -> 8001)**：彻底解决了与其他交易系统的端口冲突问题，默认端口调整为 8001。
- **审计日志体系**：正式启用 `logs/policy_gate_audit.jsonl`，记录每一次 Policy Gate 的决策链路。
- **健康检查别名**：新增 `/api/health` 别名，提升了前端负载探测的兼容性。
- **CI/CD 修复**：解决了 GitHub Actions 运行中的多项脚本缺失与断链错误，保证了自动化部署的稳健性。

---

## [1.6.5] - 2025-12-14

### ✨ 视觉与数据大升级

本次更新显著提升了 Web 界面的专业度与信息密度，并丰富了大师的背景资料。

#### 🎨 现代化 UI 重构
- **大师头像集成**：为核心投资大师配上了精选头像，支持本地缓存与自动回退机制。
- **高密度布局**：大师目录页升级为一行 5 列的紧凑网格，适配大屏显示。
- **精致视觉风格**：引入 Google Sans 字体、Hover 抬升效果、轻量渐变背景以及更细腻的阴影处理。
- **详情页海报化**：重构了大师详情页头部，采用沉浸式渐变背景与头像展示。

#### 📊 数据字段增强
- **新增字段**：在 `investor_index.yaml` 中为 17 位大师新增了 `nationality` (国籍) 与 `intro_zh` (中文简介)。
- **背景资料丰富**：现在每个卡片均展示 **国籍 · 代表公司** 以及 **一句话精简介绍**，快速建立第一印象。

#### 🛠️ 工程与自动化
- **头像抓取脚本**：新增 `tools/fetch_avatars_wikipedia.py`，支持从 Wikipedia/Wikidata 自动抓取并处理大师头像。
- **多路径部署兼容**：修复了在 `/imh` 子路径下部署时静态资源（头像）加载失败的问题，实现更稳健的路径感知。

---

## [1.6.0] - 2024-12-14

### 🚀 重大更新：IMH Web + RAG 服务化

本项目现在拥有了一个现代化的 Web 界面和生产级的 RAG 检索 API，大幅降低了非技术用户的使用门槛。

#### 🌐 现代化 Web 界面
- **大师目录**：Google 风格的搜索与卡片式布局，支持按姓名、风格、擅长领域模糊搜索。
- **大师详情页**：
  - **Overview**：渲染 17 位大师的 Markdown 投资哲学与框架。
  - **Trading Rules**：将 232 条规则按“入场”、“出场”、“风控”进行结构化分类展示。
  - **Ask AI**：深度集成 RAG 问答面板。
- **技术栈**：Next.js 15 (App Router), Material UI (MUI), TypeScript.

#### 🧠 RAG 服务化 (FastAPI)
- **生产级 API**：新增 `services/rag_service.py`，提供高性能的检索接口。
- **自动初始化**：启动时自动加载或构建持久化向量库。
- **多维过滤**：支持通过 API 按投资者 ID、来源类型（文档/规则）、规则类型（kind）进行预过滤。
- **精确溯源**：返回结果包含 `start_index` 字符偏移、`chunk_id`、`rule_id` 以及 `similarity_estimate`。

#### 🛠️ 架构改进
- **核心逻辑剥离**：将 RAG 核心功能抽离至 `tools/rag_core.py`，实现 CLI 与 API 共享代码。
- **Next.js 代理**：Web 路由通过 `/api/rag/query` 代理本地 Python 服务，解决跨域并统一错误处理。

### 🧼 工程卫生
- 修复了 `guides/rag_guide.md` 等文档中的拼写错误。
- 统一了全仓库的 LF 换行符，解决了跨平台协作的 Diff 噪音问题。

---

## [1.5.1] - 2024-12-14

### 📚 文档增强

#### RAG 完整指南
- **新增** `guides/rag_guide.md` - 700+ 行完整 RAG 使用指南
  - RAG 架构图（Mermaid）
  - 快速开始（3 步骤）
  - 核心功能：投资者文档检索、决策规则检索、混合检索
  - 高级用法：多轮对话、按投资者过滤、NOFX 集成
  - 3 个实战场景（投资决策、市场情绪、风险检查）
  - 性能优化（Embedding 选择、持久化、分块策略）
  - 最佳实践 + 常见问题

- **新增** `guides/README.md` - 指南目录索引
  - 5 个核心指南对比表
  - 使用流程建议（Mermaid 流程图）
  - 常见问题解答

#### AI500 文档优化
- **优化** `prompts/nofx_ai500_master.md`
  - 添加版本元信息（v1.5.0 | 2024-12-14）
  - 新增 3 个实战场景：启动期进场、止盈时机、不操作
  - 精简重复内容（做多条件引用 Simons 章节）
  - 433 行 → 结构更清晰

- **优化** `strategies/INVESTOR_MAPPING.md`
  - 添加版本元信息
  - 决策流程：ASCII 图 → Mermaid 流程图 + 表格
  - 信号矩阵：ASCII 图 → 表格格式
  - 6 项量化条件：改为编号表格

#### 引用更新
- **更新** `README.md` - 添加 RAG 指南链接和核心特性
- **更新** `examples/README.md` - 添加指向 RAG 指南的引用

### 🎯 用户体验提升

| 改进项 | 说明 |
|--------|------|
| **可读性** | Mermaid 图表替代 ASCII，移动端友好 |
| **实战性** | 3 个真实交易场景示例 |
| **完整性** | RAG 从概念到实战的全流程指南 |
| **导航性** | guides/README.md 帮助快速找到所需文档 |

### 📊 统计
- 新增文档：2 个（rag_guide.md, guides/README.md）
- 优化文档：4 个
- 新增 Mermaid 图表：3 个
- 新增实战场景：3 个

### 🔗 新增文件
```
guides/rag_guide.md          # RAG 检索增强生成完整指南 (700+ 行)
guides/README.md             # 指南目录索引
```

### 🔐 安全与可运维（今日追加）

- **移除 NOFX 硬编码凭证**：`strategies/nofx_ai500_quantified.json`
  - 将 URL 中的 `auth` 参数改为环境变量占位符：`${NOFX_AUTH_TOKEN}`
  - 新增安全文档：`docs/SECURITY.md`（环境变量设置 + Token 轮换指南）
  - 新增策略说明：`strategies/README.md`（如何使用环境变量占位符）

### 🧰 RAG 示例可用性（今日追加）

- **RAG 示例补齐持久化加载**：`examples/rag_langchain.py`
  - 新增 `--load/-l`：加载已保存的 Chroma 向量库（无需重复建库）
  - 依赖检查补齐 `sentence-transformers`，并同步更新示例文档

### 🎯 检索质量提升（今日追加）

- **投资者文档分块 + 引用溯源**：`examples/rag_langchain.py`
  - 对 `investors/*.md` 做标题/段落分块（chunking）
  - 输出增加 `source_type / chunk_id / title_hint`，结果可定位可溯源
- **RAG CLI 高级增强 (v1.5.1)**：
  - **字符级精准溯源**：记录并显示 `start_index`（片段在原文中的偏移位置）
  - **多维结果过滤**：新增 `--investor`、`--source-type`、`--kind` 参数
  - **分块粒度控制**：支持 `--chunk-size` 和 `--chunk-overlap` 自定义
  - **机器可读格式**：新增 `--format json` 输出支持，方便 Agent 集成

### 🧼 工程一致性（今日追加）

- **跨平台换行/格式规范**：新增 `.gitattributes`、`.editorconfig`
  - 统一 LF 行尾，减少 CRLF/LF 引发的“整文件 diff”

---

## [1.5.0] - 2024-12-14

### 🚀 新增

#### NOFX AI500 投资人适配
- **AI500 量化大师 Prompt**：`prompts/nofx_ai500_master.md`
  - 融合 5 位传奇投资人核心智慧
  - Soros 反身性 → OI+价格自我强化机制
  - Druckenmiller 流动性 → OI 排名=资金热度
  - Thorp 凯利公式 → 置信度→仓位映射
  - Marks 周期意识 → 不追高，等回调
  - Simons 量化执行 → K线+OI 信号矩阵

- **投资人映射文档**：`strategies/INVESTOR_MAPPING.md`
  - 五位大师原始理念 → AI500 适配规则
  - 决策流程整合图
  - JSON 输出示例

- **策略配置升级**：`strategies/nofx_ai500_quantified.json` v2.0
  - 新增 `investor_mapping` 元数据
  - prompt_sections 融合五位大师标注
  - 置信度→仓位映射表

#### 路由配置
- **AI500 关键词模式**：`config/router_config.yaml`
  - 新增 `ai500` 模式（AI500/NOFX/OI排名/做局/拉盘）
  - 新增 `nofx_ai500_master` Prompt 角色
  - 快速路由：AI500/OI排名/K线量化问题

### 📊 统计
- Prompt 角色：6 → 7 个（+AI500 量化大师）
- 策略配置版本：1.1 → 2.0
- 投资人适配：5 位大师 → AI500 量化场景

### 🔗 新增文件
```
prompts/nofx_ai500_master.md      # AI500 专用融合 Prompt
strategies/INVESTOR_MAPPING.md    # 投资人适配说明
```

---

## [1.2.0] - 2024-12-13

### 🚀 新增

#### 用户体验优化
- **5 分钟快速入门**：README 新增可折叠的场景化入门指南
  - 新手入门推荐
  - 宏观/择时方向
  - 量化/系统化方向
  - AI 系统集成快速通道

- **速查卡片**：`guides/quick_reference.md`
  - 一页纸掌握 17 位大师核心智慧
  - 按场景速查（选股/判断大盘/风控）
  - 指标速查表
  - 决策流程清单

#### 开发者工具
- **规则引擎 CLI**：`tools/rule_query.py`
  - 按场景查询（市场恐慌/选股/风控...）
  - 按投资者查询
  - 按关键词搜索
  - 支持 JSON 输出
  - `--list-scenarios` / `--list-investors` 速查

- **RAG 集成示例**：`examples/rag_langchain.py`
  - LangChain + ChromaDB 完整示例
  - 交互模式支持
  - 简化版关键词搜索（无依赖）

#### 中国投资人 🇨🇳
- **段永平** (`investors/duan_yongping.md`)
  - 买股票就是买公司
  - 不懂不做、本分
  - 商业模式分析框架
  - 20 条 IF-THEN 决策规则

### 📊 统计
- 投资大师：16 → 17 位（+段永平）
- 中国投资人：2 → 3 位
- IF-THEN 规则：212 → 232 条（+20）

---

## [1.1.0] - 2024-12-12

### 🚀 新增

#### 工程化架构（SSOT + CI）
- **SSOT 架构**：`config/investor_index.yaml` 成为单一数据源
- **机读规则**：新增 `config/decision_rules.generated.json`（187 条 IF-THEN 规则）
- **自动生成**：`docs/INVESTORS.generated.md` 从 YAML 自动生成
- **CI 四件套**：GitHub Actions 自动校验
  - 链接检查 (`check_links.py`)
  - Front Matter 校验 (`validate_front_matter.py`)
  - 路由冲突检测 (`check_router_config.py`)
  - 敏感信息扫描 (`scan_sensitive.py`)
- **生成脚本**：`scripts/generate_artifacts.py` 一键生成派生文档

#### 中国投资人 🇨🇳
- **邱国鹭** (`investors/qiu_guolu.md`)
  - 品牌/渠道/成本三把刀
  - 得寡头者得天下
  - 便宜是硬道理
  - 12 条 IF-THEN 决策规则
  
- **冯柳** (`investors/feng_liu.md`)
  - 弱者体系（假设市场是对的）
  - 赔率优先于胜率
  - 逆向左侧买入
  - 不择时、不止损
  - 14 条 IF-THEN 决策规则

#### 文档
- **贡献指南**：`docs/CONTRIBUTING.md`
  - 添加新投资人的 4 步标准流程
  - YAML 字段规范
  - Markdown 模板
  - DECISION_RULES 格式说明

### 📝 改进

#### README.md 大升级
- GitHub 徽章（CI 状态、License、投资人数）
- ASCII 架构图
- 16 位投资人速览表
- 核心 IF-THEN 规则示例
- 4 种快速开始方式
- Costco 实战案例摘要
- 项目结构树
- NOFX 集成简化（一行 curl 命令）

#### 文件结构重组
- `config/`：SSOT 配置文件
- `docs/`：使用文档
- `guides/`：核心指南
- `investors/`：投资人框架
- `prompts/`：AI 角色 Prompt
- `scripts/`：自动化脚本

### 🔧 技术改进
- Python 脚本兼容 3.6+
- `.gitignore` 排除 `__pycache__`
- 统一 Front Matter 格式

---

## [1.0.0] - 2024-12-11

### 🎉 初始版本

- 14 位传奇投资人框架
  - 价值派：Buffett, Munger, Lynch, Klarman
  - 宏观派：Dalio, Druckenmiller, Soros
  - 周期派：Marks, Burry
  - 量化派：Simons, Thorp, Asness
  - 激进派：Icahn
  - 接班人：Abel
- 200+ IF-THEN 决策规则
- 6 个 AI 角色 Prompt
- 决策路由系统
- LLM System Prompt 模板

---

## 统计

| 版本 | 投资人数 | IF-THEN 规则 | Prompt 角色 | 核心指南 | 文件数 |
|------|----------|--------------|-------------|----------|--------|
| **1.7.0** | **17** | **232** | **7** | **8** | **68+** |
| 1.7.0 | 17 | 232 | 7 | 8 | 68+ |
| 1.6.5 | 17 | 232 | 7 | 5 | 63+ |
| 1.6.0 | 17 | 232 | 7 | 5 | 52+ |
| 1.5.1 | 17 | 232 | 7 | 5 | 52+ |
| 1.5.0 | 17 | 232 | 7 | 3 | 50+ |
| 1.2.0 | 17 | 232 | 6 | 3 | 45+ |
| 1.1.0 | 16 | 187 | 6 | 2 | 40+ |
| 1.0.0 | 14 | 150+ | 6 | 1 | 30+ |

---

## 链接

- **GitHub**：https://github.com/sou350121/investment-masters-handbook
- **机读规则**：https://raw.githubusercontent.com/sou350121/investment-masters-handbook/main/config/decision_rules.generated.json

