# Entity 008: Plan

- **Version:** v2.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Plan is an executable blueprint produced by the Planner that transforms a Goal Graph into a structured set of Tasks, dependencies, resource requirements, assumptions, and risks.**

> Plan은 Planner가 Goal Graph를 입력으로 받아 생성한, Task·의존 구조·자원 요구·가정·위험을 포함하는 **실행 청사진**이다.

여기서 중요한 단어는 **산출물**이다.

Plan은 "계획을 세우는 행위"가 아니라, 그 행위가 만들어낸 **결과물 객체**이다.

### 1.1 Plan은 어디서 오는가 — 컴파일러 비유

```
Goal Graph            (Source Code)
  ↓
Planner               (Compiler)
  ↓
Plan                  (Object Code)
  ↓
Runtime Engine        (Loader / Runtime)
```

Planner는 Goal 하나를 보고 계획을 세우지 않는다. **[Goal Graph](e001a-goal-graph.md) 전체를 입력으로 받아** 목표 간 의존성·충돌·우선순위를 함께 고려한 Plan을 생성한다.

| 컴파일러 세계 | Intent OS |
|---|---|
| Source Code | Goal Graph |
| Compiler | Planner |
| Object Code | Plan (+ [Task Graph](e005a-task-graph.md)) |
| Loader/Runtime | Runtime Engine ([Volume 3](../v3-runtime.md)) |

---

## 2. Plan은 무엇이 아닌가?

이게 정의보다 훨씬 중요하다.

### Plan은 Planning이 아니다

Planning은 **Process**(시스템이 수행하는 것)이고, Plan은 그 Process가 생성한 **Entity**(시스템에 존재하는 것)이다.

| 분류 | 이름 | 의미 |
|---|---|---|
| **Process** | Planning | Goal Graph를 분석해 실행 청사진을 만드는 행위 |
| **Entity** | Plan | Planning의 산출물. 저장·버전 관리·비교 가능한 객체 |
| **Runtime State** | `Plan.status` | Plan을 실행하는 도중의 진행 상태 |

❌ `Planner가 지금 계획 중` — 이건 Plan이 아니다. Planning이라는 Process의 진행 상태다.

### Plan은 Goal이 아니다

❌ `학생 100명 모집` — [Goal](e001-goal.md)이다. Plan은 그 Goal을 **어떻게** 달성할지의 청사진이다.

### Plan은 Task가 아니다

❌ `인스타그램 광고 집행` — [Task](e005-task.md) 하나다. Plan은 Task들의 **집합 + 의존 구조 + 가정 + 위험**이다.

### Plan은 Workflow가 아니다

❌ `학원 시즌 캠페인은 조사 → 카피 → 파일럿 → 본 집행 순으로 흐른다` — 이건 [Workflow](e022-workflow.md)다.

| | Plan | Workflow |
|---|---|---|
| 소속 | 특정 Goal | Goal 독립 |
| 수명 | Goal이 끝나면 종료 | 영구. 버전만 올라간다 |
| 재사용 | 불가 | 가능 |
| 관계 | Workflow의 **인스턴스** | Plan의 **템플릿** |

Plan은 Workflow를 인스턴스화한 결과일 수 있지만, Workflow 없이 만들어지는 Plan도 있다([e022 Rule WFL-008](e022-workflow.md)).

### Plan은 Task Graph가 아니다

❌ `T3 → T5 → T7 의존 구조` — 이건 [Task Graph](e005a-task-graph.md)(Entity 005-A)다.

Task Graph는 Plan의 **구성 요소**다. `Plan 1:1 Task Graph`이며, Plan은 그 위에 비용·기간·성공 확률·가정·위험·대안을 더한 것이다.

### Plan은 Prompt Chain이 아니다

❌ `프롬프트 A → 프롬프트 B → 프롬프트 C` — 이건 실행 스크립트일 뿐이다. Plan은 비용·리스크·대안까지 포함한다.

---

## 3. Design Principles

### Rule P-001 — 정확히 하나의 Goal Graph(부분 그래프 포함)에서 파생되어야 한다

