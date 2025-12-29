# S-0009-backtest-history-workbench

## 目标
把回测系统生成的 `results/<run_id>/`（metrics / equity_curve / history / comparison）做成一个“很美”的 Web 工作台页面，方便复盘：

- 可视化 **回测流程（flow）**
- 浏览 **run 列表**
- 查看 **A/B 指标**（Sortino/Sharpe/CAGR/MaxDD/Total）
- 查看 **Equity 曲线**
- 查看 **Rebalance Timeline**（每次调仓的配比与输入 brief/risk_bias）

## 验收标准（必须可验证）
- [ ] 后端提供：
  - `GET /api/backtest/runs`：列出可用 run（按时间倒序）与快速指标摘要
  - `GET /api/backtest/runs/{run_id}`：返回 metrics / equity / history / comparison / run_config
- [ ] CLI 回测脚本写出 `run_config.json`（包含 start/end/step_days/tickers 等），供 Web 展示
- [ ] Web UI 新增「回测历史」Tab：展示 flow + run list + 指标卡片 + 曲线 + timeline
- [ ] 纯静态模式：Web UI 不依赖 `/api/backtest/*`，改为读取 `web/public/backtests/index.json` 与 `web/public/backtests/<run_id>/` 下的真实回测输出文件
- [ ] 验证命令通过：
  - `pytest -q`

## 范围 / 非目标
- **范围**：只做“结果可视化与复盘”，不在网页里直接发起回测（避免引入长任务与依赖）
- **非目标**：不引入重型图表库（用轻量 SVG sparkline 即可）

## 关联文件（计划/实际）
- `services/rag_service.py`（Backtest results API）
- `scripts/run_backtest_biweekly.py`（写出 run_config.json）
- `web/src/components/BacktestHistory.tsx`（回测工作台 UI）
- `web/src/components/InvestorList.tsx`（新增 Tab 入口）

## 进度日志（每次 Agent session 追加）
- 2025-12-29: 初始化 Story；实现回测历史工作台（API + Web UI）。



