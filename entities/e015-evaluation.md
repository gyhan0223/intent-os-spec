# Entity 015: Evaluation

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Evaluation is a judgment about an Outcome — how good it is, how much it advanced the Goal, and whether the Decision that produced it was sound.**

> Evaluation은 하나의 Outcome에 대한 **판정**이며, 결과가 얼마나 좋은지·Goal을 얼마나 진전시켰는지·그 결과를 낳은 Decision이 타당했는지를 함께 판단한다.

여기서 중요한 단어는 **판정(Judgment)** 이다.

[Outcome](e014-outcome.md)이 "사실"이라면 Evaluation은 "해석"이다. 같은 사실에 대해 자동 평가기와 사용자가 서로 다른 판정을 내릴 수 있고, 두 판정 모두 유효하다.

### Evaluation이 없으면 무슨 일이 벌어지는가

```
Execution → Outcome → (평가 없음) → Memory
```

무엇이 좋은 결과였는지 모른 채 기록만 쌓인다. [Memory](e010-memory.md)는 데이터 더미가 되고 [Knowledge](e011-knowledge.md)로 승격될 근거가 없다. **Learning의 입력은 Outcome이 아니라 Evaluation이다.**

---

## 2. Evaluation은 무엇이 아닌가?

### Evaluation은 Outcome이 아니다

❌ `카피 3종 생성, 0.42 USD 소모` — 이건 [Outcome](e014-outcome.md)이다.

| | Outcome | Evaluation |
|---|---|---|
| 질문 | 무엇이 나왔는가 | 그게 좋은가 |
| 성격 | 측정 | 판정 |
| 평가자 | 없음 | 반드시 있음 (`evaluator`) |
| 재생성 | 불가 | 가능 (재평가) |
| 개수 | Execution당 1 | Outcome당 0..N |

### Evaluation은 Feedback이 아니다

❌ `사용자가 별점 2개를 줌` — 이건 [Feedback](e012-feedback.md)이다.

**Feedback은 입력, Evaluation은 산출이다.**

```
Feedback(별점 2개) ─┐
Outcome(측정값)    ─┼──▶ Evaluation Engine ──▶ Evaluation(판정)
Goal(기준)         ─┘
```

Feedback 없이도 Evaluation은 만들어진다(자동 평가). 반대로 Feedback만 있고 Evaluation이 없으면 그것은 아직 판정되지 않은 원시 신호다.

### Evaluation은 Test가 아니다

❌ `단위 테스트 통과 여부` — Test는 사전에 정의된 명세와의 일치를 이진 판정한다.

Evaluation은 **정답이 없는 대상**을 다차원으로 판정한다. 광고 카피에 정답은 없다. "예비 고3 학부모에게 얼마나 설득력 있는가"를 여러 축으로 점수화할 뿐이다.

### Evaluation은 점수 하나가 아니다

❌ `score: 0.93`

단일 점수는 트레이드오프를 지운다. 품질 0.95인데 비용이 예산의 3배인 결과와, 품질 0.80인데 비용이 1/5인 결과는 **같은 점수로 뭉개면 안 된다.** Evaluation은 최소 4축을 유지한다(Rule EVA-002).

### Evaluation은 Learning이 아니다

❌ `앞으로 교육 마케팅은 Claude를 쓰자`

이건 Learning이라는 **Process**가 여러 Evaluation을 종합해 만든 [Knowledge](e011-knowledge.md)다. Evaluation은 **하나의 Outcome에 대한 판정 하나**로 국한된다.

---

## 3. Design Principles

### Rule EVA-001 — Evaluation은 정확히 하나의 Outcome을 참조한다

여러 Outcome을 묶어 평가하고 싶다면, 그것은 상위 Task/Goal 수준의 Evaluation을 별도로 만드는 것이다. 하나의 Evaluation이 여러 Outcome을 가리키지 않는다.

### Rule EVA-002 — 최소 4축을 평가한다

| 축 | 질문 | 범위 |
|---|---|---|
| **Quality** | 산출물 자체가 좋은가 | 0.0 ~ 1.0 |
| **Goal Alignment** | Goal을 얼마나 진전시켰는가 | 0.0 ~ 1.0 |
| **Efficiency** | 비용·시간 대비 효과는 어떤가 | 0.0 ~ 1.0 |
| **Satisfaction** | 사용자가 만족했는가 | 0.0 ~ 1.0 또는 `null` |

