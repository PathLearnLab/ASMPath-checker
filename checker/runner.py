import math
import os
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from checker import config
from checker import memory_types
from checker.models import ExerciseTestCase, TestCaseResult


def remove_files(files: List[str]) -> None:
    for file_path in files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass


def compile_and_link(asm_path: str, obj_path: str, exec_path: str) -> bool:
    compile_args = ["nasm", "-g", "-f", "elf64", asm_path, "-o", obj_path]
    link_args = ["ld", obj_path, "-o", exec_path]

    try:
        subprocess.run(compile_args, check=True, capture_output=True)
        subprocess.run(link_args, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def _parse_memory_key(key: str) -> Tuple[str, str]:
    if ":" in key:
        var_address, type_name = key.split(":", 1)
    else:
        var_address, type_name = key, "uchar"

    if type_name not in memory_types.MEMORY_TYPES:
        raise ValueError(f"Unsupported memory type '{type_name}' in key '{key}'")

    return var_address, type_name


def _append_gdb_initial_state_commands(
    gdb_commands: List[str],
    initial_state: Dict[str, Any]
) -> None:
    for key, value in initial_state.items():
        if key.startswith("$"):
            gdb_commands.append(f"set {key} = {value}")
        elif key.startswith("&"):
            var_address, type_name = _parse_memory_key(key)
            c_type, _, _, _ = memory_types.MEMORY_TYPES[type_name]
            gdb_commands.append(f"set {{{c_type}}}{var_address} = {value}")


def _append_gdb_expected_state_commands(
    gdb_commands: List[str],
    expected_state: Dict[str, Any]
) -> None:
    for key in expected_state.keys():
        label = f"RESULT_{key}:"
        if key.startswith("$"):
            gdb_commands.append(f'printf "{label} %ld\\n", (long){key}')
        elif key.startswith("&"):
            var_address, type_name = _parse_memory_key(key)
            c_type, fmt, cast, _ = memory_types.MEMORY_TYPES[type_name]
            gdb_commands.append(f'printf "{label} {fmt}\\n", {cast}{{{c_type}}}{var_address}')


def _prepare_gdb_commands(
    stdin_path: str,
    stdout_path: str,
    initial_state: Dict[str, Any],
    expected_state: Dict[str, Any]
) -> List[str]:
    gdb_commands = [
        "set confirm off",
        "set pagination off",
        "break _start",
        f"run < {stdin_path} > {stdout_path}"
    ]

    _append_gdb_initial_state_commands(gdb_commands, initial_state)

    gdb_commands.append("catch syscall exit")
    gdb_commands.append("continue")

    _append_gdb_expected_state_commands(gdb_commands, expected_state)

    gdb_commands.append("quit")
    return gdb_commands


def _execute_gdb(
    gdb_logic_path: str,
    exec_file: str,
    stdout_path: str,
    expected_state: Dict[str, Any],
    timeout: int
) -> Tuple[List[str], Dict[str, Any], Optional[str], bool]:
    gdb_args = ["gdb", "-batch", "-q", "-x", gdb_logic_path, exec_file]
    process = subprocess.run(
        gdb_args,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    actual_stdout: List[str] = []
    if os.path.exists(stdout_path):
        with open(stdout_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().replace("\x00", "")
            actual_stdout = [line.strip() for line in content.splitlines() if line.strip()]

    full_gdb_output = process.stdout

    actual_state: Dict[str, Any] = {}
    for key in expected_state.keys():
        match = re.search(fr"RESULT_{re.escape(key)}: (\S+)", full_gdb_output)
        if not match:
            continue

        raw_value = match.group(1)
        if key.startswith("&"):
            _, type_name = _parse_memory_key(key)
            py_type = memory_types.MEMORY_TYPES[type_name][3]
        else:
            py_type = int

        try:
            actual_state[key] = py_type(raw_value)
        except ValueError:
            pass

    error_info: Optional[str] = None
    if "Program received signal" in full_gdb_output:
        error_match = re.search(r"Program received signal (SIG\w+, [\w\s]+)", full_gdb_output)
        error_info = error_match.group(1) if error_match else "Runtime Error"

    return actual_stdout, actual_state, error_info, False


def _values_match(key: str, actual: Any, expected: Any) -> bool:
    if actual is None:
        return False

    if key.startswith("&"):
        _, type_name = _parse_memory_key(key)
        if type_name == "float":
            return math.isclose(float(actual), float(expected), rel_tol=1e-5, abs_tol=1e-6)
        if type_name == "double":
            return math.isclose(float(actual), float(expected), rel_tol=1e-9, abs_tol=1e-12)

    return actual == expected


def run_test_case(exec_file: str, test_case: ExerciseTestCase) -> TestCaseResult:
    input_str = "\n".join(test_case.stdin) + ("\n" if test_case.stdin else "")
    with open(config.STDIN_PATH, "w", encoding="utf-8") as f:
        f.write(input_str)

    gdb_commands = _prepare_gdb_commands(
        config.STDIN_PATH,
        config.STDOUT_PATH,
        test_case.initial_state,
        test_case.expected_state,
    )
    with open(config.GDB_LOGIC_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(gdb_commands))

    try:
        actual_stdout, actual_state, err_info, is_timeout = _execute_gdb(
            config.GDB_LOGIC_PATH,
            exec_file,
            config.STDOUT_PATH,
            test_case.expected_state,
            config.TEST_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        actual_stdout, actual_state, err_info, is_timeout = (
            [],
            {},
            "Time Limit Exceeded",
            True,
        )
    finally:
        remove_files([config.GDB_LOGIC_PATH, config.STDIN_PATH, config.STDOUT_PATH])

    stdout_passed = actual_stdout == test_case.expected_stdout
    state_passed = all(
        _values_match(key, actual_state.get(key), expected_val)
        for key, expected_val in test_case.expected_state.items()
    )
    has_error = err_info is not None or is_timeout
    passed = state_passed and stdout_passed and not has_error

    return TestCaseResult(
        test_id=test_case.id,
        passed=passed,
        timeout_reached=is_timeout,
        error=has_error,
        error_info=err_info,
        actual_state=actual_state,
        expected_state=test_case.expected_state,
        actual_stdout=actual_stdout,
        expected_stdout=test_case.expected_stdout,
    )
