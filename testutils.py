# -*- coding: utf-8 -*-

from datetime import datetime
from enum import Enum
from uvulog import Styles, Styled


class TestResult(Enum):
    PASSED = 1
    FAILED = 2
    IGNORED = 3


def wrap_test(name, *, need_verify=False, ground_truth=None, logger=None):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            try:
                value_to_check = fn(*args, **kwargs)
            except Exception as e:
                value_to_check = f"[{datetime.now().isoformat()}] C_Exception: {str(e)}"
            try:
                ground_truth_value = ground_truth(*args, **kwargs) if callable(ground_truth) else ground_truth
            except Exception as e:
                ground_truth_value = f"[{datetime.now().isoformat()}] G_Exception: {str(e)}"
            return need_verify, value_to_check, ground_truth_value
        return wrapper
    return decorator


def register_test(name):
    def decorator(fn):
        test_dict[name] = fn
        return fn
    return decorator


def run_single_test(test_name: str, test_fn: callable, args: list[str], kwargs: dict[str, str]) -> tuple[Styled, TestResult]:
    print(">>> Starting test: {test_name} with args: {args} and kwargs: {kwargs}... <<<"
          .format(test_name=Styled(test_name, Styles.CYAN),
                  args=Styled(args, Styles.CYAN), kwargs=Styled(kwargs, Styles.CYAN)))
    out_value: tuple[bool, str, str] = test_fn(*args, **kwargs)
    value_matches = out_value[1] == out_value[2]
    status = Styled("[ignore]", Styles.YELLOW)
    ret_test_result = TestResult.IGNORED
    if value_matches and out_value[0]:
        status = Styled("[passed]", Styles.GREEN)
        ret_test_result = TestResult.PASSED
    elif not value_matches and out_value[0]:
        status = Styled("[failed]", Styles.RED)
        ret_test_result = TestResult.FAILED
    print("    {}".format(
        "{} ({} <=> {})".format(status, Styled(out_value[1], Styles.CYAN), Styled(out_value[2], Styles.CYAN))
        if out_value[0] else
        "{} ({})".format(status, Styled(out_value[1], Styles.CYAN))
    ))
    print(">>> Finished test: {test_name} <<<\n".format(test_name=Styled(test_name, Styles.CYAN)))
    return status, ret_test_result


def print_pass_banner() -> None:
    pattern = [
        "  ########      ###       ######     ######   ",
        "  ##    ##     ## ##     ##    ##   ##    ##  ",
        "  ##    ##    ##   ##    ##         ##        ",
        "  ########   ##     ##    ######     ######   ",
        "  ##         #########         ##         ##  ",
        "  ##         ##     ##   ##    ##   ##    ##  ",
        "  ##         ##     ##    ######     ######   "
    ]
    empty_line = " " * (len(pattern[0]) + 8)
    print(Styled(empty_line, Styles.GREEN_BG, Styles.WHITE))
    for line in pattern:
        full_line = f"    {line}    "
        print(Styled(full_line, Styles.GREEN_BG, Styles.WHITE))
    print(Styled(empty_line, Styles.GREEN_BG, Styles.WHITE))


def print_fail_banner() -> None:
    pattern = [
        "  ########      ###        ####     ##        ",
        "  ##           ## ##        ##      ##        ",
        "  ######      ##   ##       ##      ##        ",
        "  ##         #########      ##      ##        ",
        "  ##         ##     ##      ##      ##        ",
        "  ##         ##     ##     ####     ########  "
    ]
    empty_line = " " * (len(pattern[0]) + 8)
    print(Styled(empty_line, Styles.RED_BG, Styles.WHITE))
    for line in pattern:
        full_line = f"    {line}    "
        print(Styled(full_line, Styles.RED_BG, Styles.WHITE))
    print(Styled(empty_line, Styles.RED_BG, Styles.WHITE))


test_dict: dict[str, callable] = {}
