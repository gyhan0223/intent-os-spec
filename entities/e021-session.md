# Entity 021: Session

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Session is a bounded unit of interaction and execution in which one or more Goals are pursued, holding transient context and a resource budget, while only referencing the durable entities it touches.**

> Session은 하나 이상의 Goal을 추진하는 **경계 지어진 상호작용·실행 단위**이며, 일시적 Context와 자원 예산을 보유하되 자신이 건드린 영속 Entity는 **참조만** 한다.

여기서 중요한 단어는 **참조만(Only Referencing)** 이다.

Session이 끝나면 대화 버퍼와 일시적 Context는 사라진다. 그러나 **Goal, Memory, Knowledge, Artifact, Outcome은 살아남는다**([INV-16](e000a-entity-relationships.md)).

```
Session 종료
├── 사라지는 것   대화 버퍼 · 임시 Context · 실행 큐 상태
└── 남는 것       Goal · Plan · Execution · Outcome · Artifact · Memory · Knowledge · Event
```

> **Intent OS의 기억은 대화보다 오래 산다.**

이것이 챗봇과 운영체제를 가르는 지점이다. 챗봇은 대화가 끝나면 아무것도 남지 않는다.

---

## 2. Session은 무엇이 아닌가?

### Session은 Goal이 아니다

❌ `윈터캠프 100명 모집` — 이건 [Goal](e001-goal.md)이다.

Goal은 Session보다 오래 산다. 하나의 Goal이 여러 Session에 걸쳐 추진되고, 하나의 Session이 여러 Goal을 다룰 수도 있다.

```
goal_001 (윈터캠프 100명 모집, 8월 ~ 12월)
├── ses_057  8/4  계획 수립
├── ses_061  8/5  카피 검토
├── ses_090  8/15 예산 삭감 대응 (Replanning)
└── ses_210  12/1 성과 리뷰
```

### Session은 Execution이 아니다

❌ `Claude로 카피를 1.82초 동안 생성` — 이건 [Execution](e013-execution.md)이다.

`Session 1 : Execution 0..N` 이다.

> **v0.1 명세 정정:** [Volume 3 §3](../v3-runtime.md)의 "Execution Instance"(Goal 하나가 처리되는 전체 단위)는 실제로는 **Session**이다. 이름이 Execution과 겹쳐 계층 혼동을 낳았으므로 v1.0에서 분리했다. Volume 3의 Runtime State Machine(`IDLE → UNDERSTANDING → … → COMPLETED`)도 Session 수준의 상태다.

### Session은 대화(Conversation)가 아니다

❌ `사용자와 주고받은 메시지 목록`

대화는 Session의 **일부**일 뿐이다. Session에는 대화가 전혀 없을 수도 있다 — 스케줄러가 매주 월요일에 자동으로 여는 Session(§4.1 `autonomous`)이 그렇다.

### Session은 User가 아니다

❌ `대표의 계정`

User는 Session의 `actor`다. 한 User가 여러 Session을 열고, 하나의 Session에 여러 actor가 참여할 수도 있다(대표 + 상담 실장).

### Session은 Transaction이 아니다

❌ `실패하면 전부 롤백되는 단위`

Session은 롤백되지 않는다. Session 중간에 실행된 광고는 Session이 실패해도 집행된 상태로 남는다. **Session은 원자성을 보장하지 않는다.** 이 점을 오해하면 비가역 작업의 위험을 과소평가하게 된다.

---

## 3. Design Principles

### Rule SES-001 — Session은 Entity를 소유하지 않는다

Session 종료가 Entity 삭제를 유발할 수 없다([INV-16](e000a-entity-relationships.md)). Session이 가진 것은 **참조 목록과 일시적 상태뿐**이다.

### Rule SES-002 — Session은 명확한 경계를 가진다

시작과 종료가 정의되어야 한다. 종료 조건이 없는 Session은 자원을 무한히 점유한다.

| 종료 조건 | 예 |
|---|---|
| 명시적 종료 | 사용자가 닫음 |
| 유휴 만료 | 30분간 활동 없음 |
| 목표 달성 | 대상 Goal이 `Achieved` |
| 예산 소진 | Session 예산 초과 |
| 절대 만료 | 생성 후 24시간 |

### Rule SES-003 — Session은 예산과 Policy 범위를 가진다

Session은 **자원 통제의 단위**다. 폭주하는 자동 Session이 조직의 예산을 태우는 것을 막는 마지막 방어선이다.

