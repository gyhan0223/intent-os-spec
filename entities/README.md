# Entity Specification

- **Version:** v1.0 Draft
- **Status:** Core Specification
- **Last Updated:** 2026-08-03

---

## 1. Entity란 무엇인가

운영체제를 만들 때는 먼저 Process, Thread, Memory 같은 핵심 개념을 하나씩 정의한다.

Intent OS도 같은 방식을 따른다. 시스템 안에 **"존재하는 것(Entity)"** 을 먼저 정의하고, 그 위에서 동작하는 Process와 Runtime State를 분리한다.

### Entity / Process / Runtime State 구분

초안에서는 Entity를 10개 정도로 잡았으나, **계층(Layer)이 섞여 있었다.**

예를 들어,

- **Execution**은 "실행 과정"이다 → Entity가 아니라 **Process**다.
- **Outcome**은 "실행 결과"다 → Entity가 아니라 **Runtime State**다.

| 분류 | 의미 | 예 |
|---|---|---|
| **Entity** | 시스템에 존재하는 것 | Goal, Task, Resource |
| **Process** | 시스템이 수행하는 것 | Execution, Learning, Prediction |
| **Runtime State** | 실행 중/후에 생기는 상태 | Outcome |

---

## 2. Core Entity 목록 (12개)

```
Goal
Intent
Context
Constraint
Task
Capability
Resource
Plan
Decision
Memory
Knowledge
Feedback
```

여기까지가 "존재하는 것(Entity)"이다.

- Execution은 Process다.
- Learning은 Process다.
- Prediction도 Process다.

---

## 3. 작성 원칙

Entity 명세는 PRD 수준이 아니라 **RFC / ISO 표준** 수준으로 작성한다.

목표는 다음과 같다.

> **개발자 여러 명이 각자 구현해도 같은 결과를 만드는 명세서**

이를 위해 각 Entity 명세는 다음을 포함하는 것을 지향한다.

- 형식 문법 (Formal Grammar)
- JSON Schema
- 생성 규칙
- 검증 알고리즘
- 추론 알고리즘
- 충돌 해결 규칙
- 계층 구조
- 우선순위 계산
- 변경 시 시스템 반응
- 실제 예시 다수

또한 진행 방식은 **Entity 하나를 운영체제 수준으로 완성한 뒤 다음 Entity로 넘어간다.** "Goal → Intent → Context…"를 얕게 훑는 것보다 장기적으로 더 좋은 설계다.

---

## 4. 명세 목차

| Entity | 이름 | 문서 | 상태 |
|---|---|---|---|
| 001 | Goal | [e001-goal.md](e001-goal.md) | v1.0 Draft |
| 001-A | Goal Graph | [e001a-goal-graph.md](e001a-goal-graph.md) | v1.0 Draft |
| 002 | Intent | — | 예정 |
| 003 | Context | — | 예정 |
| 004 | Constraint | — | 예정 |
| 005 | Task | — | 예정 |
| 006 | Capability | — | 예정 |
| 007 | Resource | — | 예정 |
| 008 | Plan | — | 예정 |
| 009 | Decision | — | 예정 |
| 010 | Memory | — | 예정 |
| 011 | Knowledge | — | 예정 |
| 012 | Feedback | — | 예정 |
