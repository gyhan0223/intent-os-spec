# Entity 020: Event

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Event is an immutable, timestamped, ordered record of something that has already happened in the system, published for any interested consumer.**

> Event는 시스템에서 **이미 일어난 일**에 대한 불변·시각·순서를 가진 기록이며, 관심 있는 소비자에게 발행된다.

여기서 중요한 단어는 **이미 일어난(Already Happened)** 이다.

Event는 항상 **과거형**이다. `execution.completed`이지 `execution.complete`가 아니다. 이 문법이 Event와 Command를 가르는 유일한 기준이다.

### Intent OS가 Event Driven이어야 하는 이유

```
동기 호출 방식
  Execution 완료 → Evaluation 호출 → Memory 기록 → Resource Profile 갱신 → Budget 차감
  ↑ Execution이 이 모든 것을 알아야 한다

Event Driven 방식
  Execution 완료 → execution.completed 발행
                        ↓ ↓ ↓ ↓
        Evaluation / Memory / Resource Profile / Budget 이 각자 구독
  ↑ Execution은 아무것도 모른다
```

새 소비자(예: Assumption 검증기)를 추가할 때 **기존 코드를 건드리지 않는다.** 27개 Entity가 서로를 직접 호출하면 결합도가 폭발한다.

---

## 2. Event는 무엇이 아닌가?

### Event는 Log가 아니다

❌ `[09:30:00] INFO POST /v1/messages 200 OK` — 이건 로그다.

| | Log | Event |
|---|---|---|
| 목적 | 사람이 디버깅한다 | 시스템이 반응한다 |
| 구조 | 자유 형식 문자열 | 스키마를 갖는 구조체 |
| 소비자 | 개발자 | 구독자(Subscriber) |
| 유실 | 허용됨 | 허용되지 않음 (INV-12) |
| 재생 | 불가 | 가능 (Event Sourcing) |

로그는 Execution의 `logs_ref`로 참조된다. Event는 독립 Entity다.

### Event는 Command가 아니다

❌ `execution.start` — 이건 명령이다.

**Event는 명령하지 않는다.** `execution.started`를 발행할 뿐이고, 그것을 보고 무엇을 할지는 구독자가 결정한다. 발행자는 구독자가 누구인지 몰라야 한다.

```
❌  execution.completed → "Evaluation을 실행하라"
✅  execution.completed → (Evaluation 모듈이 스스로 구독하고 반응)
```

### Event는 Feedback이 아니다

❌ `사용자가 별점 2개를 줌` — 이건 [Feedback](e012-feedback.md)이다.

Feedback은 **외부에서 들어오는 평가 신호**이고, Event는 **시스템 내부에서 발생한 사실**이다. 다만 Feedback이 도착하면 `feedback.received` Event가 발생한다. **Feedback은 내용이고 Event는 그 도착 사실이다.**

### Event는 State가 아니다

❌ `execution.status = "Running"` — 이건 상태다.

Event는 상태의 **변화**를 기록한다. 상태는 현재값이고, Event는 그 값이 어떻게 거기에 도달했는지의 이력이다. Event 전체를 재생하면 상태를 재구성할 수 있다(Rule EVT-006).

### Event는 알림(Notification)이 아니다

❌ `대표님께 슬랙 메시지 발송`

알림은 Event의 **소비 결과**다. 하나의 Event가 알림을 0개 만들 수도, 3개 만들 수도 있다. Event 자체는 누구에게 알릴지 모른다.

---

## 3. Design Principles

### Rule EVT-001 — Event는 과거형이다

`<entity>.<past_tense_verb>` 형식을 강제한다.

- ✅ `execution.completed`, `assumption.invalidated`, `goal.achieved`
- ❌ `execution.complete`, `assumption.invalidate`, `goal.achieve`

미래형·명령형 이름이 나오면 그것은 Command를 Event로 위장한 것이다.

### Rule EVT-002 — Event는 불변이다

발행 후 수정하지 않는다([INV-06](e000a-entity-relationships.md)). 잘못 발행했으면 **보정 Event**를 발행한다(`*.corrected`).

