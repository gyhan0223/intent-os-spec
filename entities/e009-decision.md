# Entity 009: Decision

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

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

## 3. Decision의 조건

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

## 4. Decision Attributes

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

---

## 5. Decision Types

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

---

## 6. Utility Scores

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

## 7. Decision Lifecycle

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

---

## 8. Decision Outcome — 사후 평가

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

## 9. Canonical Decision Representation

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

## 10. Decision Validation Algorithm

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

## 11. 다른 Entity와의 관계

```
Plan (e008) ──후보──→ Decision Engine ──기록──→ Decision (e009)
Task (e005) ──대상──→        │                     │
Resource (e007) ──선택지──→   │                     ├──→ Outcome (Runtime State)
Memory (e010) ←──축적────────┴─────────────────────┘
Feedback (e012) ←── 사용자/시스템 평가
```

| Entity | 관계 |
|---|---|
| **Plan** | Plan Selection Decision의 대상. Plan 버전 교체는 항상 Decision을 남긴다 |
| **Task** | Resource Selection Decision의 단위 |
| **Resource** | 선택지. Decision의 inputs_snapshot에 당시 Resource 점수가 동결된다 |
| **Memory** | Evaluated Decision이 Decision Memory로 축적된다 |
| **Feedback** | User Reject 등 Feedback이 Decision의 사후 평가에 반영된다 |
| **Goal** | 모든 Decision은 subject를 따라가면 결국 하나 이상의 Goal에 도달해야 한다 |

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
