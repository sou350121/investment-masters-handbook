# S-0004-master-reasoning-board

## 目标
实现“大师决策委员会 (Investment Committee Engine)”，将 RAG 从单纯的片段检索提升为基于 Regime 感知的定量融合推理。系统将模拟多位相关大师（如巴菲特 + 达利奥）的逻辑冲突，并由“首席投资官 (CIO) Agent”进行自动裁决，输出最终的风险乘数调整建议。

## 验收标准（必须可验证）
- [x] **后端：定量裁决引擎 (Adjudicator)**
    - [x] 升级 `api/policy/gate` 接口，支持输出 `ensemble_adjustment` 结构。
    - [x] 实现 **Regime-Weight Matrix**：在不同市场环境下（Crisis/Bull/Neutral）自动分配大师规则的权重。
    - [x] 实现 **自动冲突解决**：CIO Agent 必须能针对“集中 vs 分散”等逻辑碰撞给出确定性的定量参数建议（如 `risk_multiplier: -0.2`）。
- [x] **提示词：CIO Master Prompt**
    - [x] 必须输出结构化 JSON，包含：专家贡献度、冲突分析、裁决理由。
- [x] **前端：决策审计轨迹 (Decision Trail) UI**
    - [x] 展示“为什么这么调”的完整路径（命中规则 -> 识别冲突 -> 自动裁决 -> 参数变动）。
- [x] **性能**
    - [x] 核心推理逻辑响应需支持流式或在 5s 内完成。

## 范围 / 非目标
- 暂不接入实时下单系统。
- 暂不修改底层 Embedding 模型。

## 任务拆分
- [x] **Phase 1: 裁决逻辑开发**
    - [x] `tools/reasoning_core.py`: 实现 Ensemble 算法与权重矩阵。
- [x] **Phase 2: 接口与提示词集成**
    - [x] `services/rag_service.py`: 整合推理链条至 Policy Gate。
- [x] **Phase 3: 前端决策轨迹可视化**
    - [x] `web/src/components/InvestorList.tsx`: 新增审计轨迹视图。

## 关联文件
- `services/rag_service.py`
- `tools/reasoning_core.py`
- `web/src/components/InvestorList.tsx`
- `docs/features/S-0004-master-reasoning-board/decisions.md`

## 进度日志（每次 Agent session 追加）
- 2025-12-23: PM/Architect 初始化 Story，定义验收标准。
- 2025-12-23: 更新为“自动裁决+定量合成”模式。
- 2025-12-23: Coder 完成全部功能开发，通过全量回归测试，用户验收通过。
- 2025-12-24: 参考 @nofx 强化 LLM 辩论风格，引入专家人格化（Personas）与 `<reasoning>` 思考链。
- 2025-12-27: 实现 NOFX 模式安全架构（钥匙随身带），优化前端 Token 登录 UI 与异步初始化性能。
