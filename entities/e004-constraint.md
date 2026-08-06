# Entity 004: Constraint

- **Version:** v2.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04
- **Schema:** [`constraint.schema.json`](../intent-os-spec/schemas/constraint.schema.json)

---

## 1. Definition

### 공식 정의

> **Constraint is an explicit rule that limits the space of acceptable plans, decisions, and executions for a Goal.**

> Constraint는 Goal을 달성하는 과정에서 허용 가능한 계획·결정·실행의 공간을 제한하는 명시적 규칙이다.

핵심 단어는 **Rule(규칙)** 이다.

Goal이 "어디로 갈 것인가"라면, Constraint는 "어디로 가면 안 되는가"다. Planner와 Decision Engine은 Constraint가 그린 경계선 **안에서만** 탐색한다.

```
전체 해공간
└── Constraint가 허용하는 공간
      └── Planner가 탐색하는 공간
            └── 선택된 Plan
```

---

## 2. Constraint는 무엇이 아닌가?

이게 정의보다 훨씬 중요하다.

### Constraint는 Goal이 아니다

❌ `광고 비용 20% 절감` — 이건 원하는 미래 상태다. **Optimization Goal**이다.

✅ `광고 예산 300만원 이하` — 넘으면 안 되는 경계다. Constraint다.

판별 질문: **"이것을 더 잘하면 좋은가, 아니면 지키기만 하면 되는가?"** — 지키기만 하면 되면 Constraint다.

### Constraint는 Context가 아니다

- Context: `현재 가용 예산이 300만원이다` — 사실
- Constraint: `예산 지출은 300만원을 초과할 수 없다` — 규칙

사실에서 규칙이 파생될 수는 있지만, 둘은 다른 Entity다 ([e003-context.md §2](e003-context.md)).

### Constraint는 Assumption이 아니다

- Assumption: `광고 예산은 유지된다` — 참이라고 가정하는 명제. 깨지면 **재계획**한다.
- Constraint: `예산 300만원 이하` — 지켜야 하는 규칙. 깨지면 **위반**이다.

### Constraint는 Task가 아니다

❌ `예산 사용 내역 정리하기` — 작업이다. Constraint는 실행되지 않는다. **검사될 뿐이다.**

---

## 3. Design Principles

### Rule CN-001 — 검사 가능해야 한다

✅ `예산 ≤ 3,000,000원` — Plan을 보고 위반 여부를 판정할 수 있다.

❌ `돈을 아껴 쓴다` — 판정 불가. Constraint가 아니라 희망사항이다.

### Rule CN-002 — Hardness가 명시되어야 한다

Hard/Soft 미지정 Constraint는 Runtime에 진입할 수 없다. 기본값 추정은 하지 않는다.

### Rule CN-003 — 적용 범위(Scope)가 명시되어야 한다

Global(전역) / Goal / Task 중 하나. Context Scope([e003-context.md §4.1](e003-context.md))와 같은 상속 규칙을 따른다.

### Rule CN-004 — Soft Constraint는 위반 비용(Penalty)을 가져야 한다

감점량이 없으면 Decision Score에 반영할 수 없다.

### Rule CN-005 — 출처(Origin)를 가져야 한다

사용자 선언 / 시스템 전역 정책 / Context에서 파생 — 완화 협상 시 누구와 협상할지 결정한다.

---

## 4. Attributes

```
Constraint
├── Type
├── Hardness
├── Expression
├── Scope
├── Origin
├── Penalty (Soft만)
├── Relaxation Policy
└── Status
```

| 속성 | 의미 | 예 |
|---|---|---|
| **Type** | 분류 (§4.2) | `Budget` |
| **Hardness** | Hard / Soft | `Hard` |
| **Expression** | 검사 가능한 조건식 | `total_ad_spend <= 3000000 KRW` |
| **Scope** | 적용 범위 | `Goal (goal_001)` |
| **Origin** | 출처 | `사용자 선언 (2026-08-04)` |
| **Penalty** | Soft 위반 시 감점 | `-0.2 / 초과 10%당` |
| **Relaxation Policy** | 완화 가능 여부와 절차 | `사용자 승인 시 400만원까지 완화 가능` |
| **Status** | 상태 (§6) | `Active` |

### 4.1 Hard Constraint vs Soft Constraint

**이 구분이 Constraint 명세의 핵심이다.**