```
session.budget = { max_cost_krw: 50000, max_executions: 200, max_duration: "PT4H" }
```

### Rule SES-004 — 종료 시 요약을 남긴다

Session이 끝나면 무엇을 했는지 요약이 [Memory](e010-memory.md)로 넘어간다. 요약 없이 끝나는 Session은 학습에 기여하지 못한다.

### Rule SES-005 — Session은 재개 가능하다

`Suspended` 상태에서 다시 열 수 있다. 단 재개 시 Context는 **다시 수집한다**. 3일 전의 Context를 그대로 쓰면 낡은 정보로 판단하게 된다([Context Freshness](e003-context.md)).

### Rule SES-006 — actor를 명시한다

누가 이 Session의 주체인가. 인간·스케줄러·Event·다른 Agent 중 하나다. actor가 없으면 승인 요청을 보낼 곳이 없다.

### Rule SES-007 — 중첩되지 않는다

Session 안에 Session을 만들지 않는다. 하위 작업이 필요하면 [Agent](e023-agent.md)를 쓴다. 중첩 Session은 예산 회계를 불가능하게 만든다.

### Rule SES-008 — 비가역 작업은 Session 경계와 무관하다

Session이 실패하거나 만료되어도 이미 발행된 [Artifact](e016-artifact.md)와 집행된 광고는 되돌아가지 않는다. Session 종료를 "취소"로 취급하면 안 된다.

---

## 4. Attributes

```
Session
├── Identity
│   ├── session_id
│   ├── type
│   └── actor
├── Scope
│   ├── goal_ids[]
│   ├── policy_scope[]
│   └── context_ref
├── Budget
│   ├── max_cost
│   ├── max_executions
│   ├── max_duration
│   └── consumed
├── Timing
│   ├── started_at
│   ├── last_activity_at
│   ├── ended_at
│   ├── idle_timeout
│   └── absolute_timeout
├── References
│   ├── execution_ids[]
│   ├── decision_ids[]
│   └── artifact_ids[]
├── Result
│   ├── summary
│   └── memory_ids[]
└── Status
    ├── status
    └── end_reason
```

| 속성 | 의미 | 예 |
|---|---|---|
| **session_id** | 식별자 | `ses_057` |
| **type** | 분류 (§4.1) | `interactive` |
| **actor** | 주체 | `human:대표` |
| **goal_ids** | 다루는 Goal | `["goal_001"]` |
| **policy_scope** | 적용 Policy 집합 | `["pol_007", "pol_012", "pol_015"]` |
| **context_ref** | 일시적 Context | `ctx_ses_057` |
| **max_cost** | 예산 상한 | `{ "amount": 50000, "currency": "KRW" }` |
| **max_executions** | 실행 횟수 상한 | `200` |
| **max_duration** | 최대 지속 | `PT4H` |
| **consumed** | 소비 현황 | `{ "cost": 12400, "executions": 31 }` |
| **idle_timeout** | 유휴 만료 | `PT30M` |
| **absolute_timeout** | 절대 만료 | `PT24H` |
| **execution_ids** | 이 Session에서 실행된 것 | `["exe_219", "exe_220", …]` |
| **summary** | 종료 요약 (SES-004) | `윈터캠프 Plan 수립, 카피 3종 확정` |
| **memory_ids** | 생성된 Memory | `["mem_770"]` |
| **status** | 상태 (§6) | `Active` |
| **phase** | Runtime 진행 단계 ([Volume 3 §5](../v3-runtime.md)) | `PLANNING` |
| **end_reason** | 종료 사유 | `null` |

### 4.1 Session Types

```
Session
├── interactive   사람이 대화하며 진행
├── autonomous    스케줄에 의해 자동 실행
├── triggered     Event에 의해 시작
├── batch         다수 Goal의 일괄 처리
└── replay        과거 Event를 재생하는 분석용
```

| Type | actor | 예 | 특징 |
|---|---|---|---|
| `interactive` | 인간 | 대표가 "윈터캠프 모집 계획 짜줘" | 승인 요청 즉시 가능 |
| `autonomous` | 스케줄러 | 매주 월요일 09:00 모집 현황 리포트 | 승인 필요 시 대기하거나 보류 |
| `triggered` | Event | `assumption.invalidated` → Replanning | 원인 Event를 `trigger_ref`로 보존 |
| `batch` | 스케줄러 | 12월 종료 Goal 20건 일괄 성과 분석 | 예산 상한이 특히 중요 |
| `replay` | 운영자 | 8월 결정을 새 Policy로 재판정 | **부수효과 금지.** 실행하지 않는다 |

