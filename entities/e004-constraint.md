# Entity 004: Constraint

- **Version:** v2.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Constraint is an explicit rule that limits the space of acceptable plans, decisions, and executions for a Goal.**

> Constraint는 Goal을 달성하는 과정에서 허용 가능한 계획·결정·실행의 공간을 제한하는 명시적 규칙이다.

핵심 단어는 **Rule(규칙)** 이다.

Goal이 "어디로 갈 것인가"라면, Constraint는 "어디로 가면 안 되는가"다. Planner와 Decision Engine은 Constraint가 그린 경계선 **안에서만** 탐색한다.

```
전체 해공간
└── Policy가 허용하는 공간          ← 조직 규칙 (Goal 무관)
      └── Constraint가 허용하는 공간  ← 이 Goal의 제약
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

### Constraint는 Policy가 아니다

❌ `건당 1만원 초과 실행은 인간 승인 필요` — 이건 [Policy](e019-policy.md)다.

**이 구분이 v2.0에서 가장 중요하다.**

| | Constraint | Policy |
|---|---|---|
| 소속 | 특정 Goal / Task에 붙는다 | Goal과 무관하게 존재한다 |
| 출처 | 사용자가 Goal과 함께 말한다 | 조직·법규·보안이 정한다 |
| 수명 | Goal이 끝나면 사라진다 | 항구적 |
| 우선순위 | Policy보다 아래 | **Constraint보다 위** |
| 예 | "이번 캠프 예산 300만원" | "고액 실행은 승인 필요" |

우선순위는 다음과 같다([INV-11](e000a-entity-relationships.md)).

```
Policy  >  Hard Constraint  >  Decision Utility  >  Soft Constraint
```

> **v1.0 정정:** v1.0 §4의 `Policy Constraint` 타입(`대표 승인 없이 500만원 이상 지출 금지`)은 실제로는 [Policy](e019-policy.md) Entity다. Goal에 종속되지 않기 때문이다. v2.0에서 해당 타입을 제거했다.

### Constraint는 Context가 아니다

- Context: `현재 가용 예산이 300만원이다` — 사실
- Constraint: `예산 지출은 300만원을 초과할 수 없다` — 규칙

사실에서 규칙이 파생될 수는 있지만, 파생 시 반드시 `origin: derived_from_context`로 표시한다([e003 §2](e003-context.md)).

### Constraint는 Assumption이 아니다

- Assumption: `광고 예산은 유지된다` — 참이라고 믿는 명제. 깨지면 **재계획**한다.
- Constraint: `예산 300만원 이하` — 지켜야 하는 규칙. 깨지면 **위반**이다.

**방향이 정반대다.** Constraint는 내가 지키는 것, Assumption은 남이 지켜주길 기대하는 것이다([e017 §2](e017-assumption.md)).

**둘 다 있어야 한다.** Constraint만 있으면 예산이 줄어든 것을 모르고, Assumption만 있으면 예산을 초과 집행한다.

### Constraint는 Task가 아니다

❌ `예산 사용 내역 정리하기` — 작업이다. Constraint는 실행되지 않는다. **검사될 뿐이다.**

### Constraint는 Risk가 아니다

❌ `예산을 초과할 위험이 있다` — 이건 [Risk](e018-risk.md)다.

Constraint는 **경계선**이고 Risk는 **그 선을 넘을 확률**이다. Constraint 여유가 20% 미만이면 Risk가 자동 식별된다([e018 §9.1](e018-risk.md) ④).

---

## 3. Design Principles

### Rule CN-001 — 검사 가능해야 한다

✅ `total_ad_spend <= 3000000` — Plan을 보고 위반 여부를 판정할 수 있다.

❌ `돈을 아껴 쓴다` — 판정 불가. Constraint가 아니라 희망사항이다.

### Rule CN-002 — Hardness가 명시되어야 한다

Hard/Soft 미지정 Constraint는 Runtime에 진입할 수 없다. **기본값 추정은 하지 않는다** — 잘못 추정하면 법규 위반이 감점으로 처리된다.

### Rule CN-003 — 적용 범위(Scope)가 명시되어야 한다

Global / Goal / Task 중 하나. [Context Scope](e003-context.md)와 같은 상속 규칙을 따른다.

### Rule CN-004 — Soft Constraint는 위반 비용(Penalty)을 가져야 한다

감점량이 없으면 Decision Utility에 반영할 수 없다.

### Rule CN-005 — 출처(Origin)를 가져야 한다

사용자 선언 / 시스템 전역 / Context 파생 — **완화 협상 시 누구와 협상할지 결정한다.**

### Rule CN-006 — Hard Constraint를 점수로 다루지 않는다

"법률 위반이지만 점수가 높아서 선택"은 존재할 수 없는 상태다. Hard는 **필터**, Soft는 **점수**다.

### Rule CN-007 — 완화 이력을 남긴다

모든 Relaxation은 기록된다. **자주 완화되는 Constraint는 애초에 잘못 선언된 것이다** — 이 신호가 [Memory](e010-memory.md)를 통해 선언 품질을 개선한다.

---

## 4. Attributes

```
Constraint
├── Identity
│   ├── constraint_id
│   ├── constraint_type
│   └── scope
├── Rule
│   ├── hardness
│   ├── expression
│   ├── unit
│   └── penalty            (Soft만)
├── Governance
│   ├── origin
│   └── relaxation
└── Status
    ├── status
    └── violation_record