`Satisfaction`은 Feedback이 없으면 `null`이 될 수 있다. **나머지 3축은 `null`을 허용하지 않는다.**

### Rule EVA-003 — 평가자를 기록한다

누가 판정했는지 없는 Evaluation은 신뢰할 수 없다. `evaluator`는 자동 평가기 ID, 인간 ID, 또는 다른 Resource ID다.

### Rule EVA-004 — 결정의 품질과 결과의 품질을 분리한다

**이 명세에서 가장 중요한 규칙이다.**

```
Outcome Quality    결과가 좋았는가          → outcome_quality
Decision Quality   그 시점에 최선이었는가   → decision_quality
```

둘은 독립이다. 네 가지 조합이 모두 존재한다.

| decision_quality | outcome_quality | 해석 | 학습 신호 |
|---|---|---|---|
| 높음 | 높음 | 좋은 결정, 좋은 결과 | 패턴 강화 |
| 높음 | 낮음 | **좋은 결정, 나쁜 운** | 결정 로직 유지. 예측 모델만 보정 |
| 낮음 | 높음 | **나쁜 결정, 좋은 운** | 결정 로직 교정. 결과에 속으면 안 된다 |
| 낮음 | 낮음 | 나쁜 결정, 나쁜 결과 | 결정 로직 교정 |

결과만 보고 학습하면 2·3번 경우에서 잘못된 방향으로 학습한다. 이것이 결과론 편향(Hindsight Bias)이며, [e009 Open Issue](e009-decision.md)가 지적한 문제의 해소책이다.

`decision_quality`는 Decision의 `inputs_snapshot`을 기준으로 판정한다 — **그 시점에 알 수 있었던 정보만으로** 그 선택이 최선이었는가.

### Rule EVA-005 — 판정 근거를 남긴다

- ✅ `카피 3종 중 2종이 타겟 페르소나(예비 고3 학부모)의 관심사인 '내신 관리'를 직접 언급`
- ❌ `괜찮아 보임`

근거 없는 점수는 재현할 수 없고 이의를 제기할 수도 없다.

### Rule EVA-006 — 재평가는 새 Evaluation을 만든다

기존 Evaluation을 수정하지 않는다. 시간이 지나 새 정보(지연 지표, 사용자 Feedback)가 도착하면 새 Evaluation을 만들고 `supersedes`로 연결한다([INV-06](e000a-entity-relationships.md)).

### Rule EVA-007 — 평가 기준(Rubric)을 참조한다

점수의 의미가 평가마다 달라지면 비교가 불가능하다. Evaluation은 사용한 Rubric의 ID와 버전을 기록한다.

### Rule EVA-008 — 평가 비용도 비용이다

LLM으로 평가하면 비용이 든다. 저위험·저비용 Task에 정밀 평가를 붙이면 배보다 배꼽이 커진다. Evaluation의 깊이는 Task의 영향도에 비례한다(§9.2).

---

## 4. Attributes

```
Evaluation
├── Identity
│   ├── evaluation_id
│   ├── outcome_id
│   └── task_id
├── Evaluator
│   ├── evaluator
│   ├── evaluator_type
│   └── rubric_id / rubric_version
├── Scores
│   ├── quality
│   ├── goal_alignment
│   ├── efficiency
│   ├── satisfaction
│   └── composite
├── Decision Review
│   ├── decision_id
│   ├── decision_quality
│   └── prediction_error
├── Verdict
│   ├── verdict
│   ├── adopted
│   └── rationale[]
├── Inputs
│   └── feedback_ids[]
└── Link
    ├── supersedes
    └── evaluated_at
```

| 속성 | 의미 | 예 |
|---|---|---|
| **evaluation_id** | 식별자 | `eva_512` |
| **outcome_id** | 평가 대상 | `out_331` |
| **evaluator** | 평가 주체 | `eval_engine:v3` / `human:대표` |
| **evaluator_type** | 평가 방식 (§4.1) | `automatic` |
| **rubric_id** | 사용한 평가 기준 | `rubric_copywriting_v2` |
| **quality** | 산출물 품질 | `0.93` |
| **goal_alignment** | Goal 기여도 | `0.87` |
| **efficiency** | 비용 대비 효과 | `0.95` |
| **satisfaction** | 사용자 만족 | `null` (Feedback 미도착) |
| **composite** | 가중 합산 점수 (§9.1) | `0.91` |
| **decision_id** | 검토한 Decision | `dec_101` |
| **decision_quality** | 결정 자체의 타당성 (EVA-004) | `0.90` |
| **prediction_error** | 예측 대비 오차 | `{ "utility": +0.02, "cost": +0.07, "latency": +1020 }` |
| **verdict** | 종합 판정 (§4.2) | `accept` |
| **adopted** | 산출물을 실제로 채택했는가 | `true` |
| **rationale** | 판정 근거 | 문자열 배열 |
| **feedback_ids** | 참고한 Feedback | `[]` |
| **supersedes** | 대체한 이전 평가 | `null` |
| **evaluated_at** | 평가 시각 | `2026-08-04T09:31:10Z` |

