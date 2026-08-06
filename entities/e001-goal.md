# Entity 001: Goal — Definition

- **Version:** v2.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04
- **Schema:** [`goal.schema.json`](../intent-os-spec/schemas/goal.schema.json)

---

## 문서 구조

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

## 3. Design Principles

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

## 4. Attributes

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

### 4.1 Goal Types

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

### 4.2 Goal Expression Patterns

Goal은 자연어에서 다음 형태로 표현될 수 있다.

| Pattern | 형태 | 예 |
|---|---|---|
| A | `<Verb> + <Object>` | `학생 모집` |
| B | `<Desired State>` | `매출이 2배가 되기` |
| C | `<Metric> + <Desired State>` | `100명의 신규 회원 확보` |
| D | `<Time> + <Desired State>` | `3개월 안에 앱 출시` |
| E | `<Metric> + <Time> + <Desired State>` | `6개월 안에 MAU 5만 달성` |

---

## 5. Invariants

### INV-G-01 — 고립된 Goal은 존재하지 않는다

모든 Goal은 Goal Graph의 노드다. 부모도 자식도 관계도 없는 Goal은 우선순위 계산에도, 전파에도 참여하지 못한 채 조회만 가능한 잔여물이 된다. 그래프 차원의 정본은 [e001a](e001a-goal-graph.md)다.

| | |
|---|---|
| **위반 시** | `Executable`로 올리지 않는다. 최상위 Goal이면 root로 명시적으로 등록한다 — 고립과 root는 다르다 |
| **탐지** | 상태 전이 시점, 그래프 편집 시점 |

### INV-G-02 — Owner는 정확히 한 명이다

Owner가 없으면 아무도 결정하지 않고, 둘이면 상충하는 결정이 동시에 내려진다. Constraint 완화 승인과 Goal 폐기 권한이 여기 달려 있다.

| | |
|---|---|
| **위반 시** | `Executable` 진입을 차단하고 Owner 지정을 요청한다. 스키마 차원에서도 `minContains: 1, maxContains: 1`로 강제된다 |

### INV-G-03 — Goal에 Method·Resource·Tool 이름이 없다

Rule G-002~G-004가 생성 시점의 검사라면 이쪽은 어느 시점에 조회해도 성립해야 하는 상태다. 나중에 편집으로 들어와도 안 된다.

| | |
|---|---|
| **위반 시** | 해당 표현을 분리해 Method는 [Intent](e002-intent.md)로, Resource 지정은 제거한다. 분리할 수 없으면 그것은 Goal이 아니라 Task이므로 반려한다 |

### INV-G-04 — 미해소 CONFLICTS_WITH가 있는 Goal은 실행되지 않는다

충돌하는 두 Goal이 동시에 실행되면, 한쪽의 진척이 다른 쪽을 되돌린다. 쓴 비용이 서로를 상쇄한다.

| | |
|---|---|
| **위반 시** | `Executable` 진입을 차단하고 충돌 해소(`resolution`)를 요구한다. 실행 중 충돌이 새로 생기면 양쪽을 `Suspended`로 내리고 Owner에게 판단을 요청한다 |

### INV-G-05 — 종료된 Goal의 objective는 수정되지 않는다

`Completed` / `Failed` / `Archived`는 학습 데이터의 원본이다. 목표를 사후에 고치면 "무엇을 달성했는가"의 기준 자체가 바뀐다.

| | |
|---|---|
| **위반 시** | 변경을 거부한다. 목표가 달라졌으면 **새 Goal**이며, `metadata.history`로 이전 Goal을 잇는다 |

### INV-G-06 — 실행 중 objective가 바뀌면 그것은 같은 Goal이 아니다

`Executing` / `Monitoring` 상태에서 `objective`가 바뀌면 그때까지의 진척도와 평가 기준이 모두 무의미해진다.

| | |
|---|---|
| **위반 시** | 기존 Goal을 `Abandoned`로 처리하고 새 Goal을 생성한다. 진행 중 Plan은 `Superseded`로 내린다 ([goal-state-machine.json](../intent-os-spec/schemas/goal-state-machine.json) global_rules) |

### INV-G-07 — 상태와 완성도는 어긋나지 않는다

`quality.completeness`가 60인데 `phase`가 `Executable`이면, 검증을 통과하지 않은 Goal이 실행 대기열에 있는 것이다.

