# Entity 009: Decision

- **Version:** v2.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04
- **Schema:** [`decision.schema.json`](../intent-os-spec/schemas/decision.schema.json)

---

## 1. Definition

### 공식 정의

> **Decision is an immutable, auditable record of a choice made by the Decision Engine (or a human), including its rationale, considered alternatives, input snapshot, and confidence.**

> Decision은 Decision Engine(또는 인간)이 내린 선택의 **불변(Immutable)·감사 가능(Auditable) 기록**이며, 근거·고려한 대안·당시 입력 데이터·확신도를 포함한다.

여기서 중요한 단어는 **기록(Record)** 이다.

Decision은 "결정을 내리는 행위"가 아니라, 그 행위가 남긴 **결과물 객체**이다.

---

## 2. Decision은 무엇이 아닌가?

이게 정의보다 훨씬 중요하다.

### Decision은 Decision Engine이 아니다

Decision Engine은 **Component**(선택을 수행하는 시스템, [Volume 4](../v4-decision-engine.md))이고, 결정을 내리는 것은 **Process**다. Decision은 그 Process가 남긴 **Entity**다.

| 분류 | 이름 | 의미 |
|---|---|---|
| **Component / Process** | Decision Engine / Deciding | 후보 생성 → 예측 → 최적화 → 선택을 수행 |
| **Entity** | Decision | 선택의 기록. 저장·조회·감사·학습 가능한 객체 |
| **Runtime State** | Decision Outcome | 그 선택이 실제로 낳은 결과 |

❌ `Decision Engine이 지금 후보를 비교 중` — Decision이 아니다. Deciding이라는 Process다.

### Decision은 Plan이 아니다

❌ `T1 → T2 → T3 실행 청사진` — 이건 [Plan](e008-plan.md)이다. Decision은 "여러 Plan 중 **왜 이 Plan을 골랐는가**", "이 Task에 **왜 이 Resource를 골랐는가**"의 기록이다.

### Decision은 Outcome이 아니다

❌ `광고 CTR 9% 달성` — 이건 결과(Runtime State)다. Decision은 결과가 나오기 **전에** 이미 존재한다. 좋은 결정이 나쁜 결과를 낳을 수도 있고, 그 반대도 있다. **결정의 품질과 결과의 품질은 분리해서 평가한다.**

### Decision은 Log가 아니다

❌ `2026-08-04 09:00 Claude 호출` — 단순 이벤트 로그다. Decision은 근거·대안·입력 스냅샷·확신도를 갖춘 구조화된 기록이다. 로그는 "무엇을 했는가"만 남기지만 Decision은 "**왜** 그렇게 했는가"를 남긴다.

---

## 3. Design Principles

Decision은 반드시 아래 조건을 만족해야 한다.

### Rule D-001 — 감사 가능(Auditable)해야 한다

모든 Decision은 다음 질문에 스스로 답할 수 있어야 한다.

```
무엇을 선택했는가?         → selection
무엇과 비교했는가?         → alternatives_considered
왜 선택했는가?             → rationale + utility_scores
무엇을 근거로 판단했는가?   → inputs_snapshot
얼마나 확신했는가?         → confidence
```

### Rule D-002 — 근거(Rationale)를 포함해야 한다

- ✅ `한국어 작문 능력 96, 교육 마케팅 성공률 93%, 비용 효율 최적`
- ❌ `그냥 제일 좋아 보여서` — 시스템은 이런 Decision을 생성할 수 없다.

### Rule D-003 — 고려한 대안을 기록해야 한다

Candidate Generator가 만든 최종 후보와 각각의 Utility 점수를 남긴다. 대안이 하나도 없는 선택은 Decision이 아니라 **강제 실행(Forced Action)** 으로 별도 표기한다.

### Rule D-004 — 당시 입력 데이터의 스냅샷을 보존해야 한다

