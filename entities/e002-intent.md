# Entity 002: Intent

- **Version:** v2.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Intent is an inferred direction of solution derived from a Goal — it captures why the Goal exists and in which domain it should be solved, without specifying what to execute.**

> Intent는 Goal에서 추론된 해결의 방향이다. Goal이 왜 존재하는지, 어느 영역에서 풀어야 하는지를 담되, 무엇을 실행할지는 담지 않는다.

Intent는 Goal과 Task 사이의 **중간 계층**이다([Volume 1 §3.2](../v1-core-concepts.md)).

```
Request → Goal → Intent → Task
```

| 계층 | 담는 것 | 질문 |
|---|---|---|
| **Goal** | 원하는 미래 상태 | 무엇을 원하는가 |
| **Intent** | 해결의 방향과 이유 | 왜, 어느 방향으로 풀 것인가 |
| **Task** | 실행 단위 | 무엇을 실행하는가 |

핵심 단어는 **Inferred(추론된)** 이다. Goal은 사용자가 확정하지만, **Intent는 시스템이 추론한다.** 그래서 Intent에는 항상 Confidence(확신도)가 붙는다.

---

## 2. Intent는 무엇이 아닌가?

이게 정의보다 훨씬 중요하다.

### Intent는 Goal이 아니다

❌ `학생 100명 모집` — 이건 원하는 미래 상태다. [Goal](e001-goal.md)이다.

✅ `홍보 채널을 통해 신규 등록을 늘린다` — 방향이다. Intent다.

### Intent는 Task가 아니다

❌ `인스타그램 광고 제작` — 실행 단위다. [Task](e005-task.md)다.

Intent는 실행 가능한 작업이 아니라 **Task를 생성하기 위한 방향 제시**다.

### Intent는 Method가 아니다

❌ `유튜브 광고를 돌린다` — 특정 방법이다.

Intent는 해결 **영역(Domain)** 을 지목할 뿐, 특정 도구나 절차를 확정하지 않는다.

### Intent는 Request가 아니다

❌ `홍보 문구 하나 만들어줘` — 사용자의 입력 문장, 즉 Request다.

Request에서 Goal이 추출되고, Goal에서 Intent가 추론된다. 순서를 건너뛸 수 없다.

### Intent는 Plan이 아니다

❌ `조사 → 카피 → 집행 순서로 진행` — 이건 [Plan](e008-plan.md)이다.

Intent는 **방향 하나**이고 Plan은 **선택된 방향들을 실행 청사진으로 컴파일한 결과**다. 하나의 Plan이 여러 Intent를 동시에 수용할 수 있다.

### Intent는 Assumption이 아니다

❌ `광고비는 유지될 것이다` — 이건 [Assumption](e017-assumption.md)이다.

Intent는 **"이 방향으로 풀겠다"** 는 추론이고, Assumption은 **"이것이 참일 것이다"** 라는 전제다. 다만 둘 다 틀릴 수 있어서 확신도를 갖는다는 공통점이 있다. 차이는 **틀렸을 때의 조치**다 — Intent가 틀리면 다른 Intent로 전환하고, Assumption이 깨지면 Replanning한다.

---

## 3. Design Principles

### Rule I-001 — 반드시 하나의 Goal에서 파생되어야 한다

부모 Goal이 없는 Intent는 존재할 수 없다. 고립된 Intent는 시스템이 관리하지 않는다([INV-01](e000a-entity-relationships.md)).

### Rule I-002 — 해결 영역(Solution Domain)을 지목해야 한다

✅ `가격 구조 개선을 통한 등록 전환율 상승`

❌ `등록을 늘린다` — 방향이 없다. 이건 Goal의 반복일 뿐이다.

### Rule I-003 — 실행 단위(Task)를 포함하면 안 된다

- ❌ `랜딩페이지 A/B 테스트 실행`
- ✅ `상담 전환 프로세스 개선`

Resource 이름도 마찬가지로 금지된다([INV-09](e000a-entity-relationships.md)).

