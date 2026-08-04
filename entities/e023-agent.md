# Entity 023: Agent

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Agent is an autonomous execution subject that pursues an assigned scope of work by selecting and using Resources, making bounded decisions, and reporting Outcomes to a principal.**

> Agent는 배정된 작업 범위를 스스로 추진하는 **자율적 실행 주체**이며, Resource를 선택·사용하고 제한된 범위에서 결정을 내리며 그 결과를 상위 주체에게 보고한다.

여기서 중요한 것은 **Resource를 사용한다(Uses Resources)** 는 점이다.

> **Agent는 Resource가 아니다. Resource를 쓰는 쪽이다.**

```
Agent            "이 Goal을 맡아라"를 받고 스스로 Task를 처리한다
  │ 사용
  ▼
Resource         Claude · 검색 API · 김 카피라이터
```

---

## 2. Agent는 무엇이 아닌가?

### Agent는 Resource가 아니다

❌ `Agent = 똑똑한 LLM`

| | Resource | Agent |
|---|---|---|
| 역할 | 능력을 제공한다 | 능력을 조합해 목적을 달성한다 |
| 결정 | 하지 않는다 | 범위 안에서 스스로 한다 |
| 호출 | 요청-응답 1회 | 여러 Execution을 연속 수행 |
| 예 | Claude 5 | 마케팅 담당 Agent |

### Resource Type `agent`와의 구분

[e007 §5](e007-resource.md)의 Resource Type 목록에는 `agent`가 있다. **모순처럼 보이지만 아니다.** 판별 기준은 하나다.

> **Intent OS가 그 결정 루프를 소유하는가?**

| | 소유한다 | 소유하지 않는다 |
|---|---|---|
| 분류 | **Agent Entity** (본 문서) | **Resource** (`type: agent`) |
| 내부 결정 | Intent OS의 [Decision](e009-decision.md)으로 기록된다 | 블랙박스. 기록 불가 |
| Policy | 모든 내부 결정에 적용된다 | 입출력 경계에서만 적용 |
| 예 | 마케팅 담당 Agent (본 시스템이 운영) | 외부 리서치 에이전트 제품 |

외부 에이전트 제품은 **내부를 볼 수 없으므로** Resource다. 감사할 수 없는 것을 Agent로 취급하면 [INV-02](e000a-entity-relationships.md)(No Unexplained Assignment)가 무너진다.

### Agent는 Task가 아니다

❌ `광고 카피 작성` — 이건 [Task](e005-task.md)다. Agent는 그 Task를 **처리하는 주체**다.

### Agent는 Session이 아니다

❌ `사용자가 오늘 연 작업 단위` — 이건 [Session](e021-session.md)이다.

Session이 **경계**라면 Agent는 **주체**다. 하나의 Session 안에 여러 Agent가 활동할 수 있고, 하나의 Agent가 여러 Session에 걸쳐 살아 있을 수도 있다.

### Agent는 인간이 아니다

❌ `김 카피라이터 = Human Agent`

김 카피라이터는 **Resource**(`type: human`)다. 그에게 Task를 배정하고 결과를 받는 것이지, 그가 Intent OS의 결정을 대행하는 것이 아니다.

단, 인간이 Intent OS 안에서 **결정 권한을 위임받아** 하위 Task를 스스로 배정한다면 그때는 Agent 역할을 겸한다. 두 역할은 별개로 기록한다.

### Agent는 자율성이 무제한인 존재가 아니다

❌ `Agent에게 맡기면 알아서 다 한다`

모든 Agent는 **권한 범위(scope)·자율성 수준·예산**을 갖는다. 이것이 없으면 Agent는 통제 불가능한 비용 발생 장치다.

---

## 3. Design Principles

### Rule AGT-001 — Agent는 권한 범위(Scope)를 가진다

무엇에 대해 결정할 수 있는지 명시한다.

```
scope: {
  goal_ids: ["goal_001"],
  allowed_capabilities: ["language.*", "analysis.*"],
  allowed_tools: ["tool_search", "tool_analytics"],
  forbidden: ["advertising.campaign_execution"]
}
```

범위 밖의 결정은 **상위에게 escalate**한다. 스스로 확장할 수 없다.

### Rule AGT-002 — Agent는 자율성 수준을 가진다