| | |
|---|---|
| **위반 시** | 상태를 완성도에 맞는 단계로 되돌린다. 완성도 기준값은 [e001d §4](e001d-goal-validation.md)가 정본이다 |

Entity 간 불변식은 [e000a-entity-relationships.md](e000a-entity-relationships.md)가 단일 권위다.

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

---

## 7. Relationships

Goal은 Intent OS에서 **아무것도 참조하지 않는 최상위 객체**다. 다른 Entity들이 Goal을 참조한다([Rule REL-001](e000a-entity-relationships.md)). 예외는 Goal끼리의 관계뿐이며, 그것도 정본은 [Goal Graph](e001a-goal-graph.md)의 edge다.

```
                        Goal 001
                           ▲
      ┌──────────┬─────────┼─────────┬──────────┐
      │          │         │         │          │
  Intent 002  Context 003  │  Constraint 004  Plan 008
                           │
                        Task 005 ──▶ Execution 013 ──▶ Outcome 014
                           
  Goal 001 ──parent/child, dependencies──▶ Goal 001   (정본: Goal Graph 001-A)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Goal Graph](e001a-goal-graph.md) | Goal 간 관계의 정본. Goal 객체의 `dependencies`는 단독 조회용 로컬 뷰다 | `Goal Graph 1:N Goal` |
| Goal | 계층과 의존. 순환은 Graph Entity에서만 허용된다([Rule REL-005](e000a-entity-relationships.md)) | `Goal 1:0..N Goal` |
| [Intent](e002-intent.md) | Goal에서 해결 방향이 추론된다. Goal은 자신의 Intent를 모른다 | `Goal 1:0..N Intent` |
| [Context](e003-context.md) | Goal의 현재 상태. Gap 계산의 기준점 | `Goal 1:0..N Context` |
| [Constraint](e004-constraint.md) | Goal에 부착되고 하위 Goal로 상속된다 | `Goal 1:0..N Constraint` |
| [Task](e005-task.md) | Task는 정확히 하나의 Goal에 기여한다 | `Goal 1:0..N Task` |
| [Plan](e008-plan.md) | Active Plan은 Goal당 하나다([INV-P-01](e008-plan.md)) | `Goal 1:0..N Plan` |
| [Assumption](e017-assumption.md) | Goal이 서 있는 전제 | `Goal 1:0..N Assumption` |
| [Risk](e018-risk.md) | Goal 달성을 위협하는 요인 | `Goal 1:0..N Risk` |
| [Outcome](e014-outcome.md) | `goal_progress`로 진척을 되돌린다. Goal이 Outcome을 참조하지는 않는다 | `Goal 1:0..N Outcome` (간접) |

**Goal은 Resource를 모른다.** 실행 주체를 아는 순간 Goal은 Method를 담게 되고 INV-G-03이 깨진다.

### 7.1 Goal ≠ User Request

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

## 8. Canonical Representation

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

## 9. Validation Rules

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

### 9.1 Formal Grammar

#### 9.1 Purpose

Formal Grammar는 "문장을 예쁘게 쓰는 규칙"이 아니다.

> **Goal이 무엇이고, 무엇이 Goal이 아닌지를 컴퓨터가 판단할 수 있도록 정의하는 문법**이다.

Intent OS는 사용자의 자연어를 받아 이 문법에 맞는 **Goal 객체**로 변환한다.

Goal Grammar는 사용자의 자연어를 **표준 Goal 표현(Standard Goal Representation, SGR)** 으로 변환하기 위한 형식 문법을 정의한다. 목적은 다음과 같다.

1. Goal과 Task를 구분한다.
2. Goal과 Solution을 구분한다.
3. Goal을 구조화된 객체로 변환한다.
4. Goal Validation의 기준을 제공한다.
5. Planner와 Decision Engine이 동일한 입력 형식을 사용하도록 보장한다.

#### 9.2 Goal Grammar (EBNF)

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

## 10. Examples

### 예시 1 — Request에서 추출된 Goal

```
사용자 입력: "겨울에 애들 좀 많이 받고 싶은데요"
   ↓ Goal Extraction
질문 생성: 몇 명? / 언제까지? / 예산은? / 대상 학년은?
   ↓ 응답
goal_001
  title        2027 윈터스쿨 학생 모집
  goal_type    Outcome
  objective    학생 100명 모집
               desired_state  registered_students >= 100 (students)
  constraints  budget 3,000,000 KRW / deadline 2026-11-30
  stakeholders Owner: 김 원장 (organization)
  status       Created → Clarified → Structured
  quality      confidence 0.81 / completeness 84
  metadata     source: conversation
