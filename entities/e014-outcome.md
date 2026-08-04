# Entity 014: Outcome

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Outcome is the immutable record of what an Execution actually produced — its artifacts, measured cost and latency, errors, and observed effect on the Goal.**

> Outcome은 하나의 Execution이 **실제로 무엇을 만들어냈는가**에 대한 불변 기록이며, 산출물·실측 비용·실측 지연·오류·Goal에 미친 관측된 영향을 담는다.

여기서 중요한 단어는 **관측(Observed)** 이다.

Outcome은 **측정값만** 담는다. "좋았다 / 나빴다"는 판단은 담지 않는다. 그것은 [Evaluation](e015-evaluation.md)의 몫이다.

```
Outcome     카피 3종 생성 · 0.42 USD · 1,820ms · 오류 0건     ← 사실
Evaluation  품질 0.93 · Goal 기여 0.87 · 채택함              ← 판단
```

이 분리가 무너지면 결과론 편향(Hindsight Bias)이 데이터에 섞인다. 같은 Outcome을 두 평가자가 다르게 판정할 수 있어야 하고, 시간이 지나 재평가할 수도 있어야 한다. **사실은 하나, 판단은 여럿이다.**

---

## 2. Outcome은 무엇이 아닌가?

### Outcome은 Evaluation이 아니다

❌ `품질 0.93, 아주 좋음` — 이건 [Evaluation](e015-evaluation.md)이다.

| | Outcome | Evaluation |
|---|---|---|
| 성격 | 측정 (Measurement) | 판정 (Judgment) |
| 개수 | Execution당 1개 | Outcome당 0..N개 |
| 재생성 | 불가 (실행을 다시 해야 함) | 가능 (같은 Outcome을 재평가) |
| 평가자 | 없음 | 반드시 있음 |

### Outcome은 Artifact가 아니다

❌ `광고 카피 3종 텍스트` — 이건 [Artifact](e016-artifact.md)다.

Outcome은 **담는 그릇**, Artifact는 **담긴 것**이다. Outcome은 Artifact를 참조로만 가진다.

```
Outcome out_331
├── artifacts: ["art_450"]     ← 참조
├── cost: 0.42 USD
└── latency_ms: 1820
```

Artifact가 없는 Outcome은 정상이다(실패, 분석 전용 실행 등). 반면 **Outcome이 없는 Artifact는 존재할 수 없다**([INV-05](e000a-entity-relationships.md)).

### Outcome은 Feedback이 아니다

❌ `사용자가 "두 번째 카피가 좋다"고 함` — 이건 [Feedback](e012-feedback.md)이다.

Feedback은 **시스템 외부에서 들어오는 입력**이고, Outcome은 **시스템이 스스로 관측한 기록**이다. Feedback은 Outcome이 나온 한참 뒤에 도착할 수도 있고 아예 안 올 수도 있다.

### Outcome은 성공/실패 boolean이 아니다

❌ `success: true`

Outcome에는 부분 성공이 존재한다. 카피 3종을 요청했는데 2종만 나왔다면 그것은 성공도 실패도 아닌 `partial`이다. 이진 판정은 정보를 버린다.

### Outcome은 Execution이 아니다

❌ `1,820ms 동안 RUNNING이었음` — 이건 [Execution](e013-execution.md)의 과정 정보다.

Execution은 **어떻게 시도했는가**, Outcome은 **무엇이 나왔는가**다. 둘의 비용·지연 필드가 겹쳐 보이지만 의미가 다르다 — Execution의 것은 제어용 실시간 값이고, Outcome의 것은 **동결된 정산값**이다.

---

## 3. Design Principles

### Rule OUT-001 — 모든 종료된 Execution은 Outcome을 낳는다

성공·실패·타임아웃·취소 예외 없이 1개다([INV-04](e000a-entity-relationships.md)). **실패도 결과다.** 실패 Outcome이 누락되면 Resource 성공률이 실제보다 높게 계산된다.

