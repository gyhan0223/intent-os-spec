#!/usr/bin/env python3
"""Validate System Routing Benchmark v0.1 assets."""

from __future__ import annotations

# tools/validate-all.py 가 읽는 CI 선언.
CI_LABEL = "System Routing Benchmark 검증"

import json
import sys
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SUITE_PATH = ROOT / "benchmarks" / "cases" / "system-routing-v0.1.json"
SCHEMA_PATH = ROOT / "benchmarks" / "schemas" / "system-benchmark-run.schema.json"
EXAMPLES_DIR = ROOT / "benchmarks" / "examples"

EXPECTED_CATEGORIES = {
    "writing",
    "research",
    "planning",
    "structured",
    "coding",
    "tool_choice",
}
VALID_SPLITS = {"development", "holdout"}
VALID_TOOL_REQUIREMENTS = {"none", "optional", "recommended", "required"}


def fail(message: str) -> None:
    raise AssertionError(message)


def validate_suite() -> None:
    suite = json.loads(SUITE_PATH.read_text(encoding="utf-8"))
    cases = suite["cases"]

    if suite["benchmark_id"] != "system-routing-v0.1":
        fail("Unexpected benchmark_id.")
    if len(cases) != 30:
        fail(f"Expected 30 cases, got {len(cases)}.")

    ids = [case["id"] for case in cases]
    if len(ids) != len(set(ids)):
        fail("Case IDs must be unique.")

    split_counts = Counter(case["split"] for case in cases)
    if split_counts != Counter({"development": 20, "holdout": 10}):
        fail(f"Expected development=20 and holdout=10, got {dict(split_counts)}.")

    category_counts = Counter(case["category"] for case in cases)
    if set(category_counts) != EXPECTED_CATEGORIES:
        fail(f"Unexpected categories: {dict(category_counts)}.")
    if any(count != 5 for count in category_counts.values()):
        fail(f"Each category must have 5 cases, got {dict(category_counts)}.")

    for case in cases:
        if case["split"] not in VALID_SPLITS:
            fail(f"{case['id']}: invalid split.")
        if case["tool_requirement"] not in VALID_TOOL_REQUIREMENTS:
            fail(f"{case['id']}: invalid tool_requirement.")
        if not case.get("required_capabilities"):
            fail(f"{case['id']}: required_capabilities must not be empty.")

        rubric = case.get("quality_rubric", {})
        if not rubric:
            fail(f"{case['id']}: quality_rubric is required.")
        if abs(sum(rubric.values()) - 100) > 1e-9:
            fail(f"{case['id']}: rubric weights must sum to 100.")

        if case.get("freshness_required") and case["tool_requirement"] == "none":
            fail(f"{case['id']}: freshness task cannot forbid tools.")

    if suite.get("development_case_count") != 20:
        fail("development_case_count metadata must be 20.")
    if suite.get("holdout_case_count") != 10:
        fail("holdout_case_count metadata must be 10.")


def validate_schema_and_examples() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    if not EXAMPLES_DIR.exists():
        fail("benchmarks/examples directory is missing.")

    examples = sorted(EXAMPLES_DIR.glob("*.json"))
    if not examples:
        fail("At least one benchmark run example is required.")

    for path in examples:
        data = json.loads(path.read_text(encoding="utf-8"))
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        if errors:
            rendered = "; ".join(
                f"{'/'.join(map(str, error.path)) or '<root>'}: {error.message}"
                for error in errors[:10]
            )
            fail(f"{path.relative_to(ROOT)} failed schema validation: {rendered}")


def main() -> int:
    validate_suite()
    validate_schema_and_examples()
    print("System Routing Benchmark v0.1 validation passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Benchmark validation failed: {exc}", file=sys.stderr)
        raise
