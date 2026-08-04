# Entity 005: Task

- **Version:** v2.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Task is an independently executable unit of work that contributes to achieving a Goal.**

> Task는 Goal 달성에 기여하는, 독립적으로 실행 가능한 작업 단위이다.

여기서 중요한 단어는 **Independently Executable**이다.

Task는 "해야 할 일 목록의 한 줄"이 아니다. **입력, 필요 능력, 기대 출력이 정의되어 있어서 시스템이 Resource에게 그대로 할당할 수 있는 실행 단위**다.

---

## 2. Task는 무엇이 아닌가?

정의보다 이게 훨씬 중요하다.

### Task는 Goal이 아니다

❌ `학생 100명 모집` — 이건 Task가 아니다. [Goal](e001-goal.md)이다.

Goal은 **미래 상태**이고, Task는 그 상태에 도달하기 위한 **행위**다.

```
Goal:  학생 100명 모집          (상태)
Task:  광고 카피 작성           (행위)
```

### Task는 Capability가 아니다

❌ `언어 생성` — 이건 능력이다. Task가 아니다.

Task는 능력을 **요구**할 뿐, 능력 그 자체가 아니다. [e006-capability.md](e006-capability.md) 참조.

### Task는 Prompt가 아니다

❌ `카피 좀 멋지게 써줘` — 이건 Prompt다.

Prompt는 특정 Resource(LLM)에게 보내는 **실행 시점의 입력 표현**이며, [Execution](e013-execution.md)의 `input_ref`에 보존된다. Task는 Resource가 결정되기 전에 존재하는 **Resource 중립적** 객체다. 같은 Task라도 Resource가 Claude면 Prompt로, 사람이면 업무 지시서로 변환된다.

### Task는 Execution이 아니다

❌ `광고 카피 작성 중 (34% 진행)` — 이건 [Execution](e013-execution.md)(Entity 013)이다.

| | Task | Execution |
|---|---|---|
| 성격 | 무엇을 해야 하는가 (의도) | 실제로 어떻게 시도했는가 (사실) |
| Resource | 모른다 | 정확히 하나를 안다 |
| 개수 | Goal당 고정 | **재시도마다 증가** |
| 수정 | 가능 (재분해 등) | 종료 후 불변 |

`Task 1:0..N Execution`이다. 같은 Task를 3번 재시도했다면 Execution은 3개다.

### Task는 Workflow의 step이 아니다

❌ `s3_copywriting` — 이건 [Workflow](e022-workflow.md)의 단계 정의다.

Workflow의 step은 **재사용 가능한 템플릿의 한 칸**이고, Task는 그 칸이 특정 Goal에 대해 **인스턴스화된 결과**다. step은 Capability만 알고, Task는 `goal_id`와 구체적 `objective`를 안다.

---

## 3. Design Principles

Task는 반드시 아래 조건을 만족해야 한다.

### Rule T-001 — 독립적으로 실행 가능해야 한다

의존하는 Task가 완료되었다는 전제 하에, **추가 정보 없이 하나의 Resource에 할당 가능해야 한다.**

- ✅ `윈터캠프 타겟(예비 고3 학부모)용 인스타그램 광고 카피 3종 작성`
- ❌ `마케팅 잘하기` — 할당 불가능. 분해가 필요하다.

### Rule T-002 — 기대 출력(Expected Output)이 정의되어야 한다

✅ `경쟁 학원 5곳의 가격/커리큘럼 비교표`

❌ `경쟁사 좀 알아보기` — 무엇이 나오면 완료인지 알 수 없다.

Expected Output은 [Outcome](e014-outcome.md)의 `status` 판정 기준이 된다. 기대 개수를 충족하면 `succeeded`, 미달이면 `partial`이다([e014 §9.1](e014-outcome.md)).

### Rule T-003 — Required Capabilities를 명시해야 한다

