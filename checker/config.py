import os


WORK_DIR: str = os.getenv("CHECKER_WORK_DIR", "source")
TEST_TIMEOUT: int = int(os.getenv("CHECKER_TEST_TIMEOUT", "5"))

SOLUTION_ASM_PATH: str = os.path.join(WORK_DIR, "solution.asm")
TEST_CASES_PATH: str = os.path.join(WORK_DIR, "test_cases.json")
RESULTS_PATH: str = os.path.join(WORK_DIR, "results.json")

OBJ_FILE: str = os.getenv("CHECKER_OBJ_FILE", "solution.o")
EXEC_FILE: str = os.getenv("CHECKER_EXEC_FILE", "solution")

GDB_LOGIC_PATH: str = "gdb_logic.txt"
STDIN_PATH: str = "stdin_input.txt"
STDOUT_PATH: str = "prog_output.txt"