| | Hard Constraint | Soft Constraint |
|---|---|---|
| 의미 | 절대 위반 불가 | 가능하면 지키는 선호 |
| 위반 시 | 해당 Plan/Resource **즉시 탈락** | 점수 감점 |
| Decision Engine 역할 | **필터(Filter)** | **점수 반영(Score)** |
| 완화(Relaxation) | 사용자 승인 없이는 불가 | 시스템이 트레이드오프 가능 |
| 예 | `사교육 관련 법규 준수`, `예산 300만원 초과 금지` | `가급적 11월 15일 이전 마감`, `브랜드 톤 유지 선호` |

Decision Engine의 처리 원칙:

```
Candidate Resources / Plans
  ↓
Hard Constraint Filter      ← 위반 후보 제거 (협상 불가)
  ↓
Soft Constraint Scoring     ← 위반 정도에 따라 감점
  ↓
Decision Score Model        ([Volume 3 Stage 4](../v3-runtime.md))
  ↓
Final Selection
```

**Hard Constraint를 점수로 다루면 안 된다.** "법률 위반이지만 점수가 높아서 선택"은 존재할 수 없는 상태다.

### 4.2 Constraint Types

```
Constraint
├── Budget Constraint     (예산)
├── Time Constraint       (시간)
├── Legal Constraint      (법률)
├── Quality Constraint    (품질)
├── Resource Constraint   (자원)
├── Ethical Constraint    (윤리)
└── Policy Constraint     (정책)
```

| Type | 예시 | 기본 성격 |
|---|---|---|
| **Budget** | `광고 예산 300만원 이하` | Hard |
| **Time** | `윈터캠프 시작(12월) 전 모집 완료` | Hard |
| **Legal** | `학원법·개인정보보호법 준수, 과장 광고 금지` | **항상 Hard** |
| **Quality** | `광고 소재는 브랜드 가이드 준수` | Soft |
| **Resource** | `디자이너 없음 — 외주 또는 AI 생성만 가능` | Hard |
| **Ethical** | `학생 성적 데이터를 광고에 사용하지 않는다` | **항상 Hard** |
| **Policy** | `대표 승인 없이 500만원 이상 지출 금지` | Hard |

#### Type 규칙

1. **Legal / Ethical Constraint는 Soft로 선언할 수 없다.** 스키마 수준에서 거부한다.
2. 같은 Type이라도 Hard/Soft는 개별 Constraint마다 선언한다 (Legal/Ethical 제외).
3. 모든 Goal은 시스템 전역(Global) Constraint를 자동 상속한다.

---

## 5. Invariants

### INV-CN-01 — Legal / Ethical Constraint는 Soft가 될 수 없다

§4.2 Type 규칙 1을 상태로 표현한 것이다. 선언 시점뿐 아니라 완화·상속·병합 어느 경로로도 Hard에서 Soft로 내려가면 안 된다.

| | |
|---|---|
| **위반 시** | 변경을 거부하고 Hard로 되돌린다. 해당 Plan 탐색을 중단하고 운영자에게 보고한다. **점수로 우회할 수 있는 법규 준수는 준수가 아니다** |
| **탐지** | 선언 시점, 완화 요청 시점, 상속 병합 시점 |

### INV-CN-02 — Hard Constraint를 위반한 Plan은 선택되지 않는다

Hard는 필터이지 감점 항목이 아니다. 점수가 아무리 높아도 통과할 수 없다.

| | |
|---|---|
| **위반 시** | 이미 선택된 Plan이면 실행을 즉시 중단하고 Decision을 무효화한다. 그때까지 발생한 비용은 기록한다 — 비용은 사라지지 않는다 |
| **탐지** | 후보 필터링 시점, 실행 중 상시 감시 |

### INV-CN-03 — Soft Constraint는 Penalty 없이 존재하지 않는다

Rule CN-004가 생성 검사라면 이쪽은 항상 성립해야 하는 상태다. Penalty가 없으면 Decision Score에 반영할 방법이 없고, 반영되지 않는 Constraint는 없는 것과 같다.

| | |
|---|---|
| **위반 시** | 해당 Constraint를 `Declared`로 되돌리고 Runtime 진입을 막는다. 기본값을 임의로 채우지 않는다 |

### INV-CN-04 — 완화는 이력 없이 일어나지 않는다

