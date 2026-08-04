# Entity 000-A: Entity Relationship Model & Invariants

- **Version:** v1.0 Draft
- **Status:** Core Architecture
- **Last Updated:** 2026-08-04

---

## 0. Why This Document Exists

지금까지는 Entity를 **하나씩** 정의했다. 그것만으로는 운영체제가 되지 않는다.

Linux에서 중요한 것은 `task_struct` 하나가 아니라 **Process Tree와 그것이 절대 깨지지 않는다는 보장**이다. 관계와 불변식이 없으면 각 구현체는 같은 스키마를 쓰면서도 서로 호환되지 않는 시스템을 만든다.

이 문서는 27개 Entity가 **서로 어떻게 연결되고, 어떤 상태가 되면 시스템이 고장난 것인지**를 정의한다.

> **Entity 명세는 Entity의 정의가 아니라 Entity 사이의 계약이다.**

---

## 1. 3계층 분류

Entity를 늘리기 전에 계층부터 정리한다. 초안에서 Entity 10개를 잡았을 때의 문제는 개수가 아니라 **계층이 섞여 있었다**는 점이었다.

| 계층 | 의미 | 저장 여부 | 예 |
|---|---|---|---|
| **Entity** | 시스템에 존재하는 것. 식별자를 갖고 저장·조회된다 | 영속 | Goal, Task, Execution, Outcome |
| **Process** | 시스템이 수행하는 것. 동사다 | 비영속 | Planning, Deciding, Executing, Learning |
| **Runtime State** | 실행 중 변하는 값. Entity의 필드로 존재한다 | Entity에 종속 | `Execution.status`, `Goal.progress` |

### Execution과 Outcome은 왜 Entity인가

이전 판([README.md](README.md) v1.0)에서는 Execution을 Process, Outcome을 Runtime State로 분류했다. **이 분류는 v2.0에서 정정한다.**

운영체제의 비유가 그대로 답이 된다.

```
"프로세스가 돌고 있다"        → Process (동사, 저장 대상 아님)
 task_struct                → Entity  (명사, 커널이 소유하는 레코드)
 task_struct.state = RUNNING → Runtime State (Entity의 필드)
```

| 이름 | 계층 | 근거 |
|---|---|---|
| **Executing** | Process | "지금 실행 중"이라는 행위. 저장하지 않는다 |
| **Execution** (E013) | **Entity** | 그 행위의 제어 블록. 식별자·시작시각·재시도 횟수를 갖고 저장된다 |
| `Execution.status` | Runtime State | `RUNNING` / `WAITING` 같은 순간값 |
| **Evaluating** | Process | 평가하는 행위 |
| **Outcome** (E014) | **Entity** | 실행이 낳은 불변 기록. 사후 조회·감사·학습의 대상이다 |

판별 기준은 하나다.

> **1년 뒤에 조회해야 하는가?** 그렇다면 Entity다.

Execution 이력 없이는 Resource Drift를 감지할 수 없고, Outcome 없이는 Learning이 성립하지 않는다. 둘 다 영속 대상이므로 Entity다.

Learning과 Prediction은 여전히 **Process**다. 이들이 남기는 산출물은 [Memory](e010-memory.md)·[Knowledge](e011-knowledge.md)라는 별도 Entity다.

---

## 2. Entity 27개 지도

```
                          ┌─────────────────────────────┐
                          │  Governance (횡단)           │
                          │  Policy 019 · Constraint 004 │
                          │  Assumption 017 · Risk 018   │
                          └─────────────────────────────┘
                                      │ 제약
                                      ▼
Session 021 ──▶ Goal 001 ──▶ Intent 002 ──▶ Task 005 ──▶ Capability 006
                  │ (Goal Graph 001-A)         │ (Task Graph 005-A)   │ (Taxonomy 006-A)
                  │                            │                      │
                  ▼                            ▼                      ▼
               Plan 008 ─────────────▶ Workflow 022            Resource 007
                  │                            │                      │
                  │                            │              Resource Profile 025
                  ▼                            ▼               Tool 024 · Agent 023
              Decision 009 ────────────▶ Execution 013
                                               │
                                               ▼
                                          Outcome 014 ──▶ Artifact 016
                                               │
                                               ▼
                                        Evaluation 015 ◀── Feedback 012
                                               │
                                               ▼
                                          Memory 010 ──▶ Knowledge 011
                                               │
                                               └──────▶ Decision 009 (개선)

               Context 003 ─── 모든 단계에 주입
               Event  020 ─── 모든 상태 전이에서 발생
```

