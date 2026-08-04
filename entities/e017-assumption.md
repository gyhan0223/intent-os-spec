# Entity 017: Assumption

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Assumption is an explicitly stated belief about the world that a Goal or Plan depends on but does not control, whose invalidation must trigger replanning.**

> Assumption은 Goal 또는 Plan이 **의존하지만 통제하지는 못하는** 세계에 대한 명시적 믿음이며, 이것이 깨지면 반드시 Replanning을 유발해야 한다.

여기서 중요한 단어는 **명시적(Explicitly Stated)** 이다.

모든 계획에는 가정이 있다. 문제는 **그 가정이 대부분 암묵적**이라는 것이다.

```
Plan: 광고비 300만원으로 학생 100명 모집
      ↑
      암묵적 가정:
      · 광고비 300만원이 계속 집행 가능하다
      · 예비 고3 학부모가 인스타그램을 쓴다
      · 12월에 김 카피라이터가 가용하다
      · Claude의 한국어 카피 성능이 지금 수준을 유지한다
      · 경쟁 학원이 같은 시기에 대규모 할인을 하지 않는다
```

이 중 하나만 깨져도 계획은 틀린다. 그런데 암묵적이면 **깨진 사실조차 알아채지 못한다.**

> **Assumption의 존재 이유는 "언제 계획을 다시 세워야 하는지 아는 것"이다.**

---

## 2. Assumption은 무엇이 아닌가?

### Assumption은 Constraint가 아니다

❌ `광고비는 300만원을 넘을 수 없다` — 이건 [Constraint](e004-constraint.md)다.

**이 구분이 가장 중요하다.**

| | Constraint | Assumption |
|---|---|---|
| 성격 | 지켜야 하는 규칙 | 참이라고 믿는 사실 |
| 통제 | 시스템이 통제한다 | 시스템 밖에 있다 |
| 위반 시 | 시스템이 잘못한 것 → 차단 | 세계가 변한 것 → Replanning |
| 예 | "예산 300만원 이하로 집행한다" | "예산 300만원이 계속 확보된다" |

같은 숫자를 두고도 방향이 정반대다. Constraint는 **내가 지키는 것**, Assumption은 **남이 지켜주길 기대하는 것**이다.

### Assumption은 Risk가 아니다

❌ `광고비가 삭감될 수 있다` — 이건 [Risk](e018-risk.md)다.

```
Assumption   광고비 300만원이 유지된다          (믿음)
     │
     │ 깨질 가능성
     ▼
Risk         광고비 삭감 (likelihood 0.3 × impact 0.8)   (나쁜 사건의 가능성)
```

**Assumption이 Risk를 낳는다.** 모든 Assumption에는 그것이 깨질 Risk가 대응하며, 역으로 근거 없는 Risk는 대개 명시되지 않은 Assumption의 신호다.

### Assumption은 Context가 아니다

❌ `현재 광고 예산 잔액 2,340,000원` — 이건 [Context](e003-context.md)다.

| | Context | Assumption |
|---|---|---|
| 성격 | 관측된 사실 | 검증되지 않은 믿음 |
| 시점 | 현재 | 미래에 대한 기대 |
| 갱신 | 수집(collect)한다 | 검증(validate)한다 |

Context는 "지금 얼마인가", Assumption은 "앞으로도 그럴 것인가"다.

### Assumption은 Prediction이 아니다

❌ `Claude가 이 Task에서 0.91의 Utility를 낼 것` — 이건 Decision Engine의 Prediction이다.

Prediction은 **시스템이 데이터로 계산한 추정치**이고, Assumption은 **데이터가 없어서 믿기로 한 전제**다. Prediction은 틀리면 모델을 보정하고, Assumption은 깨지면 계획을 바꾼다.

### Assumption은 Hypothesis가 아니다

❌ `내신 소구가 합격 실적 소구보다 효과적일 것이다 — A/B 테스트로 검증하자`

