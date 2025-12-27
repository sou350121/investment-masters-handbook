# S-0004-master-reasoning-board 状态

- 状态：已完成
- Story：
  - stories/S-0004-master-reasoning-board.md
- Prompt：
  - prompts/S-0004-master-reasoning-board.md
- Decisions：
  - docs/features/S-0004-master-reasoning-board/decisions.md

## 变更摘要
- [2025-12-23] 完成 Bootstrap：定义了多大师决策看板的需求与架构。
- [2025-12-23] 后端实现定量裁决引擎 `tools/reasoning_core.py`，支持 Regime 感知的动态权重。
- [2025-12-23] 升级 `api/policy/gate` 接口，整合 CIO Adjudicator 推理输出。
- [2025-12-23] 前端实现 “Decision Trail” 可视化，展示逻辑冲突与裁决路径。
- [2025-12-23] 用户验收通过，功能正式上线。
- [2025-12-24] **参考 @nofx 强化深度会诊的大模型接入与辩论风格**：
  - `tools/llm_bridge.py`：支持 `provider=claude`（Anthropic Messages API），并增强重试/JSON 提取（支持 `<json>...</json>`）。
  - `tools/reasoning_core.py`：新增 nofx 风格 the Master→Personality 映射与角色描述（bull/bear/analyst/contrarian/risk_manager）。
  - `tools/rag_core.py`：委员会 Prompt 引入角色设定，并要求输出 `<reasoning>` + `<json>`（json 为严格对象）。
  - `services/rag_service.py`：`/api/rag/ensemble` 在 metadata 中附带 `experts_personality` 与 `reasoning_preview`，便于审计与 UI 展示。
  - `tests/test_ensemble.py`：覆盖 `<reasoning>/<json>` 输出形式，确保解析稳定。
- [2025-12-27] **实现 NOFX 模式的 Access Token 与 LLM Key 动态切换**：
  - `services/rag_service.py`：优化 `_require_bearer_token` 逻辑，支持识别 `sk-or-` 并在 `rag_ensemble` 中动态注入 `LLMBridge`。
  - `services/rag_service.py`：将向量库加载改为异步 `asyncio.create_task`，解决后端启动卡顿问题。
  - `web/src/components/InvestorList.tsx`：重构聊天 UI，增加“NOFX 风格”Token 登录区，支持持久化到 `localStorage`。
  - `web/src/components/InvestorList.tsx`：增加 Tooltip 提示，说明 Access Token 与 LLM Key 的安全机制。
- [2025-12-28] **深度会诊输出拆分为“一级/二级”**（更可执行 + 更可溯源）：
  - `services/rag_service.py`：`/api/rag/ensemble` 返回 `{ primary, secondary }`；primary 为四类资产配比（sum=100）+ 一句话结论 + confidence；secondary 保留原辩论/引用/裁决结构。
  - `tools/rag_core.py`：提示词 schema 强制输出 primary/secondary。
  - `web/src/components/InvestorList.tsx`：默认展示一级输出；二级输出折叠展开查看。
  - `tests/test_ensemble.py`：新增 tiered response 结构断言与配比约束验证。

## 验证
- 运行：`pwsh -NoProfile -File scripts/validate-docops.ps1`
- 结果：[OK] DocOps evidence chain looks good
- 单测：`cd investment-masters-handbook; $env:PYTHONPATH='.'; pytest tests/test_ensemble.py`