### Rule EVT-003 — 주체(subject)를 반드시 참조한다

무엇에 대한 Event인지 없으면 소비자가 아무것도 할 수 없다. `subject`는 `{ entity_type, entity_id }`다.

### Rule EVT-004 — 순서를 보장한다

같은 `subject`에 대한 Event는 **발생 순서대로** 소비되어야 한다. `sequence` 번호를 갖는다.

```
exe_220  seq 1  execution.queued
exe_220  seq 2  execution.started
exe_220  seq 3  execution.completed
```

`execution.completed`가 `execution.started`보다 먼저 소비되면 상태 재구성이 무너진다.

### Rule EVT-005 — 최소 정보만 담는다

Event에 Entity 전체를 복사해 넣지 않는다. `subject` 참조와 **변화에 관한 최소 데이터**만 담는다.

- ✅ `{ "from": "Running", "to": "Completed", "latency_ms": 1820 }`
- ❌ Execution 객체 전체 인라인

Event는 대량 발생한다. 크기가 곧 비용이다.

### Rule EVT-006 — Event로 상태를 재구성할 수 있어야 한다

특정 시점의 Entity 상태를 Event 재생만으로 복원할 수 있어야 한다. 상태 전이 Event가 하나라도 빠지면 이 성질이 깨진다([INV-12](e000a-entity-relationships.md)).

### Rule EVT-007 — 발행자는 구독자를 모른다

Event에 수신자 필드를 두지 않는다. 수신자를 알아야 하는 것은 알림이지 Event가 아니다.

### Rule EVT-008 — 소비는 멱등해야 한다

Event가 두 번 배달될 수 있다(At-least-once). 구독자는 같은 Event를 두 번 처리해도 같은 결과가 나오도록 구현해야 한다. `event_id`가 멱등 키다.

---

## 4. Attributes

```
Event
├── Identity
│   ├── event_id
│   ├── type
│   └── sequence
├── Subject
│   ├── entity_type
│   └── entity_id
├── Context
│   ├── session_id
│   ├── goal_id
│   └── correlation_id
├── Payload
│   ├── data
│   └── previous_state / new_state
├── Origin
│   ├── emitted_by
│   └── emitted_at
└── Delivery
    ├── severity
    └── schema_version
```

| 속성 | 의미 | 예 |
|---|---|---|
| **event_id** | 식별자 (멱등 키) | `evt_9f21a` |
| **type** | Event 유형 (§4.2) | `execution.completed` |
| **sequence** | subject 내 순번 | `3` |
| **entity_type** | 주체의 종류 | `Execution` |
| **entity_id** | 주체의 식별자 | `exe_220` |
| **session_id** | 소속 Session | `ses_057` |
| **goal_id** | 관련 Goal (추적용) | `goal_001` |
| **correlation_id** | 인과 사슬 추적 ID | `corr_a71` |
| **data** | 변화 관련 최소 데이터 | `{ "latency_ms": 1820 }` |
| **previous_state** | 이전 상태 | `Running` |
| **new_state** | 새 상태 | `Completed` |
| **emitted_by** | 발행 주체 | `runtime_engine` |
| **emitted_at** | 발생 시각 | `2026-08-04T09:30:01.820Z` |
| **severity** | 중요도 | `info` / `warning` / `critical` |
| **schema_version** | 페이로드 스키마 버전 | `1.0` |

### 4.1 Event Categories

```
Event
├── lifecycle    Entity의 상태 전이
├── threshold    지표가 임계값에 도달
├── governance   Policy / Constraint / Assumption / Risk 관련
├── external     외부 시스템·사용자로부터의 사실
└── system       Intent OS 자체의 운영 사건
```

### 4.2 Event Catalog

**lifecycle** — 모든 Entity의 상태 전이가 여기 속한다([INV-12](e000a-entity-relationships.md)).

