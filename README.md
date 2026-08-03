# Intent OS Specification

> **Human defines intent. System determines execution.**

인간과 인공지능 시스템 사이의 새로운 상호작용 구조를 정의하는 기술 명세서.

- **Version:** v0.1 Draft
- **Status:** Foundational Specification
- **Last Updated:** 2026-07-31

---

## 이름에 대하여

이 프로젝트는 초안 단계에서 **AI OS**로 불렸으나 **Intent OS**로 변경되었다.

이유: 이 시스템에서 AI는 여러 Resource 중 하나일 뿐이다. 검색 엔진, 데이터베이스, 자동화 도구, 인간 전문가도 동일하게 취급된다 ([Principle 03 — Resource Agnostic](v1-core-concepts.md#principle-03--resource-agnostic)). 이름에 "AI"가 들어가면 구현 과정에서 LLM 연결에만 집중하게 되어 핵심 설계 원칙과 충돌한다.

이 시스템의 실제 발명품은 AI를 고르는 방법이 아니라 **Intent → Task → Capability → Resource** 라는 순서다.

---

## 핵심 명제

Intent OS의 목적은 **지능 자체를 만드는 것**이 아니라, **지능 자원을 최적으로 활용하는 것**이다.

```
기존 방식                    Intent OS 방식
─────────                    ──────────
User                         User
  ↓                            ↓
Prompt                       Goal
  ↓                            ↓
AI                          Intent → Task → Capability
  ↓                            ↓
Answer                      Resource → Execution → Outcome
```

---

## 목차

| Volume | 내용 | 문서 |
|---|---|---|
| 1 | Core Concepts — 7개 핵심 객체와 설계 철학 | [v1-core-concepts.md](v1-core-concepts.md) |
| 2 | Architecture — 8개 Layer 구조 | [v2-architecture.md](v2-architecture.md) |
| 3 | Runtime — 실행 생명주기 7단계 | [v3-runtime.md](v3-runtime.md) |
| 4 | Decision Engine — Resource 선택 알고리즘 | [v4-decision-engine.md](v4-decision-engine.md) |
| 4-A | ↳ Decision Engine 상세 — 7개 모듈, Utility 공식 | [v4a-decision-engine-detail.md](v4a-decision-engine-detail.md) |
| 4-B | ↳ Resource Intelligence — Capability DNA, Drift 감지 | [v4b-resource-intelligence.md](v4b-resource-intelligence.md) |
| 4-C | ↳ Resource Genome — 행동 기반 AI 표현, Meta Prediction | [v4c-resource-genome.md](v4c-resource-genome.md) |
| 4-D | ↳ Autonomous Benchmarking — AI를 자동으로 연구·평가 | [v4d-autonomous-benchmarking.md](v4d-autonomous-benchmarking.md) |
| 4-E | ↳ Strategy Graph — 전략 자체를 학습·재사용 ⚠️연구 | [v4e-strategy-graph.md](v4e-strategy-graph.md) |
| 4-F | ↳ World Model — 사용자의 현실을 모델링 ⚠️연구 | [v4f-world-model.md](v4f-world-model.md) |
| 5 | Learning Engine — 경험 축적과 개선 | [v5-learning-engine.md](v5-learning-engine.md) |
| 6 | Developer Platform — 외부 Resource 연결 | [v6-developer-platform.md](v6-developer-platform.md) |
| 7 | Reference Implementation — MVP 및 로드맵 | [v7-reference-implementation.md](v7-reference-implementation.md) |

## Entity Specification

12개 Core Entity를 RFC/ISO 표준 수준으로 정의하는 명세. Entity 하나를 운영체제 수준으로 완성한 뒤 다음 Entity로 넘어간다.

| Entity | 이름 | 문서 | 상태 |
|---|---|---|---|
| — | Entity 개요 — 12개 Core Entity, Entity/Process/Runtime State 구분 | [entities/README.md](entities/README.md) | v1.0 Draft |
| 001 | Goal — 정의, 규칙, Formal Grammar, CGR, 검증 알고리즘 | [entities/e001-goal.md](entities/e001-goal.md) | v1.0 Draft |
| 001-A | Goal Graph — 관계, 계층, Score, Propagation, Invariants | [entities/e001a-goal-graph.md](entities/e001a-goal-graph.md) | v1.0 Draft |

## 스키마

기계가 읽을 수 있는 JSON Schema는 [`schemas/`](intent-os-spec/schemas/) 폴더에 있다.

- [`goal.schema.json`](intent-os-spec/schemas/goal.schema.json) — Canonical Goal Representation (Entity 001)
- [`goal-graph.schema.json`](intent-os-spec/schemas/goal-graph.schema.json) — Goal Graph (Entity 001-A)
- [`task.schema.json`](intent-os-spec/schemas/task.schema.json)
- [`resource.schema.json`](intent-os-spec/schemas/resource.schema.json)
- [`execution.schema.json`](intent-os-spec/schemas/execution.schema.json)

---

## 의존 관계

```mermaid
graph TD
    V1[Volume 1<br/>Core Concepts] --> V2[Volume 2<br/>Architecture]
    V2 --> V3[Volume 3<br/>Runtime]
    V3 --> V4[Volume 4<br/>Decision Engine]
    V4 --> V4A[4-A Detail]
    V4A --> V4B[4-B Resource Intelligence]
    V4B --> V4C[4-C Resource Genome]
    V4C --> V4D[4-D Autonomous Benchmarking]
    V4D --> V4E[4-E Strategy Graph]
    V4E --> V4F[4-F World Model]
    V4 --> V5[Volume 5<br/>Learning Engine]
    V5 --> V6[Volume 6<br/>Developer Platform]
    V6 --> V7[Volume 7<br/>Reference Implementation]
```

---

## 가장 중요한 규칙

> **Never choose an AI before understanding the Goal.**
>
> 목표를 이해하지 않은 AI 선택은 항상 최적화 실패를 만든다.
