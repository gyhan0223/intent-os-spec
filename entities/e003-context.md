# Entity 003: Context

- **Version:** v2.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Context is the structured representation of the current world state that surrounds a Goal — everything the system must know about "now" to reason correctly about the future.**

> Context는 Goal을 둘러싼 현재 세계 상태의 구조화된 표현이다. 미래(Goal)를 올바르게 추론하기 위해 시스템이 "지금"에 대해 알아야 하는 모든 것이다.

핵심 단어는 **Current(현재)** 이다.

Goal이 **미래 상태**라면, Context는 **현재 상태**다. Planner는 이 둘의 차이(Gap)를 좁히는 경로를 계산한다.

```
Context (현재)  ──── Gap ────▶  Goal (미래)
```

Context는 Goal만 참조하는 것이 아니다. **Intent 추론, Task 실행, Decision, Assumption 검증 모두가 Context를 참조한다.** 그래서 독립 Entity다.

---

## 2. Context는 무엇이 아닌가?

이게 정의보다 훨씬 중요하다.

### Context는 Goal이 아니다

❌ `학생 100명 모집` — 미래 상태다. [Goal](e001-goal.md)이다.

✅ `현재 등록자 20명` — 현재 상태다. Context다.

### Context는 Constraint가 아니다

`예산 300만원`은 두 얼굴을 가진다.

- **Context 관점:** "현재 가용 예산이 300만원이다" — 사실(Fact)
- **Constraint 관점:** "300만원을 초과하면 안 된다" — 규칙(Rule)

Context는 **세계를 서술**하고, [Constraint](e004-constraint.md)는 **행동을 제한**한다.

### Context는 Assumption이 아니다

❌ `광고비 300만원이 12월까지 유지된다` — 이건 [Assumption](e017-assumption.md)이다.

**같은 예산을 두고 세 Entity가 각각 존재한다.** 이 삼각형이 Intent OS 거버넌스의 기본형이다.

| Entity | 내용 | 시점 | 틀렸을 때 |
|---|---|---|---|
| **Context** `ctx_001` | 현재 가용 예산이 300만원이다 | 지금 | 재수집 |
| **Constraint** `cn_003` | 집행 총액 ≤ 300만원 | 항상 | 위반 → 차단 |
| **Assumption** `asm_012` | 300만원이 12월까지 유지된다 | 미래 | 무효화 → Replanning |

Context는 **관측된 사실**, Assumption은 **검증되지 않은 믿음**이다. Context는 수집(collect)하고 Assumption은 검증(validate)한다.

### Context는 Memory가 아니다

[Memory](e010-memory.md)는 시스템이 축적하는 **장기 저장소**다. Context는 그중 **지금 이 추론에 필요한 부분만 선별해 로드한 스냅샷**이다.

```
Memory (전체 저장소)
   ↓ 선별 + 로드
Context (현재 추론용 스냅샷)
```

### Context는 Knowledge가 아니다

[Knowledge](e011-knowledge.md)는 일반 법칙이다(`교육 업종 광고는 학기 전에 효과가 높다`). Context는 특정 상황의 사실이다(`이 학원의 현재 등록자는 20명이다`).

### Context는 Session이 아니다

❌ `이번 대화에서 오간 내용` — 이건 [Session](e021-session.md)의 대화 버퍼다.

Session은 일시적 Context를 **보유**하지만(`context_ref`), Context 자체는 Session보다 오래 살 수 있다. Global Scope Context는 Session이 끝나도 남는다([INV-16](e000a-entity-relationships.md)).

---

## 3. Design Principles

### Rule C-001 — 사실(Fact)만 담아야 한다

✅ `현재 등록자 20명` / `지역: 홍대` / `경쟁 학원 3곳 존재`

❌ `홍보를 강화해야 한다` — 판단이다. [Intent](e002-intent.md)의 영역이다.

❌ `광고비가 유지될 것이다` — 미래에 대한 믿음이다. [Assumption](e017-assumption.md)의 영역이다.

### Rule C-002 — 모든 항목은 출처(Source)를 가져야 한다

출처 없는 Context는 검증할 수 없고, 검증할 수 없는 Context 위의 추론은 신뢰할 수 없다.

### Rule C-003 — 모든 항목은 수집 시각(Collected At)을 가져야 한다