Decision은 "그 시점의 세계"에서 내려진다. Resource 점수, Historical Data, Context는 계속 변하므로([Volume 4 §12 Model Update Tracking](../v4-decision-engine.md)), 판단 당시 사용한 값을 `inputs_snapshot`으로 동결한다. 이것이 없으면 사후에 결정을 재현할 수 없다.

### Rule D-005 — Decision은 불변(Immutable)이다

**내린 결정의 기록은 수정하지 않는다.** 선택을 바꿔야 하면 기존 Decision을 `Superseded`로 표시하고 **새 Decision을 생성**한다. 새 Decision은 `supersedes` 필드로 이전 Decision을 가리킨다.

```
dec_101 (Claude 선택, Superseded)
   ↑ supersedes
dec_115 (Human Copywriter 선택, Applied)
```

이 규칙은 Plan Versioning([e008 §8](e008-plan.md)), Completed Goal 불변([e001a §15](e001a-goal-graph.md))과 같은 원칙의 반복이다.

### Rule D-006 — Confidence를 반드시 가진다

Confidence가 임계값(예: 70%) 미만이면 Multi-Agent 실행 또는 Escalation to Human이 트리거된다([Volume 4-A §10, §12](../v4a-decision-engine-detail.md)).

---

## 4. Attributes

```
Decision
├── Decision ID
├── Decision Type
├── Subject (무엇에 대한 결정인가)
├── Selection (선택된 것)
├── Alternatives Considered
├── Rationale
├── Utility Scores
├── Inputs Snapshot
├── Confidence
├── Decided By
├── Status
├── Supersedes
└── Outcome Link
```

| 속성 | 의미 | 예 |
|---|---|---|
| **Decision ID** | 식별자 | `dec_101` |
| **Decision Type** | 결정의 종류 (§5) | `ResourceSelection` |
| **Subject** | 결정 대상 | `plan_014/t3` (광고 카피 작성 Task) |
| **Selection** | 선택된 것 | `Claude` |
| **Alternatives Considered** | 고려한 대안 + 점수 | GPT(0.84), Gemini(0.79), Human(0.71) |
| **Rationale** | 선택 근거 | 한국어 작문 96 / 교육 마케팅 성공률 93% |
| **Utility Scores** | 후보별 Utility 계산 결과 (§6) | Claude 0.91 |
| **Inputs Snapshot** | 판단 당시 데이터 동결본 | Resource 점수표, Historical Data 버전 |
| **Confidence** | 확신도 | 0.89 |
| **Decided By** | 누가 결정했는가 | `decision_engine` / `human:대표` |
| **Status** | 기록의 상태 (§7) | Applied |
| **Supersedes** | 대체한 이전 Decision | `null` 또는 `dec_087` |
| **Outcome Link** | 사후 평가 연결 (§8) | `outcome_331` |

### 4.1 Decision Types

Intent OS의 결정은 Resource 선택만이 아니다.

```
Decision
├── Plan Selection
├── Resource Selection
├── Execution Strategy
├── Retry / Abort
├── Escalation to Human
└── Budget Reallocation
```

| Type | 무엇을 결정하는가 | 예 |
|---|---|---|
| **Plan Selection** | 후보 Plan 중 채택안 | 광고 중심안(0.82) vs SEO 중심안(0.61) → 광고 중심안 |
| **Resource Selection** | Task에 배정할 Resource | 광고 카피 작성 → Claude |
| **Execution Strategy** | Single / Pipeline / Collaborative | High Impact → Collaborative Agent |
| **Retry / Abort** | 실패 Task의 재시도 여부 | API 장애 → 대체 Resource로 Retry |
| **Escalation to Human** | 인간에게 넘길 것인가 | Confidence 54% → 대표에게 질문 |
| **Budget Reallocation** | 예산 재배분 | 인스타 광고 CTR 저조 → 예산 40% 검색 광고로 이동 |

모든 Type은 동일한 Canonical 구조(§9)를 공유한다. `subject`와 `selection`의 내용만 달라진다.

