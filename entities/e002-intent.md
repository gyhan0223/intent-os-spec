# Entity 002: Intent

- **Version:** v2.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04
- **Schema:** [`intent.schema.json`](../intent-os-spec/schemas/intent.schema.json)

---

## 1. Definition

### 공식 정의

> **Intent is an inferred direction of solution derived from a Goal — it captures why the Goal exists and in which domain it should be solved, without specifying what to execute.**

> Intent는 Goal에서 추론된 해결의 방향이다. Goal이 왜 존재하는지, 어느 영역에서 풀어야 하는지를 담되, 무엇을 실행할지는 담지 않는다.

Intent는 Goal과 Task 사이의 **중간 계층**이다 ([Volume 1 §3.2](../v1-core-concepts.md) 참조).

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

❌ `학생 100명 모집` — 이건 원하는 미래 상태다. Goal이다.

✅ `홍보 채널을 통해 신규 등록을 늘린다` — 방향이다. Intent다.

### Intent는 Task가 아니다

❌ `인스타그램 광고 제작` — 실행 단위다. Task다.

Intent는 실행 가능한 작업이 아니라 **Task를 생성하기 위한 방향 제시**다.

### Intent는 Method가 아니다

❌ `유튜브 광고를 돌린다` — 특정 방법이다.

Intent는 해결 **영역(Domain)** 을 지목할 뿐, 특정 도구나 절차를 확정하지 않는다.

### Intent는 Request가 아니다

❌ `홍보 문구 하나 만들어줘` — 사용자의 입력 문장, 즉 Request다.

Request에서 Goal이 추출되고, Goal에서 Intent가 추론된다. 순서를 건너뛸 수 없다.

---

## 3. Design Principles

Intent는 반드시 아래 조건을 만족해야 한다.

### Rule I-001 — 반드시 하나의 Goal에서 파생되어야 한다

부모 Goal이 없는 Intent는 존재할 수 없다. 고립된 Intent는 시스템이 관리하지 않는다.

### Rule I-002 — 해결 영역(Solution Domain)을 지목해야 한다

✅ `가격 구조 개선을 통한 등록 전환율 상승`

❌ `등록을 늘린다` — 방향이 없다. 이건 Goal의 반복일 뿐이다.

### Rule I-003 — 실행 단위(Task)를 포함하면 안 된다

- 나쁜 예: `랜딩페이지 A/B 테스트 실행`
- 좋은 예: `상담 전환 프로세스 개선`

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

### Rule I-006 — 추론 근거를 남겨야 한다

`rationale`과 `evidence`가 비어 있는 Intent는 사후에 검증할 수 없다. **어떤 근거로 추론했는지 남지 않으면 Learning Engine이 개선할 수 없다.**

---

## 4. Attributes

Intent는 최소한 아래 속성을 가진다.

```
Intent
├── Goal Reference
├── Solution Domain
├── Direction
├── Rationale
├── Confidence
├── Priority
├── Evidence
├── Expected Impact
└── Status
```

| 속성 | 의미 | 예 |
|---|---|---|
| **Goal Reference** | 어느 Goal에서 파생되었는가 | `goal_001 (학생 100명 모집)` |
| **Solution Domain** | 어느 영역에서 풀 것인가 | `Promotion` (홍보) |
| **Direction** | 방향 서술 | `타겟 지역(홍대) 학부모 대상 홍보 강화` |
| **Rationale** | 왜 이 방향인가 | `현재 등록자 20명, 인지도 부족이 주요 원인으로 추정` |
| **Confidence** | 추론 확신도 (0.0~1.0) | `0.85` |
| **Priority** | Intent 간 우선순위 | High / Medium / Low |
| **Evidence** | 추론 근거가 된 Context/데이터 | `상담 문의 수 대비 등록률 정상, 유입 자체가 부족` |
| **Expected Impact** | Goal 달성 기여 예상 | `등록 +40~60명` |
| **Status** | Intent의 상태 | Inferred / Validated / Selected / Expanded / Rejected |

### 4.1 Intent Types (Solution Domain 분류)

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

| Type | 예시 |
|---|---|
| **Promotion Intent** | `윈터캠프 홍보 도달 확대` |
| **Pricing Intent** | `조기 등록 할인으로 전환율 상승` |
| **Brand Intent** | `학원 브랜드 신뢰도 확보` |
| **Process Intent** | `상담 → 등록 전환 프로세스 개선` |
| **Experience Intent** | `기존 학생 만족도 기반 재등록/추천 유도` |
| **Product Intent** | `커리큘럼 차별화` |
| **Efficiency Intent** | `광고 예산 300만원 내 도달 효율 극대화` |

v1.0의 Domain 목록은 예시적(illustrative)이며, 도메인 온톨로지는 확장 가능해야 한다 (→ §12 Open Issues).

