#!/usr/bin/env python3
"""문서의 상대 링크가 실재하는 파일을 가리키는지 검사한다.

e000 §11 체크리스트의 "상대 링크가 깨지지 않았는가"를 자동화한 것이다.
외부 링크(http/https)와 앵커 전용 링크(`#...`)는 검사하지 않는다.

사용법:
    python3 tools/validate-links.py
"""

# tools/validate-all.py 가 읽는 CI 선언.
CI_LABEL = "상대 링크 검사"

import os
import re
import sys

RE_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
RE_CODE_FENCE = re.compile(r"```.*?```", re.S)

# 검사 대상을 목록으로 적지 않는다. 하드코딩하면 새로 생긴 디렉터리의 문서가
# 조용히 검사 밖에 남는다 — benchmarks/, architecture/, fixtures/가 그랬다.
SKIP_DIRS = {".git", "__pycache__", "node_modules"}


def discover():
    """저장소의 모든 Markdown을 찾는다."""
    found = []
    for dirpath, dirnames, filenames in os.walk("."):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        found.extend(os.path.normpath(os.path.join(dirpath, f))
                     for f in filenames if f.endswith(".md"))
    return sorted(found)


def strip_code(text):
    """코드 블록 안의 대괄호 표기는 링크가 아니다."""
    return RE_CODE_FENCE.sub("", text)


def main():
    docs = discover()
    broken = 0
    checked = 0

    for path in docs:
        base = os.path.dirname(path)
        for target in RE_LINK.findall(strip_code(open(path).read())):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            resolved = os.path.normpath(os.path.join(base, target.split("#")[0]))
            checked += 1
            if not os.path.exists(resolved):
                broken += 1
                print(f"FAIL {path}: 깨진 링크 `{target}` → {resolved}")

    print(f"\n링크 {checked}개: {checked - broken} 통과, {broken} 실패")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
