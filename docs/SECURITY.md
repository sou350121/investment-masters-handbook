# 🔐 安全政策与敏感信息管理

> **最后更新**：2024-12-14  
> **适用范围**：所有包含 API 密钥、Token、密码等敏感信息的配置文件

---

## ⚠️ 为什么不能硬编码敏感信息？

### 什么是"硬编码"？

**硬编码** = 把密码、API Key、Token 等敏感信息直接写在代码或配置文件中

### 示例：错误做法 ❌

```json
{
  "api_url": "http://api.example.com/data?auth=cm_568c67eae410d912c54c"
}
```

### 为什么这是严重的安全问题？

| 风险 | 说明 | 后果 |
|------|------|------|
| **泄露风险** | 代码上传到 GitHub 后，任何人都能看到你的 Token | 恶意用户可能盗用你的 API 配额 |
| **无法撤销** | Token 已写入 Git 历史，即使删除文件，历史记录还在 | 即使轮换 Token，旧 Token 仍可能被利用 |
| **无法个性化** | 所有用户必须用同一个 Token | 无法追踪谁在使用，无法单独撤销某个用户的权限 |
| **权限失控** | 如果有人拿到 Token，可以调用你的 API | 可能产生费用、数据泄露、账户被滥用 |

### 真实案例

```
2023 年，某开源项目在 GitHub 上暴露了 AWS Access Key
→ 24 小时内被恶意用户发现
→ 利用 Key 创建了价值 $6000 的云资源
→ 项目所有者收到巨额账单
→ 即使删除代码，Key 仍在 Git 历史中，无法彻底清除
```

---

## ✅ 正确做法：使用环境变量

### 什么是环境变量？

**环境变量** = 存储在操作系统中的键值对，程序运行时动态读取，不进入代码库

### 示例：正确做法 ✅

```json
{
  "api_url": "http://api.example.com/data?auth=${NOFX_AUTH_TOKEN}"
}
```

使用时，在系统环境变量中设置：
```bash
export NOFX_AUTH_TOKEN="你的真实token"
```

---

## 📋 本项目的敏感信息管理

### 当前使用的环境变量

| 环境变量名 | 用途 | 配置文件位置 |
|-----------|------|-------------|
| `NOFX_AUTH_TOKEN` | NOFX API 认证 Token | `strategies/nofx_ai500_quantified.json` |

### 如何设置环境变量？

#### Linux / macOS

**临时设置（当前终端会话）**：
```bash
export NOFX_AUTH_TOKEN="your_token_here"
```

**永久设置（推荐）**：
```bash
# 编辑 ~/.bashrc 或 ~/.zshrc
echo 'export NOFX_AUTH_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

**验证设置**：
```bash
echo $NOFX_AUTH_TOKEN
# 应该输出你的 token（注意：不要在公共场合执行此命令）
```

---

#### Windows PowerShell

**临时设置（当前会话）**：
```powershell
$env:NOFX_AUTH_TOKEN="your_token_here"
```

**永久设置（用户级别）**：
```powershell
[System.Environment]::SetEnvironmentVariable('NOFX_AUTH_TOKEN', 'your_token_here', 'User')
```

**永久设置（系统级别，需要管理员权限）**：
```powershell
[System.Environment]::SetEnvironmentVariable('NOFX_AUTH_TOKEN', 'your_token_here', 'Machine')
```

**验证设置**：
```powershell
$env:NOFX_AUTH_TOKEN
```

---

#### Windows CMD

**临时设置**：
```cmd
set NOFX_AUTH_TOKEN=your_token_here
```

**永久设置（用户级别）**：
```cmd
setx NOFX_AUTH_TOKEN "your_token_here"
```

**注意**：`setx` 设置后需要重新打开 CMD 窗口才能生效。

---

### 使用 .env 文件（仅用于本地开发）

**⚠️ 警告**：`.env` 文件**绝不能**提交到 Git！

**创建 `.env` 文件**（在项目根目录）：
```bash
# .env
NOFX_AUTH_TOKEN=your_token_here
```

**添加到 `.gitignore`**：
```
.env
.env.local
.env.*.local
```

**在代码中加载 .env**（Python 示例）：
```python
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 读取环境变量
token = os.getenv('NOFX_AUTH_TOKEN')
```

---

## 🔄 Token 轮换流程

### 如果 Token 已泄露怎么办？

1. **立即轮换 Token**
   - 登录 NOFX 后台
   - 撤销旧 Token（`cm_568c67eae410d912c54c`）
   - 生成新 Token

2. **更新环境变量**
   ```bash
   export NOFX_AUTH_TOKEN="新token"
   ```

3. **检查 Git 历史**
   ```bash
   # 检查历史中是否还有旧 Token
   git log -p | grep "cm_568c67eae410d912c54c"
   ```

4. **（可选）清理 Git 历史**
   - 使用 `git filter-branch` 或 `git filter-repo`
   - ⚠️ 注意：这会重写历史，需要强制推送，影响所有协作者

---

## 🛡️ 安全检查清单

在提交代码前，请确认：

- [ ] 没有硬编码的 API Key、Token、密码
- [ ] 所有敏感信息都使用环境变量
- [ ] `.env` 文件已添加到 `.gitignore`
- [ ] 配置文件中的占位符格式正确（`${VAR_NAME}`）
- [ ] 文档中说明了如何设置环境变量

---

## 📚 相关资源

- [OWASP 密钥管理最佳实践](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [GitHub 安全最佳实践](https://docs.github.com/en/code-security/security-advisories/working-with-repository-security-advisories)
- [12 Factor App - Config](https://12factor.net/config)

---

## 💬 报告安全问题

如果你发现本项目存在安全漏洞，请：

1. **不要**在公开 Issue 中报告
2. 发送邮件至：`security@your-domain.com`（替换为实际邮箱）
3. 或通过 GitHub Security Advisories 报告

---

> 🔒 **记住**：安全不是一次性的工作，而是持续的过程。每次添加新的 API 集成时，都要问自己："敏感信息是否已正确管理？"
