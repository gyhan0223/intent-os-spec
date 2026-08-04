# Entity 009: Decision

- **Version:** v2.0 Draft
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
| **Entity** | [Outcome](e014-outcome.md) | 그 선택이 실제로 낳은 결과 |

❌ `Decision Engine이 지금 후보를 비교 중` — Decision이 아니다. Deciding이라는 Process다.

### Decision은 Plan이 아니다

❌ `T1 → T2 → T3 실행 청사진` — 이건 [Plan](e008-plan.md)이다. Decision은 "여러 Plan 중 **왜 이 Plan을 골랐는가**", "이 Task에 **왜 이 Resource를 골랐는가**"의 기록이다.

### Decision은 Outcome이 아니다

❌ `광고 CTR 9% 달성` — 이건 [Outcome](e014-outcome.md)(Entity 014)이다. Decision은 결과가 나오기 **전에** 이미 존재한다. 좋은 결정이 나쁜 결과를 낳을 수도 있고, 그 반대도 있다. **결정의 품질과 결과의 품질은 분리해서 평가한다** — 이 분리는 [Evaluation Rule EVA-004](e015-evaluation.md)가 담당한다.

### Decision은 Log가 아니다

❌ `2026-08-04 09:00 Claude 호출` — 단순 이벤트 로그다. Decision은 근거·대안·입력 스냅샷·확신도를 갖춘 구조화된 기록이다. 로그는 "무엇을 했는가"만 남기지만 Decision은 "**왜** 그렇게 했는가"를 남긴다.

### Decision은 Policy가 아니다

❌ `건당 1만원 초과 실행은 승인 필요` — 이건 [Policy](e019-policy.md)다.

Policy는 **Decision보다 상위**에 있다. Policy가 금지한 후보는 Decision이 선택할 수 없고, Utility를 계산하지도 않는다([INV-11](e000a-entity-relationships.md)).

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

Candidate Generator가 만든 최종 후보와 각각의 Utility 점수를 남긴다. 대안이 하나도 없는 선택은 **강제 실행(Forced Action)** 으로 표기하되(`forced_action: true`), **기록 자체를 생략하지 않는다**([INV-02](e000a-entity-relationships.md) 예외 조항).

### Rule D-004 — 당시 입력 데이터의 스냅샷을 보존해야 한다

Decision은 "그 시점의 세계"에서 내려진다. Resource 점수, Historical Data, Context는 계속 변하므로, 판단 당시 사용한 값을 `inputs_snapshot`으로 동결한다.

동결 대상의 실체는 [Resource Profile](e025-resource-profile.md)의 **스냅샷 버전**이다([Rule RPF-004](e025-resource-profile.md)).

```json
"inputs_snapshot": {
  "resource_profile_versions": {
    "anthropic:claude-5": "rp_claude5_2026-08-04T09:00Z"
  }
}
```

이것이 없으면 사후에 결정을 재현할 수 없다.

### Rule D-005 — Decision은 불변(Immutable)이다

**내린 결정의 기록은 수정하지 않는다.** 선택을 바꿔야 하면 기존 Decision을 `Superseded`로 표시하고 **새 Decision을 생성**한다. 새 Decision은 `supersedes` 필드로 이전 Decision을 가리킨다.

```
dec_101 (Claude 선택, Superseded)
   ↑ supersedes
dec_115 (Human Copywriter 선택, Applied)
```

이 규칙은 Plan Versioning(§[e008 §6](e008-plan.md)), Outcome 불변([e014 Rule OUT-003](e014-outcome.md))과 같은 원칙의 반복이다.

### Rule D-006 — Confidence를 반드시 가진다

Confidence가 임계값(예: 70%) 미만이면 Multi-Agent 실행 또는 Escalation to Human이 트리거된다([Volume 4-A §10, §12](../v4a-decision-engine-detail.md)).

Confidence의 산출 근거는 [Resource Profile](e025-resource-profile.md)이 반환하는 점수별 confidence다. **점수만 높고 표본이 적은 후보를 신중히 다루기 위한 장치다.**

### Rule D-007 — Policy 평가를 거친 뒤에만 존재한다

후보 생성 단계에서 [Policy](e019-policy.md)가 배제한 것은 `alternatives_considered`에 올리지 않는다. 배제 사실만 `rationale`에 남긴다.