세 개의 경로가 있다.

| 경로 | 흐름 | 성격 |
|---|---|---|
| **하향 분해** | Goal → Intent → Task → Capability → Resource | 무엇을 원하는가에서 누가 할 것인가까지 |
| **실행** | Plan → Decision → Execution → Outcome → Artifact | 결정에서 산출물까지 |
| **상향 학습** | Evaluation → Memory → Knowledge → Decision | 결과가 다음 결정을 바꾼다 |

**Governance(Policy / Constraint / Assumption / Risk)와 Context / Event는 경로가 아니라 횡단 관심사다.** 특정 단계에 속하지 않고 모든 단계에 관여한다.

---

## 3. Cardinality 전체표

시스템 전체의 관계 수를 한 표에 모은다. 구현자는 이 표만 보고 스키마의 외래키를 설계할 수 있어야 한다.

| 좌변 | 관계 | 우변 | Cardinality | 비고 |
|---|---|---|---|---|
| Session | 다룬다 | Goal | `1:0..N` | Goal은 Session보다 오래 산다. 소유가 아니라 참조다 |
| Goal | 하위 목표 | Goal | `1:0..N` | Goal Graph. DAG |
| Goal | 해석된다 | Intent | `1:1..N` | Goal 하나에 해결 영역 여럿 |
| Goal | 계획된다 | Plan | `1:0..N` | 버전 관리. **Active는 항상 1개** |
| Intent | 분해된다 | Task | `1:1..N` | |
| Plan | 포함한다 | Task | `1:1..N` | Plan의 Task Graph |
| Plan | 실행순서 | Workflow | `1:0..1` | Workflow가 없으면 의존 순서대로 실행 |
| Task | 선행한다 | Task | `N:M` | Task Graph. DAG |
| Task | 요구한다 | Capability | `N:M` | `required_capabilities` |
| Capability | 제공된다 | Resource | `N:M` | 점수와 함께 |
| Resource | 갖는다 | Resource Profile | `1:1` | Profile 없는 Resource는 Active 불가 |
| Resource | 특화형 | Tool / Agent | `1:0..1` | Tool·Agent는 Resource의 부분집합 |
| Task | 낳는다 | Decision | `1:0..N` | 재선택 시 새 Decision |
| Decision | 낳는다 | Execution | `1:0..N` | 재시도마다 새 Execution |
| Task | 낳는다 | Execution | `1:0..N` | Decision 경유 |
| Agent | 수행한다 | Execution | `1:0..N` | Agent가 실행 주체일 때 |
| Execution | 낳는다 | Outcome | `1:0..1` | **종료된 Execution은 정확히 1개** |
| Outcome | 담는다 | Artifact | `1:0..N` | 실패 Outcome은 0개 가능 |
| Outcome | 평가된다 | Evaluation | `1:0..N` | 평가자·시점마다 1개 |
| Feedback | 입력된다 | Evaluation | `N:M` | Feedback은 Evaluation의 입력원 |
| Evaluation | 축적된다 | Memory | `1:0..N` | |
| Memory | 승격된다 | Knowledge | `N:1` | 여러 Memory가 하나의 Knowledge로 |
| Goal / Plan | 전제한다 | Assumption | `1:0..N` | |
| Plan | 식별한다 | Risk | `1:0..N` | |
| Policy | 지배한다 | 모든 Entity | `1:N` | 전역 |
| Constraint | 제약한다 | Goal / Task / Plan | `N:M` | 상속·전파된다 |
| Context | 주입된다 | 모든 Entity | `N:M` | Scope 계층에 따라 |
| 모든 Entity | 발생시킨다 | Event | `1:0..N` | 상태 전이마다 |