### Rule I-004 — Confidence를 가져야 한다

Intent는 추론 결과이므로 확신도 없이 Runtime으로 전달될 수 없다.

### Rule I-005 — 하나의 Goal은 여러 Intent를 가질 수 있다

```
Goal: 학생 모집

Intent:
  - 홍보 강화          (Confidence 0.9)
  - 가격 구조 개선      (Confidence 0.6)
  - 브랜드 신뢰 확보    (Confidence 0.7)
  - 상담 프로세스 개선  (Confidence 0.5)
  - 고객 경험 향상      (Confidence 0.4)
```

모든 Intent가 Task로 전개되는 것은 아니다. **Priority와 Confidence가 높은 Intent부터** Planner에 전달된다.

### Rule I-006 — Rationale과 Evidence를 남겨야 한다

**어떤 근거로 추론했는지 남지 않으면 Learning이 개선할 수 없다.** Evidence는 [Context](e003-context.md) 항목에 대한 참조여야 하며, 자유 문장으로 대체하지 않는다.

### Rule I-007 — Rejected Intent도 보존한다

탈락한 Intent를 지우지 않는다. **왜 탈락했는지가 Intent 추론 정확도 개선의 입력**이다. Rejected 이유가 사후에 틀렸던 것으로 드러나는 경우가 학습의 핵심 신호다(§10 예시 4).

---

## 4. Attributes

```
Intent
├── Identity
│   ├── intent_id
│   ├── goal_id
│   └── intent_type
├── Content
│   ├── direction
│   ├── rationale
│   └── evidence[]
├── Assessment
│   ├── confidence
│   ├── priority
│   └── expected_impact
└── Status
    ├── status
    └── rejection_reason
```

| 속성 | 의미 | 예 |
|---|---|---|
| **intent_id** | 식별자 | `intent_001` |
| **goal_id** | 어느 Goal에서 파생되었는가 (Rule I-001) | `goal_001` |
| **intent_type** | 해결 영역 (§4.1) | `Promotion` |
| **direction** | 방향 서술 | `타겟 지역(홍대) 학부모 대상 홍보 도달 확대` |
| **rationale** | 왜 이 방향인가 | `상담 전환율은 정상이나 유입 자체가 부족` |
| **evidence** | 추론 근거가 된 Context 항목 참조 | `["ctx_001#current_state.등록자", "ctx_001#history.여름캠프"]` |
| **confidence** | 추론 확신도 (0.0~1.0) | `0.85` |
| **priority** | Intent 간 우선순위 (§9.2) | High |
| **expected_impact** | Goal 달성 기여 예상 | `등록 +40~60명` |
| **status** | Intent의 상태 (§6) | Inferred |
| **rejection_reason** | 탈락 사유 (Rule I-007) | `null` |

### 4.1 Intent Types (Solution Domain)

Intent는 해결 영역에 따라 분류된다. 분류가 있어야 Planner가 Task 전개 전략을 선택할 수 있다.

```
Intent
├── Promotion Intent      (홍보)
├── Pricing Intent        (가격)
├── Brand Intent          (브랜드)
├── Process Intent        (프로세스)
├── Experience Intent     (고객 경험)
├── Product Intent        (제품/서비스)
└── Efficiency Intent     (비용/운영 효율)
```

| Type | 예시 | 주로 전개되는 Capability 도메인 |
|---|---|---|
| **Promotion** | `윈터캠프 홍보 도달 확대` | `language.generation.*`, `advertising.*` |
| **Pricing** | `조기 등록 할인으로 전환율 상승` | `analysis.financial` |
| **Brand** | `학원 브랜드 신뢰도 확보` | `verification.brand_tone`, `creation.*` |
| **Process** | `상담 → 등록 전환 프로세스 개선` | `analysis.customer_data`, `automation.*` |
| **Experience** | `기존 학생 만족도 기반 재등록 유도` | `communication.consultation` |
| **Product** | `커리큘럼 차별화` | `analysis.competitor`, `reasoning.strategy` |
| **Efficiency** | `광고 예산 300만원 내 도달 효율 극대화` | `analysis.metrics`, `advertising.budget_control` |