| type | 발행 시점 | 주요 구독자 |
|---|---|---|
| `goal.created` | Goal 생성 | Planner |
| `goal.achieved` | Goal 완료 | Memory, 알림 |
| `plan.activated` | Plan이 Active로 | Runtime |
| `plan.superseded` | 새 버전으로 교체 | Runtime, Task Graph |
| `task.assigned` | Resource 배정 | Runtime |
| `decision.committed` | 결정 확정 | Execution |
| `execution.queued` | 대기열 등록 | 스케줄러 |
| `execution.started` | 실행 시작 | 모니터링 |
| `execution.completed` | 정상 종료 | Outcome, Resource Profile |
| `execution.failed` | 실패 종료 | 재시도 관리자, Resource Profile |
| `outcome.produced` | Outcome 생성 | Evaluation, Budget |
| `evaluation.completed` | 평가 확정 | Memory, Task 상태 전이 |
| `artifact.produced` | 산출물 생성 | Policy(PII 스캔) |
| `artifact.published` | 외부 전달 | 감사 |

**threshold** — 지표 기반. 조기 경보의 핵심이다.

| type | 발행 조건 | 주요 구독자 |
|---|---|---|
| `budget.exceeded` | 예산 소진율이 임계 초과 | Plan, Risk |
| `budget.warning` | 예산 소진율 경고 수준 | Risk |
| `latency.degraded` | Resource 응답이 기준 초과 | Resource Profile |
| `quality.degraded` | 평가 점수가 기준 미달 | Decision Engine |
| `goal.progress_stalled` | 지표가 N일간 변화 없음 | Planner, Risk |

**governance** — 규칙·가정·위험 관련.

| type | 발행 조건 | 주요 구독자 |
|---|---|---|
| `policy.violated` | Policy 위반 | 감사, 알림 |
| `policy.exception_used` | 예외 사용 | 감사 |
| `constraint.violated` | Constraint 위반 | Runtime |
| `assumption.at_risk` | 조기 경보 도달 | Risk, owner |
| `assumption.invalidated` | 가정 무효화 | Planner (Replanning) |
| `risk.materialized` | 위험 현실화 | Plan, owner |
| `approval.requested` | 인간 승인 요청 | 알림 |
| `approval.granted` / `approval.denied` | 승인 결과 | Execution |

**external** — 시스템 밖에서 온 사실.

| type | 발행 조건 |
|---|---|
| `feedback.received` | 사용자 Feedback 도착 |
| `resource.registered` | 새 Resource 등록 |
| `resource.updated` | Resource 버전 변경 |
| `resource.drift_detected` | 성능 변화 감지 |
| `session.started` / `session.ended` | Session 경계 |

**system** — 운영 사건.

| type | 발행 조건 |
|---|---|
| `invariant.violated` | 불변식 위반 탐지 |
| `event.correction_issued` | 보정 Event 발행 |
| `sweep.completed` | 주기 감사 완료 |

---

## 5. Invariants

### INV-EVT-01 — Event는 불변이다

| | |
|---|---|
| **위반 시** | 저장 계층이 쓰기 거부. 정정은 보정 Event로만 |

### INV-EVT-02 — 같은 subject의 sequence는 빈틈 없이 증가한다

| | |
|---|---|
| **위반 시** | 빈 번호가 발견되면 Event 유실이다. `invariant.violated` 발행 + 상태 재구성 불가 표시 |
| **탐지** | 소비 시점 + 주기 스윕 |

### INV-EVT-03 — 모든 상태 전이는 정확히 하나의 Event를 발생시킨다

전역 불변식 [INV-12](e000a-entity-relationships.md)의 Event 측 표현이다.

| | |
|---|---|
| **위반 시** | 중복 발행이면 멱등 처리로 흡수. 누락이면 상태 재구성 불가 → 정합성 경보 |

### INV-EVT-04 — emitted_at은 되돌아가지 않는다

같은 subject의 Event 시각은 sequence 순서와 일치해야 한다.

| | |
|---|---|
| **위반 시** | 시계 동기화 문제. 해당 Event를 격리하고 논리 시계(sequence)를 우선 신뢰한다 |

### INV-EVT-05 — Event는 명령을 담지 않는다

`data`에 수신자 지정, 실행 지시, 콜백 URL이 들어가면 안 된다.

| | |
|---|---|
| **위반 시** | 스키마 검증에서 거부. 결합도가 복원되어 Event Driven의 이점이 사라진다 |