| Level | 이름 | 결정 권한 | 예 |
|---|---|---|---|
| **L0** | Suggest | 제안만. 실행은 인간이 | 카피 후보 제시 |
| **L1** | Execute-on-approval | 승인 후 실행 | 승인받은 Task만 수행 |
| **L2** | Execute-and-report | 스스로 실행하고 보고 | 조사·분석 Task 자율 수행 |
| **L3** | Delegate | 하위 Agent 생성·위임 가능 | 캠페인 전체 관리 |

**L3은 예산과 비가역 작업 금지가 함께 걸려야 한다.** 위임 권한과 비가역 권한을 동시에 주면 통제점이 사라진다.

### Rule AGT-003 — Agent의 모든 결정은 Decision을 남긴다

Agent가 Resource를 고르든 Task를 분해하든 [Decision](e009-decision.md)을 생성한다. [INV-02](e000a-entity-relationships.md)에 예외가 없다.

"Agent가 알아서 했다"는 설명이 아니다.

### Rule AGT-004 — Agent는 Policy를 우회할 수 없다

Agent가 만든 Decision과 Execution도 [Policy](e019-policy.md) 평가를 거친다. Agent에게 Policy 예외를 부여하려면 명시적 Exception이 필요하다([e019 Rule POL-007](e019-policy.md)).

### Rule AGT-005 — Agent는 예산을 가진다

`budget`이 없는 Agent는 생성할 수 없다. Session 예산과 별개로 Agent 자체의 상한을 둔다.

### Rule AGT-006 — Agent는 principal에게 보고한다

모든 Agent에는 상위 주체(인간 또는 다른 Agent)가 있다. 최상위 principal은 **반드시 인간**이다.

### Rule AGT-007 — 권한은 위임 시 확대될 수 없다 (단조 감소)

부모 Agent가 자식 Agent를 만들 때, 자식의 권한은 부모의 부분집합이어야 한다.

```
부모  L3, 예산 100,000원, capabilities: [language.*, analysis.*]
자식  L2, 예산  30,000원, capabilities: [language.*]         ✅
자식  L3, 예산 150,000원, capabilities: [language.*, advertising.*]  ❌
```

**이 규칙이 없으면 권한 확대(Privilege Escalation)가 가능해진다.**

### Rule AGT-008 — 위임 깊이에 상한이 있다

Agent 트리의 깊이는 제한된다(기본 3). 무한 위임은 비용 폭주와 책임 소재 상실을 낳는다.

---

## 4. Attributes

```
Agent
├── Identity
│   ├── agent_id
│   ├── name
│   ├── type
│   └── principal
├── Authority
│   ├── autonomy_level
│   ├── scope
│   ├── policy_scope[]
│   └── depth
├── Budget
│   ├── max_cost
│   ├── max_executions
│   └── consumed
├── Runtime
│   ├── session_id
│   ├── assigned_scope        (goal_ids / task_ids)
│   ├── children[]
│   └── reasoning_resource_id
├── Reporting
│   ├── report_interval
│   └── last_report_at
└── Status
    └── status
```

| 속성 | 의미 | 예 |
|---|---|---|
| **agent_id** | 식별자 | `agent_marketing_01` |
| **type** | 분류 (§4.1) | `orchestrator` |
| **principal** | 상위 주체 (AGT-006) | `human:대표` |
| **autonomy_level** | 자율성 (§3 AGT-002) | `L2` |
| **scope** | 권한 범위 | §8 참조 |
| **policy_scope** | 적용 Policy | `["pol_007", "pol_012"]` |
| **depth** | 위임 깊이 | `1` |
| **max_cost** | 예산 상한 | `{ "amount": 100000, "currency": "KRW" }` |
| **consumed** | 소비 현황 | `{ "cost": 31200, "executions": 47 }` |
| **assigned_scope** | 맡은 작업 | `{ "goal_ids": ["goal_001"] }` |
| **children** | 하위 Agent | `["agent_copy_02"]` |
| **reasoning_resource_id** | Agent의 판단에 쓰는 Resource | `anthropic:claude-5` |
| **report_interval** | 보고 주기 | `PT1H` |
| **status** | 상태 (§6) | `Active` |

**`reasoning_resource_id`가 Agent와 Resource의 관계를 보여준다.** Agent는 판단을 위해 Resource를 쓴다. 그 Resource가 Agent인 것이 아니다.

