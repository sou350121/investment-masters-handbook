# 贡献指南

> 如何为 Investment Masters Handbook 添加新内容。

---

## 📋 添加新投资人（标准流程）

### 概览

```
┌─────────────────────────────────────────────────────────────┐
│  1. 编辑 SSOT          config/investor_index.yaml           │
│         ↓                                                   │
│  2. 创建详情文件       investors/{investor_id}.md           │
│         ↓                                                   │
│  3. 生成 + 验证        python scripts/generate_artifacts.py │
│         ↓                                                   │
│  4. 提交推送           git add → commit → push              │
└─────────────────────────────────────────────────────────────┘
```

---

### 第 1 步：在 SSOT 添加元数据

编辑 `config/investor_index.yaml`，在 `investors:` 列表末尾添加：

```yaml
- id: investor_id              # 必填：唯一ID（英文小写+下划线）
  full_name: Full Name         # 必填：英文全名
  chinese_name: 中文名          # 必填：中文名
  fund: 基金/机构名称           # 必填：管理的基金或机构
  aum: "$XXB"                  # 选填：管理资产规模
  active_years: "YYYY-present" # 选填：活跃年份
  style:                       # 必填：投资风格标签（1-5个）
    - value_investing
    - concentrated
  best_for:                    # 必填：最适合解决的问题（1-5个）
    - stock_selection
    - valuation
  key_concepts:                # 必填：核心概念（1-5个）
    - concept_1
    - concept_2
  market_conditions:           # 选填：市场环境适用性
    all_conditions: neutral
  decision_weight:             # 必填：决策权重（0-1）
    stock_pick: 0.8
    macro_timing: 0.2
    risk_check: 0.5
    portfolio: 0.6
  tags_zh:                     # 必填：中文标签（用于搜索）
    - 标签1
    - 标签2
  related_doc: investor_id.md  # 必填：对应的详情文件名
```

#### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` | ✅ | 唯一标识符，英文小写+下划线，如 `warren_buffett` |
| `full_name` | ✅ | 英文全名 |
| `chinese_name` | ✅ | 中文名 |
| `fund` | ✅ | 管理的基金/机构 |
| `aum` | ❌ | 管理资产规模（字符串格式） |
| `active_years` | ❌ | 活跃年份范围 |
| `style` | ✅ | 投资风格标签列表 |
| `best_for` | ✅ | 最适合解决的问题类型 |
| `key_concepts` | ✅ | 核心投资概念 |
| `decision_weight` | ✅ | 四维决策权重（stock_pick/macro_timing/risk_check/portfolio） |
| `tags_zh` | ✅ | 中文搜索标签 |
| `related_doc` | ✅ | 详情文件名（需与 id 对应） |

#### 常用 style 标签

```
value_investing, growth_investing, macro, quantitative, activist,
concentrated, diversified, long_term_hold, trading, contrarian,
momentum, factor_investing, arbitrage, distressed, event_driven
```

---

### 第 2 步：创建投资人详情文件

新建 `investors/{investor_id}.md`，使用以下模板：

```markdown
---
id: investor_id
name: 中文名
tags: [tag1, tag2, tag3]
---

# 中文名 (English Name)

> 一句话总结此投资人的核心理念。

---

## 📋 基本信息

| 项目 | 内容 |
|------|------|
| **基金/机构** | 机构名称 |
| **管理规模** | $XXB |
| **投资风格** | 风格描述 |
| **代表作/著作** | 书籍/演讲/信件 |

---

## 🎯 核心投资原则

### 原则 1：标题
内容描述...

### 原则 2：标题
内容描述...

---

## 🧠 投资框架

### 选股标准
- 标准 1
- 标准 2

### 卖出条件
- 条件 1
- 条件 2

---

## DECISION_RULES

```
IF 条件A AND 条件B
   THEN 行动
   BECAUSE 原因

IF 条件C OR 条件D
   THEN 行动
   BECAUSE 原因