### Rule OUT-002 — Outcome은 측정값만 담는다

- ✅ `output_count: 3`, `cost: 0.42`, `error_count: 0`
- ❌ `quality: 0.93`, `verdict: "good"`, `recommended: true`

판단이 필요한 필드가 Outcome에 들어가려 하면, 그것은 Evaluation으로 가야 한다는 신호다.

### Rule OUT-003 — Outcome은 불변이다

생성 후 어떤 필드도 수정하지 않는다. 예외는 사후 링크(`evaluation_ids`) 추가뿐이다([INV-06](e000a-entity-relationships.md)).

늦게 도착한 정보(지연 결제, 사후 정산 비용)는 **보정 Outcome을 새로 만들고** `supersedes`로 연결한다.

### Rule OUT-004 — 비용과 지연은 실측값이다

추정값을 넣지 않는다. 측정 불가능한 Resource라면 안분값을 쓰되 `estimated: true`로 명시한다. `null`은 허용하지 않는다 — 비용 0으로 오인되면 Utility 계산이 왜곡된다.

### Rule OUT-005 — Artifact는 참조로 담는다

Outcome에 산출물 본문을 인라인으로 넣지 않는다. 영상·PDF 같은 대용량 산출물이 Outcome을 조회 불가능한 크기로 만든다.

### Rule OUT-006 — goal_progress는 관측 가능한 델타여야 한다

- ✅ `{ "metric": "enrollment_count", "before": 41, "after": 41, "delta": 0 }`
- ❌ `{ "goal_progress": 0.3 }` — 무엇을 근거로 0.3인지 알 수 없다

Goal 지표가 즉시 변하지 않는 Task(카피 작성 등)는 **`delta: 0`을 기록한다.** 비워두는 것과 0은 다르다. 0은 "측정했고 변화가 없었다"이고, 비움은 "측정하지 않았다"이다.

### Rule OUT-007 — 실패의 원인은 Execution에, 실패의 영향은 Outcome에

```
Execution.failure_class = "resource_unavailable"   ← 왜 실패했는가
Outcome.status = "failed", cost = 0.11 USD         ← 실패로 무엇을 잃었는가
```

---

## 4. Attributes

```
Outcome
├── Identity
│   ├── outcome_id
│   ├── execution_id
│   └── task_id
├── Result
│   ├── status
│   ├── artifacts[]
│   ├── output_summary
│   └── output_count
├── Measurement
│   ├── cost
│   ├── latency_ms
│   ├── usage
│   └── measured_at
├── Effect
│   ├── goal_progress[]
│   └── contributes_to_goal
├── Failure
│   ├── errors[]
│   └── partial_reason
└── Link
    ├── evaluation_ids[]
    └── supersedes
```

| 속성 | 의미 | 예 |
|---|---|---|
| **outcome_id** | 식별자 | `out_331` |
| **execution_id** | 낳은 실행 | `exe_220` |
| **task_id** | 대상 Task (조회 편의용 캐시) | `task_004` |
| **status** | 결과 구분 (§4.1) | `succeeded` |
| **artifacts** | 산출물 참조 목록 | `["art_450"]` |
| **output_summary** | 산출물 요약 (200자 이내) | `예비 고3 학부모 대상 카피 3종` |
| **output_count** | 산출물 개수 | `3` |
| **cost** | 정산된 실측 비용 | `{ "amount": 0.42, "currency": "USD", "estimated": false }` |
| **latency_ms** | 정산된 실측 지연 | `1820` |
| **usage** | 자원 사용량 | `{ "input_tokens": 1840, "output_tokens": 620 }` |
| **measured_at** | 측정 시각 | `2026-08-04T09:30:01.820Z` |
| **goal_progress** | Goal 지표의 관측 델타 (§4.2) | 아래 표 참조 |
| **contributes_to_goal** | Goal 집계 포함 여부 | `true` (Shadow는 `false`) |
| **errors** | 발생한 오류 목록 | `[]` |
| **partial_reason** | 부분 성공의 사유 | `null` |
| **evaluation_ids** | 이 Outcome에 대한 평가들 | `["eva_512"]` |
| **supersedes** | 대체한 이전 Outcome | `null` |