Hypothesis는 **검증하려고 만든 것**이다. 실험을 설계하고 결과를 본다. Assumption은 **검증할 수 없어서 믿기로 한 것**이다. 검증 가능해지는 순간 그것은 Context가 된다.

---

## 3. Design Principles

### Rule ASM-001 — 반증 가능해야 한다 (Falsifiable)

"무엇이 관측되면 이 가정이 깨진 것인가"를 답할 수 없으면 Assumption이 아니다.

- ✅ `광고비 월 300만원이 유지된다` → 반증: 월 집행 가능액이 300만원 미만으로 확인됨
- ❌ `마케팅이 잘 될 것이다` → 무엇이 관측되어야 깨진 것인지 알 수 없다

모든 Assumption은 `validation` 블록을 갖는다.

### Rule ASM-002 — 무엇이 이 가정에 의존하는지 명시한다

`dependents`가 비어 있는 Assumption은 관리할 필요가 없다. **아무것도 의존하지 않는 믿음은 계획에 영향을 주지 않기 때문이다.**

### Rule ASM-003 — 신뢰도와 검증 주기를 가진다

| 필드 | 의미 |
|---|---|
| `confidence` | 이 가정이 참일 확률 (0.0~1.0) |
| `validation.method` | 어떻게 확인하는가 |
| `validation.interval` | 얼마나 자주 확인하는가 |
| `validation.last_checked_at` | 마지막 확인 시각 |

**검증 주기가 없는 가정은 방치된다.** 방치된 가정이 깨져 있는 채로 계획이 진행되는 것이 실패의 전형적 경로다.

### Rule ASM-004 — 깨졌을 때의 조치를 미리 정의한다

`on_invalidation`이 필수다. 가정이 깨진 뒤에 무엇을 할지 논의하면 이미 늦다.

| on_invalidation | 의미 |
|---|---|
| `replan` | Plan 전체를 다시 세운다 |
| `adjust_scope` | Goal의 목표치를 조정한다 |
| `substitute` | 대체 수단으로 전환한다 |
| `escalate` | 인간에게 판단을 넘긴다 |
| `accept` | 영향을 감수하고 계속한다 (명시적 승인 필요) |

### Rule ASM-005 — 암묵적 가정을 명시화한다

Planner는 Plan을 만들 때 **가정 추출(Assumption Extraction)** 을 수행해야 한다(§9.1). 사용자가 말하지 않은 전제를 시스템이 찾아 적어야 한다.

### Rule ASM-006 — 영향도(Impact)를 가진다

가정이 깨졌을 때 얼마나 큰 문제인가. 영향도가 낮은 가정까지 매일 검증하면 비용만 든다.

$$Priority = Impact \times (1 - Confidence)$$

**신뢰도가 낮고 영향이 큰 가정부터** 검증 자원을 배분한다.

### Rule ASM-007 — 가정은 상속된다

Goal의 Assumption은 그 Goal에서 파생된 Plan·Task로 상속된다. [Constraint](e004-constraint.md)의 상속 규칙과 동일하다. 하위에서 가정을 추가할 수는 있지만 **상위의 가정을 무효화할 수는 없다.**

### Rule ASM-008 — 깨진 가정은 방치할 수 없다

`Invalidated` 상태의 Assumption을 가진 Plan은 `Active`로 남을 수 없다([INV-10](e000a-entity-relationships.md)). 이것이 이 Entity의 존재 이유 그 자체다.

---

## 4. Attributes

```
Assumption
├── Identity
│   ├── assumption_id
│   ├── scope           (goal_id / plan_id / task_id)
│   └── type
├── Statement
│   ├── statement
│   ├── confidence
│   └── impact
├── Validation
│   ├── method
│   ├── source
│   ├── interval
│   ├── last_checked_at
│   └── invalidation_criteria
├── Dependency
│   ├── dependents[]
│   └── linked_risk_id
├── Response
│   ├── on_invalidation
│   └── fallback_plan_ref
└── Status
    ├── status
    └── invalidated_at
```

