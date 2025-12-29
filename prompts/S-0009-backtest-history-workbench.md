# Prompt VCS: S-0009-backtest-history-workbench

## 1. 核心提示词 (Master Prompt)
```markdown
目标：实现 S-0009-backtest-history-workbench（回测历史可视化工作台）。
约束：不引入重型图表库；结果读取需防路径穿越；遵守 DocOps 证据链。
输出：提供可验证命令，并在 status ledger 记录验证结果。
```

## 2. 环境与配置
- 后端：FastAPI (`services/rag_service.py`)
- 前端：Next.js 静态导出 + MUI（通过后端托管 `web/out`）

## 3. 迭代策略
- 先提供“读结果的 API”，再做 UI 展示；避免前端直读文件系统。
- 只做“查看/复盘”，不在网页中启动回测（避免长任务与权限问题）。

## 4. 进度日志（Agent Session）
### Agent: coder / 2025-12-29
- 新增后端：
  - `GET /api/backtest/runs`
  - `GET /api/backtest/runs/{run_id}`
- 新增前端：
  - `web/src/components/BacktestHistory.tsx`
  - `InvestorList` 增加「回测历史」Tab
- 回测脚本增强：`scripts/run_backtest_biweekly.py` 写出 `run_config.json`
- 验证：`pytest -q`