---

## 5. Invariants

### INV-I-01 — Intent는 살아 있는 Goal 하나를 가리킨다

Rule I-001이 생성 시점의 검사라면, 이쪽은 항상 성립해야 하는 상태다. Goal이 사라지면 Intent는 갈 곳이 없다.

| | |
|---|---|
| **위반 시** | 부모 Goal이 `Archived`면 Intent도 `Archived`로 함께 내린다. 부모가 아예 없으면 고아 참조 오류로 보고하고 해당 Intent를 학습 데이터에서 제외한다 |
| **탐지** | Goal 상태 전이 훅, 야간 정합성 검사 |

### INV-I-02 — Confidence는 0~1이며 근거 없이 0.8을 넘지 않는다

`evidence`가 비어 있는데 `confidence ≥ 0.8`이면 추론이 아니라 추측이다.

| | |
|---|---|
| **위반 시** | Confidence를 0.5로 강등하고 Selected 진입을 차단한다. 강등 사실을 `rationale`에 기록한다 |
| **탐지** | 생성·갱신 시점, Confidence 재계산 시점 |

### INV-I-03 — Expanded Intent는 최소 하나의 Task를 갖는다

Task 없이 `Expanded`인 Intent는 "전개했다"는 기록만 남고 실체가 없는 상태다.

| | |
|---|---|
| **위반 시** | 상태를 `Selected`로 되돌리고 재전개를 요청한다. 두 번째 실패 시 `Rejected` + 사유 기록 |

### INV-I-04 — 종료된 Intent는 수정되지 않는다

`Rejected`와 `Archived`는 학습 데이터의 원본이다. 나중에 고치면 "그때 왜 탈락했는가"가 사라진다.

| | |
|---|---|
| **위반 시** | 변경을 거부한다. 방향을 바꾸려면 새 Intent를 만든다 |

### INV-I-05 — 한 Goal 아래 같은 방향의 Intent는 하나다

`goal_id`와 `intent_type`이 같고 `direction`이 의미상 겹치는 Intent가 둘 이상이면, Planner가 같은 Task를 두 번 만든다.

| | |
|---|---|
| **위반 시** | 나중에 생긴 Intent를 먼저 것에 병합하고, 병합된 쪽은 `Rejected` + `merged_into`로 남긴다. 삭제하지 않는다 |
| **탐지** | 생성 시점, Intent Set 확정 시점 |

Entity 간 불변식은 [e000a-entity-relationships.md](e000a-entity-relationships.md)가 단일 권위다.

---

## 6. Lifecycle

```
Inferred → Validated → Selected → Expanded → Archived
                    ↘ Rejected
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Inferred** | Intent Engine이 추론을 완료함 | 추론 파이프라인 종료 |
| **Validated** | Context/Constraint와 모순이 없음이 검증됨 | §9 검증 통과 |
| **Selected** | Planner에 전달할 Intent로 선택됨 | Priority 상위 + Confidence 기준 충족 |
| **Expanded** | Task Graph로 전개됨 | Task가 하나 이상 생성됨 |
| **Rejected** | 확신도 부족, Constraint 위반 등으로 탈락 | 검증 실패 또는 선택 탈락 |
| **Archived** | Goal 종료와 함께 보관, 학습 데이터로 사용 | 부모 Goal이 종료 상태로 전이 |

**Rejected된 Intent도 삭제하지 않는다.** 왜 탈락했는지가 Learning Engine의 입력이다.

---

## 7. Relationships

```
Goal 001 ──1:0..N──▶ Intent 002 ──1:0..N──▶ Task 005
                        ▲   ▲
      Context 003 ──────┘   └────── Constraint 004
      (Evidence 제공)              (후보 필터링)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Goal](e001-goal.md) | Intent의 부모. Goal 하나에서 여러 Intent가 추출된다 | `Goal 1:0..N Intent` |
| [Context](e003-context.md) | Intent 추론의 근거(Evidence)를 제공한다 | `Context N:M Intent` |
| [Constraint](e004-constraint.md) | Intent 후보를 필터링·감점한다. Intent를 만들지는 않는다 | `Constraint N:M Intent` |
| [Task](e005-task.md) | Selected Intent가 Task Graph로 전개된다 | `Intent 1:0..N Task` |
| [Plan](e008-plan.md) | Planner는 Selected Intent를 입력으로 Plan을 만든다 | `Intent 1:0..N Plan` |
| [Feedback](e012-feedback.md) | 실행 결과가 Intent 추론 정확도 개선에 사용된다 | `Intent 1:0..N Feedback` |

**참조 방향은 Intent → Goal이다.** Goal은 자신에게 어떤 Intent가 달렸는지 모른다([Rule REL-001](e000a-entity-relationships.md)).

