# Entity 013: Execution

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Execution is the persistent control record of one attempt to perform a single Task with a selected Resource.**

> Execution은 선택된 Resource로 하나의 Task를 수행하는 **한 번의 시도**에 대한 영속적 제어 기록이다.

여기서 중요한 단어는 **한 번의 시도(One Attempt)** 다.

같은 Task를 3번 재시도했다면 Execution은 **3개**다. 하나가 갱신되는 것이 아니다. 실패한 시도의 기록도 지우지 않는다. 그것이 Resource 성능 측정의 데이터이기 때문이다.

### 왜 Entity인가

Execution은 운영체제의 `task_struct`에 해당한다.

```
"지금 실행 중이다"     → Executing  (Process, 저장 대상 아님)
 Execution            → Entity     (제어 블록, 저장된다)
 Execution.status     → Runtime State (RUNNING 같은 순간값)
```

이 구분의 근거는 [e000a §1](e000a-entity-relationships.md)에 있다. 판별 기준은 하나다 — **1년 뒤에 조회해야 하는가.** Execution 이력이 없으면 Resource Drift를 감지할 수 없다.

---

## 2. Execution은 무엇이 아닌가?

### Execution은 Task가 아니다

❌ `인스타그램 광고 카피 3종 작성` — 이건 [Task](e005-task.md)다.

| | Task | Execution |
|---|---|---|
| 성격 | 무엇을 해야 하는가 (의도) | 실제로 어떻게 시도했는가 (사실) |
| Resource | 모른다 (Resource Agnostic) | 정확히 하나를 안다 |
| 개수 | Goal당 고정 | 재시도마다 증가 |
| 수정 | 가능 (재분해 등) | 종료 후 불변 |

### Execution은 Decision이 아니다

❌ `Claude를 선택함 (utility 0.91)` — 이건 [Decision](e009-decision.md)이다.

Decision은 **선택의 기록**, Execution은 **그 선택을 실행한 기록**이다. Decision은 실행되지 않을 수도 있다(Rejected). Execution은 항상 Decision에서 파생된다(INV-03).

### Execution은 Outcome이 아니다

❌ `카피 3종 생성, 품질 0.93` — 이건 [Outcome](e014-outcome.md)이다.

```
Execution   실행 과정의 사실     시작 09:30:00, 종료 09:30:01.82, 재시도 0회
Outcome     실행 결과물의 사실   카피 3종, 비용 0.42 USD, 오류 없음
Evaluation  결과에 대한 판정     품질 0.93, Goal 기여 0.87
```

Execution은 **끝나야** Outcome을 낳는다. Execution 없는 Outcome은 존재할 수 없다.

### Execution은 Log가 아니다

❌ `[09:30:00] POST /v1/messages 200 OK` — 이건 로그다.

로그는 Execution의 **하위 데이터**(`logs_ref`)로 참조될 뿐이다. Execution은 구조화된 상태·비용·재시도 정보를 갖는 Entity이고, 로그는 그 안에서 벌어진 일의 원시 기록이다.

### Execution은 Session이 아니다

❌ `사용자가 오늘 오전에 시스템을 쓴 전체 흐름` — 이건 [Session](e021-session.md)이다.

Session이 Goal 하나의 전체 처리 단위라면, Execution은 그 안의 Task 하나의 시도 단위다. **Session 1 : Execution 0..N** 이다.

> **v0.1 명세 정정:** [Volume 3 §3](../v3-runtime.md)의 "Execution Instance"(Goal 단위 실행)는 본 Entity가 아니라 [Session](e021-session.md)이다. 이름이 같아 혼동을 낳았으므로 v1.0에서 분리했다.

---

## 3. Design Principles

### Rule EXE-001 — Execution은 정확히 하나의 Task와 하나의 Resource를 가진다

두 Task를 동시에 처리하는 Execution은 없다. Pipeline 실행이라면 **Task마다 별도 Execution**을 만들고 `parent_execution_id`로 묶는다.

- ✅ `task_004` × `anthropic:claude-5` → `exe_220`
- ❌ `task_004 + task_005` × `Claude` → 하나의 Execution

### Rule EXE-002 — Execution은 Decision을 참조해야 한다

`decision_id`가 없는 Execution은 생성할 수 없다. 대안이 하나뿐이어도 Forced Action Decision을 먼저 남긴다(INV-02).