모든 Plan은 `source_goal_ids`로 기원을 추적할 수 있어야 한다. 기원 없는 Plan은 시스템이 관리하지 않는다.

### Rule P-002 — Task 의존 구조는 DAG여야 한다

Goal Graph와 동일하게 순환 의존(`A → B → A`)은 허용하지 않는다. 반복 실행이 필요하면 [Workflow](e022-workflow.md)의 명시적 `loop`로 표현한다([INV-08](e000a-entity-relationships.md)).

### Rule P-003 — 예상 비용과 예상 시간이 존재해야 한다

- ✅ `예상 비용 280만원 / 예상 기간 6주`
- ❌ `일단 해보자` — 추정 없는 Plan은 Draft를 벗어날 수 없다.

### Rule P-004 — 가정을 Assumption Entity로 명시해야 한다

Plan은 가정 위에 세워진다. **v2.0에서 가정은 문자열이 아니라 [Assumption](e017-assumption.md) Entity 참조다.**

```
v1.0  "assumptions": ["광고 예산 300만원 유지"]        ← 검증 불가능한 문자열
v2.0  "assumption_ids": ["asm_012"]                   ← 반증 조건·검증 주기·조치를 갖는 Entity
```

문자열로는 "누가 언제 어떻게 확인하는가"를 담을 수 없다. 깨진 가정을 방치하면 [INV-10](e000a-entity-relationships.md) 위반이다.

### Rule P-005 — Resource를 확정하지 않는다

Plan은 Task별 **Capability 요구**까지만 기술한다. 어떤 Resource를 쓸지는 Decision Engine이 결정하고, 그 기록은 [Decision](e009-decision.md)이다([INV-09](e000a-entity-relationships.md) Layer Isolation).

- ❌ `Task 3: Claude로 광고 카피 작성`
- ✅ `Task 3: 광고 카피 작성 (required: language.generation.copywriting)`

### Rule P-006 — Active Plan은 Goal당 동시에 하나만 존재한다

같은 Goal에 대해 여러 버전의 Plan이 존재할 수 있지만, `Active` 상태는 항상 하나다. 나머지는 `Superseded`가 된다([INV-14](e000a-entity-relationships.md)).

### Rule P-007 — Risk를 식별해야 한다

Severity가 High 이상인 [Risk](e018-risk.md)에 대응 계획이 없으면 Plan은 `Active`가 될 수 없다([INV-RSK-02](e018-risk.md)). Risk 식별 절차는 [e018 §9.1](e018-risk.md)이 규정한다.

### Rule P-008 — 수정하지 않고 새 버전을 만든다

Plan은 불변이 아니지만 **덮어쓰지 않는다.** 변경은 항상 새 버전이며, 이전 버전은 `Superseded`로 보존된다(§6.1).

---

## 4. Attributes

```
Plan
├── Identity
│   ├── plan_id
│   ├── version
│   └── source_goal_ids
├── Structure
│   ├── tasks[]
│   ├── task_graph_id
│   └── workflow_id
├── Estimation
│   ├── estimated_cost
│   ├── estimated_duration
│   ├── expected_success_probability
│   ├── risk_level
│   └── constraint_margin
├── Governance
│   ├── assumption_ids[]
│   ├── risk_ids[]
│   └── constraint_ids[]
├── Alternatives
│   └── alternative_plan_ids[]
└── Status
    ├── status
    ├── supersedes
    └── abort_reason
```