### 4.1 Agent Types

```
Agent
├── planner       Goal을 Task로 분해하고 Plan을 만든다
├── executor      배정된 Task를 수행한다
├── evaluator     Outcome을 평가한다
├── monitor       지표를 감시하고 Event를 발행한다
└── orchestrator  다른 Agent를 조율한다 (L3 전용)
```

| Type | 자율성 상한 | 주 Capability | 예 |
|---|---|---|---|
| `planner` | L2 | `reasoning.planning` | 윈터캠프 Plan 수립 |
| `executor` | L2 | 도메인별 | 카피 작성 Task 처리 |
| `evaluator` | L1 | `evaluation.*` | Outcome 4축 평가 |
| `monitor` | L2 | `analysis.metrics` | 예산 소진율 감시 |
| `orchestrator` | L3 | `reasoning.coordination` | 캠페인 전체 관리 |

**`evaluator`의 자율성이 L1로 제한되는 이유:** 평가자가 자신의 평가를 근거로 스스로 실행하면 자기 승인이 된다. 평가와 실행은 분리한다.

---

## 5. Invariants

### INV-AGT-01 — 모든 Agent는 principal을 가지며 최상위는 인간이다

| | |
|---|---|
| **위반 시** | 생성 거부. principal 사슬을 따라가면 반드시 인간에 도달해야 한다 |
| **근거** | 책임 소재가 시스템 안에서 끝나면 안 된다 |

### INV-AGT-02 — 자식 Agent의 권한은 부모의 부분집합이다

Rule AGT-007의 불변식 표현이다.

| | |
|---|---|
| **위반 시** | 자식 생성 거부. 권한 확대 시도를 `policy.violated` Event로 기록 |
| **탐지** | 생성 시 + 주기 스윕 (부모 권한 축소 시 자식이 초과하게 될 수 있다) |

### INV-AGT-03 — Agent의 예산 합은 부모 예산을 초과할 수 없다

$$\sum_{child} budget \leq budget_{parent}$$

| | |
|---|---|
| **위반 시** | 자식 예산 배분 거부 |

### INV-AGT-04 — 위임 깊이는 상한을 넘지 않는다

| | |
|---|---|
| **위반 시** | 자식 생성 거부. `escalate`로 전환 |

### INV-AGT-05 — Agent의 모든 Execution은 Decision을 갖는다

| | |
|---|---|
| **위반 시** | Execution 생성 차단 ([INV-02](e000a-entity-relationships.md)) |

### INV-AGT-06 — 종료된 Agent의 자식은 남아 있을 수 없다

| | |
|---|---|
| **위반 시** | 부모 종료 시 자식을 재귀적으로 종료한다. 고아 Agent는 예산을 태우며 아무에게도 보고하지 않는다 |

### INV-AGT-07 — L3 Agent는 비가역 작업을 직접 수행할 수 없다

| | |
|---|---|
| **위반 시** | Execution 차단. 비가역 작업은 인간 승인 또는 L2 이하 Agent를 통해서만 |
| **근거** | 위임 권한 + 비가역 권한의 결합을 막는다 (Rule AGT-002) |

---

## 6. Lifecycle

```
Provisioned → Active ──▶ Reporting ──▶ Active
                 │                        │
                 ├──▶ Suspended ──────────┘
                 │
                 ├──▶ Completed
                 └──▶ Terminated
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Provisioned** | 생성됨. scope·예산 확정 | principal이 생성 |
| **Active** | 작업 수행 중 | 첫 Task 배정 |
| **Reporting** | 보고 생성 중 | `report_interval` 도달 |
| **Suspended** | 일시 중지 | 예산 초과, 승인 대기, 범위 밖 판단 필요 |
| **Completed** | 배정 작업 완료 | `assigned_scope` 전부 완료 |
| **Terminated** | 강제 종료 | principal의 종료, Policy 위반, 부모 종료 |

### 6.1 Escalation

Agent가 스스로 처리할 수 없을 때의 경로다.

```
판단 필요 상황
  ↓
