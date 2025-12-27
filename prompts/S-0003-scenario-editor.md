# Prompt VCS: S-0003-scenario-editor

## 1. 核心提示词 (Master Prompt)
``````markdown
目标：实现场景编辑器与全量回归测试。
约束：支持 ~ 模糊匹配，支持原子性写入 YAML。
``````

## 2. 环境与配置
- 模型：Gemini 3 Flash

### Agent: Coder / 2025-12-23
- 实现了 `validate_all` 后端逻辑。
- 增加了 `POST /api/policy/scenarios` 持久化接口。
- 前端 UI 深度重构，支持 Tabs 切换。
- 完成了回归报告的弹出展示逻辑。