v1.0의 Domain 목록은 예시적이며, 도메인 온톨로지는 확장 가능해야 한다(§12).

---

## 5. Invariants

### INV-I-01 — 모든 Intent는 정확히 하나의 Goal을 참조한다

| | |
|---|---|
| **위반 시** | 생성 거부. 고아 Intent는 어느 Goal의 성과인지 집계할 수 없다 ([INV-01](e000a-entity-relationships.md)) |

### INV-I-02 — Intent에 Task나 Resource 식별자가 등장할 수 없다

| | |
|---|---|
| **위반 시** | Validation이 검출해 반려한다. Intent가 실행 단위를 담으면 Planner의 탐색 공간이 미리 좁혀진다 |
| **근거** | Rule I-003, [INV-09](e000a-entity-relationships.md) |

### INV-I-03 — confidence는 0.0~1.0 범위이며 1.0이 될 수 없다

추론은 확실할 수 없다. 확실하다면 그것은 사용자가 지정한 것이므로 `origin: user_declared`인 Goal의 일부다.

| | |
|---|---|
| **위반 시** | 생성 거부. 최대 0.99로 제한한다 |

### INV-I-04 — Selected Intent는 Constraint를 위반하지 않는다

Constraint Filtering을 통과하지 못한 Intent는 `Selected`가 될 수 없다.

| | |
|---|---|
| **위반 시** | `Rejected`로 전이하고 `rejection_reason`에 위반 Constraint를 기록 |

### INV-I-05 — Rejected Intent는 삭제되지 않는다

| | |
|---|---|
| **위반 시** | 삭제 차단 (Rule I-007). 탈락 이유의 오판이 학습의 핵심 신호다 |

### INV-I-06 — Expanded Intent는 하나 이상의 Task를 가진다

| | |
|---|---|
| **위반 시** | 정합성 오류. `Selected`로 되돌리고 Planner에 전개를 재요청 |

### INV-I-07 — evidence는 존재하는 Context 항목을 가리킨다

| | |
|---|---|
| **위반 시** | 참조 무결성 오류. Intent의 confidence를 하향하고 재추론을 큐에 넣는다 |
| **근거** | 근거가 사라진 추론은 검증할 수 없다 (Rule I-006) |

---

## 6. Lifecycle

```
Inferred → Validated → Selected → Expanded → Archived
     │          │           │
     └──────────┴───────────┴──▶ Rejected
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Inferred** | Intent Engine이 추론을 완료함 | 추출 알고리즘 종료 |
| **Validated** | Context/Constraint와 모순이 없음이 검증됨 | Constraint Filtering 통과 |
| **Selected** | Planner에 전달할 Intent로 선택됨 | Priority 상위 진입 |
| **Expanded** | Task로 전개됨 | Plan 생성 |
| **Rejected** | 확신도 부족, Constraint 위반 등으로 탈락 | 필터 탈락 또는 사용자 거부 |
| **Archived** | Goal 종료와 함께 보관, 학습 데이터로 사용 | Goal 종료 |

**Rejected된 Intent도 삭제하지 않는다**(INV-I-05).

### 6.1 재추론

Context가 크게 바뀌면 Intent를 다시 추론한다. **기존 Intent를 수정하지 않고 새로 만든다.**

```
ctx_001 갱신: 상담 전환율 정상 → 40% 하락
  ↓
intent_001 (홍보 강화, conf 0.85) → Archived
intent_009 (상담 프로세스 개선, conf 0.88) → Inferred
```

"그때는 왜 홍보라고 판단했는가"를 답할 수 있어야 하므로 이력을 남긴다.

---

## 7. Relationships

```
Goal 001 ──1:1..N──▶ Intent 002 ──1:1..N──▶ Task 005
                        ▲   │
   Context 003 ──근거────┘   │
   Constraint 004 ──필터─────┘
                        │
                        └──▶ Plan 008 (Selected Intent들이 하나의 Plan으로 컴파일)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Goal](e001-goal.md) | Intent의 부모. Goal 하나에서 여러 Intent가 추출된다 | `Goal 1:1..N Intent` |