scope 안인가?
  ├── Yes → autonomy_level로 처리 가능한가?
  │          ├── Yes → 스스로 Decision 생성 + 실행
  │          └── No  → principal에게 승인 요청 → Suspended
  └── No  → principal에게 escalate → Suspended
             ↓
        principal이 판단
        ├── scope 확장 승인 → 새 scope로 Active 재개
        ├── 직접 처리       → Agent는 해당 Task 제외하고 재개
        └── 거부            → Agent는 해당 경로를 포기하고 재개
```

**Agent는 스스로 scope를 넓히지 않는다.** 이것이 AGT-001의 실질적 의미다.

---

## 7. Relationships

```
human (principal) ──▶ Agent 023 ──▶ Agent 023 (자식, 권한 부분집합)
                          │
                          ├──사용──▶ Resource 007 / Tool 024
                          ├──생성──▶ Decision 009 ──▶ Execution 013
                          ├──소속──▶ Session 021
                          └──지배──▶ Policy 019
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Resource](e007-resource.md) | Agent가 Resource를 **사용한다** | `Agent N:M Resource` |
| [Tool](e024-tool.md) | Agent가 Tool을 호출한다 | `Agent N:M Tool` |
| [Decision](e009-decision.md) | Agent의 모든 결정이 기록된다 | `Agent 1:0..N Decision` |
| [Execution](e013-execution.md) | Agent가 수행 주체일 때 기록된다 | `Agent 1:0..N Execution` |
| [Session](e021-session.md) | Agent는 Session 안에서 활동한다 | `Session 1:0..N Agent` |
| [Policy](e019-policy.md) | Agent도 Policy를 우회할 수 없다 | `Policy 1:N Agent` |
| Agent | 위임 관계 (권한 단조 감소) | `Agent 1:0..N Agent` |
| [Goal](e001-goal.md) | `assigned_scope`로 배정받는다 | `Agent N:M Goal` |

---

## 8. Canonical Representation

```json
{
  "agent_id": "agent_marketing_01",
  "name": "윈터캠프 마케팅 담당",
  "type": "orchestrator",
  "principal": "human:대표",
  "autonomy_level": "L3",
  "depth": 1,
  "scope": {
    "goal_ids": ["goal_001"],
    "allowed_capabilities": ["language.*", "analysis.*", "research.*"],
    "allowed_tools": ["tool_search", "tool_analytics", "tool_crm_read"],
    "forbidden_capabilities": ["advertising.campaign_execution"],
    "max_delegation_depth": 3
  },
  "policy_scope": ["pol_007", "pol_012", "pol_015"],
  "budget": {
    "max_cost": { "amount": 100000, "currency": "KRW" },
    "max_executions": 300
  },
  "consumed": {
    "cost": { "amount": 31200, "currency": "KRW" },
    "executions": 47
  },
  "session_id": "ses_057",
  "assigned_scope": { "goal_ids": ["goal_001"] },
  "children": ["agent_copy_02"],
  "reasoning_resource_id": "anthropic:claude-5",
  "report_interval": "PT1H",
  "last_report_at": "2026-08-04T10:00:00Z",
  "status": "Active"
}
```

자식 Agent는 권한이 좁다.

```json
{
  "agent_id": "agent_copy_02",
  "name": "카피 작성 담당",
  "type": "executor",
  "principal": "agent_marketing_01",
  "autonomy_level": "L2",
  "depth": 2,
  "scope": {
    "goal_ids": ["goal_001"],
    "allowed_capabilities": ["language.generation.copywriting", "analysis.audience"],
    "allowed_tools": [],
    "forbidden_capabilities": ["advertising.campaign_execution"],
    "max_delegation_depth": 3
  },
  "budget": { "max_cost": { "amount": 30000, "currency": "KRW" }, "max_executions": 60 },
  "assigned_scope": { "task_ids": ["task_004"] },
  "children": [],
  "reasoning_resource_id": "anthropic:claude-5",
  "status": "Active"
}
```

`allowed_capabilities`가 부모의 `language.*`보다 좁고(`language.generation.copywriting`), 예산도 부모의 30% 이내다(INV-AGT-02, 03).

기계가 읽을 수 있는 스키마: [`agent.schema.json`](../intent-os-spec/schemas/agent.schema.json)

---

## 9. Validation Rules

### 9.1 Agent 생성