| 속성 | 의미 | 예 |
|---|---|---|
| **assumption_id** | 식별자 | `asm_012` |
| **scope** | 어디에 걸린 가정인가 | `goal_001` |
| **type** | 분류 (§4.1) | `economic` |
| **statement** | 가정 문장 | `윈터캠프 광고비 월 300만원이 12월까지 유지된다` |
| **confidence** | 참일 확률 | `0.85` |
| **impact** | 깨졌을 때의 영향 | `high` |
| **method** | 검증 방법 | `대표 확인` / `CRM 조회` / `외부 API` |
| **source** | 확인 대상 | `human:대표` |
| **interval** | 검증 주기 | `P7D` |
| **last_checked_at** | 마지막 검증 | `2026-08-04T09:00:00Z` |
| **invalidation_criteria** | 무엇이 관측되면 깨진 것인가 | `월 집행 가능액 < 3,000,000 KRW` |
| **dependents** | 이 가정에 의존하는 것들 | `["plan_014", "task_006"]` |
| **linked_risk_id** | 대응하는 Risk | `rsk_007` |
| **on_invalidation** | 깨졌을 때의 조치 | `replan` |
| **fallback_plan_ref** | 대비 계획 | `plan_014_fallback` |
| **status** | 상태 (§6) | `Holding` |

### 4.1 Assumption Types

```
Assumption
├── economic      비용·예산·가격에 대한 전제
├── resource      Resource의 가용성·성능에 대한 전제
├── behavioral    사람(사용자·고객·시장)의 행동에 대한 전제
├── environmental 외부 환경·경쟁·규제에 대한 전제
├── data          데이터의 정확성·최신성에 대한 전제
├── temporal      일정·시기에 대한 전제
└── technical     기술적 동작에 대한 전제
```

| Type | 예 | 검증 방법 |
|---|---|---|
| `economic` | 광고비 300만원이 유지된다 | 대표 확인 (주 1회) |
| `resource` | 김 카피라이터가 12월에 가용하다 | 캘린더 조회 (주 1회) |
| `behavioral` | 예비 고3 학부모가 인스타그램을 쓴다 | 유입 채널 분석 (월 1회) |
| `environmental` | 경쟁 학원이 12월에 대규모 할인을 하지 않는다 | 경쟁 모니터링 (주 1회) |
| `data` | CRM의 상담 이력이 최신이다 | 최종 갱신 시각 확인 (일 1회) |
| `temporal` | 12월 1일 전에 랜딩페이지가 완성된다 | Plan 진척 확인 (일 1회) |
| `technical` | Claude의 한국어 카피 성능이 유지된다 | Drift 감지 ([Volume 4-B](../v4b-resource-intelligence.md)) |

**`technical` 타입은 특별하다.** Resource Drift 감지가 자동으로 이 가정을 검증한다. 사람이 개입할 필요가 없는 유일한 유형이다.

---

## 5. Invariants

### INV-ASM-01 — 모든 Assumption은 invalidation_criteria를 가진다

| | |
|---|---|
| **위반 시** | 생성 거부. 반증 조건 없는 가정은 검증할 수 없다 (Rule ASM-001) |

### INV-ASM-02 — 모든 Assumption은 on_invalidation을 가진다

| | |
|---|---|
| **위반 시** | 생성 거부. 기본값 `escalate`를 자동 적용하되 경고를 남긴다 |

### INV-ASM-03 — Invalidated 상태의 Assumption에 의존하는 Plan은 Active일 수 없다

전역 불변식 [INV-10](e000a-entity-relationships.md)의 Assumption 측 표현이다.

| | |
|---|---|
| **위반 시** | Plan을 `Suspended`로 강제 전이하고 Replanning을 큐에 등록 |
| **탐지** | 상태 전이 훅 + 일 1회 스윕 |

### INV-ASM-04 — 검증 주기를 초과한 Assumption은 Holding으로 남을 수 없다

`now − last_checked_at > interval` 이면 상태는 `Stale`이다.