| [Context](e003-context.md) | 추론의 근거(Evidence)를 제공한다 | `Context N:M Intent` |
| [Constraint](e004-constraint.md) | Intent 후보를 필터링/감점한다 | `Constraint N:M Intent` |
| [Task](e005-task.md) | Selected Intent가 Task로 전개된다 | `Intent 1:1..N Task` |
| [Plan](e008-plan.md) | 여러 Intent가 하나의 Plan으로 컴파일된다 | `Intent N:M Plan` |
| [Evaluation](e015-evaluation.md) | 실행 결과가 Intent 추론 정확도를 검증한다 | `Intent 1:0..N Evaluation` (Task 경유) |
| [Memory](e010-memory.md) | Rejected/Archived Intent가 학습 데이터가 된다 | `Intent 1:0..N Memory` |

### 7.1 Goal / Intent / Task 구분 규칙

| 문장 | 판정 |
|---|---|
| `학생 100명 모집` | Goal |
| `홍보 강화를 통한 신규 등록 증가` | Intent |
| `인스타그램 광고 소재 3종 제작` | Task |

판별 질문: **"이것이 없어도 다른 방향으로 Goal을 달성할 수 있는가?"** — 그렇다면 Intent 이하 계층이다.

---

## 8. Canonical Representation

```json
{
  "intent_id": "intent_001",
  "goal_id": "goal_001",
  "intent_type": "Promotion",
  "direction": "타겟 지역(홍대) 예비 고3 학부모 대상 홍보 도달 확대",
  "rationale": "현재 등록자 20명. 상담 대비 등록 전환율은 정상 범위이나 상담 유입 자체가 주 5건으로 부족하다. 인지도 부족이 주요 병목으로 추정된다.",
  "evidence": [
    "ctx_001#current_state.등록자",
    "ctx_001#current_state.상담문의",
    "ctx_001#history.여름캠프"
  ],
  "confidence": 0.85,
  "priority": "High",
  "expected_impact": "등록 +40~60명",
  "status": "Selected",
  "rejection_reason": null
}
```

**이 구조만 Planner로 전달된다.**

기계가 읽을 수 있는 스키마: [`intent.schema.json`](../intent-os-spec/schemas/intent.schema.json)

---

## 9. Validation Rules

Intent Engine은 Confirmed Goal을 받아 Intent 집합을 생성한다.

```
Confirmed Goal
  ↓
Context Loading          ← e003 §9
  ↓
Gap Analysis             (목표 상태 − 현재 상태)
  ↓
Cause Hypothesis         (왜 Gap이 존재하는가)
  ↓
Solution Domain Mapping  (어느 영역에서 풀 수 있는가)
  ↓
Task/Resource 식별자 검출 (INV-I-02) ── 검출 시 방향 서술로 치환
  ↓
Constraint Filtering     ← e004 §9  (INV-I-04)
  ↓
Confidence Scoring       (§9.1)
  ↓
Priority Ranking         (§9.2)
  ↓
Intent Set 생성 → Event 발행 (intent.inferred)
```

### 9.1 Confidence 산정

Intent는 추론이므로 **틀릴 수 있다.** Confidence는 이를 명시적으로 다루는 장치다.

| Confidence | 시스템 반응 |
|---|---|
| ≥ 0.8 | 자동으로 Selected 후보 진입 |
| 0.5 ~ 0.8 | 후보 유지, 추가 Context 수집 또는 사용자 확인 |
| < 0.5 | 사용자 확인 없이는 Selected 불가 |

산정 입력:

```
Evidence 강도 + Context Freshness + 유사 Goal의 과거 성공 이력 − Constraint 충돌 위험
```

