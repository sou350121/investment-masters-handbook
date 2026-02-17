# Prompt VCS: S-0007-committee-sharpe-allocator

## 1. 核心提示词 (Master Prompt)
```markdown
目标：实现 S-0007-committee-sharpe-allocator。
约束：只改动允许目录；不要引入与需求无关的重构。
输出：必须提供验证命令，并在 PR description 回填 story/prompt/failures 链接。
```

## 2. 环境与配置
- 模型：LLM in-loop（OpenAI/OpenRouter/Claude 均可，经 `LLMBridge`）
- 模式：Sharpe-first primary allocator（primary 配比由后端确定性生成）

## 3. 迭代策略
- 如果偏航：回到验收标准逐条对齐。

## 4. 进度日志（Agent Session）
### Agent: coder / 2025-12-29
- 关键决策：primary.target_allocation 改为确定性生成（Sharpe 优先），输入来自 adjudicator 的 `final_multiplier_offset` + `conflict_detected`（并支持 YAML 外置调参）。
- 修改点：
  - `tools/reasoning_core.py`：新增 `SharpePrimaryAllocator` 与 `allocation_policy`。
  - `tools/rag_core.py`：在 `run_ensemble_committee` 用 allocator 重算 primary，并写入 `secondary.metadata.primary_generated_by/inputs`。
  - `tests/test_ensemble.py`：增加对 `primary_generated_by` 的断言。
- 验证：`pytest -q tests/test_ensemble.py tests/test_backtest_engine.py`
