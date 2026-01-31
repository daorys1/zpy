import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from zpy.interpreter import run_zpy_file


class TestZpyImports(unittest.TestCase):
    def test_imports_submodule_from_package(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package_dir = os.path.join(temp_dir, "示例包")
            os.makedirs(package_dir, exist_ok=True)

            init_path = os.path.join(package_dir, "__init__.zpy")
            with open(init_path, "w", encoding="utf-8") as handle:
                handle.write("消息 = '来自测试包'\n")

            tool_path = os.path.join(package_dir, "工具.zpy")
            with open(tool_path, "w", encoding="utf-8") as handle:
                handle.write("定义 加法(左, 右):\n    返回 左 + 右\n")

            script_path = os.path.join(temp_dir, "use_package.zpy")
            fixture_path = os.path.join(
                os.path.dirname(__file__),
                "zpy_cases",
                "imports",
                "use_package.zpy",
            )
            with open(fixture_path, "r", encoding="utf-8") as handle:
                script_contents = handle.read()
            with open(script_path, "w", encoding="utf-8") as handle:
                handle.write(script_contents)

            buffer = io.StringIO()
            original_path = list(sys.path)
            sys.path.insert(0, temp_dir)
            try:
                with redirect_stdout(buffer):
                    run_zpy_file(script_path)
            finally:
                sys.path[:] = original_path

            self.assertEqual(buffer.getvalue().strip(), "5")


if __name__ == "__main__":
    unittest.main()
