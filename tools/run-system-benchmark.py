#!/usr/bin/env python3
"""System Routing Benchmark 실행 기록을 만든다.

    python3 tools/run-system-benchmark.py --pool benchmarks/pools/<pool>.json \
        --operator-expertise intermediate --out runs/<name>.json

기본은 **실측**이다. 자격 증명이 없으면 조용히 합성으로 떨어지지 않고 멈춘다.
배관만 확인하려면 `--allow-synthetic`을 쓴다 — 그 실행은 스키마가
`provenance.evidence: false`를 강제하므로 근거로 인용할 수 없다.

사람 측정(§8 M2·M5·M6)은 조작자에게 직접 묻는다. `--no-human`을 주면 묻지 않고
비워두며, 그 실행 역시 근거가 되지 않는다.
"""
from __future__ import annotations

# tools/validate-all.py 가 읽는 CI 선언.
# 이것은 검증기가 아니라 실행기다. 실측에는 자격 증명과 피험자가 필요하므로
# CI에서 자동으로 돌릴 수 없다.
CI_SKIP = True

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from benchmarks.harness.adapters import AdapterError, build_adapter  # noqa: E402
from benchmarks.harness.router import ROUTER_VERSION, BenchmarkRouter  # noqa: E402
from benchmarks.harness.runner import (  # noqa: E402
    HumanProbe, TrialRunner, build_run_record, trial_order,
)

CASES = ROOT / "benchmarks" / "cases" / "system-routing-v0.1.json"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pool", required=True, type=Path, help="Resource pool 설정 (§4 freeze)")
    p.add_argument("--out", required=True, type=Path, help="실행 기록 출력 경로")
    p.add_argument("--operator-expertise", required=True,
                   choices=["novice", "intermediate", "expert"], help="§12 self-rated expertise")
    p.add_argument("--split", default="development", choices=["development", "holdout", "all"])
    p.add_argument("--repetitions", type=int, default=1, help="§3 변동성 측정용 반복 횟수")
    p.add_argument("--seed", type=int, default=20260807, help="§12 Arm 순서 무작위화 seed")
    p.add_argument("--allow-synthetic", action="store_true",
                   help="자격 증명 없이 합성 어댑터로 배관만 확인한다 (근거 아님)")
    p.add_argument("--no-human", action="store_true",
                   help="사람 측정을 묻지 않는다 (근거 아님)")
    p.add_argument("--limit", type=int, help="앞에서 N개 Case만 실행한다")
    args = p.parse_args()

    pool_cfg = json.loads(args.pool.read_text(encoding="utf-8"))
    suite = json.loads(CASES.read_text(encoding="utf-8"))

    cases = [c for c in suite["cases"]
             if args.split == "all" or c["split"] == args.split]
    if args.limit:
        cases = cases[:args.limit]
    if not cases:
        print("실행할 Case가 없다.", file=sys.stderr)
        return 1

    try:
        adapters = {s["resource_id"]: build_adapter(s, allow_synthetic=args.allow_synthetic)
                    for s in pool_cfg["resources"]}
    except AdapterError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 2

    fixed_default = pool_cfg["fixed_default_resource_id"]
    if fixed_default not in adapters:
        print(f"FAIL fixed_default_resource_id {fixed_default!r}가 pool에 없다.", file=sys.stderr)
        return 2

    router = BenchmarkRouter(available=set(adapters))
    probe = HumanProbe(enabled=not args.no_human)
    runner = TrialRunner(adapters=adapters, fixed_default_resource_id=fixed_default,
                         router=router, probe=probe)

    plan = trial_order(cases, seed=args.seed, repetitions=args.repetitions)
    print(f"Case {len(cases)}개 × Arm 3개 × 반복 {args.repetitions} = Trial {len(plan)}개\n")

    from benchmarks.harness.runner import _now
    started_at = _now()
    trials = []
    for i, (case, arm, rep) in enumerate(plan, 1):
        print(f"[{i}/{len(plan)}] {case['id']} · {arm} · r{rep}")
        trials.append(runner.run_trial(case, arm, rep))

    human_ok = not args.no_human
    record = build_run_record(
        trials=trials,
        resource_pool=pool_cfg["resource_pool_snapshot"],
        fixed_default=fixed_default,
        router_version=ROUTER_VERSION,
        router_config=router.config,
        seed=args.seed,
        operator_expertise=args.operator_expertise,
        adapter_kinds=[a.kind for a in adapters.values()],
        human_measurements={
            "selection_time": human_ok,
            "rework": human_ok,
            "satisfaction": human_ok,
            # M1은 이 러너가 채우지 않는다. blind judge 단계는 별도다.
            "quality_judges": False,
        },
        started_at=started_at,
        case_suite_version=suite["version"],
        judge_ids=pool_cfg.get("judge_ids", ["pending"]),
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")

    prov = record["provenance"]
    print(f"\n기록: {args.out}")
    print(f"Trial {len(trials)}개 · evidence={prov['evidence']} · {prov['notes']}")
    if not prov["evidence"]:
        print("\n이 실행은 벤치마크 근거가 아니다. 위 사유를 해소해야 §10 판정에 쓸 수 있다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