### 4.1 Outcome Status

```
Outcome
├── succeeded   기대 산출물이 전부 나옴
├── partial     일부만 나옴
├── failed      산출물 없이 종료
└── void        실행 자체가 무효 (취소, Shadow 폐기)
```

| status | 산출물 | 비용 | Goal 기여 | 예 |
|---|---|---|---|---|
| `succeeded` | 있음 | 발생 | 있음 | 카피 3종 요청 → 3종 산출 |
| `partial` | 일부 | 발생 | 있음 | 카피 3종 요청 → 2종 산출 |
| `failed` | 없음 | 발생 가능 | 없음 | API 429 오류 |
| `void` | 없음 | 발생 가능 | **없음** | 사용자 취소, Shadow 실행 |

**핵심:** `failed`와 `void`도 **비용은 발생한다.** 비용 0으로 기록하면 실제 예산 소진과 시스템 집계가 어긋난다.

### 4.2 goal_progress 구조

Goal 지표의 변화를 관측한 그대로 기록한다.

| 필드 | 의미 | 예 |
|---|---|---|
| `goal_id` | 어느 Goal의 지표인가 | `goal_001` |
| `metric` | 지표 이름 | `enrollment_count` |
| `before` | 실행 전 관측값 | `41` |
| `after` | 실행 후 관측값 | `41` |
| `delta` | 변화량 | `0` |
| `measurement_lag` | 지표가 반영되기까지의 지연 | `P14D` (14일) |

`measurement_lag`가 중요한 이유: 광고 카피를 오늘 만들어도 모집 인원은 2주 뒤에 움직인다. **즉시 델타가 0이라고 해서 기여가 없는 것이 아니다.** 이 판단은 Evaluation의 Deferred Evaluation(§[e015 §4.1](e015-evaluation.md))이 담당한다.

---

## 5. Invariants

### INV-OUT-01 — Outcome은 정확히 하나의 Execution에 속한다

| | |
|---|---|
| **위반 시** | 생성 거부. `execution_id` 없는 Outcome은 출처를 알 수 없다 |

### INV-OUT-02 — Execution당 Outcome은 최대 1개다

| | |
|---|---|
| **위반 시** | 나중에 생성된 것을 거부. 정정이 필요하면 `supersedes` 체인을 쓴다 |

### INV-OUT-03 — status가 succeeded면 artifacts는 비어 있지 않다

단, "분석 결과가 곧 산출물"인 Task는 `output_summary`가 Artifact 역할을 하므로 예외로 인정하되 `artifacts: []` + `output_count: 0`을 명시해야 한다.

| | |
|---|---|
| **위반 시** | `succeeded` → `partial`로 강등하고 `partial_reason: "no_artifact"`를 기록 |

### INV-OUT-04 — 비용은 음수가 아니고 종료 후 변하지 않는다

| | |
|---|---|
| **위반 시** | 정정은 새 Outcome + `supersedes`로만 가능. 기존 레코드 수정은 저장 계층이 거부 |

### INV-OUT-05 — contributes_to_goal이 false면 Goal 집계에 포함되지 않는다

Shadow·Rehearsal Execution의 Outcome이 Goal Progress에 섞이면 성과 측정이 오염된다.

| | |
|---|---|
| **위반 시** | 집계 쿼리에서 제외. 이미 포함되었다면 재집계 |
| **주의** | **비용은 예외다.** Shadow 실행의 비용도 예산에서는 차감한다 |

### INV-OUT-06 — measured_at은 Execution.finished_at 이상이다

