# Entity 001: Goal — Definition

- **Version:** v3.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 0. 문서 구조

Goal은 Intent OS 전체가 의존하는 가장 중요한 기반 객체다. 그래서 Goal Entity 하나를 여러 문서로 분리한다.

| 문서 | 내용 | 이 문서의 어느 절인가 |
|---|---|---|
| **e001-goal.md** (이 문서) | Goal이 무엇인가 | §1~§12 전체 |
| [e001b-goal-schema.md](e001b-goal-schema.md) | CGR v2 전체 필드 정의 | §8 Canonical Representation |
| [e001c-goal-state-machine.md](e001c-goal-state-machine.md) | 12개 상태, 상태별 Action, Guard | §6 Lifecycle |
| [e001d-goal-validation.md](e001d-goal-validation.md) | 검증 파이프라인, Completeness, Confidence | §9 Validation Rules |

Goal 간의 관계는 별도 구조 문서로 정의한다 → **[Entity 001-A: Goal Graph](e001a-goal-graph.md)**

> 세 개의 절 확장 문서(001-B/C/D)에는 12개 섹션 형식이 적용되지 않는다. 이들은 **그 자체가 이 문서의 한 절**이기 때문이다([e000b §2](e000b-entity-registry.md)).

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

Goal은 정적인 데이터가 아니라 상태(State)를 가지고 살아가는 객체다. 각 상태에서 가능한 행동(Action)이 달라진다 → [Goal State Machine](e001c-goal-state-machine.md).

### 1.1 Goal이 시스템의 시작점인 이유

Intent OS의 가장 중요한 규칙은 다음과 같다.

> **Never choose an AI before understanding the Goal.**

Goal이 없으면 [Intent](e002-intent.md)를 추론할 수 없고, Intent가 없으면 [Task](e005-task.md)를 만들 수 없고, Task가 없으면 [Capability](e006-capability.md)를 정할 수 없고, Capability가 없으면 [Resource](e007-resource.md)를 고를 수 없다.

**모든 Task는 참조 사슬을 따라가면 Goal에 도달해야 한다**([INV-01](e000a-entity-relationships.md)). 도달하지 못하는 실행은 비용만 쓰고 학습 신호를 만들지 못한다.

---

## 2. Goal은 무엇이 아닌가?

이게 정의보다 훨씬 중요하다.

### Goal은 Task가 아니다

❌ `인스타그램 광고 돌리기` — 이건 [Task](e005-task.md)다.

```
Goal:  학생 100명 모집          (상태)
Task:  인스타그램 광고 집행      (행위)
```

판별 질문: **"이것이 없어도 다른 방법으로 원하는 상태에 도달할 수 있는가?"** — 가능하면 Task다.

### Goal은 Intent가 아니다

❌ `홍보 강화를 통한 신규 등록 증가` — 이건 [Intent](e002-intent.md)다.

| | Goal | Intent |
|---|---|---|
| 담는 것 | 원하는 미래 상태 | 해결의 방향과 이유 |
| 출처 | **사용자가 확정한다** | 시스템이 추론한다 |
| Confidence | 사용자 선언이면 불필요 | **항상 필요** |
| 개수 | 하나 | Goal 하나에 여럿 |

### Goal은 Solution이 아니다

❌ `GPT 써서 글쓰기` — 방법이다.

### Goal은 Tool이 아니다

❌ `Figma 사용하기` — 도구다. [Tool](e024-tool.md) Entity의 영역이다.

### Goal은 Prompt가 아니다

❌ `블로그 글 써줘` — 사용자의 입력 문장, 즉 **Request**다(§9.2).

### Goal은 Constraint가 아니다

❌ `광고 예산 300만원 이하` — 이건 [Constraint](e004-constraint.md)다.

판별 질문: **"이것을 더 잘하면 좋은가, 아니면 지키기만 하면 되는가?"**

- 더 잘하면 좋다 → Goal (`광고 비용 20% 절감` = Optimization Goal)
- 지키기만 하면 된다 → Constraint (`예산 300만원 이하`)

### Goal은 Session이 아니다

❌ `오늘 대표가 시스템을 쓴 작업 단위` — 이건 [Session](e021-session.md)이다.

**Goal은 Session보다 오래 산다.** 하나의 Goal이 5개월에 걸쳐 여러 Session에서 추진된다([e021 §10 예시 1](e021-session.md)).

