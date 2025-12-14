# AGENT.md

## 项目概述

Investment Masters Handbook - 将 17 位传奇投资大师的智慧转化为可检索、可路由、可执行的 IF-THEN 规则。支持 RAG 检索、LLM System Prompt、AI Agent 决策。

## 技术栈

- **语言**: Python 3.9+, Markdown, YAML, JSON
- **无框架依赖**: 纯静态知识库，可直接被任何系统读取
- **CI**: GitHub Actions (链接检查、格式校验)

## 目录结构

```
investment-masters-handbook/
├── investors/              # 17位投资大师详细框架 (.md)
├── config/                 # SSOT 配置文件
│   ├── investor_index.yaml     # 投资人结构化索引
│   ├── router_config.yaml      # 关键词路由配置
│   └── decision_rules.generated.json  # 机读规则（自动生成）
├── guides/                 # 使用指南
│   ├── llm_summary.md          # LLM System Prompt 模板
│   ├── practical_guide.md      # 200+ IF-THEN 规则
│   ├── quick_reference.md      # 速查卡片
│   └── nofx_integration.md     # NOFX 集成指南
├── prompts/                # AI 角色 Prompt 模板
├── docs/                   # 文档
├── scripts/                # 自动化脚本 (Python)
├── tools/                  # CLI 工具
├── examples/               # 集成示例
├── decision_router.md      # 决策路由器（核心入口）
└── router_config.yaml      # 路由配置
```

## 关键文件

| 文件 | 作用 |
|------|------|
| `decision_router.md` | 问题→投资人路由逻辑，核心入口 |
| `config/investor_index.yaml` | 所有投资人的结构化索引（SSOT） |
| `config/decision_rules.generated.json` | 机读 IF-THEN 规则 |
| `guides/llm_summary.md` | 浓缩版框架，可直接作为 System Prompt |
| `guides/quick_reference.md` | 一页速查卡片 |
| `investors/*.md` | 各投资大师的详细决策框架 |

## 常用命令

```bash
# 规则查询
python tools/rule_query.py --scenario "市场恐慌"
python tools/rule_query.py --investor buffett
python tools/rule_query.py --keyword "护城河"

# 生成派生文档
python scripts/generate_artifacts.py

# 校验
python scripts/check_links.py
python scripts/validate_front_matter.py
python scripts/check_router_config.py
```

## 代码规范

- **Markdown**: 使用中文，IF-THEN-BECAUSE 格式写决策规则
- **YAML**: 2 空格缩进，UTF-8 编码
- **Python**: 遵循 PEP8，使用 `encoding="utf-8"` 打开文件
- **文件命名**: 投资人用 `snake_case.md`（如 `warren_buffett.md`）

## 数据流

```
investor_index.yaml (SSOT)
        ↓
scripts/generate_artifacts.py
        ↓
decision_rules.generated.json + INVESTORS.generated.md
```

## 新增投资人流程

1. 在 `investors/` 创建 `{name}.md`，遵循现有模板格式
2. 在 `config/investor_index.yaml` 添加索引条目
3. 运行 `python scripts/generate_artifacts.py` 更新派生文件
4. 运行校验脚本确保无错误

## 测试指南

### 快速验证

```bash
# 运行所有校验
python scripts/check_links.py
python scripts/validate_front_matter.py
python scripts/check_router_config.py
python scripts/scan_sensitive.py

# 验证生成文件是否最新
python scripts/generate_artifacts.py
git status --porcelain
```

### 修改后必须检查

| 修改内容 | 需要运行 |
|----------|----------|
| 修改 `investors/*.md` | `check_links.py` + `generate_artifacts.py` |
| 修改 `config/investor_index.yaml` | `generate_artifacts.py` |
| 修改 `config/router_config.yaml` | `check_router_config.py` |

## 注意事项

- `config/decision_rules.generated.json` 是自动生成的，不要手动编辑
- 所有投资人数据以 `investor_index.yaml` 为 SSOT
- 项目是纯知识库，无运行时服务