### 4.1 Evaluator Types

```
Evaluation
├── automatic     규칙·모델 기반 자동 평가
├── human         사람이 직접 판정
├── peer          다른 Resource가 교차 평가 (Multi-Agent)
├── deferred      지연 지표 확정 후의 사후 평가
└── consensus     복수 평가자의 합의 결과
```

| Type | 언제 | 특징 |
|---|---|---|
| **automatic** | 기본값. 모든 Outcome | 즉시, 저비용, 낮은 정밀도 |
| **human** | High Impact, Value Judgment | 느림, 고비용, 최고 권위 |
| **peer** | Collaborative 실행 결과 비교 | 자기 평가 편향을 줄임 |
| **deferred** | `measurement_lag` 경과 후 | Goal Alignment의 진짜 값이 여기서 확정 |
| **consensus** | 평가가 엇갈릴 때 | 가중 합의 (§11) |

**Deferred Evaluation이 핵심이다.** 카피를 만든 당일의 `goal_alignment: 0.87`은 추정이다. 2주 뒤 모집 인원이 실제로 22명 늘었을 때 만들어지는 deferred Evaluation이 진짜 값을 확정한다.

### 4.2 Verdict

| verdict | 의미 | 후속 조치 |
|---|---|---|
| `accept` | 채택 | Task → Evaluated. 다음 Task 진행 |
| `accept_with_revision` | 조건부 채택 | 보완 Task 생성 |
| `reject` | 반려 | Task → Failed. 재시도 또는 Resource 재선택 |
| `escalate` | 판단 보류 | 인간에게 이관 |
| `inconclusive` | 평가 불가 | 정보 부족. deferred Evaluation 예약 |

---

## 5. Invariants

### INV-EVA-01 — Evaluation은 정확히 하나의 Outcome을 참조한다

| | |
|---|---|
| **위반 시** | 생성 거부 |

### INV-EVA-02 — quality·goal_alignment·efficiency는 null이 아니다

| | |
|---|---|
| **위반 시** | `verdict: inconclusive`로 강제하고 Learning 입력에서 제외 |

### INV-EVA-03 — 모든 점수는 0.0 ~ 1.0 범위다

| | |
|---|---|
| **위반 시** | 생성 거부. 범위 밖 값은 Rubric 정의 오류의 신호다 |

### INV-EVA-04 — evaluated_at은 Outcome.measured_at 이상이다

| | |
|---|---|
| **위반 시** | 정합성 오류 기록, 학습 데이터에서 제외 ([INV-13](e000a-entity-relationships.md)) |

### INV-EVA-05 — decision_quality는 outcome_quality와 독립적으로 산출된다

`decision_quality = f(quality)` 같은 종속 계산은 금지한다. 결과에서 결정 품질을 역산하면 Rule EVA-004가 무의미해진다.

| | |
|---|---|
| **위반 시** | 평가기 구현 결함. 해당 평가기의 출력을 Learning에서 격리 |
| **탐지** | 두 값의 상관계수가 지속적으로 0.95를 넘으면 경보 |

### INV-EVA-06 — Evaluation은 불변이다

| | |
|---|---|
| **위반 시** | 저장 계층이 쓰기 거부. 정정은 `supersedes` 체인으로만 |

---

## 6. Lifecycle