Freshness(§4.2) 계산의 전제 조건이다.

### Rule C-004 — Scope가 명시되어야 한다

Global / Goal-level / Task-level 중 하나(§4.1).

### Rule C-005 — 추정은 사실인 척하면 안 된다

추정된 항목은 반드시 `source: inferred`로 표시한다. **추정 표시 없는 추정은 시스템 전체의 신뢰를 오염시킨다.**

### Rule C-006 — 실행은 Context를 보존해야 한다

[Volume 3 §8](../v3-runtime.md)의 "Preserve Context"와 동일한 원칙이다. 모든 실행 단계는 이전 단계의 Context를 유지·전달해야 한다.

### Rule C-007 — 전체를 전달하지 않는다

추론에 필요한 항목만 선별해 전달한다(§9). 전체 Context를 매번 전달하면 비용이 커지고 관련 없는 정보가 추론을 흐린다.

---

## 4. Attributes

```
Context
├── Identity
│   ├── context_id
│   ├── scope
│   └── goal_id / task_id
├── Content
│   ├── current_state
│   ├── environment
│   ├── user_profile
│   ├── history
│   └── available_resources
└── Metadata
    └── items_meta[]        (항목별 source / collected_at / ttl / freshness)
```

| 영역 | 의미 | 예 |
|---|---|---|
| **current_state** | Goal 대상의 현재 값 | `현재 등록자 20명`, `상담 문의 주 5건` |
| **environment** | 외부 환경 | `지역 홍대`, `경쟁 학원 3곳`, `겨울방학 시즌` |
| **user_profile** | 사용자/조직 정보 | `신규 학원, 개원 6개월, 대표 1인 운영` |
| **history** | 과거 이력 | `지난 여름캠프 등록 35명, 블로그 광고 CTR 2%` |
| **available_resources** | 가용 자원 | `예산 300만원, 마케팅 인력 0명, 인스타 계정 보유` |
| **items_meta** | 항목별 메타데이터 | source / collected_at / ttl / freshness |

**History가 있어야 Prediction이 가능하다.** 지난 여름캠프 데이터가 없으면 윈터캠프 모집 예측은 일반 [Knowledge](e011-knowledge.md)에만 의존해야 한다.

### 4.1 Context Scope

```
Global Context
└── Goal-level Context
      └── Task-level Context
```

| Scope | 의미 | 예 | Session 종료 시 |
|---|---|---|---|
| **Global** | 모든 Goal이 공유 | 사용자 프로필, 조직 정보, 지역, 시간대 | 유지 |
| **Goal-level** | 특정 Goal에 종속 | 현재 등록자 20명, 윈터캠프 일정 | 유지 |
| **Task-level** | 특정 Task 실행 중 생성/사용 | 광고 A안의 어제 CTR 3.2% | **폐기** |

#### Scope 규칙

1. 하위 Scope는 상위 Scope를 **상속**한다. Task는 Goal Context와 Global Context를 모두 볼 수 있다.
2. 충돌 시 **더 구체적인(하위) Scope가 우선**한다.
3. Task-level Context 중 Goal 전체에 의미 있는 것은 Goal-level로 **승격(Promotion)** 될 수 있다.
   예: 광고 실험에서 발견한 `학부모 타겟이 학생 타겟보다 전환율 3배`는 Goal-level 사실이다.
4. **Session이 폐기하는 것은 Task-level Context뿐이다**([INV-SES-01](e021-session.md)).

### 4.2 Context Freshness

Context는 **시간이 지나면 부패한다.** 오래된 Context 위의 추론은 오답을 만든다.

```
Fresh → Stale → Expired
```

| 상태 | 의미 | 시스템 반응 |
|---|---|---|
| **Fresh** | TTL 이내 | 그대로 사용 |
| **Stale** | TTL 초과, 만료 전 | 사용 가능하나 Confidence 감점, 갱신 시도 |
| **Expired** | 만료 | **추론에 사용 금지**, 재수집 필수 |

TTL은 항목의 성격에 따라 다르다.

| 항목 | TTL 예 |
|---|---|
| 광고 CTR | 1일 |
| 현재 등록자 수 | 1일 |
| 경쟁 학원 현황 | 30일 |
| 지역/조직 정보 | 180일 |