### 4.2 Utility Scores

Resource Selection과 Plan Selection의 근거 점수는 [Volume 4-A §8](../v4a-decision-engine-detail.md)의 Utility 공식을 따른다.

$$Utility = (Q \times W_q) + (S \times W_s) + (R \times W_r) - (C \times W_c) - (L \times W_l) - Risk$$

Decision에는 **후보별 최종 Utility뿐 아니라 그 시점의 가중치(Weight)도 함께 기록한다.** 가중치는 Dynamic Weight System에 의해 상황마다 달라지기 때문이다.

예) Task: 윈터캠프 광고 카피 작성

```
Weights: Quality 0.35 / Success 0.25 / Reliability 0.15 / Cost 0.15 / Latency 0.10

Candidate          Utility
Claude             0.91   ← Selected
GPT                0.84
Gemini             0.79
Human Copywriter   0.71   (품질 최고, 비용·속도에서 감점)
```

가중치 기록이 없으면 "왜 그날은 Human이 아니라 Claude였는가"를 사후에 설명할 수 없다.

---

## 5. Invariants

### INV-D-01 — Decision은 생성 후 변경되지 않는다

Rule D-005의 상태 표현이다. 판단을 사후에 고치면 "그때 무엇을 알고 무엇을 골랐는가"가 사라지고, 감사도 학습도 성립하지 않는다.

| | |
|---|---|
| **위반 시** | 변경을 거부한다. 판단을 바꾸려면 **새 Decision을 만들고** `supersedes`로 이전 것을 가리킨다 |
| **탐지** | 쓰기 시점 |

### INV-D-02 — 모든 Decision은 입력 스냅샷을 갖는다

Rule D-004의 상태 표현이다. Resource 점수는 계속 변하므로, 스냅샷 없이는 "왜 그때 이 Resource가 1등이었는가"를 재현할 수 없다.

| | |
|---|---|
| **위반 시** | 해당 Decision을 감사 불가로 표시하고 학습 데이터에서 제외한다. 실행은 막지 않는다 — 이미 내려진 판단을 되돌리는 비용이 더 크다 |

### INV-D-03 — 선택된 후보의 Utility가 대안보다 낮을 수 없다

낮은데도 선택됐다면 점수 밖의 이유가 작용한 것이다. 그 이유가 기록되지 않으면 Decision Engine은 자기 점수를 믿을 수 없게 된다.

| | |
|---|---|
| **위반 시** | 예외 사유(`override_reason`)를 요구한다. 사유가 없으면 Decision을 무효로 처리하고 재실행한다. 사유가 있으면 정상이며, **그 사유 자체가 Utility 모델의 보정 신호가 된다** |

### INV-D-04 — Decision 없이 Execution이 생기지 않는다

전역 불변식의 Decision 측 표현이다. Decision이 없는 실행은 누가 왜 그것을 골랐는지 알 수 없는 실행이다.

| | |
|---|---|
| **위반 시** | Execution을 `Aborted`로 종료하고 정합성 오류로 보고한다. 발생 비용은 기록한다 |
| **탐지** | Execution 생성 훅 |

### INV-D-05 — Hard Constraint를 위반한 후보는 선택되지 않는다

| | |
|---|---|
| **위반 시** | Decision을 무효화하고 재실행한다. **Hard는 필터이지 감점 항목이 아니다**([INV-CN-02](e004-constraint.md)) |

### INV-D-06 — 사후 평가는 Decision을 덮어쓰지 않는다

`decision_quality`가 낮게 나왔다고 원래 `utility`를 고치면, 예측과 실측의 차이가 사라져 Prediction Model이 배울 것을 잃는다.

| | |
|---|---|
| **위반 시** | 원본 값을 복원한다. 사후 평가는 [Evaluation](e015-evaluation.md)의 `decision_review`에 별도로 남는다 |