### Rule EXE-003 — 재시도는 새 Execution을 만든다

```
❌  exe_220.retry_count += 1        (기존 레코드 갱신)
✅  exe_221 { attempt: 2, previous_execution_id: "exe_220" }
```

`retry_count`는 **Task 관점의 누적 횟수**를 캐시할 뿐이고, 진실의 원천은 Execution 체인이다. 시도마다 비용·지연·오류가 다르므로 하나로 뭉개면 학습 데이터가 손실된다.

### Rule EXE-004 — 종료된 Execution은 불변이다

종료 상태(§6)에 도달한 뒤에는 어떤 필드도 수정하지 않는다. 유일한 예외는 사후 링크(`outcome_id`) 추가다(INV-06).

### Rule EXE-005 — 모든 종료는 Outcome을 낳는다

성공이든 실패든 취소든 타임아웃이든 예외 없이 [Outcome](e014-outcome.md) 1개를 생성한다(INV-04). **실패도 결과다.**

### Rule EXE-006 — 비용과 지연은 실측한다

`cost`와 `latency_ms`는 Decision 시점의 **추정치가 아니라 실측치**다. 추정치는 Decision의 `inputs_snapshot`에 이미 보존되어 있다. 둘의 차이가 Prediction Model 보정의 입력이 된다.

### Rule EXE-007 — Execution은 Goal을 모른다

Execution은 `task_id`만 안다. Goal 정보가 필요하면 Task를 거쳐 조회한다. 계층을 건너뛰는 참조는 금지된다([Rule REL-004](e000a-entity-relationships.md)).

### Rule EXE-008 — 취소는 상태이지 삭제가 아니다

사용자가 중단해도 Execution 레코드는 남는다. `Aborted` 상태로 전이하고 그때까지 발생한 비용을 기록한다.

---

## 4. Attributes

```
Execution
├── Identity
│   ├── execution_id
│   ├── task_id
│   ├── decision_id
│   └── session_id
├── Actor
│   ├── resource_id
│   └── agent_id            (Agent가 수행할 때만)
├── Attempt
│   ├── attempt
│   ├── previous_execution_id
│   └── parent_execution_id  (Pipeline / Composite)
├── Timing
│   ├── created_at
│   ├── started_at
│   ├── finished_at
│   └── timeout_ms
├── Measurement
│   ├── latency_ms
│   ├── cost
│   └── usage             (토큰, 호출 수 등)
├── Runtime
│   ├── status
│   ├── progress
│   ├── input_ref
│   └── logs_ref
├── Failure
│   ├── error
│   └── failure_class
└── Link
    └── outcome_id
```

| 속성 | 의미 | 예 |
|---|---|---|
| **execution_id** | 식별자 | `exe_220` |
| **task_id** | 수행 대상 Task | `task_004` |
| **decision_id** | 이 실행을 낳은 결정 | `dec_101` |
| **session_id** | 소속 Session | `ses_057` |
| **resource_id** | 실행 주체 | `anthropic:claude-5` / `human:copywriter_kim` |
| **agent_id** | Resource를 운용한 Agent | `agent_marketing_01` 또는 `null` |
| **attempt** | 몇 번째 시도인가 | `1` |
| **previous_execution_id** | 직전 시도 | `null` 또는 `exe_219` |
| **parent_execution_id** | 상위 Composite 실행 | `null` 또는 `exe_210` |
| **timeout_ms** | 제한 시간 | `120000` |
| **latency_ms** | 실측 지연 | `1820` |
| **cost** | 실측 비용 | `{ "amount": 0.42, "currency": "USD" }` |
| **usage** | 자원 사용량 | `{ "input_tokens": 1840, "output_tokens": 620 }` |
| **status** | 현재 상태 (§6) | `Completed` |
| **progress** | 진행률 0~1 | `1.0` |
| **input_ref** | 실제로 전달된 입력의 참조 | `blob://exe_220/input` |
| **logs_ref** | 원시 로그 참조 | `blob://exe_220/logs` |
| **error** | 오류 상세 | `null` |
| **failure_class** | 실패 분류 (§4.2) | `null` |
| **outcome_id** | 생성된 Outcome | `out_331` |

### 4.1 Execution Types

실행 형태에 따라 Execution의 구조가 달라진다.