### 7.1 Goal / Intent / Task 구분 규칙 요약

| 문장 | 판정 |
|---|---|
| `학생 100명 모집` | Goal |
| `홍보 강화를 통한 신규 등록 증가` | Intent |
| `인스타그램 광고 소재 3종 제작` | Task |

판별 질문: **"이것이 없어도 다른 방향으로 Goal을 달성할 수 있는가?"** — 그렇다면 Intent 이하 계층이다.

---

## 8. Canonical Representation

모든 Intent는 내부적으로 동일한 구조를 가진다.

```json
{
  "intent_id": "intent_001",
  "goal_id": "goal_001",
  "intent_type": "Promotion",
  "direction": "타겟 지역(홍대) 학부모 대상 홍보 도달 확대",
  "rationale": "현재 등록자 20명. 상담 전환율은 정상이나 유입 자체가 부족",
  "confidence": 0.85,
  "priority": "High",
  "status": "Inferred"
}
```

**이 구조만 Planner로 전달된다.**

기계가 읽을 수 있는 스키마: [`intent.schema.json`](../intent-os-spec/schemas/intent.schema.json)

---

## 9. Validation Rules

```
Confirmed Goal
  ↓
Context Loading          ← Context (e003)
  ↓
Gap Analysis             (목표 상태 − 현재 상태)
  ↓
Cause Hypothesis         (왜 Gap이 존재하는가)
  ↓
Solution Domain Mapping  (어느 영역에서 풀 수 있는가)
  ↓
Constraint Filtering     ← Constraint (e004)
  ↓
Confidence Scoring
  ↓
Priority Ranking
  ↓
Intent Set 생성
```

각 단계의 실패는 다르게 다룬다.

| 단계 | 실패 조건 | 조치 |
|---|---|---|
| Context Loading | 필수 Context 부재 | Intent 추론을 보류하고 Context 수집 요청 |
| Gap Analysis | Goal에 측정 가능한 목표값이 없음 | Goal을 `Structured` 이전으로 되돌린다. Intent를 만들지 않는다 |
| Domain Mapping | 어떤 Domain에도 매핑되지 않음 | `Rejected` + 사유 `no_domain_match`. 도메인 온톨로지 보강 후보로 기록 |
| Constraint Filtering | Hard Constraint 위반 | `Rejected` + 위반 Constraint id 기록 |
| Confidence Scoring | Rule I-004 위반 (값 없음) | 생성을 거부한다 |
| Priority Ranking | 동점 다수 | Goal Priority 상속값이 높은 쪽이 이긴다. 그래도 동점이면 Confidence 순 |

### 9.1 Confidence 산정

Intent는 추론이므로 **틀릴 수 있다.** Confidence는 이를 명시적으로 다루는 장치다.

| Confidence | 시스템 반응 |
|---|---|
| ≥ 0.8 | 자동으로 Selected 후보 진입 |
| 0.5 ~ 0.8 | 후보 유지, 추가 Context 수집 또는 사용자 확인 |
| < 0.5 | 사용자 확인 없이는 Selected 불가 |

Confidence 산정 입력:

```
Evidence 강도 + Context 신선도 + 유사 Goal의 과거 성공 이력 − Constraint 충돌 위험
```

이 기준은 [Volume 3 §7 Human Intervention Model](../v3-runtime.md)의 Low Confidence 개입 규칙과 정합해야 한다.

### 9.2 Priority 산정

여러 Intent 중 무엇을 먼저 Task로 전개할 것인가. 예를 들어,

$$Score = w_c \cdot Confidence + w_i \cdot ExpectedImpact - w_k \cdot Cost - w_r \cdot Risk$$

Goal Graph의 Goal Score([e001a-goal-graph.md §10](e001a-goal-graph.md))와 같은 방식이다. **Intent 우선순위는 Goal의 Priority를 상속한 뒤 Intent 자체 점수로 보정한다.**

---

## 10. Examples

### 예시 1 — 하나의 Goal에서 Intent Set 추론

```
Goal: 윈터캠프 학생 100명 모집 (현재 20명, 마감 2026-12-31, 광고 예산 300만원)

Gap Analysis:      80명 부족
Cause Hypothesis:  인지도 부족(0.85) / 가격 저항(0.6) / 전환 프로세스 미흡(0.5)
Domain Mapping:    Promotion / Pricing / Process
Constraint Filter: 예산 300만원 → 대규모 TV 광고 방향 제거

Intent Set:
  intent_001  Promotion  홍보 도달 확대            Confidence 0.85  Priority High
  intent_002  Pricing    조기 등록 할인 설계        Confidence 0.60  Priority Medium
  intent_003  Process    상담 전환 프로세스 개선     Confidence 0.50  Priority Medium
```

