# Entity 004: Constraint

- **Version:** v1.0 Draft
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

## 3. Hard Constraint vs Soft Constraint

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

---

## 4. Constraint Types

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

### Type 규칙

1. **Legal / Ethical Constraint는 Soft로 선언할 수 없다.** 스키마 수준에서 거부한다.
2. 같은 Type이라도 Hard/Soft는 개별 Constraint마다 선언한다 (Legal/Ethical 제외).
3. 모든 Goal은 시스템 전역(Global) Constraint를 자동 상속한다.

---

## 5. Constraint의 조건

### Rule CN-001 — 검사 가능해야 한다

✅ `예산 ≤ 3,000,000원` — Plan을 보고 위반 여부를 판정할 수 있다.

❌ `돈을 아껴 쓴다` — 판정 불가. Constraint가 아니라 희망사항이다.

### Rule CN-002 — Hardness가 명시되어야 한다

Hard/Soft 미지정 Constraint는 Runtime에 진입할 수 없다. 기본값 추정은 하지 않는다.

### Rule CN-003 — 적용 범위(Scope)가 명시되어야 한다

Global(전역) / Goal / Task 중 하나. Context Scope(§[e003-context.md §5](e003-context.md))와 같은 상속 규칙을 따른다.

### Rule CN-004 — Soft Constraint는 위반 비용(Penalty)을 가져야 한다

감점량이 없으면 Decision Score에 반영할 수 없다.

### Rule CN-005 — 출처(Origin)를 가져야 한다

사용자 선언 / 시스템 전역 정책 / Context에서 파생 — 완화 협상 시 누구와 협상할지 결정한다.

---

## 6. Constraint Attributes

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
| **Type** | 분류 (§4) | `Budget` |
| **Hardness** | Hard / Soft | `Hard` |
| **Expression** | 검사 가능한 조건식 | `total_ad_spend <= 3000000 KRW` |
| **Scope** | 적용 범위 | `Goal (goal_001)` |
| **Origin** | 출처 | `사용자 선언 (2026-08-04)` |
| **Penalty** | Soft 위반 시 감점 | `-0.2 / 초과 10%당` |
| **Relaxation Policy** | 완화 가능 여부와 절차 | `사용자 승인 시 400만원까지 완화 가능` |
| **Status** | 상태 (§7) | `Active` |

---

## 7. Constraint Lifecycle

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
| **Violated** | 위반 감지됨 (§9) |
| **Resolved** | 위반이 해소됨 |
| **Relaxed** | 완화 절차를 거쳐 조건이 변경됨 (§8) |
| **Retired** | Goal 종료 또는 사용자 철회로 비활성화 |

---

## 8. Constraint 충돌과 완화 (Relaxation)

### 충돌

Constraint끼리 충돌하여 **해공간이 공집합**이 될 수 있다.

```
예산 300만원 이하  +  11월 30일까지 100명 모집  +  유료 광고 금지
  ↓
Planner: 실행 가능한 Plan 없음 (Infeasible)
```

### 충돌 처리 규칙

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

### 완화 규칙

1. **Soft Constraint는 시스템이 자율 완화할 수 있다.** 단, 감점을 정직하게 기록한다.
2. **Hard Constraint는 사용자(또는 Origin 주체) 승인 없이 완화할 수 없다.**
3. **Legal / Ethical Constraint는 어떤 절차로도 완화할 수 없다.** 충돌 시 Goal 자체를 수정해야 한다.
4. 모든 완화는 이력으로 남는다. 완화 이력은 Learning Engine의 입력이다 (자주 완화되는 Constraint는 애초에 잘못 선언된 것이다).

---

## 9. Constraint 위반 시 시스템 반응

위반은 계획 시점이 아니라 **실행 중에도** 발생한다 (광고비 초과 지출 등).

| 상황 | 시스템 반응 |
|---|---|
| **계획 시점, Hard 위반 Plan** | 후보에서 즉시 제거. 대안 없으면 Infeasible 절차(§8) |
| **계획 시점, Soft 위반 Plan** | Decision Score 감점 후 경쟁 |
| **실행 중, Hard 위반 감지** | 해당 Execution **즉시 중단** → 사용자 통지 → 재계획 |
| **실행 중, Hard 위반 임박 (예: 예산 90% 소진)** | 경고 발생 → Planner 선제 조정 |
| **실행 중, Soft 위반** | 기록 + Evaluation 단계에서 감점 반영, 실행은 계속 |

[Volume 3 §6 Failure Handling](../v3-runtime.md)과 마찬가지로, **Constraint 위반은 예외가 아니라 정상적으로 처리되는 상태**다.

---

## 10. Canonical Constraint Representation

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

## 11. Constraint Checking Algorithm

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

---

## 12. 다른 Entity와의 관계

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

| Entity | 관계 |
|---|---|
| **Goal** [e001-goal.md](e001-goal.md) | Constraint는 Goal에 부착되며, Goal Graph를 따라 하위 Goal에 상속될 수 있다 |
| **Intent** [e002-intent.md](e002-intent.md) | Intent Extraction의 Constraint Filtering 단계에서 방향 자체를 제거한다 (`예산 300만원` → TV 광고 방향 탈락) |
| **Context** [e003-context.md](e003-context.md) | Context의 사실이 Constraint로 파생될 수 있으나, 파생 시 반드시 `origin: derived_from_context`로 표시한다 |
| **Decision** (e009, 예정) | Hard Constraint는 Candidate Generation 직후 필터로, Soft Constraint는 Score Model의 감점 항으로 들어간다 |
| **Feedback** (e012, 예정) | 완화/위반 이력이 Constraint 선언 품질 개선에 사용된다 |

---

## 13. Open Issues (v1.0)

### Expression 형식 언어

§6의 Expression은 현재 비형식 문자열이다. 검사 가능하려면 형식 언어(비교 연산, 단위, 시간 조건을 포함하는 Constraint Expression Grammar)가 필요하다. Goal의 Formal Grammar([e001-goal.md §9](e001-goal.md))와 같은 수준으로 보강한다.

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
