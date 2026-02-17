## 关联 Issue

- Closes #

## 变更摘要

- 

## 范围声明（Scope）

**In-scope**
- 

**Out-of-scope**
- 

## 运行与验证（How to test）

> 贴出你实际运行过的命令与结果（不要只写“已测试”）。

- **后端/脚本**：
  - `python scripts/check_links.py`
  - `python scripts/validate_front_matter.py`
  - `python scripts/check_router_config.py`
  - `python scripts/scan_sensitive.py`
  - `python scripts/generate_artifacts.py && git status --porcelain`
- **Web（如涉及）**：
  - `cd web && npm install && npm run dev`
  - 手动步骤：
    - 
  - 预期结果：
    - 

## 风险 & 回滚

- **风险点**：
  - 
- **回滚方式**：
  - `git revert <commit>`

## Reviewer 指引（便于定位）

> Reviewer 要求：优先使用 GitHub inline comment；若无法 inline，必须提供 **文件路径:行号**。

- **关键改动点**：
  - `path/to/file:line` - 说明

## Checklist

- [ ] 只实现 Issue 定义的范围（无额外扩展/无无关重构）
- [ ] 不触碰 Issue 约束中明确禁止的模块/文件
- [ ] CI 通过（或说明失败原因与修复计划）
- [ ] 生成文件已同步（如涉及）且 `git status` 干净
- [ ] PR 描述包含可复现的验证步骤