```

| 속성 | 의미 | 예 |
|---|---|---|
| **constraint_id** | 식별자 | `cn_003` |
| **constraint_type** | 분류 (§4.2) | `Budget` |
| **scope** | 적용 범위 (Rule CN-003) | `Goal (goal_001)` |
| **hardness** | Hard / Soft (§4.1) | `Hard` |
| **expression** | 검사 가능한 조건식 | `total_ad_spend <= 3000000` |
| **unit** | 단위 | `KRW` |
| **penalty** | Soft 위반 시 감점 | `-0.2 / 초과 10%당` |
| **origin** | 출처 (Rule CN-005) | `user_declared` |
| **relaxation** | 완화 가능 여부와 절차 (§9.2) | 승인 시 400만원까지 |
| **status** | 상태 (§6) | `Active` |

### 4.1 Hard Constraint vs Soft Constraint

**이 구분이 Constraint 명세의 핵심이다.**

| | Hard Constraint | Soft Constraint |
|---|---|---|
| 의미 | 절대 위반 불가 | 가능하면 지키는 선호 |
| 위반 시 | 해당 Plan/Resource **즉시 탈락** | 점수 감점 |
| Decision Engine 역할 | **필터(Filter)** | **점수 반영(Score)** |
| 완화 | 사용자 승인 없이는 불가 | 시스템이 트레이드오프 가능 |
| 예 | `예산 300만원 초과 금지`, `과장 광고 금지` | `가급적 11/15 이전 마감`, `브랜드 톤 유지 선호` |

```
Candidate Resources / Plans
  ↓
Policy 평가                 ← 조직 규칙. 최우선 (INV-11)
  ↓
Hard Constraint Filter      ← 위반 후보 제거 (협상 불가)
  ↓
Soft Constraint Scoring     ← 위반 정도에 따라 감점
  ↓
Decision Utility            ← e009 §4.2
  ↓
