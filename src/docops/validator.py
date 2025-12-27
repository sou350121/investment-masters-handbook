import os
import re
import sys

def validate_docops(root_dir="."):
    stories_dir = os.path.join(root_dir, "stories")
    prompts_dir = os.path.join(root_dir, "prompts")
    sessions_dir = os.path.join(root_dir, "sessions")
    features_dir = os.path.join(root_dir, "docs/features")

    if not os.path.exists(stories_dir):
        print(f"[FAIL] Stories directory not found: {stories_dir}")
        return False

    stories = [f for f in os.listdir(stories_dir) if f.endswith(".md")]
    if not stories:
        print(f"[FAIL] No stories found under {stories_dir}/*.md")
        return False

    missing = False
    for s in stories:
        base = os.path.splitext(s)[0]
        prompt = os.path.join(prompts_dir, f"{base}.md")
        failures = os.path.join(sessions_dir, base, "failures.md")
        status = os.path.join(features_dir, base, "status.md")

        if not os.path.exists(prompt):
            print(f"Missing {prompt}")
            missing = True
        if not os.path.exists(failures):
            print(f"Missing {failures}")
            missing = True
        if not os.path.exists(status):
            print(f"Missing {status}")
            missing = True

        if os.path.exists(status):
            with open(status, "r", encoding="utf-8") as f:
                content = f.read()
            
            story_rel = os.path.join("stories", s).replace("\\", "/")
            prompt_rel = os.path.join("prompts", f"{base}.md").replace("\\", "/")

            if story_rel not in content:
                print(f"[WARN] {status} does not reference story path: {story_rel}")
            
            if prompt_rel not in content:
                print(f"[WARN] {status} does not reference prompt path: {prompt_rel}")

    if missing:
        print("[FAIL] Evidence chain incomplete")
        return False

    print("[OK] DocOps evidence chain looks good")
    return True

if __name__ == "__main__":
    if not validate_docops():
        sys.exit(1)



