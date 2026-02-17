# Agent Bootstrap: DocOps + AgentOps（把 repo + 這份文件丟給 agent 就能跑）

目的：讓任何 Cursor / 多 agent 在只讀一份 Markdown的情況下，就能在本 repo 內把 DocOps + AgentOps 的「證據鏈閉環」跑起來：
Story（SSOT）→ Prompt/Failures → Code/Test → Ledger(status) →（可選）Issue/PR

## 0) 你要怎麼用（人類只做兩件事）
把這個 repo（GitHub link 或本地 workspace）給 agent。
在 chat 只說一句：
「先讀 runbooks/AGENT_BOOTSTRAP_DOCOPS_AGENTOPS.md，之後所有輸出請嚴格照 SOP 跑。」

然後就讓 agent 自己做完：建/補齊證據鏈、對齊驗收、寫狀態帳本、給驗證命令。

## 0.5) 把這套套用到「你自己的專案 repo」（新手版）

适用场景：你只知道这个 starter kit 的 GitHub 地址，但你希望 agent 把同一套 DocOps+AgentOps 证据链搬到你自己的项目中。

### A) 你需要提供给 agent 的东西（最少）
1. 你的项目 repo（GitHub link 或本地路径）
2. 你要做的 story id + title（例如 S-0001 add-login）

### B) agent 在你的项目里应该做的事（最小 checklist）
1. **把骨架复制进你的 repo**（或在你的 repo 内创建同等结构）：
   `stories/`, `prompts/`, `sessions/`, `docs/features/`, `issues/`, `scripts/`, `runbooks/`, `.cursor/`
2. **生成 story 骨架**（推荐用脚本）：
   - Windows：`pwsh -NoProfile -File scripts/new-story.ps1 -Id <ID> -Title <kebab-title>`
   - Bash：`bash scripts/new-story.sh <ID> <kebab-title>`
3. **按 story 验收标准交付并回填证据链**：
   `prompts/<id>.md`、`docs/features/<id>/status.md`、（必要时）`sessions/<id>/failures.md`
4. **跑验证命令并把命令写回 status ledger**：
   - `pytest`
   - Windows：`pwsh -NoProfile -File scripts/validate-docops.ps1`
   - CI/Linux：`bash scripts/validate-docops.sh`

### C) 可直接贴给 agent 的消息模板
你是工程交付型代理，请严格按 DocOps+AgentOps SOP 执行，不要扩大范围。

请先阅读并遵守：`runbooks/AGENT_BOOTSTRAP_DOCOPS_AGENTOPS.md`

我的项目：`<YOUR_REPO_URL_OR_PATH>`
目标 Story：`stories/<ID>-<TITLE>.md`（若不存在，请先用脚本创建；不要自创 id）

约束：
- 只改动允许目录；不引入重型框架/不做大规模重构
- 不写入任何 token/密钥

交付要求：
1. 逐条对齐 story 的验收标准实现
2. 必须回填证据链：
   - `prompts/<id>.md`（记录 master prompt/关键决策）
   - `docs/features/<id>/status.md`（变更摘要 + 验证命令）
   - `sessions/<id>/failures.md`（仅当真的失败/偏航才写）
3. 必须提供可复制验证命令：`pytest` + `validate-docops`（Windows/CI）

## 1) 最小工作規則（必須遵守）
1. **SSOT**：需求正文只認 `stories/S-xxxx-*.md`。
2. **允許改動目錄**：`src/`, `tests/`, `stories/`, `prompts/`, `sessions/`, `docs/features/`, `issues/`, `.github/`, `scripts/`, `runbooks/`, `.cursor/`
3. **禁止**：把任何 token/密鑰寫入 repo；未經授權不要引入重型框架/大改。
4. **每次交付必須回填證據鏈**：
   - `prompts/<story>.md`：追加本次 session 的 master prompt/關鍵決策
   - `docs/features/<story>/status.md`：變更摘要 + 驗證命令（可複製執行）
   - `sessions/<story>/failures.md`：只有真的偏航/失敗/回滾/重大糾結才記（高信噪比）

### 1.1) 需求 Agent（PM/架构师）Scope Guardrails（强制）

目标：避免 PM/架构师 agent 因为上下文溢出/不确定而“补完需求”，做出 roadmap 以外的东西。

1. **只认 SSOT**：只基于 `stories/<id>.md`（与已批准的 `docs/features/<id>/decisions.md`）推导；不得新增 roadmap 以外需求。
2. **只能做三件事**：需求澄清、架构方案、任务拆分（拆到验收点 + 文件/模块）。
3. **任何扩范围必须先问**：以“范围变更请求”形式列出新增点/收益/成本/风险 → 等人类确认 → 才能回写 story 并继续。
4. **Context Overflow Fallback**（上下文快爆就降级）：
   - 先把“共识/边界/假设/待确认问题/风险”写回 story 或 decisions
   - 只输出“给 coder 的下一步任务清单”，停止发散

