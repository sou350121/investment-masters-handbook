# Prompt VCS: S-0008-allocator-nonlinear-disagreement-damping

## 1. 核心提示词 (Master Prompt)
```markdown
目标：实现 S-0008-allocator-nonlinear-disagreement-damping。
约束：只改动允许目录；不要引入与需求无关的重构。
输出：必须提供验证命令，并在 PR description 回填 story/prompt/failures 链接。
```

## 2. 环境与配置
- 模型：
- 模式：

## 3. 迭代策略
- 如果偏航：回到验收标准逐条对齐。

## 4. 进度日志（Agent Session）
### Agent: coder / 2025-12-29
- 目标：在四桶结构不变下，提升 Sortino/稳定性。
- 关键改动：
  - (1) allocator 映射升级为非线性+非对称（risk-on slower / risk-off faster）。
  - (2) 用 `disagreement_score` 做连续 damping，替代 conflict 的硬开关。
- 文件：
  - `tools/reasoning_core.py`（EnsembleAdjudicator + SharpePrimaryAllocator）
  - `tools/rag_core.py`（透传 disagreement_score + metadata）
  - `config/reasoning_config.yaml`（新增 mapping 参数）
- 验证：`pytest -q tests/test_ensemble.py tests/test_backtest_engine.py`