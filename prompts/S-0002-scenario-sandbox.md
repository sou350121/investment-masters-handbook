# Prompt VCS: S-0002-scenario-sandbox

## 1. 核心提示词 (Master Prompt)
``````markdown
目标：实现 Policy Gate 场景沙盒。
约束：保持现有 RAG 内核不动。
输出：✅/❌ 报告。
``````

## 2. 环境与配置
- 模型：Gemini 3 Flash

## 3. 迭代策略
- 迁移自旧任务 IMH-TASK-001。

### Agent: Coder / 2025-12-23
- 完成了 scenarios.yaml 的初始定义。
- 实现了后端加载接口。
- 完成了前端 UI 的首次集成。
