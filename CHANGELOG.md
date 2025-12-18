# 更新日志 (Changelog)

本项目的所有重要更新都会记录在这里。

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
| **1.5.1** | **17** | **232** | **7** | **5** | **52+** |
| 1.5.0 | 17 | 232 | 7 | 3 | 50+ |
| 1.2.0 | 17 | 232 | 6 | 3 | 45+ |
| 1.1.0 | 16 | 187 | 6 | 2 | 40+ |
| 1.0.0 | 14 | 150+ | 6 | 1 | 30+ |

---

## 链接

- **GitHub**：https://github.com/sou350121/investment-masters-handbook
- **机读规则**：https://raw.githubusercontent.com/sou350121/investment-masters-handbook/main/config/decision_rules.generated.json

