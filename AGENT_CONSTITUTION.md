# 🏛️ IMH Agent 宪法（Repo 专用版）

> 上游参考：`agent-experience-library/AGENT_CONSTITUTION_UNIVERSAL.md`  
> 本文件是 **Investment Masters Handbook（IMH）** 仓库的“落地版宪法”，用于约束本仓库内的 Cursor/多 Agent 行为。  
> 目标：让每次改动都形成 **可追溯、可验证、可回滚** 的证据链闭环（DocOps + AgentOps）。

---

## 0. 身份逻辑（必须内化）

1) **主动性（Proactivity）**  
不要被动等指令。发现更优雅/更安全/更可验证的路径，必须主动提出，并明确范围变化点。

2) **幻觉零容忍**  
不确定就说不确定；不编造接口、参数、文件、验证结果。所有结论要能被命令验证。

3) **上下文守卫**  
在长任务中持续压缩无关上下文；避免“越改越发散”。遇到范围不清先问，再动手。

---

## 1. 权限与边界（Scope Guardrails）

### 1.1 允许修改的目录（白名单）
- `web/src/`：前端源码
- `services/`：后端服务（FastAPI）
- `tools/`：内核工具/桥接层
- `config/`：配置文件（SSOT/可调参数）
- `investors/`：大师文档
- `prompts/`：Prompt VCS（证据链）
- `stories/`：需求正文（SSOT）
- `sessions/`：Failures Log（仅高信噪比）
- `docs/`：特性文档与 Ledger（`docs/features/**/status.md`）
- `scripts/`：自动化脚本
- `runbooks/`：操作指南
- `.cursor/rules/`：规则配置（如存在）
- `issues/`：任务索引
- `.github/`：CI 配置（谨慎改动）

### 1.2 禁止与红线
- **禁止把任何 token/密钥写入仓库**（包括示例、README、测试用例里的真实 key）。密钥只允许：环境变量 / 本地 `localStorage`（前端）/ CI secret。
- **不要擅自重构 CI/CD 核心流程**（除非用户明确授权）。
- **未经授权不要引入重型依赖或大规模重构**；优先最小可用变更。

---

## 2. DocOps + AgentOps（证据链协议：本仓库 SSOT）

### 2.1 SSOT 定义
- **Story 是需求的唯一事实源**：`stories/S-xxxx-*.md`
- **代码库是实现事实终点**：`services/`、`tools/`、`web/src/` 等

### 2.2 交付闭环（强制）
每次交付必须形成证据链闭环：
`Story（需求） → Prompt/Failures（意图与偏航） → Code/Test（实现） → Ledger(status)（结果与验证）`

落地文件约定：
- `prompts/<story>.md`：记录本次 session 的关键 prompt/决策/约束（追加小节）
- `docs/features/<story>/status.md`：变更摘要 + 可复制验证命令（必填）
- `sessions/<story>/failures.md`：**只有真的失败/偏航/回滚/重大纠结**才写

> 快速 SOP：见 `runbooks/AGENT_BOOTSTRAP_DOCOPS_AGENTOPS.md`

---

## 3. 工程底线（IMH 特有的坑位与要求）

### 3.1 Windows / PowerShell 约束
- 不要用 bash 的 heredoc（如 `python - << 'PY'`），PowerShell 下会炸；请用临时 `.py` 文件或 `python -c`。
- 端口冲突要先处理（必要时 `netstat -ano | findstr :8001` + `taskkill /PID ...`）。

### 3.2 服务与端口约定
- 本仓库 Web UI/后端默认端口：**8001**
- 健康检查：`GET /health`（应包含 `vectorstore_ready`、`vectorstore_doc_count` 等字段）

### 3.3 LLM/密钥处理
- `/api/rag/ensemble` 允许 `Authorization: Bearer <token>`：
  - `IMH_API_TOKEN`（实例访问 token）或
  - `sk-...`（LLM key，用于本次请求动态覆盖 LLMBridge）
- **后端不得持久化存储 LLM key**；前端只允许存本地 `localStorage`（用户主动保存）。

---

## 4. 输出标准（DNA 级格式）

每次对用户的交付输出，至少包含：
1) **结论**：做了什么、当前状态（完成/阻塞/风险）
2) **改动清单**：改了哪些文件/模块（用反引号标注路径）
3) **验证命令**：用户可复制执行的命令（至少 1 条）
4) **风险与回滚**：有哪些兼容性风险；如何回退

---

## 5. 快速验证命令（本仓库标准）

### 5.1 DocOps 校验（证据链）
- Windows：`pwsh -NoProfile -File scripts/validate-docops.ps1`

### 5.2 基础校验
- `python scripts/validate_front_matter.py`
- `python scripts/validate_tasks.py`

### 5.3 单测（示例）
- `pytest tests/test_ensemble.py`

