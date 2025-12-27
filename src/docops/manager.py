import os
from datetime import datetime

def create_new_story(story_id, title, root_dir="."):
    story_filename = f"{story_id}-{title}.md"
    story_path = os.path.join(root_dir, "stories", story_filename)
    prompt_path = os.path.join(root_dir, "prompts", story_filename)
    session_dir = os.path.join(root_dir, "sessions", f"{story_id}-{title}")
    feature_dir = os.path.join(root_dir, "docs/features", f"{story_id}-{title}")
    failures_path = os.path.join(session_dir, "failures.md")
    status_path = os.path.join(feature_dir, "status.md")

    os.makedirs(os.path.dirname(story_path), exist_ok=True)
    os.makedirs(os.path.dirname(prompt_path), exist_ok=True)
    os.makedirs(session_dir, exist_ok=True)
    os.makedirs(feature_dir, exist_ok=True)
    os.makedirs(os.path.join(feature_dir, "screenshots"), exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")

    story_content = f"""# {story_id}-{title}

## 目标

## 验收标准（必须可验证）
- [ ]

## 范围 / 非目标

## 任务拆分
- [ ]

## 关联文件（计划/实际）
- 

## 进度日志（每次 Agent session 追加）
- {today}: 初始化
"""

    prompt_content = f"""# Prompt VCS: {story_id}-{title}

## 1. 核心提示词 (Master Prompt)
```markdown
目标：实现 {story_id}-{title}。
约束：只改动允许目录；不要引入与需求无关的重构。
输出：必须提供验证命令，并在 PR description 回填 story/prompt/failures 链接。
```

## 2. 环境与配置
- 模型：
- 模式：

## 3. 迭代策略
- 如果偏航：回到验收标准逐条对齐。
"""

    failures_content = f"""# 失败路径记录 (Failure Log)

## 尝试 #1
- 日期：{today}
- 现象：
- 根因分析：
- 教训/对策：
"""

    status_content = f"""# {story_id}-{title} 状态

- 状态：进行中
- Story：
  - stories/{story_filename}
- Prompt：
  - prompts/{story_filename}
- Failures：
  - sessions/{story_id}-{title}/failures.md
- PR：

## 变更摘要

## 验证
"""

    with open(story_path, "w", encoding="utf-8") as f:
        f.write(story_content)
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt_content)
    with open(failures_path, "w", encoding="utf-8") as f:
        f.write(failures_content)
    with open(status_path, "w", encoding="utf-8") as f:
        f.write(status_content)

    print(f"Created:\n- {story_path}\n- {prompt_path}\n- {session_dir}\n- {feature_dir}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python manager.py <ID> <TITLE>")
        sys.exit(1)
    create_new_story(sys.argv[1], sys.argv[2])