| 속성 | 의미 | 예 |
|---|---|---|
| **plan_id / version** | 식별자와 버전 | `plan_014`, `v2` |
| **source_goal_ids** | 어떤 Goal에서 파생되었는가 | `["goal_001"]` |
| **tasks** | 실행 단위 목록 | 시장 조사, 광고 카피 작성, … |
| **task_graph_id** | 의존 구조 ([Entity 005-A](e005a-task-graph.md)) | `tg_014` |
| **workflow_id** | 인스턴스화한 Workflow | `wf_seasonal_campaign@2.1` 또는 `null` |
| **estimated_cost** | 예상 비용 | `2,800,000 KRW` |
| **estimated_duration** | 예상 기간 | `6주` |
| **expected_success_probability** | 예상 성공 확률 | `0.82` |
| **risk_level** | 종합 리스크 | Low / Medium / High |
| **constraint_margin** | 제약 대비 여유 | 예산 여유 20만원, 기간 여유 1주 |
| **assumption_ids** | 전제 ([Entity 017](e017-assumption.md)) | `["asm_012", "asm_020"]` |
| **risk_ids** | 식별된 위험 ([Entity 018](e018-risk.md)) | `["rsk_007", "rsk_031"]` |
| **constraint_ids** | 적용 제약 ([Entity 004](e004-constraint.md)) | `["cn_003"]` |
| **alternative_plan_ids** | 고려된 대안 Plan | `["plan_014_alt1"]` |
| **status** | Plan의 상태 (§6) | Active |
| **supersedes** | 대체한 이전 버전 | `plan_014@1` |

### 4.1 Plan Quality Metrics

Planner는 Plan을 하나만 만들지 않는다. 후보 Plan들을 품질 지표로 비교하고, 최종 선택은 [Plan Selection Decision](e009-decision.md)으로 기록된다.

| 지표 | 의미 | 예 |
|---|---|---|
| **Expected Success Probability** | Goal 달성 예상 확률 | 0.82 |
| **Estimated Cost** | 총 예상 비용 | 280만원 |
| **Estimated Duration** | 총 예상 기간 | 6주 |
| **Risk Level** | 가정 취약성 + 실행 불확실성 | Medium |
| **Constraint Margin** | 제약 대비 여유 | 예산 여유 20만원, 기간 여유 1주 |

**Constraint Margin이 가장 실용적인 지표다.** 여유가 20% 미만인 항목은 [Risk](e018-risk.md) 자동 식별의 입력이 된다([e018 §9.1](e018-risk.md) ④).

---

## 5. Invariants

### INV-P-01 — Goal당 Active Plan은 최대 1개다

[INV-14](e000a-entity-relationships.md)의 Plan 측 표현이다.

| | |
|---|---|
| **위반 시** | 가장 최근 버전만 남기고 나머지를 `Superseded`로 강제 전이 |
| **근거** | 동시에 두 계획이 살아 있으면 Task Graph가 충돌하고 예산이 이중 집행된다 |

### INV-P-02 — Task 의존 구조는 순환하지 않는다

| | |
|---|---|
| **위반 시** | Plan을 `Draft`에 묶어두고 순환 경로를 Planner에 반환 |
| **탐지** | Task Graph 생성 시 증분 순환 검사 ([INV-TG-01](e005a-task-graph.md)) |

### INV-P-03 — Invalidated Assumption을 가진 Plan은 Active일 수 없다

[INV-10](e000a-entity-relationships.md)의 Plan 측 표현이다.

| | |
|---|---|
| **위반 시** | Plan을 `Suspended`로 강제 전이하고 Replanning을 큐에 등록 |
| **근거** | 가정이 깨졌는데 계획이 그대로면 그 계획은 이미 틀린 계획이다 |

### INV-P-04 — 미대응 High/Critical Risk가 있으면 Active가 될 수 없다

| | |
|---|---|
| **위반 시** | `Approved` 전이를 차단하고 대응 계획 작성을 요구 ([INV-RSK-02](e018-risk.md)) |

### INV-P-05 — estimated_cost는 Hard Constraint를 초과할 수 없다

| | |
|---|---|
| **위반 시** | Plan을 `Draft`로 반려. Goal 목표치 조정 또는 대안 Plan을 요구 ([INV-07](e000a-entity-relationships.md)) |

### INV-P-06 — Superseded / Completed Plan은 수정되지 않는다

| | |
|---|---|
| **위반 시** | 저장 계층이 쓰기를 거부. 변경은 새 버전으로만 (Rule P-008) |
| **근거** | "그때 왜 그렇게 계획했는가"를 답할 수 없게 된다 |

