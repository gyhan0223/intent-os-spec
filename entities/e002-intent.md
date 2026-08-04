# Entity 002: Intent

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

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

## 3. Intent의 조건

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

---

## 4. Intent Attributes

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

Rationale과 Evidence는 사후 학습에 특히 중요하다. **어떤 근거로 추론했는지 남지 않으면 Learning Engine이 개선할 수 없다.**

---

## 5. Intent Types (Solution Domain 분류)

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

## 6. Intent Lifecycle

```
Inferred → Validated → Selected → Expanded → Archived
                    ↘ Rejected
```

| 상태 | 의미 |
|---|---|
| **Inferred** | Intent Engine이 추론을 완료함 |
| **Validated** | Context/Constraint와 모순이 없음이 검증됨 |
| **Selected** | Planner에 전달할 Intent로 선택됨 |
| **Expanded** | Task Graph로 전개됨 |
| **Rejected** | 확신도 부족, Constraint 위반 등으로 탈락 |
| **Archived** | Goal 종료와 함께 보관, 학습 데이터로 사용 |

**Rejected된 Intent도 삭제하지 않는다.** 왜 탈락했는지가 Learning Engine의 입력이다.

---

## 7. Intent Extraction Algorithm

Intent Engine은 Confirmed Goal을 받아 Intent 집합을 생성한다.

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

예)

```
Goal: 학생 100명 모집 (현재 20명, 마감 11월, 예산 300만원)

Gap Analysis:      80명 부족
Cause Hypothesis:  인지도 부족(0.85) / 가격 저항(0.6) / 전환 프로세스 미흡(0.5)
Domain Mapping:    Promotion / Pricing / Process
Constraint Filter: 예산 300만원 → 대규모 TV 광고 방향 제거

Intent Set:
  I1  Promotion  홍보 도달 확대            Confidence 0.85  Priority High
  I2  Pricing    조기 등록 할인 설계        Confidence 0.60  Priority Medium
  I3  Process    상담 전환 프로세스 개선     Confidence 0.50  Priority Medium
```

---

## 8. Intent Confidence

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

---

## 9. Intent Priority

여러 Intent 중 무엇을 먼저 Task로 전개할 것인가. 예를 들어,

$$Score = w_c \cdot Confidence + w_i \cdot ExpectedImpact - w_k \cdot Cost - w_r \cdot Risk$$

Goal Graph의 Goal Score([e001a-goal-graph.md §10](e001a-goal-graph.md))와 같은 방식이다. **Intent 우선순위는 Goal의 Priority를 상속한 뒤 Intent 자체 점수로 보정한다.**

---

## 10. Canonical Intent Representation

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

## 11. 다른 Entity와의 관계

```
Goal (e001)
  ↓ 1:N 추론
Intent (e002) ← Context (e003) 를 근거로 추론
  ↓ 1:N 전개    ← Constraint (e004) 로 필터링
Task (e005)
```

| Entity | 관계 |
|---|---|
| **Goal** [e001-goal.md](e001-goal.md) | Intent의 부모. Goal 하나에서 여러 Intent가 추출된다 |
| **Context** [e003-context.md](e003-context.md) | Intent 추론의 근거(Evidence)를 제공한다 |
| **Constraint** [e004-constraint.md](e004-constraint.md) | Intent 후보를 필터링/감점한다 |
| **Task** (e005, 예정) | Selected Intent가 Task Graph로 전개된다 |
| **Feedback** (e012, 예정) | 실행 결과가 Intent 추론 정확도 개선에 사용된다 |

### Goal / Intent / Task 구분 규칙 요약

| 문장 | 판정 |
|---|---|
| `학생 100명 모집` | Goal |
| `홍보 강화를 통한 신규 등록 증가` | Intent |
| `인스타그램 광고 소재 3종 제작` | Task |

판별 질문: **"이것이 없어도 다른 방향으로 Goal을 달성할 수 있는가?"** — 그렇다면 Intent 이하 계층이다.

---

## 12. Open Issues (v1.0)

### Solution Domain 온톨로지

§5의 Domain 목록은 마케팅 도메인(학원 학생 모집) 예시에 치우쳐 있다. 업종/Goal Type별 표준 Domain 온톨로지와 사용자 정의 Domain 등록 방식이 필요하다.

### Intent 간 관계

Goal이 Goal Graph를 가지듯, Intent도 서로 영향을 준다.

```
가격 인하 Intent ↔ 브랜드 프리미엄 Intent   (충돌)
홍보 강화 Intent → 상담 프로세스 Intent      (부하 전이)
```

v1.0에서는 Intent를 독립 객체 집합으로 다루지만, 장기적으로 `CONFLICTS_WITH` / `AMPLIFIES` 관계를 가진 **Intent Graph**가 필요할 수 있다.

### Confidence 산정의 표준화

§8의 산정 입력은 방향만 제시했다. 가중치와 Calibration(확신도가 실제 적중률과 일치하는가) 검증 절차는 Learning Engine 명세와 함께 확정한다.

### 앞으로 보강해야 할 항목

- Intent 형식 문법 (Formal Grammar)
- Intent 추론 알고리즘의 단계별 상세화 (Cause Hypothesis 생성 규칙)
- 사용자에 의한 Intent 수동 지정/거부 프로토콜
- 실제 예시 30~50개