```
Execution
├── Single        하나의 Resource가 단독 수행
├── Pipeline      여러 Resource가 순차 수행 (자식 Execution N개)
├── Collaborative 여러 Resource가 동일 Task를 병렬 수행 후 결과 합성
├── Shadow        실제 반영 없이 비교 목적으로만 수행
└── Rehearsal     비용이 큰 실행 전 소규모 검증 수행
```

| Type | 언제 쓰는가 | 예 |
|---|---|---|
| **Single** | 기본값 | 광고 카피 작성 → Claude |
| **Pipeline** | Capability 도메인이 다를 때 | 리서치(Perplexity) → 작성(Claude) → 검수(김 카피라이터) |
| **Collaborative** | Decision Confidence < 임계값 | Claude·GPT 동시 작성 후 우수안 채택 ([Volume 4-A §10](../v4a-decision-engine-detail.md)) |
| **Shadow** | 신규 Resource Cold Start | 신규 모델을 실제 반영 없이 병행 실행해 점수 수집 |
| **Rehearsal** | 고비용·비가역 작업 | 300만원 광고 집행 전 10만원 파일럿 |

**Shadow와 Rehearsal의 Outcome은 Goal Progress에 기여하지 않는다.** `contributes_to_goal: false`로 표시한다.

### 4.2 Failure Class

실패는 원인별로 분류해야 재시도 전략이 결정된다. [e005 §7](e005-task.md)의 실패 처리와 대응한다.

| failure_class | 의미 | 기본 조치 |
|---|---|---|
| `resource_unavailable` | API 장애, 인간 부재 | 동일 Resource 재시도 |
| `resource_incapable` | 능력 부족, 품질 미달 | 다른 Resource 재선택 |
| `input_insufficient` | 입력 정보 부족 | 상위 Task 또는 사용자에게 escalate |
| `timeout` | 제한 시간 초과 | 재시도 또는 Task 재분해 |
| `constraint_violation` | 비용·기한 제약 위반 | 중단. Replanning |
| `policy_violation` | Policy 위반 | 즉시 중단. 재시도 금지 |
| `internal_error` | 시스템 오류 | 재시도. 3회 초과 시 운영자 알림 |

---

## 5. Invariants

### INV-EXE-01 — 하나의 Execution은 하나의 Task·하나의 Resource만 갖는다

| | |
|---|---|
| **위반 시** | 생성을 거부한다. 복수 Task는 Composite Execution + 자식 Execution으로 표현 |

### INV-EXE-02 — 종료된 Execution은 정확히 하나의 Outcome을 갖는다

전역 불변식 [INV-04](e000a-entity-relationships.md)의 Execution 측 표현이다.

| | |
|---|---|
| **위반 시** | Runtime이 `status: failed`인 최소 Outcome을 자동 생성한다 |
| **탐지** | 상태 전이 훅 (Transition-time) |

### INV-EXE-03 — 실행 중인 Execution은 Task당 최대 1개다

같은 Task에 대해 `Running` 상태인 Execution이 둘 이상이면 중복 비용이 발생한다.

| | |
|---|---|
| **위반 시** | 나중에 시작된 Execution을 `Aborted`로 종료 |
| **예외** | Collaborative / Shadow Execution은 `mode` 필드로 구분되어 예외 처리 |

### INV-EXE-04 — 시각의 단조성

`created_at ≤ started_at ≤ finished_at` 이며, `latency_ms = finished_at − started_at`이다.

| | |
|---|---|
| **위반 시** | 정합성 오류로 기록하고 해당 레코드를 학습 데이터에서 제외 ([INV-13](e000a-entity-relationships.md)) |

### INV-EXE-05 — 재시도 체인은 순환하지 않는다

`previous_execution_id`를 따라가면 반드시 `attempt: 1`에 도달한다.

| | |
|---|---|
| **위반 시** | 체인 생성을 거부. 순환 경로를 오류로 반환 |

### INV-EXE-06 — 비용은 음수가 아니며 종료 후 증가하지 않는다

| | |
|---|---|
| **위반 시** | 비용 집계에서 제외하고 운영자에게 경고. Budget 계산 오류의 주요 원인이다 |

---

## 6. Lifecycle