**`autonomous`가 가장 위험하다.** 사람이 보고 있지 않은 상태에서 비용이 발생한다. `max_cost`와 `require_approval` Policy가 실질적 안전장치다.

**`replay`는 특별하다.** Execution을 만들지 않고 Decision 재판정만 수행한다. `dry_run: true`가 강제된다.

---

## 5. Invariants

### INV-SES-01 — Session은 Entity를 소유하지 않는다

전역 불변식 [INV-16](e000a-entity-relationships.md)의 Session 측 표현이다.

| | |
|---|---|
| **위반 시** | Session 종료 시의 Entity 삭제 요청을 차단한다 |

### INV-SES-02 — 예산을 초과하면 새 Execution을 시작할 수 없다

| | |
|---|---|
| **위반 시** | Execution 생성을 거부하고 Session을 `Suspended`로 전이. 진행 중인 것은 완료시킨다 |
| **근거** | 중단이 더 큰 손해인 경우가 있다. 새 지출만 막는다 |

### INV-SES-03 — 종료된 Session에는 새 Execution이 붙지 않는다

| | |
|---|---|
| **위반 시** | 생성 거부. 늦게 도착한 결과는 기존 Execution의 Outcome으로 처리한다 |

### INV-SES-04 — Session은 중첩되지 않는다

| | |
|---|---|
| **위반 시** | 하위 Session 생성을 거부하고 Agent 생성을 제안한다 (Rule SES-007) |

### INV-SES-05 — replay Session은 부수효과를 만들지 않는다

Execution 생성, Artifact 발행, 외부 호출, Budget 차감이 전부 금지된다.

| | |
|---|---|
| **위반 시** | 즉시 중단. 실제 광고가 재집행되는 사고를 막는 규칙이다 |

### INV-SES-06 — 종료된 Session은 summary를 가진다

| | |
|---|---|
| **위반 시** | 자동 요약을 생성한다. 요약 없는 종료는 학습 손실이다 (Rule SES-004) |

### INV-SES-07 — consumed는 감소하지 않는다

| | |
|---|---|
| **위반 시** | 예산 회계 오류. 정합성 경보 발행 후 Execution 이력에서 재계산 |

---

## 6. Lifecycle

```
Created → Active ──▶ Idle ──▶ Completed
             │   ▲     │
             │   └─────┘
             ▼
         Suspended ──▶ Active
             │
             └──▶ Expired / Aborted
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Created** | 생성됨. 아직 활동 없음 | Session 요청 |
| **Active** | 진행 중 | 첫 활동 발생 |
| **Idle** | 유휴. 아직 만료 전 | `idle_timeout`의 절반 경과 |
| **Suspended** | 일시 중지. 재개 가능 | 예산 초과, 승인 대기, 사용자 보류 |
| **Completed** | 정상 종료 | 목표 달성 또는 명시적 종료 |
| **Expired** | 만료 종료 | `idle_timeout` 또는 `absolute_timeout` 도달 |
| **Aborted** | 강제 종료 | Policy 위반, 운영자 중단 |

### 6.1 종료 절차

어떤 경로로 끝나든 동일한 절차를 밟는다.

```
종료 트리거
  ↓
① 진행 중 Execution 처리
   ├── 완료 임박(진행률 > 0.8) → 완료 대기
   └── 그 외                    → Aborted 전이 (비용 기록, e013 Rule EXE-008)
  ↓
② 미결 승인 요청 처리
   └── 만료 또는 취소로 표시
  ↓
③ consumed 최종 정산
  ↓
④ summary 생성 (INV-SES-06)
   무엇을 했는가 / 무엇이 남았는가 / 어떤 Goal이 진전했는가
  ↓
⑤ Memory 기록 (SES-004) → e010
  ↓
⑥ 일시적 Context 폐기 (context_ref)
   ⚠️ 참조된 Entity는 건드리지 않는다 (INV-SES-01)
  ↓
⑦ Event 발행 (session.ended)
  ↓