| | |
|---|---|
| **위반 시** | 자동으로 `Stale` 전이 + 검증 Task 생성 |
| **근거** | "확인한 지 오래된 믿음"과 "확인된 사실"을 같게 취급하면 안 된다 |

### INV-ASM-05 — 하위 Assumption은 상위 Assumption과 모순될 수 없다

Goal의 가정이 "예산 300만원 유지"인데 Task의 가정이 "예산 500만원 확보"이면 모순이다.

| | |
|---|---|
| **위반 시** | 하위 가정의 생성을 거부. 상위를 바꿔야 한다면 상위 수준에서 처리 |

### INV-ASM-06 — accept로 처리된 무효 가정은 승인 기록을 갖는다

| | |
|---|---|
| **위반 시** | `on_invalidation: accept`인데 `accepted_by`가 없으면 조치를 무효로 보고 `escalate`로 전환 |
| **근거** | "감수하기로 했다"는 반드시 책임 주체가 있어야 한다 |

---

## 6. Lifecycle

```
Stated → Validated → Holding ──▶ AtRisk ──▶ Invalidated ──▶ Resolved
             │           │  ▲                    │
             │           ▼  │                    ▼
             │         Stale ┘              Accepted (명시적 승인)
             │
             └──▶ Rejected  (검증 결과 처음부터 거짓)
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Stated** | 명시됨. 아직 검증 전 | Planner 추출 또는 사용자 입력 |
| **Validated** | 최초 검증 통과 | `validation.method` 수행 성공 |
| **Holding** | 현재 참으로 유지됨 | 주기 검증 통과 |
| **Stale** | 검증 주기 초과. 참인지 모름 | `now − last_checked_at > interval` |
| **AtRisk** | 깨질 조짐이 관측됨 | 조기 경보 지표 도달 |
| **Invalidated** | 깨짐 | `invalidation_criteria` 충족 |
| **Accepted** | 깨졌으나 감수하기로 승인됨 | 인간의 명시적 승인 |
| **Resolved** | 조치 완료 (Replan 등) | `on_invalidation` 수행 완료 |
| **Rejected** | 처음부터 거짓이었음 | 최초 검증 실패 |

### 6.1 AtRisk가 필요한 이유

가정은 대개 **갑자기 깨지지 않는다.** 조짐이 있다.

```
asm_012  광고비 300만원 유지  confidence 0.85  Holding
   │
   │ 관측: 8월 집행액이 예산의 40%에서 조기 소진
   ▼
AtRisk   조기 경보 발동 → 대표에게 확인 요청
   │
   ├── 확인 결과 "예산 유지" → Holding 복귀, confidence 0.90으로 상향
   └── 확인 결과 "200만원으로 축소" → Invalidated → replan
```

`AtRisk` 단계가 없으면 계획은 **깨진 뒤에야** 대응하게 된다.

---

## 7. Relationships

```
Goal 001 ──1:0..N──▶ Assumption 017 ──1:0..1──▶ Risk 018
Plan 008 ──1:0..N──▶      │
                          ├──의존──▶ Plan 008 / Task 005  (dependents)
                          ├──깨짐──▶ Replanning (Process) ──▶ Plan 008 (새 버전)
                          ├──검증──▶ Context 003 (관측값 제공)
                          └──발생──▶ Event 020 (assumption.invalidated)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Goal](e001-goal.md) | Goal이 전제하는 가정 | `Goal 1:0..N Assumption` |
| [Plan](e008-plan.md) | Plan이 전제하는 가정. 깨지면 Replanning | `Plan 1:0..N Assumption` |
| [Task](e005-task.md) | 상속받거나 자체 가정을 가진다 | `Task 1:0..N Assumption` |
| [Risk](e018-risk.md) | 가정이 깨질 가능성이 Risk다 | `Assumption 1:0..1 Risk` |
| [Constraint](e004-constraint.md) | 대비 개념. 혼동하면 안 된다 (§2) | — |
| [Context](e003-context.md) | 검증에 필요한 관측값을 제공 | `Context N:M Assumption` |
| [Event](e020-event.md) | 상태 전이마다 발생 | `Assumption 1:N Event` |
| [Decision](e009-decision.md) | 깨진 가정은 Decision 재검토를 유발 | `Assumption 1:0..N Decision` |