Final Selection
```

### 4.2 Constraint Types

```
Constraint
├── Budget Constraint     (예산)
├── Time Constraint       (시간)
├── Legal Constraint      (법률)
├── Quality Constraint    (품질)
├── Resource Constraint   (자원)
└── Ethical Constraint    (윤리)
```

| Type | 예시 | 기본 성격 |
|---|---|---|
| **Budget** | `광고 예산 300만원 이하` | Hard |
| **Time** | `윈터캠프 시작(12월) 전 모집 완료` | Hard |
| **Legal** | `학원법·개인정보보호법 준수, 과장 광고 금지` | **항상 Hard** |
| **Quality** | `광고 소재는 브랜드 가이드 준수` | Soft |
| **Resource** | `디자이너 없음 — 외주 또는 AI 생성만 가능` | Hard |
| **Ethical** | `학생 성적 데이터를 광고에 사용하지 않는다` | **항상 Hard** |

#### Type 규칙

1. **Legal / Ethical Constraint는 Soft로 선언할 수 없다.** 스키마 수준에서 거부한다(INV-CN-02).
2. 같은 Type이라도 Hard/Soft는 개별 Constraint마다 선언한다(Legal/Ethical 제외).
3. 모든 Goal은 시스템 전역(Global) Constraint를 자동 상속한다.

> **v1.0의 `Policy Constraint` 타입은 제거되었다.** 조직 규칙은 [Policy](e019-policy.md) Entity다(§2).

---

## 5. Invariants

### INV-CN-01 — Hard Constraint를 위반한 Plan/Decision은 Active/Committed가 될 수 없다

[INV-07](e000a-entity-relationships.md)의 Constraint 측 표현이다.

| | |
|---|---|
| **위반 시** | 후보에서 제거하고 위반 사유를 기록. 대안이 없으면 Infeasible 절차 (§9.2) |
| **주의** | Soft 위반은 Utility 감점일 뿐 차단이 아니다 |

### INV-CN-02 — Legal / Ethical Constraint는 Soft가 될 수 없고 완화될 수 없다

| | |
|---|---|
| **위반 시** | 선언 자체를 거부한다. 완화 요청도 어떤 승인으로도 통과하지 않는다 |
| **충돌 시** | Goal 자체를 수정해야 한다 (§9.2) |

### INV-CN-03 — Policy가 Constraint를 이긴다

Constraint가 허용해도 Policy가 금지하면 실행되지 않는다.

| | |
|---|---|
| **위반 시** | Policy 평가를 Constraint 검사보다 먼저 수행하도록 파이프라인을 교정 ([INV-11](e000a-entity-relationships.md)) |

### INV-CN-04 — Soft Constraint는 penalty를 가진다

| | |
|---|---|
| **위반 시** | 생성 거부. penalty 없는 Soft는 Utility에 반영되지 않아 사실상 존재하지 않는 것과 같다 |

### INV-CN-05 — 하위 Scope는 상위 Constraint를 완화할 수 없다

Task 수준에서 Goal 수준의 예산 상한을 늘릴 수 없다.

| | |
|---|---|
| **위반 시** | 선언 거부. 상위를 바꿔야 한다면 상위 Scope에서 처리한다 |
| **근거** | [Assumption INV-ASM-05](e017-assumption.md)와 같은 원칙 |

### INV-CN-06 — 모든 완화는 이력을 남긴다

| | |
|---|---|
| **위반 시** | 완화를 롤백한다. 기록 없는 완화는 Constraint를 무의미하게 만든다 (Rule CN-007) |

### INV-CN-07 — Violated Hard Constraint는 실행을 중단시킨다

실행 중 위반이 감지되면 진행 중인 [Execution](e013-execution.md)을 중단한다.

| | |
|---|---|
| **위반 시** | 예산을 초과 집행하게 된다. Execution 생성 게이트와 실행 중 감시 양쪽에서 검사한다 |

---

## 6. Lifecycle

```
Declared → Active → Satisfied
              │
              ├──▶ Violated ──▶ Resolved ──▶ Active
              ├──▶ Relaxed ──▶ Active
              └──▶ Retired
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Declared** | 선언됨, 아직 검증 전 | 사용자 입력 또는 Context 파생 |
| **Active** | 검증 완료, Runtime에서 검사 중 | §9.1 검증 통과 |
| **Violated** | 위반 감지됨 (§9.3) | 검사 실패 |
| **Resolved** | 위반이 해소됨 | 재계획 또는 롤백 완료 |
| **Relaxed** | 완화 절차를 거쳐 조건이 변경됨 (§9.2) | 승인 완료 |
| **Satisfied** | Goal 종료 시점까지 위반 없음 | Goal 종료 |
| **Retired** | Goal 종료 또는 사용자 철회로 비활성화 | Goal 종료/철회 |

