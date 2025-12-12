# scripts/

本目录存放 **SSOT 生成** 与 **CI 校验** 脚本。

## 约定
- **SSOT**：`config/investor_index.yaml` + `config/router_config.yaml`
- **生成物**：会被提交到仓库；CI 会检查生成物是否最新（若有 diff 则失败）

## 脚本一览
- `generate_artifacts.py`：从 SSOT 生成/更新派生文档与 `config/decision_rules.generated.json`
- `check_links.py`：Markdown 链接有效性检查（相对路径）
- `validate_front_matter.py`：投资人文档 Front Matter 校验
- `check_router_config.py`：路由配置一致性 + 简易冲突检测
- `scan_sensitive.py`：敏感信息扫描（邮箱/密钥/私钥等）


