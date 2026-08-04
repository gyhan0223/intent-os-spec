# Entity 001-D: Goal Validation Rules

- **Version:** v2.0 Draft
- **Status:** Core Entity
- **Format:** Annex — e001 Goal의 부속 문서 (e000 §7.1)
- **Last Updated:** 2026-08-04
- **Schema:** [`goal.schema.json`](../intent-os-spec/schemas/goal.schema.json) — 이 문서의 규칙이 검사하는 대상

---

## 1. Purpose

Goal Engine은 Goal을 받으면 반드시 검증한다. **Goal이 불완전하면 바로 실행하지 않는다.**

검증의 출력은 세 가지다.

1. **판정** — 이 입력이 Goal인가, 아닌가 (Task/Solution/Prompt 거부)
2. **점수** — Completeness Score (0~100), Confidence (0~1)
3. **질문** — 부족한 정보를 채우기 위한 Question Generation

검증 결과는 [State Machine](e001c-goal-state-machine.md)의 Guard 조건으로 사용된다. 검증을 통과하지 못한 Goal은 다음 상태로 전이할 수 없다.

---

## 2. Validation Pipeline

```
Input
  ↓
1. Structural Validation      — goal.schema.json 검증
  ↓
2. Semantic Validation        — Rule G-001 ~ G-005
  ↓
3. Ownership Validation       — Rule V-OWNER
  ↓
4. Relationship Validation    — Rule V-GRAPH, V-CYCLE, V-CONFLICT
  ↓
5. Completeness Scoring       — 0~100점
  ↓
6. Confidence Estimation      — 0~1
  ↓
7. Question Generation        — 부족한 정보 → 질문
  ↓
Goal Confirmation → Canonical Goal 확정
```

---

## 3. Validation Rules

### 3.1 Structural Rules (스키마 수준)

| Rule | 내용 | 위반 시 |
|---|---|---|
| V-SCHEMA | [`goal.schema.json`](../intent-os-spec/schemas/goal.schema.json)을 통과해야 한다 | 거부 |
| V-ID | `goal_id`는 전역에서 유일해야 한다 | 거부 |
| V-VERSION | `version`은 이전 버전보다 정확히 1 커야 한다 | 거부 |
| V-HISTORY | `version` ≥ 2인 Goal은 `metadata.history`가 버전 수만큼 있어야 한다 | 경고 |

### 3.2 Semantic Rules (의미 수준)

[e001-goal.md §10](e001-goal.md)에 정의된 규칙을 실행한다.

| Rule | 내용 | 위반 시 |
|---|---|---|
| G-001 | 미래 상태(Future State)를 표현해야 한다 | 거부 또는 질문 |
| G-002 | 방법(Method)을 포함하면 안 된다 | Goal/Method 자동 분리 |
| G-003 | Resource를 포함하면 안 된다 | Goal/Resource 자동 분리 |
| G-004 | Task를 포함할 수 없다 | 상위 목적 질문 |
| G-005 | 성공 기준이 존재해야 한다 | 질문 (얼마? 언제까지?) |

### 3.3 Ownership Rule

| Rule | 내용 | 위반 시 |
|---|---|---|
| V-OWNER | `stakeholders`에 `role: "Owner"`가 **정확히 1명** 있어야 한다 | Executable 전이 차단 |

소유자 없는 Goal은 책임 주체가 없으므로 시스템이 실행 결정을 내릴 수 없다. 소유자가 2명 이상이면 충돌 해소의 최종 결정권자가 모호해진다.

### 3.4 Relationship Rules

| Rule | 내용 | 위반 시 |
|---|---|---|
| V-GRAPH | 모든 Goal은 `parent_goal` 또는 Root Goal과 연결되어야 한다 (Invariant 2) | Executable 전이 차단 |
| V-CYCLE | `dependencies`가 순환을 만들면 안 된다 (Invariant 1) | 거부 |
| V-CONFLICT | 미해소 `CONFLICTS_WITH` (`resolution: null`)가 있으면 안 된다 | Executable 전이 차단 |
| V-DANGLING | `parent_goal`, `dependencies[].goal_id` 등이 존재하는 Goal을 가리켜야 한다 | 거부 |
| V-GG-SYNC | Goal의 로컬 관계 필드는 Goal Graph edges와 일치해야 한다. 불일치 시 Graph가 정본 | 자동 동기화 |

---

## 4. Goal Completeness Score

Goal의 완성도를 점수화한다 (`quality.completeness`, 0~100).