**Freshness는 [Intent Confidence](e002-intent.md)의 직접 입력이다.** Stale한 Context로 추론한 Intent는 Confidence가 깎인다([e002 §9.1](e002-intent.md)).

### 4.3 Source와 신뢰도

| Source | 예 | 신뢰도 |
|---|---|---|
| `user_input` | "예산은 300만원이야" | 높음 |
| `system_observation` | 실행 결과, 등록 DB 조회 | 높음 |
| `external_source` | 검색, API, 시장 데이터 | 중간 |
| `inferred` | "신규 학원이므로 인지도 낮을 것" | 낮음 — 반드시 표시 (Rule C-005) |

---

## 5. Invariants

### INV-C-01 — 모든 Context 항목은 source와 collected_at을 가진다

| | |
|---|---|
| **위반 시** | 항목을 추론에서 제외하고 재수집 큐에 넣는다. 조용히 사용하지 않는다 |
| **근거** | 출처와 시각이 없으면 Freshness도 신뢰도도 계산할 수 없다 (Rule C-002, C-003) |

### INV-C-02 — Expired 항목은 추론에 사용되지 않는다

| | |
|---|---|
| **위반 시** | Loading 단계에서 차단하고 재수집을 트리거한다. 만료된 사실 위의 결정은 재현 불가능한 오류를 만든다 |

### INV-C-03 — inferred 항목은 사실로 승격되지 않는다

추정값이 관측값으로 바뀌려면 새로 수집되어야 한다. `source`를 고쳐 쓰지 않는다.

| | |
|---|---|
| **위반 시** | 쓰기 거부. 추정이 사실로 둔갑하면 그 위의 모든 추론이 오염된다 |

### INV-C-04 — 하위 Scope가 상위 Scope를 덮어쓰지 않는다

Task-level 값이 Goal-level 값보다 우선하지만, **원본을 수정하지는 않는다.** 병합은 읽기 시점에 일어난다.

| | |
|---|---|
| **위반 시** | 다른 Task가 오염된 Goal Context를 보게 된다. 쓰기를 거부하고 Promotion 절차를 요구한다 |

### INV-C-05 — Session 종료가 Global/Goal Context를 삭제하지 않는다

[INV-16](e000a-entity-relationships.md)의 Context 측 표현이다.

| | |
|---|---|
| **위반 시** | 삭제 차단. 폐기 대상은 Task-level Context뿐이다 |

### INV-C-06 — 판단성 항목을 담지 않는다

`should_*`, `recommended`, `better` 같은 키가 나타나면 Rule C-001 위반이다.

| | |
|---|---|
| **위반 시** | 쓰기 거부. 해당 내용은 [Intent](e002-intent.md) 또는 [Knowledge](e011-knowledge.md)로 보낸다 |

### INV-C-07 — Context 변경은 참조자에게 전파된다

| | |
|---|---|
| **위반 시** | 예산이 바뀌었는데 Plan이 그대로면 잘못된 계획이 실행된다. 변경 감지 시 영향 범위 계산을 강제한다 (§9.2) |

---

## 6. Lifecycle

Context는 **항목 단위로** 수명을 가진다. Context 객체 자체가 아니라 각 항목이 부패한다.

```
Collected → Fresh → Stale → Expired ──▶ Recollected (새 항목)
                       │
                       └──▶ Promoted   (Task-level → Goal-level)
                            Superseded (충돌 해소로 대체됨)
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Collected** | 수집됨. 검증 전 | 수집 파이프라인 |
| **Fresh** | TTL 이내 | 검증 통과 |
| **Stale** | TTL 초과, 만료 전 | `now − collected_at > ttl` |
| **Expired** | 만료. 사용 금지 | `now − collected_at > ttl × expiry_factor` |
| **Promoted** | 상위 Scope로 승격됨 | §4.1 규칙 3 |
| **Superseded** | 더 신뢰도 높은 값으로 대체됨 | 충돌 해소 (§9.3) |

**Expired 항목을 지우지 않는다.** "그때 시스템이 무엇을 알고 있었는가"는 [Decision](e009-decision.md)의 `inputs_snapshot` 재현에 필요하다.

---

## 7. Relationships

```
                ┌── Goal 001        : Gap 계산의 기준점
                ├── Intent 002      : 추론의 Evidence
                ├── Constraint 004  : 사실 → 규칙 파생