### INV-EVT-06 — 보존 기간 내에는 삭제되지 않는다

| | |
|---|---|
| **위반 시** | Event Sourcing으로 복원 가능한 기간이 줄어든다. 삭제 차단 |

---

## 6. Lifecycle

Event 자체는 상태가 거의 없다. **배달(Delivery)의 상태**가 있을 뿐이다.

```
Emitted → Published → Consumed ──▶ Archived
              │
              └──▶ DeadLettered ──▶ Replayed
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Emitted** | 발행자가 생성 | 상태 전이 발생 |
| **Published** | Event Bus에 등록. 구독자에게 배달 중 | 저장 커밋 |
| **Consumed** | 모든 구독자가 처리 완료 | 구독자 ACK |
| **DeadLettered** | 반복 실패로 격리 | 재시도 한도 초과 |
| **Replayed** | 재처리됨 | 수동 또는 자동 복구 |
| **Archived** | 활성 조회 대상에서 제외 | 보존 정책 |

### 6.1 배달 보장

Intent OS는 **At-least-once**를 채택한다.

| 방식 | 특징 | 채택 |
|---|---|---|
| At-most-once | 유실 가능 | ❌ INV-12 위반 |
| **At-least-once** | 중복 가능. 멱등 처리 필요 | ✅ |
| Exactly-once | 이상적이나 분산 환경에서 비용이 크다 | 향후 검토 |

중복은 `event_id` 멱등 키로 소비자가 흡수한다(Rule EVT-008). **유실보다 중복이 낫다.**

---

## 7. Relationships

```
모든 Entity ──1:0..N──▶ Event 020 ──발행──▶ Event Bus ──▶ 구독자
                            │
                            ├──재생──▶ 상태 재구성
                            ├──집계──▶ Memory 010 (패턴 추출)
                            └──감사──▶ Policy 019 (위반 이력)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| 모든 Entity | 상태 전이마다 Event를 발생 | `* 1:0..N Event` |
| [Session](e021-session.md) | Event는 Session 컨텍스트를 갖는다 | `Session 1:0..N Event` |
| [Assumption](e017-assumption.md) | `assumption.invalidated`가 Replanning을 유발 | `Assumption 1:0..N Event` |
| [Risk](e018-risk.md) | `risk.materialized`, threshold Event를 소비 | `Risk N:M Event` |
| [Policy](e019-policy.md) | `policy.violated` 발행, 감사 소비 | `Policy 1:0..N Event` |
| [Memory](e010-memory.md) | Event 흐름에서 패턴을 추출 | `Event N:M Memory` |
| [Workflow](e022-workflow.md) | Event로 다음 단계를 트리거 | `Event N:M Workflow` |

---

## 8. Canonical Representation

```json
{
  "event_id": "evt_9f21a",
  "type": "execution.completed",
  "sequence": 3,
  "subject": { "entity_type": "Execution", "entity_id": "exe_220" },
  "session_id": "ses_057",
  "goal_id": "goal_001",
  "correlation_id": "corr_a71",
  "previous_state": "Running",
  "new_state": "Completed",
  "data": {
    "resource_id": "anthropic:claude-5",
    "latency_ms": 1820,
    "cost": { "amount": 0.42, "currency": "USD" }
  },
  "emitted_by": "runtime_engine",
  "emitted_at": "2026-08-04T09:30:01.820Z",
  "severity": "info",
  "schema_version": "1.0"
}
```

거버넌스 Event는 다음과 같다.

```json
{
  "event_id": "evt_c04d8",
  "type": "assumption.invalidated",
  "sequence": 4,
  "subject": { "entity_type": "Assumption", "entity_id": "asm_012" },
  "goal_id": "goal_001",
  "correlation_id": "corr_b12",
  "previous_state": "AtRisk",
  "new_state": "Invalidated",
  "data": {
    "criteria": "월 집행 가능액 < 3000000 KRW",
    "observed": 2000000,
    "dependents": ["plan_014", "task_006"],
    "on_invalidation": "replan"
  },
  "emitted_by": "assumption_validator",
  "emitted_at": "2026-08-15T10:12:00Z",
  "severity": "critical",
  "schema_version": "1.0"
}
```