```
Agent 생성 요청
  ↓
principal 존재 확인 (INV-AGT-01)
  ↓
principal 사슬을 따라 인간에 도달하는지 검사 ── 도달 불가 시 거부
  ↓
depth = principal.depth + 1
  ↓
depth ≤ max_delegation_depth 확인 (INV-AGT-04) ── 초과 시 거부
  ↓
scope 부분집합 검사 (INV-AGT-02)
  ├── allowed_capabilities ⊆ principal.allowed_capabilities
  ├── allowed_tools ⊆ principal.allowed_tools
  └── forbidden_capabilities ⊇ principal.forbidden_capabilities
  ── 위반 시 거부 + policy.violated Event
  ↓
autonomy_level ≤ principal.autonomy_level 확인
  ↓
type별 자율성 상한 검사 (§4.1) ── evaluator는 L1 초과 불가
  ↓
예산 검사 (INV-AGT-03)
  Σ(형제 Agent 예산) + 요청 예산 ≤ principal 예산
  ↓
L3 + 비가역 Capability 조합 검사 (INV-AGT-07) ── 있으면 거부
  ↓
policy_scope 상속
  ↓
Provisioned → Event 발행 (agent.provisioned)
```

### 9.2 Agent의 결정 검증

Agent가 Decision을 생성할 때마다 실행된다.

```
Decision 생성 요청 (agent_id 포함)
  ↓
Agent status = Active 확인
  ↓
Decision의 subject가 assigned_scope 안인가 ── 밖이면 escalate
  ↓
선택하려는 Resource의 Capability가 scope.allowed_capabilities 안인가
  ── 밖이면 escalate
  ↓
forbidden_capabilities와 교집합 검사 ── 있으면 거부 + Event
  ↓
autonomy_level 검사
  ├── L0 → Decision을 Proposed로만 생성. 실행 불가
  ├── L1 → 승인 요청 생성 → Suspended
  ├── L2 → Committed 생성 가능
  └── L3 → Committed 생성 + 자식 Agent 위임 가능
  ↓
예산 검사 (consumed + 예상 비용 ≤ max_cost) ── 초과 시 Suspended
  ↓
Policy 평가 (AGT-004) ── e019 §9.2
  ↓
Decision 생성 (decided_by: agent_id)
```

**`decided_by`에 Agent ID가 들어간다.** 나중에 "이 결정은 누가 했는가"에 Agent 단위로 답할 수 있어야 한다.

---

## 10. Examples

### 예시 1 — 위임 트리

```
human:대표                        (principal, 최상위)
└── agent_marketing_01  L3  100,000원  scope: goal_001 전체
    ├── agent_research_03  L2  20,000원  scope: research.*
    ├── agent_copy_02     L2  30,000원  scope: language.generation.copywriting
    └── agent_monitor_04  L2   5,000원  scope: analysis.metrics
                                          ────────
                                    자식 합계 55,000원 ≤ 100,000원  ✅
```

`advertising.campaign_execution`은 어느 Agent도 갖지 못한다. **광고 집행은 대표만 한다.**

### 예시 2 — Escalation

```
agent_copy_02  카피 3종 작성 중
  ↓
2회 재시도 후에도 composite 0.71 (임계 0.85 미달)
  ↓
판단: 인간 카피라이터에게 넘겨야 한다
  ↓
scope 검사: human Resource 사용은 allowed_capabilities에 있는가
  → language.generation.copywriting에 human:copywriter_kim이 매칭됨 ✅
  ↓
예산 검사: 50,000원 > 남은 예산 12,000원 ❌
  ↓
Suspended → principal(agent_marketing_01)에게 escalate
  ↓
agent_marketing_01: 예산 재배분 판단
  → 자기 예산에서 40,000원을 agent_copy_02로 이전
  → 단, 이것도 Decision으로 기록된다 (dec_180, type: BudgetReallocation)
  ↓
agent_copy_02 Active 재개
```

### 예시 3 — 권한 확대 시도 차단

```
agent_copy_02 (L2, capabilities: [language.generation.copywriting])
  ↓
자식 Agent 생성 시도
  requested: L2, capabilities: [language.*, advertising.campaign_execution]
  ↓
INV-AGT-02 검사
  advertising.campaign_execution ∉ 부모의 allowed_capabilities
  ↓
❌ 생성 거부
Event: policy.violated { agent: agent_copy_02, attempted: privilege_escalation }
```

