#!/usr/bin/env python3
"""Validate cross-entity Intent OS Global Invariants against a state snapshot.

This validator complements JSON Schema validation. Schemas prove that each record has
an acceptable *shape*; this script proves that records are mutually consistent.

Implemented global invariants:
  INV-01 Goal Reachability
  INV-03 Execution Provenance
  INV-04 Outcome Completeness
  INV-08 Acyclicity
  INV-13 Temporal Ordering
  INV-14 Single Active Plan
  INV-15 Profile Existence

Snapshot format
---------------
A snapshot is a JSON object whose top-level keys are plural entity collections, e.g.
`goals`, `tasks`, `decisions`, `executions`, `outcomes`, `plans`, `resources`, and
`resource_profiles`. Graph collections are `goal_graphs`, `task_graphs`, and
`workflows`. Records may be full canonical entities or projections containing only
fields needed by the checks. Unknown top-level collections are ignored.

Usage:
    python3 tools/validate-invariants.py path/to/snapshot.json
    python3 tools/validate-invariants.py snapshot-a.json snapshot-b.json
    python3 tools/validate-invariants.py snapshot.json --only INV-01,INV-04
    python3 tools/validate-invariants.py snapshot.json --format json

Exit codes:
    0  all selected invariants hold
    1  one or more invariant violations
    2  invalid input / CLI error
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable


TERMINAL_EXECUTION_STATUSES = {"Completed", "Failed", "TimedOut", "Aborted"}
IMPLEMENTED_INVARIANTS = (
    "INV-01",
    "INV-03",
    "INV-04",
    "INV-08",
    "INV-13",
    "INV-14",
    "INV-15",
)


@dataclass(frozen=True)
class Violation:
    invariant: str
    message: str
    entity_type: str | None = None
    entity_id: str | None = None
    details: dict[str, Any] | None = None


class SnapshotError(ValueError):
    pass


def _collection(snapshot: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = snapshot.get(key, [])
    if value is None:
        return []
    if not isinstance(value, list):
        raise SnapshotError(f"top-level `{key}` must be an array")
    bad = [i for i, item in enumerate(value) if not isinstance(item, dict)]
    if bad:
        raise SnapshotError(f"`{key}` contains non-object item(s) at index {bad[:5]}")
    return value


def _entity_id(record: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _index(records: Iterable[dict[str, Any]], *id_keys: str) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        record_id = _entity_id(record, *id_keys)
        if record_id:
            result[record_id].append(record)
    return result


def _parse_time(value: Any, *, field: str, owner: str) -> tuple[datetime | None, str | None]:
    if value is None:
        return None, None
    if not isinstance(value, str) or not value:
        return None, f"{owner}.{field} must be an ISO 8601 date-time string"
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None, f"{owner}.{field} is not a valid ISO 8601 date-time: {value!r}"
    if parsed.tzinfo is None:
        return None, f"{owner}.{field} must include a timezone offset: {value!r}"
    return parsed, None


def _cycle_path(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> list[str] | None:
    adjacency: dict[str, list[str]] = defaultdict(list)
    all_nodes = set(nodes)
    for source, target in edges:
        all_nodes.add(source)
        all_nodes.add(target)
        adjacency[source].append(target)

    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in all_nodes}
    stack: list[str] = []
    stack_pos: dict[str, int] = {}

    def visit(node: str) -> list[str] | None:
        color[node] = GRAY
        stack_pos[node] = len(stack)
        stack.append(node)
        for nxt in adjacency.get(node, []):
            if color[nxt] == WHITE:
                cycle = visit(nxt)
                if cycle:
                    return cycle
            elif color[nxt] == GRAY:
                start = stack_pos[nxt]
                return stack[start:] + [nxt]
        stack.pop()
        stack_pos.pop(node, None)
        color[node] = BLACK
        return None

    for node in sorted(all_nodes):
        if color[node] == WHITE:
            cycle = visit(node)
            if cycle:
                return cycle
    return None


def check_inv_01(snapshot: dict[str, Any]) -> list[Violation]:
    goals = _index(_collection(snapshot, "goals"), "goal_id", "id")
    intents = _index(_collection(snapshot, "intents"), "intent_id", "id")
    violations: list[Violation] = []

    for task in _collection(snapshot, "tasks"):
        task_id = _entity_id(task, "id", "task_id") or "<unknown>"
        resolved_goal_ids: set[str] = set()
        dangling: list[str] = []

        direct_goal_id = _entity_id(task, "goal_id")
        if direct_goal_id:
            if direct_goal_id in goals:
                resolved_goal_ids.add(direct_goal_id)
            else:
                dangling.append(f"goal_id={direct_goal_id}")

        intent_refs: list[str] = []
        intent_id = _entity_id(task, "intent_id")
        if intent_id:
            intent_refs.append(intent_id)
        if isinstance(task.get("intent_ids"), list):
            intent_refs.extend(x for x in task["intent_ids"] if isinstance(x, str) and x)

        for ref in intent_refs:
            matches = intents.get(ref, [])
            if len(matches) != 1:
                dangling.append(f"intent_id={ref}")
                continue
            goal_id = _entity_id(matches[0], "goal_id")
            if goal_id and goal_id in goals:
                resolved_goal_ids.add(goal_id)
            elif goal_id:
                dangling.append(f"intent:{ref}.goal_id={goal_id}")
            else:
                dangling.append(f"intent:{ref}.goal_id=<missing>")

        if not resolved_goal_ids:
            violations.append(Violation("INV-01", "Task cannot reach any existing Goal", "Task", task_id, {"dangling_references": dangling}))
        elif dangling:
            violations.append(Violation("INV-01", "Task reaches a Goal but also contains a dangling Goal/Intent reference", "Task", task_id, {"resolved_goal_ids": sorted(resolved_goal_ids), "dangling_references": dangling}))
    return violations


def check_inv_03(snapshot: dict[str, Any]) -> list[Violation]:
    decisions = _index(_collection(snapshot, "decisions"), "decision_id", "id")
    violations: list[Violation] = []

    for execution in _collection(snapshot, "executions"):
        execution_id = _entity_id(execution, "execution_id", "id") or "<unknown>"
        decision_id = _entity_id(execution, "decision_id")
        matches = decisions.get(decision_id or "", [])
        if len(matches) != 1:
            violations.append(Violation("INV-03", "Execution must reference exactly one existing Decision", "Execution", execution_id, {"decision_id": decision_id, "matching_decision_count": len(matches)}))
            continue

        execution_task_id = _entity_id(execution, "task_id")
        subject = matches[0].get("subject")
        decision_task_id = subject.get("task_id") if isinstance(subject, dict) else None
        if execution_task_id and decision_task_id and execution_task_id != decision_task_id:
            violations.append(Violation("INV-03", "Execution Task does not match the originating Decision subject Task", "Execution", execution_id, {"execution_task_id": execution_task_id, "decision_task_id": decision_task_id, "decision_id": decision_id}))
    return violations


def check_inv_04(snapshot: dict[str, Any]) -> list[Violation]:
    outcomes_by_execution: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for outcome in _collection(snapshot, "outcomes"):
        execution_id = _entity_id(outcome, "execution_id")
        if execution_id:
            outcomes_by_execution[execution_id].append(outcome)

    violations: list[Violation] = []
    for execution in _collection(snapshot, "executions"):
        execution_id = _entity_id(execution, "execution_id", "id") or "<unknown>"
        if execution.get("status") not in TERMINAL_EXECUTION_STATUSES:
            continue
        matches = outcomes_by_execution.get(execution_id, [])
        if len(matches) != 1:
            violations.append(Violation("INV-04", "Terminal Execution must have exactly one Outcome", "Execution", execution_id, {"status": execution.get("status"), "outcome_count": len(matches)}))
            continue

        actual_outcome_id = _entity_id(matches[0], "outcome_id", "id")
        linked_outcome_id = _entity_id(execution, "outcome_id")
        if linked_outcome_id and actual_outcome_id and linked_outcome_id != actual_outcome_id:
            violations.append(Violation("INV-04", "Execution.outcome_id disagrees with Outcome.execution_id relation", "Execution", execution_id, {"execution_outcome_id": linked_outcome_id, "actual_outcome_id": actual_outcome_id}))
        elif not linked_outcome_id:
            violations.append(Violation("INV-04", "Terminal Execution is missing its outcome_id back-link", "Execution", execution_id, {"actual_outcome_id": actual_outcome_id}))
    return violations


def _graph_violation(graph_type: str, graph_id: str, nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> Violation | None:
    cycle = _cycle_path(nodes, edges)
    if not cycle:
        return None
    return Violation("INV-08", f"{graph_type} must be acyclic", graph_type, graph_id, {"cycle": cycle})


def check_inv_08(snapshot: dict[str, Any]) -> list[Violation]:
    violations: list[Violation] = []

    for graph in _collection(snapshot, "goal_graphs"):
        graph_id = _entity_id(graph, "graph_id", "id") or "<unknown>"
        node_ids = []
        for node in graph.get("nodes", []):
            if isinstance(node, str):
                node_ids.append(node)
            elif isinstance(node, dict):
                node_id = _entity_id(node, "goal_id", "id")
                if node_id:
                    node_ids.append(node_id)
        edges = [(edge["from"], edge["to"]) for edge in graph.get("edges", []) if isinstance(edge, dict) and isinstance(edge.get("from"), str) and isinstance(edge.get("to"), str)]
        violation = _graph_violation("GoalGraph", graph_id, node_ids, edges)
        if violation:
            violations.append(violation)

    for graph in _collection(snapshot, "task_graphs"):
        graph_id = _entity_id(graph, "graph_id", "id") or "<unknown>"
        node_ids = [node for node in graph.get("nodes", []) if isinstance(node, str)]
        edges = [(edge["from"], edge["to"]) for edge in graph.get("edges", []) if isinstance(edge, dict) and isinstance(edge.get("from"), str) and isinstance(edge.get("to"), str)]
        violation = _graph_violation("TaskGraph", graph_id, node_ids, edges)
        if violation:
            violations.append(violation)

    for plan in _collection(snapshot, "plans"):
        plan_id = _entity_id(plan, "plan_id", "id") or "<unknown>"
        tasks = [task for task in plan.get("tasks", []) if isinstance(task, dict)]
        node_ids = [task_id for task in tasks if (task_id := _entity_id(task, "task_id", "id"))]
        edges: list[tuple[str, str]] = []
        for task in tasks:
            task_id = _entity_id(task, "task_id", "id")
            if not task_id:
                continue
            for dep in task.get("depends_on", []):
                if isinstance(dep, str):
                    edges.append((dep, task_id))
        violation = _graph_violation("PlanTaskGraph", plan_id, node_ids, edges)
        if violation:
            violations.append(violation)

    for workflow in _collection(snapshot, "workflows"):
        workflow_id = _entity_id(workflow, "workflow_id", "id") or "<unknown>"
        steps = [step for step in workflow.get("steps", []) if isinstance(step, dict)]
        node_ids = [step_id for step in steps if (step_id := _entity_id(step, "step_id", "id"))]
        edges: list[tuple[str, str]] = []
        for step in steps:
            source = _entity_id(step, "step_id", "id")
            if not source:
                continue
            for field in ("next", "on_true", "on_false", "branch_to", "compensation"):
                target = step.get(field)
                if isinstance(target, str) and target:
                    edges.append((source, target))
            branches = step.get("branches", [])
            if isinstance(branches, list):
                edges.extend((source, target) for target in branches if isinstance(target, str) and target)
        violation = _graph_violation("Workflow", workflow_id, node_ids, edges)
        if violation:
            violations.append(violation)

    return violations


def check_inv_13(snapshot: dict[str, Any]) -> list[Violation]:
    decisions = _index(_collection(snapshot, "decisions"), "decision_id", "id")
    outcomes = _index(_collection(snapshot, "outcomes"), "outcome_id", "id")
    evaluations_by_outcome: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for evaluation in _collection(snapshot, "evaluations"):
        outcome_id = _entity_id(evaluation, "outcome_id")
        if outcome_id:
            evaluations_by_outcome[outcome_id].append(evaluation)

    violations: list[Violation] = []

    def parse(owner_type: str, owner_id: str, record: dict[str, Any], field: str) -> datetime | None:
        parsed, error = _parse_time(record.get(field), field=field, owner=f"{owner_type}:{owner_id}")
        if error:
            violations.append(Violation("INV-13", error, owner_type, owner_id))
        return parsed

    for execution in _collection(snapshot, "executions"):
        execution_id = _entity_id(execution, "execution_id", "id") or "<unknown>"
        created_at = parse("Execution", execution_id, execution, "created_at")
        started_at = parse("Execution", execution_id, execution, "started_at")
        finished_at = parse("Execution", execution_id, execution, "finished_at")

        if created_at and started_at and created_at > started_at:
            violations.append(Violation("INV-13", "Execution.created_at must be <= started_at", "Execution", execution_id))
        if started_at and finished_at and started_at > finished_at:
            violations.append(Violation("INV-13", "Execution.started_at must be <= finished_at", "Execution", execution_id))

        decision_id = _entity_id(execution, "decision_id")
        decision_matches = decisions.get(decision_id or "", [])
        if len(decision_matches) == 1 and started_at:
            decided_at = parse("Decision", decision_id or "<unknown>", decision_matches[0], "decided_at")
            if decided_at and decided_at > started_at:
                violations.append(Violation("INV-13", "Decision.decided_at must be <= Execution.started_at", "Execution", execution_id, {"decision_id": decision_id}))

        linked_outcome_id = _entity_id(execution, "outcome_id")
        if not linked_outcome_id:
            continue
        outcome_matches = outcomes.get(linked_outcome_id, [])
        if len(outcome_matches) != 1:
            continue
        outcome = outcome_matches[0]
        measured_at = parse("Outcome", linked_outcome_id, outcome, "measured_at")
        if finished_at and measured_at and finished_at > measured_at:
            violations.append(Violation("INV-13", "Execution.finished_at must be <= Outcome.measured_at", "Execution", execution_id, {"outcome_id": linked_outcome_id}))

        for evaluation in evaluations_by_outcome.get(linked_outcome_id, []):
            evaluation_id = _entity_id(evaluation, "evaluation_id", "id") or "<unknown>"
            evaluated_at = parse("Evaluation", evaluation_id, evaluation, "evaluated_at")
            if measured_at and evaluated_at and measured_at > evaluated_at:
                violations.append(Violation("INV-13", "Outcome.measured_at must be <= Evaluation.evaluated_at", "Evaluation", evaluation_id, {"outcome_id": linked_outcome_id}))
    return violations


def check_inv_14(snapshot: dict[str, Any]) -> list[Violation]:
    active_by_goal: dict[str, list[str]] = defaultdict(list)
    for plan in _collection(snapshot, "plans"):
        if plan.get("status") != "Active":
            continue
        plan_id = _entity_id(plan, "plan_id", "id") or "<unknown>"
        source_goal_ids = plan.get("source_goal_ids", [])
        if not isinstance(source_goal_ids, list):
            continue
        for goal_id in source_goal_ids:
            if isinstance(goal_id, str) and goal_id:
                active_by_goal[goal_id].append(plan_id)

    return [Violation("INV-14", "Goal has more than one Active Plan", "Goal", goal_id, {"active_plan_ids": plan_ids}) for goal_id, plan_ids in sorted(active_by_goal.items()) if len(plan_ids) > 1]


def check_inv_15(snapshot: dict[str, Any]) -> list[Violation]:
    profiles = _index(_collection(snapshot, "resource_profiles"), "resource_id")
    violations: list[Violation] = []
    for resource in _collection(snapshot, "resources"):
        if resource.get("lifecycle") != "Active":
            continue
        resource_id = _entity_id(resource, "id", "resource_id") or "<unknown>"
        matches = profiles.get(resource_id, [])
        if len(matches) != 1:
            violations.append(Violation("INV-15", "Active Resource must have exactly one Resource Profile", "Resource", resource_id, {"profile_count": len(matches)}))
    return violations


CHECKS: dict[str, Callable[[dict[str, Any]], list[Violation]]] = {
    "INV-01": check_inv_01,
    "INV-03": check_inv_03,
    "INV-04": check_inv_04,
    "INV-08": check_inv_08,
    "INV-13": check_inv_13,
    "INV-14": check_inv_14,
    "INV-15": check_inv_15,
}


def validate_snapshot(snapshot: dict[str, Any], selected: Iterable[str] | None = None) -> list[Violation]:
    if not isinstance(snapshot, dict):
        raise SnapshotError("snapshot root must be a JSON object")
    selected_ids = tuple(selected or IMPLEMENTED_INVARIANTS)
    unknown = [inv for inv in selected_ids if inv not in CHECKS]
    if unknown:
        raise SnapshotError(f"unknown/unimplemented invariant(s): {', '.join(unknown)}")
    violations: list[Violation] = []
    for invariant in selected_ids:
        violations.extend(CHECKS[invariant](snapshot))
    return violations


def _load_snapshot(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise SnapshotError(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SnapshotError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SnapshotError(f"snapshot root must be an object: {path}")
    return data


def _parse_only(raw: str | None) -> tuple[str, ...]:
    if not raw:
        return IMPLEMENTED_INVARIANTS
    selected = tuple(part.strip().upper() for part in raw.split(",") if part.strip())
    unknown = [inv for inv in selected if inv not in CHECKS]
    if unknown:
        raise SnapshotError(f"unknown/unimplemented invariant(s): {', '.join(unknown)}")
    return selected


def _print_text(path: Path, violations: list[Violation], selected: tuple[str, ...]) -> None:
    if not violations:
        print(f"PASS {path}: {len(selected)} invariant(s) checked")
        return
    print(f"FAIL {path}: {len(violations)} violation(s)")
    for violation in violations:
        owner = ""
        if violation.entity_type or violation.entity_id:
            owner = f" [{violation.entity_type or '?'}:{violation.entity_id or '?'}]"
        print(f"  {violation.invariant}{owner} {violation.message}")
        if violation.details:
            print(f"    details={json.dumps(violation.details, ensure_ascii=False, sort_keys=True)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshots", nargs="+", help="JSON state snapshot(s) to validate")
    parser.add_argument("--only", help="comma-separated invariant ids, e.g. INV-01,INV-04")
    parser.add_argument("--format", choices=("text", "json"), default="text", dest="output_format")
    args = parser.parse_args(argv)

    try:
        selected = _parse_only(args.only)
        results = []
        failed = False
        for raw_path in args.snapshots:
            path = Path(raw_path)
            snapshot = _load_snapshot(path)
            violations = validate_snapshot(snapshot, selected)
            failed = failed or bool(violations)
            if args.output_format == "text":
                _print_text(path, violations, selected)
            else:
                results.append({"snapshot": str(path), "selected_invariants": list(selected), "passed": not violations, "violations": [asdict(v) for v in violations]})
        if args.output_format == "json":
            print(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True))
        return 1 if failed else 0
    except SnapshotError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