**Relaxed는 새 Constraint를 만들지 않는다.** 같은 `constraint_id`의 `expression`이 바뀌고 이력이 `relaxation_history`에 쌓인다 — [Plan](e008-plan.md)이나 [Decision](e009-decision.md)과 다른 점이다. Constraint는 "지금 유효한 경계선"이 하나여야 하기 때문이다.

---

## 7. Relationships

```
Context 003 ──파생──▶ Constraint 004 ──제약──▶ Goal 001 / Plan 008 / Task 005
                            │  ▲
     Policy 019 ──우선─────┘  │
                              ├──필터──▶ Decision 009 (Hard) / 감점 (Soft)
                              ├──감시──▶ Execution 013
                              └──여유──▶ Risk 018 (margin < 20% → Risk 식별)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Goal](e001-goal.md) | Constraint는 Goal에 부착되며 Goal Graph를 따라 상속된다 | `Goal 1:0..N Constraint` |
| [Intent](e002-intent.md) | Intent 후보를 필터링한다 (`예산 300만원` → TV 광고 방향 탈락) | `Constraint N:M Intent` |
| [Context](e003-context.md) | 사실이 규칙으로 파생될 수 있다 | `Context 1:0..N Constraint` |
| [Task](e005-task.md) | Goal의 Constraint가 Task로 상속·전파된다 | `Constraint N:M Task` |
| [Plan](e008-plan.md) | 탐색 공간의 경계. Hard 위반은 Active를 막는다 | `Constraint N:M Plan` |
| [Decision](e009-decision.md) | Hard = 필터, Soft = Utility 감점 | `Constraint N:M Decision` |
| [Execution](e013-execution.md) | 실행 전·중 상시 감시 대상 | `Constraint 1:N Execution` |
| [Policy](e019-policy.md) | **Policy가 Constraint보다 우선한다** (INV-CN-03) | `Policy 1:N Constraint` |
| [Assumption](e017-assumption.md) | 대비 개념. 통제 가능하면 Constraint, 불가능하면 Assumption | — |
| [Risk](e018-risk.md) | 여유가 적으면 Risk가 식별된다 | `Constraint 1:0..N Risk` |

---

## 8. Canonical Representation

```json
{
  "constraint_id": "cn_003",
  "constraint_type": "Budget",
  "hardness": "Hard",
  "expression": "total_ad_spend <= 3000000",
  "unit": "KRW",
  "scope": "Goal",
  "goal_id": "goal_001",
  "origin": "user_declared",
  "declared_at": "2026-08-04T09:00:00Z",
  "relaxation": {
    "relaxable": true,
    "requires_approval": true,
    "approver": "human:대표",
    "max_relaxed_value": 4000000
  },
  "relaxation_history": [],
  "status": "Active"
}
```

Soft Constraint는 `penalty`를 갖는다.

```json
{
  "constraint_id": "cn_007",
  "constraint_type": "Quality",
  "hardness": "Soft",
  "expression": "brand_tone_score >= 0.8",
  "scope": "Goal",
  "goal_id": "goal_001",
  "origin": "user_declared",
  "penalty": { "per_unit": 0.2, "unit": "0.1 미달당", "max_penalty": 0.6 },
  "relaxation": { "relaxable": true, "requires_approval": false },
  "status": "Active"
}
```

Legal Constraint는 완화가 불가능하다.

```json
{
  "constraint_id": "cn_001",
  "constraint_type": "Legal",
  "hardness": "Hard",
  "expression": "contains_exaggerated_claim == false",
  "scope": "Global",
  "origin": "system_global",
  "reference": "표시광고법 제3조",
  "relaxation": { "relaxable": false, "requires_approval": false },
  "status": "Active"
}
```

기계가 읽을 수 있는 스키마: [`constraint.schema.json`](../intent-os-spec/schemas/constraint.schema.json)

---

## 9. Validation Rules

### 9.1 선언 검증

```
Constraint 선언 요청
  ↓