### INV-P-07 — 모든 Task는 정확히 하나의 Plan에 속한다

| | |
|---|---|
| **위반 시** | Task 생성 거부 ([INV-TG-03](e005a-task-graph.md)). Plan 간 결과 재사용은 [Artifact](e016-artifact.md) 참조로 한다 |

### INV-P-08 — supersedes 체인은 순환하지 않으며 v1에 도달한다

| | |
|---|---|
| **위반 시** | 버전 체인 생성 거부. 계획 이력 추적이 불가능해진다 |

---

## 6. Lifecycle

```
Draft → Approved → Active → Completed
  ▲                  │
  │                  ├──→ Suspended ──→ Active
  │                  │        │
  └──────────────────┤        └──→ (Replanning) ──→ 새 버전 Active
                     ├──→ Superseded   (새 버전으로 대체)
                     └──→ Aborted      (Goal 취소/실패)
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Draft** | Planner가 생성했으나 아직 검증/승인 전 | 생성 |
| **Approved** | 검증 통과. 실행 대기 (High Impact는 Human 승인 포함) | §9 검증 통과 |
| **Active** | Runtime이 실행 중인 유일한 버전 | 실행 시작 |
| **Suspended** | 실행 중지. 재개 또는 재계획 대기 | 가정 무효화(INV-P-03), 예산 초과, Critical Risk 발생 |
| **Superseded** | Replanning으로 새 버전에 자리를 내줌. 기록은 보존 | 새 버전 Active |
| **Completed** | 모든 Task 완료, Goal 평가로 이관 | Task Graph Completed |
| **Aborted** | 실행 중단. 사유가 반드시 기록되어야 한다 | Goal 취소/실패 |

`Superseded`와 `Aborted`는 다르다. Superseded는 **Goal은 그대로, 방법만 교체**된 것이고, Aborted는 **Goal 자체가 취소되거나 실패**한 것이다.

### 6.1 Versioning

Plan은 수정하지 않는다. **새 버전을 만든다**(Rule P-008).

```
plan_014 v1 (Active)
  ↓  asm_012 Invalidated — 광고 예산 300만원 → 200만원
plan_014 v1 (Superseded)
plan_014 v2 (Active)  ← 저비용 채널 중심으로 재컴파일
                        supersedes: "plan_014@1"