```
Created → Queued → Running ──────────────▶ Completed
                      │  ▲                      │
                      ▼  │                      │  (종료 상태 4개는
                   Waiting                      │   모두 Outcome 생성)
                      │                         │
                      ├──────────────▶ Failed ──┤
                      ├──────────────▶ TimedOut─┤
                      └──────────────▶ Aborted ─┘
```

| 상태 | 의미 | 진입 조건 | 종료 상태 |
|---|---|---|---|
| **Created** | 레코드 생성. 아직 대기열에 없음 | Decision이 Applied로 전이 | |
| **Queued** | 실행 대기열 등록 | 선행 Task 완료, 자원 확보 | |
| **Running** | Resource가 수행 중 | Resource 호출 시작 | |
| **Waiting** | 외부 응답 대기 | 인간 Resource 회신 대기, 비동기 콜백 대기 | |
| **Completed** | 실행이 끝났고 산출물이 나옴 | Resource가 결과 반환 | ✅ |
| **Failed** | 오류로 종료 | 예외, 품질 미달, 제약 위반 | ✅ |
| **TimedOut** | 제한 시간 초과 | `now − started_at > timeout_ms` | ✅ |
| **Aborted** | 외부 요인으로 중단 | 사용자 취소, Policy 차단, Plan 폐기 | ✅ |

### 6.1 Completed ≠ 성공

[Task 상태 머신](e005-task.md)과 동일한 원칙이다.

> **Completed는 "실행이 끝났다"는 뜻이지 "잘 됐다"는 뜻이 아니다.**

성공 여부의 판정은 [Evaluation](e015-evaluation.md)의 몫이다. Completed된 Execution의 Outcome이 품질 미달로 평가되면, Task가 다시 `Failed`로 전이하고 새 Execution이 생성된다.

### 6.2 상태 전이와 Event

모든 전이는 [Event](e020-event.md)를 발생시킨다([INV-12](e000a-entity-relationships.md)).

| 전이 | Event Type |
|---|---|
| Created → Queued | `execution.queued` |
| Queued → Running | `execution.started` |
| Running → Waiting | `execution.waiting` |
| * → Completed | `execution.completed` |
| * → Failed / TimedOut | `execution.failed` |
| * → Aborted | `execution.aborted` |

---

## 7. Relationships

```
Decision 009 ──1:0..N──▶ Execution 013 ──1:0..1──▶ Outcome 014
     ▲                        │  ▲
     │                        │  └──1:0..N── Execution (자식, Pipeline)
  Task 005 ──1:0..N──────────┘
                              │
  Resource 007 ──1:0..N───────┤
  Agent 023 ──1:0..N──────────┤
  Session 021 ──1:0..N────────┘
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Task](e005-task.md) | Execution은 하나의 Task를 수행한다 | `Task 1:0..N Execution` |
| [Decision](e009-decision.md) | 모든 Execution은 하나의 Decision에서 파생된다 | `Decision 1:0..N Execution` |
| [Resource](e007-resource.md) | 실행 주체. 성능 이력의 귀속 대상 | `Resource 1:0..N Execution` |
| [Agent](e023-agent.md) | Resource를 운용한 주체 (있을 수도, 없을 수도) | `Agent 1:0..N Execution` |
| [Outcome](e014-outcome.md) | 종료 시 정확히 하나 생성 | `Execution 1:0..1 Outcome` |
| [Session](e021-session.md) | 어느 실행 단위에 속하는가 | `Session 1:0..N Execution` |
| [Workflow](e022-workflow.md) | 실행 순서를 정의. Execution을 만들지는 않는다 | `Workflow 1:0..N Execution` |
| [Event](e020-event.md) | 상태 전이마다 발생 | `Execution 1:N Event` |
| [Policy](e019-policy.md) | 실행 전·중 차단 권한을 가진다 | `Policy 1:N Execution` |

---

## 8. Canonical Representation

```json
{
  "execution_id": "exe_220",
  "task_id": "task_004",
  "decision_id": "dec_101",
  "session_id": "ses_057",
  "resource_id": "anthropic:claude-5",
  "agent_id": null,
  "mode": "single",
  "attempt": 1,
  "previous_execution_id": null,
  "parent_execution_id": null,
  "status": "Completed",
  "progress": 1.0,
  "contributes_to_goal": true,
  "created_at": "2026-08-04T09:29:58Z",
  "started_at": "2026-08-04T09:30:00Z",
  "finished_at": "2026-08-04T09:30:01.820Z",
  "timeout_ms": 120000,
  "latency_ms": 1820,
  "cost": { "amount": 0.42, "currency": "USD" },
  "usage": { "input_tokens": 1840, "output_tokens": 620 },
  "input_ref": "blob://exe_220/input",
  "logs_ref": "blob://exe_220/logs",
  "error": null,
  "failure_class": null,
  "outcome_id": "out_331"
}
```

실패한 Execution도 같은 구조를 가진다.

```json
{
  "execution_id": "exe_219",
  "task_id": "task_004",
  "decision_id": "dec_100",
  "resource_id": "openai:gpt-5",
  "attempt": 1,
  "status": "Failed",
  "progress": 0.4,
  "created_at": "2026-08-04T09:11:58Z",
  "started_at": "2026-08-04T09:12:00Z",
  "finished_at": "2026-08-04T09:12:31Z",
  "latency_ms": 31000,
  "cost": { "amount": 0.11, "currency": "USD" },
  "error": { "code": "rate_limit_exceeded", "message": "429 Too Many Requests" },
  "failure_class": "resource_unavailable",
  "outcome_id": "out_330"
}
```

기계가 읽을 수 있는 스키마: [`execution.schema.json`](../intent-os-spec/schemas/execution.schema.json)

---

## 9. Validation Rules

```
Execution 생성 요청
  ↓