- ✅ `rationale: ["pol_015에 의해 해외 리전 Resource 1건 배제"]`
- ❌ 금지된 후보의 Utility를 계산해 기록

**금지된 선택지의 점수가 로그에 남으면 "최적해였는데 막혔다"는 유혹이 생긴다.**

---

## 4. Attributes

```
Decision
├── Identity
│   ├── decision_id
│   ├── decision_type
│   └── decided_at
├── Choice
│   ├── subject
│   ├── selection
│   ├── alternatives_considered
│   └── forced_action
├── Justification
│   ├── rationale
│   ├── utility_scores
│   ├── inputs_snapshot
│   └── confidence
├── Governance
│   ├── decided_by
│   └── policy_evaluation
└── Link
    ├── status
    ├── supersedes
    └── outcome_link
```

| 속성 | 의미 | 예 |
|---|---|---|
| **decision_id** | 식별자 | `dec_101` |
| **decision_type** | 결정의 종류 (§4.1) | `ResourceSelection` |
| **subject** | 결정 대상 | `plan_014/t3` (광고 카피 작성 Task) |
| **selection** | 선택된 것 | `Claude` |
| **alternatives_considered** | 고려한 대안 + 점수 | GPT(0.84), Gemini(0.79), Human(0.71) |
| **forced_action** | 대안 없는 선택인가 | `false` |
| **rationale** | 선택 근거 | 한국어 작문 96 / 교육 마케팅 성공률 93% |
| **utility_scores** | 후보별 Utility 계산 결과 (§4.2) | Claude 0.91 |
| **inputs_snapshot** | 판단 당시 데이터 동결본 | Resource Profile 스냅샷 버전 |
| **confidence** | 확신도 | 0.89 |
| **decided_by** | 누가 결정했는가 | `decision_engine` / `human:대표` / `agent_marketing_01` |
| **policy_evaluation** | Policy 판정 결과와 버전 | §8 참조 |
| **status** | 기록의 상태 (§6) | Applied |
| **supersedes** | 대체한 이전 Decision | `null` 또는 `dec_087` |
| **outcome_link** | 사후 평가 연결 (§6.1) | `outcome_331` |

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
| **Execution Strategy** | Single / Pipeline / Collaborative | High Impact → Collaborative ([e013 §4.1](e013-execution.md)) |
| **Retry / Abort** | 실패 Task의 재시도 여부 | API 장애 → 대체 Resource로 Retry |
| **Escalation to Human** | 인간에게 넘길 것인가 | Confidence 54% → 대표에게 질문 |
| **Budget Reallocation** | 예산 재배분 | 인스타 광고 CTR 저조 → 예산 40% 검색 광고로 이동 |

모든 Type은 동일한 Canonical 구조(§8)를 공유한다. `subject`와 `selection`의 내용만 달라진다.

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

공식의 `Risk` 항은 후보별 잔여 위험의 합계이며, 그 출처는 [Risk Entity](e018-risk.md)의 `residual_severity`다([e018 §7.1](e018-risk.md)). **Risk를 명시적으로 관리해야 이 항이 설명 가능해진다.**

---

## 5. Invariants

### INV-D-01 — Decision의 핵심 속성은 생성 후 수정되지 않는다

`selection`, `alternatives_considered`, `rationale`, `utility_scores`, `inputs_snapshot`, `confidence`가 대상이다. [INV-06](e000a-entity-relationships.md)의 Decision 측 표현이다.

| | |
|---|---|
| **위반 시** | 저장 계층이 쓰기를 거부한다. 감사 로그에 시도를 기록한다 |
| **허용되는 변경** | `status` 전이와 사후 링크(`outcome_link`) 추가만 |
| **근거** | 사후에 rationale을 "보기 좋게" 고치면 결과론 편향이 데이터에 들어간다 |

### INV-D-02 — selection은 alternatives_considered에 포함된다

`forced_action: true`인 경우는 예외이며, 이때 `alternatives_considered`는 빈 배열이다.

| | |
|---|---|
| **위반 시** | 생성 거부. 비교하지 않은 것을 골랐다는 뜻이므로 감사가 불가능하다 |