| | |
|---|---|
| **위반 시** | 완화를 되돌린다. 누가 언제 무엇을 어디까지 풀었는지가 없으면 사후에 책임도 학습도 성립하지 않는다 |
| **탐지** | Relaxed 전이 훅 |

### INV-CN-05 — 완화된 값은 Relaxation Policy의 상한을 넘지 않는다

`max_relaxed_value: 4000000`인 예산 제약이 500만원으로 풀려 있으면, 상한 자체가 무의미해진다.

| | |
|---|---|
| **위반 시** | 상한값으로 되돌리고 초과분에 해당하는 Plan을 재탐색한다. Origin 주체에게 통지한다 |

### INV-CN-06 — 상충하는 Constraint가 동시에 Active일 수 없다

`예산 ≤ 300만원`과 `예산 ≥ 400만원`이 함께 Active면 해공간은 영원히 공집합이다.

| | |
|---|---|
| **위반 시** | Infeasible로 판정하고 §6.1 충돌 처리 절차에 넘긴다. 조용히 한쪽을 무시하지 않는다 |

Entity 간 불변식은 [e000a-entity-relationships.md](e000a-entity-relationships.md)가 단일 권위다.

---

## 6. Lifecycle

```
Declared → Active → Satisfied
              ├→ Violated → Resolved
              ├→ Relaxed
              └→ Retired
```

| 상태 | 의미 |
|---|---|
| **Declared** | 선언됨, 아직 검증 전 |
| **Active** | 검증 완료, Runtime에서 검사 중 |
| **Satisfied** | Goal 종료 시점까지 위반 없음 |
| **Violated** | 위반 감지됨 (§9.1) |
| **Resolved** | 위반이 해소됨 |
| **Relaxed** | 완화 절차를 거쳐 조건이 변경됨 (§6.1) |
| **Retired** | Goal 종료 또는 사용자 철회로 비활성화 |

### 6.1 충돌과 완화 (Relaxation)

#### 충돌

Constraint끼리 충돌하여 **해공간이 공집합**이 될 수 있다.

```
예산 300만원 이하  +  11월 30일까지 100명 모집  +  유료 광고 금지
  ↓
Planner: 실행 가능한 Plan 없음 (Infeasible)
```

#### 충돌 처리 규칙

```
Infeasible 감지
  ↓
충돌 Constraint 집합 식별 (최소 충돌 집합)
  ↓
Soft Constraint 존재?
  ├─ Yes → Penalty가 가장 작은 Soft부터 완화 → 재탐색
  └─ No  → Hard끼리 충돌
            ↓
          사용자에게 트레이드오프 제시
            "예산을 400만원으로 올리거나, 목표를 70명으로 조정해야 합니다"
            ↓
          사용자 선택 → Relaxed 기록 → 재계획
```

#### 완화 규칙

1. **Soft Constraint는 시스템이 자율 완화할 수 있다.** 단, 감점을 정직하게 기록한다.
2. **Hard Constraint는 사용자(또는 Origin 주체) 승인 없이 완화할 수 없다.**
3. **Legal / Ethical Constraint는 어떤 절차로도 완화할 수 없다.** 충돌 시 Goal 자체를 수정해야 한다.
4. 모든 완화는 이력으로 남는다. 완화 이력은 Learning Engine의 입력이다 (자주 완화되는 Constraint는 애초에 잘못 선언된 것이다).

---

## 7. Relationships

