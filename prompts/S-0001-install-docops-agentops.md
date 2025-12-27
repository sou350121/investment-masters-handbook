# Prompt VCS: S-0001-install-docops-agentops

## 1. 核心提示词 (Master Prompt)
``````markdown
目标：在本项目装上 DocOps + AgentOps Starter Kit。
参考：https://github.com/sou350121/docops-agentops-starter-kit
执行 SOP：先读 runbooks/AGENT_BOOTSTRAP_DOCOPS_AGENTOPS.md。
``````

## 2. 环境与配置
- 模型：Gemini 3 Flash
- 模式：Architect / Coder

## 3. 迭代策略
- 步骤：
  1. 浏览器访问 GitHub 仓库，读取核心脚本与文档内容。
  2. 在本地创建目录结构。
  3. 写入 4 个核心脚本。
  4. 写入引导手册与宪法。
  5. 写入 Cursor Rule (.mdc)。
  6. 创建第一个 Story 并回填证据链。

### Agent: Coder / 2025-12-23
- 完成了所有目录的创建。
- 搬运了 `new-story` 和 `validate-docops` 脚本。
- 搬运了 `AGENT_BOOTSTRAP_DOCOPS_AGENTOPS.md` 和 `AGENT_CONSTITUTION.md`。
- 搬运了 `.cursor/rules/docops-agentops.mdc`。
- 初始化了 S-0001 证据链。

### Agent: Coder / 2025-12-23 (Refactoring & Testing)
- **重构逻辑**：将 `new-story` 和 `validate-docops` 的核心逻辑从 Shell/PowerShell 迁移到 Python (`src/docops/`)。
- **单元测试**：在 `tests/` 目录下实现了 `pytest` 驱动的测试用例，覆盖了验证器和管理器。
- **脚本增强**：更新了 `scripts/` 下的 `.sh` 和 `.ps1` 文件，使其作为 Python 模块的包装器运行。
- **验证通过**：通过了 `pytest` 测试，并确认 `validate-docops` 脚本在当前项目结构下运行正常。

### Agent: Reviewer / 2025-12-23
- **审查结论**：通过。
- **验证通过**：
  1. `python investment-masters-handbook/scripts/validate-docops.py` 输出 `[OK]`。
  2. `pytest` 单元测试全部通过。
  3. 核心文件（宪法、规则、手册、脚本）均已就位且互相引用。
- **风险确认**：已在 `status.md` 中记录 Python 依赖风险及详细回滚方案。
- **建议**：后续 Story 需保持 `failures.md` 的高质量记录，尤其是在复杂重构时。