`intent_001`만 §9.1 기준으로 자동 Selected가 되고, 나머지 둘은 사용자 확인 대기에 들어간다.

### 예시 2 — Constraint에 걸려 탈락한 Intent

```
intent_004  Promotion  옥외 광고 집행으로 지역 인지도 확보
            Confidence 0.72
            ↓ Constraint Filtering
            cn_002 (광고 예산 최대 300만원) 위반 — 예상 집행액 800만원
            ↓
            Rejected  reason: hard_constraint_violation (cn_002)
```

탈락했지만 삭제하지 않는다. 예산 제약이 완화되면 이 Intent가 먼저 재검토 후보가 된다.

### 예시 3 — Confidence가 근거 부족으로 강등된 경우

```
intent_005  Brand  학원 브랜드 신뢰도 확보
            추론 시 confidence 0.88, evidence 없음
            ↓ INV-I-02
            confidence 0.50으로 강등, rationale에 강등 사유 기록
            ↓
            Selected 불가 → 사용자 확인 대기
```

김 원장이 "재등록 문의에서 신뢰 얘기가 자주 나온다"는 Context를 추가하면 Evidence가 채워지고 Confidence가 다시 산정된다.

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **Goal이 너무 구체적이어서 Intent가 Goal의 복사본이 됨** | Rule I-002 위반으로 `Rejected`. Goal에 이미 방법이 섞여 있다는 신호이므로 **Goal을 되돌려 검토**한다. Intent 쪽에서 억지로 방향을 지어내지 않는다 |
| **Intent 두 개가 서로 충돌** (가격 인하 ↔ 브랜드 프리미엄) | v1.0은 둘 다 유지하고 **Planner 단계에서 조정**한다. Intent 층위에서 충돌을 해소하지 않는다 — 판단 근거가 Plan에 있기 때문이다 (→ §12 Intent Graph) |
| **추론 결과가 0개** | Goal은 유효한데 Intent가 하나도 안 나오면 Context 부족이다. Goal을 `Rejected`시키지 않고 **Context 수집 질문을 생성**한다 |
| **사용자가 Intent를 직접 지정** | 허용한다. 단 `confidence: 1.0`, `evidence: ["user_specified"]`로 기록해 시스템 추론과 구분한다. 이 값은 추론 정확도 통계에서 제외한다 |
| **Selected 이후 Context가 바뀜** | 이미 `Expanded`면 Intent는 그대로 두고 Plan 재검토로 넘긴다. 아직 `Selected`면 Confidence를 재산정하고 기준 미달 시 `Rejected`로 내린다 |
| **부모 Goal이 분할됨** | Intent를 복제하지 않는다. 분할된 Goal 각각에 대해 **다시 추론**한다. 복제하면 INV-I-05가 깨진다 |
| **같은 방향인데 Domain 분류만 다름** | 병합 대상이다(INV-I-05). 어느 Domain이 맞는지는 Learning Engine의 판정 대상으로 남긴다 |

---

## 12. Open Issues (v1.0)

### Solution Domain 온톨로지

§4.1의 Domain 목록은 마케팅 도메인(학원 학생 모집) 예시에 치우쳐 있다. 업종/Goal Type별 표준 Domain 온톨로지와 사용자 정의 Domain 등록 방식이 필요하다.

### Intent 간 관계

Goal이 Goal Graph를 가지듯, Intent도 서로 영향을 준다.

```
가격 인하 Intent ↔ 브랜드 프리미엄 Intent   (충돌)
홍보 강화 Intent → 상담 프로세스 Intent      (부하 전이)
```

v1.0에서는 Intent를 독립 객체 집합으로 다루지만, 장기적으로 `CONFLICTS_WITH` / `AMPLIFIES` 관계를 가진 **Intent Graph**가 필요할 수 있다.

### Confidence 산정의 표준화

§9.1의 산정 입력은 방향만 제시했다. 가중치와 Calibration(확신도가 실제 적중률과 일치하는가) 검증 절차는 Learning Engine 명세와 함께 확정한다.

### 방향의 동일성 판정

INV-I-05는 "의미상 겹치는 direction"을 하나로 본다고 했지만, 그 판정 기준이 없다. 문자열 비교로는 부족하고 임베딩 유사도가 필요한데, 유사도 함수 자체가 [Volume 4-C](../v4c-resource-genome.md)의 미해결 항목이다.

### 앞으로 보강해야 할 항목

- Intent 형식 문법 (Formal Grammar)
- Intent 추론 알고리즘의 단계별 상세화 (Cause Hypothesis 생성 규칙)
- 사용자에 의한 Intent 수동 지정/거부 프로토콜
- 실제 예시 30~50개