기계가 읽을 수 있는 스키마: [`event.schema.json`](../intent-os-spec/schemas/event.schema.json)

---

## 9. Validation Rules

```
Event 발행 요청
  ↓
type 형식 검사 (EVT-001) — <entity>.<past_tense>
  ── 미래형/명령형 어미 검출 시 거부
  ↓
type이 Event Catalog(§4.2)에 등록되어 있는가
  ── 미등록 → 거부 (임의 Event 타입 금지)
  ↓
subject 존재 확인 (EVT-003) ── 없으면 거부
  ↓
sequence 할당 (subject별 단조 증가, INV-EVT-02)
  ↓
data 크기 검사 (EVT-005) ── 임계 초과 시 경고 + 참조로 전환 권고
  ↓
명령성 필드 검출 (INV-EVT-05)
  recipient / callback_url / action / execute 등 → 거부
  ↓
emitted_at 검사 (INV-EVT-04) ── 직전 Event보다 이르면 격리
  ↓
저장 + Published → Event Bus 발행
  ↓
구독자 배달 (At-least-once)
  ├── ACK 수신 → Consumed
  └── 재시도 한도 초과 → DeadLettered + 알림
```

### 9.1 상태 재구성 알고리즘 (Event Sourcing)

```
목표: 특정 시점 T의 Entity E 상태 복원
  ↓
E의 모든 Event를 sequence 오름차순으로 조회 (emitted_at ≤ T)
  ↓
sequence 연속성 검사 (INV-EVT-02)
  ├── 빈틈 있음 → 복원 불가. 정합성 경보 발행 후 스냅샷 폴백
  └── 연속      → 계속
  ↓
초기 상태에서 시작해 Event를 순서대로 적용
  ↓
복원된 상태 반환
```

**빈틈이 있으면 복원을 시도하지 않는다.** 부분 복원은 잘못된 상태보다 위험하다.

### 9.2 인과 사슬 추적 (correlation_id)

하나의 원인에서 파생된 Event들을 묶는다.

```
corr_b12
├── assumption.invalidated  (asm_012)
├── risk.materialized       (rsk_007)
├── plan.suspended          (plan_014)
├── approval.requested      (대표에게 Replanning 승인)
└── plan.activated          (plan_015)
```

"9월에 계획이 왜 바뀌었는가"를 한 번의 질의로 답할 수 있다.

---

## 10. Examples

### 예시 1 — 하나의 Execution이 발생시키는 Event 열

```
exe_220
  seq 1  execution.queued     09:29:58
  seq 2  execution.started    09:30:00
  seq 3  execution.completed  09:30:01.820
```

`execution.completed` 하나에 4개 모듈이 반응한다.

```
execution.completed
├── Outcome 생성기        → outcome.produced (out_331)
├── Resource Profile 갱신 → Claude의 latency 관측값 추가
├── Budget 차감기         → 0.42 USD 차감, 소진율 재계산
└── Session 집계기        → ses_057의 누적 비용 갱신
```

Execution은 이 4개를 **하나도 모른다.**

### 예시 2 — 임계값 Event가 연쇄를 시작

```
budget.warning (소진율 62%)
  ↓ 구독: Assumption 검증기
assumption.at_risk (asm_012)
  ↓ 구독: 알림
approval.requested (대표에게 예산 확인)
  ↓ 대표 응답: "9월부터 200만원"
assumption.invalidated (asm_012)
  ↓ 구독: Risk 관리자, Planner
risk.materialized (rsk_007)
plan.suspended (plan_014)
  ↓
plan.activated (plan_015)
```

전부 `correlation_id: corr_b12`로 묶인다. **6개 모듈이 관여했지만 서로를 호출한 곳은 한 군데도 없다.**

### 예시 3 — 보정 Event

```
evt_a11  execution.completed  { latency_ms: 1820, cost: 0.42 }
   │ 3일 뒤 실제 청구액 확정
   ▼
evt_d77  event.correction_issued
         { corrects: "evt_a11", field: "cost", from: 0.42, to: 0.47 }
```

