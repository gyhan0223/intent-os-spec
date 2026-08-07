from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from reference.marketing_thin.runtime import RESOURCES, MarketingThinRuntime, validate_core_invariants


ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "intent-os-spec" / "schemas"


class ThinReferenceSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = MarketingThinRuntime().run(
            "윈터스쿨 모집 마케팅 문서를 조사부터 검수까지 완성한다",
            user_rating=5,
        )

    def _validate(self, schema_name: str, instance: dict) -> None:
        schema = json.loads((SCHEMA_DIR / schema_name).read_text(encoding="utf-8"))
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(instance)

    def test_end_to_end_route(self) -> None:
        route = [task["assigned_resource_id"] for task in self.bundle["tasks"]]
        self.assertEqual(route, ["tool:web-search", "model:balanced", "model:quality"])
        self.assertEqual(len(RESOURCES), 4)
        self.assertEqual(self.bundle["evaluations"][-1]["verdict"], "accept")
        final = self.bundle["artifact_contents"][self.bundle["final_artifact_id"]]
        self.assertIn("검수 완료본", final)
        self.assertIn("CTA", final)

    def test_core_invariants(self) -> None:
        validate_core_invariants(self.bundle)
        self.assertEqual(len(self.bundle["executions"]), len(self.bundle["outcomes"]))
        self.assertEqual(len(self.bundle["outcomes"]), len(self.bundle["evaluations"]))

    def test_canonical_schemas(self) -> None:
        self._validate("goal.schema.json", self.bundle["goal"])
        self._validate("intent.schema.json", self.bundle["intent"])
        for item in self.bundle["tasks"]:
            self._validate("task.schema.json", item)
        for item in self.bundle["decisions"]:
            self._validate("decision.schema.json", item)
        for item in self.bundle["executions"]:
            self._validate("execution.schema.json", item)
        for item in self.bundle["outcomes"]:
            self._validate("outcome.schema.json", item)
        for item in self.bundle["artifacts"]:
            self._validate("artifact.schema.json", item)
        for item in self.bundle["evaluations"]:
            self._validate("evaluation.schema.json", item)

    def test_user_rating_flows_into_evaluation(self) -> None:
        bundle = MarketingThinRuntime().run("마케팅 문서를 만든다", user_rating=3)
        self.assertEqual(bundle["evaluations"][-1]["scores"]["satisfaction"], 0.5)


if __name__ == "__main__":
    unittest.main()