Entity 간 불변식은 [e000a-entity-relationships.md](e000a-entity-relationships.md)가 단일 권위다.

---

## 6. Lifecycle

Decision의 **내용**은 불변이지만, **기록의 상태**는 전이한다.

```
Proposed → Committed → Applied → Evaluated
    │          │
    └──→ Rejected          Applied ──→ Superseded
```

| 상태 | 의미 |
|---|---|
| **Proposed** | Engine이 선택안을 생성. High Impact면 Human 승인 대기 |
| **Committed** | 승인 완료. 실행 대기 |
| **Applied** | 선택이 실제로 실행에 반영됨 |
| **Evaluated** | Outcome과 대조 완료. Learning 신호 생성 |
| **Rejected** | Human이 승인 거부. 사유가 기록된다 |
| **Superseded** | 새 Decision으로 대체됨. 기록은 영구 보존 |

상태 전이는 필드 추가(평가 결과, 대체 링크)만 허용하며, **§4의 핵심 속성(selection, rationale, inputs_snapshot 등)은 어떤 상태에서도 수정할 수 없다.**

### 6.1 Decision Outcome — 사후 평가

Decision은 내리는 순간이 아니라 **결과와 대조될 때** 가치가 완성된다.

```
Decision (예측)          Outcome (실제)
  prediction 0.91   ↔     actual 0.95
        ↓
  Learning Signal: positive
        ↓
  Decision Memory 갱신 → 다음 Prediction 정확도 향상
```

이 구조는 Decision Memory([Volume 4-A §14](../v4a-decision-engine-detail.md))의 입력이 되며, Learning Engine([Volume 3 §Stage 7](../v3-runtime.md))이 소비한다.

| 대조 결과 | 해석 | 조치 |
|---|---|---|
| 예측 0.91 / 실제 0.95 | 좋은 결정, 좋은 결과 | 패턴 강화 |
| 예측 0.90 / 실제 0.50 | 예측 실패 | Prediction Model 보정 |
| 예측 0.55 / 실제 0.92 | 과소평가 | 해당 Resource 점수 상향 |

**주의:** 결과가 나빴다고 결정이 틀린 것은 아니다. 당시 `inputs_snapshot` 기준으로 최선이었는지를 별도로 평가한다. 이것이 스냅샷 보존(Rule D-004)이 필요한 두 번째 이유다.

---

## 7. Relationships