**Context Freshness가 직접 반영된다.** Stale한 Context로 추론한 Intent는 Confidence가 깎인다([e003 §4.2](e003-context.md)). 이 기준은 [Volume 3 §7](../v3-runtime.md)의 Low Confidence 개입 규칙과 정합해야 한다.

### 9.2 Priority 산정

여러 Intent 중 무엇을 먼저 Task로 전개할 것인가.

$$Score = w_c \cdot Confidence + w_i \cdot ExpectedImpact - w_k \cdot Cost - w_r \cdot Risk$$

[Goal Score](e001a-goal-graph.md)와 같은 방식이다. **Intent 우선순위는 Goal의 Priority를 상속한 뒤 Intent 자체 점수로 보정한다.**

---

## 10. Examples

### 예시 1 — Intent 추출 전체 흐름

```
Goal: 학생 100명 모집 (현재 20명, 마감 11월, 예산 300만원)

Gap Analysis:      80명 부족
Cause Hypothesis:  인지도 부족(0.85) / 가격 저항(0.6) / 전환 프로세스 미흡(0.5)
Domain Mapping:    Promotion / Pricing / Process
Constraint Filter: cn_003 (예산 300만원) → 대규모 TV 광고 방향 제거

Intent Set:
  intent_001  Promotion  홍보 도달 확대            conf 0.85  Priority High
  intent_002  Pricing    조기 등록 할인 설계        conf 0.60  Priority Medium
  intent_003  Process    상담 전환 프로세스 개선     conf 0.50  Priority Medium
```

`intent_001`만 `Selected`가 되고 나머지는 `Validated`로 대기한다. **한 번에 모든 방향을 전개하지 않는다** — 예산이 분산되면 어느 방향도 검증되지 않는다.

### 예시 2 — Constraint에 의한 Rejected

```json
{
  "intent_id": "intent_004",
  "goal_id": "goal_001",
  "intent_type": "Promotion",
  "direction": "지역 케이블 TV 광고를 통한 대중 인지도 확보",
  "rationale": "학부모 세대의 TV 접촉률이 높다",
  "evidence": ["ctx_001#user_profile.조직"],
  "confidence": 0.55,
  "priority": "Low",
  "expected_impact": "등록 +30~80명 (변동 큼)",
  "status": "Rejected",
  "rejection_reason": "cn_003 위반 — 최소 집행 단가 800만원이 예산 300만원 Hard Constraint를 초과"
}
```

**삭제하지 않는다.** 다음 시즌에 예산이 1,000만원이 되면 이 Intent가 다시 후보가 된다.

### 예시 3 — 재추론

```
2026-08-04  ctx_001: 상담 문의 주 5건, 전환율 정상
            → intent_001 (홍보 강화) conf 0.85 Selected
   ↓
2026-08-20  ctx_001 갱신: 상담 문의 주 18건(↑), 전환율 40% 하락
            → Gap의 원인이 바뀌었다
   ↓
intent_001 → Archived  (유입은 이제 병목이 아니다)
intent_009 (Process, 상담 전환 프로세스 개선) conf 0.88 → Selected
   ↓
plan_014 → Suspended, Replanning
```

홍보 Intent가 **성공했기 때문에** 병목이 이동했다. Intent는 고정된 진단이 아니다.

### 예시 4 — 탈락 판단의 오판 (학습 신호)

```
2026-08-04  intent_002 (Pricing, 조기 할인) conf 0.60 → Validated (미선택)
2026-11-30  Goal 최종: 63명 (목표 100명 미달)
   ↓ 사후 분석
경쟁 학원 3곳이 10월에 조기 할인 시행 → 전환율 격차 발생
   ↓
Memory 기록:
  "시즌 캠페인에서 경쟁사 할인 이력이 있으면 Pricing Intent의
   confidence 초기값을 0.60 → 0.80으로 상향"
```

