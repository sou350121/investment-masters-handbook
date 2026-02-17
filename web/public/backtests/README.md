# Backtests (Static Snapshot)

把你已经跑出来的真实回测输出（`results/<run_id>/`）**原样拷贝**到这里，以便 Web UI 在纯静态模式下展示回测历史（不依赖后端 API）。

## 目录结构（每个 run 一个文件夹）

`web/public/backtests/<run_id>/`

建议包含以下文件（与后端 `/api/backtest/runs/{run_id}` 读取的输出一致）：

- `run_config.json`
- `metrics_A.json` / `metrics_B.json`
- `equity_curve_A.csv` / `equity_curve_B.csv`
- `history_A.csv` / `history_B.csv`
- `comparison.md`（可选）

## 索引文件

运行脚本生成索引（供前端加载 runs 列表）：

```bash
python scripts/build_static_backtests_index.py
```

它会写入：`web/public/backtests/index.json`