| | |
|---|---|
| **위반 시** | 정합성 오류 기록, 학습 데이터에서 제외 ([INV-13](e000a-entity-relationships.md)) |

---

## 6. Lifecycle

Outcome은 내용이 불변이므로 상태 전이가 최소한이다.

```
Produced → Evaluated → Archived
    │
    └──▶ Superseded   (보정 Outcome 생성 시)
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Produced** | 생성됨. 아직 평가되지 않음 | Execution 종료 |
| **Evaluated** | 하나 이상의 Evaluation이 연결됨 | Evaluation 생성 |
| **Superseded** | 보정 Outcome으로 대체됨. 기록은 영구 보존 | 사후 정산·지연 데이터 도착 |
| **Archived** | 활성 조회 대상에서 제외. 통계는 유지 | 보존 정책의 기간 경과 |

### 6.1 Superseded가 필요한 경우

| 상황 | 조치 |
|---|---|
| 광고 플랫폼의 실제 청구액이 3일 뒤 확정 | 보정 Outcome 생성. `cost` 갱신 |
| 타임아웃 후 늦게 도착한 결과 | 보정 Outcome. `late_arrival: true` |
| 인간 Resource의 작업 시간이 사후 보고됨 | 보정 Outcome. `latency_ms` 갱신 |

**원본은 지우지 않는다.** "시스템이 그 시점에 무엇을 알고 있었는가"가 Decision 품질 평가의 기준이기 때문이다.

---

## 7. Relationships

```
Execution 013 ──1:0..1──▶ Outcome 014 ──1:0..N──▶ Artifact 016
                              │
                              ├──1:0..N──▶ Evaluation 015
                              │
                              └──기여──▶ Goal 001 (goal_progress)

Feedback 012 ──────────────▶ Evaluation 015 (Outcome을 직접 참조하지 않는다)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Execution](e013-execution.md) | Outcome을 낳는 유일한 출처 | `Execution 1:0..1 Outcome` |
| [Artifact](e016-artifact.md) | Outcome이 담는 산출물 | `Outcome 1:0..N Artifact` |
| [Evaluation](e015-evaluation.md) | Outcome에 대한 판정 | `Outcome 1:0..N Evaluation` |
| [Goal](e001-goal.md) | `goal_progress`로 지표 델타를 기여 | `Goal 1:0..N Outcome` |
| [Decision](e009-decision.md) | 예측 vs 실측 대조의 상대편 | `Decision 1:0..N Outcome` (Execution 경유) |
| [Resource](e007-resource.md) | `observed_score` 갱신의 원천 데이터 | `Resource 1:0..N Outcome` |
| [Feedback](e012-feedback.md) | **직접 관계 없음.** Evaluation을 통해서만 만난다 | — |

---

## 8. Canonical Representation

```json
{
  "outcome_id": "out_331",
  "execution_id": "exe_220",
  "task_id": "task_004",
  "status": "succeeded",
  "artifacts": ["art_450"],
  "output_summary": "예비 고3 학부모 대상 인스타그램 광고 카피 3종",
  "output_count": 3,
  "cost": { "amount": 0.42, "currency": "USD", "estimated": false },
  "latency_ms": 1820,
  "usage": { "input_tokens": 1840, "output_tokens": 620 },
  "measured_at": "2026-08-04T09:30:01.820Z",
  "goal_progress": [
    {
      "goal_id": "goal_001",
      "metric": "enrollment_count",
      "before": 41,
      "after": 41,
      "delta": 0,
      "measurement_lag": "P14D"
    }
  ],
  "contributes_to_goal": true,
  "errors": [],
  "partial_reason": null,
  "evaluation_ids": ["eva_512"],
  "supersedes": null,
  "status_lifecycle": "Evaluated"
}
```

실패 Outcome도 같은 구조다.