| 항목 | 가중치 | v2 기준 필드 | 만점 조건 |
|---|--:|---|---|
| Objective | 25% | `objective.description` | G-001~G-004 통과하는 서술 존재 |
| Success Metric | 20% | `objective.desired_state` | metric + operator + target 모두 존재 |
| Deadline | 15% | `constraints.deadline` | 유효한 미래 날짜 |
| Constraints | 15% | `constraints.*` | budget 등 1개 이상의 실질 제약 |
| Context | 10% | `context.current_state` | desired_state.metric에 대응하는 현재 값 존재 |
| Stakeholders | 10% | `stakeholders` | Owner 1명 + 영향 주체 식별 |
| Priority | 5% | `priority.level` 또는 `weight` | 지정됨 |

예)

- `학생 모집` → 약 **25/100점** (Objective만 존재)
- `2026년 11월까지 홍대 지역 예비 고3 학생 100명 모집. 예산은 300만원 이하.` → **80~90점**

### Completeness Level

| Level | 이름 | 조건 | 의미 |
|---|---|---|---|
| 1 | Raw Goal | score < 60 | 정보 부족. Clarification 필요 |
| 2 | Structured Goal | 60 ≤ score < 80 | Planner 실행 가능하나 미검증 |
| 3 | Executable Goal | score ≥ 80 + 전체 Validation 통과 | 즉시 Planning 시작 가능 |

Level은 State Machine의 Guard와 연동된다: Clarified→Structured는 score ≥ 60, Structured→Executable은 score ≥ 80을 요구한다.

---

## 5. Confidence Estimation

`quality.confidence` (0~1)는 Completeness와 다르다.

- **Completeness** — Goal에 정보가 얼마나 채워져 있는가
- **Confidence** — 이 Goal이 **사용자의 실제 의도를 정확히 반영하는가**

정보가 완벽하게 채워진 Goal도 사용자가 원한 것이 아닐 수 있다.

Confidence를 낮추는 요인:

| 요인 | 예 |
|---|---|
| `metadata.source = "inference"` | Request에서 추론된 Goal은 시작 confidence가 낮다 |
| Goal Extraction 중 모호한 표현 | "잘 되게 해줘" |
| 사용자 확인(Confirmation) 없음 | 추론 후 미확인 상태 |
| 잦은 역방향 전이 | Structured→Clarified 반복은 의도 파악 실패 신호 |

Confidence를 높이는 요인: 사용자의 명시적 확인, 질문-응답을 통한 보강, `source = "conversation"` 또는 `"api"`.

운영 규칙(권장): `confidence < 0.7`인 Goal은 Planning 진입 전에 사용자 확인을 요구한다.

---

## 6. Question Generation

검증에 실패하거나 점수가 부족하면, 시스템은 부족한 항목을 **질문으로 변환**한다.

| 부족한 항목 | 생성되는 질문 예 |
|---|---|
| `desired_state.target` | "얼마를 의미합니까?" |
| `constraints.deadline` | "언제까지 달성해야 합니까?" |
| `constraints.budget` | "사용 가능한 예산이 있습니까?" |
| Owner 부재 | "이 목표의 최종 책임자는 누구입니까?" |
| G-004 위반 (Task 입력) | "블로그를 작성하는 궁극적인 목적이 무엇입니까?" |
| 미해소 CONFLICTS_WITH | "A와 B가 충돌합니다. 무엇을 우선합니까?" |

질문 우선순위는 Completeness 가중치 순서를 따른다 — Objective를 명확히 하는 질문이 Priority를 묻는 질문보다 먼저 나간다.

---

## 7. Validation 실행 시점

| 시점 | 실행 범위 |
|---|---|
| Goal 생성 시 | 전체 파이프라인 |
| 필드 수정 시 (version 증가) | Structural + 영향받는 규칙 재검증, 필요 시 상태 롤백 (Executable→Structured) |
| 상태 전이 요청 시 | 해당 전이의 Guard |
| Goal Propagation 수신 시 | Relationship + Completeness 재계산 |
| 가정(assumption) 붕괴 감지 시 | Semantic + Completeness 재검증 |

---

## 8. Open Issues

- Completeness 가중치가 goal_type과 무관하게 고정되어 있다 — Maintenance Goal에는 Deadline 15%가 과도할 수 있다. 타입별 가중치 프로파일 필요
- Confidence의 정량적 산출식 미정의 — 현재는 요인 목록 수준
- Method/Resource/Task 자동 분리(G-002~G-004)의 알고리즘 상세 명세 필요
- 충돌 해소(V-CONFLICT) 전략의 자동 제안 — 현재는 질문 생성까지만 정의