IF 风险信号出现
   THEN PASS/减仓
   BECAUSE 风险原因
```

---

## 📚 经典语录

> "语录 1"

> "语录 2"

---

## 🔗 相关资源

- 资源链接 1（如有）
- 资源链接 2（如有）
```

#### DECISION_RULES 格式规范

```
IF <条件>
   THEN <行动>
   BECAUSE <原因>
```

- **条件**：可用 `AND`、`OR` 连接多个条件
- **行动**：`买入`、`卖出`、`持有`、`PASS`、`深入研究`、`减仓` 等
- **原因**：简短说明逻辑依据

---

### 第 3 步：生成派生文档 + 本地验证

```bash
cd /opt/investment-handbook/investment-masters

# 1) 重新生成（更新 INVESTORS.generated.md 和 decision_rules.generated.json）
python scripts/generate_artifacts.py

# 2) 运行 CI 验证脚本
python scripts/check_links.py           # 链接检查
python scripts/validate_front_matter.py # Front Matter 校验
python scripts/check_router_config.py   # 路由一致性
python scripts/scan_sensitive.py        # 敏感信息扫描

# 如果全部显示 [xxx] ok，则可以提交
```

---

### 第 4 步：提交并推送

```bash
git add -A
git commit -m "Add investor: 投资人中文名"
git push origin main
```

推送后 GitHub Actions 会自动运行 CI 检查。

---

## 📋 添加新 Prompt 角色

### 流程

1. 在 `prompts/` 目录创建 `{role_id}.md`
2. 使用 YAML front matter 定义元数据
3. 提交推送

### 模板

```markdown
---
id: role_id
name: 角色名称
category: analysis|trading|philosophy
---

# 角色名称

## 🌌 角色设定
描述这个角色是谁、能做什么...

## ⚡ 核心能力
- 能力 1
- 能力 2

## 🎯 使用场景
适合用于什么场景...

## 💬 示例对话
**用户**：问题示例
**角色**：回答示例
```

---

## 📋 更新路由配置

如果新投资人需要被路由系统引用：

1. 编辑 `config/router_config.yaml`
2. 在相关的 `categories` 或 `keyword_patterns` 中添加投资人 ID
3. 运行 `python scripts/check_router_config.py` 验证无冲突

---

## ✅ 检查清单

提交前确认：

- [ ] `investor_index.yaml` 中的 `id` 与 `related_doc` 文件名一致
- [ ] 详情文件包含 YAML front matter（`---` 包裹的元数据）
- [ ] 详情文件包含 `## DECISION_RULES` 章节
- [ ] 所有脚本验证通过（显示 `[xxx] ok`）
- [ ] Commit message 格式：`Add investor: 中文名` 或 `Update investor: 中文名`

---

## 🤝 问题反馈

如果遇到问题：
1. 检查 CI 日志中的具体错误信息
2. 确认文件路径和命名是否正确
3. 提 Issue 或 PR 描述问题

---

## 📁 项目结构速查

```
investment-masters/
├── config/
│   ├── investor_index.yaml          # ⭐ SSOT：投资人元数据
│   ├── router_config.yaml           # 路由配置
│   └── decision_rules.generated.json # 🤖 自动生成：机读规则
├── docs/
│   ├── INVESTORS.generated.md       # 🤖 自动生成：投资人表
│   └── CONTRIBUTING.md              # 👈 本文件
├── investors/
│   └── {investor_id}.md             # 投资人详情文件
├── prompts/
│   └── {role_id}.md                 # Prompt 角色文件
├── scripts/
│   ├── generate_artifacts.py        # 生成脚本
│   ├── validate_front_matter.py     # Front Matter 校验
│   ├── check_links.py               # 链接检查
│   ├── check_router_config.py       # 路由检查
│   └── scan_sensitive.py            # 敏感信息扫描
└── .github/workflows/quality.yml    # CI 配置
```