Context 003 ────┼── Task 005        : 실행 파라미터 공급
                ├── Decision 009    : inputs_snapshot의 일부
                ├── Assumption 017  : 검증에 필요한 관측값 제공
                ├── Session 021     : 일시적 Context 보유
                └── Memory 010      : 저장소 ↔ 스냅샷
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Goal](e001-goal.md) | Gap 계산의 현재값 | `Context N:M Goal` |
| [Intent](e002-intent.md) | 추론의 Evidence를 제공 | `Context N:M Intent` |
| [Constraint](e004-constraint.md) | 사실이 규칙으로 파생될 수 있다 (`origin: derived_from_context`) | `Context 1:0..N Constraint` |
| [Task](e005-task.md) | 실행 파라미터 공급 | `Context N:M Task` |
| [Decision](e009-decision.md) | `inputs_snapshot`에 Context 참조가 동결된다 | `Context N:M Decision` |
| [Assumption](e017-assumption.md) | 가정 검증에 필요한 관측값을 제공한다 | `Context N:M Assumption` |
| [Memory](e010-memory.md) | Context는 Memory에서 로드된 스냅샷이다 | `Memory 1:0..N Context` |
| [Session](e021-session.md) | 일시적 Context를 보유. **Task-level만 함께 소멸** | `Session 1:0..1 Context` |
| [Resource Profile](e025-resource-profile.md) | Context 축이 Profile 점수의 범위를 결정한다 | `Context N:M Resource Profile` |

### 7.1 Context와 Resource Profile의 Context 축

두 곳에서 "Context"라는 말을 쓰지만 다른 것이다.

| | Entity 003 Context | Profile의 `context` 필드 |
|---|---|---|
| 대상 | 이 Goal의 현재 세계 상태 | 점수가 유효한 **범위 라벨** |
| 예 | `등록자 20명, 지역 홍대` | `{domain: 교육, language: ko, audience: 학부모}` |
| 용도 | 추론의 입력 | 점수 조회 키 |

Profile의 Context 축은 **Entity 003에서 파생될 수 있다** — 이 Goal의 `environment.지역`과 `user_profile.업종`이 `{domain: 교육}`을 결정한다. 그 매핑 규칙은 미결이다(§12).

---

## 8. Canonical Representation

```json
{
  "context_id": "ctx_001",
  "scope": "Goal",
  "goal_id": "goal_001",
  "current_state": {
    "등록자": { "value": 20, "unit": "명" },
    "상담문의": { "value": 5, "unit": "건/주" }
  },
  "environment": {
    "지역": "홍대",
    "시즌": "겨울방학",
    "경쟁학원수": { "value": 3, "unit": "곳" }
  },
  "user_profile": {
    "조직": "신규 학원, 개원 6개월",
    "운영형태": "대표 1인 운영"
  },
  "history": [
    { "event": "여름캠프", "결과": "등록 35명", "period": "2026-06" },
    { "event": "블로그 광고", "결과": "CTR 2.0%", "period": "2026-07" }
  ],
  "available_resources": {
    "예산": { "value": 3000000, "unit": "KRW" },
    "마케팅인력": { "value": 0, "unit": "명" }
  },
  "items_meta": [
    {
      "key": "current_state.등록자",
      "source": "system_observation",
      "collected_at": "2026-08-04T09:00:00Z",
      "ttl_hours": 24,
      "freshness": "Fresh"
    },
    {
      "key": "environment.경쟁학원수",
      "source": "external_source",
      "collected_at": "2026-07-20T11:00:00Z",
      "ttl_hours": 720,
      "freshness": "Fresh"
    },
    {
      "key": "user_profile.운영형태",
      "source": "inferred",
      "collected_at": "2026-08-01T10:00:00Z",
      "ttl_hours": 4320,
      "freshness": "Fresh",
      "inference_basis": "사업자 등록 정보에 직원 등록 없음"
    }
  ]
}
```

기계가 읽을 수 있는 스키마: [`context.schema.json`](../intent-os-spec/schemas/context.schema.json)

---

## 9. Validation Rules

### 9.1 Loading

Runtime의 각 단계는 Context를 이렇게 로드한다.

