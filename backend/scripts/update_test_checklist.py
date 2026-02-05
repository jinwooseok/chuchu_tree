#!/usr/bin/env python3
"""
pytest JSON 결과를 파싱하여 TEST_CHECKLIST.md를 자동 생성/업데이트하는 스크립트

특징:
- 테스트 파일의 docstring을 자동으로 추출하여 체크리스트 항목 생성
- 디렉토리 구조에서 도메인 자동 감지 (tests/integration/<domain>/, tests/unit/<domain>/)
- 새 테스트 추가 시 자동으로 체크리스트에 반영
- 테스트 결과를 타임스탬프와 함께 누적 저장

사용법:
    1. pytest 실행: pytest --json-report --json-report-file=test_report.json
    2. 스크립트 실행: python scripts/update_test_checklist.py

또는 한 번에:
    pytest --json-report --json-report-file=test_report.json && python scripts/update_test_checklist.py
"""

import ast
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict


# 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent
REPORT_PATH = PROJECT_ROOT / "test_report.json"
CHECKLIST_PATH = PROJECT_ROOT / "docs" / "TEST_CHECKLIST.md"
TESTS_PATH = PROJECT_ROOT / "tests"
CHECKLIST_ARCHIVE_DIR = PROJECT_ROOT / "tests" / "reports"


@dataclass
class TestInfo:
    """테스트 정보"""
    name: str
    docstring: str
    domain: str
    test_type: str  # "unit" or "integration"
    class_name: str | None = None
    class_docstring: str | None = None
    passed: bool = False
    outcome: str = "not_run"
    error_message: str | None = None  # 오류 메시지
    error_traceback: str | None = None  # 스택 트레이스


@dataclass
class DomainStats:
    """도메인별 통계"""
    unit_passed: int = 0
    unit_total: int = 0
    integration_passed: int = 0
    integration_total: int = 0

    @property
    def total(self) -> int:
        return self.unit_total + self.integration_total

    @property
    def passed(self) -> int:
        return self.unit_passed + self.integration_passed

    @property
    def percentage(self) -> int:
        return int((self.passed / self.total * 100) if self.total > 0 else 0)


def parse_test_file(file_path: Path) -> list[TestInfo]:
    """
    테스트 파일을 파싱하여 테스트 정보 추출

    Args:
        file_path: 테스트 파일 경로

    Returns:
        테스트 정보 리스트
    """
    tests = []

    # 도메인과 테스트 타입 추출 (경로에서)
    relative_path = file_path.relative_to(TESTS_PATH)
    parts = relative_path.parts

    # tests/integration/auth/test_auth_me.py -> integration, auth
    # tests/unit/auth/test_token.py -> unit, auth
    if len(parts) >= 2:
        test_type = parts[0] if parts[0] in ("unit", "integration") else "integration"
        domain = parts[1] if len(parts) >= 2 else "unknown"
    else:
        test_type = "integration"
        domain = "unknown"

    # 도메인명 정리 (첫 글자 대문자)
    domain = domain.replace("_", " ").title().replace(" ", "")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except SyntaxError:
        print(f"⚠️  파싱 실패: {file_path}")
        return tests

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # 테스트 클래스
            class_name = node.name
            class_docstring = ast.get_docstring(node)

            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name.startswith("test_"):
                        docstring = ast.get_docstring(item) or item.name
                        tests.append(TestInfo(
                            name=item.name,
                            docstring=docstring,
                            domain=domain,
                            test_type=test_type,
                            class_name=class_name,
                            class_docstring=class_docstring
                        ))

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # 클래스 없이 정의된 테스트 함수
            if node.name.startswith("test_"):
                # 클래스 내부가 아닌 경우만
                parent_is_class = False
                for parent in ast.walk(tree):
                    if isinstance(parent, ast.ClassDef):
                        for child in parent.body:
                            if child is node:
                                parent_is_class = True
                                break

                if not parent_is_class:
                    docstring = ast.get_docstring(node) or node.name
                    tests.append(TestInfo(
                        name=node.name,
                        docstring=docstring,
                        domain=domain,
                        test_type=test_type
                    ))

    return tests


