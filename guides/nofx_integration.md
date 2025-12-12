# NOFX 集成指南

> 把 187 条投资大师决策规则接入 NOFX 或任何 AI Agent 系统。

---

## 30 秒快速接入

### 方法 1：直接粘贴 URL（推荐）

复制这个 URL 到 NOFX 配置或任何支持 JSON 数据源的工具：

```
https://raw.githubusercontent.com/sou350121/investment-masters-handbook/main/config/decision_rules.generated.json
```

### 方法 2：一行命令下载

```bash
curl -sL https://raw.githubusercontent.com/sou350121/investment-masters-handbook/main/config/decision_rules.generated.json -o rules.json
```

### 方法 3：Python 直接加载（无需下载）

```python
import json, urllib.request
rules = json.load(urllib.request.urlopen("https://raw.githubusercontent.com/sou350121/investment-masters-handbook/main/config/decision_rules.generated.json"))
print(f"已加载 {len(rules['rules'])} 条规则")
```

---

## 数据格式说明

### JSON 结构

```json
{
  "rules": [
    {
      "rule_id": "warren_buffett:buy:001",
      "investor_id": "warren_buffett",
      "kind": "buy",
      "when": "盈餘收益率 > 10Y國債 × 1.5 AND 護城河完好",
      "then": "考慮買入",
      "because": "提供安全邊際，回報優於無風險利率",
      "source_file": "investors/warren_buffett.md"
    }
  ],
  "version": "1.0"
}
```

### 字段映射

| 字段 | 类型 | 说明 |
|------|------|------|
| `rule_id` | string | 唯一标识：`{investor}:{kind}:{序号}` |
| `investor_id` | string | 投资人 ID，对应 `investor_index.yaml` |
| `kind` | string | 规则类型：`buy` / `sell` / `hold` / `risk` / `other` |
| `when` | string | 触发条件（IF 部分） |
| `then` | string | 执行动作（THEN 部分） |
| `because` | string | 原因说明（BECAUSE 部分） |
| `source_file` | string | 来源文件路径 |

---

## 最小冒烟测试 JSON

复制以下 JSON 验证你的系统能正确解析：

```json
{
  "rules": [
    {
      "rule_id": "test:buy:001",
      "investor_id": "warren_buffett",
      "kind": "buy",
      "when": "PE < 15 AND ROE > 15%",
      "then": "考虑买入",
      "because": "低估值高质量"
    },
    {
      "rule_id": "test:sell:001",
      "investor_id": "george_soros",
      "kind": "sell",
      "when": "买入论点不成立",
      "then": "立即止损",
      "because": "生存第一"
    },
    {
      "rule_id": "test:risk:001",
      "investor_id": "charlie_munger",
      "kind": "risk",
      "when": "只看到利好信息",
      "then": "检查确认偏误",
      "because": "避免心理偏误"
    }
  ],
  "version": "test"
}
```

---

## NOFX 配置示例

### 如果 NOFX 支持 URL 数据源

```yaml
# nofx.config.yaml（示例，具体字段名以 NOFX 文档为准）
rules:
  source: url
  url: https://raw.githubusercontent.com/sou350121/investment-masters-handbook/main/config/decision_rules.generated.json
  format: json
  refresh_interval: 86400  # 每天刷新一次
```

### 如果 NOFX 支持本地文件

```yaml
# 先下载规则文件
# curl -sL <URL> -o /path/to/rules.json

rules:
  source: file
  path: /path/to/rules.json
  format: json
```

### 如果 NOFX 支持内嵌规则

直接复制 `decision_rules.generated.json` 的内容到 NOFX 配置中。

---

## 验证步骤

### 1. 检查规则数量

```python
import json

with open("rules.json") as f:
    data = json.load(f)

print(f"规则总数: {len(data['rules'])}")  # 应为 187 条左右
```

### 2. 按投资人统计

```python
from collections import Counter

investors = Counter(r["investor_id"] for r in data["rules"])
for inv, count in investors.most_common():
    print(f"  {inv}: {count} 条")
```

### 3. 随机抽样检查

```python
import random

sample = random.sample(data["rules"], 3)
for r in sample:
    print(f"[{r['rule_id']}]")
    print(f"  IF {r['when']}")
    print(f"  THEN {r['then']}")
    print(f"  BECAUSE {r['because']}")
    print()
```

---

## 常见问题排查

### 问题：加载失败 / 404

**原因**：URL 错误或网络问题

**解决**：
1. 确认 URL 正确（注意 `raw.githubusercontent.com`）
2. 浏览器直接访问 URL 检查是否能打开
3. 如果被墙，使用代理或下载到本地

### 问题：JSON 解析错误

**原因**：编码问题或文件损坏

**解决**：
```bash
# 检查文件是否为有效 JSON
python -m json.tool rules.json > /dev/null && echo "Valid JSON" || echo "Invalid JSON"
```

### 问题：规则数量为 0

**原因**：JSON 结构不匹配

**解决**：检查是否正确访问 `data["rules"]`（不是 `data` 本身）

### 问题：中文乱码

**原因**：编码未指定为 UTF-8

**解决**：
```python
with open("rules.json", encoding="utf-8") as f:
    data = json.load(f)
```

---

## 架构图

```
┌─────────────────────────────────────────────────────────┐
│                      NOFX 系统                          │
├─────────────────────────────────────────────────────────┤
│  市场数据 → 信号生成 → [投资大师规则] → 风控 → 执行    │
│                            ↑                            │
│              investment-masters-handbook                │
│              (本项目作为决策知识库)                     │
└─────────────────────────────────────────────────────────┘

数据流：
1. NOFX 从 URL/文件 加载 decision_rules.generated.json
2. 解析 187 条 IF-THEN 规则
3. 在信号生成/风控环节匹配规则
4. 输出决策建议（买入/卖出/持有/风险警告）
```

---

## 版本与一致性

- 规则由 `scripts/generate_artifacts.py` 从 `investors/*.md` 自动提取
- CI 保证每次提交后规则文件与源文档一致
- 版本号见 JSON 中的 `version` 字段
- 更新日志见 [CHANGELOG.md](../CHANGELOG.md)

---

## 相关资源

| 资源 | 说明 |
|------|------|
| [config/decision_rules.generated.json](../config/decision_rules.generated.json) | 机读规则文件 |
| [config/investor_index.yaml](../config/investor_index.yaml) | 投资人结构化索引 |
| [config/router_config.yaml](../config/router_config.yaml) | 路由配置 |
| [guides/llm_summary.md](llm_summary.md) | LLM System Prompt |
| [docs/README_Usage.md](../docs/README_Usage.md) | 完整使用案例 |

---

## 需要帮助？

如果遇到集成问题：
1. 检查 [常见问题排查](#常见问题排查)
2. 提 Issue 到 [GitHub](https://github.com/sou350121/investment-masters-handbook/issues)
3. 附上错误信息和你的 NOFX 版本