```json
{
  "outcome_id": "out_330",
  "execution_id": "exe_219",
  "task_id": "task_004",
  "status": "failed",
  "artifacts": [],
  "output_count": 0,
  "cost": { "amount": 0.11, "currency": "USD", "estimated": false },
  "latency_ms": 31000,
  "measured_at": "2026-08-04T09:12:31Z",
  "goal_progress": [],
  "contributes_to_goal": true,
  "errors": [
    { "code": "rate_limit_exceeded", "message": "429 Too Many Requests", "retryable": true }
  ],
  "partial_reason": null,
  "evaluation_ids": [],
  "supersedes": null
}
```

기계가 읽을 수 있는 스키마: [`outcome.schema.json`](../intent-os-spec/schemas/outcome.schema.json)

---

## 9. Validation Rules

```
Outcome 생성 요청 (Execution 종료 훅)
  ↓
execution_id 존재 + 종료 상태 확인 ── 아니면 반려
  ↓
동일 execution_id의 기존 Outcome 확인 (INV-OUT-02) ── 존재 시 반려
  ↓
status 결정
  ├── artifacts 있음 + 기대 개수 충족 → succeeded
  ├── artifacts 있음 + 기대 개수 미달 → partial (+ partial_reason 필수)
  ├── Execution.status = Aborted        → void
  └── 그 외                             → failed
  ↓
cost 검사 (OUT-004)
  ├── null           → 거부. 안분값 계산 요구
  ├── amount < 0     → 거부 (INV-OUT-04)
  └── estimated=true → 경고 로그, 통과
  ↓
measured_at ≥ Execution.finished_at 확인 (INV-OUT-06)
  ↓
goal_progress 항목별 metric 존재 확인 (Goal에 정의된 지표인가)
  ↓
판단성 필드 검출 (OUT-002) ── quality / verdict / rating 발견 시 거부
  ↓
Outcome 생성 → 동결 → Event 발행 (outcome.produced)
  ↓
후속 트리거
  ├── Evaluation 큐 등록          → e015
  ├── Resource Profile 갱신 신호  → e025
  └── Budget 차감                 → e004 Constraint
```

### 9.1 status 판정 규칙표

| Execution.status | artifacts | 기대 개수 충족 | → Outcome.status |
|---|---|---|---|
| Completed | 있음 | 충족 | `succeeded` |
| Completed | 있음 | 미달 | `partial` |
| Completed | 없음 | — | `partial` (INV-OUT-03) |
| Failed | 없음 | — | `failed` |
| Failed | 일부 있음 | — | `partial` |
| TimedOut | — | — | `failed` |
| Aborted | — | — | `void` |

---

## 10. Examples

### 예시 1 — 성공

```
exe_220 Claude / 카피 작성 / Completed
  ↓
out_331  succeeded
         artifacts: [art_450]  output_count: 3
         cost: 0.42 USD  latency: 1,820ms
         goal_progress: enrollment_count 41 → 41 (delta 0, lag P14D)
```

`delta: 0`인데 정상이다. 카피를 만든 날 학생이 늘지 않는 것은 당연하다.

### 예시 2 — 부분 성공

```
out_338  partial
         artifacts: [art_461, art_462]   output_count: 2   (요청 3)
         partial_reason: "3번째 카피가 금칙어 필터에 걸려 생성 중단"
         cost: 0.38 USD
```

Task는 `Completed`가 아니라 재실행 대상이 된다. 다만 **이미 나온 2종은 버리지 않는다.**

### 예시 3 — 광고 집행 (지표가 실제로 움직이는 Task)

```
exe_301  광고 플랫폼 API / 인스타 광고 2주 집행 / Completed
  ↓
out_402  succeeded
         cost: { amount: 1200000, currency: "KRW", estimated: false }
         goal_progress: [
           { metric: "ad_impressions", before: 0,  after: 184000, delta: 184000 },
           { metric: "landing_visits", before: 320, after: 2140, delta: 1820 },
           { metric: "enrollment_count", before: 41, after: 63, delta: 22 }
         ]
```

