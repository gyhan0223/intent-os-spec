#!/usr/bin/env python3
"""Validate End-to-End Golden Fixtures against canonical JSON Schemas.

This validator intentionally checks fixture shape, per-record schema validity,
and a small set of intra-fixture references. It is NOT the global invariant
validator described by entities/e000a-entity-relationships.md.
"""

from __future__ import annotations

# tools/validate-all.py 가 읽는 CI 선언.
CI_LABEL = "End-to-End Golden Fixture 검증"

import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_FILE = ROOT / "fixtures" / "e2e" / "golden-fixtures-v0.1.json"
SCHEMA_DIR = ROOT / "intent-os-spec" / "schemas"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)


def record_id(schema_name: str, data: dict) -> str | None:
    candidates = {
        "goal.schema.json": "goal_id",
        "context.schema.json": "context_id",
        "constraint.schema.json": "constraint_id",
        "intent.schema.json": "intent_id",
        "plan.schema.json": "plan_id",
        "task.schema.json": "id",
        "task-graph.schema.json": "graph_id",
        "decision.schema.json": "decision_id",
        "execution.schema.json": "execution_id",
        "outcome.schema.json": "outcome_id",
        "evaluation.schema.json": "evaluation_id",
        "memory.schema.json": "memory_id",
        "resource-profile.schema.json": "profile_id",
    }
    key = candidates.get(schema_name)
    return data.get(key) if key else None


def validate_refs(scenario: dict) -> list[str]:
    errors: list[str] = []
    records = scenario["records"]
    ids: dict[str, set[str]] = {}
    typed: list[tuple[str, dict]] = []

    for record in records:
        schema_name = record["schema"]
        data = record["data"]
        rid = record_id(schema_name, data)
        if rid:
            ids.setdefault(schema_name, set()).add(rid)
        typed.append((schema_name, data))

    def has(schema: str, value: str | None) -> bool:
        return value is not None and value in ids.get(schema, set())

    for schema_name, data in typed:
        if schema_name == "intent.schema.json" and not has("goal.schema.json", data.get("goal_id")):
            errors.append(f"Intent {data.get('intent_id')} references missing Goal {data.get('goal_id')}")

        elif schema_name == "task.schema.json":
            goal_id = data.get("goal_id")
            if goal_id and not has("goal.schema.json", goal_id):
                errors.append(f"Task {data.get('id')} references missing Goal {goal_id}")

        elif schema_name == "task-graph.schema.json":
            task_ids = ids.get("task.schema.json", set())
            for node in data.get("nodes", []):
                if node not in task_ids:
                    errors.append(f"Task Graph {data.get('graph_id')} references missing Task {node}")
            for edge in data.get("edges", []):
                for endpoint in (edge.get("from"), edge.get("to")):
                    if endpoint not in task_ids:
                        errors.append(f"Task Graph {data.get('graph_id')} edge references missing Task {endpoint}")

        elif schema_name == "decision.schema.json":
            subject = data.get("subject", {})
            goal_id = subject.get("goal_id")
            task_id = subject.get("task_id")
            if goal_id and not has("goal.schema.json", goal_id):
                errors.append(f"Decision {data.get('decision_id')} references missing Goal {goal_id}")
            if task_id and not has("task.schema.json", task_id):
                errors.append(f"Decision {data.get('decision_id')} references missing Task {task_id}")

        elif schema_name == "execution.schema.json":
            if not has("task.schema.json", data.get("task_id")):
                errors.append(f"Execution {data.get('execution_id')} references missing Task {data.get('task_id')}")
            if not has("decision.schema.json", data.get("decision_id")):
                errors.append(f"Execution {data.get('execution_id')} references missing Decision {data.get('decision_id')}")

        elif schema_name == "outcome.schema.json":
            if not has("execution.schema.json", data.get("execution_id")):
                errors.append(f"Outcome {data.get('outcome_id')} references missing Execution {data.get('execution_id')}")

        elif schema_name == "evaluation.schema.json":
            if not has("outcome.schema.json", data.get("outcome_id")):
                errors.append(f"Evaluation {data.get('evaluation_id')} references missing Outcome {data.get('outcome_id')}")

        elif schema_name == "memory.schema.json":
            if data.get("goal_ref") and not has("goal.schema.json", data.get("goal_ref")):
                errors.append(f"Memory {data.get('memory_id')} references missing Goal {data.get('goal_ref')}")
            if data.get("decision_ref") and not has("decision.schema.json", data.get("decision_ref")):
                errors.append(f"Memory {data.get('memory_id')} references missing Decision {data.get('decision_ref')}")
            if data.get("source") and not has("execution.schema.json", data.get("source")):
                errors.append(f"Memory {data.get('memory_id')} references missing Execution {data.get('source')}")

    return errors


def main() -> int:
    payload = json.loads(FIXTURE_FILE.read_text(encoding="utf-8"))
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) != 10:
        fail("golden-fixtures-v0.1.json must contain exactly 10 scenarios for fixture_version 0.1.0")
        return 1

    seen: set[str] = set()
    all_errors: list[str] = []
    checker = FormatChecker()

    for scenario in scenarios:
        sid = scenario.get("scenario_id")
        if not sid or sid in seen:
            all_errors.append(f"invalid or duplicate scenario_id: {sid!r}")
            continue
        seen.add(sid)

        if not scenario.get("process_trace"):
            all_errors.append(f"{sid}: process_trace must not be empty")
        records = scenario.get("records")
        if not isinstance(records, list) or not records:
            all_errors.append(f"{sid}: records must be a non-empty list")
            continue

        for index, record in enumerate(records):
            schema_name = record.get("schema")
            data = record.get("data")
            if not isinstance(schema_name, str) or not isinstance(data, dict):
                all_errors.append(f"{sid}: record[{index}] must contain schema:string and data:object")
                continue

            schema_path = SCHEMA_DIR / schema_name
            if not schema_path.exists():
                all_errors.append(f"{sid}: missing schema {schema_name}")
                continue

            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            validator = Draft202012Validator(schema, format_checker=checker)
            for error in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
                path = ".".join(str(p) for p in error.path) or "<root>"
                all_errors.append(f"{sid}: {schema_name} {path}: {error.message}")

        all_errors.extend(f"{sid}: {message}" for message in validate_refs(scenario))

    if all_errors:
        for error in all_errors:
            fail(error)
        print(f"FAILED: {len(all_errors)} error(s)")
        return 1

    print(f"OK: validated {len(scenarios)} End-to-End Golden Fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