```

이 규칙이 중요한 이유:

1. **감사 가능성** — "그때 왜 그렇게 계획했는가"를 답할 수 있다.
2. **Learning Engine의 입력** — 버전 간 차이와 결과 차이가 학습 데이터가 된다.
3. **일관성** — [Decision 불변](e009-decision.md)·[Outcome 불변](e014-outcome.md)과 같은 원칙이다.

**새 버전은 이전 버전을 통째로 버리지 않는다.** 완료된 Task와 그 [Artifact](e016-artifact.md)는 [Task Graph Diff](e005a-task-graph.md)를 통해 승계된다(§10 예시 3).

### 6.2 Replanning Triggers

Plan은 고정되지 않는다([Volume 3 Stage 3 — Dynamic Planning](../v3-runtime.md)). 다음 조건에서 Planner가 새 버전을 생성한다.

| Trigger | 예 | 감지 주체 |
|---|---|---|
| **Assumption Invalidated** | 광고 예산 300만원 → 200만원 | [Assumption 검증기](e017-assumption.md) |
| **Risk Materialized** | 김 카피라이터 12월 불가용 확정 | [Risk 모니터](e018-risk.md) |
| **Goal Propagation** | 상위 Goal 변경이 하위 목표치를 바꿈 | [Goal Graph](e001a-goal-graph.md) |
| **Execution Deviation** | 예상 CTR 8% 대비 실제 3% — 허용 편차 초과 | [Outcome](e014-outcome.md) 집계 |
| **Resource Failure Cascade** | 대체 Resource로도 Task를 수행할 수 없음 | [Execution](e013-execution.md) 실패 누적 |
| **Low Confidence** | 남은 구간의 예상 성공 확률이 임계값 이하 | Planner |
| **User Request** | 사용자가 방향 전환을 요청 | [Session](e021-session.md) |

각 트리거는 [Event](e020-event.md)로 도착한다(`assumption.invalidated`, `risk.materialized`, `budget.exceeded` 등). **Planner는 이 Event들을 구독할 뿐 능동적으로 감시하지 않는다.**

Replanning은 전체 재컴파일이 아닐 수 있다. 영향받는 부분 그래프만 다시 계획하는 **Partial Replanning**이 기본이다(§12 Open Issue).

---

## 7. Relationships

```
Goal Graph 001-A ──입력──▶ Planner ──생성──▶ Plan 008
                                                │
              ┌─────────────────────────────────┼──────────────────────┐
              ▼                ▼                ▼                      ▼
        Task 005         Task Graph 005-A   Decision 009        Assumption 017
        Capability 006   Workflow 022       (Plan Selection)     Risk 018
                                                                 Constraint 004
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Goal](e001-goal.md) | Plan의 입력이자 존재 이유 | `Goal 1:0..N Plan` (Active는 1개, INV-P-01) |
| [Task](e005-task.md) | Plan의 구성 단위. Task는 Plan 밖에서 실행되지 않는다 | `Plan 1:1..N Task` |
| [Task Graph](e005a-task-graph.md) | Plan의 의존 구조 | `Plan 1:1 Task Graph` |
| [Workflow](e022-workflow.md) | Plan이 Workflow를 인스턴스화한다 | `Plan 1:0..1 Workflow` |
| [Capability](e006-capability.md) | Task별 요구 능력. Candidate Filtering 기준 | `Plan N:M Capability` |
| [Decision](e009-decision.md) | Plan Selection의 대상. 버전 교체는 Decision을 남긴다 | `Plan 1:0..N Decision` |
| [Constraint](e004-constraint.md) | 비용·기한 제약. Hard 위반은 Active를 막는다 | `Constraint N:M Plan` |
| [Assumption](e017-assumption.md) | Plan이 전제하는 가정. 깨지면 Suspended | `Plan 1:0..N Assumption` |
| [Risk](e018-risk.md) | Plan에 귀속된 위험 | `Plan 1:0..N Risk` |
| [Execution](e013-execution.md) | Plan의 Task가 실행된다 | `Plan 1:0..N Execution` (Task 경유) |
| [Feedback](e012-feedback.md) | 예측과 실제의 차이가 Planner 학습 데이터가 된다 | `Plan 1:0..N Feedback` |
| Plan | 버전 체인 | `Plan 1:0..1 Plan` (supersedes) |

---

## 8. Canonical Representation

```json
{
  "plan_id": "plan_014",
  "version": 2,
  "source_goal_ids": ["goal_001"],
  "status": "Active",
  "task_graph_id": "tg_014",
  "workflow_id": "wf_seasonal_campaign@2.1",
  "tasks": [
    {
      "task_id": "task_004",
      "name": "인스타그램 광고 카피 3종 작성",
      "required_capabilities": ["language.generation.copywriting", "analysis.audience"],
      "depends_on": ["task_003"]
    },
    {
      "task_id": "task_005",
      "name": "랜딩페이지 개선",
      "required_capabilities": ["code.frontend", "language.generation.copywriting"],
      "depends_on": ["task_002", "task_004"]
    }
  ],
  "estimated_cost": { "value": 2800000, "currency": "KRW" },
  "estimated_duration": { "value": 6, "unit": "week" },
  "expected_success_probability": 0.82,
  "risk_level": "Medium",
  "constraint_margin": { "budget_krw": 200000, "duration_week": 1 },
  "constraint_ids": ["cn_003"],
  "assumption_ids": ["asm_012", "asm_020", "asm_031"],
  "risk_ids": ["rsk_007", "rsk_031"],
  "alternative_plan_ids": ["plan_014_alt1"],
  "supersedes": "plan_014@1",
  "created_by": "planner:v2",
  "created_at": "2026-08-04T09:00:00Z"
}
```