Completed / Expired / Aborted
```

**⑥이 이 Entity의 핵심이다.** 지우는 것은 Context뿐이다.

---

## 7. Relationships

```
Session 021 ──참조──▶ Goal 001        (소유하지 않는다)
     │
     ├──1:0..N──▶ Execution 013
     ├──1:0..N──▶ Decision 009
     ├──1:0..N──▶ Event 020
     ├──1:0..1──▶ Context 003      (일시적. Session과 함께 소멸)
     ├──N:M─────▶ Policy 019       (적용 범위)
     └──1:0..N──▶ Memory 010       (종료 요약)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Goal](e001-goal.md) | **참조만 한다.** Goal이 Session보다 오래 산다 | `Session N:M Goal` |
| [Execution](e013-execution.md) | Session 안에서 실행된다 | `Session 1:0..N Execution` |
| [Decision](e009-decision.md) | Session 안에서 내려진다 | `Session 1:0..N Decision` |
| [Context](e003-context.md) | 일시적 Context를 보유. **함께 소멸한다** | `Session 1:0..1 Context` |
| [Policy](e019-policy.md) | Session 범위의 Policy 집합 | `Policy N:M Session` |
| [Memory](e010-memory.md) | 종료 요약이 Memory가 된다 | `Session 1:0..N Memory` |
| [Artifact](e016-artifact.md) | Session보다 오래 산다 | `Session 1:0..N Artifact` (참조) |
| [Agent](e023-agent.md) | Session 안에서 Agent가 활동한다 | `Session 1:0..N Agent` |
| [Event](e020-event.md) | Event의 컨텍스트 | `Session 1:0..N Event` |

---

## 8. Canonical Representation

```json
{
  "session_id": "ses_057",
  "type": "interactive",
  "actor": "human:대표",
  "goal_ids": ["goal_001"],
  "policy_scope": ["pol_007", "pol_012", "pol_015"],
  "context_ref": "ctx_ses_057",
  "budget": {
    "max_cost": { "amount": 50000, "currency": "KRW" },
    "max_executions": 200,
    "max_duration": "PT4H"
  },
  "consumed": {
    "cost": { "amount": 12400, "currency": "KRW" },
    "executions": 31,
    "duration": "PT1H12M"
  },
  "started_at": "2026-08-04T09:00:00Z",
  "last_activity_at": "2026-08-04T10:12:00Z",
  "ended_at": null,
  "idle_timeout": "PT30M",
  "absolute_timeout": "PT24H",
  "execution_ids": ["exe_219", "exe_220", "exe_240"],
  "decision_ids": ["dec_100", "dec_101"],
  "artifact_ids": ["art_450", "art_463"],
  "summary": null,
  "memory_ids": [],
  "status": "Active",
  "end_reason": null
}
```

자동 Session은 다음과 같다.

```json
{
  "session_id": "ses_180",
  "type": "autonomous",
  "actor": "scheduler:weekly_report",
  "goal_ids": ["goal_001"],
  "trigger_ref": { "cron": "0 9 * * MON" },
  "budget": {
    "max_cost": { "amount": 5000, "currency": "KRW" },
    "max_executions": 20,
    "max_duration": "PT30M"
  },
  "started_at": "2026-08-11T09:00:00Z",
  "ended_at": "2026-08-11T09:06:20Z",
  "idle_timeout": "PT10M",
  "absolute_timeout": "PT1H",
  "status": "Completed",
  "end_reason": "goal_task_completed",
  "summary": "8월 2주차 모집 현황 리포트 생성. 누적 63명(목표 대비 63%). 랜딩 전환율 전주 대비 +0.4%p",
  "memory_ids": ["mem_812"]
}
```

기계가 읽을 수 있는 스키마: [`session.schema.json`](../intent-os-spec/schemas/session.schema.json)

---

## 9. Validation Rules

### 9.1 Session 생성

```
Session 생성 요청
  ↓
actor 확인 (SES-006) ── 없으면 반려
  ↓
중첩 검사 (INV-SES-04) ── 상위 Session이 활성이면 반려 + Agent 제안
  ↓
type별 필수 항목
  ├── interactive → actor가 인간
  ├── autonomous  → trigger_ref(스케줄) 필수
  ├── triggered   → trigger_ref(원인 Event) 필수
  ├── batch       → goal_ids 2개 이상
  └── replay      → dry_run: true 강제 (INV-SES-05)
  ↓
budget 확인 (SES-003)
  ├── 없으면 type별 기본값 부여
  └── autonomous / batch는 상한을 조직 Policy로 제한
  ↓
종료 조건 확인 (SES-002) ── idle_timeout, absolute_timeout 없으면 기본값
  ↓
policy_scope 해소 (actor·Goal에 적용되는 Active Policy 수집)
  ↓
Context 수집 → context_ref 생성
  ↓
Created → Event 발행 (session.started)
```