---

## 4. 참조 방향 규칙

관계는 양방향으로 보이지만, **저장되는 참조(foreign key)는 한 방향뿐**이다.

### Rule REL-001 — 하위가 상위를 참조한다

```
✅  Task.goal_id = "goal_001"
❌  Goal.task_ids = ["task_001", ...]
```

Goal이 Task 목록을 들고 있으면 Task를 추가할 때마다 Goal을 수정해야 한다. Goal은 안정적이어야 하는 Entity다.

### Rule REL-002 — 시간상 뒤에 생긴 것이 앞의 것을 참조한다

```
Decision.subject      → Task        (Task가 먼저 존재)
Execution.decision_id → Decision
Outcome.execution_id  → Execution
Evaluation.outcome_id → Outcome
```

### Rule REL-003 — 역방향 링크는 캐시일 뿐이다

`Decision.outcome_link` 처럼 편의를 위한 역방향 필드는 허용하되, **진실의 원천(Source of Truth)이 아니다.** 정합성이 깨지면 정방향 참조를 신뢰한다.

### Rule REL-004 — 계층을 건너뛰는 참조를 금지한다

```
❌  Task.resource_id = "anthropic:claude-5"
✅  Task → Capability → (Decision) → Resource
```

Task가 Resource를 직접 가리키면 Principle 03(Resource Agnostic)이 무너진다. 계층을 건너뛰어야 한다면 그것은 설계가 잘못된 신호다.

### Rule REL-005 — 순환 참조는 Graph Entity에서만 허용한다

Goal Graph와 Task Graph는 노드 간 참조를 갖지만 **DAG여야 한다**(INV-08). 그 외 Entity 간의 순환 참조는 금지한다.

---

## 5. 전역 불변식 (Global Invariants)

여기서 정의한 `INV-NN`은 **시스템 전체에 항상 성립해야 하는 규칙**이다. 하나라도 깨지면 그것은 잘못된 입력이 아니라 **시스템의 버그**다.

### INV-01 — Goal Reachability

> 모든 Task는 참조 사슬을 따라가면 정확히 하나 이상의 Goal에 도달한다.

```
Task → Intent → Goal        ✅
Task → (없음)               ❌ 고아 Task
```

| | |
|---|---|
| **위반 시** | Runtime이 해당 Task를 `Orphaned`로 격리하고 실행하지 않는다 |
| **탐지** | Task 생성 시 + 주기적 Graph 스캔 |
| **근거** | Goal 없는 실행은 비용만 쓰고 학습 신호를 만들지 못한다 |

### INV-02 — No Unexplained Assignment

> Resource가 배정된 모든 Task에는 그 배정을 설명하는 Decision이 존재한다.

`Task.state = Assigned` 인데 대응하는 `Decision(type=ResourceSelection)`이 없으면 위반이다.

| | |
|---|---|
| **위반 시** | 실행을 차단하고 Decision 생성을 강제한다 |
| **예외** | 대안이 하나뿐인 강제 실행(Forced Action)도 Decision을 남긴다. `alternatives_considered: []` + `forced: true` |
| **근거** | 설명할 수 없는 선택은 감사도 학습도 불가능하다 ([e009 Rule D-001](e009-decision.md)) |

### INV-03 — Execution Provenance

> 모든 Execution은 정확히 하나의 Decision에서 파생된다.

| | |
|---|---|
| **위반 시** | Execution을 시작하지 않는다. 이미 시작했다면 `Aborted`로 종료 |
| **근거** | Decision 없는 Execution은 비용 추적과 책임 소재가 사라진다 |

### INV-04 — Outcome Completeness

> 종료 상태에 도달한 모든 Execution은 정확히 하나의 Outcome을 가진다.