```
Goal (e001)         : Goal의 constraints 속성은 이 Entity 참조로 대체된다
  ↓
Intent (e002)       : Intent 후보 필터링 (Constraint Filtering 단계)
  ↓
Task / Plan (예정)   : Plan 탐색 공간의 경계
  ↓
Decision (e009 예정) : Hard = 필터, Soft = 점수
  ↓
Execution           : 실행 중 상시 감시 대상
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Goal](e001-goal.md) | Constraint는 Goal에 부착되며, Goal Graph를 따라 하위 Goal에 상속될 수 있다 | `Goal 1:0..N Constraint` |
| [Intent](e002-intent.md) | Intent Extraction의 Constraint Filtering 단계에서 방향 자체를 제거한다 (`예산 300만원` → TV 광고 방향 탈락) | `Constraint N:M Intent` |
| [Context](e003-context.md) | Context의 사실이 Constraint로 파생될 수 있으나, 파생 시 반드시 `origin: derived_from_context`로 표시한다 | `Context 1:0..N Constraint` |
| [Plan](e008-plan.md) | Plan 탐색 공간의 경계를 정한다 | `Constraint N:M Plan` |
| [Decision](e009-decision.md) | Hard Constraint는 Candidate Generation 직후 필터로, Soft Constraint는 Score Model의 감점 항으로 들어간다 | `Constraint N:M Decision` |
| [Execution](e013-execution.md) | 실행 중 상시 감시 대상. Hard 위반 시 즉시 중단한다 | `Constraint N:M Execution` |
| [Feedback](e012-feedback.md) | 완화·위반 이력이 Constraint 선언 품질 개선에 사용된다 | `Constraint 1:0..N Feedback` |

**Constraint는 Goal을 참조하고 Goal은 Constraint 목록을 들고 있지 않다**([Rule REL-001](e000a-entity-relationships.md)).

---

## 8. Canonical Representation

```json
{
  "constraint_id": "cst_001",
  "constraint_type": "Budget",
  "hardness": "Hard",
  "expression": "total_ad_spend <= 3000000",
  "unit": "KRW",
  "scope": "Goal",
  "goal_id": "goal_001",
  "origin": "user_declared",
  "relaxation": {
    "relaxable": true,
    "requires_approval": true,
    "max_relaxed_value": "4000000"
  },
  "status": "Active"
}
```

기계가 읽을 수 있는 스키마: [`constraint.schema.json`](../intent-os-spec/schemas/constraint.schema.json)

---

## 9. Validation Rules

```
Plan / Decision Candidate
  ↓
적용 Constraint 수집 (Global + Goal + Task 상속 병합)
  ↓
Hard Constraint 전수 검사
  ├─ 위반 → 후보 탈락, 위반 사유 기록
  └─ 통과
       ↓
Soft Constraint 검사
  ↓
위반별 Penalty 합산 → Decision Score에 반영
  ↓
후보 순위 결정
```

### 9.1 위반 시 시스템 반응

위반은 계획 시점이 아니라 **실행 중에도** 발생한다 (광고비 초과 지출 등).

| 상황 | 시스템 반응 |
|---|---|
| **계획 시점, Hard 위반 Plan** | 후보에서 즉시 제거. 대안 없으면 Infeasible 절차(§6.1) |
| **계획 시점, Soft 위반 Plan** | Decision Score 감점 후 경쟁 |
| **실행 중, Hard 위반 감지** | 해당 Execution **즉시 중단** → 사용자 통지 → 재계획 |
| **실행 중, Hard 위반 임박 (예: 예산 90% 소진)** | 경고 발생 → Planner 선제 조정 |
| **실행 중, Soft 위반** | 기록 + Evaluation 단계에서 감점 반영, 실행은 계속 |

[Volume 3 §6 Failure Handling](../v3-runtime.md)과 마찬가지로, **Constraint 위반은 예외가 아니라 정상적으로 처리되는 상태**다.

---

## 10. Examples

### 예시 1 — 윈터캠프 Goal의 Constraint 집합

```
goal_001  윈터캠프 학생 100명 모집

cst_001  Budget   Hard  total_ad_spend <= 3000000 KRW      origin: user_declared
cst_002  Time     Hard  모집 완료 <= 2026-11-30             origin: user_declared
cst_003  Legal    Hard  과장 광고 금지 (학원법)              origin: global_policy
cst_004  Ethical  Hard  학생 성적 데이터 광고 사용 금지        origin: global_policy
cst_005  Quality  Soft  브랜드 가이드 준수   penalty -0.15    origin: user_declared
cst_006  Resource Hard  디자이너 없음 — 외주 또는 AI 생성만    origin: derived_from_context
```

`cst_006`은 Context의 사실(`마케팅 인력 0명`)에서 파생됐다. 파생된 Constraint는 `origin`으로 구분되며, 원본 Context가 바뀌면 함께 재검토된다.

### 예시 2 — Hard 필터와 Soft 감점이 갈리는 순간

```
후보 Plan 3개
                      cst_001(예산)  cst_005(브랜드 가이드)  최종
plan_A  280만원 집행    통과           준수                   점수 0.82  ✅ 선택
plan_B  340만원 집행    위반           준수                   즉시 탈락  ❌
plan_C  190만원 집행    통과           일부 이탈               점수 0.71  ⚠️ 차선
```

`plan_B`는 점수를 계산하지도 않는다. **Hard는 경쟁에 참여할 자격의 문제이지 점수의 문제가 아니다**(INV-CN-02).

### 예시 3 — 충돌로 Infeasible이 된 경우와 그 해소

```
cst_001 예산 300만원 이하  +  cst_002 11월 30일까지 100명  +  cst_007 유료 광고 금지
  ↓
