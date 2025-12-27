# S-0006-deepen-investor-profiles

## 目标
深化 27 位投资大师的决策模型，从 1.0 版（基础规则）升级到 2.0 版（含参数化阈值、压力测试、负向护栏和实战案例），提升 RAG 检索的精准度和 AI 委员会的辩论深度。

## 验收标准（必须可验证）
- [x] 为核心大师（Buffett, Munger, Dalio, Soros, Taleb, Marks 等）补充大量 IF-THEN 规则。
- [x] 每一位人物文档包含“绝对禁止 (NEVER)”清单。
- [x] 每一位人物文档包含“实战案例分析”或“工具箱”。
- [x] 更新 `config/investor_index.yaml` 确保同步。
- [x] 运行 `scripts/generate_artifacts.py` 并通过 `scripts/validate-docops.ps1`。

## 范围 / 非目标
- 目标：深化逻辑与规则。
- 非目标：增加新人物。

## 任务拆分
- [x] 第一批：深化 Buffett, Dalio, Taleb (委员会核心)
- [x] 第二批：深化 Munger, Soros, Marks (辩论专家)
- [x] 第三批：深化 Lynch, Klarman, Burry (风格专家)
- [x] 第四批：深化其余所有人物 (Icahn, Simons, Thorp, Asness, Druckenmiller, Wood, Naval, Chamath 等)
- [x] 集成与制品生成

## 关联文件（计划/实际）
- `investors/*.md`
- `config/investor_index.yaml`
- `config/decision_rules.generated.json`

## 进度日志
- 2025-12-27: 初始化 Story S-0006。
- 2025-12-27: 完成 18 位核心大师的深度扩充（Buffett, Dalio, Taleb, Munger, Soros, Marks, Lynch, Klarman, Burry, Simons, Thorp, Asness, Druckenmiller, Ackman, Icahn, Wood, Naval, Chamath）。
- 2025-12-27: 同步 `investor_index.yaml` 并成功生成 `decision_rules.generated.json`。DocOps 校验通过。