**이것이 Task의 가장 중요한 속성이다.** Decision Engine은 Task의 `required_capabilities`와 Resource의 `capabilities`를 매칭해서 실행 주체를 선택한다. Capability가 비어 있는 Task는 라우팅할 수 없다.

Capability 식별자는 [Capability Taxonomy](e006a-capability-taxonomy.md)의 표준 이름을 쓴다. 매칭은 **하향 포함·상향 미포함**이다([Rule CT-005](e006a-capability-taxonomy.md)).

### Rule T-004 — Resource 이름을 포함하면 안 된다

❌ `Claude로 카피 작성`

분석 결과:

```
Task:       광고 카피 작성
Capability: language.generation.copywriting
Resource:   (Decision Engine이 결정)
```

Resource 선택은 Task의 소관이 아니다([INV-09](e000a-entity-relationships.md) Layer Isolation, Principle 03 — Resource Agnostic).

### Rule T-005 — 반드시 Goal에 연결되어야 한다

어떤 Goal에도 기여하지 않는 Task는 시스템이 관리하지 않는다([INV-01](e000a-entity-relationships.md) Goal Reachability).

### Rule T-006 — 정확히 하나의 Plan에 속한다

Task는 [Plan](e008-plan.md) 밖에서 독립적으로 존재하지 않는다. 다른 Plan의 결과를 쓰고 싶다면 Task를 공유하는 것이 아니라 [Artifact](e016-artifact.md)를 참조한다([INV-P-07](e008-plan.md)).

### Rule T-007 — Retry Policy를 가진다

실패는 정상 상태다([Volume 3 §6](../v3-runtime.md)). 실패했을 때 무엇을 할지 미리 정하지 않으면 Runtime이 판단할 근거가 없다.

---

## 4. Attributes

Task는 최소한 아래 속성을 가진다.

```
Task
├── Identity
│   ├── id
│   ├── goal_id
│   └── plan_id
├── Definition
│   ├── objective
│   ├── required_capabilities
│   ├── expected_output
│   └── task_type
├── Structure
│   ├── dependencies
│   ├── execution_mode
│   └── priority
├── Governance
│   ├── constraints
│   ├── irreversible
│   └── retry_policy
└── State
    └── state
```

| 속성 | 의미 | 예 |
|---|---|---|
| **id** | 식별자 | `task_004` |
| **goal_id** | 어느 Goal에 기여하는가 | `goal_001 (학생 100명 모집)` |
| **plan_id** | 소속 Plan (Rule T-006) | `plan_014` |
| **objective** | 무엇을 하는가 | `인스타그램 광고 카피 3종 작성` |
| **required_capabilities** | 필요한 능력 목록 | `language.generation.copywriting`, `analysis.audience` |
| **expected_output** | 완료 판정 기준이 되는 산출물 | `카피 3종 + 각 카피의 타겟 근거` |
| **task_type** | 요구 능력의 성격 (§4.1) | `Creation` |
| **dependencies** | 선행 Task | `["task_003"]` |
| **execution_mode** | 실행 방식 (§4.2) | `sequential` |
| **priority** | Task Graph 내 우선순위 | High |
| **constraints** | Task 수준 제약 | `건당 비용 5,000원 이하`, `24시간 이내` |
| **irreversible** | 되돌릴 수 없는 작업인가 | `false` |
| **retry_policy** | 실패 시 행동 (Rule T-007) | 최대 2회 재시도 후 Resource 재선택 |
| **state** | 상태 머신의 현재 상태 (§6) | Pending |

> **`irreversible`이 왜 Task에 있는가:** 광고 집행·메시지 발송처럼 되돌릴 수 없는 작업은 [Risk](e018-risk.md) 평가에서 impact가 한 단계 상향되고([Rule RSK-008](e018-risk.md)), [Policy](e019-policy.md)의 승인 게이트를 강제로 통과해야 한다. 실행 시점에 판단하면 이미 늦다.

### 4.1 Task Types

