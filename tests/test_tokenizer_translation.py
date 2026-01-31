import os
import sys
import unittest
from importlib import resources

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, ROOT_DIR)

from zpy.tokenizer import KEYWORDS_CONFIG_PATH, load_keywords, translate_zpy_to_py


def iter_example_resources():
    root = resources.files("examples")
    stack = [root]
    while stack:
        current = stack.pop()
        for entry in current.iterdir():
            if entry.is_dir():
                stack.append(entry)
            elif entry.name.endswith(".zpy"):
                yield entry


class TestTokenizerTranslation(unittest.TestCase):
    def test_translate_examples_to_valid_python(self):
        keyword_map, builtins_map = load_keywords(KEYWORDS_CONFIG_PATH)
        self.assertIsNotNone(keyword_map)
        self.assertIsNotNone(builtins_map)

        example_files = list(iter_example_resources())
        self.assertTrue(example_files, "No example .zpy files found")

        for resource in example_files:
            with self.subTest(example=resource.name):
                zpy_code = resource.read_text(encoding="utf-8")
                python_code = translate_zpy_to_py(zpy_code, keyword_map, builtins_map)
                self.assertIsNotNone(python_code)
                compile(python_code, str(resource), "exec")


if __name__ == "__main__":
    unittest.main()