expression 검사 가능성 확인 (Rule CN-001)
  └── 판정 불가한 자연어 → 반려 + 구체화 요구
  ↓
hardness 명시 확인 (Rule CN-002) ── 없으면 반려. 추정하지 않는다
  ↓
Legal / Ethical 인가?
  └── Yes + hardness=Soft → 거부 (INV-CN-02)
  └── Yes + relaxable=true → 거부
  ↓
Soft인가? → penalty 필수 (INV-CN-04)
  ↓
scope 확인 (Rule CN-003)
  ↓
상위 Scope Constraint와의 관계 검사 (INV-CN-05)
  └── 상위보다 느슨하면 거부
  ↓
origin 확인 (Rule CN-005)
  ↓
Goal ID를 포함하지 않는 조직 규칙인가?
  └── Yes → Policy로 등록하도록 안내 (§2)
  ↓
Declared → Active
```

### 9.2 검사 알고리즘

```
Plan / Decision Candidate
  ↓
Policy 평가 (INV-CN-03) ── e019 §9.2. Constraint보다 먼저
  ↓
적용 Constraint 수집 (Global + Goal + Task 상속 병합)
  ↓
Hard Constraint 전수 검사
  ├─ 위반 → 후보 탈락, 위반 사유 기록 (INV-CN-01)
  └─ 통과
       ↓
Soft Constraint 검사
  ↓
위반별 Penalty 합산 → Decision Utility에 반영
  ↓
Constraint Margin 계산 → Plan의 constraint_margin
  └── 여유 < 20% → Risk 식별 트리거 (e018 §9.1 ④)
  ↓
후보 순위 결정
```

#### 충돌과 완화 (Relaxation)

Constraint끼리 충돌하여 **해공간이 공집합**이 될 수 있다.

```
예산 300만원 이하  +  11월 30일까지 100명 모집  +  유료 광고 금지
  ↓
Planner: 실행 가능한 Plan 없음 (Infeasible)
```

해소 절차:

```
Infeasible 감지
  ↓
충돌 Constraint 집합 식별 (최소 충돌 집합)
  ↓
Legal / Ethical 포함? ── Yes → 완화 불가 (INV-CN-02). Goal 수정 제안
  ↓ No
Soft Constraint 존재?
  ├─ Yes → Penalty가 가장 작은 Soft부터 완화 → 재탐색
  └─ No  → Hard끼리 충돌
            ↓
          사용자에게 트레이드오프 제시
            "예산을 400만원으로 올리거나, 목표를 70명으로 조정해야 합니다"
            ↓
          사용자 선택 → Relaxed + relaxation_history 기록 (INV-CN-06) → 재계획
