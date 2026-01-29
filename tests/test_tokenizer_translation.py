import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from zpy.tokenizer import KEYWORDS_CONFIG_PATH, load_keywords, translate_zpy_to_py


class TestTokenizerTranslation(unittest.TestCase):
    def test_translates_keywords_and_builtins(self):
        keyword_map, builtins_map = load_keywords(KEYWORDS_CONFIG_PATH)
        self.assertIsNotNone(keyword_map)
        self.assertIsNotNone(builtins_map)

        zpy_code = "如果 真:\n    打印(整数('3'))\n"
        python_code = translate_zpy_to_py(zpy_code, keyword_map, builtins_map)
        self.assertIsNotNone(python_code)
        self.assertIn("if True", python_code)
        self.assertIn("print", python_code)
        self.assertIn("int", python_code)


if __name__ == "__main__":
    unittest.main()
