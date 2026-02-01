import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from importlib import resources

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, ROOT_DIR)

from zpy.interpreter import run_zpy_file


class TestArgvExample(unittest.TestCase):
    def test_example_reads_sys_argv(self):
        resource = resources.files("examples").joinpath("参数示例.zpy")
        buffer = io.StringIO()
        extra_args = ["first", "second"]
        with resources.as_file(resource) as path:
            with redirect_stdout(buffer):
                run_zpy_file(str(path), extra_args)

        output_lines = buffer.getvalue().strip().splitlines()
        expected_path = os.path.abspath(str(path))
        expected_lines = [
            f"参数列表: { [expected_path] + extra_args }",
            "参数数量: 2",
        ]
        self.assertEqual(output_lines, expected_lines)


if __name__ == "__main__":
    unittest.main()