```

완화 규칙:

1. **Soft는 시스템이 자율 완화할 수 있다.** 단 감점을 정직하게 기록한다.
2. **Hard는 Origin 주체의 승인 없이 완화할 수 없다.**
3. **Legal / Ethical은 어떤 절차로도 완화할 수 없다.**
4. 모든 완화는 이력으로 남는다(Rule CN-007).

### 9.3 위반 시 시스템 반응

위반은 계획 시점이 아니라 **실행 중에도** 발생한다.

| 상황 | 시스템 반응 |
|---|---|
| **계획 시점, Hard 위반** | 후보에서 즉시 제거. 대안 없으면 Infeasible 절차(§9.2) |
| **계획 시점, Soft 위반** | Utility 감점 후 경쟁 |
| **실행 전, Hard 위반 예상** | Execution 생성 차단 ([e013 §9](e013-execution.md)) |
| **실행 중, Hard 위반 감지** | 해당 Execution **즉시 중단**(INV-CN-07) → 사용자 통지 → 재계획 |
| **실행 중, Hard 위반 임박 (예: 예산 90% 소진)** | `budget.warning` Event 발행 → Planner 선제 조정 + Risk 재평가 |
| **실행 중, Soft 위반** | 기록 + [Evaluation](e015-evaluation.md)에서 감점 반영, 실행은 계속 |

[Volume 3 §6](../v3-runtime.md)과 마찬가지로, **Constraint 위반은 예외가 아니라 정상적으로 처리되는 상태**다.

---

## 10. Examples

### 예시 1 — 세 Entity의 삼각형

같은 300만원을 두고 세 Entity가 각각 존재한다.

| Entity | 내용 | 위반/변화 시 |
|---|---|---|
| Context `ctx_001#available_resources.예산` | 현재 가용 예산 3,000,000 KRW | 재수집 |
| Constraint `cn_003` | `total_ad_spend <= 3000000` | 위반 → 실행 차단 |
| Assumption `asm_012` | 300만원이 12월까지 유지된다 | 무효화 → Replanning |

**셋 다 있어야 한다.** 하나라도 없으면 사고가 난다 — Constraint가 없으면 초과 집행, Assumption이 없으면 예산 삭감을 모른 채 진행, Context가 없으면 Gap 계산 불가.

### 예시 2 — Hard 필터

```
plan_020 (Draft)  estimated_cost: 3,400,000 KRW
  ↓ §9.2 Hard Constraint 검사
cn_003: total_ad_spend <= 3000000
  ↓ 위반 (초과 400,000)
❌ Draft 유지. Planner에 결함 목록 반환
   - "estimated_cost 3,400,000 > cn_003 상한 3,000,000"
   - "권고: T6 광고 집행 예산 축소 또는 Goal 목표치 조정"
```

**시스템이 임의로 예산을 늘리지 않는다.** Hard Constraint는 협상 대상이 아니다.

### 예시 3 — Soft 감점

```
후보 카피 3종 평가
  cn_007 (Soft): brand_tone_score >= 0.8   penalty: 0.2 / 0.1 미달당

카피 A  brand_tone 0.92  → 위반 없음         Utility 0.91
카피 B  brand_tone 0.75  → 0.05 미달 → -0.1  Utility 0.88 → 0.78
카피 C  brand_tone 0.61  → 0.19 미달 → -0.4  Utility 0.90 → 0.50
```

카피 C는 **Utility가 가장 높았지만** 브랜드 톤 감점으로 최하위가 되었다. Hard였다면 아예 탈락했을 것이다.

### 예시 4 — Infeasible과 트레이드오프

```
cn_003 (Hard, Budget)  예산 ≤ 300만원
cn_005 (Hard, Time)    11/30까지 100명 모집
cn_009 (Hard, Resource) 유료 광고 금지
  ↓
Planner: 실행 가능한 Plan 없음
  ↓ 최소 충돌 집합: {cn_003, cn_005, cn_009}
  ↓ Legal/Ethical 없음 → 완화 가능
  ↓ Soft 없음 → Hard끼리 충돌
  ↓
사용자에게 제시:
  ① 유료 광고 허용 (cn_009 철회)     → 성공 확률 0.82
  ② 목표 70명으로 조정 (Goal 수정)    → 성공 확률 0.71
  ③ 마감 1월로 연기 (cn_005 완화)     → 성공 확률 0.68
  ↓
사용자 선택 ① → cn_009 Retired, relaxation_history 기록 → 재계획
```

### 예시 5 — 완화 불가

```
cn_001 (Legal)  contains_exaggerated_claim == false
  ↓
카피 C: "100% 합격 보장"  → 위반
  ↓ 완화 요청?
❌ INV-CN-02 — Legal은 어떤 승인으로도 완화 불가
  ↓
조치: 카피 C 폐기, 재작성 Task 생성
```