---

## 8. Canonical Representation

```json
{
  "assumption_id": "asm_012",
  "scope": { "goal_id": "goal_001", "plan_id": "plan_014" },
  "type": "economic",
  "statement": "윈터캠프 광고비 월 300만원이 2026년 12월까지 유지된다",
  "confidence": 0.85,
  "impact": "high",
  "validation": {
    "method": "human_confirmation",
    "source": "human:대표",
    "interval": "P7D",
    "last_checked_at": "2026-08-04T09:00:00Z",
    "invalidation_criteria": "월 집행 가능액 < 3000000 KRW"
  },
  "early_warning": {
    "metric": "monthly_spend_ratio",
    "threshold": 0.6,
    "window": "P10D"
  },
  "dependents": ["plan_014", "task_006"],
  "linked_risk_id": "rsk_007",
  "on_invalidation": "replan",
  "fallback_plan_ref": null,
  "status": "Holding",
  "invalidated_at": null,
  "created_at": "2026-08-01T10:00:00Z",
  "created_by": "planner:v2"
}
```

기계가 읽을 수 있는 스키마: [`assumption.schema.json`](../intent-os-spec/schemas/assumption.schema.json)

---

## 9. Validation Rules

```
Assumption 생성 요청
  ↓
statement 반증 가능성 검사 (ASM-001)
  판정: invalidation_criteria가 관측 가능한 값으로 표현되었는가
  ── 아니면 반려 + 구체화 요구
  ↓
scope 존재 확인 (Goal / Plan / Task가 실제로 존재하는가)
  ↓
dependents 존재 확인 (ASM-002) ── 비어 있으면 경고 (관리 대상 아님)
  ↓
상위 Assumption과의 모순 검사 (INV-ASM-05) ── 모순 시 반려
  ↓
on_invalidation 확인 (INV-ASM-02) ── 없으면 escalate 기본값 + 경고
  ↓
validation.interval 확인 ── 없으면 impact 기반 기본값 부여
  high: P7D  /  medium: P14D  /  low: P30D
  ↓
linked_risk_id 자동 생성 여부 판단
  impact = high AND confidence < 0.9  →  Risk 자동 생성 (e018)
  ↓
Stated 생성 → 최초 검증 큐 등록 → Event 발행
```

### 9.1 Assumption Extraction — 암묵적 가정 추출

Planner가 Plan을 만들 때 반드시 수행한다(Rule ASM-005).

```
Plan 초안
  ↓
질문 1: 이 Plan이 성립하려면 무엇이 참이어야 하는가
  ├── 자원 관점  누가·무엇이 가용해야 하는가        → resource
  ├── 비용 관점  얼마가 확보되어야 하는가            → economic
  ├── 시간 관점  언제까지 무엇이 끝나야 하는가        → temporal
  ├── 사람 관점  누가 어떻게 행동해야 하는가          → behavioral
  ├── 환경 관점  외부에서 무엇이 변하지 않아야 하는가  → environmental
  ├── 데이터 관점 어떤 데이터가 정확해야 하는가        → data
  └── 기술 관점  어떤 성능이 유지되어야 하는가        → technical
  ↓
질문 2: 각 항목은 시스템이 통제 가능한가
  ├── Yes → Constraint로 등록 (e004)
  └── No  → Assumption으로 등록 (본 문서)
  ↓
질문 3: 각 가정의 반증 조건을 관측 가능한 값으로 표현할 수 있는가
  ├── Yes → Assumption 확정
  └── No  → 더 구체적인 문장으로 분해
  ↓
Priority = impact × (1 − confidence) 계산 → 검증 자원 배분
```

**질문 2가 핵심이다.** 통제 가능하면 Constraint, 불가능하면 Assumption이다.