---

## 3. Design Principles

> **v2.0 정정:** v2.0에는 §3의 `Goal Rule 1~5`와 §10의 `Rule G-001~005`가 **같은 내용을 다른 번호로** 중복 정의하고 있었다. v3.0에서 `Rule G-001~007`로 통합했다.

### Rule G-001 — 미래 상태(Desired State)를 표현해야 한다

✅ `학생 100명 모집` / `매출 2배 증가` / `영어 회화 가능`

❌ `학생 모집 중` — 현재 상태다. 이건 [Context](e003-context.md)다.

### Rule G-002 — 방법(Method)을 포함해서는 안 된다

❌ `유튜브 광고해서 학생 모집`

Intent OS는 이를 자동 분리한다.

```
Goal:   학생 모집
Method: 유튜브 광고   → Intent 후보로 이관
```

방법을 Goal에 박으면 **더 나은 방법을 탐색할 기회를 잃는다.**

### Rule G-003 — Resource를 포함해서는 안 된다

❌ `GPT로 블로그 작성`

```
Goal:     블로그 게시
Resource: GPT   → Decision Engine의 후보로 이관
```

[INV-09](e000a-entity-relationships.md) Layer Isolation. Goal은 Resource를 모른다.

### Rule G-004 — Tool을 포함해서는 안 된다

❌ `Notion으로 정리하기` — [Tool](e024-tool.md)은 Resource의 부분집합이므로 Rule G-003의 연장이다.

### Rule G-005 — Task를 포함할 수 없다

❌ `블로그 작성하기` — 이건 Task다.

Intent OS는 사용자에게 질문한다.

> 블로그를 작성하는 궁극적인 목적이 무엇입니까?

### Rule G-006 — 성공 기준(Success Metric)이 존재해야 한다

`돈 많이 벌기`는 Goal이지만 측정할 수 없다. 시스템은 질문한다.

```
얼마를 의미합니까?
언제까지입니까?
```

**Metric이 없으면 [Systemic Feedback](e012-feedback.md)이 생성되지 않는다**([e012 §4.1](e012-feedback.md)). 즉, 시스템이 스스로 성패를 알 수 없다.

### Rule G-007 — Owner가 정확히 한 명이어야 한다

`stakeholders.owner`는 단수다. 주인이 둘이면 승인 요청을 어디로 보낼지, 완화 협상을 누구와 할지 결정할 수 없다([Constraint Rule CN-005](e004-constraint.md)).

---

## 4. Attributes

Goal은 아홉 개의 속성 그룹을 가진다. 각 필드의 정확한 정의는 [Goal JSON Schema](e001b-goal-schema.md)에 있다.

```
Goal
├── Identity        (goal_id, version, title, goal_type)
├── Objective       (description, desired_state, secondary_metrics)
├── Motivation      (왜 원하는가 — 전략이 달라진다)
├── Constraints     (constraint_ids → Entity 004)
├── Priority        (level, weight, factors, computed_score)
├── Context         (context_ref → Entity 003, assumption_ids → Entity 017)
├── Stakeholders    (Owner 정확히 1명 + Sponsor/Approver/Contributor/Affected)
├── Relationships   (parent_goal, child_goals, dependencies, related_goals)
├── Status          (phase, progress — State Machine이 관리)
├── Quality         (confidence, completeness, completeness_level)
└── Metadata        (created_by, source, history — 출처와 변경 이력)
```

**Motivation은 의외로 굉장히 중요하다.** 같은 `학생 100명 모집`이라도 동기가 다르면 전략이 달라진다.

| Motivation | 달라지는 전략 |
|---|---|
| 신규 개원, 인지도 확보가 급함 | 도달 우선. 할인 공격적 |
| 기존 학원, 재등록률 유지가 목적 | 브랜드 톤 유지. 할인 회피 |
| 투자 유치용 지표 | 단기 숫자 우선. 장기 LTV 후순위 |

> **v3.0 필드 변경:** `constraints`와 `context`가 인라인 값에서 **Entity 참조**로 바뀌었다. [Constraint](e004-constraint.md)·[Context](e003-context.md)·[Assumption](e017-assumption.md)이 독립 Entity가 되었기 때문이다. 인라인 문자열로는 검증 주기도 완화 이력도 담을 수 없다.

### 4.1 Goal Types

