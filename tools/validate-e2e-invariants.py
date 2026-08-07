#!/usr/bin/env python3
"""Run Global Invariants against End-to-End Golden Fixtures plus invariant evidence.

The canonical E2E fixture focuses on product flow. `invariant-evidence-v0.1.json`
adds the minimum cross-cutting records/audit projections needed to exercise all 16
Global Invariants without bloating the base scenarios.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_FILE = ROOT / "fixtures" / "e2e" / "golden-fixtures-v0.1.json"
EVIDENCE_FILE = ROOT / "fixtures" / "e2e" / "invariant-evidence-v0.1.json"
SCHEMA_DIR = ROOT / "intent-os-spec" / "schemas"
INVARIANT_SCRIPT = ROOT / "tools" / "validate-invariants.py"

spec = importlib.util.spec_from_file_location("validate_invariants", INVARIANT_SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot import {INVARIANT_SCRIPT}")
inv = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = inv
spec.loader.exec_module(inv)

SCHEMA_TO_COLLECTION = {
    "goal.schema.json": "goals", "goal-graph.schema.json": "goal_graphs",
    "intent.schema.json": "intents", "context.schema.json": "contexts",
    "constraint.schema.json": "constraints", "task.schema.json": "tasks",
    "task-graph.schema.json": "task_graphs", "capability.schema.json": "capabilities",
    "resource.schema.json": "resources", "plan.schema.json": "plans",
    "decision.schema.json": "decisions", "memory.schema.json": "memories",
    "knowledge.schema.json": "knowledge", "feedback.schema.json": "feedback",
    "execution.schema.json": "executions", "outcome.schema.json": "outcomes",
    "evaluation.schema.json": "evaluations", "artifact.schema.json": "artifacts",
    "assumption.schema.json": "assumptions", "risk.schema.json": "risks",
    "policy.schema.json": "policies", "event.schema.json": "events",
    "session.schema.json": "sessions", "workflow.schema.json": "workflows",
    "agent.schema.json": "agents", "tool.schema.json": "tools",
    "resource-profile.schema.json": "resource_profiles",
}
TERMINAL_EXECUTION = {"Completed", "Failed", "TimedOut", "Aborted"}


def validate_extra_records(sid: str, records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    checker = FormatChecker()
    for idx, record in enumerate(records):
        schema_name = record.get("schema")
        data = record.get("data")
        if not isinstance(schema_name, str) or not isinstance(data, dict):
            errors.append(f"{sid}: evidence record[{idx}] must contain schema:string and data:object")
            continue
        schema_path = SCHEMA_DIR / schema_name
        if not schema_path.exists():
            errors.append(f"{sid}: evidence references missing schema {schema_name}")
            continue
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=checker)
        for error in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
            path = ".".join(str(p) for p in error.path) or "<root>"
            errors.append(f"{sid}: evidence {schema_name} {path}: {error.message}")
    return errors


def append_records(snapshot: dict[str, Any], records: list[dict[str, Any]]) -> None:
    for record in records:
        if not isinstance(record, dict):
            continue
        schema_name = record.get("schema")
        data = record.get("data")
        collection = SCHEMA_TO_COLLECTION.get(schema_name)
        if collection and isinstance(data, dict):
            snapshot.setdefault(collection, []).append(data)


def collapse_state_versions(snapshot: dict[str, Any]) -> None:
    # E2E S10 intentionally stores before/after snapshots of the same Resource Profile.
    # The invariant checker consumes a *current state* snapshot, so keep the last
    # occurrence for each profile_id while the base E2E validator still verifies both.
    profiles = snapshot.get("resource_profiles")
    if isinstance(profiles, list):
        latest: dict[str, dict[str, Any]] = {}
        order: list[str] = []
        anonymous: list[dict[str, Any]] = []
        for profile in profiles:
            pid = profile.get("profile_id") if isinstance(profile, dict) else None
            if isinstance(pid, str) and pid:
                if pid not in latest:
                    order.append(pid)
                latest[pid] = profile
            elif isinstance(profile, dict):
                anonymous.append(profile)
        snapshot["resource_profiles"] = [latest[pid] for pid in order] + anonymous


def project_scenario(scenario: dict[str, Any], supplement: dict[str, Any]) -> dict[str, Any]:
    snapshot: dict[str, Any] = defaultdict(list)
    append_records(snapshot, scenario.get("records", []))
    append_records(snapshot, supplement.get("records", []))
    for key in ("mutations", "constraint_evaluations", "policy_evaluations", "state_transitions", "deletions"):
        value = supplement.get(key)
        if isinstance(value, list):
            snapshot[key].extend(x for x in value if isinstance(x, dict))
    collapse_state_versions(snapshot)
    return dict(snapshot)


def check_assignment_evidence(snapshot: dict[str, Any], assignments: list[dict[str, Any]]) -> list[Any]:
    """E2E-specific positive evidence for INV-02 after Task has moved past Assigned.

    Canonical Task snapshots in the Golden Fixtures are terminal (Evaluated), so the
    transient Assigned state is not stored. The evidence overlay freezes the assignment
    tuple and we verify it against the immutable ResourceSelection Decision and Execution.
    """
    violations: list[Any] = []
    decisions = {d.get("decision_id"): d for d in snapshot.get("decisions", []) if isinstance(d, dict)}
    executions = snapshot.get("executions", [])
    for assignment in assignments:
        tid = assignment.get("task_id")
        rid = assignment.get("resource_id")
        did = assignment.get("decision_id")
        decision = decisions.get(did)
        if not isinstance(decision, dict):
            violations.append(inv.Violation("INV-02", "Assignment evidence references missing Decision", "Task", str(tid), {"decision_id": did}))
            continue
        subject = decision.get("subject") if isinstance(decision.get("subject"), dict) else {}
        selection = decision.get("selection")
        selected_rid = selection if isinstance(selection, str) else selection.get("resource_id") if isinstance(selection, dict) else None
        if decision.get("decision_type") != "ResourceSelection" or subject.get("task_id") != tid or selected_rid != rid or decision.get("status") not in {"Committed", "Applied", "Evaluated"}:
            violations.append(inv.Violation("INV-02", "Assignment evidence is not explained by a committed ResourceSelection Decision", "Task", str(tid), {"resource_id": rid, "decision_id": did}))
            continue
        matching_exec = [e for e in executions if isinstance(e, dict) and e.get("task_id") == tid and e.get("decision_id") == did and e.get("resource_id") == rid]
        if not matching_exec:
            violations.append(inv.Violation("INV-02", "Assignment evidence does not match any Execution provenance", "Task", str(tid), {"resource_id": rid, "decision_id": did}))
    return violations


def evidence(snapshot: dict[str, Any], supplement: dict[str, Any], invariant: str) -> bool:
    tasks = snapshot.get("tasks", [])
    decisions = snapshot.get("decisions", [])
    executions = snapshot.get("executions", [])
    outcomes = snapshot.get("outcomes", [])
    evaluations = snapshot.get("evaluations", [])
    plans = snapshot.get("plans", [])
    constraints = snapshot.get("constraints", [])
    if invariant == "INV-01": return bool(tasks and snapshot.get("goals"))
    if invariant == "INV-02": return bool(supplement.get("assignments")) or any(t.get("state") == "Assigned" or t.get("assigned_resource_id") for t in tasks)
    if invariant == "INV-03": return bool(executions and decisions)
    if invariant == "INV-04": return any(e.get("status") in TERMINAL_EXECUTION for e in executions)
    if invariant == "INV-05": return bool(snapshot.get("artifacts"))
    if invariant == "INV-06": return bool(snapshot.get("mutations"))
    if invariant == "INV-07": return any(c.get("hardness") == "Hard" for c in constraints) and bool(decisions)
    if invariant == "INV-08": return bool(snapshot.get("goal_graphs") or snapshot.get("task_graphs") or snapshot.get("workflows") or plans)
    if invariant == "INV-09": return bool(tasks and decisions)
    if invariant == "INV-10": return bool(snapshot.get("assumptions"))
    if invariant == "INV-11": return bool(snapshot.get("policies") and snapshot.get("policy_evaluations"))
    if invariant == "INV-12": return bool(snapshot.get("state_transitions") and snapshot.get("events"))
    if invariant == "INV-13": return bool(executions and outcomes and evaluations)
    if invariant == "INV-14": return bool(plans)
    if invariant == "INV-15": return any(r.get("lifecycle") == "Active" for r in snapshot.get("resources", []))
    if invariant == "INV-16": return bool(snapshot.get("sessions") or snapshot.get("deletions"))
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-all-covered", action="store_true")
    args = parser.parse_args()

    payload = json.loads(FIXTURE_FILE.read_text(encoding="utf-8"))
    evidence_payload = json.loads(EVIDENCE_FILE.read_text(encoding="utf-8"))
    scenarios = payload.get("scenarios")
    supplements = evidence_payload.get("supplements", {})
    if not isinstance(scenarios, list) or not isinstance(supplements, dict):
        print("ERROR: invalid fixture/evidence envelope", file=sys.stderr)
        return 2

    coverage: dict[str, list[str]] = {iid: [] for iid in inv.IMPLEMENTED_INVARIANTS}
    violations: list[tuple[str, Any]] = []
    schema_errors: list[str] = []

    for scenario in scenarios:
        sid = str(scenario.get("scenario_id", "<unknown>"))
        supplement = supplements.get(sid, {})
        if not isinstance(supplement, dict):
            supplement = {}
        extra_records = supplement.get("records", [])
        if isinstance(extra_records, list):
            schema_errors.extend(validate_extra_records(sid, extra_records))
        snapshot = project_scenario(scenario, supplement)
        for iid in inv.IMPLEMENTED_INVARIANTS:
            if evidence(snapshot, supplement, iid):
                coverage[iid].append(sid)
        for violation in inv.validate_snapshot(snapshot):
            violations.append((sid, violation))
        assignments = supplement.get("assignments", [])
        if isinstance(assignments, list):
            for violation in check_assignment_evidence(snapshot, [x for x in assignments if isinstance(x, dict)]):
                violations.append((sid, violation))

    if schema_errors:
        print(f"FAILED: {len(schema_errors)} invariant evidence schema error(s)", file=sys.stderr)
        for error in schema_errors:
            print(f"  {error}", file=sys.stderr)
        return 1

    print(f"E2E invariant validation: {len(scenarios)} scenario(s), {len(inv.IMPLEMENTED_INVARIANTS)} invariant(s)")
    print("Coverage:")
    for iid in inv.IMPLEMENTED_INVARIANTS:
        label = ", ".join(coverage[iid]) if coverage[iid] else "NOT COVERED"
        print(f"  {iid}: {label}")

    if violations:
        print(f"FAILED: {len(violations)} invariant violation(s)", file=sys.stderr)
        for sid, violation in violations:
            owner = f" [{violation.entity_type or '?'}:{violation.entity_id or '?'}]" if violation.entity_type or violation.entity_id else ""
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
