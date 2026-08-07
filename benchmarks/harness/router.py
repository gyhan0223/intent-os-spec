#!/usr/bin/env python3
"""Arm C의 라우터. Benchmark Case를 Resource pool의 한 항목으로 보낸다.

Intent OS의 경로 그대로 간다 — Goal → Intent → Task → Capability → Resource.
Task 분류와 효용 계산은 `reference/marketing_thin/runtime.py`의 `RuleRouter`를
재사용한다. 벤치마크용 라우터를 따로 만들면 측정 대상이 제품이 아니라
벤치마크 전용 코드가 되어 실험이 무의미해진다.

§5 Fairness Rules에 따라 라우터가 볼 수 없는 것이 있다. `expected`,
`quality_rubric`, Judge comment는 §12 Prompt Leakage가 금지한다. `rank()`는
`prompt`·`category`·`required_capabilities`·`tool_requirement`만 읽는다.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from reference.marketing_thin.runtime import RuleRouter  # noqa: E402

ROUTER_VERSION = "rule-router-phase0"

# Benchmark의 6개 category를 참조 구현의 Task 유형으로 옮긴다.
# 라우터를 벤치마크에 맞춰 고치는 대신 입력을 제품의 어휘로 번역한다.
CATEGORY_TO_TASK_TYPE = {
    "research": "Research",
    "writing": "Creation",
    "planning": "Creation",
    "coding": "Creation",
    "structured": "Verification",
    "tool_choice": "Research",
}

# 참조 구현의 추상 Resource id → 실제 pool 항목. 실행 설정에서 덮어쓴다.
DEFAULT_BINDING = {
    "tool:web-search": "tool:web-search",
    "model:fast": "model:fast",
    "model:balanced": "model:balanced",
    "model:quality": "model:quality",
}


@dataclass
class BenchmarkRouter:
    """Case를 받아 실행할 Resource id를 순위대로 돌려준다."""

    available: set[str]
    binding: dict[str, str] = None
    _inner: RuleRouter = None

    def __post_init__(self) -> None:
        self.binding = self.binding or dict(DEFAULT_BINDING)
        self._inner = RuleRouter()

    @property
    def config(self) -> dict:
        """`router_config_hash`의 재료. 실행 간 설정 차이를 드러낸다."""
        return {
            "version": ROUTER_VERSION,
            "category_map": CATEGORY_TO_TASK_TYPE,
            "binding": self.binding,
            "available": sorted(self.available),
        }

    def rank(self, case: dict) -> list[str]:
        task_type = CATEGORY_TO_TASK_TYPE.get(case["category"])
        if task_type is None:
            return []

        ranked = self._inner.rank({"task_type": task_type})

        out = []
        for spec, _utility in ranked:
            resource_id = self.binding.get(spec.resource_id, spec.resource_id)
            if resource_id not in self.available:
                continue
            # Tool이 필수인 Task에 tool 없는 Resource를 보내지 않는다.
            if case.get("tool_requirement") == "required" and not resource_id.startswith("tool:"):
                continue
            out.append(resource_id)

        # 참조 라우터가 tool을 못 고르는 유형인데 tool이 필수면 pool에서 직접 찾는다.
        if not out and case.get("tool_requirement") == "required":
            out = sorted(r for r in self.available if r.startswith("tool:"))
        return out