Task는 요구하는 Capability의 성격에 따라 분류된다. Task Type은 Decision Engine의 후보 생성(Candidate Generation)을 좁혀주고, [Evaluation](e015-evaluation.md)의 가중치를 결정한다([e015 §9.1](e015-evaluation.md)).

```
Task
├── Research Task        (조사·수집)
├── Analysis Task        (분석·비교)
├── Creation Task        (생성·제작)
├── Transformation Task  (변환·가공)
├── Decision Task        (판단·선택)
├── Communication Task   (전달·상담)
├── Automation Task      (반복 실행)
└── Verification Task    (검증·평가)
```

| Type | 예시 | 주 Capability 도메인 |
|---|---|---|
| **Research Task** | `홍대 지역 경쟁 학원 조사` | `research.*` |
| **Analysis Task** | `광고 채널별 CAC 비교` | `analysis.*` |
| **Creation Task** | `광고 카피 3종 작성` | `language.generation.*`, `creation.*` |
| **Transformation Task** | `상담 녹취록 요약` | `language.transformation.*` |
| **Decision Task** | `광고 예산 배분안 선택` | `reasoning.*` |
| **Communication Task** | `학부모 안내 메시지 발송` | `communication.*` |
| **Automation Task** | `주간 모집 현황 리포트 생성` | `automation.*` |
| **Verification Task** | `랜딩페이지 카피 사실 검증` | `verification.*` |

### 4.2 Execution Mode

Task Graph 실행 방식은 세 가지다([Volume 3 Stage 5](../v3-runtime.md)).

| Mode | 의미 | 예 |
|---|---|---|
| **sequential** | 선행 Task 완료 후 실행 | 조사 → 분석 → 보고서 |
| **parallel** | 의존이 없는 Task 동시 실행 | 시장 조사 ‖ 경쟁 분석 ‖ 고객 분석 |
| **conditional** | 조건에 따라 실행 여부 결정 | `IF 전환율 < 목표 → 랜딩페이지 개선` |

`execution_mode`는 **Task 하나의 실행 방식**이다. 여러 Task에 걸친 분기·반복은 [Workflow](e022-workflow.md)의 영역이다.

---

## 5. Invariants

### INV-T-01 — 모든 Task는 Goal에 도달 가능하다

[INV-01](e000a-entity-relationships.md) Goal Reachability의 Task 측 표현이다.

| | |
|---|---|
| **위반 시** | Task를 `Orphaned`로 격리하고 실행하지 않는다 |
| **탐지** | Task 생성 시 + 일 1회 Graph 스캔 |
| **근거** | Goal 없는 실행은 비용만 쓰고 학습 신호를 만들지 못한다 |

### INV-T-02 — Task에 Resource 식별자가 등장할 수 없다

| | |
|---|---|
| **위반 시** | Validation이 Resource 이름을 검출해 Capability로 치환한다 (§9). 치환 불가면 반려 |
| **근거** | [INV-09](e000a-entity-relationships.md) Layer Isolation |

### INV-T-03 — Assigned 상태의 Task에는 대응하는 Decision이 존재한다

[INV-02](e000a-entity-relationships.md) No Unexplained Assignment의 Task 측 표현이다.

| | |
|---|---|
| **위반 시** | 실행을 차단하고 Decision 생성을 강제한다 |

### INV-T-04 — 동시에 Running인 Execution은 Task당 최대 1개다

| | |
|---|---|
| **위반 시** | 나중에 시작된 Execution을 `Aborted`로 종료 ([INV-EXE-03](e013-execution.md)) |
| **예외** | `collaborative` / `shadow` 모드는 예외로 인정된다 |

### INV-T-05 — dependencies는 순환하지 않는다

| | |
|---|---|
| **위반 시** | 간선 추가를 롤백하고 순환 경로를 반환 ([INV-TG-01](e005a-task-graph.md)) |
| **근거** | 순환은 Runtime 교착 상태를 만든다 |

### INV-T-06 — Blocked Task에는 Execution이 생성되지 않는다