### INV-D-03 — Hard Constraint를 위반한 Decision은 Committed가 될 수 없다

[INV-07](e000a-entity-relationships.md)의 Decision 측 표현이다.

| | |
|---|---|
| **위반 시** | `Rejected`로 전이하고 사유를 기록. 재선택을 트리거 |
| **주의** | Soft Constraint 위반은 Utility 감점일 뿐 차단이 아니다 |

### INV-D-04 — Policy가 deny한 것은 어떤 Utility로도 선택될 수 없다

| | |
|---|---|
| **위반 시** | Decision을 무효화하고 파생된 Execution을 즉시 중단. 사고로 기록 |
| **탐지** | Decision 생성 시 + Execution 시작 시 이중 검사 ([e013 §9](e013-execution.md)) |

### INV-D-05 — Resource가 배정된 Task에는 대응하는 Decision이 존재한다

[INV-02](e000a-entity-relationships.md) No Unexplained Assignment의 Decision 측 표현이다.

| | |
|---|---|
| **위반 시** | 실행을 차단하고 Decision 생성을 강제한다 |
| **근거** | 설명할 수 없는 선택은 감사도 학습도 불가능하다 |

### INV-D-06 — supersedes 체인은 순환하지 않는다

| | |
|---|---|
| **위반 시** | 링크 생성 거부. 결정 이력 추적이 무한 루프에 빠진다 |

### INV-D-07 — inputs_snapshot이 참조하는 스냅샷은 불변이다

`resource_profile_versions`가 가리키는 [Resource Profile](e025-resource-profile.md) 스냅샷이 변경되면 Decision의 재현성이 무너진다.

| | |
|---|---|
| **위반 시** | 스냅샷 쓰기 거부 ([INV-RPF-03](e025-resource-profile.md)). 이미 변경되었다면 해당 Decision을 재현 불가로 표시 |

### INV-D-08 — decided_at은 파생된 Execution의 started_at 이하다

| | |
|---|---|
| **위반 시** | 정합성 오류로 기록하고 학습 데이터에서 제외 ([INV-13](e000a-entity-relationships.md)) |

---

## 6. Lifecycle

Decision의 **내용**은 불변이지만, **기록의 상태**는 전이한다.

```
Proposed → Committed → Applied → Evaluated
    │          │
    └──→ Rejected          Applied ──→ Superseded
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Proposed** | Engine이 선택안을 생성. High Impact면 Human 승인 대기 | 후보 비교 완료 |
| **Committed** | 승인 완료. 실행 대기 | 검증·승인 통과 |
| **Applied** | 선택이 실제로 실행에 반영됨 | Execution 생성 |
| **Evaluated** | Outcome과 대조 완료. Learning 신호 생성 | Evaluation 완료 |
| **Rejected** | Human이 승인 거부. 사유가 기록된다 | 승인 거부 또는 INV-D-03/04 위반 |
| **Superseded** | 새 Decision으로 대체됨. 기록은 영구 보존 | 재선택 |

상태 전이는 필드 추가(평가 결과, 대체 링크)만 허용하며, **§4의 핵심 속성은 어떤 상태에서도 수정할 수 없다**(INV-D-01).

### 6.1 사후 평가 — Decision이 완성되는 시점

Decision은 내리는 순간이 아니라 **결과와 대조될 때** 가치가 완성된다.

```
Decision (예측)              Outcome (실측)              Evaluation (판정)
  utility 0.91         →     cost 0.42 / quality 0.93  →  decision_quality 0.90
  예상 비용 0.35 USD                                        prediction_error +0.07
        ↓
  Learning Signal
        ↓
  Decision Memory 갱신 → 다음 Prediction 정확도 향상
