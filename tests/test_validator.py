import os
import shutil
import tempfile
import unittest
from src.docops.validator import validate_docops

class TestValidator(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.test_dir, "stories"))
        os.makedirs(os.path.join(self.test_dir, "prompts"))
        os.makedirs(os.path.join(self.test_dir, "sessions/S-0001-test"))
        os.makedirs(os.path.join(self.test_dir, "docs/features/S-0001-test"))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_validate_success(self):
        # Create valid evidence chain
        with open(os.path.join(self.test_dir, "stories/S-0001-test.md"), "w") as f:
            f.write("test")
        with open(os.path.join(self.test_dir, "prompts/S-0001-test.md"), "w") as f:
            f.write("test")
        with open(os.path.join(self.test_dir, "sessions/S-0001-test/failures.md"), "w") as f:
            f.write("test")
        with open(os.path.join(self.test_dir, "docs/features/S-0001-test/status.md"), "w") as f:
            f.write("stories/S-0001-test.md\nprompts/S-0001-test.md")

        self.assertTrue(validate_docops(self.test_dir))

    def test_validate_missing_prompt(self):
        with open(os.path.join(self.test_dir, "stories/S-0001-test.md"), "w") as f:
            f.write("test")
        # Missing prompt
        with open(os.path.join(self.test_dir, "sessions/S-0001-test/failures.md"), "w") as f:
            f.write("test")
        with open(os.path.join(self.test_dir, "docs/features/S-0001-test/status.md"), "w") as f:
            f.write("test")

        self.assertFalse(validate_docops(self.test_dir))

if __name__ == "__main__":
    unittest.main()