```
Pending → InProgress → Completed ──▶ Superseded
   │                       │
   │                       └──▶ Disputed ──▶ Completed (재판정)
   └──▶ Skipped
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Pending** | 평가 큐에 등록됨 | Outcome 생성 |
| **InProgress** | 평가 수행 중 | 평가기 배정 |
| **Completed** | 판정 확정 | 점수·verdict 산출 |
| **Disputed** | 사용자가 판정에 이의 제기 | 반대 Feedback 수신 |
| **Superseded** | 새 평가로 대체 | deferred / consensus 평가 생성 |
| **Skipped** | 평가 생략 | 저영향 Task + 비용 정책 (EVA-008) |

### 6.1 Disputed 처리

```
eva_512  automatic  verdict: accept   quality 0.93
   │
   │ 사용자 Feedback: "이 카피는 우리 톤이 아니다" (fb_881)
   ▼
eva_512  → Disputed
   │
   ▼
eva_530  human  verdict: reject  quality 0.55
         supersedes: eva_512
         feedback_ids: [fb_881]
```

**자동 평가가 틀렸다는 사실 자체가 학습 데이터다.** 자동 평가기와 인간 판정의 괴리는 Rubric 보정의 입력이 된다.

---

## 7. Relationships

```
Outcome 014 ──1:0..N──▶ Evaluation 015 ──1:0..N──▶ Memory 010 ──▶ Knowledge 011
                             ▲     │
Feedback 012 ──N:M──────────┘     │
Decision 009 ◀──검토(decision_quality)
Goal 001 ◀──기준(goal_alignment)
Resource 007 ◀──observed_score 갱신
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Outcome](e014-outcome.md) | 평가 대상 | `Outcome 1:0..N Evaluation` |
| [Feedback](e012-feedback.md) | 평가의 입력 신호 | `Feedback N:M Evaluation` |
| [Decision](e009-decision.md) | `decision_quality`로 사후 검토 | `Decision 1:0..N Evaluation` |
| [Goal](e001-goal.md) | `goal_alignment`의 판정 기준 | `Goal 1:0..N Evaluation` |
| [Memory](e010-memory.md) | 평가 결과가 경험으로 축적됨 | `Evaluation 1:0..N Memory` |
| [Resource](e007-resource.md) | `observed_score`를 갱신하는 권위 있는 신호 | `Resource 1:0..N Evaluation` |
| [Task](e005-task.md) | verdict가 Task 상태를 전이시킨다 | `Task 1:0..N Evaluation` |
| [Policy](e019-policy.md) | 어떤 Task에 어떤 평가를 강제할지 규정 | `Policy 1:N Evaluation` |

---

## 8. Canonical Representation

```json
{
  "evaluation_id": "eva_512",
  "outcome_id": "out_331",
  "task_id": "task_004",
  "evaluator": "eval_engine:v3",
  "evaluator_type": "automatic",
  "rubric_id": "rubric_copywriting_v2",
  "rubric_version": "2.1",
  "scores": {
    "quality": 0.93,
    "goal_alignment": 0.87,
    "efficiency": 0.95,
    "satisfaction": null,
    "composite": 0.91
  },
  "decision_review": {
    "decision_id": "dec_101",
    "decision_quality": 0.90,
    "prediction_error": { "utility": 0.02, "cost": 0.07, "latency_ms": 1020 }
  },
  "verdict": "accept",
  "adopted": true,
  "rationale": [
    "카피 3종 중 2종이 타겟 관심사(내신 관리)를 직접 언급",
    "금칙어·과장 광고 표현 없음",
    "예상 비용 0.35 USD 대비 0.42 USD로 20% 초과했으나 예산 내"
  ],
  "feedback_ids": [],
  "supersedes": null,
  "status": "Completed",
  "evaluated_at": "2026-08-04T09:31:10Z"
}
```

기계가 읽을 수 있는 스키마: [`evaluation.schema.json`](../intent-os-spec/schemas/evaluation.schema.json)

---

## 9. Validation Rules

```
Evaluation 생성 요청
  ↓
outcome_id 존재 확인 ── 없으면 반려
  ↓
Outcome.status = void ? ── Yes → Skipped 생성 후 종료
  ↓
evaluator 존재 확인 (EVA-003) ── 없으면 반려
  ↓
rubric_id 존재 + 버전 확인 (EVA-007) ── 없으면 기본 Rubric 적용 + 경고
  ↓
4축 점수 산출
  ├── quality         Rubric 기반
  ├── goal_alignment  Goal 지표 델타 + measurement_lag 고려
  ├── efficiency      Outcome.cost / 기대 비용
  └── satisfaction    Feedback 있으면 산출, 없으면 null
  ↓
범위 검사 0.0~1.0 (INV-EVA-03) ── 위반 시 거부
  ↓
decision_quality 독립 산출 (EVA-004)
  기준: Decision.inputs_snapshot 만으로 그 선택이 최선이었는가
  ↓
prediction_error 계산 (예측 − 실측)
  ↓
verdict 결정 (§9.3)
  ↓
evaluated_at ≥ Outcome.measured_at 확인 (INV-EVA-04)
  ↓
Completed → 동결 → Event 발행 (evaluation.completed)
  ↓
후속 트리거
  ├── verdict별 Task 상태 전이
  ├── Memory 기록                   → e010
  ├── Resource observed_score 갱신  → e025
  ├── Decision status → Evaluated   → e009
  └── measurement_lag 있으면 deferred Evaluation 예약
```

