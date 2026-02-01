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


EXPECT_PREFIX = "# EXPECT:"
CASE_FILES = [
    "类定义示例.zpy",
    "控制流示例.zpy",
    "异常处理示例.zpy",
    "循环控制示例.zpy",
]


def load_expected_output(resource):
    for line in resource.read_text(encoding="utf-8").splitlines():
        if line.strip():
            if line.startswith(EXPECT_PREFIX):
                expected = line[len(EXPECT_PREFIX):].strip()
                return expected.replace("\\n", "\n")
            raise ValueError(f"Missing expectation header in {resource}")
    raise ValueError(f"Missing expectation header in {resource}")


class TestZpyCases(unittest.TestCase):
    _cases_loaded = False

    def __init__(self, methodName="runTest"):
        self._ensure_dynamic_tests()
        super().__init__(methodName)

    @classmethod
    def _ensure_dynamic_tests(cls):
        if cls._cases_loaded:
            return

        if not CASE_FILES:
            def test_no_cases(self):
                self.fail("No .zpy cases configured")

            setattr(cls, "test_no_cases", test_no_cases)
            cls._cases_loaded = True
            return

        for filename in CASE_FILES:
            resource = resources.files("examples").joinpath(filename)
            test_name = f"test_{os.path.splitext(filename)[0]}"

            def _make_test(case_resource, case_name):
                def _test(self):
                    expected = load_expected_output(case_resource)
                    output = self.run_case(case_resource)
                    self.assertEqual(output, expected, msg=f"Case failed: {case_name}")

                return _test

            if hasattr(cls, test_name):
                continue

            setattr(cls, test_name, _make_test(resource, filename))

        cls._cases_loaded = True

    def run_case(self, resource):
        buffer = io.StringIO()
        with resources.as_file(resource) as path:
            with redirect_stdout(buffer):
                run_zpy_file(path)
        return buffer.getvalue().strip()


def load_tests(loader, tests, pattern):
    TestZpyCases._ensure_dynamic_tests()
    return loader.loadTestsFromTestCase(TestZpyCases)


if __name__ == "__main__":
    unittest.main()
