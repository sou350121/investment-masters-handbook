# S-0009-backtest-history-workbench 状态

- 状态：已完成
- Story：
  - stories/S-0009-backtest-history-workbench.md
- Prompt：
  - prompts/S-0009-backtest-history-workbench.md
- Failures：
  - sessions/S-0009-backtest-history-workbench/failures.md

## 变更摘要
- 回测结果 API：新增 `/api/backtest/runs` 与 `/api/backtest/runs/{run_id}`，读取 `results/<run_id>/` 输出并转成前端友好 JSON。
- 回测工作台 UI：新增「回测历史」Tab，展示 flow、run 列表、A/B 指标卡片、曲线 sparkline、rebalance timeline。
- 回测脚本增强：写出 `run_config.json`，让网页能显示 tickers / 区间 / 步长。
- 纯静态真实快照：新增 `web/public/backtests/` + `scripts/build_static_backtests_index.py`；前端改为读取静态 `index.json` 与 `backtests/<run_id>/` 下的真实输出，不再依赖 `/api/backtest/*`。

## 验证
- `pytest -q`
- `python scripts/build_static_backtests_index.py`
- `cd web && npm run build`


