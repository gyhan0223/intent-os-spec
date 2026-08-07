#!/usr/bin/env python3
"""Canonical Data Model v1 conformance validator.

This validator complements validate-format.py and validate-examples.py.
It checks two layers that JSON Schema alone cannot express:

1. The six normalized schemas preserve the canonical ownership annotations.
2. Golden fixtures obey cross-entity source-of-truth and provenance rules.

Usage:
    python3 tools/validate-canonical.py

Dependencies:
    jsonschema, referencing
"""

from __future__ import annotations

import glob
import json
import os
import sys
from collections import defaultdict, deque

from jsonschema import Draft202012Validator
from referencing import Registry, Resource as RefResource
from referencing.jsonschema import DRAFT202012

SCHEMA_DIR = "intent-os-spec/schemas"
FIXTURE_GLOB = "fixtures/canonical/*.json"

COLLECTION_SCHEMAS = {
    "goals": "goal.schema.json",
    "goal_graphs": "goal-graph.schema.json",
    "plans": "plan.schema.json",
    "tasks": "task.schema.json",
    "task_graphs": "task-graph.schema.json",
    "resources": "resource.schema.json",
    "resource_profiles": "resource-profile.schema.json",
    "decisions": "decision.schema.json",
    "executions": "execution.schema.json",
    "outcomes": "outcome.schema.json",
    "artifacts": "artifact.schema.json",
    "evaluations": "evaluation.schema.json",
}

ID_FIELDS = {
    "goals": "goal_id",
    "goal_graphs": "graph_id",
    "plans": "plan_id",
    "tasks": "id",
    "task_graphs": "graph_id",
    "resources": "id",
    "resource_profiles": "profile_id",
    "decisions": "decision_id",
    "executions": "execution_id",
    "outcomes": "outcome_id",
    "artifacts": "artifact_id",
    "evaluations": "evaluation_id",
}

# Schema JSON pointer -> expected ownership annotation.
OWNERSHIP_RULES = {
    "goal.schema.json": {
        "/properties/constraints": "SNAPSHOT",
        "/properties/context": "SNAPSHOT",
        "/properties/parent_goal": "DERIVED",
        "/properties/child_goals": "DERIVED",
        "/properties/dependencies": "DERIVED",
        "/properties/related_goals": "DERIVED",
        "/properties/status/properties/progress": "DERIVED",
        "/properties/priority/properties/computed_score": "DERIVED",
        "/properties/quality/properties/completeness": "DERIVED",
    },
    "goal-graph.schema.json": {
        "/properties/nodes": "REFERENCE",
        "/properties/edges": "AUTHORITATIVE",
    },
    "task.schema.json": {
        "/properties/goal_id": "REFERENCE",
        "/properties/dependencies": "DERIVED",
        "/properties/constraints": "DERIVED",
        "/properties/assigned_resource_id": "DERIVED",
        "/properties/attempts": "DERIVED",
    },
    "task-graph.schema.json": {
        "/properties/nodes": "REFERENCE",
        "/properties/edges": "AUTHORITATIVE",
        "/properties/entry_tasks": "DERIVED",
        "/properties/analysis": "DERIVED",
        "/properties/diff": "DERIVED",
    },
    "resource.schema.json": {
        "/properties/performance": "DERIVED",
        "/properties/capabilities/items/properties/observed_score": "DERIVED",
        "/properties/capabilities/items/properties/confidence": "DERIVED",
    },
    "resource-profile.schema.json": {
        "/properties/resource_id": "REFERENCE",
        "/properties/capability_scores": "AUTHORITATIVE",
        "/properties/performance": "AUTHORITATIVE",
        "/properties/availability": "AUTHORITATIVE",
        "/properties/drift": "AUTHORITATIVE",
    },
}

# Canonical write fixtures must not send fields that are snapshots/projections.
FORBIDDEN_CANONICAL_WRITES = {
    "goals": {
        "constraints",
        "context",
        "parent_goal",
        "child_goals",
        "dependencies",
        "related_goals",
    },
    "tasks": {"dependencies", "constraints", "assigned_resource_id", "attempts"},
    "task_graphs": {"entry_tasks", "analysis", "diff"},
    "resources": {"performance"},
}

