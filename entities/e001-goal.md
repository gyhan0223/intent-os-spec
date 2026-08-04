# Entity 001: Goal — Definition

- **Version:** v2.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 0. 문서 구조

Goal은 Intent OS 전체가 의존하는 가장 중요한 기반 객체다. 그래서 Goal Entity 하나를 네 개의 문서로 분리한다.

| # | 문서 | 내용 | 파일 |
|---|---|---|---|
| 1 | **Goal Definition** | Goal이 무엇인가 (이 문서) | `e001-goal.md` |
| 2 | **Goal JSON Schema** | 데이터 구조 (CGR v2) | [e001b-goal-schema.md](e001b-goal-schema.md) |
| 3 | **Goal State Machine** | Goal의 생명주기 | [e001c-goal-state-machine.md](e001c-goal-state-machine.md) |
| 4 | **Goal Validation Rules** | 검증과 점수화 | [e001d-goal-validation.md](e001d-goal-validation.md) |

Goal 간의 관계는 별도 문서로 정의한다 → [Entity 001-A: Goal Graph](e001a-goal-graph.md)

기계가 읽을 수 있는 명세:

- [`goal.schema.json`](../intent-os-spec/schemas/goal.schema.json) — Canonical Goal Representation v2
- [`goal-state-machine.json`](../intent-os-spec/schemas/goal-state-machine.json) — State Machine Specification

---

## 1. Definition

### 공식 정의

> **Goal is a desired future state defined by a user or another intelligent agent.**

> Goal은 사용자 또는 다른 지능형 주체가 원하는 미래 상태이다.

여기서 중요한 단어는 **Future State**이다.

Goal은 현재가 아니라 **미래의 상태**를 의미한다.

그리고 v2에서 하나가 더 추가된다.

> **Goal is a living object, not a static record.**

Goal은 정적인 데이터가 아니라 상태(State)를 가지고 살아가는 객체다. 각 상태에서 가능한 행동(Action)이 달라진다. → [Goal State Machine](e001c-goal-state-machine.md)

---

## 2. Goal은 무엇이 아닌가?

이게 정의보다 훨씬 중요하다.

### Goal은 Task가 아니다

❌ `인스타그램 광고 돌리기` — 이건 Goal이 아니다. Task다.

### Goal은 Solution이 아니다

❌ `GPT 써서 글쓰기` — Goal이 아니다. 방법이다.

### Goal은 Tool이 아니다

❌ `Figma 사용하기` — Tool이다.

### Goal은 Prompt가 아니다

❌ `블로그 글 써줘` — Prompt일 뿐이다.

---

## 3. Goal의 조건

Goal은 반드시 아래 조건을 만족해야 한다.

### Goal Rule 1 — Desired State를 표현해야 한다

✅ `학생 100명 모집`

### Goal Rule 2 — 방법(Method)을 포함하면 안 된다

- 나쁜 예: `유튜브 광고해서 학생 모집`
- 좋은 예: `학생 모집`

### Goal Rule 3 — AI 이름이 들어가면 안 된다

❌ `Claude로 마케팅하기`

### Goal Rule 4 — Tool 이름이 들어가면 안 된다

❌ `Notion으로 정리하기`

### Goal Rule 5 — 측정 가능해야 한다

가능하면 Metric이 존재해야 한다.

- ✅ `신규 회원 100명`
- ⚠️ `잘하고 싶다` — 애매하다.

---

## 4. Goal Attributes (v2)

Goal은 아홉 개의 속성 그룹을 가진다. 각 필드의 정확한 정의는 [Goal JSON Schema](e001b-goal-schema.md)에 있다.

```
Goal
├── Identity        (goal_id, version, title, goal_type)
├── Objective       (description, desired_state, secondary_metrics)
├── Motivation      (왜 원하는가 — 전략이 달라진다)
├── Constraints     (budget, deadline, location, legal, resource_limits)
├── Priority        (level, weight, factors, computed_score)
├── Context         (current_state, environment, assumptions)
├── Stakeholders    (Owner 정확히 1명 + Sponsor/Approver/Contributor/Affected)
├── Relationships   (parent_goal, child_goals, dependencies, related_goals)
├── Status          (phase, progress — State Machine이 관리)
├── Quality         (confidence, completeness, completeness_level)
└── Metadata        (created_by, source, history — 출처와 변경 이력)
```

v1 대비 추가된 것: **계층 구조, 의존성, 소유자, 생성 출처, 변경 이력, 버전, 신뢰도, 충돌, 우선순위 계산 정보.** 이것들이 있어야 Goal이 운영체제 수준의 Entity가 된다.