**Rejected/미선택 Intent를 보존했기 때문에 이 학습이 가능하다**(Rule I-007).

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **Intent가 하나도 추출되지 않음** | Goal이 너무 모호하거나 Context가 부족한 것이다. Intent를 억지로 만들지 않고 [Goal Clarification](e001d-goal-validation.md)으로 되돌린다 |
| **모든 Intent의 confidence < 0.5** | 자동 Selected가 불가능하다. 사용자에게 방향 후보를 제시하고 선택을 요청한다. **임의로 최고점을 선택하지 않는다** |
| **두 Intent가 서로 충돌** | 정상이다(가격 인하 ↔ 브랜드 프리미엄). 동시에 Selected하지 않고 하나를 고른다. 충돌 관계의 명시적 표현은 §12 미결 |
| **Intent는 Selected인데 Task로 전개 불가** | 해당 Capability를 제공하는 Resource가 없는 경우다. Intent를 `Rejected`로 전이하고 `rejection_reason`에 기록한 뒤 차순위 Intent를 Selected한다 |
| **사용자가 Intent를 직접 지정** | 허용한다. `confidence`는 여전히 필요하며 `origin: user_declared`로 표시해 1.0에 가깝게 둔다. 단 INV-I-03에 따라 1.0은 불가하다 |
| **Goal이 Achieved인데 Intent가 Selected 상태** | Goal 종료 시 모든 Intent를 `Archived`로 전이한다. 진행 중 Task는 [Plan](e008-plan.md)의 종료 절차를 따른다 |
| **evidence가 가리키는 Context가 Expired** | Intent의 confidence를 감쇠시키고 재추론 큐에 넣는다. 즉시 무효화하지는 않는다 — **오래된 근거와 틀린 근거는 다르다** |
| **하나의 Intent에서 30개 Task가 나옴** | Intent가 너무 넓다는 신호다. Solution Domain을 더 좁혀 2~3개 Intent로 분할한다 |
| **Rejected Intent가 나중에 옳았던 것으로 판명** | 예시 4가 그 경우다. Intent를 되살리지 않고 **새 Intent를 만든다.** 오판 사실은 Memory에 기록해 다음 추론의 confidence를 보정한다 |

---

## 12. Open Issues (v2.0)

### Solution Domain 온톨로지

§4.1의 Domain 목록은 마케팅 도메인(학원 학생 모집) 예시에 치우쳐 있다. 업종/Goal Type별 표준 Domain 온톨로지와 사용자 정의 Domain 등록 방식이 필요하다. [Capability Taxonomy](e006a-capability-taxonomy.md)가 겪는 것과 같은 문제이며, 같은 거버넌스 절차를 쓰는 것이 자연스럽다.

### Intent 간 관계 (Intent Graph)

Goal이 [Goal Graph](e001a-goal-graph.md)를 가지듯, Intent도 서로 영향을 준다.

```
가격 인하 Intent ↔ 브랜드 프리미엄 Intent   (충돌)
홍보 강화 Intent → 상담 프로세스 Intent      (부하 전이)
```

v2.0에서도 Intent를 독립 객체 집합으로 다룬다. `CONFLICTS_WITH` / `AMPLIFIES` 관계를 가진 Intent Graph가 필요한지는 미결이다. 다만 §10 예시 3(홍보 성공이 프로세스 병목을 낳음)은 **부하 전이 관계가 실재함**을 보여준다.

### Confidence 산정의 Calibration

§9.1의 산정 입력은 방향만 제시했다. 가중치와 Calibration(확신도 0.85인 Intent가 실제로 85% 적중하는가) 검증 절차가 없다. [Evaluation](e015-evaluation.md)의 `decision_quality`가 겪는 것과 같은 문제다.

### 앞으로 보강해야 할 항목

- Intent 형식 문법 (Formal Grammar)
- Cause Hypothesis 생성 규칙의 상세화
- 사용자에 의한 Intent 수동 지정/거부 프로토콜
- 실제 예시 30~50개