선행 Task가 최종 실패해 입력을 얻을 수 없는 상태다.

| | |
|---|---|
| **위반 시** | Execution 생성 거부 ([INV-TG-06](e005a-task-graph.md)). 입력이 없는 실행은 비용만 태운다 |

### INV-T-07 — 재시도 횟수는 retry_policy.max_retries를 넘지 않는다

| | |
|---|---|
| **위반 시** | Execution 생성 거부. `abort` 경로로 전환하고 하류 Task를 Blocked로 전파 |
| **근거** | 재시도 폭주는 예산을 태우는 가장 흔한 경로다 |

### INV-T-08 — irreversible Task는 Policy 승인 없이 실행되지 않는다

| | |
|---|---|
| **위반 시** | Execution 생성 차단 + `policy.violated` Event ([INV-TOL-05](e024-tool.md), [INV-WFL-05](e022-workflow.md)) |

---

## 6. Lifecycle

Task의 상태는 다음 6개다. ([task.schema.json](../intent-os-spec/schemas/task.schema.json)의 `state` enum과 동일하다.)

```
Pending → Assigned → Running → Completed → Evaluated
   ▲                    │
   │                    ▼
   └──(재시도)──────── Failed ──(재시도 소진)──▶ Aborted
                                                    │
Blocked ◀──(상류 실패 전파)────────────────────────┘
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Pending** | 실행 대기 | 생성됨, 또는 재시도 결정됨 |
| **Assigned** | Resource 할당됨 | Decision Engine이 Resource 선택 (INV-T-03) |
| **Running** | 실행 중 | Runtime이 Execution 시작 |
| **Completed** | 산출물 생성됨 | Expected Output 산출 |
| **Evaluated** | 평가 완료 | Evaluation이 verdict 판정 |
| **Failed** | 실행 실패 | 오류, 타임아웃, 품질 미달 |
| **Aborted** | 재시도 소진 또는 취소 | max_retries 초과, Plan 폐기 |
| **Blocked** | 상류 실패로 실행 불가 (파생 상태) | 모든 선행이 최종 실패 |

**주의:** `Completed ≠ 성공`이다. Completed는 "산출물이 나왔다"는 뜻이고, 좋은 결과인지는 **Evaluated에서 판정**한다. 평가에서 품질 미달(`verdict: reject`)이면 Failed로 전이할 수 있다.

`Ready`와 `Blocked`는 저장하지 않고 그래프 구조에서 계산한다([e005a §9.2](e005a-task-graph.md)).

### 6.1 실패 처리와 재시도

Failed 상태의 Task는 Retry Policy에 따라 처리된다. 원인 분류는 [Execution](e013-execution.md)의 `failure_class`가 제공한다.

| failure_class | 조치 | 새 Execution |
|---|---|---|
| `resource_unavailable` | 같은 Resource로 재시도 (max_retries 이내) | 같은 Decision |
| `resource_incapable` | Decision Engine이 다른 Resource 선택 | **새 Decision** |
| `input_insufficient` | 사용자/상위 Task로 escalate | 없음 |
| `timeout` | 재시도 또는 Task 재분해 | 상황에 따라 |
| `constraint_violation` | 중단. Replanning | 없음 |
| `policy_violation` | 즉시 중단. **재시도 금지** | 없음 |
| `internal_error` | 재시도. 3회 초과 시 운영자 알림 | 같은 Decision |

```
Failed
  ↓
failure_class 분류 (e013 §4.2)
  ↓
retry_policy 적용
  ├── attempt < max_retries  → Pending 복귀 → 새 Execution
  └── attempt ≥ max_retries  → Aborted
                                 ↓
                            하류 Task → Blocked (e005a §9.3)
                                 ↓
                            Goal Graph에 영향 전파