**이 구조만 Runtime으로 전달된다.**

기계가 읽을 수 있는 스키마: [`plan.schema.json`](../intent-os-spec/schemas/plan.schema.json)

> **v1.0 → v2.0 필드 변경:** `assumptions`(문자열 배열)가 `assumption_ids`([Assumption](e017-assumption.md) 참조)로 대체되었다. `risk_ids`, `constraint_ids`, `task_graph_id`, `workflow_id`가 추가되었다. 문자열 가정은 검증 주기도 조치도 담을 수 없어 [INV-10](e000a-entity-relationships.md)을 만족시킬 수 없었다.

---

## 9. Validation Rules

Plan이 `Draft → Approved`로 넘어가려면 다음 검증을 통과해야 한다.

```
Plan (Draft)
  ↓
Source Goal 존재 확인 (Rule P-001)
  ↓
Task Graph 검증 ── e005a §9.1
  ├── 순환 검사 (INV-P-02)
  ├── 도달성 검사 (고아 Task 없음)
  └── SPOF 계산 → Risk 후보 생성
  ↓
Resource 식별자 검출 (Rule P-005) ── 검출 시 Capability로 치환 요구
  ↓
Capability 커버리지 확인
  ├── 모든 Task에 required_capabilities 존재
  └── 각 Capability를 제공하는 Active Resource가 존재하는가
      ── 없으면 반려 + escalate ([e006a §10 예시 4](e006a-capability-taxonomy.md))
  ↓
Constraint 검사 (INV-P-05)
  ├── estimated_cost ≤ 예산 Hard Constraint
  └── estimated_duration ≤ 마감
  ↓
Assumption 추출·검증 (Rule P-004) ── e017 §9.1
  ├── 7개 관점 질문으로 암묵적 가정 추출
  ├── 각 가정의 반증 조건이 관측 가능한가
  └── Invalidated 가정이 있는가 (INV-P-03) ── 있으면 반려
  ↓
Risk 식별 (Rule P-007) ── e018 §9.1
  ├── Assumption 부정형 → Risk 후보
  ├── SPOF → dependency Risk
  ├── 비가역 Task → irreversible Risk
  ├── Constraint 여유 < 20% → cost/schedule Risk
  └── severity High 이상에 response_plan 존재 (INV-P-04) ── 없으면 반려
  ↓
품질 지표 존재 확인 (Rule P-003)
  ↓
동일 Goal의 기존 Active Plan 확인 (INV-P-01)
  └── 존재 → 이 Plan Approved 시 기존을 Superseded로 전이 예약
  ↓
[High Impact?] ──Yes──→ Human Approval ([e009 §9.1](e009-decision.md))
  ↓ No
Approved → Event 발행 (plan.approved)
```

하나라도 실패하면 Plan은 Draft에 머물고, Planner에게 **결함 목록**이 반환된다.

---

## 10. Examples

### 예시 1 — 윈터캠프 Plan v1

Goal: `2026년 11월까지 윈터캠프 학생 100명 모집, 예산 300만원 이하`

```
Plan plan_014 (v1)                            Task Graph tg_014
│
├── T1 시장 조사       research.web             T1 ──▶ T2 ──┐
├── T2 경쟁 분석       analysis.competitor                  ├──▶ T5 ──┐
├── T3 타겟 분석       analysis.audience        T3 ──▶ T4 ──┤          ├──▶ T7
├── T4 광고 카피 작성   language.generation.copywriting      │          │
├── T5 랜딩 개선       code.frontend                        └──▶ T6 ──┘
├── T6 광고 집행       advertising.campaign_execution
└── T7 성과 분석       analysis.metrics

Estimated Cost:     280만원        Constraint Margin: 예산 20만원, 기간 1주
Estimated Duration: 6주
Success Prob.:      0.82
Risk Level:         Medium
Assumptions:        asm_012 (예산 유지) / asm_020 (김 카피라이터 가용) / asm_031 (Claude 성능 유지)
Risks:              rsk_007 (예산 삭감) / rsk_031 (브랜드 톤 부적합 카피로 비가역 집행)
Alternatives:       plan_014_alt1 (SEO 중심, 저비용·장기)
```

