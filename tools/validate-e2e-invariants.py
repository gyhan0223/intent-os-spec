#!/usr/bin/env python3
"""Run the Global Invariant checker against every End-to-End Golden Fixture.

The E2E fixture envelope stores typed records as {schema, data}. This bridge projects
those records into the collection-oriented snapshot format consumed by
`tools/validate-invariants.py`, validates all 16 Global Invariants, and reports which
invariants have concrete E2E evidence versus only a vacuous pass.

Usage:
    python3 tools/validate-e2e-invariants.py
    python3 tools/validate-e2e-invariants.py --require-all-covered
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_FILE = ROOT / "fixtures" / "e2e" / "golden-fixtures-v0.1.json"
INVARIANT_SCRIPT = ROOT / "tools" / "validate-invariants.py"

spec = importlib.util.spec_from_file_location("validate_invariants", INVARIANT_SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot import {INVARIANT_SCRIPT}")
inv = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = inv
spec.loader.exec_module(inv)

SCHEMA_TO_COLLECTION = {
    "goal.schema.json": "goals",
    "goal-graph.schema.json": "goal_graphs",
    "intent.schema.json": "intents",
    "context.schema.json": "contexts",
    "constraint.schema.json": "constraints",
    "task.schema.json": "tasks",
    "task-graph.schema.json": "task_graphs",
    "capability.schema.json": "capabilities",
    "resource.schema.json": "resources",
    "plan.schema.json": "plans",
    "decision.schema.json": "decisions",
    "memory.schema.json": "memories",
    "knowledge.schema.json": "knowledge",
    "feedback.schema.json": "feedback",
    "execution.schema.json": "executions",
    "outcome.schema.json": "outcomes",
    "evaluation.schema.json": "evaluations",
    "artifact.schema.json": "artifacts",
    "assumption.schema.json": "assumptions",
    "risk.schema.json": "risks",
    "policy.schema.json": "policies",
    "event.schema.json": "events",
    "session.schema.json": "sessions",
    "workflow.schema.json": "workflows",
    "agent.schema.json": "agents",
    "tool.schema.json": "tools",
    "resource-profile.schema.json": "resource_profiles",
}

TERMINAL_EXECUTION = {"Completed", "Failed", "TimedOut", "Aborted"}


def project_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    snapshot: dict[str, Any] = defaultdict(list)
    for record in scenario.get("records", []):
        if not isinstance(record, dict):
            continue
        schema_name = record.get("schema")
        data = record.get("data")
        collection = SCHEMA_TO_COLLECTION.get(schema_name)
        if collection and isinstance(data, dict):
            snapshot[collection].append(data)

    # Optional audit projections may be authored directly on a scenario later without
    # changing canonical Entity schemas.
    for key in (
        "mutations",
        "constraint_evaluations",
        "policy_evaluations",
        "state_transitions",
        "deletions",
    ):
        value = scenario.get(key)
        if isinstance(value, list):
            snapshot[key].extend(x for x in value if isinstance(x, dict))

    return dict(snapshot)


def evidence(snapshot: dict[str, Any], invariant: str) -> bool:
    tasks = snapshot.get("tasks", [])
    decisions = snapshot.get("decisions", [])
    executions = snapshot.get("executions", [])
    outcomes = snapshot.get("outcomes", [])
    evaluations = snapshot.get("evaluations", [])
    plans = snapshot.get("plans", [])
    constraints = snapshot.get("constraints", [])

    if invariant == "INV-01":
        return bool(tasks and snapshot.get("goals"))
    if invariant == "INV-02":
        return any(t.get("state") == "Assigned" or t.get("assigned_resource_id") for t in tasks)
    if invariant == "INV-03":
        return bool(executions and decisions)
    if invariant == "INV-04":
        return any(e.get("status") in TERMINAL_EXECUTION for e in executions)
    if invariant == "INV-05":
        return bool(snapshot.get("artifacts"))
    if invariant == "INV-06":
        return bool(snapshot.get("mutations"))
    if invariant == "INV-07":
        return any(c.get("hardness") == "Hard" for c in constraints) and bool(decisions)
    if invariant == "INV-08":
        return bool(snapshot.get("goal_graphs") or snapshot.get("task_graphs") or snapshot.get("workflows") or plans)
    if invariant == "INV-09":
        return bool(tasks and (decisions or executions or snapshot.get("resources") or snapshot.get("tools") or snapshot.get("agents")))
    if invariant == "INV-10":
        return bool(snapshot.get("assumptions"))
    if invariant == "INV-11":
        return bool(snapshot.get("policies") or snapshot.get("policy_evaluations"))
    if invariant == "INV-12":
        return bool(snapshot.get("state_transitions"))
    if invariant == "INV-13":
        return bool(executions and outcomes and evaluations)
    if invariant == "INV-14":
        return bool(plans)
    if invariant == "INV-15":
        return any(r.get("lifecycle") == "Active" for r in snapshot.get("resources", []))
    if invariant == "INV-16":
        return bool(snapshot.get("sessions") or snapshot.get("deletions"))
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-all-covered", action="store_true", help="fail if any INV-01..INV-16 lacks concrete E2E evidence")
    args = parser.parse_args()

    payload = json.loads(FIXTURE_FILE.read_text(encoding="utf-8"))
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list):
        print("ERROR: fixture scenarios must be a list", file=sys.stderr)
        return 2

    coverage: dict[str, list[str]] = {iid: [] for iid in inv.IMPLEMENTED_INVARIANTS}
    violations: list[tuple[str, Any]] = []

    for scenario in scenarios:
        sid = scenario.get("scenario_id", "<unknown>")
        snapshot = project_scenario(scenario)
        for iid in inv.IMPLEMENTED_INVARIANTS:
            if evidence(snapshot, iid):
                coverage[iid].append(str(sid))
        for violation in inv.validate_snapshot(snapshot):
            violations.append((str(sid), violation))

    print(f"E2E invariant validation: {len(scenarios)} scenario(s), {len(inv.IMPLEMENTED_INVARIANTS)} invariant(s)")
    print("Coverage:")
    for iid in inv.IMPLEMENTED_INVARIANTS:
        scenarios_for_inv = coverage[iid]
        label = ", ".join(scenarios_for_inv) if scenarios_for_inv else "NOT COVERED"
        print(f"  {iid}: {label}")

    if violations:
        print(f"FAILED: {len(violations)} invariant violation(s)", file=sys.stderr)
        for sid, violation in violations:
            owner = ""
            if violation.entity_type or violation.entity_id:
                owner = f" [{violation.entity_type or '?'}:{violation.entity_id or '?'}]"
            print(f"  {sid} {violation.invariant}{owner} {violation.message}", file=sys.stderr)
            if violation.details:
                print(f"    details={json.dumps(violation.details, ensure_ascii=False, sort_keys=True)}", file=sys.stderr)
        return 1

    uncovered = [iid for iid, scenario_ids in coverage.items() if not scenario_ids]
    if args.require_all_covered and uncovered:
        print("FAILED: E2E suite has no concrete evidence for " + ", ".join(uncovered), file=sys.stderr)
        return 1

    if uncovered:
        print("PASS WITH COVERAGE GAPS: " + ", ".join(uncovered))
    else:
        print("PASS: all 16 Global Invariants have concrete E2E evidence and no violations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