Motivation은 의외로 굉장히 중요하다. **Motivation에 따라 전략이 달라진다.**

---

## 5. Goal Lifecycle

Goal은 살아있는 객체이며 다음 생명주기를 가진다.

```
Created → Clarified → Structured → Executable
   → Planning → Executing → Monitoring
   → Completed → Archived
```

예외 경로로 `Failed`, `Suspended`, `Abandoned`가 있다.

각 상태의 정의, 상태별 허용 행동, 전이 조건(Guard)은 일반 JSON Schema가 아니라 **State Machine Specification**으로 별도 정의한다.

→ **[Entity 001-C: Goal State Machine](e001c-goal-state-machine.md)** / [`goal-state-machine.json`](../intent-os-spec/schemas/goal-state-machine.json)

---

## 6. Goal Validation

Goal Engine은 Goal을 받으면 검증한다.

예)

사용자: `돈 많이 벌고 싶어`

검증 결과:

```
모호함
  ↓
질문 생성
  ↓
얼마? / 언제까지? / 어떤 방법 제약? / 위험 허용 범위?
```

즉, **Goal이 불완전하면 바로 실행하지 않는다.**

검증 알고리즘, Completeness Score, Confidence 산출은 별도 문서에 정의한다.

→ **[Entity 001-D: Goal Validation Rules](e001d-goal-validation.md)**

---

## 7. Goal ≠ User Request

사용자가 입력하는 문장은 대부분 Goal이 아니다.

예) `홍보 문구 하나 만들어줘.` — 이건 **Request**다.

시스템은 여기서 Goal을 추론해야 한다.

```
Request
   ↓
Goal Extraction
   ↓
Goal
   ↓
Planning
```

추론으로 생성된 Goal은 `metadata.source = "inference"`로 기록되며, 사용자의 실제 의도와 일치하는지에 대한 `quality.confidence`가 특히 중요하다.

---

## 8. Goal Types

실제 Intent OS에서 Goal은 종류가 있다. 모든 Goal은 하나 이상의 Goal Type을 가진다. Goal Type을 정의하면 Planner와 Decision Engine이 훨씬 더 정확하게 동작할 수 있다.

```
Goal
├── Outcome Goal
├── Optimization Goal
├── Learning Goal
├── Exploration Goal
├── Maintenance Goal
├── Creation Goal
├── Decision Goal
└── Automation Goal
```

| Type | 예시 |
|---|---|
| **Outcome Goal** | `학생 100명 모집` |
| **Learning Goal** | `영어 회화 실력 향상` |
| **Optimization Goal** | `광고 비용 20% 절감` |
| **Maintenance Goal** | `서버 가동률 99.9% 유지` |
| **Exploration Goal** | `새로운 사업 아이디어 탐색` |
| **Creation Goal** | `브랜드 아이덴티티 제작` |
| **Decision Goal** | `최적의 CRM 선택` |
| **Automation Goal** | `주간 보고서 자동 생성` |

---

## 9. Formal Grammar

### 9.1 Purpose

Formal Grammar는 "문장을 예쁘게 쓰는 규칙"이 아니다.

> **Goal이 무엇이고, 무엇이 Goal이 아닌지를 컴퓨터가 판단할 수 있도록 정의하는 문법**이다.

Intent OS는 사용자의 자연어를 받아 이 문법에 맞는 **Goal 객체**로 변환한다.

Goal Grammar는 사용자의 자연어를 **표준 Goal 표현(Standard Goal Representation, SGR)** 으로 변환하기 위한 형식 문법을 정의한다. 목적은 다음과 같다.

1. Goal과 Task를 구분한다.
2. Goal과 Solution을 구분한다.
3. Goal을 구조화된 객체로 변환한다.
4. Goal Validation의 기준을 제공한다.
5. Planner와 Decision Engine이 동일한 입력 형식을 사용하도록 보장한다.

### 9.2 Goal Grammar (EBNF)

```ebnf
Goal
    ::= DesiredState
        [ SuccessMetric ]
        [ TimeConstraint ]
        [ Constraints ]
        [ Context ]

DesiredState
    ::= Objective

Objective
    ::= Verb Phrase
      | State Description

SuccessMetric
    ::= Quantity
      | Percentage
      | Quality Measure

TimeConstraint
    ::= Deadline
      | Duration

Constraints
    ::= Constraint
      | Constraint Constraints

Context
    ::= Environment
      | UserProfile
      | CurrentState
```

