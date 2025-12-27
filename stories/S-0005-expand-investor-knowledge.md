# S-0005-expand-investor-knowledge

## 目标
扩展投资大师手册的知识库，新增 4 位具有显著差异化投资逻辑的大师（塔勒布、木头姐、阿克曼、格林布拉特），提升系统在极端风险对冲、创新捕捉及量化价值方面的决策质量。

## 验收标准（必须可验证）
- [x] 为 Nassim Taleb, Cathie Wood, Bill Ackman, Joel Greenblatt 各创建一个 `.md` 文档，包含至少 10 条 IF-THEN 规则。
- [x] 更新 `config/investor_index.yaml`，包含新大师的风格、适用场景和权重矩阵。
- [x] 运行 `scripts/generate_artifacts.py`，确保 `config/decision_rules.generated.json` 已合并新规则。
- [x] 运行 `scripts/validate-docops.ps1` 校验全链路证据链。

## 范围 / 非目标
- 目标：核心决策框架、IF-THEN 规则、RAG 索引。
- 非目标：大师的详细生平传记（仅保留对投资有意义的 intro）。

## 任务拆分
- [x] 实现 Nassim Taleb 决策框架 (`nassim_taleb.md`)
- [x] 实现 Cathie Wood 决策框架 (`cathie_wood.md`)
- [x] 实现 Bill Ackman 决策框架 (`bill_ackman.md`)
- [x] 实现 Joel Greenblatt 决策框架 (`joel_greenblatt.md`)
- [x] 集成到 `investor_index.yaml` 并生成制品

## 关联文件（计划/实际）
- `investors/nassim_taleb.md`
- `investors/cathie_wood.md`
- `investors/bill_ackman.md`
- `investors/joel_greenblatt.md`
- `config/investor_index.yaml`
- `config/decision_rules.generated.json`

## 进度日志（每次 Agent session 追加）
- 2025-12-27: 初始化 Story 与证据链。
- 2025-12-27: 完成 4 位大师决策框架编写、索引更新及制品生成。验证通过。