def discover_all_tests() -> dict[str, list[TestInfo]]:
    """
    모든 테스트 파일을 탐색하여 테스트 정보 수집

    Returns:
        {domain: [TestInfo, ...]} 형태의 딕셔너리
    """
    all_tests = defaultdict(list)

    # tests/ 디렉토리 하위의 모든 test_*.py 파일 탐색
    for test_file in TESTS_PATH.rglob("test_*.py"):
        tests = parse_test_file(test_file)
        for test in tests:
            all_tests[test.domain].append(test)

    return dict(all_tests)


def archive_checklist(content: str) -> Path | None:
    """
    체크리스트를 타임스탬프와 함께 보관

    Returns:
        저장된 파일 경로 또는 None
    """
    # 디렉토리 생성
    CHECKLIST_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # 타임스탬프 파일명
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archived_path = CHECKLIST_ARCHIVE_DIR / f"TEST_CHECKLIST_{timestamp}.md"

    # 저장
    with open(archived_path, "w", encoding="utf-8") as f:
        f.write(content)

    return archived_path


def list_archived_checklists() -> list[Path]:
    """보관된 체크리스트 목록 반환"""
    if not CHECKLIST_ARCHIVE_DIR.exists():
        return []
    return sorted(CHECKLIST_ARCHIVE_DIR.glob("TEST_CHECKLIST_*.md"), reverse=True)


def load_test_results() -> dict[str, dict]:
    """
    pytest JSON 리포트에서 테스트 결과 로드

    Returns:
        {test_name: {"passed": bool, "outcome": str, "error_message": str|None, "error_traceback": str|None}}
    """
    if not REPORT_PATH.exists():
        print(f"⚠️  테스트 리포트 없음: {REPORT_PATH}")
        print("   모든 테스트가 '미실행' 상태로 표시됩니다.")
        return {}

    print(f"   리포트 파일: {REPORT_PATH.name}")

    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        report = json.load(f)

    results = {}
    for test in report.get("tests", []):
        nodeid = test.get("nodeid", "")
        outcome = test.get("outcome", "unknown")

        # 테스트 함수명 추출
        if "::" in nodeid:
            test_name = nodeid.split("::")[-1]
        else:
            test_name = nodeid

        # 오류 정보 추출
        error_message = None
        error_traceback = None

        if outcome in ("failed", "error"):
            # call 단계의 오류 정보 확인
            call_info = test.get("call", {})
            if call_info:
                # longrepr: 전체 트레이스백
                longrepr = call_info.get("longrepr", "")
                if longrepr:
                    error_traceback = longrepr

                # crash: 오류 발생 위치 및 메시지
                crash = call_info.get("crash", {})
                if crash:
                    error_message = crash.get("message", "")

            # setup 단계 오류 확인
            setup_info = test.get("setup", {})
            if setup_info and setup_info.get("outcome") in ("failed", "error"):
                longrepr = setup_info.get("longrepr", "")
                if longrepr:
                    error_traceback = longrepr
                crash = setup_info.get("crash", {})
                if crash:
                    error_message = crash.get("message", "")

        results[test_name] = {
            "passed": outcome == "passed",
            "outcome": outcome,
            "error_message": error_message,
            "error_traceback": error_traceback
        }

    return results


def merge_results(all_tests: dict[str, list[TestInfo]], results: dict[str, dict]) -> dict[str, list[TestInfo]]:
    """테스트 정보와 실행 결과 병합"""
    for domain, tests in all_tests.items():
        for test in tests:
            if test.name in results:
                result = results[test.name]
                test.passed = result["passed"]
                test.outcome = result["outcome"]
                test.error_message = result.get("error_message")
                test.error_traceback = result.get("error_traceback")

    return all_tests


