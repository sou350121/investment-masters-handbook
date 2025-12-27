# Review Guide（Reviewer Agent）

> 目标：建立“可定位、可执行”的 Review 闭环，减少来回沟通成本。

## 基本原则

- **需求对齐优先**：先对照 Issue 的 Goal/Scope/DoD，确认是否“少做/多做/跑偏”。
- **最小必要建议**：优先给出能 unblock 合并的修改；“可选优化”单独标注，不阻塞。
- **必须可定位**：优先使用 GitHub inline comment；若无法 inline，必须提供 **文件路径:行号**。

## 评论格式（建议）

请按严重级别标注，方便 Coder 排优先级：

- **[blocker]**：不修不能合（错误逻辑/安全/数据损坏/测试缺失导致不可验证）
- **[major]**：建议修复后合（易错/可维护性差/边界情况缺失）
- **[minor]**：小问题（命名/注释/一致性）
- **[nit]**：非阻塞（格式/语气）

每条评论至少包含：

- **定位**：GitHub inline comment 或 `path/to/file:line`（可用 `Lx-Ly`）
- **问题**：现状是什么
- **影响**：为什么重要（关联 DoD / 约束 / 潜在 bug）
- **建议**：给出明确修复方向（必要时贴伪代码/示例）

## 示例

- **[blocker] `services/rag_service.py:L45-L60`**：`/api/policy/scenarios` 读取 YAML 缺少异常处理（文件不存在/格式错误会 500）。  
  - **影响**：DoD 要求接口稳定可用；前端加载会直接失败。  
  - **建议**：捕获 `FileNotFoundError`/`yaml.YAMLError`，返回结构化错误（HTTP 400/500 区分）。

## Scope Check（强制）

- 若发现“超出 Issue 范围”的改动：必须指出具体文件/提交点，并要求移除或拆分到新 Issue。




