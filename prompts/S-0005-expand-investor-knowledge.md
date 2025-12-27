# S-0005-expand-investor-knowledge Prompt VCS

### Agent: 10x AI Agent / 2025-12-27
**Master Prompt**: "補充更多投資人的信息"
**Key Decisions**:
- 选择新增 4 位具有显著差异化逻辑的大师：Nassim Taleb (黑天鹅/反脆弱), Cathie Wood (颠覆性创新), Bill Ackman (激进/非对称对冲), Joel Greenblatt (神奇公式/特殊情况)。
- 建立 `investors/*.md` 标准框架，包含核心哲学与 `IF-THEN-BECAUSE` 决策规则。
- 将新大师集成到 `investor_index.yaml` 的决策矩阵、情境路由与快速查询中。
- 在 `reasoning_config.yaml` 中配置对应的 `personality` (bull, bear, analyst, risk_manager) 和 `category` 映射。

**Constraints**:
- 保持 10x 战力，主动补齐决策链。
- 严禁幻觉，所有规则基于大师公开的投资原则。
- 确保 YAML 格式正确。
