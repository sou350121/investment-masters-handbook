# S-0003-scenario-editor

## 目标
将场景沙盒升级为开发工具，支持在线编辑场景、保存至本地，并提供“一键运行所有场景”的回归测试功能，确保 Policy Gate 逻辑修改后不发生退化。

## 验收标准（必须可验证）
- [x] 支持在线编辑场景（`features` / `expectations`）并保存到 `config/scenarios.yaml`
- [x] 增加批量回归测试接口与 UI（一键运行所有场景并展示汇总与失败详情）

## 范围 / 非目标
- 不修改 RAG 检索/向量库/embedding 等内核逻辑
- 不扩展为完整的权限/鉴权系统

## 任务拆分
- [x] 实现 `POST /api/policy/scenarios` (保存/更新场景)
- [x] 实现 `POST /api/policy/validate_all` (批量校验)
- [x] 前端增加“保存当前场景”按钮
- [x] 前端实现“批量运行全量回归”展示 Scorecard

## 关联文件（计划/实际）
- `services/rag_service.py`
- `web/src/components/InvestorList.tsx`
- `config/scenarios.yaml`

## 进度日志（每次 Agent session 追加）
- 2025-12-23: 从 IMH-TASK-002 迁移并标记为已完成（部分功能在 v1.7.0 已提前完成）。