모든 Goal은 하나 이상의 Goal Type을 가진다. Type을 정의하면 Planner와 Decision Engine이 훨씬 정확하게 동작한다.

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

| Type | 예시 | 성공 판정 방식 |
|---|---|---|
| **Outcome** | `학생 100명 모집` | 목표치 도달 여부 |
| **Optimization** | `광고 비용 20% 절감` | 기준선 대비 개선폭 |
| **Learning** | `영어 회화 실력 향상` | 사전/사후 측정 |
| **Exploration** | `새로운 사업 아이디어 탐색` | 산출물의 다양성·질 |
| **Maintenance** | `서버 가동률 99.9% 유지` | 위반 횟수 |
| **Creation** | `브랜드 아이덴티티 제작` | 산출물 완성·채택 |
| **Decision** | `최적의 CRM 선택` | 결정 도달 여부 |
| **Automation** | `주간 보고서 자동 생성` | 반복 성공률 |

**Type이 [Evaluation](e015-evaluation.md)의 가중치를 결정한다.** Exploration Goal에서 `efficiency`를 높게 잡으면 탐색 자체가 억제된다.

### 4.2 Goal Expression Patterns

Goal은 자연어에서 다음 형태로 표현된다.

| Pattern | 형태 | 예 |
|---|---|---|
| A | `<Verb> + <Object>` | `학생 모집` |
| B | `<Desired State>` | `매출이 2배가 되기` |
| C | `<Metric> + <Desired State>` | `100명의 신규 회원 확보` |
| D | `<Time> + <Desired State>` | `3개월 안에 앱 출시` |
| E | `<Metric> + <Time> + <Desired State>` | `6개월 안에 MAU 5만 달성` |

Pattern A와 B는 Rule G-006(성공 기준)을 만족하지 못하므로 **Clarification 질문이 생성된다**([e001d](e001d-goal-validation.md)).

---

## 5. Invariants

### INV-G-01 — 모든 Task는 참조 사슬로 Goal에 도달한다

[INV-01](e000a-entity-relationships.md) Goal Reachability의 Goal 측 표현이다.

| | |
|---|---|
| **위반 시** | 고아 Task를 `Orphaned`로 격리하고 실행하지 않는다 |
| **탐지** | Task 생성 시 + 일 1회 Graph 스캔 |

### INV-G-02 — Goal에 Resource / Tool 식별자가 등장할 수 없다

| | |
|---|---|
| **위반 시** | Validation이 검출해 분리한다 (Rule G-003, G-004). 분리 불가면 Clarification |
| **근거** | [INV-09](e000a-entity-relationships.md) Layer Isolation |

### INV-G-03 — Owner는 정확히 한 명이다

| | |
|---|---|
| **위반 시** | 생성 거부. 승인 요청과 완화 협상의 수신처가 모호해진다 (Rule G-007) |

### INV-G-04 — Goal당 Active Plan은 최대 1개다

[INV-14](e000a-entity-relationships.md)의 Goal 측 표현이다.

| | |
|---|---|
| **위반 시** | 가장 최근 버전만 남기고 나머지를 `Superseded`로 전이 ([INV-P-01](e008-plan.md)) |

### INV-G-05 — Completed Goal은 수정되지 않는다

| | |
|---|---|
| **위반 시** | 쓰기 거부. 완료된 목표의 목표치를 사후에 낮추면 성과 평가가 무의미해진다 |
| **변경이 필요하면** | 새 Goal을 만들고 `related_goals`로 연결한다 |

### INV-G-06 — Goal Graph는 순환하지 않는다

| | |
|---|---|
| **위반 시** | 간선 추가를 롤백한다 ([INV-08](e000a-entity-relationships.md), [e001a §5](e001a-goal-graph.md)) |
| **근거** | 순환은 Planner를 무한 루프에 빠뜨린다 |

### INV-G-07 — Invalidated Assumption을 가진 Goal의 Plan은 Active일 수 없다

| | |
|---|---|
| **위반 시** | Plan을 `Suspended`로 전이하고 Replanning을 트리거 ([INV-10](e000a-entity-relationships.md)) |

### INV-G-08 — Goal은 Session보다 오래 산다

| | |
|---|---|
| **위반 시** | Session 종료 시의 Goal 삭제를 차단한다 ([INV-16](e000a-entity-relationships.md)) |

---

## 6. Lifecycle

Goal은 살아있는 객체이며 다음 생명주기를 가진다.