### 9.2 실행 전 Session 검사

모든 Execution 생성 시 호출된다([e013 §9](e013-execution.md)의 파이프라인에 포함).

```
Execution 생성 요청 (session_id 포함)
  ↓
Session status ∈ {Active, Idle} 확인 (INV-SES-03) ── 아니면 거부
  ↓
예산 검사 (INV-SES-02)
  ├── consumed.cost + 예상 비용 > max_cost      → 거부 + Suspended
  ├── consumed.executions + 1 > max_executions  → 거부 + Suspended
  └── 경과 시간 > max_duration                   → 거부 + Expired
  ↓
dry_run 검사 (INV-SES-05) ── replay Session이면 거부
  ↓
policy_scope 평가 (e019 §9.2)
  ↓
통과 → Execution 생성, last_activity_at 갱신
```

### 9.3 재개 절차

```
Suspended Session 재개 요청
  ↓
absolute_timeout 경과 확인 ── 경과 시 재개 불가, 새 Session 생성 안내
  ↓
Suspend 사유별 해소 확인
  ├── 예산 초과   → 예산 증액 승인 필요
  ├── 승인 대기   → 승인 완료 확인
  └── 사용자 보류 → 즉시 가능
  ↓
Context 재수집 (SES-005) ⚠️ 기존 Context를 재사용하지 않는다
  ↓
policy_scope 재해소 (그동안 Policy가 바뀌었을 수 있다)
  ↓
Active → Event 발행 (session.resumed)
```

---

## 10. Examples

### 예시 1 — 하나의 Goal, 네 개의 Session

```
goal_001  윈터캠프 100명 모집 (2026-08-01 ~ 2026-12-31)

ses_057  8/4   interactive   대표          계획 수립, 카피 3종 확정      12,400원
ses_061  8/5   interactive   대표          카피 검수본 승인              3,200원
ses_090  8/15  triggered     assumption    예산 삭감 대응 Replanning     8,100원
ses_180  매주  autonomous    scheduler     모집 현황 리포트              주 1,200원
ses_412  12/1  interactive   대표          시즌 성과 리뷰                6,700원
```

**Goal은 5개월을 산다. Session은 각각 몇 시간을 산다.** `ses_057`이 끝나도 `plan_014`, `art_450`, `mem_770`은 남아서 `ses_061`이 그대로 이어받는다.

### 예시 2 — Triggered Session

```
2026-08-15 10:12  evt_c04d8  assumption.invalidated (asm_012)
   ↓ 구독: Session 관리자
ses_090 생성
  type: triggered
  actor: system:assumption_validator
  trigger_ref: { event_id: "evt_c04d8", correlation_id: "corr_b12" }
  goal_ids: ["goal_001"]
  budget: { max_cost: 10000 KRW, max_executions: 30 }
   ↓
Replanning 수행 → plan_015 생성
   ↓
pol_012 (고액 실행 승인) 평가 → 대표 승인 필요
   ↓
actor가 인간이 아니므로 즉시 응답 불가 → Suspended (승인 대기)
   ↓
8/15 14:30  대표 승인
   ↓
Active 재개 → plan_015 활성화 → Completed
summary: "예산 300만→200만 삭감 대응. plan_015로 교체. 유료 광고 비중 60%→35%"
```

### 예시 3 — 예산 초과

```
ses_180  autonomous  max_cost 5,000원
  exe_901  1,200원   consumed 1,200
  exe_902    900원   consumed 2,100
  exe_903  2,400원   consumed 4,500
  exe_904  예상 1,100원 → 4,500 + 1,100 = 5,600 > 5,000
             ↓
        INV-SES-02: 생성 거부
        Session → Suspended (end_reason 후보: budget_exceeded)
        Event: budget.exceeded
             ↓
        운영자 알림. 진행 중이던 exe_903은 완료시킨다.
```

**자동 Session이 조직 예산을 태우지 못하게 막는 지점이다.**

### 예시 4 — Replay Session