```

이 구조는 Decision Memory([Volume 4-A §14](../v4a-decision-engine-detail.md))의 입력이 되며, Learning Engine([Volume 5](../v5-learning-engine.md))이 소비한다.

| 대조 결과 | 해석 | 조치 |
|---|---|---|
| 예측 0.91 / 실제 0.95 | 좋은 결정, 좋은 결과 | 패턴 강화 |
| 예측 0.90 / 실제 0.50 | 예측 실패 | Prediction Model 보정 |
| 예측 0.55 / 실제 0.92 | 과소평가 | 해당 Resource 점수 상향 |

**주의:** 결과가 나빴다고 결정이 틀린 것은 아니다. 당시 `inputs_snapshot` 기준으로 최선이었는지는 [Evaluation](e015-evaluation.md)의 `decision_quality`가 **독립적으로** 판정한다([Rule EVA-004](e015-evaluation.md), [INV-EVA-05](e015-evaluation.md)). 이것이 스냅샷 보존(Rule D-004)이 필요한 두 번째 이유다.

---

## 7. Relationships

```
Plan 008 ──후보──▶ Decision Engine ──기록──▶ Decision 009
Task 005 ──대상──▶        │                      │
Resource 007 ──선택지──▶   │                      ├──▶ Execution 013 ──▶ Outcome 014
Policy 019 ──배제──▶       │                      │                          │
Risk 018 ──감점──▶         │                      └──◀── Evaluation 015 ◀────┘
Resource Profile 025 ──동결──▶ inputs_snapshot            │
                                                    Memory 010 ──▶ Knowledge 011
                                                          │
                                                          └─개선─▶ Decision 009
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Task](e005-task.md) | Resource Selection Decision의 단위 | `Task 1:0..N Decision` |
| [Plan](e008-plan.md) | Plan Selection Decision의 대상. 버전 교체는 항상 Decision을 남긴다 | `Plan 1:0..N Decision` |
| [Resource](e007-resource.md) | 선택지 | `Resource N:M Decision` |
| [Resource Profile](e025-resource-profile.md) | `inputs_snapshot`이 스냅샷을 동결 참조한다 | `Resource Profile 1:0..N Decision` |
| [Execution](e013-execution.md) | 모든 Execution은 하나의 Decision에서 파생된다 | `Decision 1:0..N Execution` |
| [Evaluation](e015-evaluation.md) | `decision_quality`로 사후 검토된다 | `Decision 1:0..N Evaluation` |
| [Policy](e019-policy.md) | 후보 생성 전에 배제. Utility보다 우선한다 | `Policy 1:N Decision` |
| [Constraint](e004-constraint.md) | Hard는 차단, Soft는 감점 | `Constraint N:M Decision` |
| [Risk](e018-risk.md) | Utility 공식의 `Risk` 항에 반영된다 | `Risk N:M Decision` |
| [Memory](e010-memory.md) | Evaluated Decision이 Decision Memory로 축적된다 | `Decision 1:0..N Memory` |
| [Agent](e023-agent.md) | Agent의 모든 결정이 Decision으로 기록된다 | `Agent 1:0..N Decision` |
| [Session](e021-session.md) | 어느 실행 단위에서 내려졌는가 | `Session 1:0..N Decision` |
| [Goal](e001-goal.md) | `subject`를 따라가면 결국 하나 이상의 Goal에 도달한다 | `Goal 1:0..N Decision` |
| Decision | 재선택 시 `supersedes` 체인 | `Decision 1:0..1 Decision` |

---

## 8. Canonical Representation

모든 Decision은 내부적으로 동일한 구조를 가진다.

