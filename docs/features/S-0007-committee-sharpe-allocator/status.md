# S-0007-committee-sharpe-allocator 状态

- 状态：已完成
- Story：
  - stories/S-0007-committee-sharpe-allocator.md
- Prompt：
  - prompts/S-0007-committee-sharpe-allocator.md
- Failures：
  - sessions/S-0007-committee-sharpe-allocator/failures.md
- PR：

## 变更摘要
- **Sharpe 优先一级输出**：`primary.target_allocation` 由后端确定性 Allocator 生成（基于 adjudicator 的 `final_multiplier_offset` 与 `conflict_detected`），降低 LLM 数值噪音与抖动。
- **可调参数外置**：在 `config/reasoning_config.yaml` 新增 `allocation_policy`（amplitude/conflict_damping/min_cash/max_cash/regime_bases）。
- **可追溯**：`secondary.metadata.primary_generated_by="allocator_sharpe_v1"`，并记录 `primary_allocator_inputs`。

## 验证
- `pytest -q tests/test_ensemble.py tests/test_backtest_engine.py`