### 9.1 Composite Score

$$Composite = (Q \times W_q) + (A \times W_a) + (E \times W_e) + (S \times W_s)$$

가중치는 Task의 성격에 따라 달라지며, **사용한 가중치를 반드시 함께 기록한다**([Decision §6](e009-decision.md)의 원칙과 동일).

| Task 성격 | Wq | Wa | We | Ws |
|---|---|---|---|---|
| 창작 (카피 작성) | 0.40 | 0.25 | 0.15 | 0.20 |
| 조사 (경쟁 분석) | 0.30 | 0.35 | 0.25 | 0.10 |
| 자동화 (주간 리포트) | 0.20 | 0.20 | 0.50 | 0.10 |
| 고영향 (예산 집행) | 0.25 | 0.45 | 0.15 | 0.15 |

`satisfaction`이 `null`이면 `Ws`를 나머지 축에 비례 배분한다.

### 9.2 평가 깊이 결정

Rule EVA-008에 따라 평가 비용을 Task 영향도에 맞춘다.

| Task 영향도 | 평가 방식 | 비용 |
|---|---|---|
| Low (자동 리포트 생성) | 규칙 기반 자동 평가만 | ~0 |
| Medium (카피 작성) | LLM 자동 평가 | 실행 비용의 5~10% |
| High (랜딩페이지 개편) | 자동 + peer 교차 평가 | 실행 비용의 20% |
| Critical (300만원 광고 집행) | 자동 + human + deferred | 제한 없음 |

### 9.3 Verdict 결정 규칙

```
composite ≥ 0.80  AND  Hard Constraint 위반 없음     → accept
0.60 ≤ composite < 0.80  AND  보완 가능              → accept_with_revision
composite < 0.60                                     → reject
Hard Constraint 위반 OR Policy 위반                   → reject (점수 무관)
평가 축 중 하나라도 산출 불가                          → inconclusive
Task 영향도 = Critical  AND  evaluator_type=automatic → escalate
```

---

## 10. Examples

### 예시 1 — 자동 평가 (즉시)

```
out_331  카피 3종 / 0.42 USD / 1,820ms
  ↓
eva_512  automatic  rubric_copywriting_v2
         quality 0.93  alignment 0.87(추정)  efficiency 0.95
         decision_quality 0.90
         verdict accept
```

`goal_alignment 0.87`은 **추정치**다. `measurement_lag: P14D`이므로 deferred 평가가 예약된다.

### 예시 2 — Deferred 평가 (2주 뒤)

```
2026-08-18  광고 집행 결과 확정: 모집 41 → 63명 (+22)
  ↓
eva_690  deferred
         supersedes: eva_512
         quality 0.93 (변동 없음)
         goal_alignment 0.94  ← 추정 0.87에서 상향
         verdict accept
         rationale: ["2주 누적 랜딩 방문 1,820건 중 카피 A 유입이 61%"]
```

`goal_alignment`의 진짜 값은 여기서 확정된다.

### 예시 3 — 좋은 결정, 나쁜 결과 (Rule EVA-004)

```
dec_100  GPT 선택 (utility 0.88, 당시 GPT의 rate limit 이력 없음)
  ↓
exe_219  Failed (429 Too Many Requests)
  ↓
out_330  failed  cost 0.11 USD
  ↓
eva_505  quality 0.0   goal_alignment 0.0   efficiency 0.0
         decision_quality 0.85   ← 낮지 않다
         rationale: [
           "선택 시점의 inputs_snapshot에 rate limit 징후 없음",
           "Utility 0.88은 당시 데이터 기준 타당한 값",
           "장애는 예측 범위 밖"
         ]
         verdict reject
```