T1·T3은 선행이 없으므로 **병렬 실행 가능**하다([Task Graph §10 예시 1](e005a-task-graph.md)).

### 예시 2 — 대안 비교와 Plan Selection

| | plan_014 (광고 중심) | plan_014_alt1 (SEO 중심) |
|---|---|---|
| Success Prob. | 0.82 | 0.61 |
| Cost | 280만원 | 90만원 |
| Duration | 6주 | 14주 |
| Risk | Medium | Low |
| Constraint Margin | 예산 20만원 / 기간 1주 | 예산 210만원 / **기간 −7주** |

마감이 11월이므로 alt1은 **기간 여유가 음수**여서 탈락한다.

```
dec_090  decision_type: PlanSelection
         selection: plan_014
         alternatives_considered: [{ plan_014_alt1, utility 0.61 }]
         rationale: ["alt1은 예상 기간 14주로 마감(11/30)을 7주 초과"]
```

**좋은 Plan은 절대 순위가 아니라 제약 조건 위에서의 최적해다.**

### 예시 3 — Replanning (v1 → v2)

```
2026-08-15  evt_c04d8  assumption.invalidated (asm_012: 예산 300만 → 200만)
   ↓ Planner 구독
plan_014 v1 → Suspended  (INV-P-03)
   ↓ Task Graph Diff ([e005a §9.4.2](e005a-task-graph.md))
Preserved   T1 T2 T3 T4 T5 T7   (조사·분석·카피는 예산과 무관 — 약 12만원 보존)
Invalidated T6                  (광고 집행 예산 전제가 바뀜)
Added       T8 SEO 콘텐츠 제작 / T9 자연 유입 최적화
   ↓
plan_014 v2 생성
  estimated_cost: 195만원        constraint_margin: { budget_krw: 50000 }
  expected_success_probability: 0.68   ← 0.82에서 하락
  supersedes: "plan_014@1"
  assumption_ids: ["asm_020", "asm_031", "asm_045"]   ← asm_012 제거, 신규 asm_045 추가
   ↓
plan_014 v1 → Superseded
plan_014 v2 → Active
```

`expected_success_probability`가 0.82 → 0.68로 떨어진 것을 **숨기지 않는다.** 예산이 1/3 줄었는데 성공 확률이 그대로라면 그 추정이 틀린 것이다.

### 예시 4 — Constraint 위반으로 반려

```
plan_020 (Draft)  estimated_cost: 340만원
  ↓ §9 Constraint 검사
cn_003 (Hard): 광고비 집행 총액 ≤ 3,000,000 KRW
  ↓ INV-P-05 위반
Draft 유지. Planner에 결함 목록 반환:
  - "estimated_cost 3,400,000 > cn_003 상한 3,000,000 (초과 400,000)"
  - "권고: T6 광고 집행 예산 축소 또는 Goal 목표치 조정 제안 생성"
```