이 문법은 **Goal이 반드시 "원하는 미래 상태(DesiredState)"를 포함해야 함**을 강제한다.

---

## 10. Semantic Rules

문법적으로 올바르다고 Goal이 되는 것은 아니다. Intent OS는 의미 규칙(Semantic Rules)도 검사한다. 이 규칙들은 [Goal Validation Rules](e001d-goal-validation.md)의 Semantic Validation 단계에서 실행된다.

### Rule G-001 — 미래 상태(Future State)를 표현해야 한다

✅ `학생 100명 모집` / `매출 2배 증가` / `영어 회화 가능`

❌ `학생 모집 중` — 현재 상태이므로 Goal이 아니다.

### Rule G-002 — 방법(Method)을 포함해서는 안 된다

❌ `유튜브 광고해서 학생 모집`

Intent OS는 이를 자동 분리해야 한다.

```
Goal:   학생 모집
Method: 유튜브 광고
```

### Rule G-003 — Resource를 포함해서는 안 된다

❌ `GPT로 블로그 작성`

분석 결과:

```
Goal:     블로그 게시
Resource: GPT
```

### Rule G-004 — Task를 포함할 수 없다

❌ `블로그 작성하기` — 이것은 Task다.

Intent OS는 사용자에게 질문한다.

> 블로그를 작성하는 궁극적인 목적이 무엇입니까?

### Rule G-005 — 성공 기준이 존재해야 한다

`돈 많이 벌기`는 Goal이지만 Success Metric이 없다.

Intent OS는 질문한다.

```
얼마를 의미합니까?
언제까지입니까?
```

---

## 11. Goal Expression Patterns

Goal은 자연어에서 다음 형태로 표현될 수 있다.

| Pattern | 형태 | 예 |
|---|---|---|
| A | `<Verb> + <Object>` | `학생 모집` |
| B | `<Desired State>` | `매출이 2배가 되기` |
| C | `<Metric> + <Desired State>` | `100명의 신규 회원 확보` |
| D | `<Time> + <Desired State>` | `3개월 안에 앱 출시` |
| E | `<Metric> + <Time> + <Desired State>` | `6개월 안에 MAU 5만 달성` |

---

## 12. Canonical Goal Representation (CGR v2)

모든 Goal은 내부적으로 동일한 구조를 가진다. **이 구조만 Runtime으로 전달된다.**

최소 형태의 예:

```json
{
  "goal_id": "goal_01HZX9M4Y4QF2X",
  "version": 1,
  "title": "2027 윈터스쿨 학생 모집",
  "goal_type": "Outcome",
  "objective": {
    "description": "학생 100명 모집",
    "desired_state": {
      "metric": "registered_students",
      "operator": ">=",
      "target": 100,
      "unit": "students"
    }
  },
  "status": { "phase": "Created" },
  "metadata": {
    "created_by": "user",
    "created_at": "2026-08-04T12:00:00Z",
    "source": "conversation"
  }
}
```

전체 필드 정의와 완전한 예시는 → **[Entity 001-B: Goal JSON Schema](e001b-goal-schema.md)**

기계가 읽을 수 있는 스키마: [`goal.schema.json`](../intent-os-spec/schemas/goal.schema.json)

---

## 13. Open Issues (v2.0)

v1.0의 Open Issue 중 다음은 v2에서 반영되었다.

- ~~Goal 계층 구조~~ → `parent_goal` / `child_goals` + Entity 001-A
- ~~Goal 간 의존성~~ → `dependencies` / `related_goals`
- ~~Goal 소유자~~ → `stakeholders` (Owner 정확히 1명)
- ~~Goal 생성 출처~~ → `metadata.source` / `origin_ref`
- ~~Goal 변경 이력~~ → `metadata.history`
- ~~Goal 버전~~ → `version`
- ~~Goal 신뢰도~~ → `quality.confidence`
- ~~Goal 충돌~~ → `related_goals[].relationship = CONFLICTS_WITH` + resolution
- ~~Goal 우선순위 계산 정보~~ → `priority.factors` / `computed_score`
- ~~Goal 변경 시 시스템 반응~~ → State Machine (e001c) + Goal Propagation (e001a §14)

앞으로 보강해야 할 항목:

- Goal 추론(Extraction/Inference) 알고리즘 — Request → Goal 변환의 상세 명세
- Goal 충돌 해소(Conflict Resolution) 전략의 상세 정의 — 현재는 표현만 가능
- Goal 병합(merge)/분할(split) 연산의 정확한 의미론
- 실제 예시 30~50개