```json
{
  "decision_id": "dec_101",
  "decision_type": "ResourceSelection",
  "subject": { "goal_id": "goal_001", "plan_id": "plan_014", "task_id": "task_004" },
  "selection": "anthropic:claude-5",
  "alternatives_considered": [
    { "candidate": "openai:gpt-5", "utility": 0.84 },
    { "candidate": "google:gemini", "utility": 0.79 },
    { "candidate": "human:copywriter_kim", "utility": 0.71 }
  ],
  "rationale": [
    "한국어 광고 카피 observed_score 93 (표본 214, confidence 0.95)",
    "교육 마케팅 Task 성공률 93%",
    "비용 효율 최적 — 인간 대비 1/120",
    "pol_015에 의해 해외 리전 Resource 1건 배제"
  ],
  "utility_scores": {
    "selected_utility": 0.91,
    "weights": { "quality": 0.35, "success": 0.25, "reliability": 0.15, "cost": 0.15, "latency": 0.10 }
  },
  "inputs_snapshot": {
    "resource_profile_versions": {
      "anthropic:claude-5": "rp_claude5_2026-08-04T09:00Z",
      "openai:gpt-5": "rp_gpt5_2026-08-04T09:00Z",
      "human:copywriter_kim": "rp_copywriter_kim_2026-08-04T09:00Z"
    },
    "historical_window": "최근 100회 실행",
    "context_ref": "ctx_ses_057"
  },
  "confidence": 0.89,
  "decided_by": "decision_engine",
  "policy_evaluation": {
    "evaluated_at": "2026-08-04T09:29:58Z",
    "point": "pre_decision",
    "matched_policies": ["pol_015"],
    "policy_versions": { "pol_015": "1.0" },
    "exceptions_used": [],
    "result": "allow"
  },
  "status": "Applied",
  "forced_action": false,
  "supersedes": null,
  "outcome_link": "out_331",
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
Subject → Goal 도달 가능성 확인 (INV-01)
  ↓
Policy 평가 (pre_decision) ── e019 §9.2
  ├── deny된 후보를 alternatives_considered에서 제거 (Rule D-007)
  └── 남은 후보가 0개 → escalate 생성 후 종료
  ↓
Selection이 alternatives_considered에 포함되는가 (INV-D-02)
  └── 후보가 1개뿐이면 forced_action: true 설정
  ↓
Rationale 존재 확인 (Rule D-002) ── 빈 근거 금지
  ↓
Inputs Snapshot 존재 확인 (Rule D-004)
  └── 참조된 Profile 스냅샷의 존재·불변성 확인 (INV-D-07)
  ↓
Hard Constraint 검사 (INV-D-03) ── 위반 시 Rejected
  ↓
Confidence 계산 완료 확인 (Rule D-006)
  ↓
[Confidence < 임계값?] ──Yes──→ Multi-Agent 또는 Escalation to Human
  ↓ No
[High Impact?] ──Yes──→ Human Approval (Proposed 유지)
  ↓ No
Committed → Event 발행 (decision.committed)
```

기존 Decision의 수정 요청은 **무조건 거부**된다(INV-D-01). 유일한 경로는 새 Decision 생성 + `supersedes` 연결이다.

### 9.1 High Impact 판정

무엇이 Human Approval을 요구하는가. 판정은 [Policy](e019-policy.md)가 하며, Decision은 그 결과를 따를 뿐이다.

| 조건 | 근거 |
|---|---|
| 예상 비용이 임계 초과 | `pol_012` (cost) |
| 비가역 작업을 포함 | [Risk RSK-008](e018-risk.md), [Tool TOL-002](e024-tool.md) |
| Confidence < 임계값 | Rule D-006 |
| 미해결 Critical Risk 존재 | [INV-RSK-07](e018-risk.md) |

---

## 10. Examples

### 예시 1 — Resource Selection (정상)

§8의 Canonical이 그대로 이 사례다. 요약하면 다음과 같다.

```
Task     task_004  인스타그램 광고 카피 3종 작성
후보      Claude(0.91) / GPT(0.84) / Gemini(0.79) / 김 카피라이터(0.71)
배제      해외 리전 Resource 1건 (pol_015)
선택      Claude
확신도    0.89  → 임계값 0.70 초과 → 자동 Committed
```

김 카피라이터는 **품질이 가장 높지만(96) Utility는 가장 낮다.** 비용 50,000원과 지연 4시간이 감점되기 때문이다. 절대 순위가 아니라 이 Task의 가중치 위에서의 최적해다.

### 예시 2 — Forced Action (대안 없음)

```json
{
  "decision_id": "dec_210",
  "decision_type": "ResourceSelection",
  "subject": { "goal_id": "goal_001", "plan_id": "plan_014", "task_id": "task_010" },
  "selection": "adplatform:ads_api",
  "alternatives_considered": [],
  "forced_action": true,
  "rationale": [
    "advertising.campaign_execution을 제공하는 Active Resource가 1개뿐",
    "대안 부재 — 비교 없이 강제 선택됨"
  ],
  "utility_scores": { "selected_utility": null, "weights": {} },
  "inputs_snapshot": { "historical_window": "최근 20회 실행" },
  "confidence": 0.75,
  "decided_by": "decision_engine",
  "status": "Proposed",
  "supersedes": null,
  "outcome_link": null,
  "decided_at": "2026-08-04T14:55:00Z"
}
```

