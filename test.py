from argparse import ArgumentParser, Namespace
import glob
import importlib
import os
import re
from uvulog import Styled, Styles

from utils.testutils import test_dict, run_single_test, print_fail_banner, print_pass_banner
from utils.testutils import TestResult


def preload() -> None:
    test_files = glob.glob(os.path.join(os.path.dirname(__file__), "tests", "*.py"))
    for test_file in test_files:
        module_name = os.path.splitext(os.path.basename(test_file))[0]
        if module_name != "__init__":
            try:
                importlib.import_module(f"tests.{module_name}")
            except Exception as e:
                print(Styled(f"[-] Failed to import test module: {module_name}, error: {str(e)}", Styles.RED))


def parse_args() -> tuple[Namespace, dict[str, str]]:
    parser = ArgumentParser("MSEdit Components Test Utils", "uv run test.py -c/--components [c1 ...] -a/--args/--append_args [a1 ...] [--k1 v1 ...]")
    parser.add_argument(
        "--components", "-c", nargs="+",
        help="List of components to test, regex is available, available components: " + str(Styled(
            ", ".join(test_dict.keys()), Styles.CYAN) if len(test_dict) > 0 else Styled(
                "No available components", Styles.YELLOW)))
    parser.add_argument("--append_args", "--args", "-a", nargs="+",
                        help="Additional arguments to pass to the test functions")
    opt, unknown_args = parser.parse_known_args()
    kwargs = {unknown_args[i]: unknown_args[i + 1] for i in range(0, len(unknown_args), 2)}
    return opt, kwargs


def run_test_pipeline(selected_tests: list[str], args: list[str], kwargs: dict[str, str]) -> None:
    def match_test_cases(test_name: str) -> bool:
        for pattern in selected_tests:
            if pattern == test_name or re.fullmatch(pattern, test_name):
                return True
        return False
    tests = {test_name: test_fn for test_name, test_fn in test_dict.items() if match_test_cases(test_name)}
    print(f"imported {Styled(len(tests), Styles.CYAN)}/{Styled(len(test_dict), Styles.CYAN)} valid tests, ready to run")
    summary = {}
    ignored, passed, failed = 0, 0, 0
    for test_name, test_fn in tests.items():
        status, test_result = run_single_test(test_name, test_fn, args, kwargs)
        ignored += test_result == TestResult.IGNORED
        passed += test_result == TestResult.PASSED
        failed += test_result == TestResult.FAILED
        summary[test_name] = status

    max_name_length = max(22, max(len(test_name) for test_name in summary.keys()) if len(summary) else 0)
    print("====== Test Summary ======".center(max_name_length + 32, "="))
    for test_name, status in summary.items():
        print("{} {}".format(Styled(test_name.ljust(max_name_length + 23, "."), Styles.CYAN), status))

    print("\nFinal Pass Result ".ljust(max_name_length + 33, "="))
    if failed <= 0:
        print_pass_banner()
    else:
        print_fail_banner()
    print()


if __name__ == "__main__":
    preload()
    opt, kwargs = parse_args()
    run_test_pipeline(opt.components or list(test_dict.keys()), opt.append_args or [], kwargs or {})
