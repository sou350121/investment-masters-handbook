# 更新日志 (Changelog)

本项目的所有重要更新都会记录在这里。

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

| 版本 | 投资人数 | IF-THEN 规则 | 文件数 |
|------|----------|--------------|--------|
| 1.1.0 | 16 | 187 | 40+ |
| 1.0.0 | 14 | 150+ | 30+ |

---

## 链接

- **GitHub**：https://github.com/sou350121/investment-masters-handbook
- **机读规则**：https://raw.githubusercontent.com/sou350121/investment-masters-handbook/main/config/decision_rules.generated.json