**결과는 0점인데 결정은 0.85점이다.** 이 구분이 없으면 시스템은 "GPT는 나쁘다"고 잘못 학습한다. 올바른 학습 신호는 "GPT의 가용성 지표를 inputs_snapshot에 추가하라"이다.

### 예시 4 — 나쁜 결정, 좋은 결과

```
dec_140  가장 싼 Resource를 선택 (utility 0.61, 품질 지표 확인 생략)
  ↓
out_390  succeeded  quality 0.91  (운 좋게 잘 나옴)
  ↓
eva_601  quality 0.91  decision_quality 0.35
         rationale: [
           "필수 Capability(analysis.audience) 매칭을 검증하지 않음",
           "결과 품질은 우연. 동일 선택의 기대 품질은 0.52"
         ]
         verdict accept   (결과물은 채택)
```

산출물은 채택하되(`adopted: true`) 결정 로직은 교정 대상으로 표시한다.

### 예시 5 — 이의 제기

```
eva_512  automatic  accept  quality 0.93
  ↓ fb_881  대표: "우리 학원 톤이 아니다. 너무 자극적"
  ↓
eva_512 → Disputed
  ↓
eva_530  human:대표   quality 0.55   verdict reject
         supersedes eva_512
  ↓
학습 신호: rubric_copywriting_v2에 "브랜드 톤 적합성" 축 누락
```

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **Feedback이 영영 오지 않음** | `satisfaction: null` 유지. 가중치를 나머지 축에 배분(§9.1). null을 0으로 대체하면 안 된다 — 만족하지 않은 것과 응답하지 않은 것은 다르다 |
| **Goal 지표가 아예 측정 불가** | `goal_alignment`를 Task의 Expected Output 충족도로 대체하고 `alignment_proxy: true` 표시. `inconclusive` 남발보다 낫다 |
| **자동 평가와 인간 평가가 엇갈림** | 인간 평가가 우선한다. 단 자동 평가를 삭제하지 않는다. 괴리 자체가 Rubric 보정 데이터다 |
| **peer 평가가 3개인데 모두 다름** | `consensus` Evaluation을 생성. 가중 중앙값을 쓰고 분산을 `rationale`에 기록. 분산이 크면 `escalate` |
| **평가 비용이 실행 비용을 초과** | Rule EVA-008 위반. 평가 깊이를 한 단계 낮추고 경고를 남긴다 |
| **Collaborative 실행의 미채택 결과** | 정상 평가한다. `adopted: false`. 미채택 결과의 품질 점수도 Resource 성능 데이터로 쓴다 |
| **Outcome.status = void** | 평가하지 않는다. `Skipped` 상태의 Evaluation을 생성해 "평가하지 않기로 했음"을 명시적으로 남긴다 |
| **재평가가 5회 이상 반복** | 판정 불안정의 신호. Rubric 또는 Goal 정의에 문제가 있다. `escalate`하고 Rubric 검토를 트리거 |
| **decision_quality를 판정할 Decision이 없음** | INV-02 위반 상태다. `decision_quality: null` + 정합성 경보 발행 |

---

## 12. Open Issues (v1.0)

### Rubric의 표준 스키마

`rubric_id`를 참조만 하고 Rubric 자체의 구조는 정의하지 않았다. 평가 축·척도·예시(anchor)를 담는 Rubric Entity가 필요한지, 아니면 [Policy](e019-policy.md)의 하위 개념으로 둘지 미정이다.

### decision_quality의 정량화 방법

"그 시점에 알 수 있었던 정보만으로 최선이었는가"를 어떻게 계산하는가. 후보군을 `inputs_snapshot`으로 재실행(counterfactual replay)하는 방식이 이상적이지만 비용이 크다. 근사 방법의 표준이 필요하다.

### Deferred 평가의 만료

`measurement_lag`가 지났는데 지표를 여전히 측정할 수 없으면 언제까지 기다릴 것인가. 무한 대기는 Evaluation 큐를 오염시킨다.

### 평가자 편향의 측정

인간 평가자마다 후한 정도가 다르다. 평가자별 캘리브레이션(z-score 정규화 등)이 없으면 `human` 평가끼리도 비교가 불가능하다.

### 앞으로 보강해야 할 항목

- Rubric Entity 정의 여부 결정
- `consensus` 평가의 가중 합의 알고리즘 명세
- 평가 축의 확장 규칙 (4축 외 도메인별 축 추가)
- 실제 예시 30~50개
