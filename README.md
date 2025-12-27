## Investment Masters Handbook (IMH)

[![CI](https://github.com/sou350121/investment-masters-handbook/actions/workflows/quality.yml/badge.svg)](https://github.com/sou350121/investment-masters-handbook/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Investors](https://img.shields.io/badge/Investors-26-green.svg)
![Rules](https://img.shields.io/badge/Rules-299-blue.svg)

> **把投资大师的公开决策哲学，转化为可检索、可路由、可执行的 IF-THEN 规则库**  
> 支持 RAG 检索 · LLM System Prompt · AI 委员会（NOFX 风格）· Policy Gate 风控护栏

- **核心产品说明书 (Product Manual)**: [`PRODUCT_MANUAL.md`](PRODUCT_MANUAL.md)
- **速查卡片 (Quick Reference)**: [`guides/quick_reference.md`](guides/quick_reference.md)
- **更新日志**: [`CHANGELOG.md`](CHANGELOG.md)

---

## Navigation

- [5 分钟快速入门](#-5-分钟快速入门)
- [核心能力](#-核心能力)
- [Web UI / API](#-web-ui--api)
- [大师深度会诊（一级输出/二级输出）](#-大师深度会诊一级输出二级输出)
- [投资大师速览](#-投资大师速览)
- [项目结构](#-项目结构)
- [工具与常用命令](#-工具与常用命令)
- [安全与 Token](#-安全与-token)
- [免责声明](#-免责声明)

---

## ⚡ 5 分钟快速入门

### 方式一：Web 界面（推荐）

```bash
cd investment-masters-handbook
python -m pip install -r requirements.txt

cd web
npm install
npm run build

cd ..
python services/rag_service.py
```

打开浏览器访问：
- `http://localhost:8001/imh/`（推荐：前端构建默认 `basePath=/imh`）
- 或 `http://localhost:8001/`（后端同时挂载了 `/` 与 `/imh` 以兼容）

### 方式二：只要规则 JSON（给 Agent/外部系统）

```bash
curl -sL "https://raw.githubusercontent.com/sou350121/investment-masters-handbook/main/config/decision_rules.generated.json" -o rules.json
```

---

## 🌟 核心能力

| 能力 | 说明 |
|------|------|
| **299 条 IF-THEN 规则** | 自动生成的机读规则：`config/decision_rules.generated.json` |
| **26 位投资大师** | 覆盖价值、宏观、周期、量化、事件、硅谷等多风格 |
| **SSOT 架构** | `config/investor_index.yaml` 为结构化单一数据源（索引/路由/矩阵） |
| **RAG 检索** | 向量化规则与人物文档，支持语义检索 + rerank |
| **大师深度会诊** | `/api/rag/ensemble`：NOFX 风格辩论 + 定量裁决 + 可视化溯源 |
| **Policy Gate 风控护栏** | `/api/policy/gate`：regime/scenario/guardrails + 场景回归校验 |

---

## 🧱 Web UI / API

### 1) 健康检查

- `GET /health`：向量库就绪状态、doc_count、持久化目录大小等

### 2) 普通问答（RAG）

- `POST /api/rag/query`：语义检索（可选 Bearer token，取决于后端配置）

### 3) 大师深度会诊（IC Engine）

- `POST /api/rag/ensemble`：**需要** `Authorization: Bearer <token>`  
  - token 可以是 `IMH_API_TOKEN`（实例口令），也可以直接用 `sk-...` / `or-...` 作为 LLM key（NOFX 风格）。

---

## 🏛️ 大师深度会诊（一级输出/二级输出）

为了解决“我真正关心的是股/债/金/现金配比”，`/api/rag/ensemble` 输出被拆为两层：

- **一级输出 (`primary`)**：四类资产目标配比 + 一句话结论 + 置信度
- **二级输出 (`secondary`)**：原始辩论与证据链（experts/opinions/citations/ensemble_adjustment/metadata）

> Web UI 会优先展示一级输出，二级输出可展开查看溯源。

---

## 📊 投资大师速览

### 🔬 价值投资派
| 投资人 | 核心一句话 | 适用场景 |
|--------|-----------|----------|
| [Warren Buffett](investors/warren_buffett.md) | 好公司 + 好价格 + 长期持有 | 护城河、安全边际 |
| [Charlie Munger](investors/charlie_munger.md) | 多元思维模型、避免愚蠢 | 决策品质、排除偏误 |
| [Peter Lynch](investors/peter_lynch.md) | 买你懂的、PEG < 1 | 成长股筛选 |
| [Seth Klarman](investors/seth_klarman.md) | 深度价值、极端耐心 | 冷门资产、特殊情况 |

### 🌍 宏观择时派
| 投资人 | 核心一句话 | 适用场景 |
|--------|-----------|----------|
| [Ray Dalio](investors/ray_dalio.md) | 经济四象限 + 风险平价 | 资产配置、周期定位 |
| [Stanley Druckenmiller](investors/stanley_druckenmiller.md) | 流动性追踪、集中重注 | 择时、方向性交易 |
| [George Soros](investors/george_soros.md) | 反身性、攻击失衡 | 货币/宏观极端事件 |

### 🔄 周期/逆向派
| 投资人 | 核心一句话 | 适用场景 |
|--------|-----------|----------|
| [Howard Marks](investors/howard_marks.md) | 周期极端时逆向、控制下档 | 信用周期、恐慌抄底 |
| [Michael Burry](investors/michael_burry.md) | 逆向深挖、不从众 | 特殊情况、做空泡沫 |

### 🤖 量化/系统化派
| 投资人 | 核心一句话 | 适用场景 |
|--------|-----------|----------|
| [James Simons](investors/james_simons.md) | 数据驱动、无情绪 | 量化策略设计 |
| [Ed Thorp](investors/ed_thorp.md) | 凯利公式 + 套利 | 仓位管理、期权定价 |
| [Cliff Asness](investors/cliff_asness.md) | 因子投资、价值+动量 | 因子策略、组合构建 |

### 🇨🇳 中国价值投资派
| 投资人 | 核心一句话 | 适用场景 |
|--------|-----------|----------|
| [邱国鹭](investors/qiu_guolu.md) | 品牌渠道成本三把刀、得寡头者得天下 | A股选股、行业选择 |
| [冯柳](investors/feng_liu.md) | 弱者体系、赔率优先、左侧买入 | 逆向投资、困境反转 |
| [段永平](investors/duan_yongping.md) | 买股票就是买公司、不懂不做 | 商业模式分析、长期持有 |

---

## ⚡ 核心 IF-THEN 规则示例

### 买入决策

```
IF 盈余收益率 > 10Y国债 × 1.5 AND 护城河完好
   THEN 考虑买入
   BECAUSE 提供安全边际，回报优于无风险利率 (Buffett)

IF PEG < 1 AND 增速可持续 5年+
   THEN 成长股机会
   BECAUSE 成长被低估 (Lynch)

IF 股价因短期利空下跌 > 30% AND 长期逻辑未变
   THEN 逆向机会
   BECAUSE 人弃我取 (邱国鹭)

IF 赔率 > 3:1 AND 胜率 > 30%
   THEN 值得下注
   BECAUSE 赔率优先于胜率 (冯柳)
```

### 卖出/风控

```
IF 护城河被侵蚀 AND 无改善迹象
   THEN 卖出
   BECAUSE 便宜会更便宜 (Buffett)

IF 买入论点不再成立
   THEN 立即止损
   BECAUSE 生存第一 (Soros)

IF 信用利差极窄 + VIX极低 + 散户疯狂入场
   THEN 提高现金比例
   BECAUSE 周期过热信号 (Marks)
```

---

## 🚀 快速开始

### 方式一：Web 界面 (推荐)
```bash
cd investment-masters-handbook
python -m pip install -r requirements.txt

cd web
npm install
npm run build

cd ..
python services/rag_service.py
```
打开浏览器访问：
- `http://localhost:8001/imh/`（推荐，前端构建时固定 `basePath=/imh`）
- 或 `http://localhost:8001/`（后端同时挂载了 `/` 与 `/imh`，便于兼容）

> 说明：`web` 采用静态导出（Next `output: "export"`），所以推荐用后端 FastAPI 直接托管 `web/out`。

#### 验证：Policy Gate 场景沙盒 (Scenario Sandbox)
- 打开 Web UI → 展开 **Policy Gate** 面板
- 在 **🚀 场景沙盒** 点击任一场景（如“2008 极度恐慌”）
- 点击 **生成 Policy Gate 护栏**
- 你会看到该场景的 ✅/❌ 校验报告（按 `config/scenarios.yaml` 的 expectations 对比）

#### 常见问题：点击“运行全量回归”提示失败 / 场景加载不到
如果页面提示：
- `GET /api/policy/scenarios 失败（HTTP 404）`
- 或 `POST /api/policy/validate_all 失败（HTTP 404）`

说明你当前访问的这个站点背后的后端 **不是 IMH 的 `services/rag_service.py`**（例如端口被其它项目占用）。

快速自检：
- IMH 后端的 `GET /health` 应返回：`{"status":"ok","vectorstore_ready": ...}`

解决：
- 停止占用端口的服务后运行：`python services/rag_service.py`
- 或设置不同端口运行：`$env:PORT=8001; python services/rag_service.py`，然后访问 `http://localhost:8001/imh/`

### 方式二：AI System Prompt
```python
# 直接使用 guides/llm_summary.md 作为 System Prompt
with open("guides/llm_summary.md") as f:
    system_prompt = f.read()
```

### 方式一（可选）：前端开发模式（仅在你要改 UI 时）
> 注意：本仓库前端默认 `basePath=/imh`，且 Policy Gate 面板会直接请求后端的 `/api/policy/*`。
> 推荐仍然通过 `python services/rag_service.py` 提供 API，再按需修改 Next 的代理/路由规则做本地联调。

### 方式三：RAG 检索
```python
import yaml

# 加载结构化索引
with open("config/investor_index.yaml") as f:
    index = yaml.safe_load(f)

# 根据问题类型路由到投资人
def route_question(question_type):
    matrix = index["decision_matrix"]
    return matrix.get(question_type, {})
```

### 方式四：NOFX / Agent 集成

**一行命令下载规则：**
```bash
curl -sL https://raw.githubusercontent.com/sou350121/investment-masters-handbook/main/config/decision_rules.generated.json -o rules.json
```

**Python 直接加载（无需下载）：**
```python
import json, urllib.request
rules = json.load(urllib.request.urlopen("https://raw.githubusercontent.com/sou350121/investment-masters-handbook/main/config/decision_rules.generated.json"))
```

**或复制这个 URL 到任何支持 JSON 的工具：**
```
https://raw.githubusercontent.com/sou350121/investment-masters-handbook/main/config/decision_rules.generated.json
```

---

## 📖 实战案例：分析 Costco

> 完整案例见 [docs/README_Usage.md](docs/README_Usage.md)

### Step 1：宏观定位（Dalio）
```
当前：增长↓ + 通胀↓ → 衰退/通缩象限
IF 增长↓ + 通胀↓
   THEN 偏防守，必需消费（如 Costco）相对有利 ✅
```

### Step 2：护城河评估（Buffett）
| 护城河类型 | Costco | 评估 |
|-----------|--------|------|
| 品牌 | 会员信任度极高 | ✅ 强 |
| 成本优势 | 规模采购、低毛利 | ✅ 强 |
| 转换成本 | 会员制 + 习惯 | ✅ 中强 |

### Step 3：估值判断（Buffett + Lynch）
```
P/E: 53x | PEG: 4.4 | 盈余收益率: 1.9% < 国债×1.5
→ 以 Buffett/Lynch 标准，估值偏高 ⚠️
```

### Step 4：最终决策
```
✅ 好公司（护城河存在）
⚠️ 估值偏高（安全边际不足）
→ 行动：加入观察名单，等待 P/E < 35 再考虑
```

---

## 📁 项目结构

```text
investment-masters-handbook/
├── config/                          # ⭐ SSOT 配置
│   ├── investor_index.yaml          #    投资人结构化索引（名单/矩阵/路由/题库）
│   ├── decision_rules.generated.json #   🤖 自动生成：机读 IF-THEN 规则（299）
│   ├── reasoning_config.yaml        #    委员会人格/类别/权重配置
│   ├── policy_gate.yaml             #    Policy Gate 风控护栏规则
│   └── scenarios.yaml               #    场景沙盒回归用例
│
├── investors/                       # 📚 投资人详细框架（Markdown + DECISION_RULES）
│   ├── warren_buffett.md
│   ├── ray_dalio.md
│   └── ...
│
├── services/                        # 🧠 FastAPI 服务端
│   └── rag_service.py               #    /api/rag/query /api/rag/ensemble /api/policy/gate /health
│
├── tools/                           # 🔧 核心逻辑（RAG/Reasoning/LLM Bridge）
│   ├── rag_core.py
│   ├── reasoning_core.py
│   └── llm_bridge.py
│
├── web/                             # 🌐 Next.js 前端（静态导出 + 后端托管）
│   ├── src/components/InvestorList.tsx
│   └── out/                         #    npm run build 输出（FastAPI 托管）
│
├── scripts/                         # 🧪 工具脚本（生成制品/校验）
│   ├── generate_artifacts.py
│   └── validate-docops.ps1
│
├── stories/                         # 📒 Story（SSOT for changes）
├── prompts/                         # 🧾 Prompt VCS（证据链）
└── docs/                            # 📖 文档与指南
```

---

## 🔗 NOFX AI 交易系统集成

本项目设计为 [NOFX](https://github.com/NoFxAiOS/nofx) 的知识库模块：

```
┌─────────────────────────────────────────────────────────┐
│                      NOFX 系统                          │
├─────────────────────────────────────────────────────────┤
│  市场数据 → 信号生成 → [投资大师规则] → 风控 → 执行    │
│                            ↑                            │
│              investment-masters-handbook                │
│              (本项目作为决策知识库)                     │
└─────────────────────────────────────────────────────────┘
```

### ⚡ 30 秒接入（复制粘贴即可）

**Step 1** - 复制这个 URL：
```
https://raw.githubusercontent.com/sou350121/investment-masters-handbook/main/config/decision_rules.generated.json
```

**Step 2** - 粘贴到 NOFX 配置（或任何支持 JSON URL 的工具）

**Step 3** - 验证：应加载 299 条规则

**Step 4** - 设置环境变量（如果使用 AI500 策略配置）：
```bash
# Linux / macOS
export NOFX_AUTH_TOKEN="your_token_here"

# Windows PowerShell
$env:NOFX_AUTH_TOKEN="your_token_here"
```

> 📖 详细集成指南、字段说明、排错步骤见 **[guides/nofx_integration.md](guides/nofx_integration.md)**
> 
> 🔐 **安全提示**：配置文件使用环境变量管理敏感信息，详见 [安全政策](docs/SECURITY.md)

### 集成方式对比

| 方式 | 复杂度 | 说明 |
|------|--------|------|
| **JSON 规则导入** | ⭐ | 直接加载 `decision_rules.generated.json` |
| **YAML 配置** | ⭐⭐ | 读取 `investor_index.yaml` 进行路由 |
| **RAG 检索** | ⭐⭐⭐ | 向量化 `.md` 文件，语义搜索 |

---

## 📋 实战速查表

| 你在做什么？ | 参考谁 | 核心规则 |
|--------------|--------|----------|
| 挑个股 | Buffett → Lynch → 邱国鹭 | 护城河 + PEG + 行业集中度 |
| 判断大盘方向 | Druckenmiller → Dalio | 净流动性 + 四象限 |
| 决定现金比例 | Marks → Klarman | 周期位置 + 安全边际 |
| 检查决策偏误 | Munger | 25 种心理偏误清单 |
| 逆向抄底 | 冯柳 → Klarman | 赔率优先 + 左侧买入 |
| 量化策略灵感 | Simons → Thorp | 统计套利 + 凯利公式 |

---

## 🛠️ 工具与常用命令

### 规则引擎 CLI

```bash
# 按场景查询
python tools/rule_query.py --scenario "市场恐慌"

# 按投资者查询
python tools/rule_query.py --investor buffett

# 按关键词查询
python tools/rule_query.py --keyword "护城河"

# 组合查询
python tools/rule_query.py --when "估值" --then "买入"

# 输出 JSON（方便程序处理）
python tools/rule_query.py --scenario "选股" --format json
```

### RAG 检索增强生成

> 📚 **完整指南**：[guides/rag_guide.md](guides/rag_guide.md)

#### 1. 启动 RAG API 服务 (FastAPI)
```bash
pip install -r requirements.txt
python services/rag_service.py
```

#### 2. CLI 示例
```bash
# 单次查询
python examples/rag_langchain.py "这个股票值得买吗？"

# 交互模式
python examples/rag_langchain.py --interactive
```

**核心特性**：
- 🔍 语义检索 26 位大师的智慧
- 📊 299 条 IF-THEN 规则检索
- 🤖 支持多轮对话上下文
- ⚡ 按投资者/规则类型过滤

---

## 📝 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新历史。

**最新版本 v1.8.0** (2025-12-27):
- 🧠 **大师深度会诊 (NOFX Mode)**：支持直接填入 OpenRouter/OpenAI Key，实现“钥匙随身带”安全架构。
- 🎭 **角色化辩论引擎**：大师们现在拥有专属人格，推理过程包含 `<reasoning>` 思考链。
- ⚡ **异步性能优化**：向量库异步后台加载，首页实现秒开体验。
- 🎨 **UX 进化**：全新的 Token 登录面板、交互式提示 Tooltip 以及更醒目的会诊工作台。

---

## [1.7.0] - 2025-12-23

## 🤝 贡献

欢迎贡献新的投资人框架或改进现有内容！

详见 [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) 了解：
- 添加新投资人的标准流程
- YAML 字段规范
- Markdown 模板
- CI 校验要求

---

## ⚠️ 免责声明

本项目仅供**教育和研究**目的，不构成投资建议。投资有风险，请根据自身情况谨慎决策。

---

## 📄 License

MIT License

---

> **学习大师的思考方式，而非简单复制操作。**
