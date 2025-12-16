# Strategies 策略配置

本目录包含各种量化交易策略的配置文件。

---

## 📁 文件列表

| 文件 | 说明 | 版本 |
|------|------|------|
| `nofx_ai500_quantified.json` | NOFX AI500 量化策略配置（融合五位投资大师） | v2.0 |

---

## 🔐 环境变量设置（必须）

### ⚠️ 重要提示

**所有策略配置文件都使用环境变量来管理敏感信息（如 API Token），请在使用前先设置环境变量！**

### 快速设置

#### Linux / macOS
```bash
export NOFX_AUTH_TOKEN="your_token_here"
```

#### Windows PowerShell
```powershell
$env:NOFX_AUTH_TOKEN="your_token_here"
```

#### Windows CMD
```cmd
set NOFX_AUTH_TOKEN=your_token_here
```

### 详细说明

👉 **完整的环境变量设置指南**：[../docs/SECURITY.md](../docs/SECURITY.md)

---

## 📖 使用方式

### NOFX AI500 量化策略

**配置文件**：`nofx_ai500_quantified.json`

**特点**：
- 融合 Soros、Druckenmiller、Thorp、Marks、Simons 五位大师智慧
- K线 + OI 量化信号矩阵
- 置信度 → 仓位映射（凯利公式）

**使用步骤**：

1. **设置环境变量**（见上方）
2. **加载配置**：
   ```python
   import json
   import os
   
   with open("strategies/nofx_ai500_quantified.json", "r", encoding="utf-8") as f:
       config = json.load(f)
   
   # 替换环境变量占位符
   token = os.getenv("NOFX_AUTH_TOKEN")
   if not token:
       raise ValueError("请设置 NOFX_AUTH_TOKEN 环境变量")
   
   # 替换 URL 中的占位符
   config["config"]["coin_source"]["coin_pool_api_url"] = \
       config["config"]["coin_source"]["coin_pool_api_url"].replace("${NOFX_AUTH_TOKEN}", token)
   ```

3. **在 NOFX 系统中导入**：
   - 将配置文件上传到 NOFX 后台
   - 系统会自动读取环境变量并替换占位符

---

## 🔄 环境变量占位符说明

配置文件中的占位符格式：`${VARIABLE_NAME}`

| 占位符 | 环境变量 | 说明 |
|--------|----------|------|
| `${NOFX_AUTH_TOKEN}` | `NOFX_AUTH_TOKEN` | NOFX API 认证 Token |

**替换逻辑**：
- 程序读取配置文件时，检测到 `${...}` 格式的占位符
- 从系统环境变量中查找对应的值
- 如果找不到，抛出错误（防止使用空值）

---

## 📚 相关文档

- [安全政策](../docs/SECURITY.md) - 详细的安全管理指南
- [NOFX AI500 大师 Prompt](../prompts/nofx_ai500_master.md) - 策略的 Prompt 说明
- [投资人映射说明](./INVESTOR_MAPPING.md) - 五位大师如何应用到策略中

---

## ⚠️ 常见问题

### Q: 为什么配置文件里没有真实的 Token？

**A**: 为了安全！Token 是敏感信息，不应该进入代码库。使用环境变量可以：
- 每个用户用自己的 Token
- 随时轮换 Token 而不改代码
- 避免 Token 泄露到公开仓库

### Q: 如何获取 NOFX Token？

**A**: 
1. 登录 NOFX 后台
2. 进入"API 设置"或"开发者设置"
3. 生成新的 API Token
4. 复制 Token 并设置为环境变量

### Q: 环境变量设置后还是不生效？

**A**: 
1. 确认环境变量名拼写正确（区分大小写）
2. 确认已重启终端/IDE
3. 运行 `echo $NOFX_AUTH_TOKEN`（Linux/macOS）或 `$env:NOFX_AUTH_TOKEN`（PowerShell）验证
4. 检查配置文件中的占位符格式是否正确（`${NOFX_AUTH_TOKEN}`）

---

> 💡 **提示**：如果遇到问题，请查看 [安全政策文档](../docs/SECURITY.md) 获取详细帮助。