### 9.2 검증 파이프라인 (주기 실행)

```
매 검증 주기
  ↓
status ∈ {Holding, Stale, AtRisk} 인 Assumption 조회
  ↓
Priority 내림차순 정렬 (ASM-006)
  ↓
각 Assumption에 대해
  ├── validation.method 실행 (Context 조회 / 인간 확인 / 외부 API)
  ├── invalidation_criteria 평가
  │     ├── 충족   → Invalidated → on_invalidation 실행
  │     ├── 미충족 + early_warning 도달 → AtRisk
  │     └── 미충족 → Holding, last_checked_at 갱신
  └── Event 발행
  ↓
Invalidated 발생 시
  ├── dependents의 Plan을 Suspended로 전이 (INV-ASM-03)
  ├── on_invalidation 별 분기
  │     replan       → Replanning 큐 등록
  │     adjust_scope → Goal 목표치 조정 제안 생성
  │     substitute   → fallback_plan_ref 활성화
  │     escalate     → 인간에게 알림
  │     accept       → 승인 요청 (INV-ASM-06)
  └── linked_risk_id의 Risk를 Materialized로 전이 (e018)
```

---

## 10. Examples

### 예시 1 — 예산 가정이 깨짐

```
asm_012  광고비 월 300만원 유지  confidence 0.85  impact high  Holding
   │
   │ 2026-08-14  월 집행 비율 62% 관측 (임계값 60% 초과)
   ▼
AtRisk → 대표 확인 요청
   │
   │ 2026-08-15  대표: "9월부터 200만원으로 줄인다"
   ▼
Invalidated  (invalidation_criteria: 월 집행 가능액 < 300만원 충족)
   │
   ├── plan_014 → Suspended
   ├── rsk_007 → Materialized
   └── on_invalidation: replan
        ↓
   plan_015 생성 (예산 200만원 기준, 목표 100명 → 유료 광고 비중 축소 + SEO 강화)
```

가정을 명시하지 않았다면 9월 중순에 예산이 바닥나고 나서야 알았을 것이다.

### 예시 2 — Resource 가정 (인간)

```json
{
  "assumption_id": "asm_020",
  "scope": { "goal_id": "goal_001", "plan_id": "plan_014", "task_id": "task_009" },
  "type": "resource",
  "statement": "김 카피라이터가 2026년 12월 첫 2주에 검수 작업이 가능하다",
  "confidence": 0.7,
  "impact": "medium",
  "validation": {
    "method": "calendar_check",
    "source": "human:copywriter_kim",
    "interval": "P7D",
    "invalidation_criteria": "12/01~12/14 가용 시간 < 8시간"
  },
  "dependents": ["task_009"],
  "on_invalidation": "substitute",
  "fallback_plan_ref": "task_009_alt_ai_review",
  "status": "Holding"
}
```

`confidence 0.7`은 낮은 편이다. 그래서 `on_invalidation: substitute`와 대체안(AI 검수)이 미리 준비되어 있다.

### 예시 3 — Technical 가정 (자동 검증)

```json
{
  "assumption_id": "asm_031",
  "scope": { "goal_id": "goal_001", "plan_id": "plan_014" },
  "type": "technical",
  "statement": "Claude의 한국어 카피 작성 성능이 현재 수준(observed_score 93)을 유지한다",
  "confidence": 0.9,
  "impact": "medium",
  "validation": {
    "method": "drift_detection",
    "source": "resource_intelligence",
    "interval": "P1D",
    "invalidation_criteria": "observed_score < 85 for 3 consecutive windows"
  },
  "dependents": ["dec_101", "task_004"],
  "on_invalidation": "substitute",
  "status": "Holding"
}
```

이 가정은 [Volume 4-B](../v4b-resource-intelligence.md)의 Drift 감지가 자동으로 검증한다. **사람이 개입하지 않는다.**

### 예시 4 — Constraint와의 짝

같은 예산을 두고 두 Entity가 각각 존재한다.

