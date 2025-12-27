# Coder Task: 实现 Policy Gate 场景沙盒 (Scenario Sandbox)

**ID**: IMH-TASK-001
**状态**: 已完成 (Completed)
**完成日期**: 2025-12-23
**优先级**: 高 (P0)
**需求来源**: Requirement Agent (PM/架构师)

## 1. 目标 (Goal)
在 IMH 系统中引入“场景化测试”能力，允许用户一键模拟经典市场情境（如 2008 金融危机），并验证 Policy Gate 的风险护栏输出是否符合大师逻辑。

## 2. 范围 (Scope)

**In-scope**
- 新增 `config/scenarios.yaml`，定义最少 3 个场景（含 features 与 expectations）
- 新增后端接口 `GET /api/policy/scenarios`（返回场景列表 JSON）
- 前端新增“场景加载器（Scenario Loader）”：
  - 点击场景：自动填充输入框（如 `features`、`portfolio_state`）
  - 执行 Policy Gate 后：将实际输出与 expectations 做对比，展示 ✅ / ❌ 报告

**Out-of-scope**
- 不实现“在线编辑并保存场景”（该能力由 `IMH-TASK-002` 覆盖）
- 不修改向量数据库/检索链路/embedding 与 RAG 内核
- 不引入新的外部依赖（除非 Requirement Agent 明确批准）

## 3. 详细规格 (Spec)

### A. 数据配置 (`config/scenarios.yaml`)
创建一个新配置文件，定义至少 3 个经典场景：
- **场景 1: 极度恐慌 (Crisis 2008)**
    - Features: `vix: 45, credit_spread: 3.5, yield_curve: -0.5`
    - 预期结果: `risk_multiplier < 0.6`, `min_cash > 0.2`
- **场景 2: 科技牛市 (AI Boom 2024)**
    - Features: `vix: 12, market_momentum: 0.8, cpi: 2.5`
    - 预期结果: `risk_multiplier > 1.0`, `max_leverage > 1.0`
- **场景 3: 滞胀震荡 (Stagflation)**
    - Features: `vix: 22, inflation: 6.0, gdp_growth: 0.5`
    - 预期结果: `risk_multiplier ~ 0.8`, `max_invest < 0.08`

### B. 后端 API (`services/rag_service.py`)
- 新增 `GET /api/policy/scenarios` 接口，读取并返回上述 YAML 内容。

### C. 前端 UI (`web/src/components/InvestorList.tsx`)
- 在 Policy Gate 面板中新增 **“场景加载器 (Scenario Loader)”** 组件。
- 点击场景按钮，自动填充 `features`、`portfolio_state` 等 JSON 输入框。
- 执行 `/api/policy/gate` 后，对比 `risk_multiplier` 等实际值与场景预设的“预期阈值”，在界面上通过 ✅ 或 ❌ 显示验证报告。

## 4. 验收标准 (DoD)
1. [x] `config/scenarios.yaml` 存在且格式正确（已扩展至 8 个场景）。
2. [x] `/api/policy/scenarios` 接口返回正确的 JSON 列表。
3. [x] 网页端点击“极度恐慌”场景，输入框自动更新（且会自动切换至“风控护栏”标签页）。
4. [x] 点击“生成护栏”后，界面能显示该场景的“验证通过/失败”状态（支持 ~ 模糊匹配与多维度校验）。
5. [x] 新增：实现 `GET/POST /api/policy/validate_all` 接口，支持一键全量场景自动化回归。

## 5. 限制 (Constraints)
- 不要修改现有的向量数据库和 RAG 核心逻辑。
- 保持前端 Material UI 风格的一致性。
- 代码改动需符合 `agents/coder_agent.md` 中的规范。

## 6. 依赖关系（Dependencies）

- 无（可独立交付）

## 7. 运行/验证方式（Test Plan / Runbook）

- 后端快速验证：
  - 运行：`python services/rag_service.py`
  - 请求：`GET /api/policy/scenarios` 返回 3 个场景列表
- Web 手动验证：
  - 运行：`cd web && npm install && npm run dev`
  - 操作：打开 Policy Gate 面板，点击 “极度恐慌 (Crisis 2008)” 场景
  - 预期：输入框自动填充；执行护栏后显示 ✅ / ❌ 验证结果

---
**审批意见**: 同意执行。
**审批人**: PM Agent
**日期**: 2025-12-14
