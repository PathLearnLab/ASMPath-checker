from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ExerciseTestCase:
    id: str
    description: str = ""
    initial_state: Dict[str, Any] = field(default_factory=dict)
    expected_state: Dict[str, Any] = field(default_factory=dict)
    stdin: List[str] = field(default_factory=list)
    expected_stdout: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExerciseTestCase":
        return cls(
            id=str(data.get("id", "")),
            description=data.get("description") or "",
            initial_state=data.get("initialState") or {},
            expected_state=data.get("expectedState") or {},
            stdin=data.get("stdin") or [],
            expected_stdout=data.get("expectedStdout") or []
        )


@dataclass
class ExerciseTestCasesDocument:
    id: str
    unit_id: Optional[int] = None
    test_cases: List[ExerciseTestCase] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExerciseTestCasesDocument":
        raw_test_cases = data.get("testCases") or []    
        return cls(
            id=str(data.get("id", "")),
            unit_id=data.get("unitId"),
            test_cases=[ExerciseTestCase.from_dict(tc) for tc in raw_test_cases]
        )


@dataclass
class TestCaseResult:
    test_id: str
    passed: bool
    timeout_reached: bool
    error: bool
    error_info: Optional[str] = None
    actual_state: Dict[str, Any] = field(default_factory=dict)
    expected_state: Dict[str, Any] = field(default_factory=dict)
    actual_stdout: List[str] = field(default_factory=list)
    expected_stdout: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "testId": self.test_id,
            "passed": self.passed,
            "timeoutReached": self.timeout_reached,
            "error": self.error,
            "errorInfo": self.error_info,
            "actualState": self.actual_state,
            "expectedState": self.expected_state,
            "actualStdout": self.actual_stdout,
            "expectedStdout": self.expected_stdout
        }


@dataclass
class CheckingReport:
    compilation_error: bool = False
    checker_error: bool = False
    checker_error_info: Optional[str] = None
    total_tests: int = 0
    passed_tests: int = 0
    accepted: bool = False
    results: List[TestCaseResult] = field(default_factory=list)

    @classmethod
    def from_results(cls, results: List[TestCaseResult]) -> "CheckingReport":
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        return cls(
            total_tests=total,
            passed_tests=passed,
            accepted=(total > 0 and total == passed),
            results=results
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "compilationError": self.compilation_error,
            "checkerError": self.checker_error,
            "checkerErrorInfo": self.checker_error_info,
            "totalTests": self.total_tests,
            "passedTests": self.passed_tests,
            "accepted": self.accepted,
            "results": [r.to_dict() for r in self.results]
        }