```
요청 (Goal / Intent / Task / Decision / Assumption 검증)
  ↓
Scope 결정 (Global + Goal + Task 병합, 하위 우선 — INV-C-04)
  ↓
Freshness 검사 (§4.2)
  ├── Expired  → 추론에서 제외 + 재수집 큐 (INV-C-02)
  ├── Stale    → 사용 + 갱신 시도 + Confidence 감점 표시
  └── Fresh    → 그대로 사용
  ↓
source 검사 (INV-C-01) ── 없는 항목 제외
  ↓
Relevance 필터 (이 추론에 필요한 항목만 — Rule C-007)
  ↓
Context Snapshot 생성 → 추론 엔진 전달
```

### 9.2 수집과 갱신

```
Context 변경 감지
  ↓
판단성 필드 검사 (INV-C-06) ── should_* / recommended 검출 시 거부
  ↓
source / collected_at 부여 (INV-C-01)
  ↓
기존 값과 충돌? ── §9.3
  ↓
Freshness 갱신
  ↓
영향 범위 계산 (INV-C-07)
  어느 Goal / Intent / Plan / Assumption이 이 항목을 참조하는가
  ↓
전파
  ├── Assumption 검증 트리거      → e017 §9.2
  ├── Intent confidence 재계산    → e002 §9.1
  ├── Goal Propagation            → e001a §14
  └── Replanning 트리거 (필요 시) → e008 §6.2
  ↓
Event 발행 (context.updated)
```

예)

```
광고 예산: 300만원 → 200만원 (사용자 입력)
  ↓ 참조 추적
goal_001 / intent_001 / plan_014 / asm_012
  ↓
asm_012 (예산 300만원 유지) → invalidation_criteria 충족 → Invalidated
  ↓
plan_014 → Suspended → Replanning
```

**[Goal Propagation](e001a-goal-graph.md)의 실제 발화 지점은 대부분 Context 변경이다.**

### 9.3 충돌 해소

같은 키에 다른 값이 들어올 수 있다.

```
user_input:          등록자 25명
system_observation:  등록자 20명 (DB 조회)
```

해소 규칙:

```
① source 신뢰도 비교 (§4.3)
   system_observation ≥ user_input > external_api > inferred
② 같으면 collected_at이 최신인 값
③ 그래도 같으면 사용자에게 고지하고 확인 요청
  ↓
채택되지 않은 값 → Superseded (삭제하지 않는다)
  ↓
불일치 자체를 기록 — 반복되면 수집 파이프라인의 결함 신호
```

**사용자 입력이 항상 이기지는 않는다.** 사람은 최신 DB 값을 모를 수 있다. 다만 불일치를 조용히 넘기지 않고 반드시 고지한다.

---

## 10. Examples

### 예시 1 — Gap 계산

```
Context ctx_001              Goal goal_001
current_state.등록자 = 20  →  target = 100
                    Gap = 80명
                     ↓
Intent 추출 (e002 §9)
```

Context 없이는 Gap을 계산할 수 없고, Gap 없이는 Intent를 추론할 수 없다.

### 예시 2 — Freshness가 Confidence를 깎는다

```
2026-08-04  intent_001 추론
  evidence: ctx_001#current_state.상담문의 (Fresh, 수집 2시간 전)
  confidence: 0.85
   ↓
2026-08-20  같은 근거로 재추론 시도
  evidence: ctx_001#current_state.상담문의 (Stale, TTL 24h 초과)
  confidence: 0.85 → 0.68  ← Freshness 감점
   ↓
0.68 < 0.8 → 자동 Selected 불가. 재수집 우선.
```

### 예시 3 — Task-level Context의 승격

```
task_006 실행 중 관측
  Task-level: "광고 A안(학부모 소구) CTR 3.2%"
              "광고 B안(학생 소구) CTR 1.1%"
   ↓ Goal 전체에 의미 있는 사실인가? → Yes
   ↓ Promotion (§4.1 규칙 3)
Goal-level: "학부모 타겟이 학생 타겟보다 전환율 약 3배"
   ↓
이후 모든 Task가 이 사실을 상속한다
   ↓ 반복 관측되면
Memory → Knowledge 승격 후보 (e011 §7)
```

**Task-level은 Session과 함께 사라지지만, 승격된 것은 살아남는다.**

### 예시 4 — 추정과 사실의 구분