task_id 존재 확인 ── 없으면 반려
  ↓
decision_id 존재 + status ∈ {Committed, Applied} 확인 (EXE-002) ── 아니면 반려
  ↓
Decision.selection == resource_id 일치 확인 ── 불일치 시 반려
  ↓
Policy 사전 검사 (POL) ── 위반 시 차단, Event 발행
  ↓
Hard Constraint 잔여 예산·기한 확인 ── 초과 시 차단
  ↓
동일 Task의 Running Execution 존재 확인 (INV-EXE-03)
  ├── 존재 + mode=single  → 거부
  └── 존재 + mode ∈ {collaborative, shadow} → 허용
  ↓
재시도라면 previous_execution_id 체인 검사 (INV-EXE-05)
  ↓
attempt ≤ Task.retry_policy.max_retries + 1 확인 ── 초과 시 abort 경로로
  ↓
Created 생성 → Event 발행
```

### 9.1 종료 시 검사

```
종료 상태 전이 요청
  ↓
finished_at ≥ started_at 확인 (INV-EXE-04)
  ↓
latency_ms 재계산 및 일치 확인
  ↓
cost ≥ 0 확인 (INV-EXE-06)
  ↓
Outcome 생성 (EXE-005) ── 실패 시에도 최소 Outcome 생성
  ↓
Execution 동결 (이후 쓰기 거부, INV-06)
  ↓
Resource Profile 갱신 신호 발행 → e025
  ↓
Event 발행
```

---

## 10. Examples

### 예시 1 — 정상 실행

```
Task     task_004  인스타그램 광고 카피 3종 작성
Decision dec_101   Claude 선택 (utility 0.91, 예상 지연 800ms, 예상 비용 0.35 USD)
  ↓
exe_220  Created → Queued → Running → Completed
         실측: 1,820ms / 0.42 USD
  ↓
out_331  카피 3종 (art_450)
```

예측(800ms / 0.35)과 실측(1,820ms / 0.42)의 차이는 Prediction Model 보정 신호가 된다([Volume 4-A](../v4a-decision-engine-detail.md)).

### 예시 2 — 실패 후 재시도

```
exe_219  GPT      Failed (rate_limit_exceeded)  0.11 USD
   │ failure_class: resource_unavailable → 재선택
   ▼
exe_220  Claude   Completed                     0.42 USD
```

Task의 총 비용은 **0.53 USD**다. 실패한 시도의 비용도 Goal 예산에서 차감된다.

### 예시 3 — Waiting 상태 (인간 Resource)

```
exe_240  human:copywriter_kim   랜딩페이지 헤드카피 검수
         Created 14:00 → Queued 14:00 → Running 14:02 → Waiting 14:02
         (김 카피라이터 회신 대기)
         → Completed 18:10
         latency_ms: 14,880,000  (4시간 8분)
