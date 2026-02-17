# S-0007-committee-sharpe-allocator

## 目标
将 `/api/rag/ensemble` 的 **一级输出 `primary.target_allocation`** 从“LLM 直接给配比”升级为 **Sharpe 优先的确定性 Allocator**：\n
- 降低数值噪音与随机漂移\n
- 在专家分歧时自动“减小动作”（conflict damping）\n
- 让回测调参与稳定性优化成为可能

## 验收标准（必须可验证）
- [x] `/api/rag/ensemble` 的 `primary.target_allocation` **由后端确定性生成**（输入：regime_id + adjudicator 的 `final_multiplier_offset` + `conflict_detected`），并保证四桶 sum=100。
- [x] `secondary.metadata.primary_generated_by == "allocator_sharpe_v1"`，并在 `secondary.metadata.primary_allocator_inputs` 记录 allocator 输入。
- [x] `config/reasoning_config.yaml` 支持 `allocation_policy` 覆盖（amplitude/conflict_damping/min_cash/max_cash/regime_bases）。
- [x] 单测通过：`pytest -q tests/test_ensemble.py tests/test_backtest_engine.py`。
- [x] 清理本地临时模拟脚本/数据，并在 `.gitignore` 中忽略回测临时产物（避免误提交）。

## 范围 / 非目标
- **范围**：仅优化 `primary` 的生成方式与稳定性（Sharpe-first）；不改变二级输出结构与证据链。
- **非目标**：本次不引入更复杂的“turnover penalty/最小变动阈值”到 API 请求层（需要新增 current_allocation 字段与前端联动）。

## 任务拆分
- [x] 新增 `SharpePrimaryAllocator`（确定性配比生成）并支持 YAML 覆盖。
- [x] 在 `tools/rag_core.py::run_ensemble_committee` 中接入 allocator，写入 `secondary.metadata.primary_generated_by/inputs`。
- [x] 提示词补充：告知 LLM primary 配比会被服务端重算，重点输出 secondary 的 impact/confidence/citations。
- [x] 更新单测：断言 `primary_generated_by` 字段存在。
- [x] 清理临时模拟文件并更新 `.gitignore`。

## 关联文件（计划/实际）
- `tools/reasoning_core.py`
- `tools/rag_core.py`
- `services/rag_service.py`
- `config/reasoning_config.yaml`
- `tests/test_ensemble.py`
- `.gitignore`

## 进度日志（每次 Agent session 追加）
- 2025-12-29: 初始化 Story。
- 2025-12-29: 完成 Sharpe-first allocator 接入、配置覆盖、单测与清理。