TERMINAL_EXECUTION_STATES = {"Completed", "Failed", "TimedOut", "Aborted"}


def load_registry_and_schemas():
    resources = []
    schemas = {}
    for path in glob.glob(f"{SCHEMA_DIR}/*.json"):
        doc = json.load(open(path, encoding="utf-8"))
        name = os.path.basename(path)
        schemas[name] = doc
        ref = RefResource(contents=doc, specification=DRAFT202012)
        if doc.get("$id"):
            resources.append((doc["$id"], ref))
        resources.append((name, ref))
    return Registry().with_resources(resources), schemas


def pointer_get(doc, pointer):
    cur = doc
    for token in pointer.strip("/").split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if token not in cur:
            return None
        cur = cur[token]
    return cur


def validate_ownership_annotations(schemas, report):
    failed = 0
    for schema_name, rules in OWNERSHIP_RULES.items():
        schema = schemas.get(schema_name)
        if schema is None:
            report(f"FAIL canonical ownership: missing schema {schema_name}")
            failed += 1
            continue
        for pointer, expected in rules.items():
            node = pointer_get(schema, pointer)
            if node is None:
                report(f"FAIL {schema_name}: missing canonical field {pointer}")
                failed += 1
                continue
            actual = node.get("x-ownership")
            if actual != expected:
                report(
                    f"FAIL {schema_name}{pointer}: x-ownership={actual!r}, expected {expected!r}"
                )
                failed += 1
            if expected == "DERIVED" and node.get("readOnly") is not True:
                report(f"FAIL {schema_name}{pointer}: DERIVED field must be readOnly")
                failed += 1
    return failed


def extract_goal_node_id(node):
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        return node.get("goal_id")
    return None


