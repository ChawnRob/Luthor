import ast
import os
import unittest
from pathlib import Path


class LocustfileTests(unittest.TestCase):
    def test_locustfile_is_valid_python(self):
        path = Path(__file__).resolve().parent / "locustfile.py"
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        self.assertIn("LuthorEngineUser", classes)

    def test_locustfile_documents_run_command(self):
        path = Path(__file__).resolve().parent / "locustfile.py"
        self.assertIn("locust -f", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