```

실패 이력은 버려지지 않는다. **[Resource Profile](e025-resource-profile.md)의 `success_rate` 갱신 입력이 된다.** 다만 실패한 Execution은 `observed_score`에는 반영하지 않는다 — 품질을 측정할 산출물이 없기 때문이다([e025 §11](e025-resource-profile.md)).

---

## 7. Relationships

```
Goal 001 ──▶ Intent 002 ──▶ Task 005 ──요구──▶ Capability 006 ──제공──▶ Resource 007
                              │  │
              Plan 008 ──소속──┘  ├──구조──▶ Task Graph 005-A
                                  │
                                  ├──낳음──▶ Decision 009 ──▶ Execution 013 ──▶ Outcome 014
                                  └──입력──◀ Artifact 016 (선행 Task의 산출물)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Goal](e001-goal.md) | Task는 정확히 하나의 Goal에 기여한다 | `Goal 1:1..N Task` |
| [Intent](e002-intent.md) | Selected Intent가 Task로 전개된다 | `Intent 1:1..N Task` |
| [Plan](e008-plan.md) | Task는 정확히 하나의 Plan에 속한다 (Rule T-006) | `Plan 1:1..N Task` |
| [Task Graph](e005a-task-graph.md) | Task 간 의존 구조 | `Task N:M Task` (DAG) |
| [Capability](e006-capability.md) | Task는 Capability를 **요구**한다 | `Task N:M Capability` |
| [Resource](e007-resource.md) | Task는 Resource를 직접 지정하지 않는다 | **직접 관계 없음** (INV-T-02) |
| [Decision](e009-decision.md) | Resource 배정의 기록 | `Task 1:0..N Decision` |
| [Execution](e013-execution.md) | 재시도마다 새 Execution | `Task 1:0..N Execution` |
| [Artifact](e016-artifact.md) | 선행 Task의 산출물이 입력이 된다 | `Artifact N:M Task` |
| [Constraint](e004-constraint.md) | Goal의 Constraint가 Task로 상속·전파된다 | `Constraint N:M Task` |
| [Assumption](e017-assumption.md) | Task 수준 가정을 가질 수 있다 | `Task 1:0..N Assumption` |
| [Workflow](e022-workflow.md) | Workflow의 step이 Task로 전개된다 | `Workflow 1:N Task` (인스턴스 경유) |
| [Evaluation](e015-evaluation.md) | verdict가 Task 상태를 전이시킨다 | `Task 1:0..N Evaluation` |

---

## 8. Canonical Representation

모든 Task는 내부적으로 동일한 구조를 가진다.

```json
{
  "id": "task_004",
  "goal_id": "goal_001",
  "plan_id": "plan_014",
  "objective": "인스타그램 광고 카피 3종 작성",
  "required_capabilities": [
    "language.generation.copywriting",
    "analysis.audience"
  ],
  "expected_output": "카피 3종 + 각 카피의 타겟 근거",
  "task_type": "Creation",
  "dependencies": ["task_003"],
  "execution_mode": "sequential",
  "priority": "High",
  "constraints": ["건당 비용 5,000원 이하", "24시간 이내"],
  "irreversible": false,
  "retry_policy": { "max_retries": 2, "on_failure": "reassign" },
  "state": "Pending"
}
```

비가역 Task는 다음과 같다.

```json
{
  "id": "task_010",
  "goal_id": "goal_001",
  "plan_id": "plan_014",
  "objective": "윈터캠프 인스타그램 캠페인 본 집행",
  "required_capabilities": ["advertising.campaign_execution"],
  "expected_output": "집행된 캠페인 + 일 단위 지표 수집 설정",
  "task_type": "Automation",
  "dependencies": ["task_006"],
  "execution_mode": "sequential",
  "priority": "High",
  "constraints": ["총 집행액 2,850,000 KRW 이하"],
  "irreversible": true,
  "retry_policy": { "max_retries": 0, "on_failure": "escalate" },
  "state": "Pending"
}
```

`irreversible: true`이므로 `max_retries: 0`이다. **되돌릴 수 없는 작업은 자동 재시도하지 않는다.**

**이 구조만 Runtime으로 전달된다.**

