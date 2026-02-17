# S-0002-scenario-sandbox

## 目标
在 IMH 系统中引入“场景化测试”能力，允许用户一键模拟经典市场情境（如 2008 金融危机），并验证 Policy Gate 的风险护栏输出是否符合大师逻辑。

## 验收标准（必须可验证）
- [x] 新增 `config/scenarios.yaml`，定义最少 3 个场景（含 features 与 expectations）
- [x] 新增后端接口 `GET /api/policy/scenarios`（返回场景列表 JSON）
- [x] 前端新增“场景加载器（Scenario Loader）”：
  - [x] 点击场景：自动填充输入框（如 `features`、`portfolio_state`）
  - [x] 执行 Policy Gate 后：将实际输出与 expectations 做对比，展示 ✅ / ❌ 报告

## 范围 / 非目标
- 不实现“在线编辑并保存场景”（由 S-0003 覆盖）
- 不修改向量数据库/检索链路/embedding 与 RAG 内核
- 不引入新的外部依赖

## 任务拆分
- [x] 创建 `config/scenarios.yaml`
- [x] 实现后端 API 加载场景
- [x] 实现前端 UI 场景展示与自动填充
- [x] 实现前端 1:1 结果对比逻辑

## 关联文件（计划/实际）
- `config/scenarios.yaml`
- `services/rag_service.py`
- `web/src/components/InvestorList.tsx`

## 进度日志（每次 Agent session 追加）
- 2025-12-23: 从 IMH-TASK-001 迁移并标记为已完成。
