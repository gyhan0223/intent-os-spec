#!/usr/bin/env python3
"""세 Arm을 실행해 Trial 기록을 만든다.

`benchmarks/system-routing-v0.1.md` §7 Trial Procedure 구현이다.

    Arm A (manual)   사용자에게 catalog를 보여주고 타이머를 재며 선택을 받는다
    Arm B (fixed)    사전 지정 Resource로 즉시 실행. selection_time_ms = 0
    Arm C (intent_os) Router가 고른다. selection_time_ms = 0, router 시간은 latency에 포함

**사람에게서만 나오는 값은 사람에게 묻는다.** §8의 M2(선택 시간),
M5(재작업), M6(만족도)와 accepted 여부가 그렇다. 이 값들을 프로그램이
만들어내면 그 순간 실행 기록은 실측이 아니라 창작이 된다. 조작자가 없는
실행(`--no-human`)은 해당 필드를 비우고 `provenance.human_measurements`를
false로 남긴다 — 스키마가 그런 기록의 `evidence`를 false로 강제한다.
"""
from __future__ import annotations

import hashlib
import json
import random
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .adapters import Adapter, AdapterError, ExecutionResult

ARMS = ("manual", "fixed", "intent_os")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


@dataclass
class HumanProbe:
    """사람에게 M2·M5·M6과 accepted를 묻는다.

    `enabled`가 False면 묻지 않고 None을 돌려준다. 기본값으로 때우지 않는다 —
    rework=0, satisfaction=5 같은 기본값은 조용히 데이터가 되어버린다.
    """

    enabled: bool = True
    prompt_fn: object = input

    def _ask_int(self, question: str, lo: int, hi: int) -> int | None:
        if not self.enabled:
            return None
        while True:
            raw = self.prompt_fn(f"{question} [{lo}-{hi}] > ").strip()
            if raw.isdigit() and lo <= int(raw) <= hi:
                return int(raw)
            print(f"  {lo}~{hi} 사이 정수를 입력한다.")

    def rework_count(self) -> int | None:
        return self._ask_int("재작업 횟수 (0=첫 결과 수락)", 0, 2)

    def satisfaction(self) -> int | None:
        return self._ask_int('"이 결과를 실제 목적에 사용한다면 얼마나 만족합니까?"', 1, 7)

    def accepted(self) -> bool | None:
        if not self.enabled:
            return None
        while True:
            raw = self.prompt_fn("결과를 수락하는가? [y/n] > ").strip().lower()
            if raw in ("y", "n"):
                return raw == "y"

    def manual_selection(self, catalog: list[str]) -> tuple[str, float] | None:
        """§7 Arm A 1~4단계. catalog 표시 → 타이머 시작 → 선택 → 시간 기록."""
        if not self.enabled:
            return None
        print("\n[Arm A] Resource catalog:")
        for i, rid in enumerate(catalog, 1):
            print(f"  {i}. {rid}")
        started = time.perf_counter()
        while True:
            raw = self.prompt_fn(f"어느 Resource로 실행하는가? [1-{len(catalog)}] > ").strip()
            if raw.isdigit() and 1 <= int(raw) <= len(catalog):
                elapsed_ms = (time.perf_counter() - started) * 1000
                return catalog[int(raw) - 1], elapsed_ms