기계가 읽을 수 있는 스키마: [`task.schema.json`](../intent-os-spec/schemas/task.schema.json)

---

## 9. Validation Rules

Planner가 생성한 Task는 Runtime에 전달되기 전에 검증된다.

```
Task 후보
  ↓
Goal 연결 확인 (Rule T-005, INV-T-01)
  ↓
Plan 소속 확인 (Rule T-006, INV-P-07)
  ↓
Resource/Tool 이름 검출 (Rule T-004, INV-T-02)
  ── 검출 시 → Capability로 치환. 치환 불가면 반려
  ↓
Required Capabilities 확인 (Rule T-003)
  ├── 없으면 → Capability 추론
  ├── Taxonomy 정규화 (e006a §9.2) — Alias 해소
  └── 미등록 이름 → Proposed 노드 제안 + 반려
  ↓
Expected Output 확인 (Rule T-002) ── 없으면 Planner에 반려
  ↓
크기 기준 검사 (§9.1) ── 초과 시 재분해
  ↓
irreversible 판정
  └── true면 Policy 승인 게이트 필수 표시 (INV-T-08)
  ↓
retry_policy 확인 (Rule T-007)
  └── irreversible이면 max_retries = 0 강제
  ↓
Task Graph 순환 검사 (INV-T-05) ── 순환 시 Planner에 반려
  ↓
Canonical Task 생성 → Event 발행 (task.created)
```

### 9.1 Task Decomposition

Goal은 직접 실행되지 않는다. **Planner가 Goal을 Task로 분해한다.**

```
Goal: 윈터캠프 100명 모집
  ↓ Decomposition
T1  시장 조사
T2  경쟁 분석            (T1 의존)
T3  타겟 분석
T4  광고 카피 작성        (T3 의존)
T5  랜딩페이지 개선       (T2, T4 의존)
T6  광고 집행            (T4 의존)
T7  성과 분석            (T5, T6 의존)
```

#### 분해 규칙

1. **각 Task는 Rule T-001~T-007을 만족할 때까지 분해한다.**
2. **분해 결과의 합집합이 Goal 달성을 커버해야 한다.** 빠진 영역이 있으면 Planner는 Task를 추가한다.
3. **Task 간 중복 작업은 제거한다.** 두 Task가 같은 산출물을 만들면 하나로 합치고 의존 관계로 연결한다.
4. **분해는 재귀적이다.** Task가 아래 크기 기준을 넘으면 Sub-Task로 다시 분해한다.

#### 크기 기준 — 더 분해해야 하는가?

다음 중 하나라도 해당되면 **더 분해한다.**

| 판정 질문 | 예 |
|---|---|
| 서로 다른 Capability 도메인을 3개 이상 요구하는가? | `조사 + 카피 작성 + 디자인` → 3개 Task로 분리 |
| Expected Output이 2개 이상인가? | `비교표와 광고 시안` → 분리 |
| 단일 Resource가 처리하기 어려운가? | 검색과 장문 작성을 동시에 요구 → 분리 |
| 실패 시 부분 재시도가 필요한가? | 카피만 다시 쓰면 되는데 조사까지 다시 하게 되는 구조 → 분리 |
| 가역 작업과 비가역 작업이 섞여 있는가? | `카피 작성 + 광고 집행` → **반드시 분리** |

마지막 항목이 가장 중요하다. 가역과 비가역이 한 Task에 있으면 **재시도가 불가능해진다** — 카피를 다시 쓰려면 광고를 다시 집행해야 하기 때문이다.

반대로, 다음이면 **분해를 멈춘다.**

- 단일 Capability 집합으로 수행 가능하다.
- Expected Output이 하나다.
- 더 쪼개면 조율 비용이 실행 비용보다 커진다.

### 9.2 Task Graph 구조 검증

의존 구조·임계 경로·SPOF·재계획 시 보존 규칙은 별도 명세가 다룬다.

