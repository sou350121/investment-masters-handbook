# S-0005 状态账本：扩展投资人知识库

## 1. 变更摘要
- **目标**：新增 4 位投资大师（Taleb, Wood, Ackman, Greenblatt）以增强系统的风险对冲与创新投资决策能力。
- **当前状态**：[COMPLETED] 已完成 4 位大师的扩展并验证。

## 2. 证据链 (DocOps)
- **Story**: `stories/S-0005-expand-investor-knowledge.md`
- **Prompt VCS**: `prompts/S-0005-expand-investor-knowledge.md`
- **Failures Log**: `sessions/S-0005-expand-investor-knowledge/failures.md`

## 3. 验证命令 (Verification)
- `pwsh -NoProfile -File scripts/validate-docops.ps1`
- `python scripts/generate_artifacts.py`
- `pytest tests/test_ensemble.py`

## 4. 关键指标
- **新增投资人**: 4 / 4
- **新增规则数**: 24 (4 大师 x 6 核心规则)
- **向量库就绪**: 是 (doc_count: 531)