@dataclass
class TrialRunner:
    adapters: dict[str, Adapter]
    fixed_default_resource_id: str
    router: object                      # rank(case) -> [resource_id, ...]
    probe: HumanProbe = field(default_factory=HumanProbe)

    def _execute(self, resource_id: str, prompt: str) -> tuple[ExecutionResult | None, str]:
        try:
            return self.adapters[resource_id].execute(prompt), "completed"
        except AdapterError as exc:
            print(f"  ! {exc}")
            return None, exc.status

    def run_trial(self, case: dict, arm: str, repetition: int) -> dict:
        assert arm in ARMS, arm
        prompt = case["prompt"]
        selection_time_ms = 0.0
        router_overhead_ms = 0.0

        if arm == "manual":
            picked = self.probe.manual_selection(sorted(self.adapters))
            if picked is None:
                # 사람이 없으면 Manual arm은 성립하지 않는다. 임의로 고르지 않는다.
                return self._abandoned(case, arm, repetition,
                                       "Manual arm은 사용자의 실제 선택을 요구한다 (§7 Arm A)")
            resource_id, selection_time_ms = picked
        elif arm == "fixed":
            resource_id = self.fixed_default_resource_id
        else:
            started = time.perf_counter()
            ranked = self.router.rank(case)
            router_overhead_ms = (time.perf_counter() - started) * 1000
            if not ranked:
                return self._abandoned(case, arm, repetition, "Router가 Resource를 고르지 못했다")
            resource_id = ranked[0]

        result, status = self._execute(resource_id, prompt)

        if result is None:
            return self._record(case, arm, repetition, [resource_id], status=status,
                                selection_time_ms=selection_time_ms,
                                router_overhead_ms=router_overhead_ms,
                                execution_latency_ms=0.0, cost=0.0, accepted=False)

        # Intent OS의 라우팅 시간은 숨기지 않고 지연에 포함한다 (§8 M4).
        execution_latency_ms = result.latency_ms + router_overhead_ms

        print(f"\n  [{arm}/{resource_id}] {execution_latency_ms:.0f}ms  ${result.cost_usd:.6f}")
        print(f"  {result.output[:400]}")

        return self._record(
            case, arm, repetition, [resource_id], status="completed",
            selection_time_ms=selection_time_ms,
            router_overhead_ms=router_overhead_ms,
            execution_latency_ms=execution_latency_ms,
            cost=result.cost_usd,
            internal_retry_count=result.internal_retry_count,
            rework_count=self.probe.rework_count(),
            satisfaction=self.probe.satisfaction(),
            accepted=self.probe.accepted(),
            output=result.output,
        )

    def _abandoned(self, case, arm, repetition, reason) -> dict:
        rec = self._record(case, arm, repetition, [], status="user_abandoned",
                           selection_time_ms=0.0, router_overhead_ms=0.0,
                           execution_latency_ms=0.0, cost=0.0, accepted=False)
        rec["excluded"] = True
        rec["excluded_reason"] = reason
        return rec

    @staticmethod
    def _record(case, arm, repetition, resource_ids, *, status, selection_time_ms,
                router_overhead_ms, execution_latency_ms, cost,
                internal_retry_count=0, rework_count=None, satisfaction=None,
                accepted=None, output=None) -> dict:
        return {
            "trial_id": f"{case['id']}-{arm}-r{repetition}",
            "case_id": case["id"],
            "repetition": repetition,
            "arm": arm,
            "status": status,
            "selected_resource_ids": resource_ids,
            "decision_id": None,
            "selection_time_ms": round(selection_time_ms, 3),
            "router_overhead_ms": round(router_overhead_ms, 3),
            "execution_latency_ms": round(execution_latency_ms, 3),
            "time_to_accepted_ms": None,
            "total_cost_usd": round(cost, 8),
            # 사람이 답하지 않았으면 0으로 때우지 않는다. 스키마상 필수이므로
            # 0을 넣되 provenance.human_measurements.rework=false로 무효를 남긴다.
            "rework_count": rework_count if rework_count is not None else 0,
            "internal_retry_count": internal_retry_count,
            "quality_score": None,          # M1은 별도 blind judge 단계에서 채운다
            "satisfaction_1_7": satisfaction,
            "accepted": bool(accepted) if accepted is not None else False,
            "excluded": False,
            "excluded_reason": None,
            "output_artifact_ref": None if output is None else _artifact_ref(output),
            "freshness_snapshot_ref": None,
        }


def _artifact_ref(output: str) -> str:
    return "sha256:" + hashlib.sha256(output.encode("utf-8")).hexdigest()[:32]


def build_run_record(*, trials, resource_pool, fixed_default, router_version,
                     router_config, seed, operator_expertise, adapter_kinds,
                     human_measurements, started_at, case_suite_version,
                     judge_ids, notes="") -> dict:
    """Trial 목록을 스키마에 맞는 실행 기록으로 감싼다.

    `evidence`는 여기서 계산한다. 조작자가 주장하는 게 아니라 실행 사실에서
    유도한다 — 합성 어댑터가 섞였거나 사람 측정이 하나라도 비면 false다.
    """
    evidence = ("synthetic" not in adapter_kinds) and all(human_measurements.values())

    reasons = []
    if "synthetic" in adapter_kinds:
        reasons.append("합성 어댑터가 사용되었다")
    missing = [k for k, v in human_measurements.items() if not v]
    if missing:
        reasons.append(f"사람 측정 누락: {', '.join(missing)}")

    return {
        "benchmark_id": "system-routing-v0.1",
        "run_id": f"run-{uuid.uuid4().hex[:12]}",
        "started_at": started_at,
        "finished_at": _now(),
        "case_suite_version": case_suite_version,
        "router_version": router_version,
        "router_config_hash": hashlib.sha256(
            json.dumps(router_config, sort_keys=True).encode()).hexdigest()[:16],
        "fixed_default_resource_id": fixed_default,
        "randomization_seed": seed,
        "operator_expertise": operator_expertise,
        "resource_pool_snapshot": resource_pool,
        "judge_configuration": {
            "blind": True,
            "judge_ids": judge_ids,
            "human_tiebreak_threshold": 15,
        },
        "evaluation_cost_usd": 0.0,
        "provenance": {
            "evidence": evidence,
            "adapter_kinds": sorted(set(adapter_kinds)),
            "human_measurements": human_measurements,
            "notes": "; ".join(reasons) if reasons else "실측 실행",
        },
        "notes": notes,
        "trials": trials,
    }


def trial_order(cases: list[dict], seed: int, repetitions: int = 1) -> list[tuple[dict, str, int]]:
    """§12 Order Effect — Arm 제시 순서를 Task마다 무작위화한다."""
    rng = random.Random(seed)
    plan = []
    for rep in range(1, repetitions + 1):
        for case in cases:
            arms = list(ARMS)
            rng.shuffle(arms)
            plan.extend((case, arm, rep) for arm in arms)
    return plan