→ **[Entity 005-A: Task Graph](e005a-task-graph.md)**

---

## 10. Examples

### 예시 1 — 표준 Creation Task

§8의 Canonical `task_004`가 그대로 이 사례다.

```
task_004  인스타그램 광고 카피 3종 작성
  required: language.generation.copywriting + analysis.audience
  depends:  task_003 (타겟 분석)
  expected: 카피 3종 + 타겟 근거
  ↓ Decision dec_101 → Claude 선택
  ↓ Execution exe_220 → Completed (1,820ms / 0.42 USD)
  ↓ Outcome out_331 → succeeded, art_450
  ↓ Evaluation eva_512 → accept (composite 0.91)
task_004 → Evaluated
```

### 예시 2 — 분해가 필요한 Task

```
❌ task_x  "윈터캠프 마케팅 준비"
   required_capabilities: [research.web, analysis.audience,
                           language.generation.copywriting, creation.image,
                           advertising.campaign_execution]
   expected_output: "조사 결과, 카피, 이미지, 집행된 캠페인"
```

크기 기준 판정:

| 질문 | 판정 |
|---|---|
| Capability 도메인 3개 이상? | ✅ research / analysis / language / creation / advertising = 5개 |
| Expected Output 2개 이상? | ✅ 4개 |
| 가역·비가역 혼재? | ✅ 카피 작성(가역) + 광고 집행(비가역) |

→ **분해 필수.** 5개 Task로 나뉜다.

### 예시 3 — 실패 후 Resource 재선택

```
task_004  Pending → Assigned (dec_100: GPT)
   ↓
exe_219  Failed  failure_class: resource_unavailable (429)
   ↓ §6.1: 같은 Resource로 재시도
task_004  Pending → Assigned (dec_100 유지)
   ↓
exe_220b Failed  failure_class: resource_incapable (품질 0.51)
   ↓ §6.1: 다른 Resource 선택 필요
task_004  Pending → Assigned (dec_101: Claude)   ← 새 Decision
   ↓
exe_221  Completed
task_004  Completed → Evaluated
```

`attempt`는 3이지만 Decision은 2개다. **failure_class가 재시도 전략을 갈랐다.**

### 예시 4 — 비가역 Task의 차단

```
task_010  광고 본 집행  irreversible: true
   ↓ Execution 생성 시도
INV-T-08 검사
  ├── pol_012 (고액 실행 승인 필요) → require_approval
  └── rsk_031 (Critical, 미해결) → INV-RSK-07 위반
   ↓
❌ Execution 생성 차단
Event: policy.violated + approval.requested
   ↓ 대표 승인 + rsk_031 대응 완료 (파일럿 선행)
   ↓
✅ Execution 생성 허용
```

### 예시 5 — Blocked 전파

```
task_004 (카피 작성)  Aborted  (재시도 소진, INV-T-07)
   ↓ 하류 도달 집합 계산 (e005a §9.3)
task_005 (랜딩 개선)  → Blocked
task_006 (광고 집행)  → Blocked
task_007 (성과 분석)  → Blocked
   ↓
Blocked 집합이 Goal 달성에 필수인가 → Yes
   ↓
plan_014 → Suspended, Replanning 트리거
```

