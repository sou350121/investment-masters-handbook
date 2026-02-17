import os
import sys

# Add src to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from docops.validator import validate_docops

if __name__ == "__main__":
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if not validate_docops(root_dir):
        sys.exit(1)



