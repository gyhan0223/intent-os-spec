#!/usr/bin/env python3
"""저장소의 모든 검증 검사를 자동 발견해 실행한다.

CI 워크플로가 검사마다 스텝을 하나씩 갖고 있으면, 여러 작업이 병렬로
진행될 때 전부 `.github/workflows/validate-spec.yml` 같은 자리에 스텝을
덧붙이게 되어 매번 충돌한다. 그리고 그 충돌을 "한쪽 선택"으로 풀면
이미 머지된 검사가 CI에서 조용히 사라진다. 파일은 남고 검사만 없어지니
눈에 띄지도 않는다.

그래서 CI는 이 디스패처 하나만 부르고, 검사 목록은 파일 시스템에서
발견한다. 새 검사를 추가할 때 공유 파일을 고칠 일이 없다 =
충돌할 자리가 없다.

발견 규칙:
    1. `tools/validate-*.py`                    (이 파일 자신은 제외)
    2. `test_*.py`를 가진 `tests/` 디렉터리     → unittest discover

인자가 필요하거나 이름을 붙이고 싶은 검사는 **자기 파일 안에서** 선언한다.
디스패처가 AST로 읽으므로 모듈을 import하지 않는다.

    CI_ARGS  = ["tests/invariants/valid-chain.json"]   # 넘길 인자
    CI_LABEL = "전역 불변식 정상 체인 검증"             # 출력용 이름
    CI_SKIP  = True                                    # CI에서 제외

사용법:
    python3 tools/validate-all.py              # 전부 실행
    python3 tools/validate-all.py --list       # 실행할 검사 목록만 출력
    python3 tools/validate-all.py canonical    # 이름에 부분일치하는 것만
"""

import ast
import glob
import json
import os
import subprocess
import sys
import time
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SELF = os.path.basename(os.path.abspath(__file__))
SCHEMA_GLOB = "intent-os-spec/schemas/*.json"
LABEL_WIDTH = 48


def pad(text, width=LABEL_WIDTH):
    """한글은 터미널에서 2칸을 차지한다. 문자 수로 맞추면 표가 어긋난다."""
    shown = sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text)
    return text + " " * max(1, width - shown)


def read_declarations(path):
    """검사 파일 상단의 CI_* 선언을 AST로 읽는다.

    import하지 않는 이유는 두 가지다. 파일명에 하이픈이 있어 모듈명으로
    쓸 수 없고, 발견만 하려고 남의 모듈 최상위 코드를 실행할 이유가 없다.
    """
    declared = {}
    try:
        tree = ast.parse(open(path, encoding="utf-8").read(), filename=path)
    except SyntaxError as exc:
        return {"_syntax_error": f"{exc.lineno}행: {exc.msg}"}

    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.startswith("CI_"):
                try:
                    declared[target.id] = ast.literal_eval(node.value)
                except ValueError:
                    pass  # 상수가 아닌 선언은 무시한다
    return declared


def discover_validators():
    checks = []
    for path in sorted(glob.glob(os.path.join(ROOT, "tools", "validate-*.py"))):
        name = os.path.basename(path)
        if name == SELF:
            continue

        declared = read_declarations(path)
        if "_syntax_error" in declared:
            checks.append({
                "label": f"{name} (구문 오류)",
                "cmd": None,
                "error": declared["_syntax_error"],
            })
            continue
        if declared.get("CI_SKIP"):
            continue

        args = [str(a) for a in declared.get("CI_ARGS", [])]
        checks.append({
            "label": declared.get("CI_LABEL", name),
            "cmd": [sys.executable, os.path.join("tools", name), *args],
        })
    return checks


def discover_test_suites():
    """`test_*.py`를 담은 `tests/` 디렉터리를 찾는다."""
    suites = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in {".git", "__pycache__", ".github", "node_modules"}]
        if os.path.basename(dirpath) != "tests":
            continue
        if not any(f.startswith("test_") and f.endswith(".py") for f in filenames):
            continue
        rel = os.path.relpath(dirpath, ROOT)
        suites.append({
            "label": f"unittest {rel}",
            "cmd": [sys.executable, "-m", "unittest", "discover",
                    "-s", rel, "-p", "test_*.py"],
        })
    return sorted(suites, key=lambda s: s["label"])


def preflight_schemas():
    """스키마가 JSON으로 파싱되는지 먼저 본다.

    다른 검사도 스키마를 읽지만, 깨졌을 때 traceback 대신
    어느 파일인지 한 줄로 알려주려고 앞에 둔다.
    """
    broken = []
    for path in sorted(glob.glob(os.path.join(ROOT, SCHEMA_GLOB))):
        try:
            json.load(open(path, encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            broken.append(f"{os.path.relpath(path, ROOT)}: {exc}")
    return broken


def run(check):
    if check.get("cmd") is None:
        return False, check.get("error", ""), 0.0
    started = time.monotonic()
    proc = subprocess.run(check["cmd"], cwd=ROOT, capture_output=True, text=True)
    elapsed = time.monotonic() - started
    return proc.returncode == 0, (proc.stdout + proc.stderr), elapsed


def main(argv):
    checks = discover_validators() + discover_test_suites()

    filters = [a for a in argv if not a.startswith("-")]
    if filters:
        checks = [c for c in checks
                  if any(f.lower() in c["label"].lower()
                         or any(f in part for part in (c["cmd"] or []))
                         for f in filters)]

    if "--list" in argv:
        for c in checks:
            shown = " ".join(c["cmd"][1:]) if c["cmd"] else "(실행 불가)"
            print(f"  {pad(c['label'])} {shown}")
        print(f"\n검사 {len(checks)}개")
        return 0

    if not checks:
        print("FAIL 실행할 검사가 없다. 발견 규칙이 깨졌는지 확인한다.")
        return 1

    broken = preflight_schemas()
    if broken:
        print("FAIL JSON Schema 파싱 실패")
        for line in broken:
            print(f"  {line}")
        return 1

    # 첫 실패에서 멈추지 않는다. 한 번 돌려 전부 보는 편이 낫다.
    failures = []
    for check in checks:
        ok, output, elapsed = run(check)
        print(f"{'OK  ' if ok else 'FAIL'} {pad(check['label'])} {elapsed:5.1f}s")
        if not ok:
            failures.append((check["label"], output))

    if failures:
        for label, output in failures:
            print(f"\n{'─' * 68}\nFAIL {label}\n{'─' * 68}")
            print(output.rstrip() or "(출력 없음)")

    print(f"\n검사 {len(checks)}개: {len(checks) - len(failures)} 통과, {len(failures)} 실패")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
