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
PROJECT_ROOT = Path(__file__).parent.parent.parent
REPORT_PATH = PROJECT_ROOT / "test_report.json"
COVERAGE_REPORT_PATH = PROJECT_ROOT / "coverage_report.json"
TESTS_PATH = PROJECT_ROOT / "tests"
CHECKLIST_PATH = TESTS_PATH / "docs" / "test_checklist.md"
CHECKLIST_ARCHIVE_DIR = TESTS_PATH / "reports"


@dataclass
class TestInfo:
    """테스트 정보"""
    name: str
    docstring: str
    domain: str
    test_type: str  # "unit" or "integration"
    class_name: str | None = None
    class_docstring: str | None = None
    file_path: str | None = None  # 테스트 파일의 상대 경로
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


@dataclass
class DomainCoverage:
    """도메인별 커버리지"""
    covered_lines: int = 0
    total_lines: int = 0
    covered_branches: int = 0
    total_branches: int = 0

    @property
    def line_rate(self) -> float:
        return (self.covered_lines / self.total_lines * 100) if self.total_lines > 0 else 0

    @property
    def line_rate_str(self) -> str:
        return f"{self.line_rate:.1f}%"


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

    # pytest nodeid 형식의 상대 경로 (슬래시 구분)
    rel_path_str = str(relative_path).replace("\\", "/")
    # "integration/auth/test_auth_me.py" → "tests/integration/auth/test_auth_me.py"
    nodeid_file = f"tests/{rel_path_str}"

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
                            class_docstring=class_docstring,
                            file_path=nodeid_file,
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
                        test_type=test_type,
                        file_path=nodeid_file,
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

        # nodeid에서 매칭 키 생성: "tests/unit/auth/test_x.py::ClassName::test_func"
        # → 함수명만 쓰면 중복되므로, 파일경로 + 클래스명 + 함수명 전체를 키로 사용
        # 매칭 시에는 (file_stem, class_name, func_name) 튜플로도 조회 가능하도록 복수 키 등록
        parts = nodeid.split("::")
        func_name = parts[-1] if parts else nodeid
        class_name = parts[-2] if len(parts) >= 3 else None

        # 오류 정보 추출
        error_message = None
        error_traceback = None

        if outcome in ("failed", "error"):
            # call 단계의 오류 정보 확인
            call_info = test.get("call", {})
            if call_info:
                longrepr = call_info.get("longrepr", "")
                if longrepr:
                    error_traceback = longrepr
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

        result_data = {
            "passed": outcome == "passed",
            "outcome": outcome,
            "error_message": error_message,
            "error_traceback": error_traceback
        }

        # 전체 nodeid를 기본 키로 등록
        results[nodeid] = result_data

        # class::func 복합 키로도 등록 (매칭용)
        if class_name:
            results[f"{class_name}::{func_name}"] = result_data
        else:
            # 클래스 없는 테스트는 함수명으로만 등록
            results[func_name] = result_data

    # 컬렉션 에러 처리 (import 실패, 문법 오류 등 - tests 배열에 포함되지 않음)
    for collector in report.get("collectors", []):
        if collector.get("outcome") == "failed":
            nodeid = collector.get("nodeid", "")
            longrepr = collector.get("longrepr", "")

            # 컬렉션 에러는 해당 파일의 모든 테스트에 영향
            result_data = {
                "passed": False,
                "outcome": "error",
                "error_message": f"Collection error: {nodeid}",
                "error_traceback": longrepr if longrepr else None,
            }
            # 파일 경로를 키로 등록 (나중에 파일 단위로 매칭)
            results[f"__collection_error__{nodeid}"] = result_data

    return results


def merge_results(all_tests: dict[str, list[TestInfo]], results: dict[str, dict]) -> dict[str, list[TestInfo]]:
    """테스트 정보와 실행 결과 병합"""

    # 컬렉션 에러를 파일 경로별로 정리
    collection_errors = {}
    for key, result in results.items():
        if key.startswith("__collection_error__"):
            # nodeid 예: "tests/unit/chat/entity/test_chat_session.py"
            file_path = key.replace("__collection_error__", "")
            collection_errors[file_path] = result

    for domain, tests in all_tests.items():
        for test in tests:
            matched = False

            # 1순위: class::func 복합 키로 매칭
            if test.class_name:
                composite_key = f"{test.class_name}::{test.name}"
                if composite_key in results:
                    result = results[composite_key]
                    test.passed = result["passed"]
                    test.outcome = result["outcome"]
                    test.error_message = result.get("error_message")
                    test.error_traceback = result.get("error_traceback")
                    matched = True

            # 2순위: 함수명으로 매칭 (클래스 없는 테스트)
            if not matched and not test.class_name and test.name in results:
                result = results[test.name]
                test.passed = result["passed"]
                test.outcome = result["outcome"]
                test.error_message = result.get("error_message")
                test.error_traceback = result.get("error_traceback")
                matched = True

            # 3순위: 전체 nodeid에서 매칭 시도
            if not matched:
                for key, result in results.items():
                    if key.startswith("__collection_error__"):
                        continue
                    if key.endswith(f"::{test.name}"):
                        # class_name도 일치하는지 확인
                        if test.class_name and f"::{test.class_name}::{test.name}" in key:
                            test.passed = result["passed"]
                            test.outcome = result["outcome"]
                            test.error_message = result.get("error_message")
                            test.error_traceback = result.get("error_traceback")
                            matched = True
                            break
                        elif not test.class_name:
                            test.passed = result["passed"]
                            test.outcome = result["outcome"]
                            test.error_message = result.get("error_message")
                            test.error_traceback = result.get("error_traceback")
                            matched = True
                            break

            # 4순위: 컬렉션 에러 - 해당 파일의 모든 테스트에 에러 적용
            if not matched and collection_errors and test.file_path:
                for col_path, error_result in collection_errors.items():
                    # 정확한 파일 경로 매칭
                    if test.file_path in col_path or col_path in test.file_path:
                        test.passed = False
                        test.outcome = "error"
                        test.error_message = error_result.get("error_message")
                        test.error_traceback = error_result.get("error_traceback")
                        matched = True
                        break

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


