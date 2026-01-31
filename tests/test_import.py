import os
import sys
import unittest
from contextlib import redirect_stdout
import io
from importlib import resources

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, ROOT_DIR)

from zpy.interpreter import run_zpy_file


class TestImportKeyword(unittest.TestCase):
    def test_import_example(self):
        resource = resources.files("examples").joinpath("导入.zpy")
        buffer = io.StringIO()
        with resources.as_file(resource) as path:
            with redirect_stdout(buffer):
                run_zpy_file(path)
        self.assertEqual(buffer.getvalue().strip(), "圆周率: 3.14")


if __name__ == "__main__":
    unittest.main()
