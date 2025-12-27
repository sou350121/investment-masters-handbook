import os
import sys
import argparse

# Add src to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from docops.manager import create_new_story

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new story with DocOps structure.")
    parser.add_argument("--id", required=True, help="Story ID (e.g., S-0002)")
    parser.add_argument("--title", required=True, help="Story title (e.g., add-login)")
    
    args = parser.parse_args()
    
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    create_new_story(args.id, args.title, root_dir)