성공(`Succeeded`)이든 실패(`Failed`)든 취소(`Aborted`)든 예외가 없다. **실패도 결과다.**

| | |
|---|---|
| **위반 시** | Runtime이 `status: failed`, `artifacts: []` 인 최소 Outcome을 자동 생성한다 |
| **근거** | Outcome이 비면 Resource 성공률 통계에 구멍이 생긴다 |

### INV-05 — No Orphan Artifact

> 모든 Artifact는 정확히 하나의 Outcome에 속한다.

| | |
|---|---|
| **위반 시** | 고아 Artifact는 GC 대상으로 표시하되 보존 기간까지 삭제하지 않는다 |
| **근거** | 출처를 모르는 산출물은 신뢰할 수 없다 ([e016 Rule ART-002](e016-artifact.md)) |

### INV-06 — Immutability of Records

> Decision, Execution(종료 후), Outcome, Evaluation, Event, Artifact의 **내용**은 생성 이후 수정되지 않는다.

수정이 필요하면 **새 레코드 + `supersedes` 링크**를 만든다.

| | |
|---|---|
| **위반 시** | 저장 계층이 쓰기를 거부한다. 감사 로그에 시도를 기록한다 |
| **허용되는 변경** | 상태 필드(`status`)와 사후 링크(`outcome_link`, `evaluation_ids`) 추가만 |
| **근거** | 감사 가능성의 전제 ([e009 Rule D-005](e009-decision.md)) |

### INV-07 — Hard Constraint Supremacy

> Hard [Constraint](e004-constraint.md)를 위반하는 Decision은 `Committed` 상태로 전이할 수 없다.

| | |
|---|---|
| **위반 시** | Decision을 `Rejected`로 전이하고 사유를 기록. 재선택을 트리거 |
| **주의** | Soft Constraint 위반은 Utility 감점일 뿐 차단이 아니다 |

### INV-08 — Acyclicity

> Goal Graph, Task Graph, Workflow는 모두 DAG다. 순환이 존재하면 안 된다.

| | |
|---|---|
| **위반 시** | 그래프 변경을 롤백하고 순환 경로를 오류로 반환 |
| **탐지** | 간선 추가 시점 (증분 순환 검사) |
| **근거** | 순환은 Runtime 교착 상태를 만든다 |

### INV-09 — Layer Isolation

> Task는 Resource를 모르고, Capability는 Resource를 모른다.

```
❌  Task.objective = "Claude로 카피 작성"
❌  Capability.provided_by = ["anthropic:claude-5"]
✅  Resource.capabilities = ["language.generation.copywriting"]
```

관계의 방향이 중요하다. **Resource가 Capability를 선언하지, Capability가 Resource를 나열하지 않는다.**

| | |
|---|---|
| **위반 시** | Task Validation이 Resource 이름을 검출해 Capability로 치환한다 ([e005 Rule T-004](e005-task.md)) |
| **근거** | Principle 03 — Resource Agnostic ([Volume 1](../v1-core-concepts.md)) |

### INV-10 — Assumption Accountability

> 깨진(`Invalidated`) Assumption은 반드시 Replanning 또는 명시적 승인(Acknowledged Risk)으로 귀결된다.

깨진 가정을 방치한 채 Plan이 `Active`로 남아 있으면 위반이다.

| | |
|---|---|
| **위반 시** | Plan을 `Suspended`로 전이하고 Replanning을 큐에 넣는다 |
| **근거** | 가정이 깨졌는데 계획이 그대로면 그 계획은 이미 틀린 계획이다 ([e017](e017-assumption.md)) |

### INV-11 — Policy Precedence

> Policy는 Decision보다 우선한다. Policy가 금지한 것을 Decision이 선택할 수 없다.

우선순위는 다음과 같다.

```
Policy  >  Hard Constraint  >  Decision Utility  >  Soft Constraint
```