```
Plan (e008) ──후보──→ Decision Engine ──기록──→ Decision (e009)
Task (e005) ──대상──→        │                     │
Resource (e007) ──선택지──→   │                     ├──→ Outcome (Runtime State)
Memory (e010) ←──축적────────┴─────────────────────┘
Feedback (e012) ←── 사용자/시스템 평가
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Plan](e008-plan.md) | Plan Selection Decision의 대상. Plan 버전 교체는 항상 Decision을 남긴다 | `Plan 1:0..N Decision` |
| [Task](e005-task.md) | Resource Selection Decision의 단위 | `Task 1:0..N Decision` |
| [Resource](e007-resource.md) | 선택지. Decision의 `inputs_snapshot`에 당시 Resource 점수가 동결된다 | `Resource 1:0..N Decision` |
| [Execution](e013-execution.md) | 모든 Execution은 하나의 Decision에서 파생된다 (INV-D-04) | `Decision 1:0..N Execution` |
| [Constraint](e004-constraint.md) | Hard는 후보 필터, Soft는 점수 감점으로 들어온다 | `Constraint N:M Decision` |
| [Evaluation](e015-evaluation.md) | 사후 평가는 Decision을 덮지 않고 별도로 남는다 (INV-D-06) | `Decision 1:0..N Evaluation` |
| [Memory](e010-memory.md) | Evaluated Decision이 Decision Memory로 축적된다 | `Decision 1:0..N Memory` |
| [Feedback](e012-feedback.md) | User Reject 등 Feedback이 Decision의 사후 평가에 반영된다 | `Decision 1:0..N Feedback` |
| [Goal](e001-goal.md) | 모든 Decision은 subject를 따라가면 결국 하나 이상의 Goal에 도달해야 한다 | `Goal 1:0..N Decision` (간접) |

**Decision은 시간상 앞선 것들을 참조한다**([Rule REL-002](e000a-entity-relationships.md)).

---

## 8. Canonical Representation

모든 Decision은 내부적으로 동일한 구조를 가진다.

```json
{
  "decision_id": "dec_101",
  "decision_type": "ResourceSelection",
  "subject": { "plan_id": "plan_014", "task_id": "t3" },
  "selection": "Claude",
  "alternatives_considered": [
    { "candidate": "GPT", "utility": 0.84 },
    { "candidate": "Gemini", "utility": 0.79 },
    { "candidate": "Human Copywriter", "utility": 0.71 }
  ],
  "rationale": [
    "한국어 작문 능력 96",
    "교육 마케팅 Task 성공률 93%",
    "비용 효율 최적"
  ],
  "utility_scores": {
    "selected_utility": 0.91,
    "weights": { "quality": 0.35, "success": 0.25, "reliability": 0.15, "cost": 0.15, "latency": 0.10 }
  },
  "inputs_snapshot": {
    "resource_scores_version": "rr_2026-08-04",
    "historical_window": "최근 100회 실행"
  },
  "confidence": 0.89,
  "decided_by": "decision_engine",
  "status": "Applied",
  "supersedes": null,
  "outcome_link": null,
  "decided_at": "2026-08-04T09:30:00Z"
}
```

기계가 읽을 수 있는 스키마: [`decision.schema.json`](../intent-os-spec/schemas/decision.schema.json)

---

## 9. Validation Rules

Decision이 `Proposed`로 생성될 때 다음 검증을 통과해야 한다.

```
Decision (생성 요청)
  ↓
Subject 존재 확인 (Plan / Task가 실제로 존재하는가)
  ↓
Selection이 alternatives_considered에 포함되는가
  ↓
Rationale 존재 확인 (빈 근거 금지)
  ↓
Inputs Snapshot 존재 확인
  ↓
Confidence 계산 완료 확인
  ↓
[Confidence < 임계값?] ──Yes──→ Multi-Agent 또는 Escalation to Human
  ↓ No
[High Impact?] ──Yes──→ Human Approval (Proposed 유지)
  ↓ No
Committed
```

기존 Decision의 수정 요청은 **무조건 거부**된다. 유일한 경로는 새 Decision 생성 + `supersedes` 연결이다.

---

## 10. Examples

### 예시 1 — Resource Selection Decision

```
dec_101   subject: task_004 (인스타그램 광고 카피 3종 작성)
          type: resource_selection
          decided_at: 2026-08-04T09:12:00Z

후보와 Utility
  anthropic:claude-5      0.91   ✅ 선택
  human:copywriter_kim    0.78        품질 최고(94)이나 지연 4시간이 감점
  openai:gpt              0.74        관측 점수 81

inputs_snapshot
  claude-5   copywriting 88 (conf 0.82)  예상 800ms / 0.35 USD
  kim        copywriting 94 (conf 0.91)  예상 4h    / 50,000 KRW
  gpt        copywriting 81 (conf 0.68)  예상 950ms / 0.28 USD

rationale: 마감까지 8주이나 후속 Task 3개가 이 산출물에 의존(SPOF).
           지연 감점이 품질 우위를 상쇄한다.
```

스냅샷이 있으므로 한 달 뒤 claude-5의 점수가 76으로 떨어져도 **이 판단이 당시 기준으로 옳았는지** 그대로 검증할 수 있다.

### 예시 2 — 점수를 뒤집은 선택과 그 사유

```
dec_118   subject: task_009 (학부모 대상 상담 스크립트 검수)
          후보  claude-5              0.88
                human:copywriter_kim  0.71   ✅ 선택