```json
{
  "key": "user_profile.인지도",
  "value": "낮음",
  "source": "inferred",
  "inference_basis": "개원 6개월 미만 + 온라인 리뷰 3건 미만",
  "collected_at": "2026-08-01T10:00:00Z",
  "freshness": "Fresh"
}
```

이 항목을 근거로 추론한 [Intent](e002-intent.md)의 confidence는 낮게 시작한다. 나중에 실제 인지도 조사가 수행되면 **새 항목이 수집되고**(`source: external_source`) 이 항목은 `Superseded`가 된다. **`source`를 `external_source`로 고쳐 쓰지 않는다**(INV-C-03).

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **Context가 거의 비어 있음 (신규 사용자)** | 정상이다. Gap 계산이 불가능하면 [Goal Clarification](e001d-goal-validation.md)으로 질문을 생성한다. 빈 Context를 추정으로 채우지 않는다 |
| **모든 항목이 Expired** | 추론을 중단하고 재수집을 먼저 수행한다. Expired 위의 추론은 [INV-C-02](e000a-entity-relationships.md) 위반이다 |
| **사용자 입력과 시스템 관측이 충돌** | §9.3의 규칙을 적용하되 **반드시 고지한다.** 조용한 해소는 사용자가 시스템을 불신하게 만든다 |
| **TTL이 지났지만 값이 변할 리 없는 항목** | `지역: 홍대` 같은 항목이다. TTL을 길게(180일) 두되 Stale 자체는 정상 상태로 취급한다. TTL 자동 보정은 §12 미결 |
| **Task-level Context가 Goal-level과 충돌** | 하위가 우선한다(§4.1 규칙 2). 단 **원본은 수정하지 않는다**(INV-C-04). 병합은 읽기 시점에만 일어난다 |
| **Context 항목이 개인정보를 포함** | `user_profile`과 `history`가 대표적이다. [Policy](e019-policy.md)의 `privacy` 유형이 보존 기간과 접근 범위를 강제한다 |
| **Expired Context를 참조하는 과거 Decision 조회** | 허용한다. Expired 항목을 삭제하지 않는 이유다(§6). `inputs_snapshot` 재현에는 "그때의 값"이 필요하다 |
| **Context가 너무 커서 전달 비용이 큼** | Relevance 필터(Rule C-007)가 해결한다. 필터가 무엇을 제외했는지 기록해 "정보 부족으로 인한 오판"과 구분할 수 있어야 한다 |
| **inferred 항목만으로 Intent를 추론** | 허용하되 confidence를 크게 감점한다. 추정 위에 세운 추론임을 `rationale`에 명시한다 |

---

## 12. Open Issues (v2.0)

### ✅ v1.0에서 해소된 항목

| v1.0 Open Issue | 해소 |
|---|---|
| Context와 Memory의 경계 (쓰기 방향) | [Memory](e010-memory.md)의 기록 규칙 + §10 예시 3의 Promotion 경로로 정리 |
| 개인정보와 Context | [Policy](e019-policy.md)의 `privacy`·`data_retention` 유형이 강제 |

### Freshness TTL의 산정과 자동 보정

§4.2의 TTL은 예시 값이다. 항목 유형별 기본 TTL 테이블과, 학습을 통한 자동 보정(변화가 잦은 항목은 TTL 단축)이 필요하다. 현재는 모든 항목이 고정 TTL을 쓴다.

### Context 항목의 표준 키 체계

`current_state.등록자` 같은 키가 자유 문자열이다. [Capability Taxonomy](e006a-capability-taxonomy.md)처럼 표준 온톨로지가 없으면 Goal 간·조직 간 비교가 불가능하다.

### Profile의 Context 축과의 매핑

§7.1에서 지적한 문제다. Entity 003의 `environment`·`user_profile`에서 [Resource Profile](e025-resource-profile.md)의 Context 축(`{domain, language, audience}`)을 어떻게 도출하는가. 매핑이 없으면 점수 조회 시 잘못된 Context로 질의하게 된다.

### Context Diff / Versioning

스냅샷 간 변경을 추적하는 표준이 없다. §9.2의 영향 범위 계산은 "무엇이 바뀌었는가"를 전제하는데, 그 표현 형식이 정의되지 않았다.

### 앞으로 보강해야 할 항목

- Context 항목 표준 키 온톨로지
- TTL 자동 보정 알고리즘
- Relevance 필터 알고리즘 상세화
- 실제 예시 30~50개
