# S-0006 状态账本：深化投资人决策模型

## 1. 变更摘要
- **目标**：将 18 位核心投资大师的决策模型从 1.0 升级到 2.0，增加深度规则、负向约束和实战工具箱。
- **当前状态**：[COMPLETED] 已完成所有核心人物的深度扩充并集成。

## 2. 证据链 (DocOps)
- **Story**: `stories/S-0006-deepen-investor-profiles.md`
- **Prompt VCS**: `prompts/S-0006-deepen-investor-profiles.md`
- **Failures Log**: `sessions/S-0006-deepen-investor-profiles/failures.md`

## 3. 验证命令 (Verification)
- `python scripts/generate_artifacts.py`
- `pwsh -NoProfile -File scripts/validate-docops.ps1`
- `pytest tests/test_ensemble.py`

## 4. 关键指标
- **深化人物数**: 18 / 18 (核心人物)
- **新增规则数**: 约 150+ 条 (分布在各 .md 文件中)
- **向量库状态**: 就绪 (doc_count 显著增加)
- **DocOps 状态**: 通过