def calculate_stats(all_tests: dict[str, list[TestInfo]]) -> dict[str, DomainStats]:
    """도메인별 통계 계산"""
    stats = {}

    for domain, tests in all_tests.items():
        domain_stats = DomainStats()

        for test in tests:
            if test.test_type == "unit":
                domain_stats.unit_total += 1
                if test.passed:
                    domain_stats.unit_passed += 1
            else:  # integration
                domain_stats.integration_total += 1
                if test.passed:
                    domain_stats.integration_passed += 1

        stats[domain] = domain_stats

    return stats


def generate_checklist(all_tests: dict[str, list[TestInfo]], stats: dict[str, DomainStats]) -> str:
    """체크리스트 마크다운 생성"""
    today = datetime.now().strftime("%Y-%m-%d")

    lines = [
        "# ChuChu Tree 테스트 체크리스트",
        "",
        "| 버전 | 수정일 | 수정 사항 |",
        "| --- | --- | --- |",
        f"| 자동생성 | {today} | pytest 결과 기반 자동 업데이트 |",
        "",
        "---",
        "",
        "## 범례",
        "",
        "- [ ] 미완료 / 실패",
        "- [x] 통과",
        "",
        "---",
        "",
    ]

    # 도메인별 섹션 생성 (알파벳 순)
    sorted_domains = sorted(all_tests.keys())

    for idx, domain in enumerate(sorted_domains, 1):
        tests = all_tests[domain]
        lines.append(f"## {idx}. {domain} 도메인")
        lines.append("")

        # Unit Test 섹션
        unit_tests = [t for t in tests if t.test_type == "unit"]
        if unit_tests:
            lines.append(f"### {idx}.1 Unit Test")
            lines.append("")
            lines.extend(generate_test_items(unit_tests))
            lines.append("")

        # Integration Test 섹션
        integration_tests = [t for t in tests if t.test_type == "integration"]
        if integration_tests:
            section_num = f"{idx}.2" if unit_tests else f"{idx}.1"
            lines.append(f"### {section_num} Integration Test")
            lines.append("")
            lines.extend(generate_test_items(integration_tests))
            lines.append("")

        lines.append("---")
        lines.append("")

    # 요약 테이블
    lines.append("## 테스트 완료 요약")
    lines.append("")
    lines.append("| 도메인 | Unit Test | Integration Test | 완료율 |")
    lines.append("| --- | --- | --- | --- |")

    total_stats = DomainStats()

    for domain in sorted_domains:
        s = stats[domain]
        lines.append(f"| {domain} | {s.unit_passed}/{s.unit_total} | {s.integration_passed}/{s.integration_total} | {s.percentage}% |")
        total_stats.unit_passed += s.unit_passed
        total_stats.unit_total += s.unit_total
        total_stats.integration_passed += s.integration_passed
        total_stats.integration_total += s.integration_total

    lines.append(f"| **총계** | **{total_stats.unit_passed}/{total_stats.unit_total}** | **{total_stats.integration_passed}/{total_stats.integration_total}** | **{total_stats.percentage}%** |")
    lines.append("")

    return "\n".join(lines)


def format_error_block(test: TestInfo) -> list[str]:
    """실패한 테스트의 오류 정보를 마크다운으로 포맷"""
    lines = []

    if test.error_message:
        lines.append(f"  > **Error:** {test.error_message}")

    if test.error_traceback:
        # 트레이스백을 간결하게 정리 (너무 길면 마지막 부분만)
        traceback_lines = test.error_traceback.strip().split("\n")

        # 최대 15줄로 제한
        if len(traceback_lines) > 15:
            traceback_lines = ["  ..."] + traceback_lines[-14:]

        lines.append("  ```")
        for line in traceback_lines:
            lines.append(f"  {line}")
        lines.append("  ```")

    return lines


