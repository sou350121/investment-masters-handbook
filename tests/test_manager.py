import os
import shutil
import tempfile
import unittest
from src.docops.manager import create_new_story

class TestManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_create_new_story(self):
        story_id = "S-0002"
        title = "test-feature"
        create_new_story(story_id, title, self.test_dir)

        self.assertTrue(os.path.exists(os.path.join(self.test_dir, f"stories/{story_id}-{title}.md")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, f"prompts/{story_id}-{title}.md")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, f"sessions/{story_id}-{title}/failures.md")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, f"docs/features/{story_id}-{title}/status.md")))

if __name__ == "__main__":
    unittest.main()