**대표가 승인해도 통과하지 않는다.** 이것이 Legal/Ethical을 별도로 다루는 이유다.

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **Constraint가 하나도 없는 Goal** | 허용하되 경고한다. Global Constraint(Legal/Ethical)는 자동 상속되므로 실제로 0개는 아니다 |
| **Hard와 Soft가 같은 대상을 규정** | 정상이다. `예산 ≤ 300만원`(Hard) + `가급적 250만원 이하`(Soft) 조합이 흔하다. Hard가 경계, Soft가 선호를 표현한다 |
| **완화 후 다시 위반** | 재완화하지 않고 `escalate`한다. 두 번 완화된 Constraint는 잘못 선언된 것이다(Rule CN-007) |
| **Context 파생 Constraint의 원본이 변경** | Constraint를 자동 갱신하지 않는다. `context.updated` Event를 받아 **재선언을 제안**한다. 자동 갱신하면 사용자가 모르는 사이 경계선이 움직인다 |
| **실행 중 Hard 위반인데 중단이 더 큰 손해** | 중단한다(INV-CN-07). 예외를 허용하려면 [Policy](e019-policy.md) 예외 절차를 쓴다 — Constraint 자체를 무시하지 않는다 |
| **Soft Constraint의 penalty 합이 Utility를 음수로** | 허용한다. 음수 Utility 후보는 자연히 탈락한다. penalty 상한(`max_penalty`)으로 조절할 수 있다 |
| **Task가 Goal보다 엄격한 Constraint를 선언** | 허용한다. INV-CN-05는 **완화**만 금지한다. 강화는 정상이다 |
| **Goal 종료 후 Constraint 조회** | `Satisfied` / `Retired` 상태로 남아 있어야 한다. 삭제하지 않는다 — 과거 Decision이 참조한다 |
| **expression이 참조하는 지표가 측정 불가** | Constraint를 `Declared`에 묶어두고 Active로 전이하지 않는다. 검사할 수 없는 Constraint는 없는 것과 같다(Rule CN-001) |

---

## 12. Open Issues (v2.0)

### ✅ v1.0에서 해소된 항목

| v1.0 Open Issue | 해소 |
|---|---|
| Constraint와 조직 정책의 구분 | [Policy](e019-policy.md) Entity 신설. `Policy Constraint` 타입 제거 (§2) |
| Constraint 상속과 예외 | INV-CN-05(하위는 완화 불가) + Policy 예외 절차로 분리 |
| Soft Penalty가 Decision Score에 반영되는 경로 | [Decision Utility](e009-decision.md) §4.2의 감점 항으로 확정 |

### Expression 형식 언어

§4의 `expression`은 여전히 비형식 문자열이다. 검사 가능하려면 형식 문법(비교 연산, 단위, 시간 조건)이 필요하다. **[Policy](e019-policy.md)의 `condition`, [Workflow](e022-workflow.md)의 `condition`과 동일한 표현식 언어를 공유해야 한다** — 세 곳에서 각각 다른 문법을 쓰면 구현이 세 배가 된다.

### Soft Constraint Penalty의 척도

감점량(-0.2 등)이 [Decision Utility](e009-decision.md)의 다른 항(Quality, Cost)과 같은 척도인지 정의되지 않았다. 정규화 규칙이 필요하다.

### 시간에 따라 변하는 Constraint

`캠프 시작 30일 전부터는 환불 규정 강화` 같은 시간 조건부 Constraint의 활성화 규칙이 없다. 현재는 항상 Active이거나 Retired다.

### 최소 충돌 집합 탐지

§9.2는 "최소 충돌 집합을 식별한다"고만 서술한다. Constraint가 20개일 때 어느 부분집합이 충돌의 원인인지 찾는 알고리즘이 정의되지 않았다.

### 앞으로 보강해야 할 항목

- Constraint Expression 형식 문법 (Policy·Workflow와 공유)
- 최소 충돌 집합 탐지 알고리즘
- 위반 감지의 실시간성 (폴링 주기 vs Event 기반)
- 실제 예시 30~50개
