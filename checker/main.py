import json
import os

from checker import config
from checker.models import CheckingReport, ExerciseTestCasesDocument
from checker.runner import compile_and_link, remove_files, run_test_case


def write_result(report: CheckingReport) -> None:
    with open(config.RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, indent=4, ensure_ascii=False)


def main() -> None:
    if not os.path.exists(config.TEST_CASES_PATH):
        write_result(
            CheckingReport(
                checker_error=True,
                checker_error_info=f"File {config.TEST_CASES_PATH} not found",
            )
        )
        return

    if not os.path.exists(config.SOLUTION_ASM_PATH):
        write_result(
            CheckingReport(
                checker_error=True,
                checker_error_info=f"File {config.SOLUTION_ASM_PATH} not found",
            )
        )
        return

    try:
        with open(config.TEST_CASES_PATH, "r", encoding="utf-8") as f:
            document = ExerciseTestCasesDocument.from_dict(json.load(f))
    except Exception as e:
        write_result(
            CheckingReport(
                checker_error=True,
                checker_error_info=f"Failed to parse {config.TEST_CASES_PATH}: {e}",
            )
        )
        return

    if not compile_and_link(config.SOLUTION_ASM_PATH, config.OBJ_FILE, config.EXEC_FILE):
        write_result(CheckingReport(compilation_error=True))
        remove_files([config.OBJ_FILE, config.EXEC_FILE])
        return

    try:
        results = [run_test_case(config.EXEC_FILE, tc) for tc in document.test_cases]
        report = CheckingReport.from_results(results)
        write_result(report)
        print("Testing finished.")
    except ValueError as e:
        write_result(
            CheckingReport(
                checker_error=True,
                checker_error_info=str(e),
            )
        )
    finally:
        remove_files([config.OBJ_FILE, config.EXEC_FILE])


if __name__ == "__main__":
    main()
