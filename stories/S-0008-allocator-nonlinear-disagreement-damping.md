# S-0008-allocator-nonlinear-disagreement-damping

## 目标
在不增加新 bucket（仍然四桶：stocks/bonds/gold/cash）的前提下，进一步提升 **下行风险表现（Sortino）** 与稳定性：

- **(1) 非线性 + 非对称映射**：risk-on 加仓更慢，risk-off 减仓更快。
- **(2) 连续型分歧抑制**：用 `disagreement_score` 连续衡量专家分歧度，替代二值 `conflict_detected` 的硬开关。

## 验收标准（必须可验证）
- [x] `EnsembleAdjudicator.adjudicate` 输出 `disagreement_score`（0..1），并在 API 的 `secondary.ensemble_adjustment.disagreement_score` 可见。
- [x] `SharpePrimaryAllocator` 支持 `disagreement_score` 连续抑制：分歧越大动作越小；无分歧时接近不抑制。
- [x] `SharpePrimaryAllocator` 使用非线性+非对称映射（risk-on slower / risk-off faster），并支持 YAML 通过 `allocation_policy.mapping_mode/exp_up/exp_down/scale_up/scale_down` 调参。
- [x] 单测通过：`pytest -q tests/test_ensemble.py tests/test_backtest_engine.py`

## 范围 / 非目标
- **范围**：仅优化 `primary` 的映射逻辑与分歧抑制机制；不改变四桶结构。
- **非目标**：本次不做 no-trade band / EWMA 平滑（需要引入上一期状态或请求带 current_allocation），留待下一步。

## 任务拆分
- [x] `EnsembleAdjudicator` 增加 `disagreement_score`（基于 signed/abs contribution 的连续指标）。
- [x] `SharpePrimaryAllocator.allocate(..., disagreement_score=...)`：连续 damping。
- [x] allocator 映射升级为 `asymmetric_power`（默认 exp_up=1.35 / exp_down=0.85）。
- [x] 更新 `config/reasoning_config.yaml` 增加可调参数。
- [x] 更新 `tools/rag_core.py`：把 `disagreement_score` 透传进 allocator，并写入 `secondary.metadata.primary_allocator_inputs`。

## 关联文件（计划/实际）
- `tools/reasoning_core.py`
- `tools/rag_core.py`
- `config/reasoning_config.yaml`

## 进度日志（每次 Agent session 追加）
- 2025-12-29: 初始化 Story。
- 2025-12-29: 完成非线性映射与连续分歧抑制；单测通过。