**상류로는 전파되지 않는다.** task_003(타겟 분석)의 결과는 여전히 유효하고, 재계획에서 Preserved된다.

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **하나의 Task가 두 Goal에 기여** | 허용하지 않는다. `goal_id`는 단수다. 두 Goal이 같은 작업을 필요로 하면 각각 Task를 만들고, 결과는 [Artifact](e016-artifact.md) 참조로 공유한다 |
| **Expected Output이 나왔는데 품질 미달** | `Completed → Evaluated`로 가되 verdict가 `reject`면 `Failed`로 전이한다. Completed는 산출 여부만 본다 |
| **선행 Task가 partial로 끝남** | `Completed`로 간주하고 하류를 진행한다. 단 하류 Task의 입력이 부족하면 `input_insufficient`로 실패한다. **partial을 자동으로 실패 처리하지 않는다** — 2/3만 있어도 진행 가능한 경우가 있다 |
| **재시도 중 Plan이 바뀜** | 기존 Execution 체인은 `Aborted`. 새 Plan에서 동일 Task로 판정되면(objective+capabilities+output 일치) Preserved되고, 아니면 새 Task가 생성된다([e005a §9.4.2](e005a-task-graph.md)) |
| **Capability를 제공하는 Resource가 없음** | Task 생성은 허용하되 Plan Validation에서 반려된다([e008 §9](e008-plan.md)). 실행 시점에 발견하면 이미 늦다 |
| **conditional Task의 조건이 거짓** | 실행하지 않고 `Aborted`로 종료한다. `Blocked`가 아니다 — 막힌 것이 아니라 필요 없어진 것이다. 하류에 전파하지 않는다 |
| **Task 하나에 Execution이 10개 이상** | 재시도 폭주 신호다. INV-T-07이 max_retries로 막지만, `collaborative`/`shadow` 모드는 예외이므로 별도 상한이 필요하다 |
| **irreversible Task가 partial로 끝남** | 가장 위험한 경우다. 광고 절반이 집행된 상태다. 재시도하지 않고 즉시 `escalate`한다. 사람이 외부 상태를 확인해야 한다([e024 §11](e024-tool.md)) |
| **선행이 없고 하류도 없는 고립 Task** | `dependencies: []`이고 아무도 참조하지 않는 것은 정상이다(단독 Task). 그러나 `goal_id`가 없으면 INV-T-01 위반으로 격리된다 |
| **state는 Completed인데 Outcome이 없음** | [INV-04](e000a-entity-relationships.md) 위반이다. Runtime이 최소 Outcome을 자동 생성하고 정합성 경보를 발행한다 |

---

## 12. Open Issues (v2.0)

### ✅ v1.0에서 해소된 항목

| v1.0 Open Issue | 해소 |
|---|---|
| Task Graph는 별도 명세가 필요한가 | [Entity 005-A](e005a-task-graph.md) 신설. 임계 경로·SPOF·실패 전파 정의 |
| Dynamic Planning 시 Task Graph의 부분 재생성 규칙 | [e005a §9.4](e005a-task-graph.md)의 Graph Diff (Preserved/Invalidated/Removed/Added) |
| Retry Policy의 비용 상한 (재시도 폭주 방지) | INV-T-07 + `irreversible`이면 `max_retries: 0` 강제 |
| Task 수준 Constraint의 상속 규칙 | [Constraint](e004-constraint.md)의 상속·전파 규칙으로 이관 |

### Task 우선순위 계산식

`priority`가 현재 High/Medium/Low의 열거값이다. Goal Score([e001a §10](e001a-goal-graph.md))와 연동한 정량 계산식이 없다. [Task Graph §9.2](e005a-task-graph.md)의 Ready 목록 정렬 기준(임계 경로 → Goal Score → SPOF)과 통합해야 한다.

### conditional 모드의 조건 표현 문법

`IF 전환율 < 목표` 같은 서술을 기계가 평가할 수 있는 형식으로 정의해야 한다. [Policy](e019-policy.md)의 `condition`, [Workflow](e022-workflow.md)의 `condition`과 **동일한 표현식 언어를 공유해야 한다.**

### Goal Propagation의 Task 전파

Goal의 목표치나 우선순위가 바뀌었을 때 이미 생성된 Task에 어떻게 반영되는가. 현재는 Replanning으로 전체가 다시 만들어지는 것을 전제하지만, 경미한 변경까지 재계획하는 것은 과하다.

### 앞으로 보강해야 할 항목

- Task 우선순위 계산식 (Goal Score 연동)
- 조건 표현식 언어 (Policy·Workflow와 공유)
- `collaborative` / `shadow` 모드의 Execution 개수 상한
- 실제 예시 30~50개