시스템이 **임의로 예산을 늘리지 않는다.** Hard Constraint는 협상 대상이 아니다.

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **Goal 하나에 Plan이 필요 없을 만큼 단순** | Task 1~2개짜리 Plan을 만든다. Plan을 건너뛰지 않는다 — Plan 없이 실행하면 [INV-P-07](e000a-entity-relationships.md)이 깨지고 비용 집계가 불가능해진다. Workflow는 생략 가능하다 |
| **Replanning 중에 또 다른 트리거 발생** | 진행 중인 Replanning에 흡수한다. 트리거마다 새 버전을 만들면 Replanning Storm이 된다. 감쇠 규칙은 §12 미해결 |
| **Preserved Task의 Artifact가 이미 Purged** | 해당 Task를 `Invalidated`로 재분류하고 재실행한다([e005a §11](e005a-task-graph.md)). Artifact 보존 기간과 재계획 가능 기간을 맞춰야 한다는 신호다 |
| **대안 Plan이 채택된 Plan보다 나중에 더 좋아짐** | 기존 Plan을 고치지 않는다. 대안을 새 버전으로 승격하고 `supersedes` 연결. Plan Selection Decision을 새로 남긴다 |
| **Plan은 Active인데 Goal이 Achieved** | Plan을 `Completed`로 전이한다. 남은 Task는 실행하지 않고 `Aborted` 처리하되 비용은 0이므로 손실이 없다 |
| **여러 Goal이 하나의 Plan을 공유** | 허용한다(`source_goal_ids`가 배열인 이유). 단 INV-P-01은 **각 Goal마다** 적용되므로, 그 Plan이 Superseded되면 관련 Goal 전부가 영향을 받는다 |
| **estimated_cost가 실제와 크게 다름** | Plan을 수정하지 않는다. 차이는 [Evaluation](e015-evaluation.md)의 `prediction_error`로 기록되고 Planner 추정 모델 보정에 쓰인다 |
| **Assumption이 하나도 추출되지 않음** | 추출 실패의 신호다. 모든 Plan에는 최소 하나의 가정이 있다(적어도 "필요한 Resource가 가용하다"). 경고를 발행하고 [e017 §9.1](e017-assumption.md)의 7개 관점 질문을 강제한다 |
| **Suspended 상태로 오래 방치** | 가정 무효화가 해소되지 않은 상태다. `absolute_timeout`을 두고 초과 시 `Aborted`로 전이하며 Goal 재검토를 요구한다 |
| **Workflow가 Deprecated되었는데 Plan은 Active** | 진행 중 Plan은 영향받지 않는다. Version Pinning으로 v2.1을 계속 사용한다([e022 §6.1](e022-workflow.md)) |

---

## 12. Open Issues (v2.0)

### ✅ v1.0에서 해소된 항목

| v1.0 Open Issue | 해소 |
|---|---|
| Assumption이 검사 가능한 형태여야 한다는 요구 | [Assumption Entity](e017-assumption.md) 신설. `assumption_ids` 참조로 전환 |
| Risk Level의 근거 | [Risk Entity](e018-risk.md) 신설. `risk_ids`와 severity 산출 규칙 정의 |
| Task 의존 구조의 상세 명세 | [Task Graph](e005a-task-graph.md)(Entity 005-A) 분리. Graph Diff로 재계획 보존 규칙 확정 |

### Partial Replanning의 경계 문제

부분 재계획 시 "영향받는 부분 그래프"를 어디까지로 볼 것인가. [Task Graph §9.4](e005a-task-graph.md)의 Graph Diff는 **전체 재생성 후 비교** 방식이다. 국소 재계획(Local Replanning)이 비용상 유리하지만 정합성 보장이 어렵다. 과도한 재계획(Replanning Storm)을 막는 감쇠 규칙도 필요하다.

### Plan 품질 지표의 산출 근거

Expected Success Probability는 초기에는 Rule + Benchmark 기반이고, 장기적으로는 Performance Prediction Engine([Volume 4-A §7](../v4a-decision-engine-detail.md))의 예측 모델을 공유해야 한다. 두 시스템의 예측 일관성 규칙이 미정이다.

### Alternative Plan의 보존 기간

탈락한 대안 Plan을 얼마나 오래 보존할 것인가. Learning 관점에서는 전부 보존이 이상적이지만 저장 비용과의 균형 규칙이 필요하다.

### Plan 예산과 Session 예산의 관계

`estimated_cost`는 Plan 전체의 예상이고 `Session.budget`은 한 번의 실행 단위 상한이다. 둘의 계층 관계(조직 → Goal → Plan → Session → Agent)가 정의되지 않았다. [e021 §12](e021-session.md)와 동일한 미결 항목이다.

### 앞으로 보강해야 할 항목

- Plan 형식 문법 (Formal Grammar)
- Partial Replanning 알고리즘 상세
- Plan 간 비교(diff) 표준 포맷
- 실제 예시 30~50개
