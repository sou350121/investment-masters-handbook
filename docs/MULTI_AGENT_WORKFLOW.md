# Multi-Agent 协作闭环（IMH）

> 目标：建立“需求澄清 -> Issue -> PR -> Review -> 修复 -> 合并”的稳定闭环，并让每个 Agent **只持有最小必要上下文**。

## 角色分工（最小职责）

- **Requirement Agent（PM/架构师）**：只做需求澄清、方案拆分、产出可执行 Issue（含 DoD/Scope/Constraints）。
- **Coder Agent**：只基于 Issue 实现并提交 PR，不主动扩展范围。
- **Reviewer Agent**：只对 PR 做审查并输出可定位修改意见，推动 Coder 修复。

对应手册：

- `agents/requirement_agent.md`
- `agents/coder_agent.md`
- `agents/reviewer_agent.md`

## 闭环载体（你应该用哪个文件/入口？）

- **Issue（推荐，协作单元）**：使用 GitHub Issue 模板 `IMH Task（Spec -> PR -> Review）`
- **PR（交付单元）**：使用 `.github/PULL_REQUEST_TEMPLATE.md`
- **Review（质量门禁）**：遵循 `.github/REVIEW_GUIDE.md`
- **docs/tasks（仓内任务镜像，可选）**：当你希望任务长期沉淀在仓库时使用（格式与 Issue 同构）

## 流程步骤（强约束）

### 1) 需求澄清 -> Issue（Requirement Agent）

- **必须包含**：Goal / Scope（In & Out）/ Spec / DoD / Constraints / Dependencies / Test Plan
- **拆分规则**：复杂功能拆成多个子 Issue，并显式标注依赖（Depends on / Blocks）
- **最小上下文原则**：不要让 Coder/Reviewer 自己去“找入口/猜需求”

推荐：直接创建 Issue，并在需要时将内容同步到 `docs/tasks/IMH-TASK-xxx.md`。

### 2) Issue -> PR（Coder Agent）

- **只实现 Issue 范围**：禁止顺手重构无关模块
- **PR 必须包含**：
  - 关联 Issue（Closes #）
  - 变更摘要 + Scope 声明
  - 运行与验证命令（How to test）
  - 关键改动点定位（`path:line`）

### 3) Review -> 修复（Reviewer Agent & Coder Agent）

- Reviewer 评论必须 **可定位**：
  - **优先** GitHub inline comment
  - **否则** 提供 `文件路径:行号`（可用 `Lx-Ly`）
- Coder 按严重级别优先修复 `[blocker]`，每轮修复后 push 触发再次 review。

### 4) 合并与并行

- 评审通过后合并；是否并行取决于 Issue 之间依赖关系。

## 提效检查清单（合并前必须过一遍）

- [ ] Issue 包含验收标准（DoD）与边界条件（Scope/Constraints）
- [ ] PR 说明包含改动范围与运行命令（可复现）
- [ ] Review 意见可定位到文件与行号（或 inline）
- [ ] 修复后能触发再次 Review（CI/检查通过）