override_reason: "학부모 응대 문구는 대표가 최종 책임을 진다.
                  인간 검수를 Policy(pol_004)가 요구한다."
```

INV-D-03이 요구하는 사유가 붙어 있으므로 정상이다. 이 사유가 반복되면 Utility 모델에 `human_required` 항을 넣어야 한다는 신호가 된다.

### 예시 3 — 예측과 실측이 갈린 뒤의 사후 평가

```
dec_101   예측  utility 0.91  /  800ms  /  0.35 USD
exe_220   실측         —      / 1,820ms /  0.42 USD
  ↓ Evaluation (eval_055)
decision_review
  prediction_error  utility +0.06  latency_ms +1,020  cost +0.07
  decision_quality  good — 결과는 좋았고 선택도 옳았다
```

`dec_101` 자체는 한 글자도 바뀌지 않는다(INV-D-06). 차이는 별도 Evaluation에 기록되고 Prediction Model의 보정에 쓰인다.

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **후보가 하나뿐** | 그래도 Decision을 남긴다. `alternatives_considered`가 비었다는 사실 자체가 정보다 — 선택지가 없었다는 뜻이며, Resource 등록의 필요를 알린다 |
| **Utility 동점** | 임의로 고르지 않는다. 비용이 낮은 쪽 → 관측 표본이 많은 쪽 → 먼저 등록된 쪽 순으로 결정론적 규칙을 적용하고, 적용한 규칙을 `rationale`에 남긴다 |
| **선택 직후 Resource가 사용 불가가 됨** | 기존 Decision을 수정하지 않는다. **새 Decision을 만들고** `supersedes`로 잇는다. 이전 판단이 틀렸던 것이 아니라 상황이 바뀐 것이다 |
| **사용자가 시스템 선택을 거부** | Decision을 지우지 않는다. 사용자 선택을 새 Decision으로 기록하고, 거부 사실은 [Feedback](e012-feedback.md)으로 붙인다. **거부당한 판단이 학습 가치가 가장 높다** |
| **스냅샷 없이 내려진 과거 Decision** | 감사 불가로 표시하고 학습 데이터에서 제외한다(INV-D-02). 소급해서 현재 점수로 스냅샷을 채우지 않는다 — 그건 기록이 아니라 날조다 |
| **같은 Task에 Decision이 둘** | 재시도 때문이면 정상이다. 각 Execution이 자기 Decision을 갖는다. 동시에 두 개가 Applied면 [INV-P-01](e008-plan.md) 위반의 하류 증상이므로 Plan 쪽을 먼저 본다 |
| **결과는 나빴는데 선택은 옳았던 경우** | `decision_quality: good`, `outcome: bad`로 **따로 기록한다.** 결과로만 판단을 평가하면 운 좋은 나쁜 판단이 학습되고, 운 나쁜 좋은 판단이 버려진다 |

---

## 12. Open Issues (v1.0)

### Inputs Snapshot의 크기 문제

모든 판단 근거를 동결하면 저장 비용이 커진다. 현재는 "참조 + 버전"(예: `resource_scores_version`) 방식을 가정하지만, 참조 대상 자체의 불변성 보장이 전제되어야 한다.

### Human Decision의 근거 기록

인간이 내린 결정(Escalation 이후)은 Rationale이 자연어로만 남을 수 있다. 이를 구조화된 형태로 유도하는 UI/프로토콜이 미정이다.

### 결정 품질 vs 결과 품질의 분리 평가 지표

"당시 정보 기준 최선이었는가"를 정량화하는 Decision Quality Score가 필요하다. Outcome 기반 평가와 섞이면 Learning이 왜곡된다(결과론 편향).

### 앞으로 보강해야 할 항목

- Decision Quality Score 정의
- Forced Action(대안 없는 선택)의 처리 규칙
- Superseded 체인의 최대 깊이 및 조회 표준
- 실제 예시 30~50개

