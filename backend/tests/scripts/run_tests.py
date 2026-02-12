#!/usr/bin/env python3
"""
테스트 실행 + 체크리스트 업데이트를 한 번에 수행하는 스크립트

사용법:
    poetry run python tests/scripts/run_tests.py              # 전체 테스트 실행
    poetry run python tests/scripts/run_tests.py auth         # auth 도메인만 테스트
    poetry run python tests/scripts/run_tests.py --checklist  # 체크리스트만 업데이트 (테스트 실행 없이)
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

def run_pytest(target: str | None = None) -> int:
    """pytest 실행"""

    cmd = [sys.executable, "-m", "pytest"]

    if target:
        # 특정 도메인만 테스트
        test_path = PROJECT_ROOT / "tests"

        # integration과 unit 모두 탐색
        paths = []
        for test_type in ["integration", "unit"]:
            domain_path = test_path / test_type / target
            if domain_path.exists():
                paths.append(str(domain_path))

        if paths:
            cmd.extend(paths)
        else:
            print(f"⚠️  '{target}' 도메인의 테스트를 찾을 수 없습니다.")
            return 1

    print("=" * 60)
    print("🧪 테스트 실행")
    print("=" * 60)
    print(f"명령어: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return result.returncode


def run_checklist_update() -> int:
    """체크리스트 업데이트 스크립트 실행"""
    script_path = PROJECT_ROOT / "tests" / "scripts" / "update_test_checklist.py"
    cmd = [sys.executable, str(script_path)]

    print()
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return result.returncode


def main():
    args = sys.argv[1:]

    # --checklist 옵션: 테스트 실행 없이 체크리스트만 업데이트
    if "--checklist" in args:
        sys.exit(run_checklist_update())

    # --help 옵션
    if "--help" in args or "-h" in args:
        print(__doc__)
        sys.exit(0)

    # 테스트 대상 (도메인명)
    target = args[0] if args else None

    # 1. pytest 실행
    pytest_result = run_pytest(target)

    # 2. 체크리스트 업데이트 (테스트 결과와 관계없이 실행)
    checklist_result = run_checklist_update()

    # 결과 반환 (pytest 실패 시 실패 코드 반환)
    sys.exit(pytest_result)


if __name__ == "__main__":
    main()
