#!/usr/bin/env python3
"""벤치마크 Trial을 실제로 실행하는 Resource 어댑터.

`benchmarks/system-routing-v0.1.md` §7 Trial Procedure를 실행 가능하게 만든다.
세 Arm이 **같은 Resource pool**을 써야 하므로(§4 Resource Pool Freeze),
Arm은 어댑터를 고르는 방식만 다르고 어댑터 자체는 공유한다.

어댑터는 세 종류다. 종류가 곧 그 실행의 증거력이다.

| kind | 무엇을 하는가 | 근거로 쓸 수 있나 |
|---|---|---|
| `live_api` | 실제 provider API를 호출한다 | ✅ |
| `human` | 사람이 직접 수행한다 | ✅ |
| `synthetic` | 결정적 로컬 응답을 만든다 | ❌ 배관 점검 전용 |

`synthetic`이 한 번이라도 쓰이면 실행 기록의 `provenance.evidence`는
false가 되고, 스키마가 그것을 강제한다. 합성 실행이 실측으로 오인되는 것을
막는 장치는 이것 하나뿐이다 — 두 기록은 형태가 완전히 같기 때문이다.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Protocol


class AdapterError(RuntimeError):
    """어댑터가 결과를 낼 수 없다. Trial은 status를 남기고 계속 진행한다."""

    def __init__(self, message: str, status: str = "provider_error") -> None:
        super().__init__(message)
        self.status = status  # 스키마 trials[].status enum 값


@dataclass
class ExecutionResult:
    """Trial 한 번의 실행 결과. 측정값은 전부 실제로 잰 것이어야 한다."""

    output: str
    latency_ms: float
    cost_usd: float
    internal_retry_count: int = 0
    status: str = "completed"
    usage: dict = field(default_factory=dict)


class Adapter(Protocol):
    resource_id: str
    kind: str  # "live_api" | "human" | "synthetic"

    def execute(self, prompt: str) -> ExecutionResult: ...


# ─────────────────────────────────────────────────────────────────────
# live_api — 실제 호출. 지연과 비용을 실제로 잰다.
# ─────────────────────────────────────────────────────────────────────

@dataclass
class AnthropicAdapter:
    """Anthropic Messages API를 실제로 호출한다.

    비용은 응답의 `usage`(실제 토큰 수)와 `pricing`(1M 토큰당 USD)으로 계산한다.
    추정하지 않는다. usage가 없으면 비용을 지어내는 대신 예외를 던진다.
    """

    resource_id: str
    model: str
    pricing: dict  # {"input_per_mtok": float, "output_per_mtok": float}
    api_key: str
    base_url: str = "https://api.anthropic.com"
    max_tokens: int = 2048
    timeout_s: float = 120.0
    kind: str = "live_api"

    def execute(self, prompt: str) -> ExecutionResult:
        body = json.dumps({
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url}/v1/messages",
            data=body,
            headers={
                "content-type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
        )

        started = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                payload = json.load(resp)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:300]
            raise AdapterError(f"{self.model} HTTP {exc.code}: {detail}") from exc
        except TimeoutError as exc:
            raise AdapterError(f"{self.model} 시간 초과", status="timeout") from exc
        except urllib.error.URLError as exc:
            raise AdapterError(f"{self.model} 연결 실패: {exc.reason}") from exc
        latency_ms = (time.perf_counter() - started) * 1000

        usage = payload.get("usage") or {}
        if "input_tokens" not in usage or "output_tokens" not in usage:
            # 비용을 추정으로 채우면 M3가 오염된다. 차라리 실패시킨다.
            raise AdapterError(f"{self.model} 응답에 usage가 없어 비용을 잴 수 없다")

        cost = (usage["input_tokens"] / 1e6 * self.pricing["input_per_mtok"]
                + usage["output_tokens"] / 1e6 * self.pricing["output_per_mtok"])

        text = "".join(b.get("text", "") for b in payload.get("content", [])
                       if b.get("type") == "text")
        if not text.strip():
            raise AdapterError(f"{self.model} 빈 응답", status="invalid_output")

        return ExecutionResult(output=text, latency_ms=latency_ms, cost_usd=cost, usage=usage)


# ─────────────────────────────────────────────────────────────────────
# human — 사람이 수행한다. 벽시계로 실제 소요를 잰다.
# ─────────────────────────────────────────────────────────────────────

@dataclass
class HumanAdapter:
    """사람 Resource(예: 김 카피라이터)가 직접 수행하는 Trial.

    Resource pool에 `kind: human`이 있으면(§4) 그것도 실행 가능해야 한다.
    소요 시간은 조작자가 시작/종료를 알리는 벽시계로 잰다.
    """

    resource_id: str
    hourly_rate_usd: float
    prompt_fn: object = input  # 테스트에서 주입 가능하게 둔다
    kind: str = "human"

    def execute(self, prompt: str) -> ExecutionResult:
        print(f"\n[사람 Resource: {self.resource_id}] 아래 Task를 수행한다.\n")
        print(prompt)
        self.prompt_fn("\n시작하려면 Enter. 끝나면 다시 Enter를 누른다. > ")
        started = time.perf_counter()
        output = self.prompt_fn("결과 파일 경로 또는 결과 텍스트를 붙여넣고 Enter > ")
        latency_ms = (time.perf_counter() - started) * 1000

        if not output.strip():
            raise AdapterError(f"{self.resource_id} 결과 없음", status="user_abandoned")

        # 사람 비용은 실제 소요 시간 × 시급이다. 추정 상수를 쓰지 않는다.
        cost = self.hourly_rate_usd * (latency_ms / 3_600_000)
        return ExecutionResult(output=output, latency_ms=latency_ms, cost_usd=cost)


# ─────────────────────────────────────────────────────────────────────
# synthetic — 배관 점검 전용. 근거가 될 수 없다.
# ─────────────────────────────────────────────────────────────────────

@dataclass
class SyntheticAdapter:
    """결정적 로컬 응답. **측정값이 아니다.**

    러너와 채점기 배관이 도는지 확인하는 용도다. 지연은 실제 계산 시간이지만
    provider 왕복이 없으므로 M4로 쓸 수 없고, 비용은 0으로 두어 M3를 오염시키지
    않는다. 이 어댑터가 쓰인 실행은 `provenance.evidence: false`가 강제된다.
    """

    resource_id: str
    kind: str = "synthetic"

    def execute(self, prompt: str) -> ExecutionResult:
        started = time.perf_counter()
        output = (f"[SYNTHETIC · 벤치마크 근거 아님] {self.resource_id} "
                  f"응답 자리표시자 ({len(prompt)}자 입력)")
        return ExecutionResult(
            output=output,
            latency_ms=(time.perf_counter() - started) * 1000,
            cost_usd=0.0,
        )


def build_adapter(spec: dict, *, allow_synthetic: bool) -> Adapter:
    """Resource pool 항목 하나를 어댑터로 만든다.

    자격 증명이 없으면 조용히 합성으로 떨어지지 않는다. 그렇게 하면 실측인 줄
    알고 돌린 실행이 합성 데이터를 낳는다.
    """
    kind = spec.get("kind")

    if kind == "model":
        key = os.environ.get(spec.get("api_key_env", "ANTHROPIC_API_KEY"), "")
        if key:
            return AnthropicAdapter(
                resource_id=spec["resource_id"],
                model=spec["model"],
                pricing=spec["pricing_snapshot"],
                api_key=key,
                base_url=os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
            )
        if not allow_synthetic:
            raise AdapterError(
                f"{spec['resource_id']}: {spec.get('api_key_env', 'ANTHROPIC_API_KEY')}가 없다. "
                f"실측을 하려면 키를 설정한다. 배관만 확인하려면 --allow-synthetic을 쓴다 "
                f"(그 실행은 근거가 되지 않는다)."
            )
        return SyntheticAdapter(resource_id=spec["resource_id"])

    if kind == "human":
        return HumanAdapter(
            resource_id=spec["resource_id"],
            hourly_rate_usd=spec["hourly_rate_usd"],
        )

    raise AdapterError(f"{spec.get('resource_id')}: 알 수 없는 kind {kind!r}")