`evt_a11`은 수정되지 않는다(INV-EVT-01). 보정 Event가 추가될 뿐이다. 상태 재구성 시 두 Event를 순서대로 적용하면 최종값이 나온다.

### 예시 4 — DeadLetter

```
evt_e33  outcome.produced (out_402)
  ↓ 구독자: Budget 차감기
  ├── 시도 1  실패 (DB 연결 오류)
  ├── 시도 2  실패
  ├── 시도 3  실패
  └── DeadLettered + 알림
```

**예산이 차감되지 않은 상태다.** DeadLetter는 조용히 넘어가면 안 되는 사건이며, 운영자가 원인을 고친 뒤 `Replayed`한다. 멱등 처리(Rule EVT-008) 덕분에 재생이 안전하다.

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **같은 Event가 두 번 배달됨** | 정상이다(At-least-once). 구독자가 `event_id`로 멱등 처리한다. 발행 측에서 중복을 없애려고 exactly-once를 시도하면 지연과 복잡도가 커진다 |
| **구독자가 없는 Event** | 정상이다. 발행자는 구독자를 모른다(EVT-007). 소비되지 않아도 저장되고, 나중에 추가된 구독자가 재생할 수 있다 |
| **Event 순서가 뒤바뀌어 도착** | `sequence`로 재정렬한다. 소비자는 순서 버퍼를 갖고, 빈틈이 임계 시간 이상 채워지지 않으면 정합성 경보를 발행한다 |
| **Event 폭주 (초당 수만 건)** | `severity: info`인 lifecycle Event를 샘플링하지 않는다. 대신 배치 발행과 파티셔닝을 쓴다. **샘플링은 INV-12를 깨뜨린다** |
| **Event 페이로드가 너무 큼** | `data`를 참조로 전환한다(`artifact_id`, `blob://`). Event는 포인터이지 컨테이너가 아니다 |
| **잘못된 Event를 발행함** | 삭제하지 않는다. `*.corrected` 보정 Event를 발행한다(예시 3) |
| **상태 전이 없이 중요한 일이 일어남** | threshold·external 카테고리를 쓴다. 모든 Event가 상태 전이일 필요는 없지만, 모든 상태 전이는 Event여야 한다(비대칭) |
| **Session이 끝난 뒤 도착한 Event** | 정상 저장한다. Event는 Session에 종속되지 않는다([INV-16](e000a-entity-relationships.md)). 늦게 온 인간 Resource의 회신이 대표적이다 |
| **보존 기간이 지난 Event로 재구성 시도** | 복원 불가를 명확히 반환한다. 이를 대비해 주기적 스냅샷을 저장한다(§9.1 폴백) |

---

## 12. Open Issues (v1.0)

### 스냅샷 전략

Event 재생만으로 상태를 복원하면 Event가 쌓일수록 느려진다. 주기적 스냅샷이 필요하지만 주기·저장 위치·스냅샷과 Event의 정합 검증 방법이 미정이다.

### Event 스키마 진화

`schema_version`을 두었으나 버전이 올라갈 때 옛 Event를 어떻게 읽을지(업캐스팅) 규칙이 없다. Event는 영구 보존되므로 v1 페이로드를 5년 뒤에도 해석할 수 있어야 한다.

### 순서 보장의 범위

현재 `subject` 단위 순서만 보장한다. 그러나 `assumption.invalidated → plan.suspended`처럼 **다른 subject 간의 인과 순서**도 지켜져야 하는 경우가 있다. `correlation_id` 내 순서 보장이 필요한지 검토가 필요하다.

### Event Bus의 명세

발행·구독·재시도·DeadLetter는 개념으로만 서술했고 인터페이스 명세가 없다. [Volume 6](../v6-developer-platform.md)에서 외부 시스템이 Event를 구독하는 방법과 함께 정의해야 한다.

### 앞으로 보강해야 할 항목

- Event Catalog의 완전한 열거 (현재는 주요 항목만)
- `data` 페이로드의 type별 스키마
- 보존 기간의 카테고리별 차등 (governance는 길게, lifecycle info는 짧게)
- 실제 예시 30~50개