대안이 없어도 **기록은 남긴다.** "선택의 여지가 없었다"는 사실 자체가 시스템의 공백을 드러내는 정보다([e006a §10 예시 4](e006a-capability-taxonomy.md)).

`status: Proposed`인 이유는 이 Task가 비가역 작업이라 Human Approval이 필요하기 때문이다(§9.1).

### 예시 3 — Superseded (재선택)

```
dec_101  Claude 선택  Applied
   │ exe_220 완료 → out_331 → eva_512 (accept)
   │ 이후 fb_881 도착: "우리 학원 톤이 아니다"
   │ eva_530 (human, reject)
   ▼
dec_101 → Superseded
dec_115  human:copywriter_kim 선택  Applied
         supersedes: dec_101
         rationale: [
           "eva_530에서 브랜드 톤 부적합 판정 (quality 0.55)",
           "rubric_copywriting_v2에 브랜드 톤 축이 누락되어 자동 평가가 이를 잡지 못함",
           "인간 검수로 전환. 비용 50,000원은 재작업 리스크 대비 정당"
         ]
```

`dec_101`은 지워지지 않는다. **"그때는 왜 Claude였는가"** 에 답할 수 있어야 하기 때문이다.

### 예시 4 — Escalation (낮은 Confidence)

```
Task: 커머스 B2B 영문 카피 작성
  ↓ Resource Profile 조회
Claude  observed 88, sample 12, confidence 0.52   ← 표본 부족
GPT     observed 91, sample  8, confidence 0.41
  ↓
Utility는 계산되지만 confidence 0.52 < 임계 0.70
  ↓
dec_150  decision_type: EscalationToHuman
         selection: "human:대표에게 확인"
         rationale: [
           "해당 Context(커머스/en/B2B)의 표본이 12건으로 부족",
           "교육/ko Context의 confidence 0.95와 대비됨",
           "Shadow Execution 병행 또는 인간 판단 필요"
         ]
         confidence: 0.52
```

**점수가 아니라 confidence가 Escalation을 유발했다.** 88점은 낮지 않지만 믿을 근거가 얇다.

### 예시 5 — Budget Reallocation

```json
{
  "decision_id": "dec_302",
  "decision_type": "BudgetReallocation",
  "subject": { "goal_id": "goal_001", "plan_id": "plan_014" },
  "selection": "인스타그램 40% → 검색 광고로 이전",
  "alternatives_considered": [
    { "candidate": "현행 유지", "utility": 0.44 },
    { "candidate": "인스타 20% 이전", "utility": 0.61 },
    { "candidate": "인스타 40% 이전", "utility": 0.73 },
    { "candidate": "인스타 전면 중단", "utility": 0.58 }
  ],
  "rationale": [
    "인스타 CTR 0.8% — 목표 1.5% 대비 47% 미달 (10일 관측)",
    "검색 광고 CTR 2.1% — 전환당 비용 1/2.4",
    "전면 중단은 리타게팅 모수 손실로 감점"
  ],
  "utility_scores": {
    "selected_utility": 0.73,
    "weights": { "quality": 0.20, "success": 0.45, "reliability": 0.10, "cost": 0.20, "latency": 0.05 }
  },
  "inputs_snapshot": { "metrics_window": "2026-08-05 ~ 2026-08-14", "historical_window": "최근 20회 실행" },
  "confidence": 0.81,
  "decided_by": "human:대표",
  "status": "Applied",
  "forced_action": false,
  "supersedes": null,
  "outcome_link": null,
  "decided_at": "2026-08-15T11:20:00Z"
}
```

