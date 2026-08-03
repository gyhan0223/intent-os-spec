# Entity 001: Goal

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-03

---

## 1. Definition

### 공식 정의

> **Goal is a desired future state defined by a user or another intelligent agent.**

> Goal은 사용자 또는 다른 지능형 주체가 원하는 미래 상태이다.

여기서 중요한 단어는 **Future State**이다.

Goal은 현재가 아니라 **미래의 상태**를 의미한다.

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

## 4. Goal Attributes

Goal은 최소한 아래 속성을 가진다.

```
Goal
├── Objective
├── Motivation
├── Success Metric
├── Constraints
├── Priority
├── Deadline
├── Context
├── Stakeholders
├── Assumptions
└── Status
```

| 속성 | 의미 | 예 |
|---|---|---|
| **Objective** | 무엇을 이루고 싶은가 | `학생 모집` |
| **Motivation** | 왜? | `윈터캠프 정원 채우기 → 학원 매출 증가 → 신규 브랜드 인지도 확보` |
| **Success Metric** | 성공 기준 | `100명`, `매출 2억`, `CTR 8%` |
| **Constraints** | 제약조건 | 예산, 시간, 법률, 지역 |
| **Priority** | 우선순위 | High / Medium / Low |
| **Deadline** | 언제까지 | `2026-11-30` |
| **Context** | 현재 상황 | 현재 등록자 20명, 예산 300만원, 지역 홍대 |
| **Stakeholders** | 누가 영향을 받는가 | 대표, 학생, 학부모, 마케팅팀 |
| **Assumptions** | 가정 | 광고 예산은 유지된다. 윈터캠프 일정은 변경되지 않는다 |
| **Status** | Goal의 상태 | Draft / Confirmed / Planning / Executing / Completed / Failed |

Motivation은 의외로 굉장히 중요하다. **Motivation에 따라 전략이 달라진다.**

---

## 5. Goal Lifecycle

Goal도 생명주기가 있다.

```
Created → Clarified → Confirmed → Planning → Executing → Monitoring → Completed → Archived
```

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

문법적으로 올바르다고 Goal이 되는 것은 아니다. Intent OS는 의미 규칙(Semantic Rules)도 검사한다.

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

## 12. Canonical Goal Representation (CGR)

모든 Goal은 내부적으로 동일한 구조를 가진다.

```json
{
  "goal_id": "goal_001",
  "goal_type": "Outcome",
  "objective": "학생 모집",
  "target_state": {
    "value": 100,
    "unit": "명"
  },
  "deadline": "2026-11-30",
  "constraints": [],
  "priority": "High",
  "status": "Draft"
}
```

**이 구조만 Runtime으로 전달된다.**

기계가 읽을 수 있는 스키마: [`goal.schema.json`](../intent-os-spec/schemas/goal.schema.json)

---

## 13. Goal Completeness

Goal은 세 단계로 분류된다.

### Level 1 — Raw Goal

```
학생 모집
```

정보 부족.

### Level 2 — Structured Goal

```
학생 100명 모집 / 11월까지 / 홍대 / 예산 300만원
```

Planner 실행 가능.

### Level 3 — Executable Goal

모든 제약조건과 성공 기준이 포함되어 즉시 Planning을 시작할 수 있는 상태.

---

## 14. Goal Validation Algorithm

```
Input
  ↓
Goal Detection
  ↓
Goal Type Classification
  ↓
Method Detection
  ↓
Task Detection
  ↓
Metric Detection
  ↓
Constraint Detection
  ↓
Missing Information
  ↓
Question Generation
  ↓
Goal Confirmation
  ↓
Canonical Goal 생성
```

---

## 15. Goal Completeness Score

Intent OS는 Goal의 완성도를 점수화한다.

| 항목 | 가중치 |
|---|--:|
| Objective | 25% |
| Success Metric | 20% |
| Deadline | 15% |
| Constraints | 15% |
| Context | 10% |
| Stakeholders | 10% |
| Priority | 5% |

예)

- `학생 모집` → 약 **25/100점**
- `2026년 11월까지 홍대 지역 예비 고3 학생 100명 모집. 예산은 300만원 이하.` → **80~90점** 수준

---

## 16. Open Issues (v1.0)

### Goal은 독립 객체로 충분하지 않다

현재 Goal을 **하나의 객체(Object)** 로 정의하고 있는데, 장기적으로는 이것만으로 부족하다.

```
회사 성장
├── 매출 증가
│     ├── 학생 모집
│     ├── 객단가 상승
│     └── 재등록률 향상
│
└── 브랜드 강화
      ├── 유튜브 운영
      ├── SNS 활성화
      └── 후기 확보
```

이건 Goal이 아니라 **Goal Tree**다.

Intent OS가 실제 기업이나 장기 프로젝트를 관리하려면 Goal은 독립적인 객체가 아니라 **계층 구조(DAG, Directed Acyclic Graph)** 로 표현되어야 한다.

모든 Planning, Decision, Learning은 결국 **Goal 간의 관계**를 이해하는 것에서 시작하기 때문에, **Goal Graph가 Intent OS 전체의 가장 중요한 데이터 구조**가 될 가능성이 크다. 이 부분이 다른 AI 오케스트레이션 시스템들과 가장 큰 차별점이 될 수 있다.

→ **[Entity 001-A: Goal Graph Specification](e001a-goal-graph.md)** 에서 정의한다.

### 앞으로 보강해야 할 항목

운영체제 수준의 명세가 되려면 다음까지 포함해야 한다.

- ~~Goal의 형식 문법(Formal Grammar)~~ → §9 반영
- ~~Goal JSON Schema~~ → §12, `goal.schema.json` 반영
- Goal 생성 규칙 (보강 필요)
- ~~Goal 검증 알고리즘~~ → §14 반영 (상세화 필요)
- Goal 추론 알고리즘
- Goal 충돌 해결 (여러 Goal이 충돌할 때) → Goal Graph `CONFLICTS_WITH` 관계로 일부 반영
- ~~Goal 계층 구조 (상위/하위 Goal)~~ → Entity 001-A 반영
- Goal 우선순위 계산 → Goal Graph §10 Goal Score로 일부 반영
- Goal 변경 시 시스템 반응 → Goal Graph §14 Goal Propagation으로 일부 반영
- 실제 예시 30~50개
