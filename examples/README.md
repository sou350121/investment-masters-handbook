# Examples 使用示例

> 📚 **RAG 完整指南**：[../guides/rag_guide.md](../guides/rag_guide.md)

## 文件列表

| 文件 | 说明 |
|------|------|
| `rag_langchain.py` | RAG 检索增强生成示例（支持投资者文档 + 232条规则） |

## 快速开始

```bash
# 安装依赖
pip install langchain langchain-community chromadb pyyaml

# 运行查询
python examples/rag_langchain.py "这个股票值得买吗？"

# 交互模式
python examples/rag_langchain.py --interactive

# 仅使用规则（更快，无需向量数据库）
python examples/rag_langchain.py --rules-only "护城河"
```

## 更多用法

### Python 直接加载规则

```python
import json

with open("config/decision_rules.generated.json", encoding="utf-8") as f:
    data = json.load(f)

rules = data["rules"]
print(f"共 {len(rules)} 条规则")
```

### 作为 System Prompt

```python
with open("guides/llm_summary.md", encoding="utf-8") as f:
    system_prompt = f.read()

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "特斯拉值得买吗？"}
]
```

