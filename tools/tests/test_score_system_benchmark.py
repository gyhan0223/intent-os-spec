#!/usr/bin/env python3
"""벤치마크 채점기가 실제로 돌아가는지 검사한다.

`.github/workflows/validate-spec.yml`에 있던 smoke test를 옮겨온 것이다.
CI 워크플로에 검사를 직접 적으면 병렬 작업이 그 파일에서 충돌하므로,
`tools/validate-all.py`가 자동 발견하는 자리로 내렸다.

`tools/validate-system-benchmark.py`는 스위트·스키마·예시가 규격에 맞는지를 본다.
이 테스트는 그 예시로 채점기를 **실행**해 결과가 나오는지를 본다. 둘은 다른 검사다.

주의: `system-routing-run.example.json`은 합성 예시이며 벤치마크 근거가 아니다.
여기서 확인하는 것은 채점기가 동작한다는 사실뿐이고, 라우팅 우위가 아니다.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCORER = ROOT / "tools" / "score-system-benchmark.py"
EXAMPLE = ROOT / "benchmarks" / "examples" / "system-routing-run.example.json"


class ScoreSystemBenchmarkSmokeTest(unittest.TestCase):
    def test_scorer_compiles(self):
        proc = subprocess.run(
            [sys.executable, "-m", "py_compile", str(SCORER)],
            capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_scorer_runs_on_synthetic_example(self):
        self.assertTrue(EXAMPLE.exists(), f"합성 예시가 없다: {EXAMPLE}")
        proc = subprocess.run(
            [sys.executable, str(SCORER), str(EXAMPLE), "--json"],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        # 예전 CI 스텝은 stdout을 /dev/null로 버렸다. 파싱까지 해서 조금 더 본다.
        try:
            json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            self.fail(f"--json 출력이 JSON이 아니다: {exc}")


if __name__ == "__main__":
    unittest.main()