```
Created → Clarified → Structured → Executable
   → Planning → Executing → Monitoring
   → Completed → Archived
```

예외 경로로 `Failed`, `Suspended`, `Abandoned`가 있다.

각 상태의 정의, 상태별 허용 행동, 전이 조건(Guard)은 일반 JSON Schema가 아니라 **State Machine Specification**으로 별도 정의한다.

→ **[Entity 001-C: Goal State Machine](e001c-goal-state-machine.md)** / [`goal-state-machine.json`](../intent-os-spec/schemas/goal-state-machine.json)

### 6.1 Goal이 멈추는 두 가지 방식

| | Suspended | Abandoned |
|---|---|---|
| 의미 | 일시 중지. 재개 가능 | 포기. 재개하지 않는다 |
| 트리거 | 가정 무효화, 예산 소진, 사용자 보류 | 사용자 철회, 전제 소멸 |
| Plan | `Suspended` | `Aborted` |
| 진행 중 Execution | 완료 대기 또는 Abort | Abort |
| 이력 | 보존 | 보존 |

**둘 다 기록은 남는다.** 포기한 목표도 "왜 포기했는가"가 다음 Planning의 입력이다.

---

## 7. Relationships

```
Session 021 ─참조─▶ Goal 001 ─▶ Intent 002 ─▶ Task 005 ─▶ Capability 006 ─▶ Resource 007
                      │  │ (Goal Graph 001-A)
                      │  └──▶ Plan 008 ──▶ Decision 009 ──▶ Execution 013 ──▶ Outcome 014
                      │
     Context 003 ─────┤ 현재값 (Gap 계산)
     Constraint 004 ──┤ 제약
     Assumption 017 ──┤ 전제
     Risk 018 ────────┘ 위험
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Goal Graph](e001a-goal-graph.md) | Goal 간 관계 구조 | `Goal N:M Goal` (DAG) |
| [Intent](e002-intent.md) | Goal 하나에서 여러 Intent가 추론된다 | `Goal 1:1..N Intent` |
| [Context](e003-context.md) | Gap 계산의 현재값을 제공 | `Context N:M Goal` |
| [Constraint](e004-constraint.md) | Goal에 부착되며 하위 Goal로 상속된다 | `Goal 1:0..N Constraint` |
| [Task](e005-task.md) | Task는 정확히 하나의 Goal에 기여한다 | `Goal 1:1..N Task` |
| [Plan](e008-plan.md) | Goal당 Active Plan은 1개 (INV-G-04) | `Goal 1:0..N Plan` |
| [Decision](e009-decision.md) | 모든 Decision은 subject를 따라 Goal에 도달한다 | `Goal 1:0..N Decision` |
| [Assumption](e017-assumption.md) | Goal이 전제하는 가정 | `Goal 1:0..N Assumption` |
| [Risk](e018-risk.md) | Goal 수준의 위험 | `Goal 1:0..N Risk` |
| [Outcome](e014-outcome.md) | `goal_progress`로 지표 델타가 귀속된다 | `Goal 1:0..N Outcome` |
| [Evaluation](e015-evaluation.md) | `goal_alignment`의 판정 기준 | `Goal 1:0..N Evaluation` |
| [Feedback](e012-feedback.md) | Systemic Feedback의 기준은 Goal의 Metric | `Goal 1:0..N Feedback` |
| [Session](e021-session.md) | Session은 Goal을 **참조만** 한다 (INV-G-08) | `Session N:M Goal` |
| [Knowledge](e011-knowledge.md) | Domain/User Knowledge가 Clarification 질문을 줄인다 | `Knowledge N:M Goal` |

### 7.1 Goal / Intent / Task 판별표

| 문장 | 판정 | 근거 |
|---|---|---|
| `학생 100명 모집` | **Goal** | 미래 상태 |
| `홍보 강화를 통한 신규 등록 증가` | **Intent** | 해결 방향 |
| `인스타그램 광고 소재 3종 제작` | **Task** | 실행 단위 |
| `광고 예산 300만원 이하` | **Constraint** | 지키기만 하면 되는 경계 |
| `광고 비용 20% 절감` | **Goal** (Optimization) | 더 잘하면 좋은 것 |
| `현재 등록자 20명` | **Context** | 현재 상태 |
| `광고비가 유지될 것이다` | **Assumption** | 미래에 대한 믿음 |

---

## 8. Canonical Representation

모든 Goal은 내부적으로 동일한 구조를 가진다. **이 구조만 Runtime으로 전달된다.**

최소 형태:

```json
{
  "goal_id": "goal_001",
  "version": 1,
  "title": "2027 윈터캠프 학생 모집",
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

Entity 참조를 포함한 형태:

```json
{
  "goal_id": "goal_001",
  "version": 3,
  "title": "2027 윈터캠프 학생 모집",
  "goal_type": "Outcome",
  "objective": {
    "description": "2026년 11월 30일까지 윈터캠프 학생 100명 모집",
    "desired_state": {
      "metric": "registered_students",
      "operator": ">=",
      "target": 100,
      "unit": "students"
    }
  },
  "motivation": "개원 6개월 신규 학원. 첫 시즌 실적이 이후 인지도를 좌우한다",
  "constraint_ids": ["cn_003", "cn_005", "cn_001"],
  "context_ref": "ctx_001",
  "assumption_ids": ["asm_012", "asm_020", "asm_031"],
  "risk_ids": ["rsk_007"],
  "priority": { "level": "High", "computed_score": 0.88 },
  "stakeholders": {
    "owner": "human:대표",
    "contributors": ["human:copywriter_kim"]
  },
  "relationships": {
    "parent_goal": null,
    "child_goals": ["goal_004", "goal_005"],
    "dependencies": [],
    "related_goals": []
  },
  "status": { "phase": "Executing", "progress": 0.63 },
  "quality": { "confidence": 0.93, "completeness": 0.91, "completeness_level": "Executable" },
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

## 9. Validation Rules

Goal Engine은 Goal을 받으면 검증한다. **Goal이 불완전하면 바로 실행하지 않는다.**

```
Request / Goal 후보
  ↓
Syntactic Validation — Formal Grammar (§9.1)
  ↓
Semantic Validation — Rule G-001 ~ G-007
  ├── 현재 상태 서술 검출 (G-001)      → Context로 이관
  ├── Method 검출 (G-002)             → Intent 후보로 분리
  ├── Resource/Tool 검출 (G-003, 004) → Decision 후보로 분리 (INV-G-02)
  ├── Task 검출 (G-005)               → "궁극적 목적" 질문 생성
  ├── Metric 부재 (G-006)             → Clarification 질문 생성
  └── Owner 부재 (G-007)              → 요청자를 Owner로 설정 (INV-G-03)
  ↓
Completeness Score 계산     → e001d §4
  ↓
Confidence 산출             → e001d §5
  ↓
Question Generation         → e001d §6
  Expected Information Gain > User Friction 인 질문만
  ↓
Goal Graph 순환 검사 (INV-G-06) → e001a
  ↓
Confirmed Goal → Intent 추출 (e002 §9)
```

검증 알고리즘, Completeness Score, Confidence 산출의 상세는 → **[Entity 001-D: Goal Validation Rules](e001d-goal-validation.md)**

### 9.1 Formal Grammar

Formal Grammar는 "문장을 예쁘게 쓰는 규칙"이 아니다.

> **Goal이 무엇이고 무엇이 Goal이 아닌지를 컴퓨터가 판단할 수 있도록 정의하는 문법**이다.

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

이 문법은 **Goal이 반드시 DesiredState를 포함해야 함**을 강제한다. 목적은 다섯 가지다.

1. Goal과 Task를 구분한다.
2. Goal과 Solution을 구분한다.
3. Goal을 구조화된 객체로 변환한다.
4. Goal Validation의 기준을 제공한다.
5. Planner와 Decision Engine이 동일한 입력 형식을 쓰도록 보장한다.

### 9.2 Goal ≠ User Request

사용자가 입력하는 문장은 대부분 Goal이 아니다.

```
Request:  "홍보 문구 하나 만들어줘"
   ↓ Goal Extraction
Goal:     "윈터캠프 학생 100명 모집"
   ↓
Intent:   "홍보 도달 확대"
   ↓
Task:     "인스타그램 광고 카피 3종 작성"
```

추론으로 생성된 Goal은 `metadata.source = "inference"`로 기록되며, `quality.confidence`가 특히 중요하다. **사용자가 확정하지 않은 Goal 위에 세운 계획은 방향 자체가 틀릴 수 있다.**

---

## 10. Examples

### 10.1 예시 1 — Request에서 Goal까지

```
사용자: "홍보 문구 하나 만들어줘"
   ↓ Syntactic Validation
DesiredState 없음 → Goal이 아니다 (Request)
   ↓ Goal Extraction + Clarification
Q: "이 홍보로 궁극적으로 무엇을 이루고 싶으신가요?"
A: "겨울 캠프에 학생을 채우고 싶어요"
Q: "몇 명을, 언제까지입니까?"
A: "100명, 11월 말까지요"
   ↓
goal_001  "2026년 11월 30일까지 윈터캠프 학생 100명 모집"
          metric: registered_students >= 100
          confidence 0.93 (사용자 확인 거침)
```

**질문 2개로 Goal이 완성되었다.** [Expected Information Gain > User Friction](e001d-goal-validation.md) 기준에 따라 그 이상 묻지 않는다.

### 10.2 예시 2 — Method가 섞인 Goal의 분리

```
사용자: "유튜브 광고로 학생 100명 모으고 싶어"
   ↓ Rule G-002
Goal:   학생 100명 모집
Method: 유튜브 광고
   ↓
Method는 Intent 후보로 이관
intent_00X  Promotion  "영상 채널을 통한 도달 확대"  confidence 0.7
   ↓
Intent 추출 단계에서 다른 후보와 경쟁
intent_001  Promotion  "인스타그램 중심 도달 확대"   confidence 0.85  ← 선택
```

사용자가 말한 방법이 **버려지지 않고 후보로 남는다.** 그러나 자동으로 채택되지도 않는다 — 더 나은 방법이 있을 수 있다.

### 10.3 예시 3 — Optimization Goal vs Constraint

같은 "비용"을 두고 두 가지가 가능하다.

```
"광고 예산 300만원 이하로 해줘"
   ↓ 판별 질문: 더 잘하면 좋은가?
   ↓ No — 지키기만 하면 된다
cn_003 (Constraint, Hard)  total_ad_spend <= 3000000

"광고 비용을 20% 줄이고 싶어"
   ↓ 판별 질문: 더 잘하면 좋은가?
   ↓ Yes — 25% 줄이면 더 좋다
goal_007 (Optimization Goal)  ad_cost_reduction >= 0.20
```

**두 문장은 비슷하게 들리지만 시스템의 처리가 완전히 다르다.** Constraint는 필터, Goal은 최적화 대상이다.

### 10.4 예시 4 — Goal 계층

```
goal_001  윈터캠프 학생 100명 모집          (parent)
├── goal_004  랜딩페이지 전환율 3% 달성      (child)
└── goal_005  월 상담 문의 40건 확보         (child)
```

하위 Goal의 달성이 상위 Goal에 기여하지만 **자동으로 상위를 완료시키지 않는다.** 전환율 3%와 문의 40건을 달성해도 등록이 100명이 안 될 수 있다. Propagation 규칙은 [e001a §14](e001a-goal-graph.md)가 정의한다.

### 10.5 예시 5 — Motivation이 전략을 바꾼다

같은 Goal, 다른 Motivation.

```
goal_001  학생 100명 모집
motivation: "개원 6개월 신규 학원. 첫 시즌 실적이 이후 인지도를 좌우"
   ↓ Intent 추출
intent_001  Promotion (도달 확대)     conf 0.85  ← 선택
intent_002  Pricing (조기 할인)       conf 0.72  ← 선택 (공격적 할인 허용)
```

```
goal_001'  학생 100명 모집
motivation: "10년차 학원. 브랜드 프리미엄 유지가 장기 수익의 핵심"
   ↓ Intent 추출
intent_001  Promotion (도달 확대)     conf 0.85  ← 선택
intent_002  Pricing (조기 할인)       conf 0.72  → Rejected
            rejection_reason: "브랜드 프리미엄 훼손. motivation과 충돌"
```

**Motivation 없이는 이 판단이 불가능하다.**

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **Goal이 너무 모호함** (`잘하고 싶다`) | Clarification 질문을 생성하고 `Created`에 머문다. 추측으로 채우지 않는다 — 틀린 Goal 위의 모든 실행이 낭비다 |
| **사용자가 질문에 답하지 않음** | `Created` 유지. 부분 정보로 진행하려면 `quality.confidence`를 크게 낮추고 그 사실을 명시한다 |
| **Goal이 실행 중에 바뀜** | 새 `version`을 만든다. 이전 버전은 보존한다. 진행 중 Plan은 [Replanning](e008-plan.md) 대상이 된다 |
| **하위 Goal이 전부 완료됐는데 상위가 미달** | 정상이다(§10.4). 하위 달성이 상위를 보장하지 않는다. 이 괴리 자체가 Goal 분해가 잘못됐다는 학습 신호다 |
| **두 Goal이 충돌** (`가격 인하` ↔ `브랜드 프리미엄`) | `related_goals[].relationship = CONFLICTS_WITH`로 표현한다. 해소는 [Goal Graph](e001a-goal-graph.md)의 소관이며 사용자 판단이 필요하다 |
| **Metric은 있는데 측정 수단이 없음** | Rule G-006은 만족하지만 [Systemic Feedback](e012-feedback.md)이 생성되지 않는다. Goal 생성 시 측정 수단 확보 여부를 함께 확인한다 |
| **Owner가 퇴사/부재** | Goal을 무주공산으로 두지 않는다. 조직 기본 Owner로 승계하고 알림을 발행한다([Risk §11](e018-risk.md)과 같은 원칙) |
| **Completed Goal의 목표치를 사후 수정 요청** | 거부한다(INV-G-05). 새 Goal을 만들고 `related_goals`로 연결한다 |
| **Goal 없이 Task를 만들려는 시도** | 거부한다(INV-G-01). 시스템 내부 작업도 `system` Goal에 귀속시킨다 — 그래야 모든 비용이 집계된다 |
| **추론된 Goal(source: inference)이 틀림** | 사용자가 정정하면 새 version을 만들고 `metadata.source`를 `user_confirmed`로 바꾼다. 오판 이력은 Goal Extraction 정확도 개선의 입력이다 |

---

## 12. Open Issues (v3.0)

### ✅ 해소된 항목

| Open Issue | 해소 |
|---|---|
| Goal 계층 구조 | `parent_goal` / `child_goals` + [Entity 001-A](e001a-goal-graph.md) |
| Goal 간 의존성 | `dependencies` / `related_goals` |
| Goal 소유자 | `stakeholders.owner` (정확히 1명, INV-G-03) |
| Goal 생성 출처 / 변경 이력 / 버전 / 신뢰도 | `metadata.source`, `metadata.history`, `version`, `quality.confidence` |
| Goal 충돌 표현 | `related_goals[].relationship = CONFLICTS_WITH` |
| Goal 우선순위 계산 정보 | `priority.factors` / `computed_score` |
| Goal 변경 시 시스템 반응 | [State Machine](e001c-goal-state-machine.md) + [Goal Propagation](e001a-goal-graph.md) |
| Rule 번호 중복 (§3 vs §10) | v3.0에서 `Rule G-001~007`로 통합 |
| Constraint / Context / Assumption의 인라인 저장 | Entity 참조로 전환 (§4) |

### Goal 추론(Extraction) 알고리즘

`Request → Goal` 변환의 상세 명세가 없다. §10.1의 예시는 흐름만 보여줄 뿐이며, "어떤 Request에서 어떤 Goal 후보를 만드는가"의 규칙이 정의되지 않았다. [Intent Extraction](e002-intent.md)과 같은 수준의 알고리즘 서술이 필요하다.

### Goal 충돌 해소 전략

`CONFLICTS_WITH`로 **표현**은 가능하지만 **해소**는 사용자 판단에 맡긴다. [Constraint의 Infeasible 절차](e004-constraint.md)처럼 트레이드오프를 제시하는 절차가 필요하다.

### Goal 병합/분할의 의미론

두 Goal을 합치거나 하나를 나눌 때 하위 Task·Plan·Memory의 귀속이 어떻게 되는가. [Task Graph의 Graph Diff](e005a-task-graph.md)와 유사한 규칙이 필요하다.

### 측정 수단의 확보 확인

Rule G-006은 Metric의 **존재**만 요구한다. 그 Metric을 실제로 측정할 [Tool](e024-tool.md)이 있는지는 검사하지 않는다(§11). Goal 생성 시점에 확인하지 않으면 실행이 끝난 뒤에야 성패를 알 수 없다는 것을 발견한다.

### 앞으로 보강해야 할 항목

- Goal Extraction 알고리즘 명세
- Goal 충돌 해소 절차 (트레이드오프 제시)
- Goal 병합/분할 연산의 의미론
- 실제 예시 30~50개