## 2) 一鍵命令（agent 可以自行跑）

只要能跑其中一組即可（Windows/CI 皆可用）。

- **驗證證據鏈**：
  - Windows：`pwsh -NoProfile -File scripts/validate-docops.ps1`
  - Bash/CI：`bash scripts/validate-docops.sh`
- **跑測試**：
  - `python -m pip install pytest`
  - `pytest`
- **新建 story 骨架**（推薦，會自動建好證據鏈檔案）：
  - Windows：`pwsh -NoProfile -File scripts/new-story.ps1 -Id S-0002 -Title add-login`
  - Bash：`bash scripts/new-story.sh S-0002 add-login`

## 3) Master Prompt（直接貼到 Cursor chat）

### A) 新 Story（從 0 開始）
你是工程交付型代理，請嚴格按 DocOps+AgentOps SOP 執行，不要擴大範圍。

目標：在此 repo 內完成一個 Story 的交付閉環。

你必須先做「Bootstrap」：
1) 列出你要做的目標 story 檔案：`stories/S-xxxx-*.md`（若使用者未給 id，請先詢問；不要自創）
2) 若證據鏈檔案不存在，請用腳本建立：
   - Windows: `pwsh -NoProfile -File scripts/new-story.ps1 -Id <ID> -Title <kebab-title>`
   - Bash: `bash scripts/new-story.sh <ID> <kebab-title>`
   證據鏈包含：`prompts/<story>.md`、`sessions/<story>/failures.md`、`docs/features/<story>/status.md`
3) 讀取 story，逐條對齊「驗收標準」並實作：只改動允許目錄，不引入重型框架/大重構。
4) 補測試（`tests/`），確保 `pytest` 會過。
5) 更新 `prompts/<story>.md`：追加一段「### Agent: <name/role> / <date>」並記錄本次 master prompt/關鍵決策/關鍵約束。
6) 更新 `docs/features/<story>/status.md`：寫清變更摘要 + 完整驗證命令（至少 `pytest` + `validate-docops`）
7) 只有發生偏航/失敗/回滾/重大糾結時才更新 `sessions/<story>/failures.md`（保持高信噪比）。
8) 最後輸出：完成狀態 + 涉及的檔案清單 + 可複製執行的驗證命令。

### B) 延續既有 Story（你只要做這次變更）
你是工程交付型代理，請嚴格按 `stories/<id>.md` 的驗收標準執行，不要擴大範圍。

請先做：
1) 讀 `stories/<id>.md`，列出每條驗收標準的對應實作點
2) 確認證據鏈齊全：`prompts/<id>.md`、`sessions/<id>/failures.md`、`docs/features/<id>/status.md`
3) 若缺檔，補齊（可用 `scripts/new-story.*` 或手動補同名路徑）

實作時：
- 只改動允許目錄
- 每做一個驗收點就同步更新測試與 `status.md` 的變更摘要（避免漏）

結尾必須提供可複製的驗證命令：`pytest` + `validate-docops`。

### C) 多 Agent 分工（同一個 Story，避免斷鏈）
你是多代理協作中的其中一個 agent。你只能在同一個 canonical story 下工作：`stories/<id>.md`。

協作規則：
1) 你只負責 story 任務拆分中的一段（先說清楚你負責哪一段）
2) 你所有改動都要回填到同一套證據鏈：
   - `prompts/<id>.md`：用小節追加「### Agent: <role/name> / <date>」記錄你做了什麼與關鍵決策
   - `docs/features/<id>/status.md`：在變更摘要追加你做的部分，並補充你新增/更新的驗證命令（如有）
3) 若你遇到偏航/失敗路徑，才在 `sessions/<id>/failures.md` 新增「嘗試 #n」
4) 任何與驗收/範圍相關的结论，必须回写到 story 或 `docs/features/<id>/decisions.md`（若存在）

## 4) Agent 交付檢查清單（最後一分鐘自查）
- [ ] 我明確指出了 canonical story：`stories/<id>.md`
- [ ] 我逐條對齊 story 的验收标准（每条都有对应变更或理由）
- [ ] 我更新了 `prompts/<id>.md`（新增本次 agent 小节）
- [ ] 我更新了 `docs/features/<id>/status.md`（变更摘要 + 验证命令）
- [ ] 我提供了可复制的验证命令：`pytest` + `validate-docops`
- [ ] 我没有写入任何 token/密鑰


