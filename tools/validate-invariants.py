#!/usr/bin/env python3
"""Validate cross-entity Intent OS Global Invariants against a state snapshot.

JSON Schema validates individual records. This validator checks relationships and
system-wide semantics across records.

All 16 global invariants from entities/e000a-entity-relationships.md are implemented.
History-dependent rules use optional audit projections in the snapshot:

- mutations: before/after record mutations (INV-06)
- constraint_evaluations: hard-constraint results per Decision (INV-07)
- policy_evaluations: policy results per Decision (INV-11)
- state_transitions: lifecycle transitions emitted by the runtime (INV-12)

If those collections are absent, the corresponding invariant still validates what can
be proven from canonical entity state and otherwise passes vacuously. Production
conformance snapshots SHOULD include the audit projections.

Usage:
    python3 tools/validate-invariants.py path/to/snapshot.json
    python3 tools/validate-invariants.py snapshot.json --only INV-01,INV-04
    python3 tools/validate-invariants.py snapshot.json --format json
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
TERMINAL_SESSION_STATUSES = {"Completed", "Expired", "Aborted"}
IMPLEMENTED_INVARIANTS = tuple(f"INV-{i:02d}" for i in range(1, 17))

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
    out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        rid = _entity_id(record, *id_keys)
        if rid:
            out[rid].append(record)
    return out

def _single(index: dict[str, list[dict[str, Any]]], key: str | None) -> dict[str, Any] | None:
    if not key:
        return None
    matches = index.get(key, [])
    return matches[0] if len(matches) == 1 else None

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
        all_nodes.update((source, target))
        adjacency[source].append(target)
    color = {node: 0 for node in all_nodes}
    stack: list[str] = []
    pos: dict[str, int] = {}
    def visit(node: str) -> list[str] | None:
        color[node] = 1
        pos[node] = len(stack)
        stack.append(node)
        for nxt in adjacency.get(node, []):
            if color[nxt] == 0:
                found = visit(nxt)
                if found:
                    return found
            elif color[nxt] == 1:
                return stack[pos[nxt]:] + [nxt]
        stack.pop()
        pos.pop(node, None)
        color[node] = 2
        return None
    for node in sorted(all_nodes):
        if color[node] == 0:
            found = visit(node)
            if found:
                return found
    return None

def _resource_selection(decision: dict[str, Any]) -> str | None:
    selection = decision.get("selection")
    if isinstance(selection, str):
        return selection
    if isinstance(selection, dict):
        return _entity_id(selection, "resource_id", "id", "selected_resource_id")
    return None

def _subject_task_id(decision: dict[str, Any]) -> str | None:
    subject = decision.get("subject")
    return _entity_id(subject, "task_id") if isinstance(subject, dict) else None

def _subject_goal_id(decision: dict[str, Any]) -> str | None:
    subject = decision.get("subject")
    return _entity_id(subject, "goal_id") if isinstance(subject, dict) else None

def _active_plan_ids_for_assumption(snapshot: dict[str, Any], assumption: dict[str, Any]) -> list[str]:
    scope = assumption.get("scope") if isinstance(assumption.get("scope"), dict) else {}
    scoped_plan = _entity_id(scope, "plan_id")
    scoped_goal = _entity_id(scope, "goal_id")
    dependents = {x for x in assumption.get("dependents", []) if isinstance(x, str)} if isinstance(assumption.get("dependents"), list) else set()
    affected: list[str] = []
    for plan in _collection(snapshot, "plans"):
        if plan.get("status") != "Active":
            continue
        pid = _entity_id(plan, "plan_id", "id")
        goals = {x for x in plan.get("source_goal_ids", []) if isinstance(x, str)} if isinstance(plan.get("source_goal_ids"), list) else set()
        if pid and (pid == scoped_plan or pid in dependents or (scoped_goal and scoped_goal in goals)):
            affected.append(pid)
    return affected

def _text_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _text_values(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _text_values(item)

def _contains_marker(text: str, markers: Iterable[str]) -> str | None:
    low = text.casefold()
    for marker in markers:
        m = marker.strip().casefold()
        if len(m) >= 4 and m in low:
            return marker
    return None

def check_inv_01(snapshot: dict[str, Any]) -> list[Violation]:
    goals = _index(_collection(snapshot, "goals"), "goal_id", "id")
    intents = _index(_collection(snapshot, "intents"), "intent_id", "id")
    violations: list[Violation] = []
    for task in _collection(snapshot, "tasks"):
        tid = _entity_id(task, "id", "task_id") or "<unknown>"
        resolved: set[str] = set()
        dangling: list[str] = []
        gid = _entity_id(task, "goal_id")
        if gid:
            if gid in goals:
                resolved.add(gid)
            else:
                dangling.append(f"goal_id={gid}")
        refs: list[str] = []
        iid = _entity_id(task, "intent_id")
        if iid:
            refs.append(iid)
        if isinstance(task.get("intent_ids"), list):
            refs += [x for x in task["intent_ids"] if isinstance(x, str) and x]
        for ref in refs:
            intent = _single(intents, ref)
            if not intent:
                dangling.append(f"intent_id={ref}")
                continue
            igid = _entity_id(intent, "goal_id")
            if igid and igid in goals:
                resolved.add(igid)
            else:
                dangling.append(f"intent:{ref}.goal_id={igid or '<missing>'}")
        if not resolved:
            violations.append(Violation("INV-01", "Task cannot reach any existing Goal", "Task", tid, {"dangling_references": dangling}))
        elif dangling:
            violations.append(Violation("INV-01", "Task reaches a Goal but also contains a dangling Goal/Intent reference", "Task", tid, {"resolved_goal_ids": sorted(resolved), "dangling_references": dangling}))
    return violations

def check_inv_02(snapshot: dict[str, Any]) -> list[Violation]:
    decisions = _collection(snapshot, "decisions")
    violations: list[Violation] = []
    for task in _collection(snapshot, "tasks"):
        tid = _entity_id(task, "id", "task_id") or "<unknown>"
        assigned = _entity_id(task, "assigned_resource_id")
        if task.get("state") != "Assigned" and not assigned:
            continue
        if not assigned:
            violations.append(Violation("INV-02", "Assigned Task is missing assigned_resource_id", "Task", tid))
            continue
        explaining = [d for d in decisions if d.get("decision_type") == "ResourceSelection" and _subject_task_id(d) == tid and _resource_selection(d) == assigned and d.get("status") in {"Committed", "Applied", "Evaluated"}]
        if not explaining:
            violations.append(Violation("INV-02", "Task resource assignment has no committed ResourceSelection Decision", "Task", tid, {"assigned_resource_id": assigned}))
    return violations

def check_inv_03(snapshot: dict[str, Any]) -> list[Violation]:
    decisions = _index(_collection(snapshot, "decisions"), "decision_id", "id")
    violations: list[Violation] = []
    for execution in _collection(snapshot, "executions"):
        eid = _entity_id(execution, "execution_id", "id") or "<unknown>"
        did = _entity_id(execution, "decision_id")
        matches = decisions.get(did or "", [])
        if len(matches) != 1:
            violations.append(Violation("INV-03", "Execution must reference exactly one existing Decision", "Execution", eid, {"decision_id": did, "matching_decision_count": len(matches)}))
            continue
        etid = _entity_id(execution, "task_id")
        dtid = _subject_task_id(matches[0])
        if etid and dtid and etid != dtid:
            violations.append(Violation("INV-03", "Execution Task does not match originating Decision subject Task", "Execution", eid, {"execution_task_id": etid, "decision_task_id": dtid}))
    return violations

def check_inv_04(snapshot: dict[str, Any]) -> list[Violation]:
    by_exec: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for outcome in _collection(snapshot, "outcomes"):
        eid = _entity_id(outcome, "execution_id")
        if eid:
            by_exec[eid].append(outcome)
    violations: list[Violation] = []
    for execution in _collection(snapshot, "executions"):
        eid = _entity_id(execution, "execution_id", "id") or "<unknown>"
        if execution.get("status") not in TERMINAL_EXECUTION_STATUSES:
            continue
        matches = by_exec.get(eid, [])
        if len(matches) != 1:
            violations.append(Violation("INV-04", "Terminal Execution must have exactly one Outcome", "Execution", eid, {"outcome_count": len(matches)}))
            continue
        actual = _entity_id(matches[0], "outcome_id", "id")
        linked = _entity_id(execution, "outcome_id")
        if not linked or (actual and linked != actual):
            violations.append(Violation("INV-04", "Execution.outcome_id must agree with its unique Outcome", "Execution", eid, {"execution_outcome_id": linked, "actual_outcome_id": actual}))
    return violations

def check_inv_05(snapshot: dict[str, Any]) -> list[Violation]:
    outcomes = _index(_collection(snapshot, "outcomes"), "outcome_id", "id")
    artifacts = _collection(snapshot, "artifacts")
    artifact_ids = _index(artifacts, "artifact_id", "id")
    violations: list[Violation] = []
    for aid, records in artifact_ids.items():
        if len(records) != 1:
            violations.append(Violation("INV-05", "Artifact id must identify exactly one record", "Artifact", aid, {"record_count": len(records)}))
    for artifact in artifacts:
        aid = _entity_id(artifact, "artifact_id", "id") or "<unknown>"
        oid = _entity_id(artifact, "outcome_id")
        matches = outcomes.get(oid or "", [])
        if len(matches) != 1:
            violations.append(Violation("INV-05", "Artifact must belong to exactly one existing Outcome", "Artifact", aid, {"outcome_id": oid, "matching_outcome_count": len(matches)}))
            continue
        for other_oid, orecs in outcomes.items():
            for outcome in orecs:
                refs = outcome.get("artifacts", [])
                if isinstance(refs, list) and aid in refs and other_oid != oid:
                    violations.append(Violation("INV-05", "Artifact is back-linked from a different Outcome", "Artifact", aid, {"canonical_outcome_id": oid, "conflicting_outcome_id": other_oid}))
    return violations

def check_inv_06(snapshot: dict[str, Any]) -> list[Violation]:
    immutable = {"Decision", "Outcome", "Evaluation", "Event", "Artifact"}
    allowed = {
        "Decision": {"status", "outcome_link"},
        "Execution": {"status", "outcome_id"},
        "Outcome": {"status_lifecycle", "evaluation_ids"},
        "Evaluation": {"status"},
        "Event": {"delivery"},
        "Artifact": {"status", "last_verified_at"},
    }
    violations: list[Violation] = []
    for mutation in _collection(snapshot, "mutations"):
        etype = mutation.get("entity_type")
        eid = mutation.get("entity_id") or "<unknown>"
        before = mutation.get("before")
        after = mutation.get("after")
        if not isinstance(before, dict) or not isinstance(after, dict):
            continue
        protected = etype in immutable or (etype == "Execution" and before.get("status") in TERMINAL_EXECUTION_STATUSES)
        if not protected:
            continue
        changed = {k for k in set(before) | set(after) if before.get(k) != after.get(k)}
        illegal = sorted(changed - allowed.get(str(etype), set()))
        if illegal:
            violations.append(Violation("INV-06", "Immutable record content changed after creation/finalization", str(etype), str(eid), {"illegal_changed_fields": illegal}))
    return violations

def _constraint_applies(constraint: dict[str, Any], decision: dict[str, Any]) -> bool:
    scope = constraint.get("scope")
    if scope == "Global":
        return True
    if scope == "Goal":
        return _entity_id(constraint, "goal_id") == _subject_goal_id(decision)
    if scope == "Task":
        return _entity_id(constraint, "task_id") == _subject_task_id(decision)
    return False

def check_inv_07(snapshot: dict[str, Any]) -> list[Violation]:
    hard = [c for c in _collection(snapshot, "constraints") if c.get("hardness") == "Hard" and c.get("status") not in {"Resolved", "Retired", "Relaxed"}]
    evals = _collection(snapshot, "constraint_evaluations")
    violations: list[Violation] = []
    for decision in _collection(snapshot, "decisions"):
        if decision.get("status") not in {"Committed", "Applied", "Evaluated"}:
            continue
        did = _entity_id(decision, "decision_id", "id") or "<unknown>"
        for constraint in hard:
            if not _constraint_applies(constraint, decision):
                continue
            cid = _entity_id(constraint, "constraint_id", "id") or "<unknown>"
            matches = [e for e in evals if _entity_id(e, "decision_id") == did and _entity_id(e, "constraint_id") == cid]
            if constraint.get("status") == "Violated" or any(e.get("result") in {"violated", "fail", "deny"} for e in matches):
                violations.append(Violation("INV-07", "Committed Decision violates a Hard Constraint", "Decision", did, {"constraint_id": cid}))
            elif evals and not matches:
                violations.append(Violation("INV-07", "Committed Decision lacks Hard Constraint evaluation evidence", "Decision", did, {"constraint_id": cid}))
    return violations

def _graph_violation(kind: str, gid: str, nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> Violation | None:
    cycle = _cycle_path(nodes, edges)
    return Violation("INV-08", f"{kind} must be acyclic", kind, gid, {"cycle": cycle}) if cycle else None

def check_inv_08(snapshot: dict[str, Any]) -> list[Violation]:
    violations: list[Violation] = []
    for graph in _collection(snapshot, "goal_graphs"):
        gid = _entity_id(graph, "graph_id", "id") or "<unknown>"
        nodes = []
        for node in graph.get("nodes", []):
            if isinstance(node, str):
                nodes.append(node)
            elif isinstance(node, dict):
                nid = _entity_id(node, "goal_id", "id")
                if nid:
                    nodes.append(nid)
        edges = [(e["from"], e["to"]) for e in graph.get("edges", []) if isinstance(e, dict) and isinstance(e.get("from"), str) and isinstance(e.get("to"), str)]
        v = _graph_violation("GoalGraph", gid, nodes, edges)
        if v:
            violations.append(v)
    for graph in _collection(snapshot, "task_graphs"):
        gid = _entity_id(graph, "graph_id", "id") or "<unknown>"
        nodes = [n for n in graph.get("nodes", []) if isinstance(n, str)]
        edges = [(e["from"], e["to"]) for e in graph.get("edges", []) if isinstance(e, dict) and isinstance(e.get("from"), str) and isinstance(e.get("to"), str)]
        v = _graph_violation("TaskGraph", gid, nodes, edges)
        if v:
            violations.append(v)
    for plan in _collection(snapshot, "plans"):
        pid = _entity_id(plan, "plan_id", "id") or "<unknown>"
        tasks = [t for t in plan.get("tasks", []) if isinstance(t, dict)]
        nodes = [tid for t in tasks if (tid := _entity_id(t, "task_id", "id"))]
        edges: list[tuple[str, str]] = []
        for task in tasks:
            tid = _entity_id(task, "task_id", "id")
            if tid:
                edges += [(dep, tid) for dep in task.get("depends_on", []) if isinstance(dep, str)]
        v = _graph_violation("PlanTaskGraph", pid, nodes, edges)
        if v:
            violations.append(v)
    for wf in _collection(snapshot, "workflows"):
        wid = _entity_id(wf, "workflow_id", "id") or "<unknown>"
        steps = [s for s in wf.get("steps", []) if isinstance(s, dict)]
        nodes = [sid for s in steps if (sid := _entity_id(s, "step_id", "id"))]
        edges: list[tuple[str, str]] = []
        for step in steps:
            src = _entity_id(step, "step_id", "id")
            if not src:
                continue
            for field in ("next", "on_true", "on_false", "branch_to", "compensation"):
                target = step.get(field)
                if isinstance(target, str) and target:
                    edges.append((src, target))
            if isinstance(step.get("branches"), list):
                edges += [(src, target) for target in step["branches"] if isinstance(target, str) and target]
        v = _graph_violation("Workflow", wid, nodes, edges)
        if v:
            violations.append(v)
    return violations

def check_inv_09(snapshot: dict[str, Any]) -> list[Violation]:
    markers: list[str] = []
    for resource in _collection(snapshot, "resources"):
        markers += [x for x in (_entity_id(resource, "id", "resource_id"), _entity_id(resource, "name")) if x]
    violations: list[Violation] = []
    for task in _collection(snapshot, "tasks"):
        tid = _entity_id(task, "id", "task_id") or "<unknown>"
        for field in ("objective", "expected_output", "constraints", "required_capabilities"):
            for text in _text_values(task.get(field)):
                marker = _contains_marker(text, markers)
                if marker:
                    violations.append(Violation("INV-09", "Task authoring fields must be Resource-agnostic", "Task", tid, {"field": field, "resource_marker": marker}))
                    break
    forbidden_keys = {"provided_by", "providers", "resource_id", "resource_ids", "resources", "preferred_resource", "preferred_resource_id"}
    for cap in _collection(snapshot, "capabilities"):
        cid = _entity_id(cap, "capability_id", "id") or "<unknown>"
        present = sorted(k for k in forbidden_keys if k in cap)
        if present:
            violations.append(Violation("INV-09", "Capability must not contain Resource relationship fields", "Capability", cid, {"fields": present}))
        for field in ("display_name", "description", "aliases"):
            for text in _text_values(cap.get(field)):
                marker = _contains_marker(text, markers)
                if marker:
                    violations.append(Violation("INV-09", "Capability definition must not name a Resource", "Capability", cid, {"field": field, "resource_marker": marker}))
                    break
    return violations

def check_inv_10(snapshot: dict[str, Any]) -> list[Violation]:
    risks = _index(_collection(snapshot, "risks"), "risk_id", "id")
    violations: list[Violation] = []
    for assumption in _collection(snapshot, "assumptions"):
        if assumption.get("status") != "Invalidated":
            continue
        aid = _entity_id(assumption, "assumption_id", "id") or "<unknown>"
        active = _active_plan_ids_for_assumption(snapshot, assumption)
        if not active:
            continue
        accepted = bool(assumption.get("accepted_by") and assumption.get("accepted_at") and assumption.get("on_invalidation") == "accept")
        rid = _entity_id(assumption, "linked_risk_id")
        risk = _single(risks, rid)
        if risk and risk.get("strategy") == "accept" and risk.get("status") == "Accepted" and risk.get("accepted_by") and risk.get("accepted_at"):
            accepted = True
        if not accepted:
            violations.append(Violation("INV-10", "Invalidated Assumption still supports an Active Plan without explicit accepted risk", "Assumption", aid, {"active_plan_ids": active, "linked_risk_id": rid}))
    return violations

def _policy_applies_to_decision(policy: dict[str, Any]) -> bool:
    applies = policy.get("applies_to", [])
    if not isinstance(applies, list):
        return False
    normalized = {str(x).casefold() for x in applies}
    return "decision" in normalized or "*" in normalized or "all" in normalized

def check_inv_11(snapshot: dict[str, Any]) -> list[Violation]:
    policies = [p for p in _collection(snapshot, "policies") if p.get("status") == "Active" and _policy_applies_to_decision(p) and (not isinstance(p.get("enforcement_points"), list) or "pre_decision" in p.get("enforcement_points", []))]
    evals = _collection(snapshot, "policy_evaluations")
    violations: list[Violation] = []
    for decision in _collection(snapshot, "decisions"):
        if decision.get("status") not in {"Committed", "Applied", "Evaluated"}:
            continue
        did = _entity_id(decision, "decision_id", "id") or "<unknown>"
        for policy in policies:
            pid = _entity_id(policy, "policy_id", "id") or "<unknown>"
            matches = [e for e in evals if _entity_id(e, "decision_id") == did and _entity_id(e, "policy_id") == pid]
            if evals and not matches:
                violations.append(Violation("INV-11", "Committed Decision lacks applicable Policy evaluation evidence", "Decision", did, {"policy_id": pid}))
                continue
            for ev in matches:
                result = ev.get("result")
                if result == "deny":
                    violations.append(Violation("INV-11", "Committed Decision was denied by Policy", "Decision", did, {"policy_id": pid}))
                if result == "require_approval" and ev.get("approved") is not True and not ev.get("exception_id"):
                    violations.append(Violation("INV-11", "Committed Decision requires Policy approval that is not recorded", "Decision", did, {"policy_id": pid}))
    return violations

def check_inv_12(snapshot: dict[str, Any]) -> list[Violation]:
    transitions = _collection(snapshot, "state_transitions")
    events = _collection(snapshot, "events")
    violations: list[Violation] = []
    for transition in transitions:
        etype = str(transition.get("entity_type") or "")
        eid = str(transition.get("entity_id") or "")
        old = transition.get("previous_state")
        new = transition.get("new_state")
        matches = []
        for event in events:
            subject = event.get("subject") if isinstance(event.get("subject"), dict) else {}
            if subject.get("entity_type") == etype and subject.get("entity_id") == eid and event.get("previous_state") == old and event.get("new_state") == new:
                matches.append(event)
        if len(matches) != 1:
            violations.append(Violation("INV-12", "State transition must emit exactly one matching Event", etype or "Entity", eid or "<unknown>", {"previous_state": old, "new_state": new, "matching_event_count": len(matches)}))
    return violations

def check_inv_13(snapshot: dict[str, Any]) -> list[Violation]:
    decisions = _index(_collection(snapshot, "decisions"), "decision_id", "id")
    outcomes = _index(_collection(snapshot, "outcomes"), "outcome_id", "id")
    evals_by_out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for evaluation in _collection(snapshot, "evaluations"):
        oid = _entity_id(evaluation, "outcome_id")
        if oid:
            evals_by_out[oid].append(evaluation)
    violations: list[Violation] = []
    def parse(kind: str, eid: str, rec: dict[str, Any], field: str):
        value, error = _parse_time(rec.get(field), field=field, owner=f"{kind}:{eid}")
        if error:
            violations.append(Violation("INV-13", error, kind, eid))
        return value
    for exe in _collection(snapshot, "executions"):
        eid = _entity_id(exe, "execution_id", "id") or "<unknown>"
        created = parse("Execution", eid, exe, "created_at")
        started = parse("Execution", eid, exe, "started_at")
        finished = parse("Execution", eid, exe, "finished_at")
        if created and started and created > started:
            violations.append(Violation("INV-13", "Execution.created_at must be <= started_at", "Execution", eid))
        if started and finished and started > finished:
            violations.append(Violation("INV-13", "Execution.started_at must be <= finished_at", "Execution", eid))
        did = _entity_id(exe, "decision_id")
        dec = _single(decisions, did)
        if dec and started:
            decided = parse("Decision", did or "<unknown>", dec, "decided_at")
            if decided and decided > started:
                violations.append(Violation("INV-13", "Decision.decided_at must be <= Execution.started_at", "Execution", eid))
        oid = _entity_id(exe, "outcome_id")
        out = _single(outcomes, oid)
        if out:
            measured = parse("Outcome", oid or "<unknown>", out, "measured_at")
            if finished and measured and finished > measured:
                violations.append(Violation("INV-13", "Execution.finished_at must be <= Outcome.measured_at", "Execution", eid))
            for ev in evals_by_out.get(oid or "", []):
                evid = _entity_id(ev, "evaluation_id", "id") or "<unknown>"
                evaluated = parse("Evaluation", evid, ev, "evaluated_at")
                if measured and evaluated and measured > evaluated:
                    violations.append(Violation("INV-13", "Outcome.measured_at must be <= Evaluation.evaluated_at", "Evaluation", evid))
    return violations

def check_inv_14(snapshot: dict[str, Any]) -> list[Violation]:
    active: dict[str, list[str]] = defaultdict(list)
    for plan in _collection(snapshot, "plans"):
        if plan.get("status") != "Active":
            continue
        pid = _entity_id(plan, "plan_id", "id") or "<unknown>"
        if isinstance(plan.get("source_goal_ids"), list):
            for gid in plan["source_goal_ids"]:
                if isinstance(gid, str) and gid:
                    active[gid].append(pid)
    return [Violation("INV-14", "Goal has more than one Active Plan", "Goal", gid, {"active_plan_ids": pids}) for gid, pids in sorted(active.items()) if len(pids) > 1]

def check_inv_15(snapshot: dict[str, Any]) -> list[Violation]:
    profiles = _index(_collection(snapshot, "resource_profiles"), "resource_id")
    violations: list[Violation] = []
    for resource in _collection(snapshot, "resources"):
        if resource.get("lifecycle") != "Active":
            continue
        rid = _entity_id(resource, "id", "resource_id") or "<unknown>"
        matches = profiles.get(rid, [])
        if len(matches) != 1:
            violations.append(Violation("INV-15", "Active Resource must have exactly one Resource Profile", "Resource", rid, {"profile_count": len(matches)}))
    return violations

def check_inv_16(snapshot: dict[str, Any]) -> list[Violation]:
    indexes = {
        "goal_ids": (_index(_collection(snapshot, "goals"), "goal_id", "id"), "Goal"),
        "artifact_ids": (_index(_collection(snapshot, "artifacts"), "artifact_id", "id"), "Artifact"),
        "memory_ids": (_index(_collection(snapshot, "memories"), "memory_id", "id"), "Memory"),
        "decision_ids": (_index(_collection(snapshot, "decisions"), "decision_id", "id"), "Decision"),
        "execution_ids": (_index(_collection(snapshot, "executions"), "execution_id", "id"), "Execution"),
    }
    violations: list[Violation] = []
    for session in _collection(snapshot, "sessions"):
        if session.get("status") not in TERMINAL_SESSION_STATUSES:
            continue
        sid = _entity_id(session, "session_id", "id") or "<unknown>"
        for field, (idx, kind) in indexes.items():
            refs = session.get(field, [])
            if not isinstance(refs, list):
                continue
            for ref in refs:
                if isinstance(ref, str) and len(idx.get(ref, [])) != 1:
                    violations.append(Violation("INV-16", "Terminal Session reference must not disappear with Session end", "Session", sid, {"reference_field": field, "missing_entity_type": kind, "entity_id": ref}))
    for deletion in _collection(snapshot, "deletions"):
        reason = str(deletion.get("reason") or deletion.get("cause") or "").casefold()
        if "session" in reason and any(token in reason for token in ("end", "close", "expire", "abort", "cascade")):
            etype = str(deletion.get("entity_type") or "")
            if etype in {"Goal", "Memory", "Knowledge", "Artifact", "Outcome", "Decision", "Execution"}:
                violations.append(Violation("INV-16", "Persistent Entity was deleted as a consequence of Session termination", etype, str(deletion.get("entity_id") or "<unknown>"), {"reason": deletion.get("reason") or deletion.get("cause")}))
    return violations

CHECKS: dict[str, Callable[[dict[str, Any]], list[Violation]]] = {
    f"INV-{i:02d}": fn for i, fn in enumerate([
        check_inv_01, check_inv_02, check_inv_03, check_inv_04,
        check_inv_05, check_inv_06, check_inv_07, check_inv_08,
        check_inv_09, check_inv_10, check_inv_11, check_inv_12,
        check_inv_13, check_inv_14, check_inv_15, check_inv_16,
    ], start=1)
}

def validate_snapshot(snapshot: dict[str, Any], selected: Iterable[str] | None = None) -> list[Violation]:
    if not isinstance(snapshot, dict):
        raise SnapshotError("snapshot root must be a JSON object")
    selected_ids = tuple(selected or IMPLEMENTED_INVARIANTS)
    unknown = [x for x in selected_ids if x not in CHECKS]
    if unknown:
        raise SnapshotError(f"unknown/unimplemented invariant(s): {', '.join(unknown)}")
    violations: list[Violation] = []
    for inv in selected_ids:
        violations.extend(CHECKS[inv](snapshot))
    return violations

def _load_snapshot(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
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
    selected = tuple(x.strip().upper() for x in raw.split(",") if x.strip())
    unknown = [x for x in selected if x not in CHECKS]
    if unknown:
        raise SnapshotError(f"unknown/unimplemented invariant(s): {', '.join(unknown)}")
    return selected

def _print_text(path: Path, violations: list[Violation], selected: tuple[str, ...]) -> None:
    if not violations:
        print(f"PASS {path}: {len(selected)} invariant(s) checked")
        return
    print(f"FAIL {path}: {len(violations)} violation(s)")
    for violation in violations:
        owner = f" [{violation.entity_type or '?'}:{violation.entity_id or '?'}]" if violation.entity_type or violation.entity_id else ""
        print(f"  {violation.invariant}{owner} {violation.message}")
        if violation.details:
            print(f"    details={json.dumps(violation.details, ensure_ascii=False, sort_keys=True)}")

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshots", nargs="+", help="JSON state snapshot(s) to validate")
    parser.add_argument("--only", help="comma-separated invariant ids")
    parser.add_argument("--format", choices=("text", "json"), default="text", dest="output_format")
    args = parser.parse_args(argv)
    try:
        selected = _parse_only(args.only)
        results = []
        failed = False
        for raw in args.snapshots:
            path = Path(raw)
            violations = validate_snapshot(_load_snapshot(path), selected)
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
