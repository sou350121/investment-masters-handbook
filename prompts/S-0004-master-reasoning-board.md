# Prompt VCS: S-0004-master-reasoning-board

## 1. 核心提示词 (Master Prompt)
``````markdown
目标：实现多大师融合推理看板。
角色：你现在是后端架构师。
核心逻辑：
1. 编写路由逻辑，从 RAG 检索结果中聚合 top-N 大师。
2. 设计 System Prompt，让 LLM 扮演这些大师进行对话式推理。
3. 确保输出格式支持前端解析引用。
``````

## 2. 环境与配置
- 模型建议：Claude 3.5 Sonnet 或 GPT-4o (由于逻辑推演需求高)
- 依赖：FastAPI, LangChain, React

## 3. 迭代策略
- 任务拆分见 stories/S-0004-master-reasoning-board.md。

### Agent: PM/Architect / 2025-12-23
- 完成了需求定义与架构决策。
- 定义了「专家选择」与「两階段合成」協議。
- 确认 Coder 已按照「定量合成+自动裁决」逻辑完成开发。
- 用户已完成最终验收，功能状态更新为「已完成」。

### Agent: Coder / 2025-12-23
- **LLM 接入（参考 @nofx）**：新增 `tools/llm_bridge.py`，以 OpenAI-compatible Chat Completions 为统一协议，通过环境变量配置：
  - `LLM_PROVIDER / LLM_API_KEY / LLM_BASE_URL / LLM_MODEL`
  - 支持 `LLM_BASE_URL` 末尾 `#` 作为 full URL（不自动拼接 `/chat/completions`）
  - 默认超时 5s（可用 `LLM_TIMEOUT_S` 覆盖）
- **后端新接口**：在 `services/rag_service.py` 新增 `POST /api/rag/ensemble`：
  Top-20 规则命中 → 选出 2-3 位大师 → 生成结构化输出（共识/分歧/合意建议 + 引用）。
- **定量合成输出**：强制返回 `ensemble_adjustment`：
  `final_multiplier_offset / primary_expert / conflict_detected / resolution`。
- **前端深度会诊**：Next.js 新增代理路由 `web/src/app/api/rag/ensemble/route.ts`；在 `InvestorList.tsx` 增加“**大师深度会诊**”开关，展示推理过程与可点击引用。
- **引用可跳转**：在 `InvestorDetail.tsx` 的规则卡片增加锚点 `id="rule-<rule_id>"`，前端引用可跳到对应规则。
- **测试**：新增 `tests/test_ensemble.py`，mock LLM 输出 JSON，确保 `pytest` 稳定通过。

### Agent: Reviewer / 2025-12-23
- **审查结论**：通过。
- **验证通过**：
  1. `POST /api/rag/ensemble` 接口功能完整，支持多大师路由与逻辑合成。
  2. `pytest tests/test_ensemble.py` 全部通过，覆盖了定量调整参数校验。
  3. 前端“大师深度会诊”开关逻辑正确，引用跳转（Anchor）精准指向具体规则卡片。
  4. 证据链完整：Story/Prompt/Failures/Status/Decisions 均已更新。
- **风险点确认**：已确认 LLM 延迟风险，前端已增加 Loading 状态提示。
- **建议**：`ensemble_adjustment` 的 `final_multiplier_offset` 目前仅由 LLM 生成，后续可考虑增加基于规则得分的启发式校准以防幻觉。

### Agent: Coder / 2025-12-24
- **目标**：参考 `@nofx` 的多 AI Debate 风格，把“深度会诊”从“单一总结”升级为“角色驱动的冲突→共识→定量输出”。
- **LLM 接入增强（对齐 nofx/mcp）**：
  - `tools/llm_bridge.py` 增强为多 Provider：默认 OpenAI-compatible；新增 `provider=claude`（Anthropic Messages API）。
  - 支持 `LLM_BASE_URL` 末尾 `#` 表示 full URL（不拼接 path）。
  - 增强重试：除 429/5xx 外，增加 nofx 风格的可重试网络错误字符串匹配。
  - JSON 提取增强：支持 `<json>...</json>` 以适配 nofx 风格“先 reasoning 后 json”的输出。
- **委员会提示词升级**：在 `tools/rag_core.py` 中对每位专家注入 `personality`（bull/bear/analyst/contrarian/risk_manager），并要求输出：
  - `<reasoning>...</reasoning>`（自然语言辩论过程）
  - `<json>{...}</json>`（严格结构化 JSON 供前端消费）
- **审计补强**：`/api/rag/ensemble` 的 `metadata` 增加 `experts_personality` 与 `reasoning_preview`，用于追踪“为什么偏向某位大师”。

### Agent: Coder / 2025-12-27
- **目标**：实现 NOFX 模式的“钥匙随身带”安全架构，并优化深度会诊的 UI/UX。
- **NOFX 安全模式 (Dynamic Key Injection)**：
  - `services/rag_service.py`：重构 `_require_bearer_token`，现在它是一个“双重识别器”。
    - 如果是 `IMH_API_TOKEN`（暗号），则放行并使用后端配置的 `LLM_API_KEY`。
    - 如果是以 `sk-or-` 或 `sk-` 开头的 Token，则将其识别为临时 LLM Key，并在 `rag_ensemble` 中动态注入 `LLMBridge`。
  - `tools/llm_bridge.py`：新增 `set_api_key()` 方法，允许在请求级别动态覆盖 API Key。
- **UX 与性能优化**：
  - **异步初始化**：`services/rag_service.py` 的 `startup_event` 现在使用 `asyncio.create_task` 在后台加载向量库，API 响应更快，不再阻塞服务器启动。
  - **Token 登录工作台**：`web/src/components/InvestorList.tsx` 新增 NOFX 风格的登录面板，支持保存 Token 到 `localStorage`。
  - **Tooltip 引导**：添加了 Tooltip 文字提示，详细解释了本地存储的安全机制，降低用户认知负担。
- **验证**：
  - 手动测试：前端填入 OpenRouter Key 后保存，开启深度会诊模式，请求成功返回。
  - 验证了 401 Unauthorized 逻辑：当 Token 错误且不符合 Key 格式时，准确报错。
