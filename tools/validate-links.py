#!/usr/bin/env python3
"""문서의 상대 링크가 실재하는 파일을 가리키는지 검사한다.

e000 §11 체크리스트의 "상대 링크가 깨지지 않았는가"를 자동화한 것이다.
외부 링크(http/https)와 앵커 전용 링크(`#...`)는 검사하지 않는다.

사용법:
    python3 tools/validate-links.py
"""

# tools/validate-all.py 가 읽는 CI 선언.
CI_LABEL = "상대 링크 검사"

import glob
import os
import re
import sys

RE_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
RE_CODE_FENCE = re.compile(r"```.*?```", re.S)

TARGETS = ["*.md", "entities/*.md", "tools/*.py", ".github/workflows/*.yml"]


def strip_code(text):
    """코드 블록 안의 대괄호 표기는 링크가 아니다."""
    return RE_CODE_FENCE.sub("", text)


def main():
    docs = sorted({p for pattern in TARGETS for p in glob.glob(pattern)
                   if p.endswith(".md")})
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