### 예시 4 — Agent vs Resource type=agent

같은 "에이전트"라는 말이지만 다르게 취급된다.

```
① agent_research_03          Agent Entity
   Intent OS가 결정 루프를 소유
   내부 Decision 12건이 전부 기록됨
   Policy가 각 Decision에 적용됨

② external:deepresearch-x    Resource (type: agent)
   외부 제품. 블랙박스
   Decision 1건만 기록됨 ("이 Task에 external:deepresearch-x를 선택")
   내부에서 무엇을 했는지 모름
   Policy는 입력·출력 경계에서만 적용
```

②를 쓰려면 그 사실을 감수해야 한다. **감사 불가 구간이 생긴다는 것을 Decision의 rationale에 명시한다.**

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **부모 Agent가 종료되었는데 자식이 실행 중** | 자식을 재귀적으로 종료한다(INV-AGT-06). 진행 중 Execution은 완료시키고 새 Execution은 막는다 |
| **부모의 권한이 사후에 축소됨** | 자식이 부모의 부분집합이 아니게 된다. 주기 스윕에서 탐지하고 자식 권한을 자동 축소한다. 축소로 진행 불가해지면 `escalate` |
| **Agent가 Policy 예외를 요청** | Agent가 스스로 승인할 수 없다. principal 사슬을 따라 인간까지 올라간다 |
| **Agent가 무한 루프에 빠짐** | 예산(INV-AGT-03)과 `max_executions`가 최종 방어선이다. 추가로 `monitor` Agent가 동일 Task 반복을 감지해 Event를 발행한다 |
| **여러 Agent가 같은 Task를 처리** | [INV-EXE-03](e013-execution.md)이 막는다. Task 배정은 Decision을 통해서만 일어나며 중복 배정은 거부된다 |
| **L0 Agent가 실행을 시도** | Decision을 `Proposed`로만 만들 수 있고 `Committed` 전이가 차단된다. 인간이 승인하면 Decision의 `decided_by`는 Agent, 승인자는 별도 필드에 기록한다 |
| **Agent의 reasoning Resource가 Drift** | Agent의 판단 품질이 조용히 떨어진다. `resource.drift_detected` Event를 Agent 관리자가 구독하고, 필요 시 `reasoning_resource_id`를 교체한다 |
| **인간이 Agent 역할을 겸함** | 두 역할을 분리 기록한다. Resource로서의 `human:copywriter_kim`과 Agent로서의 `agent_human_kim`은 다른 식별자다 |
| **Agent가 자기 Outcome을 스스로 평가** | 금지한다. `evaluator` 타입 Agent를 분리하거나 자동 평가기를 쓴다. 자기 평가는 [Evaluation](e015-evaluation.md)의 신뢰성을 무너뜨린다 |

---

## 12. Open Issues (v1.0)

### Multi-Agent 협업의 조정 프로토콜

현재 명세는 **위임(계층)** 만 다룬다. 동등한 Agent 간의 협상·경매·합의(Contract Net, Consensus)는 정의되지 않았다. [Volume 4-A §10](../v4a-decision-engine-detail.md)의 Multi-Agent 실행과 통합이 필요하다.

### Agent의 학습과 개인화

같은 Agent가 반복 실행되며 축적한 [Memory](e010-memory.md)를 어떻게 소유하는가. Agent 종료 시 그 경험이 사라지면 안 되고, 그렇다고 Agent별로 격리하면 조직 전체가 학습하지 못한다.

### 자율성 수준의 동적 조정

성과가 좋은 Agent의 자율성을 자동으로 올리는 것이 자연스럽지만, 그 판단 자체가 중대한 결정이다. 승격 기준과 승인 주체가 미정이다.

### 외부 Agent의 부분 관측

Resource `type: agent`는 블랙박스이지만, 일부 제품은 중간 추론 과정을 노출한다. 부분적으로 관측 가능한 Agent를 어떻게 분류할지(Agent인가 Resource인가) 경계가 흐리다.

### 앞으로 보강해야 할 항목

- Agent 간 통신 프로토콜 (메시지 스키마)
- 자율성 수준별 감사 요구사항
- Agent 성능 프로파일 ([Resource Profile](e025-resource-profile.md)의 Agent 판)
- 실제 예시 30~50개