def is_dag(nodes, edges):
    adjacency = defaultdict(list)
    indegree = {node: 0 for node in nodes}
    for edge in edges:
        src, dst = edge.get("from"), edge.get("to")
        if src not in indegree or dst not in indegree:
            return False
        adjacency[src].append(dst)
        indegree[dst] += 1
    queue = deque(n for n, d in indegree.items() if d == 0)
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for nxt in adjacency[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return visited == len(nodes)


def index_entities(entities, report, fixture_id):
    indexes = {}
    failures = 0
    for collection, id_field in ID_FIELDS.items():
        items = entities.get(collection, [])
        seen = {}
        for item in items:
            value = item.get(id_field)
            if not value:
                report(f"FAIL {fixture_id}: {collection} item missing {id_field}")
                failures += 1
                continue
            if value in seen:
                report(f"FAIL {fixture_id}: duplicate {collection} id {value}")
                failures += 1
            seen[value] = item
        indexes[collection] = seen
    return indexes, failures


def validate_schema_instances(entities, schemas, registry, report, fixture_id):
    failures = 0
    for collection, schema_name in COLLECTION_SCHEMAS.items():
        schema = schemas[schema_name]
        validator = Draft202012Validator(schema, registry=registry)
        for item in entities.get(collection, []):
            errors = sorted(validator.iter_errors(item), key=lambda e: list(e.path))
            if errors:
                failures += 1
                report(f"FAIL {fixture_id}: {collection} -> {schema_name}")
                for err in errors[:5]:
                    report(f"       {list(err.path)}: {err.message[:180]}")
    return failures


def validate_canonical_writes(entities, report, fixture_id):
    failures = 0
    for collection, forbidden in FORBIDDEN_CANONICAL_WRITES.items():
        for item in entities.get(collection, []):
            present = sorted(forbidden & set(item))
            if present:
                report(
                    f"FAIL {fixture_id}: canonical write to {collection} contains derived/snapshot fields {present}"
                )
                failures += 1

    for resource in entities.get("resources", []):
        for capability in resource.get("capabilities", []):
            legacy = sorted({"observed_score", "confidence"} & set(capability))
            if legacy:
                report(
                    f"FAIL {fixture_id}: Resource capability writes observed fields {legacy}; use ResourceProfile"
                )
                failures += 1
    return failures


def validate_references(entities, indexes, report, fixture_id):
    failures = 0
    goals = indexes["goals"]
    plans = indexes["plans"]
    tasks = indexes["tasks"]
    resources = indexes["resources"]
    profiles = indexes["resource_profiles"]
    decisions = indexes["decisions"]
    executions = indexes["executions"]
    outcomes = indexes["outcomes"]

    for task in entities.get("tasks", []):
        if task.get("goal_id") not in goals:
            report(f"FAIL {fixture_id}: Task {task.get('id')} references missing Goal {task.get('goal_id')}")
            failures += 1

    for graph in entities.get("goal_graphs", []):
        node_ids = [extract_goal_node_id(n) for n in graph.get("nodes", [])]
        if any(not isinstance(n, str) for n in graph.get("nodes", [])):
            report(f"FAIL {fixture_id}: GoalGraph {graph.get('graph_id')} canonical nodes must be goal_id strings")
            failures += 1
        if any(n not in goals for n in node_ids):
            report(f"FAIL {fixture_id}: GoalGraph {graph.get('graph_id')} contains missing Goal reference")
            failures += 1
        if graph.get("root_goal_id") and graph["root_goal_id"] not in node_ids:
            report(f"FAIL {fixture_id}: GoalGraph root_goal_id is not in nodes")
            failures += 1
        if not is_dag(node_ids, graph.get("edges", [])):
            report(f"FAIL {fixture_id}: GoalGraph {graph.get('graph_id')} is cyclic or has dangling edge")
            failures += 1

    for plan in entities.get("plans", []):
        for goal_id in plan.get("source_goal_ids", []):
            if goal_id not in goals:
                report(f"FAIL {fixture_id}: Plan {plan.get('plan_id')} references missing Goal {goal_id}")
                failures += 1
        for task_snapshot in plan.get("tasks", []):
            if task_snapshot.get("task_id") not in tasks:
                report(f"FAIL {fixture_id}: Plan {plan.get('plan_id')} snapshot references missing Task {task_snapshot.get('task_id')}")
                failures += 1

    for graph in entities.get("task_graphs", []):
        node_ids = graph.get("nodes", [])
        if graph.get("plan_id") not in plans:
            report(f"FAIL {fixture_id}: TaskGraph {graph.get('graph_id')} references missing Plan {graph.get('plan_id')}")
            failures += 1
        if any(node not in tasks for node in node_ids):
            report(f"FAIL {fixture_id}: TaskGraph {graph.get('graph_id')} contains missing Task reference")
            failures += 1
        if not is_dag(node_ids, graph.get("edges", [])):
            report(f"FAIL {fixture_id}: TaskGraph {graph.get('graph_id')} is cyclic or has dangling edge")
            failures += 1

    profile_by_resource = {}
    for profile in entities.get("resource_profiles", []):
        resource_id = profile.get("resource_id")
        if resource_id not in resources:
            report(f"FAIL {fixture_id}: ResourceProfile {profile.get('profile_id')} references missing Resource {resource_id}")
            failures += 1
        if resource_id in profile_by_resource:
            report(f"FAIL {fixture_id}: more than one current ResourceProfile for Resource {resource_id}")
            failures += 1
        profile_by_resource[resource_id] = profile

    for decision in entities.get("decisions", []):
        subject = decision.get("subject", {})
        if subject.get("goal_id") and subject["goal_id"] not in goals:
            report(f"FAIL {fixture_id}: Decision {decision.get('decision_id')} references missing Goal")
            failures += 1
        if subject.get("plan_id") and subject["plan_id"] not in plans:
            report(f"FAIL {fixture_id}: Decision {decision.get('decision_id')} references missing Plan")
            failures += 1
        if subject.get("task_id") and subject["task_id"] not in tasks:
            report(f"FAIL {fixture_id}: Decision {decision.get('decision_id')} references missing Task")
            failures += 1

        selection = decision.get("selection")
        candidates = [a.get("candidate") for a in decision.get("alternatives_considered", [])]
        if not decision.get("forced_action") and isinstance(selection, str) and candidates and selection not in candidates:
            report(f"FAIL {fixture_id}: Decision {decision.get('decision_id')} selection is not among alternatives")
            failures += 1
        if decision.get("decision_type") == "ResourceSelection" and isinstance(selection, str) and selection not in resources:
            report(f"FAIL {fixture_id}: ResourceSelection chose missing Resource {selection}")
            failures += 1

        snapshot_version = decision.get("inputs_snapshot", {}).get("resource_profile_version")
        if snapshot_version and snapshot_version not in {p.get("snapshot_version") for p in profiles.values()}:
            report(f"FAIL {fixture_id}: Decision references unknown resource_profile_version {snapshot_version}")
            failures += 1

    for execution in entities.get("executions", []):
        if execution.get("task_id") not in tasks:
            report(f"FAIL {fixture_id}: Execution {execution.get('execution_id')} references missing Task")
            failures += 1
        if execution.get("decision_id") not in decisions:
            report(f"FAIL {fixture_id}: Execution {execution.get('execution_id')} references missing Decision")
            failures += 1
        if execution.get("resource_id") not in resources:
            report(f"FAIL {fixture_id}: Execution {execution.get('execution_id')} references missing Resource")
            failures += 1

    outcomes_by_execution = defaultdict(list)
    for outcome in entities.get("outcomes", []):
        execution_id = outcome.get("execution_id")
        if execution_id not in executions:
            report(f"FAIL {fixture_id}: Outcome {outcome.get('outcome_id')} references missing Execution")
            failures += 1
        outcomes_by_execution[execution_id].append(outcome)

    for execution in entities.get("executions", []):
        if execution.get("status") in TERMINAL_EXECUTION_STATES:
            count = len(outcomes_by_execution.get(execution.get("execution_id"), []))
            if count != 1:
                report(f"FAIL {fixture_id}: terminal Execution {execution.get('execution_id')} has {count} Outcomes, expected 1")
                failures += 1

    for artifact in entities.get("artifacts", []):
        if artifact.get("outcome_id") not in outcomes:
            report(f"FAIL {fixture_id}: Artifact {artifact.get('artifact_id')} references missing Outcome")
            failures += 1

    for evaluation in entities.get("evaluations", []):
        if evaluation.get("outcome_id") not in outcomes:
            report(f"FAIL {fixture_id}: Evaluation {evaluation.get('evaluation_id')} references missing Outcome")
            failures += 1

    return failures


def load_fixture_documents():
    for path in sorted(glob.glob(FIXTURE_GLOB)):
        doc = json.load(open(path, encoding="utf-8"))
        if isinstance(doc, dict) and "fixtures" in doc:
            for fixture in doc["fixtures"]:
                yield path, fixture
        else:
            yield path, doc


def main():
    registry, schemas = load_registry_and_schemas()
    lines = []
    report = lines.append
    failures = validate_ownership_annotations(schemas, report)

    fixture_count = 0
    for path, fixture in load_fixture_documents():
        fixture_count += 1
        fixture_id = fixture.get("fixture_id") or f"{path}#{fixture_count}"
        entities = fixture.get("entities", {})
        indexes, index_failures = index_entities(entities, report, fixture_id)
        failures += index_failures
        failures += validate_schema_instances(entities, schemas, registry, report, fixture_id)
        failures += validate_canonical_writes(entities, report, fixture_id)
        failures += validate_references(entities, indexes, report, fixture_id)

    if fixture_count < 10:
        report(f"FAIL golden fixtures: found {fixture_count}, expected at least 10")
        failures += 1

    for line in lines:
        print(line)

    print(f"\nCanonical ownership rules: {sum(len(v) for v in OWNERSHIP_RULES.values())} checks")
    print(f"Golden fixtures: {fixture_count}")
    print(f"Result: {'PASS' if failures == 0 else f'FAIL ({failures})'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
