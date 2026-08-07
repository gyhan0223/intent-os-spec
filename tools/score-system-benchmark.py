#!/usr/bin/env python3
"""Score Intent OS System Routing Benchmark v0.1.

Usage:
    python tools/score-system-benchmark.py path/to/run.json
    python tools/score-system-benchmark.py path/to/run.json --json
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

ARMS = ("manual", "fixed", "intent_os")
FAILURE_STATUSES = {
    "timeout",
    "provider_error",
    "tool_error",
    "policy_block",
    "invalid_output",
    "budget_exceeded",
    "user_abandoned",
}


def mean(values: Iterable[float]) -> float | None:
    xs = list(values)
    return statistics.fmean(xs) if xs else None


def median(values: Iterable[float]) -> float | None:
    xs = list(values)
    return statistics.median(xs) if xs else None


def percentile(values: Iterable[float], q: float) -> float | None:
    xs = sorted(values)
    if not xs:
        return None
    if len(xs) == 1:
        return float(xs[0])
    pos = (len(xs) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return float(xs[lo])
    weight = pos - lo
    return float(xs[lo] * (1 - weight) + xs[hi] * weight)


def safe_ratio(num: float | None, den: float | None) -> float | None:
    if num is None or den is None or den == 0:
        return None
    return num / den


def effective_quality(trial: dict[str, Any]) -> float:
    score = trial.get("quality_score")
    if score is not None:
        return float(score)
    if trial.get("status") in FAILURE_STATUSES:
        return 0.0
    raise ValueError(
        f"Trial {trial.get('trial_id')} is completed but has no quality_score."
    )


def fmt(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{digits}f}"


def fmt_pct(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.{digits}f}%"


def aggregate(trials: list[dict[str, Any]]) -> dict[str, Any]:
    quality = [effective_quality(t) for t in trials]
    selection = [float(t["selection_time_ms"]) for t in trials]
    latency = [float(t["execution_latency_ms"]) for t in trials]
    rework = [float(t["rework_count"]) for t in trials]
    satisfaction = [
        float(t["satisfaction_1_7"])
        for t in trials
        if t.get("satisfaction_1_7") is not None
    ]
    costs = [float(t["total_cost_usd"]) for t in trials]
    accepted = [bool(t["accepted"]) for t in trials]
    first_pass = [bool(t["accepted"]) and int(t["rework_count"]) == 0 for t in trials]

    total_cost = sum(costs)
    accepted_count = sum(accepted)
    mean_cost = mean(costs)
    mean_quality = mean(quality)
    p50_latency = percentile(latency, 0.50)

    return {
        "trial_count": len(trials),
        "quality_mean": mean_quality,
        "selection_time_mean_ms": mean(selection),
        "selection_time_median_ms": median(selection),
        "cost_mean_usd": mean_cost,
        "cost_total_usd": total_cost,
        "latency_mean_ms": mean(latency),
        "latency_p50_ms": p50_latency,
        "latency_p95_ms": percentile(latency, 0.95),
        "rework_mean": mean(rework),
        "satisfaction_mean": mean(satisfaction),
        "first_pass_acceptance_rate": safe_ratio(sum(first_pass), len(trials)),
        "accepted_task_rate": safe_ratio(accepted_count, len(trials)),
        "cost_per_accepted_task_usd": safe_ratio(total_cost, accepted_count),
        "quality_per_dollar": safe_ratio(mean_quality, mean_cost),
        "quality_adjusted_latency": safe_ratio(
            mean_quality, (p50_latency / 1000.0) if p50_latency else None
        ),
    }


def paired_quality_deltas(
    trials: list[dict[str, Any]], left_arm: str, right_arm: str
) -> list[float]:
    grouped: dict[tuple[str, int], dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for trial in trials:
        key = (trial["case_id"], int(trial["repetition"]))
        grouped[key][trial["arm"]].append(effective_quality(trial))

    deltas = []
    for by_arm in grouped.values():
        if left_arm in by_arm and right_arm in by_arm:
            left = statistics.fmean(by_arm[left_arm])
            right = statistics.fmean(by_arm[right_arm])
            deltas.append(left - right)
    return deltas


def bootstrap_ci(
    values: list[float], seed: int = 42, iterations: int = 5000
) -> tuple[float | None, float | None]:
    if not values:
        return None, None
    if len(values) == 1:
        return values[0], values[0]
    rng = random.Random(seed)
    n = len(values)
    samples = []
    for _ in range(iterations):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        samples.append(statistics.fmean(sample))
    samples.sort()
    lo = samples[int(0.025 * (iterations - 1))]
    hi = samples[int(0.975 * (iterations - 1))]
    return lo, hi


def check_completeness(trials: list[dict[str, Any]]) -> list[str]:
    warnings = []
    counts: dict[tuple[str, int], set[str]] = defaultdict(set)
    for trial in trials:
        counts[(trial["case_id"], int(trial["repetition"]))].add(trial["arm"])

    incomplete = [key for key, arms in counts.items() if set(ARMS) - arms]
    if incomplete:
        warnings.append(
            f"{len(incomplete)} case/repetition pairs do not contain all three arms."
        )

    arm_counts = {arm: sum(1 for t in trials if t["arm"] == arm) for arm in ARMS}
    if len(set(arm_counts.values())) != 1:
        warnings.append(f"Arm trial counts differ: {arm_counts}")

    return warnings


def evaluate_success(summary: dict[str, dict[str, Any]]) -> dict[str, Any]:
    manual = summary["manual"]
    fixed = summary["fixed"]
    intent = summary["intent_os"]

    q_vs_manual = intent["quality_mean"] - manual["quality_mean"]
    q_vs_fixed = intent["quality_mean"] - fixed["quality_mean"]

    manual_sel = manual["selection_time_median_ms"]
    intent_sel = intent["selection_time_median_ms"]
    selection_reduction = None
    if manual_sel and manual_sel > 0:
        selection_reduction = 1.0 - (intent_sel / manual_sel)

    criteria = {
        "quality_noninferior_vs_manual": q_vs_manual >= -3.0,
        "quality_advantage_vs_fixed": q_vs_fixed >= 5.0,
        "selection_time_reduction_80pct": (
            selection_reduction is not None and selection_reduction >= 0.80
        ),
        "cost_not_over_15pct_vs_manual": (
            intent["cost_mean_usd"] <= manual["cost_mean_usd"] * 1.15
        ),
        "latency_not_over_20pct_vs_manual": (
            intent["latency_p50_ms"] <= manual["latency_p50_ms"] * 1.20
        ),
        "rework_not_worse_than_manual": (
            intent["rework_mean"] <= manual["rework_mean"]
        ),
        "satisfaction_not_worse_than_manual": (
            intent["satisfaction_mean"] is not None
            and manual["satisfaction_mean"] is not None
            and intent["satisfaction_mean"] >= manual["satisfaction_mean"] - 0.2
        ),
    }

    strong_conditions = {
        "quality_plus_3_vs_manual": q_vs_manual >= 3.0,
        "quality_plus_8_vs_fixed": q_vs_fixed >= 8.0,
        "cost_10pct_better_vs_manual": (
            intent["cost_mean_usd"] <= manual["cost_mean_usd"] * 0.90
        ),
        "rework_20pct_better_vs_manual": (
            manual["rework_mean"] > 0
            and intent["rework_mean"] <= manual["rework_mean"] * 0.80
        ),
        "time_to_accepted_20pct_better_vs_manual": false,
        "satisfaction_plus_0_5_vs_manual": (
            intent["satisfaction_mean"] is not None
            and manual["satisfaction_mean"] is not None
            and intent["satisfaction_mean"] >= manual["satisfaction_mean"] + 0.5
        ),
    }

    minimum_pass = all(criteria.values())
    strong_count = sum(strong_conditions.values())
    verdict = "FAIL"
    if minimum_pass:
        verdict = "STRONG PASS" if strong_count >= 3 else "PASS"

    return {
        "minimum_criteria": criteria,
        "strong_conditions": strong_conditions,
        "strong_condition_count": strong_count,
        "selection_reduction": selection_reduction,
        "quality_delta_vs_manual": q_vs_manual,
        "quality_delta_vs_fixed": q_vs_fixed,
        "verdict": verdict,
    }


def add_time_to_accepted(
    trials: list[dict[str, Any]],
    summary: dict[str, dict[str, Any]],
    success: dict[str, Any],
) -> None:
    by_arm = {}
    for arm in ARMS:
        values = [
            float(t["time_to_accepted_ms"])
            for t in trials
            if t["arm"] == arm
            and t.get("time_to_accepted_ms") is not None
            and t.get("accepted")
        ]
        by_arm[arm] = {
            "mean_ms": mean(values),
            "p50_ms": median(values),
        }
        summary[arm]["time_to_accepted_mean_ms"] = by_arm[arm]["mean_ms"]
        summary[arm]["time_to_accepted_p50_ms"] = by_arm[arm]["p50_ms"]

    manual = by_arm["manual"]["p50_ms"]
    intent = by_arm["intent_os"]["p50_ms"]
    condition = manual is not None and intent is not None and intent <= manual * 0.80
    success["strong_conditions"]["time_to_accepted_20pct_better_vs_manual"] = condition
    success["strong_condition_count"] = sum(success["strong_conditions"].values())
    if all(success["minimum_criteria"].values()):
        success["verdict"] = (
            "STRONG PASS" if success["strong_condition_count"] >= 3 else "PASS"
        )


def markdown_report(
    run: dict[str, Any],
    summary: dict[str, dict[str, Any]],
    success: dict[str, Any],
    ci_manual: tuple[float | None, float | None],
    ci_fixed: tuple[float | None, float | None],
    warnings: list[str],
) -> str:
    lines = []
    lines.append(f"# Benchmark Result — {run['run_id']}")
    lines.append("")
    lines.append(f"**Verdict: {success['verdict']}**")
    lines.append("")
    lines.append("| Metric | Manual | Fixed | Intent OS |")
    lines.append("|---|---:|---:|---:|")
    rows = [
        ("Quality", "quality_mean", ""),
        ("Selection median (ms)", "selection_time_median_ms", ""),
        ("Cost / trial (USD)", "cost_mean_usd", "$"),
        ("Latency p50 (ms)", "latency_p50_ms", ""),
        ("Latency p95 (ms)", "latency_p95_ms", ""),
        ("Rework / trial", "rework_mean", ""),
        ("Satisfaction (1-7)", "satisfaction_mean", ""),
        ("First-pass acceptance", "first_pass_acceptance_rate", "%"),
        ("Accepted task rate", "accepted_task_rate", "%"),
        ("Time-to-accepted p50 (ms)", "time_to_accepted_p50_ms", ""),
    ]
    for label, key, mode in rows:
        values = []
        for arm in ARMS:
            value = summary[arm].get(key)
            if mode == "%":
                values.append(fmt_pct(value))
            elif mode == "$":
                values.append(f"${fmt(value, 4)}" if value is not None else "n/a")
            else:
                values.append(fmt(value))
        lines.append(f"| {label} | {values[0]} | {values[1]} | {values[2]} |")

    lines.append("")
    lines.append("## Paired quality deltas")
    lines.append("")
    lines.append(
        f"- Intent OS − Manual: {success['quality_delta_vs_manual']:.2f} "
        f"(bootstrap 95% CI {fmt(ci_manual[0])} .. {fmt(ci_manual[1])})"
    )
    lines.append(
        f"- Intent OS − Fixed: {success['quality_delta_vs_fixed']:.2f} "
        f"(bootstrap 95% CI {fmt(ci_fixed[0])} .. {fmt(ci_fixed[1])})"
    )

    lines.append("")
    lines.append("## Minimum criteria")
    lines.append("")
    for name, passed in success["minimum_criteria"].items():
        lines.append(f"- {'✅' if passed else '❌'} {name}")

    lines.append("")
    lines.append("## Strong conditions")
    lines.append("")
    for name, passed in success["strong_conditions"].items():
        lines.append(f"- {'✅' if passed else '⬜'} {name}")
    lines.append(
        f"- Strong conditions met: {success['strong_condition_count']} / "
        f"{len(success['strong_conditions'])}"
    )

    if warnings:
        lines.append("")
        lines.append("## Warnings")
        lines.append("")
        for warning in warnings:
            lines.append(f"- ⚠️ {warning}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_json", type=Path)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of Markdown.",
    )
    args = parser.parse_args()

    run = json.loads(args.run_json.read_text(encoding="utf-8"))
    if run.get("benchmark_id") != "system-routing-v0.1":
        raise ValueError("Unsupported benchmark_id.")

    trials = [t for t in run["trials"] if not t.get("excluded", False)]
    warnings = check_completeness(trials)

    by_arm = {arm: [t for t in trials if t["arm"] == arm] for arm in ARMS}
    missing = [arm for arm, arm_trials in by_arm.items() if not arm_trials]
    if missing:
        raise ValueError(f"Missing benchmark arms: {', '.join(missing)}")

    summary = {arm: aggregate(arm_trials) for arm, arm_trials in by_arm.items()}
    success = evaluate_success(summary)
    add_time_to_accepted(trials, summary, success)

    d_manual = paired_quality_deltas(trials, "intent_os", "manual")
    d_fixed = paired_quality_deltas(trials, "intent_os", "fixed")
    ci_manual = bootstrap_ci(d_manual)
    ci_fixed = bootstrap_ci(d_fixed)

    output = {
        "benchmark_id": run["benchmark_id"],
        "run_id": run["run_id"],
        "summary": summary,
        "paired_quality": {
            "intent_minus_manual": {
                "mean": mean(d_manual),
                "ci95": ci_manual,
                "pairs": len(d_manual),
            },
            "intent_minus_fixed": {
                "mean": mean(d_fixed),
                "ci95": ci_fixed,
                "pairs": len(d_fixed),
            },
        },
        "success": success,
        "warnings": warnings,
    }

    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(markdown_report(run, summary, success, ci_manual, ci_fixed, warnings))
    return 0


if __name__ == "__main__":
    sys.exit(main())