def generate_test_items(tests: list[TestInfo]) -> list[str]:
    """테스트 항목들을 마크다운 체크리스트로 변환"""
    lines = []

    # 클래스별로 그룹화
    by_class = defaultdict(list)
    no_class = []

    for test in tests:
        if test.class_name:
            by_class[test.class_name].append(test)
        else:
            no_class.append(test)

    # 클래스별 출력
    for class_name, class_tests in by_class.items():
        # 클래스 docstring이 있으면 헤더로 사용
        class_docstring = class_tests[0].class_docstring if class_tests else None
        if class_docstring:
            lines.append(f"#### {class_docstring}")
        else:
            lines.append(f"#### {class_name}")

        for test in class_tests:
            checkbox = "[x]" if test.passed else "[ ]"
            lines.append(f"- {checkbox} {test.docstring}")

            # 실패한 경우 오류 정보 추가
            if not test.passed and (test.error_message or test.error_traceback):
                lines.extend(format_error_block(test))

        lines.append("")

    # 클래스 없는 테스트
    for test in no_class:
        checkbox = "[x]" if test.passed else "[ ]"
        lines.append(f"- {checkbox} {test.docstring}")

        # 실패한 경우 오류 정보 추가
        if not test.passed and (test.error_message or test.error_traceback):
            lines.extend(format_error_block(test))

    return lines


def main():
    print("=" * 60)
    print("테스트 체크리스트 자동 생성")
    print("=" * 60)
    print()

    # 1. 모든 테스트 파일 탐색
    print("📂 테스트 파일 탐색 중...")
    all_tests = discover_all_tests()

    total_tests = sum(len(tests) for tests in all_tests.values())
    print(f"   {len(all_tests)}개 도메인, {total_tests}개 테스트 발견")

    for domain, tests in sorted(all_tests.items()):
        unit_count = len([t for t in tests if t.test_type == "unit"])
        int_count = len([t for t in tests if t.test_type == "integration"])
        print(f"   - {domain}: Unit {unit_count}, Integration {int_count}")

    print()

    # 2. 테스트 결과 로드
    print("🔍 테스트 결과 로드 중...")
    results = load_test_results()
    print(f"   {len(results)}개 테스트 결과 로드")
    print()

    # 3. 결과 병합
    all_tests = merge_results(all_tests, results)

    # 4. 통계 계산
    stats = calculate_stats(all_tests)

    # 5. 체크리스트 생성
    print("📝 체크리스트 생성 중...")
    content = generate_checklist(all_tests, stats)

    # 6. 파일 저장 (docs/TEST_CHECKLIST.md)
    CHECKLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CHECKLIST_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    # 7. 체크리스트 보관 (tests/reports/)
    print("💾 체크리스트 보관 중...")
    archived = archive_checklist(content)
    if archived:
        print(f"   저장됨: {archived.name}")

    print()
    print("=" * 60)
    print(f"✅ 완료! {CHECKLIST_PATH}")
    print("=" * 60)

    # 8. 요약 출력
    passed = sum(1 for tests in all_tests.values() for t in tests if t.passed)
    print(f"\n📊 요약: {passed}/{total_tests} 통과")

    for domain in sorted(stats.keys()):
        s = stats[domain]
        print(f"   - {domain}: {s.passed}/{s.total} ({s.percentage}%)")

    # 9. 보관된 체크리스트 히스토리 출력
    archived_checklists = list_archived_checklists()
    if archived_checklists:
        print(f"\n📁 보관된 체크리스트 ({len(archived_checklists)}개):")
        for checklist in archived_checklists[:5]:  # 최근 5개만 표시
            # 파일명에서 날짜 추출
            name = checklist.stem  # TEST_CHECKLIST_20260204_123456
            timestamp = name.replace("TEST_CHECKLIST_", "")
            if len(timestamp) >= 15:
                formatted = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]} {timestamp[9:11]}:{timestamp[11:13]}:{timestamp[13:15]}"
            else:
                formatted = timestamp
            print(f"   - {formatted}")
        if len(archived_checklists) > 5:
            print(f"   ... 외 {len(archived_checklists) - 5}개")


if __name__ == "__main__":
    main()