def generate_checklist(
    all_tests: dict[str, list[TestInfo]],
    stats: dict[str, DomainStats],
    coverage: dict[str, "DomainCoverage"] | None = None,
) -> str:
    """체크리스트 마크다운 생성"""
    today = datetime.now().strftime("%Y-%m-%d")
    has_coverage = bool(coverage)

    lines = [
        "# Build Genie 테스트 체크리스트",
        "",
        "| 버전 | 수정일 | 수정 사항 |",
        "| --- | --- | --- |",
        f"| 자동생성 | {today} | 초기 생성 테스트 |",
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

        # 도메인별 커버리지 표시
        if has_coverage and domain in coverage:
            dc = coverage[domain]
            lines.append(f"> 코드 커버리지: **{dc.line_rate_str}** ({dc.covered_lines}/{dc.total_lines} lines)")
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

    if has_coverage:
        lines.append("| 도메인 | Unit Test | Integration Test | 완료율 | 커버리지 |")
        lines.append("| --- | --- | --- | --- | --- |")
    else:
        lines.append("| 도메인 | Unit Test | Integration Test | 완료율 |")
        lines.append("| --- | --- | --- | --- |")

    total_stats = DomainStats()
    total_coverage = DomainCoverage()

    for domain in sorted_domains:
        s = stats[domain]
        row = f"| {domain} | {s.unit_passed}/{s.unit_total} | {s.integration_passed}/{s.integration_total} | {s.percentage}%"

        if has_coverage:
            dc = coverage.get(domain)
            if dc:
                row += f" | {dc.line_rate_str}"
                total_coverage.covered_lines += dc.covered_lines
                total_coverage.total_lines += dc.total_lines
            else:
                row += " | -"

        row += " |"
        lines.append(row)

        total_stats.unit_passed += s.unit_passed
        total_stats.unit_total += s.unit_total
        total_stats.integration_passed += s.integration_passed
        total_stats.integration_total += s.integration_total

    total_row = f"| **총계** | **{total_stats.unit_passed}/{total_stats.unit_total}** | **{total_stats.integration_passed}/{total_stats.integration_total}** | **{total_stats.percentage}%**"
    if has_coverage:
        total_row += f" | **{total_coverage.line_rate_str}**"
    total_row += " |"
    lines.append(total_row)
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


def load_coverage_data() -> dict[str, DomainCoverage]:
    """
    pytest-cov JSON 리포트에서 도메인별 커버리지 로드

    Returns:
        {domain_name: DomainCoverage} (도메인명은 PascalCase)
    """
    if not COVERAGE_REPORT_PATH.exists():
        print(f"⚠️  커버리지 리포트 없음: {COVERAGE_REPORT_PATH}")
        return {}

    with open(COVERAGE_REPORT_PATH, "r", encoding="utf-8") as f:
        cov_data = json.load(f)

    domain_coverage: dict[str, DomainCoverage] = {}

    # 도메인 매핑: app/common → Common, app/chat → Chat 등
    # "common" 도메인의 테스트는 "Common" 키로 저장됨
    domain_aliases = {
        "common": "Common",
        "chat": "Chat",
        "project": "Project",
        "document": "Document",
        "document_template": "DocumentTemplate",
        "checklist": "Checklist",
        "user_account": "UserAccount",
    }

    files = cov_data.get("files", {})
    for file_path, file_data in files.items():
        # file_path 예: "app/chat/application/service/chat_application_service.py"
        # 또는 Windows: "app\\chat\\..." — 정규화
        normalized = file_path.replace("\\", "/")

        parts = normalized.split("/")
        if len(parts) < 2 or parts[0] != "app":
            continue

        # app/<domain>/... → domain 추출
        raw_domain = parts[1]
        domain_name = domain_aliases.get(raw_domain, raw_domain.replace("_", " ").title().replace(" ", ""))

        if domain_name not in domain_coverage:
            domain_coverage[domain_name] = DomainCoverage()

        summary = file_data.get("summary", {})
        dc = domain_coverage[domain_name]
        dc.covered_lines += summary.get("covered_lines", 0)
        dc.total_lines += summary.get("num_statements", 0)
        dc.covered_branches += summary.get("covered_branches", 0)
        dc.total_branches += summary.get("num_branches", 0)

    return domain_coverage


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

    # 4.5 커버리지 로드
    print("📊 커버리지 데이터 로드 중...")
    coverage = load_coverage_data()
    if coverage:
        print(f"   {len(coverage)}개 도메인 커버리지 로드")
        for domain in sorted(coverage.keys()):
            dc = coverage[domain]
            print(f"   - {domain}: {dc.line_rate_str} ({dc.covered_lines}/{dc.total_lines} lines)")
    print()

    # 5. 체크리스트 생성
    print("📝 체크리스트 생성 중...")
    content = generate_checklist(all_tests, stats, coverage)

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