Planner: 실행 가능한 Plan 없음 (Infeasible)
  ↓ 최소 충돌 집합 식별
{cst_001, cst_002, cst_007}
  ↓ Soft 없음 → Hard끼리 충돌
사용자에게 트레이드오프 제시
  "예산을 400만원으로 올리거나, 목표를 70명으로 낮추거나, 유료 광고를 허용해야 합니다"
  ↓ 김 원장 선택: 예산 400만원
cst_001  Relaxed  3000000 → 4000000  승인 김 원장  2026-08-20
```

완화 상한이 `max_relaxed_value: 4000000`이었으므로 이 완화는 허용된다. 450만원을 요구했다면 INV-CN-05에 걸려 거부되고, 다른 축을 조정해야 한다.

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **Hard와 Soft가 같은 대상을 두고 충돌** (`예산 ≤ 300만원` Hard + `가급적 200만원 이내` Soft) | 충돌이 아니다. Soft는 Hard의 부분집합을 선호하는 것뿐이다. 250만원 Plan은 통과하되 Soft 감점을 받는다 |
| **Legal Constraint가 Goal 자체를 불가능하게 만듦** | Constraint를 건드리지 않는다. **Goal을 수정한다.** 법규를 완화하는 경로는 어떤 절차로도 존재하지 않는다(INV-CN-01) |
| **실행 중 예산이 이미 초과됨** (감지가 늦음) | 되돌릴 수 없는 지출이다. Execution을 즉시 중단하고 초과분을 기록한다. Constraint를 사후에 완화해 "위반이 아니었던 것"으로 만들지 않는다 — 그러면 학습 데이터가 오염된다 |
| **Context가 바뀌어 파생 Constraint의 근거가 사라짐** | 자동으로 지우지 않는다. `Declared`로 내리고 재검토를 요청한다. 근거가 사라진 것과 제약이 사라진 것은 다르다 |
| **상위 Goal의 Constraint와 하위 Goal의 Constraint가 다름** | 하위가 상위보다 **엄격한 것만** 허용한다. 느슨하게 만드는 override는 Origin 주체 승인이 필요하며, Legal/Ethical은 승인으로도 불가하다 |
| **Soft Constraint를 전부 위반해도 통과하는 Plan이 유일** | 통과시킨다. 단 누적 Penalty를 Decision에 기록하고 사용자에게 고지한다. Soft를 전부 어겨야만 풀리는 Goal은 **Constraint 선언이 잘못됐다는 신호**이므로 Learning Engine 입력으로 남긴다 |
| **완화 이력이 계속 쌓이는 Constraint** | 위반이 아니라 **선언 오류**로 다룬다. 같은 Constraint가 3회 이상 완화되면 초기 선언값 재검토를 제안한다 (§6.1 완화 규칙 4) |

---

## 12. Open Issues (v1.0)

### Expression 형식 언어

§4의 Expression은 현재 비형식 문자열이다. 검사 가능하려면 형식 언어(비교 연산, 단위, 시간 조건을 포함하는 Constraint Expression Grammar)가 필요하다. Goal의 Formal Grammar([e001-goal.md](e001-goal.md))와 같은 수준으로 보강한다.

### Soft Constraint Penalty의 단위

감점량(-0.2 등)이 Decision Score의 다른 항(Quality, Cost 등)과 같은 척도인지 정의되지 않았다. Volume 4 Decision Engine 명세와 함께 확정한다.

### Constraint 상속과 예외

Global Constraint를 특정 Goal에서 예외 처리(Override)할 수 있는가? v1.0은 "Legal/Ethical은 불가, 나머지는 Origin 주체 승인 시 가능" 원칙만 정한다.

### 시간에 따라 변하는 Constraint

`캠프 시작 30일 전부터는 환불 규정 강화` 같은 시간 조건부 Constraint의 활성화 규칙이 필요하다.

### 앞으로 보강해야 할 항목

- Constraint Expression 형식 문법
- 최소 충돌 집합(Minimal Conflict Set) 탐지 알고리즘 상세화
- 위반 감지의 실시간성 (폴링 주기 vs 이벤트 기반)
- 실제 예시 30~50개

