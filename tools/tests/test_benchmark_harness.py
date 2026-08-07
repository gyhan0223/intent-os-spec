#!/usr/bin/env python3
"""하네스가 측정을 지어내지 않는지 검사한다.

여기서 지키려는 성질은 하나다 — **합성 실행과 사람 없는 실행이 실측으로
오인될 수 없어야 한다.** 두 기록은 형태가 같으므로 `provenance` 하나가
유일한 구분 장치다. 그 장치가 새면 벤치마크 전체가 무의미해진다.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from benchmarks.harness.adapters import AdapterError, SyntheticAdapter, build_adapter
from benchmarks.harness.runner import HumanProbe, TrialRunner, build_run_record, trial_order

CASE = {"id": "T01", "category": "writing", "prompt": "테스트", "tool_requirement": "none"}
ALL_HUMAN = {"selection_time": True, "rework": True, "satisfaction": True, "quality_judges": True}


class ProvenanceTest(unittest.TestCase):
    def _record(self, adapter_kinds, human):
        return build_run_record(
            trials=[], resource_pool=[], fixed_default="model:balanced",
            router_version="v", router_config={}, seed=1,
            operator_expertise="intermediate", adapter_kinds=adapter_kinds,
            human_measurements=human, started_at="2026-01-01T00:00:00Z",
            case_suite_version="0.1", judge_ids=["j1"],
        )

    def test_synthetic_run_is_never_evidence(self):
        rec = self._record(["synthetic"], ALL_HUMAN)
        self.assertFalse(rec["provenance"]["evidence"])
        self.assertIn("합성", rec["provenance"]["notes"])

    def test_missing_human_measurement_is_never_evidence(self):
        for missing in ALL_HUMAN:
            with self.subTest(missing=missing):
                human = {**ALL_HUMAN, missing: False}
                rec = self._record(["live_api"], human)
                self.assertFalse(rec["provenance"]["evidence"],
                                 f"{missing}이 비었는데 근거로 표시됐다")

    def test_live_run_with_all_human_measurements_is_evidence(self):
        rec = self._record(["live_api", "human"], ALL_HUMAN)
        self.assertTrue(rec["provenance"]["evidence"])


class ManualArmTest(unittest.TestCase):
    def test_manual_arm_is_excluded_without_a_human(self):
        """사람이 없으면 Manual arm은 성립하지 않는다. 임의 선택으로 때우지 않는다."""
        runner = TrialRunner(
            adapters={"model:balanced": SyntheticAdapter("model:balanced")},
            fixed_default_resource_id="model:balanced",
            router=_StubRouter(),
            probe=HumanProbe(enabled=False),
        )
        trial = runner.run_trial(CASE, "manual", 1)
        self.assertTrue(trial["excluded"])
        self.assertEqual(trial["status"], "user_abandoned")
        self.assertEqual(trial["selected_resource_ids"], [])

    def test_human_probe_returns_none_when_disabled(self):
        """기본값으로 때우면 그 값이 조용히 데이터가 된다."""
        probe = HumanProbe(enabled=False)
        self.assertIsNone(probe.rework_count())
        self.assertIsNone(probe.satisfaction())
        self.assertIsNone(probe.accepted())

    def test_satisfaction_is_null_not_zero_when_unmeasured(self):
        runner = TrialRunner(
            adapters={"model:balanced": SyntheticAdapter("model:balanced")},
            fixed_default_resource_id="model:balanced",
            router=_StubRouter(), probe=HumanProbe(enabled=False),
        )
        trial = runner.run_trial(CASE, "fixed", 1)
        self.assertIsNone(trial["satisfaction_1_7"], "만족도가 임의 값으로 채워졌다")
        self.assertIsNone(trial["quality_score"], "품질이 Judge 없이 채워졌다")


class AdapterTest(unittest.TestCase):
    def test_missing_credentials_does_not_fall_back_to_synthetic(self):
        """조용한 합성 대체는 실측인 줄 알고 돌린 실행을 오염시킨다."""
        spec = {"resource_id": "model:x", "kind": "model", "model": "m",
                "api_key_env": "DEFINITELY_UNSET_KEY_FOR_TEST",
                "pricing_snapshot": {"input_per_mtok": 1, "output_per_mtok": 1}}
        with self.assertRaises(AdapterError):
            build_adapter(spec, allow_synthetic=False)

        adapter = build_adapter(spec, allow_synthetic=True)
        self.assertEqual(adapter.kind, "synthetic")

    def test_synthetic_output_is_labelled(self):
        result = SyntheticAdapter("model:x").execute("입력")
        self.assertIn("SYNTHETIC", result.output)
        self.assertEqual(result.cost_usd, 0.0, "합성 실행이 비용을 주장하면 M3가 오염된다")


class OrderTest(unittest.TestCase):
    def test_arm_order_is_randomized_per_case(self):
        """§12 Order Effect."""
        plan = trial_order([CASE, {**CASE, "id": "T02"}], seed=7)
        self.assertEqual(len(plan), 6)
        self.assertEqual({arm for _, arm, _ in plan}, {"manual", "fixed", "intent_os"})

    def test_order_is_reproducible_from_seed(self):
        a = [(c["id"], arm) for c, arm, _ in trial_order([CASE], seed=42)]
        b = [(c["id"], arm) for c, arm, _ in trial_order([CASE], seed=42)]
        self.assertEqual(a, b)


class _StubRouter:
    def rank(self, case):
        return ["model:balanced"]


class RunnerCliTest(unittest.TestCase):
    def test_cli_refuses_live_run_without_credentials(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "run.json"
            proc = subprocess.run(
                [sys.executable, "tools/run-system-benchmark.py",
                 "--pool", "benchmarks/pools/example-pool.json",
                 "--out", str(out), "--operator-expertise", "intermediate", "--limit", "1"],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertFalse(out.exists(), "실패했는데 기록 파일이 생겼다")

    def test_synthetic_cli_run_is_schema_valid_and_not_evidence(self):
        from jsonschema import Draft202012Validator
        schema = json.loads(
            (ROOT / "benchmarks" / "schemas" / "system-benchmark-run.schema.json")
            .read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "run.json"
            proc = subprocess.run(
                [sys.executable, "tools/run-system-benchmark.py",
                 "--pool", "benchmarks/pools/example-pool.json",
                 "--out", str(out), "--operator-expertise", "intermediate",
                 "--allow-synthetic", "--no-human", "--limit", "1"],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            record = json.loads(out.read_text(encoding="utf-8"))
            errors = [e.message for e in Draft202012Validator(schema).iter_errors(record)]
            self.assertEqual(errors, [], "생성된 기록이 스키마를 위반한다")
            self.assertFalse(record["provenance"]["evidence"])


if __name__ == "__main__":
    unittest.main()