| Entity | 내용 | 위반 시 |
|---|---|---|
| Constraint `cn_003` | 광고비 집행 총액 ≤ 3,000,000 KRW | 실행 차단 (시스템이 잘못) |
| Assumption `asm_012` | 광고비 3,000,000 KRW가 확보된다 | Replanning (세계가 변함) |

**둘 다 있어야 한다.** Constraint만 있으면 예산이 줄어든 것을 모르고, Assumption만 있으면 예산을 초과 집행한다.

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **가정이 깨졌는데 이미 Goal이 완료됨** | Replanning하지 않는다. `Resolved`로 전이하고 "완료 후 무효화" 이력만 남긴다. 다음 유사 Goal의 Planner 입력이 된다 |
| **검증 대상(대표)이 응답하지 않음** | `Stale` 유지. `Invalidated`로 보지 않는다. **모르는 것과 거짓인 것은 다르다.** 단 Stale이 검증 주기의 3배를 넘으면 `escalate` |
| **가정이 깨졌다가 다시 참이 됨** | `Invalidated → Resolved` 후 **새 Assumption을 만든다.** 되살리지 않는다. 깨졌던 기간의 이력이 보존되어야 한다 |
| **여러 Plan이 같은 가정에 의존** | `dependents`에 전부 기록. 깨지면 **전부** Suspended. 하나만 처리하고 나머지를 방치하면 INV-10 위반이다 |
| **가정과 Context가 충돌** | Context(관측된 사실)가 우선한다. 충돌은 곧 `invalidation_criteria` 충족을 의미하므로 즉시 `Invalidated` |
| **confidence 1.0인 가정** | 허용하지 않는다. 확실한 것은 가정이 아니라 Context나 Constraint다. 최대 0.99로 제한한다 |
| **Planner가 가정을 하나도 추출하지 못함** | 추출 실패의 신호다. 모든 Plan에는 최소 하나의 가정이 있다(적어도 "필요한 Resource가 가용하다"). 경고를 발행하고 §9.1의 7개 관점 질문을 강제한다 |
| **가정이 100개를 넘음** | 관리 불능 신호. `Priority = impact × (1 − confidence)` 상위 20개만 능동 검증하고 나머지는 `passive`로 표시한다. 능동 검증에서 빠졌다는 사실을 명시적으로 기록한다 |
| **on_invalidation: accept인데 승인자가 없음** | INV-ASM-06 위반. `escalate`로 자동 전환한다. 시스템이 스스로 "감수하기로" 결정할 수 없다 |

---

## 12. Open Issues (v1.0)

### 가정 추출의 자동화 수준

§9.1의 7개 관점 질문은 사람이 만든 체크리스트다. LLM Planner가 이를 얼마나 신뢰성 있게 수행하는지, 놓친 가정을 어떻게 사후에 발견하는지(실패 원인 분석 → 가정 역추출)가 미정이다.

### confidence의 산출 근거

현재 `confidence`는 대부분 사람이 부여하는 주관적 값이다. 과거 유사 가정의 유지율에서 통계적으로 추정하는 방법이 필요하다.

### 가정 간 의존 관계

"광고비가 유지된다"가 깨지면 "12월 전에 랜딩페이지가 완성된다"도 흔들린다. 현재는 가정끼리의 의존을 표현할 수 없다. 가정 그래프(Assumption Graph)가 필요한지 검토가 필요하다.

### 조기 경보 임계값의 학습

`early_warning.threshold`를 사람이 정하고 있다. 과거에 가정이 깨졌을 때의 선행 지표를 학습해 자동 설정하는 것이 이상적이다.

### 앞으로 보강해야 할 항목

- Assumption과 Constraint의 자동 분류기 (통제 가능성 판정)
- 가정 무효화가 Goal Graph를 타고 전파되는 규칙 ([e001a §14](e001a-goal-graph.md)와 연동)
- `passive` 가정의 샘플링 검증 전략
- 실제 예시 30~50개