```

인간 Resource의 지연은 API와 자릿수가 다르다. Utility 계산에서 `latency` 가중치가 낮은 Task에만 후보로 오르는 이유다.

### 예시 4 — Pipeline Execution

```
exe_210  (parent, pipeline)  경쟁 학원 분석 리포트
  ├── exe_211  perplexity        조사        3,200ms  0.08 USD
  ├── exe_212  anthropic:claude-5 분석·작성  2,100ms  0.31 USD
  └── exe_213  human:copywriter_kim 검수     7,200,000ms  50,000 KRW
```

부모 Execution의 `cost`와 `latency_ms`는 자식의 합계이며, 자식이 하나라도 실패하면 부모는 `Failed`가 된다.

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **Resource가 부분 결과만 반환** | `Completed` + Outcome의 `status: partial`. 실패가 아니다. 품질 판정은 Evaluation이 한다 |
| **응답은 왔는데 파싱 불가** | `Failed` / `failure_class: resource_incapable`. 원시 응답은 `logs_ref`에 보존한다 |
| **타임아웃 직후 응답 도착** | Execution은 이미 `TimedOut`으로 종료. 늦게 온 결과는 **버리지 않고** Outcome에 `late_arrival: true`로 기록해 타임아웃 임계값 보정에 쓴다 |
| **사용자가 실행 중 Goal을 취소** | 진행 중 Execution 전부 `Aborted`. 그때까지 발생한 비용을 기록한다. 비용은 사라지지 않는다 |
| **인간 Resource가 응답하지 않음** | `timeout_ms` 도달 시 `TimedOut`. `failure_class: resource_unavailable`이며 해당 인간의 `availability` 보정에 반영 |
| **동일 Task에 Collaborative 3개 실행** | INV-EXE-03의 예외. 3개 모두 정상 Execution이며 각각 Outcome을 낳는다. 채택되지 않은 2개는 `contributes_to_goal: true`이되 Artifact가 채택되지 않을 뿐이다 |
| **Shadow Execution이 본 실행보다 좋은 결과** | Goal에는 반영하지 않는다. 대신 해당 Resource의 `observed_score`를 올려 다음 Decision에서 채택되게 한다 |
| **비용을 측정할 수 없는 Resource** | 정액 계약 인간·사내 도구 등. `cost.amount`를 계약 단가로 안분(按分)하고 `cost.estimated: true`로 표시한다. `null`은 허용하지 않는다 — 비용 0으로 오인되면 Utility가 왜곡된다 |
| **재시도 중 Plan이 바뀜** | 새 Plan의 Task가 다르면 기존 Execution 체인은 `Aborted`로 종료하고 새 Task에서 `attempt: 1`부터 시작한다 |

---

## 12. Open Issues (v1.0)

### 분산 실행의 상태 동기화

Execution이 여러 노드에 걸쳐 수행되면 `status`의 단일 진실 원천이 흔들린다. 현재 명세는 단일 Runtime을 전제한다. 분산 시 INV-EXE-03(Task당 Running 1개)의 보장 방법이 미정이다.

### 스트리밍 실행의 진행률

`progress` 필드는 0~1 실수로 정의했지만, LLM 스트리밍처럼 총량을 모르는 실행에서는 의미 있는 값을 계산할 수 없다. 토큰 기반 추정과 단계 기반 추정 중 무엇을 표준으로 할지 미정이다.

### 비용 안분 규칙

정액 요금제 Resource(월 구독 LLM, 정규직 인력)의 Execution당 비용 안분 공식이 없다. 사용량 비례·시간 비례·균등 배분 중 선택이 필요하며, 이 선택이 Utility 계산을 직접 왜곡한다.

### Volume 3와의 정합

[Volume 3](../v3-runtime.md)의 Runtime State Machine(`IDLE → UNDERSTANDING → … → COMPLETED`)은 Session 수준의 상태다. 본 문서의 Execution 상태와 계층이 다르다는 점을 Volume 3에도 반영해야 한다.

### 앞으로 보강해야 할 항목

- Composite Execution의 부분 실패 정책 (자식 3개 중 1개 실패 시 부모 판정)
- `usage` 필드의 Resource 타입별 표준화 (토큰 / API 호출 / 인시 / GPU 초)
- 실행 취소의 전파 규칙 (부모 취소 시 자식 처리)
- 실제 예시 30~50개
