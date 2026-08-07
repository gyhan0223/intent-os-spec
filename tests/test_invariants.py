#!/usr/bin/env python3
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "validate-invariants.py"
FIXTURE = ROOT / "tests" / "invariants" / "valid-chain.json"

spec = importlib.util.spec_from_file_location("validate_invariants", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class InvariantCheckerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def snapshot(self):
        return copy.deepcopy(self.baseline)

    def assert_only(self, snapshot, invariant):
        violations = module.validate_snapshot(snapshot, [invariant])
        self.assertGreaterEqual(len(violations), 1)
        self.assertTrue(all(v.invariant == invariant for v in violations))

    def test_valid_chain_passes_all_implemented_invariants(self):
        self.assertEqual(module.validate_snapshot(self.snapshot()), [])

    def test_inv_01_goal_reachability(self):
        snapshot = self.snapshot()
        snapshot["tasks"][0]["goal_id"] = "goal_missing"
        self.assert_only(snapshot, "INV-01")

    def test_inv_03_execution_provenance_missing_decision(self):
        snapshot = self.snapshot()
        snapshot["executions"][0]["decision_id"] = "dec_missing"
        self.assert_only(snapshot, "INV-03")

    def test_inv_03_execution_provenance_task_mismatch(self):
        snapshot = self.snapshot()
        snapshot["decisions"][0]["subject"]["task_id"] = "task_other"
        self.assert_only(snapshot, "INV-03")

    def test_inv_04_outcome_completeness(self):
        snapshot = self.snapshot()
        snapshot["outcomes"] = []
        self.assert_only(snapshot, "INV-04")

    def test_inv_08_goal_graph_cycle(self):
        snapshot = self.snapshot()
        snapshot["goal_graphs"][0]["nodes"] = ["goal_001", "goal_002"]
        snapshot["goal_graphs"][0]["edges"] = [
            {"from": "goal_001", "to": "goal_002"},
            {"from": "goal_002", "to": "goal_001"}
        ]
        self.assert_only(snapshot, "INV-08")

    def test_inv_08_task_graph_cycle(self):
        snapshot = self.snapshot()
        snapshot["task_graphs"][0]["nodes"] = ["task_001", "task_002"]
        snapshot["task_graphs"][0]["edges"] = [
            {"from": "task_001", "to": "task_002"},
            {"from": "task_002", "to": "task_001"}
        ]
        self.assert_only(snapshot, "INV-08")

    def test_inv_08_workflow_cycle(self):
        snapshot = self.snapshot()
        snapshot["workflows"][0]["steps"] = [
            {"step_id": "step_1", "control": "sequence", "next": "step_2"},
            {"step_id": "step_2", "control": "sequence", "next": "step_1"}
        ]
        self.assert_only(snapshot, "INV-08")

    def test_inv_13_temporal_ordering(self):
        snapshot = self.snapshot()
        snapshot["executions"][0]["started_at"] = "2026-08-07T08:59:00Z"
        self.assert_only(snapshot, "INV-13")

    def test_inv_14_single_active_plan(self):
        snapshot = self.snapshot()
        second = copy.deepcopy(snapshot["plans"][0])
        second["plan_id"] = "plan_002"
        second["version"] = 2
        snapshot["plans"].append(second)
        self.assert_only(snapshot, "INV-14")

    def test_inv_15_profile_existence_missing(self):
        snapshot = self.snapshot()
        snapshot["resource_profiles"] = []
        self.assert_only(snapshot, "INV-15")

    def test_inv_15_profile_existence_duplicate(self):
        snapshot = self.snapshot()
        duplicate = copy.deepcopy(snapshot["resource_profiles"][0])
        duplicate["profile_id"] = "rp_002"
        snapshot["resource_profiles"].append(duplicate)
        self.assert_only(snapshot, "INV-15")


if __name__ == "__main__":
    unittest.main()
