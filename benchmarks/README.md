# Intent OS Benchmarks

Intent OS의 벤치마크는 두 층으로 나뉜다.

## 1. Resource Benchmark

**질문:** 특정 AI/Tool/Resource가 어떤 Capability에서 얼마나 잘하는가?

정본 설계는 [Volume 4-D — Autonomous Benchmarking Engine](../v4d-autonomous-benchmarking.md)에 있다.

이 결과는 Resource Profile과 Decision Engine의 prior를 개선하는 데 사용한다.

## 2. System Routing Benchmark

**질문:** 같은 Resource pool이 주어졌을 때 Intent OS의 자동 라우팅이 사용자의 직접 선택 또는 고정 기본 Resource보다 실제로 더 좋은가?

정본 프로토콜:

- [System Routing Benchmark v0.1](system-routing-v0.1.md)
- [30-Task Case Suite](cases/system-routing-v0.1.json)
- [Run JSON Schema](schemas/system-benchmark-run.schema.json)
- [Score Calculator](../tools/score-system-benchmark.py)

비교 Arm:

```text
A — Manual Choice
B — Fixed Default
C — Intent OS
```

핵심 지표:

```text
Result Quality
User Selection Time
Total Cost
Total Latency
Rework Count
User Satisfaction
```

## Versioning Rule

Benchmark version은 Router version과 독립적이다.

```text
Benchmark Suite: system-routing-v0.1
Router:          router-v0.3
Resource Pool:   pool-2026-08-07
```

Router를 수정해도 동일 Benchmark version으로 재실행할 수 있다.

단, Holdout Task가 Router tuning에 노출되었거나 평가 기준이 변경되면 Benchmark Suite version을 올린다.

## Rule

> Benchmark 결과를 본 뒤 성공 기준을 바꾸지 않는다.

Threshold, Metric, Holdout split은 Run 전에 고정한다. 변경이 필요하면 다음 Benchmark version에서 변경한다.