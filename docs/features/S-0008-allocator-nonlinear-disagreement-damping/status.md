# S-0008-allocator-nonlinear-disagreement-damping 状态

- 状态：已完成
- Story：
  - stories/S-0008-allocator-nonlinear-disagreement-damping.md
- Prompt：
  - prompts/S-0008-allocator-nonlinear-disagreement-damping.md
- Failures：
  - sessions/S-0008-allocator-nonlinear-disagreement-damping/failures.md

## 变更摘要
- **非线性+非对称 allocator 映射**：risk-on 更慢、risk-off 更快（提升 Sortino 稳定性）。
- **连续型分歧抑制**：新增 `disagreement_score`（0..1）并用于 allocator damping，替代“硬开关”式 conflict 处理。
- **参数外置**：`config/reasoning_config.yaml` 增加 mapping 参数（exp_up/exp_down/scale_up/scale_down）。

## 验证
- `pytest -q tests/test_ensemble.py tests/test_backtest_engine.py`

# S-0008-allocator-nonlinear-disagreement-damping 状态

- 状态：进行中
- Story：
  - stories/S-0008-allocator-nonlinear-disagreement-damping.md
- Prompt：
  - prompts/S-0008-allocator-nonlinear-disagreement-damping.md
- Failures：
  - sessions/S-0008-allocator-nonlinear-disagreement-damping/failures.md
- PR：

## 变更摘要

## 验证