```
ses_500  replay  운영자
  목적: pol_015(국내 리전 한정)를 8월 이전에 적용했다면 어떤 Decision이 바뀌었는가
  dry_run: true

  8월 Decision 142건 재판정
  ├── 변동 없음  138건
  └── 차단됨       4건 (해외 리전 Resource 선택)

  결과: Artifact로 리포트 생성 ← ❌ 금지 (INV-SES-05)
  결과: Session summary + 운영자 화면 표시 ← ✅
```

`replay`는 **아무것도 만들지 않는다.** 분석 결과조차 Artifact로 남기려면 별도의 일반 Session이 필요하다.

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **Session이 만료됐는데 인간 Resource가 4시간 뒤 회신** | Execution은 Session과 무관하게 완료된다(INV-SES-03은 **새** Execution만 막는다). Outcome이 정상 생성되고, 늦게 온 결과는 Goal에 반영된다 |
| **Session 중 Goal이 완료됨** | Session은 자동 종료되지 않는다. 다른 Goal 작업이 남아 있을 수 있다. `goal.achieved` Event가 종료 조건에 해당할 때만 종료 |
| **여러 사람이 같은 Session에 참여** | `actor`를 주 책임자로 두고 `participants[]`를 추가한다. 승인 요청은 `actor`에게 간다 |
| **Session 중 Policy가 개정됨** | 진행 중 Session의 `policy_scope`는 갱신하지 않는다. 판정 시점 버전 원칙(§[e019 §6.1](e019-policy.md))을 따른다. 재개 시에는 재해소한다(§9.3) |
| **autonomous Session이 승인을 필요로 함** | 사람이 없으므로 `Suspended`로 대기한다. `absolute_timeout` 안에 승인이 없으면 `Expired`. Policy의 `on_timeout: deny`가 최종 결정한다 |
| **Session이 중간에 크래시** | Event로 상태를 재구성한다([e020 §9.1](e020-event.md)). 진행 중이던 Execution은 `TimedOut`으로 정리하고 Outcome을 생성한다 |
| **Session 예산은 남았는데 Goal 예산이 소진** | Goal의 [Constraint](e004-constraint.md)가 우선한다. 두 예산은 독립적이며 **더 제한적인 쪽이 이긴다** |
| **replay Session이 외부 API를 호출하려 함** | 즉시 중단(INV-SES-05). 재판정은 `inputs_snapshot`만으로 수행되어야 한다 |
| **Session 없이 Execution이 생성됨** | 허용하지 않는다. 시스템 내부 작업도 `system` Session에 귀속시킨다. 그래야 모든 비용이 집계된다 |

---

## 12. Open Issues (v1.0)

### Session 예산과 Goal 예산의 관계

두 예산이 독립적이라고 정의했으나(§11), 실무에서는 "이 Goal의 남은 예산 안에서 Session을 열어라"가 자연스럽다. 예산 계층(조직 → Goal → Session)의 상속·차감 규칙이 필요하다.

### 장기 실행 Session

`absolute_timeout`을 24시간으로 예시했으나, 인간 Resource가 며칠 걸리는 Task를 포함하면 부족하다. Session을 닫고 Execution만 남기는 방식과, Session을 길게 유지하는 방식 중 선택이 필요하다.

### Context 재수집 비용

Rule SES-005는 재개 시 Context 재수집을 요구한다. 그러나 Context 수집 자체가 비용이 드는 경우(외부 API 조회) 매 재개마다 비용이 발생한다. TTL 기반 부분 재사용 규칙이 필요하다.

### ~~Volume 3와의 정합~~ — 해소됨 (2026-08-04)

[Volume 3](../v3-runtime.md)의 Runtime State Machine과 본 문서의 Session Lifecycle이 같은 계층인데 상태 이름이 달랐다(`UNDERSTANDING/PLANNING/DECIDING` vs `Active/Idle/Suspended`).

**`phase` 필드를 §4 Attributes와 [`session.schema.json`](../intent-os-spec/schemas/session.schema.json)에 정식 도입해 해소했다.** `status`는 Session의 생존 상태, `phase`는 진행 위치로 계층이 분리된다. 두 필드는 독립적이다 — `status = Suspended`이면서 `phase = EXECUTING`인 상태가 정상이며, 이는 "실행 도중 멈춘 Session"을 뜻한다.

### 앞으로 보강해야 할 항목

- 다중 actor Session의 승인 위임 규칙
- Session 요약 생성 알고리즘 (무엇을 요약에 넣는가)
- 실제 예시 30~50개