| | |
|---|---|
| **위반 시** | 해당 후보를 Candidate Generation 단계에서 제거한다. 이미 실행 중이면 즉시 중단 |
| **근거** | 최적해가 규정 위반이면 그것은 해가 아니다 ([e019](e019-policy.md)) |

### INV-12 — Event Completeness

> Entity의 모든 상태 전이는 정확히 하나의 Event를 발생시킨다.

| | |
|---|---|
| **위반 시** | Event가 유실되면 시스템 상태 재구성이 불가능하다. Runtime이 정합성 경고를 발생시킨다 |
| **근거** | Event Sourcing으로 상태를 재구성할 수 있어야 한다 ([e020](e020-event.md)) |

### INV-13 — Temporal Ordering

> 실행 사슬의 시각은 단조 증가한다.

```
Decision.decided_at
  ≤ Execution.started_at
  ≤ Execution.finished_at
  = Outcome.produced_at
  ≤ Evaluation.evaluated_at
```

| | |
|---|---|
| **위반 시** | 데이터 정합성 오류로 기록하고 해당 레코드를 학습 데이터에서 제외 |
| **근거** | 시간이 뒤집히면 인과 분석이 무너지고 Learning이 오염된다 |

### INV-14 — Single Active Plan

> 하나의 Goal에 대해 `Active` 상태인 Plan은 최대 1개다.

| | |
|---|---|
| **위반 시** | 가장 최근 버전만 남기고 나머지를 `Superseded`로 전이 |
| **근거** | 동시에 두 계획이 살아 있으면 Task Graph가 충돌한다 ([e008](e008-plan.md)) |

### INV-15 — Profile Existence

> `Active` 상태의 Resource는 반드시 Resource Profile을 가진다.

| | |
|---|---|
| **위반 시** | Resource를 `Evaluating`으로 강등하고 후보군에서 제외 |
| **근거** | Profile이 없으면 cost/latency 추정이 불가능해 Utility를 계산할 수 없다 ([e025](e025-resource-profile.md)) |

### INV-16 — Session Boundary

> Session은 Entity를 소유하지 않는다. 참조만 한다.

Session이 끝나도 Goal, Memory, Knowledge, Artifact는 살아남는다. Session에 종속되어 사라지는 것은 **일시적 Context와 대화 버퍼뿐**이다.

| | |
|---|---|
| **위반 시** | Session 종료 시 Entity가 함께 삭제되면 데이터 손실이다. 삭제를 차단한다 |
| **근거** | Intent OS의 기억은 대화보다 오래 산다 ([e021](e021-session.md)) |

---

## 6. 불변식 검사 시점

전부를 항상 검사하면 비용이 감당되지 않는다. 검사 시점을 셋으로 나눈다.

| 시점 | 대상 | 비용 |
|---|---|---|
| **쓰기 시(Write-time)** | INV-02, 03, 05, 06, 07, 08, 11, 13, 14 | 낮음. 트랜잭션 내 |
| **전이 시(Transition-time)** | INV-04, 10, 12, 15 | 중간. 상태 머신 훅 |
| **주기 스캔(Sweep)** | INV-01, 09, 16 | 높음. 일 1회 배치 |

```
쓰기 요청
  ↓
Write-time Invariant 검사 ── 위반 → 트랜잭션 롤백
  ↓
커밋
  ↓
상태 전이 발생 → Transition-time 검사 ── 위반 → 보정 액션 (Outcome 자동 생성 등)
  ↓
Event 발행
  ↓
(일 1회) Sweep ── 위반 → 격리 + 운영자 알림
```

---

## 7. 표준 실행 사슬(Canonical Chain)

Intent OS에서 가장 중요한 참조 사슬이다. 이 사슬이 끊기면 학습이 불가능해진다.

