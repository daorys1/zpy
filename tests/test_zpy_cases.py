import os
import sys
import unittest
from contextlib import redirect_stdout
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from zpy.interpreter import run_zpy_file


CASES_DIR = os.path.join(os.path.dirname(__file__), "zpy_cases")
EXPECT_PREFIX = "# EXPECT:"


def load_expected_output(path):
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                if line.startswith(EXPECT_PREFIX):
                    expected = line[len(EXPECT_PREFIX):].strip()
                    return expected.replace("\\n", "\n")
                raise ValueError(f"Missing expectation header in {path}")
    raise ValueError(f"Missing expectation header in {path}")


class TestZpyCases(unittest.TestCase):
    _cases_loaded = False

    def __init__(self, methodName="runTest"):
        self._ensure_dynamic_tests()
        super().__init__(methodName)

    @classmethod
    def _ensure_dynamic_tests(cls):
        if cls._cases_loaded:
            return

        cases = sorted(
            filename for filename in os.listdir(CASES_DIR) if filename.endswith(".zpy")
        )
        if not cases:
            def test_no_cases(self):
                self.fail("No .zpy cases found")

            setattr(cls, "test_no_cases", test_no_cases)
            cls._cases_loaded = True
            return

        for filename in cases:
            path = os.path.join(CASES_DIR, filename)
            test_name = f"test_{os.path.splitext(filename)[0]}"

            def _make_test(case_path, case_name):
                def _test(self):
                    expected = load_expected_output(case_path)
                    output = self.run_case(case_path)
                    self.assertEqual(output, expected, msg=f"Case failed: {case_name}")

                return _test

            if hasattr(cls, test_name):
                continue

            setattr(cls, test_name, _make_test(path, filename))

        cls._cases_loaded = True

    def run_case(self, path):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            run_zpy_file(path)
        return buffer.getvalue().strip()


def load_tests(loader, tests, pattern):
    TestZpyCases._ensure_dynamic_tests()
    return loader.loadTestsFromTestCase(TestZpyCases)


if __name__ == "__main__":
    unittest.main()