```

`source: conversation`이 중요하다. 사용자가 확정한 Goal이 아니라 대화에서 추론한 Goal이므로 `confidence`가 따라붙는다.

### 예시 2 — Goal이 아닌 것들과 그 판정

```
❌ "인스타그램 광고 돌리기"        → Task      (실행 단위)
❌ "GPT 써서 카피 만들기"          → Method + Resource (Rule G-002, G-003)
❌ "학생 모집 중"                  → 현재 상태 (Rule G-001)
❌ "돈 많이 벌기"                  → Metric 없음 (Rule G-005) → 질문 생성
✅ "2026년 12월까지 윈터캠프 학생 100명 모집"
```

네 번째는 **거부하지 않는다.** Goal이긴 한데 불완전한 것이므로 `Created`에 두고 질문을 만든다.

### 예시 3 — 하위 Goal로 분해된 모습

```
goal_001  윈터캠프 학생 100명 모집          (root, Owner 김 원장)
  ├── goal_002  신규 문의 300건 확보         DEPENDS_ON 없음
  ├── goal_003  상담 전환율 40% 달성         DEPENDS_ON goal_002
  └── goal_004  기존 학생 재등록 30명        CONFLICTS_WITH goal_005
                                             (goal_005: 신규반 정원 확대)
```

`goal_004`와 `goal_005`의 충돌은 교실 수가 한정되어 있기 때문이다. **해소되기 전에는 둘 다 `Executable`로 갈 수 없다**(INV-G-04).

### 예시 4 — 실행 중 목표가 바뀐 경우

```
goal_001  Executing   objective: 학생 100명 모집
   ↓ 09-15 김 원장: "100명은 무리고 70명으로 갑시다"
INV-G-06 — objective 변경은 같은 Goal이 아니다
   ↓
goal_001  Abandoned   (진척 42명까지의 기록 보존)
goal_009  Created     objective: 학생 70명 모집
                      metadata.history: superseded goal_001 (42명 달성 시점)
plan_003  Superseded
```

진척 42명은 사라지지 않는다. 새 Goal의 출발점이 되며, "왜 100명이 70명이 되었는가"가 Learning 입력으로 남는다.

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **Goal이 사실은 Task** (`블로그 작성하기`) | 거부하지 않고 **되묻는다.** "블로그를 작성하는 궁극적인 목적이 무엇입니까?" 상위 Goal이 나오면 원래 문장은 Task가 된다 |
| **Metric을 붙일 수 없는 Goal** (`브랜드 신뢰도 확보`) | Goal로 인정하되 `Structured`로 올리지 않는다. 대리 지표(재등록률, 추천 발생 수)를 제안한다. **측정할 수 없으면 달성 여부도 판정할 수 없다** |
| **Owner가 조직 전체** | `type: organization`으로 한 명(하나의 주체)으로 다룬다. 실무 담당자가 여럿이면 Contributor로 넣는다. Owner는 **책임의 단위이지 인원수가 아니다** |
| **하위 Goal이 모두 달성됐는데 상위가 미달** | 상위 Goal을 자동으로 `Completed`로 올리지 않는다. 분해가 상위를 커버하지 못했다는 뜻이며, 이 불일치 자체가 분해 품질의 학습 신호다 |
| **Goal 두 개가 사실상 같음** | 병합한다. 병합된 쪽은 삭제하지 않고 `metadata.history`로 잇는다. 어느 쪽을 남길지는 진척이 있는 쪽이다 |
| **deadline이 지났는데 미달성** | 자동으로 `Failed`로 내리지 않는다. Owner에게 연장·축소·포기의 판단을 요청한다. **기한은 제약이지 판정이 아니다** |
| **추론된 Goal이 사용자 의도와 다름** | 사용자가 정정하면 새 버전으로 기록하고 `quality.confidence`의 예측 오차를 남긴다. 조용히 덮어쓰면 Goal Extraction이 개선되지 않는다 |
| **상위 Goal이 폐기됐는데 하위가 진행 중** | 하위 Goal을 함께 `Abandoned`로 내리되 진행 중 Execution은 정상 종료시킨다. 중단 비용이 완료 비용보다 큰 경우가 있기 때문이다 |

---

## 12. Open Issues (v2.0)

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