```
Goal        goal_001    윈터캠프 100명 모집
  └ Intent  int_003     신규 학부모 유입을 늘린다
      └ Task    task_004   인스타그램 광고 카피 3종 작성
          └ Decision  dec_101   Claude 선택 (utility 0.91)
              └ Execution exe_220  RUNNING → SUCCEEDED (1,820ms, 0.42 USD)
                  └ Outcome   out_331  quality 0.93
                      ├ Artifact  art_450  카피 3종 (text/markdown)
                      └ Evaluation eva_512 goal_alignment 0.87
                          └ Memory  mem_770 → Knowledge know_090
```

이 사슬은 **양방향으로 완전히 순회 가능해야 한다.**

| 질문 | 순회 방향 |
|---|---|
| 이 카피는 왜 이렇게 나왔는가 | Artifact → Outcome → Execution → Decision → Task → Intent → Goal |
| 이 Goal에 얼마를 썼는가 | Goal → Task* → Execution* 의 cost 합 |
| Claude는 이 도메인에서 잘하는가 | Resource → Execution* → Outcome* → Evaluation* 의 통계 |

---

## 8. 관계의 무결성 위반 사례

실제로 자주 발생하는 오류 유형이다.

| 사례 | 위반 | 증상 |
|---|---|---|
| Planner가 Task를 만들고 Intent를 연결하지 않음 | INV-01 | 비용은 발생하는데 어느 Goal의 성과인지 집계 불가 |
| 운영자가 콘솔에서 Resource를 직접 지정 | INV-02 | Learning이 "왜 그 선택이 좋았는지" 학습하지 못함 |
| 타임아웃된 Execution이 Outcome 없이 방치 | INV-04 | Resource 성공률이 실제보다 높게 계산됨 |
| Decision의 rationale을 사후에 "보기 좋게" 수정 | INV-06 | 결과론 편향. 예측 정확도 평가가 무의미해짐 |
| 예산 초과 가정이 깨졌는데 Plan 유지 | INV-10 | 300만원 예산을 넘겨 집행 |
| Goal Graph에 순환 추가 | INV-08 | Planner 무한 루프 |

---

## 9. Entity 추가 시 지켜야 할 것

새 Entity를 추가할 때 아래를 반드시 갱신한다. **하나라도 빠지면 관계 모델에 구멍이 생긴다.**

```
[ ] §3 Cardinality 전체표에 행을 추가했는가
[ ] §2 Entity 지도에 위치를 표시했는가
[ ] 참조 방향이 Rule REL-001~005를 지키는가
[ ] 새 전역 불변식이 필요한가 (§5)
[ ] 기존 불변식 중 이 Entity에 적용되는 것을 §5에 명시했는가
[ ] Rule Prefix를 [e000 §3](e000-spec-format.md)에 등록했는가
```

---

## 10. Open Issues (v1.0)

### 불변식 위반의 심각도 등급

현재 모든 불변식이 동등하게 서술되어 있다. 실제로는 "즉시 중단"과 "경고 후 계속"이 구분되어야 한다. `severity: fatal / error / warn` 등급 도입이 필요하다.

### 분산 환경에서의 불변식

INV-04(Outcome Completeness)와 INV-12(Event Completeness)는 단일 트랜잭션을 전제한다. Execution이 여러 노드에 분산되면 최종적 일관성(Eventual Consistency)만 보장 가능하다. 그 경우 "언제까지 수렴해야 하는가"의 기한 정의가 없다.

### Session 경계와 GDPR 삭제 요구

INV-16은 Entity가 Session보다 오래 사는 것을 보장한다. 그러나 사용자의 삭제 요구가 있으면 Artifact·Memory를 지워야 한다. 이때 Outcome·Evaluation의 통계값을 어떻게 보존할지(익명화 vs 삭제)가 미정이다.

### 앞으로 보강해야 할 항목

- 불변식별 자동 검사기 구현 → [Volume 7](../v7-reference-implementation.md)
- Cardinality 표를 기계가 읽을 수 있는 형식(관계 스키마)으로 추출
- Entity 간 참조 무결성의 캐스케이드 규칙 (삭제·아카이빙 시)
- 불변식 위반 시 발생하는 Event Type 표준화 ([e020](e020-event.md)와 연동)
