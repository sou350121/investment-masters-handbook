# S-0001-install-docops-agentops

## 目标
在 investment-masters-handbook 项目中集成 DocOps + AgentOps 证据链工作流，提升多 Agent 协作的可追溯性。

## 验收标准（必须可验证）
- [x] 创建核心目录结构：`stories/`, `sessions/`, `issues/`, `runbooks/`, `.cursor/rules/`, `docs/features/`。
- [x] 安装自动化脚本：`scripts/new-story.ps1/sh` 与 `scripts/validate-docops.ps1/sh`。
- [x] 安装引导文档：`runbooks/AGENT_BOOTSTRAP_DOCOPS_AGENTOPS.md`。
- [x] 安装代理宪法：`AGENT_CONSTITUTION.md`。
- [x] 安装 Cursor 规则：`.cursor/rules/docops-agentops.mdc`。
- [x] 成功运行 `validate-docops` 脚本并通过校验。

## 范围 / 非目标
- 不涉及具体业务功能的变更。
- 不修改现有的 RAG 或 Policy Gate 逻辑。

## 任务拆分
- [x] 读取 Starter Kit 仓库内容。
- [x] 创建本地目录。
- [x] 写入脚本文件。
- [x] 写入文档文件。
- [x] 运行校验脚本。

## 关联文件（计划/实际）
- `scripts/new-story.ps1`
- `scripts/validate-docops.ps1`
- `runbooks/AGENT_BOOTSTRAP_DOCOPS_AGENTOPS.md`
- `AGENT_CONSTITUTION.md`
- `.cursor/rules/docops-agentops.mdc`

## 进度日志（每次 Agent session 追加）
- 2025-12-23: 初始化并完成安装。
