# S-0001-install-docops-agentops 状态

- 状态：已完成
- Story：
  - stories/S-0001-install-docops-agentops.md
- Prompt：
  - prompts/S-0001-install-docops-agentops.md
- Failures：
  - sessions/S-0001-install-docops-agentops/failures.md
- PR：

## 变更摘要
- 集成了 DocOps + AgentOps 工作流骨架。
- 新增了 `scripts/` 下的自动化脚本，支持一键新建 Story 和校验。
- 引入了 `.cursor/rules/docops-agentops.mdc` 强制规范 Agent 输出。
- **Coder 增强**：将核心逻辑重构至 `src/docops`，支持 Python 调用。
- **质量保证**：增加了 `tests/` 目录并使用 `pytest` 进行了单元测试覆盖。
- **脚本迁移**：`.sh` 和 `.ps1` 脚本现在调用 Python 核心逻辑，提高跨平台一致性。

## 验证
- 单元测试：`cd investment-masters-handbook; $env:PYTHONPATH="."; pytest tests`
- 集成校验：`pwsh -NoProfile -File scripts/validate-docops.ps1`
- 预期：单元测试全部通过，校验脚本输出 `[OK] DocOps evidence chain looks good`

## 风险点与回滚方案
### 风险点
1. **Python 依赖**：核心逻辑已迁移至 Python，若运行环境缺少 Python 或 `PYTHONPATH` 未正确设置，自动化脚本将失效。
2. **证据链约束**：`.cursor/rules/docops-agentops.mdc` 开启了 `alwaysApply`，会对所有 Agent 操作增加文档负担。

### 回滚方案
若需移除此工作流，执行以下操作：
1. 删除目录：`stories/`, `sessions/`, `prompts/`, `docs/features/S-0001-install-docops-agentops/`
2. 删除脚本：`scripts/new-story.*`, `scripts/validate-docops.*`
3. 删除代码：`src/docops/` 和 `tests/test_*.py`
4. 删除规则：`.cursor/rules/docops-agentops.mdc`
5. 删除文档：`AGENT_CONSTITUTION.md` 和 `runbooks/AGENT_BOOTSTRAP_DOCOPS_AGENTOPS.md`