Goal(100명 모집)의 실제 진척이 여기서 처음 나타난다. 카피 작성 Task의 기여는 **이 Outcome을 통해 간접적으로 귀속**된다.

### 예시 4 — 보정 Outcome

```
out_402  cost 1,200,000 KRW  (플랫폼 예상 청구액)
   │  3일 뒤 실제 청구액 1,247,300원 확정
   ▼
out_419  supersedes: "out_402"
         cost 1,247,300 KRW
```

원본 `out_402`는 그대로 남는다. Decision 품질 평가는 "그 시점에 알던 값"으로 해야 하기 때문이다.

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **산출물이 없는 것이 정상인 Task** | 검증 Task, 조사 Task 등. `artifacts: []` + `output_summary`에 결과 요약. `status: succeeded` 허용 (INV-OUT-03 예외 조항) |
| **Goal 지표를 측정할 수 없는 시점** | `goal_progress: []`가 아니라 `delta: 0` + `measurement_lag` 기록. 측정 안 함과 변화 없음을 구분한다 |
| **하나의 Execution이 여러 Goal에 기여** | `goal_progress` 배열에 Goal별 항목을 각각 기록. 기여도 배분은 Evaluation이 판정한다 |
| **비용이 나중에 확정되는 Resource** | 잠정 Outcome을 즉시 생성(`estimated: true`)하고, 확정 시 보정 Outcome으로 대체 |
| **Collaborative 실행에서 채택되지 않은 결과** | Outcome은 정상 생성된다. `status: succeeded`이고 Artifact도 남는다. "채택 여부"는 Evaluation의 `adopted: false`로 표현한다 |
| **Shadow 실행의 Outcome** | `contributes_to_goal: false`. Goal 집계에서 제외하되 **비용은 예산에서 차감**하고 Resource 점수 갱신에는 사용한다 |
| **동일 Artifact가 두 Outcome에 나타남** | 금지([INV-05](e000a-entity-relationships.md)). 재사용이라면 새 Artifact를 만들고 `derived_from`으로 원본을 가리킨다 |
| **오류는 있었지만 산출물은 나옴** | `status: succeeded` + `errors`에 기록. 오류의 존재가 실패를 뜻하지 않는다 (재시도 후 성공 등) |
| **지표가 나빠짐 (delta 음수)** | 정상 기록이다. `delta: -5`도 사실이다. 나쁜 결과를 기록하지 않는 시스템은 학습하지 못한다 |

---

## 12. Open Issues (v1.0)

### 기여도 귀속(Attribution) 문제

`out_402`에서 학생이 22명 늘었을 때, 그 공을 카피 작성(`task_004`)·랜딩페이지 개선(`task_005`)·광고 집행(`task_006`) 중 무엇에 얼마나 돌릴 것인가. 현재 Outcome은 **자기 실행의 델타만** 기록하고 배분은 하지 않는다. 배분 모델(Last-touch / Linear / Shapley)의 선택이 미정이다.

### 지연 지표(Lagging Metric)의 표준 표현

`measurement_lag`를 ISO 8601 기간으로 두었으나, "2주 뒤 측정"과 "누적 효과가 8주에 걸쳐 나타남"은 다른 개념이다. 감쇠 곡선(Decay Curve)의 표현이 필요하다.

### 다중 통화와 비용 정규화

예제에 USD와 KRW가 섞여 있다. 예산 제약([Constraint](e004-constraint.md))은 단일 통화로 평가되어야 하므로 환율 스냅샷의 저장 위치와 시점 기준이 정해져야 한다.

### 앞으로 보강해야 할 항목

- `usage` 필드의 Resource 타입별 표준 스키마
- 보정 Outcome 체인의 최대 깊이와 조회 표준
- Outcome 보존 정책 (Archived 전이 기준, 통계 유지 범위)
- 실제 예시 30~50개
