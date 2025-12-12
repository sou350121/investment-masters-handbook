# 📈 Investment Masters Handbook

[![CI](https://github.com/sou350121/investment-masters-handbook/actions/workflows/quality.yml/badge.svg)](https://github.com/sou350121/investment-masters-handbook/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Investors](https://img.shields.io/badge/Investors-16-green.svg)](#-投资大师速览)

> **把 16 位传奇投资大师的智慧，转化为可检索、可路由、可执行的 IF-THEN 规则**
> 
> 支持 RAG 检索 · LLM System Prompt · AI Agent · NOFX 集成

---

## 🎯 这个项目能帮你做什么？

```
┌─────────────────────────────────────────────────────────────────┐
│                    Investment Masters Handbook                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   问题输入                         智慧输出                      │
│   ────────                         ────────                      │
│   "这只股票值得买吗？"      →      Buffett 护城河框架            │
│   "现在是牛市还是熊市？"    →      Dalio 四象限 + Marks 周期     │
│   "我的决策有偏误吗？"      →      Munger 心理检查清单           │
│   "该持有多少现金？"        →      Klarman + Marks 框架          │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│   🤖 AI 原生设计                                                 │
│   ─────────────                                                  │
│   • 结构化 YAML 索引 → RAG 检索                                 │
│   • IF-THEN 规则 → Agent 决策                                   │
│   • System Prompt 模板 → LLM 助手                               │
│   • 机读 JSON → NOFX 交易系统                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🌟 核心特性

| 特性 | 说明 |
|------|------|
| **200+ IF-THEN 规则** | 从大师著作中提炼的可执行决策规则 |
| **16 位投资大师** | 涵盖价值、宏观、量化、逆向等流派 |
| **机器可读** | YAML/JSON 格式，支持程序化调用 |
| **AI 原生** | 专为 RAG、Agent、LLM 设计 |
| **CI 校验** | 自动化链接检查、格式校验、一致性检测 |
| **SSOT 架构** | 单一数据源，自动生成派生文档 |

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

### 方式一：手动查询
```
1. 遇到问题 → 打开 decision_router.md
2. 找到问题类型 → 定位推荐投资人
3. 打开对应 .md → 应用 IF-THEN 规则
```

### 方式二：AI System Prompt
```python
# 直接使用 guides/llm_summary.md 作为 System Prompt
with open("guides/llm_summary.md") as f:
    system_prompt = f.read()
```

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

### 方式四：NOFX 集成
```python
import json

# 加载机读规则
with open("config/decision_rules.generated.json") as f:
    rules = json.load(f)

# 187 条 IF-THEN 规则，可直接用于 Agent 决策
for rule in rules["rules"]:
    print(f"IF {rule['when']} THEN {rule['then']}")
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

```
investment-masters/
├── config/                          # ⭐ SSOT 配置
│   ├── investor_index.yaml          #    投资人结构化索引
│   ├── router_config.yaml           #    路由配置
│   └── decision_rules.generated.json #   🤖 自动生成：机读规则
│
├── investors/                       # 📚 投资人详细框架
│   ├── warren_buffett.md
│   ├── qiu_guolu.md                 #    🇨🇳 邱国鹭
│   ├── feng_liu.md                  #    🇨🇳 冯柳
│   └── ...
│
├── docs/                            # 📖 使用文档
│   ├── README_Usage.md              #    完整使用案例
│   ├── README_investors.md          #    投资人索引
│   ├── CONTRIBUTING.md              #    贡献指南
│   └── INVESTORS.generated.md       #    🤖 自动生成
│
├── guides/                          # 🎯 核心指南
│   ├── llm_summary.md               #    LLM System Prompt
│   └── practical_guide.md           #    200+ IF-THEN 规则
│
├── prompts/                         # 🎭 AI 角色 Prompt
│   ├── valuation_philosopher.md     #    估值哲学家
│   ├── crypto_trader.md             #    加密交易员
│   └── ...
│
├── scripts/                         # 🔧 自动化脚本
│   ├── generate_artifacts.py        #    生成派生文档
│   └── validate_*.py                #    CI 校验脚本
│
├── decision_router.md               # 🔀 决策路由（权威入口）
└── .github/workflows/quality.yml    # ⚙️ CI 配置
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

### 集成方式

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