가중치가 §4.2의 카피 작성 Task와 다르다. 예산 재배분에서는 `success` 비중이 0.25에서 0.45로 올라간다. **Dynamic Weight가 실제로 작동하는 모습이며, 이것을 기록하지 않으면 사후 설명이 불가능하다.**

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **후보가 하나도 없음** | Decision을 만들지 않는다. `EscalationToHuman` Decision을 대신 생성하고 "현재 Policy·Capability 하에서 수행 가능한 Resource가 없다"를 보고한다. 임의로 Policy를 완화하지 않는다 |
| **Utility 동점** | `confidence`가 높은 쪽을 택한다. 그래도 같으면 비용이 낮은 쪽. 판정 근거를 `rationale`에 명시한다. 무작위 선택은 금지 — 재현할 수 없다 |
| **Policy가 최적 후보를 배제** | 배제된 후보의 Utility를 계산하지 않는다(Rule D-007). 배제 사실만 `rationale`에 남긴다 |
| **인간이 Engine의 추천을 뒤집음** | 새 Decision을 만들고 `decided_by: human:*`, `supersedes`로 연결한다. **Engine의 원래 Decision은 `Rejected`가 아니라 `Superseded`다** — 거부된 것이 아니라 교체된 것이다 |
| **Decision 후 실행 전에 Resource가 Deprecated** | Decision은 그대로 두고 `Superseded`로 전이 + 새 Decision 생성. 이미 내린 결정을 소급 수정하지 않는다 |
| **같은 Task에 Decision이 여러 개** | 정상이다. 재시도마다 새 Decision이 생긴다(`Task 1:0..N Decision`). 단 동시에 `Applied`인 것은 하나여야 한다 |
| **Human Decision의 rationale이 자연어 한 줄** | 허용하되 구조화를 유도한다. `decided_by`가 인간이면 rationale의 최소 항목 수 검사를 완화한다. **기록이 없는 것보다 거친 기록이 낫다** |
| **inputs_snapshot이 너무 큼** | 값을 복사하지 않고 "참조 + 버전"만 담는다. 참조 대상(Resource Profile 스냅샷)의 불변성이 전제다(INV-D-07) |
| **Evaluated 이후 새 정보로 판단이 바뀜** | Decision을 고치지 않는다. 새 [Evaluation](e015-evaluation.md)을 만들고 `supersedes`로 연결한다. Decision의 사후 평가는 Evaluation의 영역이다 |
| **Agent가 내린 Decision** | 동일하게 기록한다. `decided_by: agent_marketing_01`. Agent의 자율성 수준이 L0이면 `Proposed`에서 멈추고 `Committed`로 전이할 수 없다([e023 §9.2](e023-agent.md)) |

---

## 12. Open Issues (v2.0)

### ✅ v1.0에서 해소된 항목

| v1.0 Open Issue | 해소 |
|---|---|
| 결정 품질 vs 결과 품질의 분리 평가 지표 | [Evaluation Rule EVA-004](e015-evaluation.md)의 `decision_quality`와 [INV-EVA-05](e015-evaluation.md)(독립 산출 강제)로 해소 |
| Forced Action(대안 없는 선택)의 처리 규칙 | Rule D-003 + `forced_action` 필드 + §10 예시 2로 해소 |
| Inputs Snapshot의 크기 문제 | [Resource Profile](e025-resource-profile.md)의 스냅샷 버전 참조 방식으로 해소. 불변성은 INV-D-07이 보장 |

### Decision Quality Score의 산출 방법

`decision_quality`를 **어떻게 계산하는가**는 여전히 미정이다. "그 시점에 알 수 있었던 정보만으로 최선이었는가"를 판정하려면 `inputs_snapshot`으로 후보군을 재실행(counterfactual replay)하는 것이 이상적이지만 비용이 크다. [e015 §12](e015-evaluation.md)와 함께 확정해야 한다.

### Human Decision의 근거 구조화

인간이 내린 결정(Escalation 이후)은 Rationale이 자연어로만 남을 수 있다(§11). 이를 구조화된 형태로 유도하는 UI/프로토콜이 미정이다.

### Superseded 체인의 깊이

체인이 길어지면 "현재 유효한 결정"을 찾는 비용이 커진다. 최대 깊이 제한과 체인 압축(compaction) 규칙이 필요하다.

### Utility의 Risk 항 산출

§4.2에서 `Risk` 항을 "후보별 잔여 위험의 합계"로 정의했으나, 합·최댓값·가중합 중 무엇이 옳은지 근거가 없다. [e018 §12](e018-risk.md)와 동일한 미결 항목이다.

### 앞으로 보강해야 할 항목

- Decision Quality Score 산출 공식 확정
- Superseded 체인의 조회 표준 (현재 유효 Decision 질의)
- Multi-Agent 합의로 내려진 Decision의 `decided_by` 표현
- 실제 예시 30~50개
