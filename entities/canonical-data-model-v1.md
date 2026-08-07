# Entity 000-B: Canonical Data Model v1

- **Version:** v1.0 Draft
- **Status:** Normative Architecture
- **Last Updated:** 2026-08-07

---

## 0. Why This Document Exists

Intent OS에는 같은 사실을 둘 이상의 Entity가 표현하는 경우가 있다. 조회 편의를 위한 중복 자체는 허용할 수 있지만, **어느 값이 진실의 원천(Source of Truth)인지 모호하면 구현체마다 서로 다른 값을 믿게 된다.**

이 문서는 모든 영속 필드를 다음 네 종류 중 하나로 분류하고, 충돌 시 무엇을 신뢰할지 정의한다.

| 분류 | 의미 | 변경 방식 | 충돌 시 |
|---|---|---|---|
| `AUTHORITATIVE` | 해당 사실의 정본 | 이 필드/Entity를 직접 변경 | 항상 이 값이 이김 |
| `REFERENCE` | 다른 Entity 정본을 가리키는 식별자 | 대상 Entity와 독립적으로 ID만 유지 | 참조 대상이 정본 |
| `SNAPSHOT` | 특정 시점의 동결 복사본 | 생성 후 원칙적으로 불변 | 현재값과 달라도 정상 |
| `DERIVED` | 다른 정본으로부터 계산·집계·투영한 값 | 직접 수정 금지, 재계산 | 원본 정본이 이김 |

> **Canonical Data Model의 목적은 데이터를 덜 저장하는 것이 아니라, 같은 사실의 정답을 하나로 만드는 것이다.**

---

## 1. Global Ownership Rules

### Rule CDM-001 — Entity-native facts are AUTHORITATIVE by default

어떤 필드가 그 Entity 자체의 정체성·정의·설정·생명주기 상태를 표현하고, 다른 Entity의 같은 사실을 복제한 것이 아니라면 `AUTHORITATIVE`다.

예:

- `Goal.objective`
- `Constraint.expression`
- `Task.objective`
- `Execution.status`
- `Artifact.location`

이 문서에서 별도 예외로 지정하지 않은 **Entity-native scalar/object field는 AUTHORITATIVE가 기본값**이다.

### Rule CDM-002 — Foreign IDs are REFERENCE by default

다른 Entity를 가리키는 `*_id`, `*_ref`, `*_ids`, `*_refs`는 원칙적으로 `REFERENCE`다.

예:

- `Intent.goal_id → Goal`
- `Execution.decision_id → Decision`
- `Outcome.execution_id → Execution`
- `Artifact.outcome_id → Outcome`

REFERENCE는 관계의 정본 방향일 수도 있고, 조회 편의를 위한 역방향 참조일 수도 있다. **관계의 정본 방향은 [e000a §4](e000a-entity-relationships.md)의 REL-001~005를 따른다.**

### Rule CDM-003 — Later-to-earlier reference wins

시간상 뒤에 생성된 Entity가 앞의 Entity를 가리키는 방향을 관계 정본으로 삼는다.

```text
Goal ← Intent ← Task ← Decision ← Execution ← Outcome ← Evaluation
```

따라서:

- `Outcome.execution_id`는 관계 정본이다.
- `Execution.outcome_id`가 존재하더라도 역방향 캐시이며 정본이 아니다.
- `Evaluation.outcome_id`가 정본이다.
- `Outcome.evaluation_ids`는 정본이 아니다.

### Rule CDM-004 — Graph edges own graph relationships

Goal 간 관계와 Task 간 실행 의존 관계는 각 노드 객체가 아니라 Graph Entity의 edge가 정본이다.

- Goal relationship 정본 → `GoalGraph.edges`
- Task dependency 정본 → `TaskGraph.edges`

노드 내부의 `parent`, `children`, `dependencies`, `depends_on` 등은 존재하더라도 `DERIVED` 또는 호환용 projection이다.

### Rule CDM-005 — Runtime aggregates are DERIVED

다른 Entity의 실행 기록을 합산해 얻을 수 있는 값은 `DERIVED`다.

예:

- 누적 실행 횟수
- 누적 비용
- 성공률
- 평균/p95 latency
- Goal progress
- Graph critical path

### Rule CDM-006 — Decision-time evidence is SNAPSHOT

과거의 판단을 재현하기 위해 저장하는 값은 현재 정본의 복사가 아니라 **그 시점의 동결 증거**이므로 `SNAPSHOT`이다.

예:

- `Decision.inputs_snapshot`
- `Decision.utility_scores.weights`
- `Execution.policy_evaluation.policy_versions`
- 버전 고정된 Resource Profile 입력

### Rule CDM-007 — Snapshots never auto-sync

SNAPSHOT은 원본이 바뀌어도 갱신하지 않는다. 현재값과 다르다는 이유로 정합성 오류로 판단하면 안 된다.

### Rule CDM-008 — Derived fields are not write APIs

`DERIVED` 필드는 클라이언트가 직접 수정할 수 없다. 구현체는 다음 둘 중 하나를 택한다.

1. 조회 시 계산한다.
2. 캐시/머티리얼라이즈드 뷰로 저장하되 원본 변경 시 재계산한다.

### Rule CDM-009 — Duplicated current-state facts are prohibited

동일한 현재 사실을 둘 이상의 Entity에서 모두 `AUTHORITATIVE`로 선언할 수 없다.

### Rule CDM-010 — Historical append-only records may duplicate facts as SNAPSHOT

Decision, Event, Outcome, Evaluation처럼 감사·재현을 위해 과거 사실을 보존하는 Entity는 현재 정본과 같은 내용을 포함할 수 있다. 단 반드시 `SNAPSHOT` 의미여야 한다.

---

## 2. Canonical Relationship Ownership

| 관계 | 정본 필드/구조 | 반대 방향 표현 |
|---|---|---|
| Goal → Intent | `Intent.goal_id` (`REFERENCE`) | Goal.intent_ids가 생기면 `DERIVED` |
| Goal/Plan/Task → Constraint | `Constraint.scope + goal_id/task_id` 및 적용 규칙 | Goal/Task 내 복제 제약은 제거 또는 `SNAPSHOT` |
| Goal/Plan/Task → Context | `Context.scope + goal_id/task_id` | Goal.context는 제거 또는 명시적 `SNAPSHOT` |
| Goal/Plan/Task → Assumption | `Assumption.scope` | Plan.assumptions 문자열은 제거 또는 `SNAPSHOT` |
| Goal/Plan → Risk | `Risk.scope` | 역방향 risk_ids는 `DERIVED` |
| Goal ↔ Goal | `GoalGraph.edges` | Goal.parent_goal/child_goals/dependencies/related_goals는 `DERIVED` |
| Plan → Task | `TaskGraph.plan_id + TaskGraph.nodes` / Task의 Goal lineage | `Plan.tasks`는 계획 생성 시 `SNAPSHOT` 또는 projection |
| Task ↔ Task | `TaskGraph.edges` | `Task.dependencies`, `Plan.tasks[].depends_on`은 `DERIVED` |
| Task → Decision | `Decision.subject.task_id` | Task.decision_ids가 생기면 `DERIVED` |
| Decision → Execution | `Execution.decision_id` | Decision.execution_ids가 생기면 `DERIVED` |
| Execution → Outcome | `Outcome.execution_id` | `Execution.outcome_id`는 `DERIVED` |
| Outcome → Evaluation | `Evaluation.outcome_id` | `Outcome.evaluation_ids`는 `DERIVED` |
| Outcome → Artifact | `Artifact.outcome_id` | `Outcome.artifacts`는 `DERIVED` |
| Resource → ResourceProfile | `ResourceProfile.resource_id` | Resource.profile_id가 생기면 `DERIVED` |
| Memory → Knowledge | `Knowledge.evidence.*_memory_refs` | Memory.knowledge_ids가 생기면 `DERIVED` |
| Session → Execution | `Execution.session_id` | `Session.execution_ids`는 `DERIVED` |
| Session → Decision | Event/correlation 또는 Decision subject lineage | `Session.decision_ids`는 `DERIVED` |
| Session → Artifact | Execution→Outcome→Artifact chain | `Session.artifact_ids`는 `DERIVED` |
| Agent → Execution | `Execution.agent_id` | Agent.execution_ids가 생기면 `DERIVED` |

---

## 3. Entity-by-Entity Ownership Map

### E001 Goal

**AUTHORITATIVE**

- `goal_id`, `version`, `title`, `goal_type`
- `objective.*`, `motivation`
- 사람이 직접 지정한 `priority.level`
- `stakeholders`
- `status.phase`, `status.entered_at`, `status.blocked_reason`
- `quality.confidence`
- `metadata.created_by`, `created_at`, `updated_at`, `source`, `origin_ref`

**DERIVED**

- `parent_goal`, `child_goals`, `dependencies`, `related_goals` ← `GoalGraph.edges`
- `status.progress` ← Goal metric + current Context/Outcome
- `priority.weight`, `priority.factors.*`, `priority.computed_score`, `priority.computed_at` ← scoring engine
- `quality.completeness`, `quality.completeness_level` ← validation rules
- `metadata.history` ← Event/change log projection. 장기적으로 Goal 내부 정본에서 제거 권장

**REMOVE / NORMALIZE**

- `constraints` → 현재 제약 정본으로 사용하지 않는다. `Constraint` Entity로 이관. 필요한 경우 Goal 생성 당시 조건을 보여주는 `SNAPSHOT`으로만 명시한다.
- `context` → 현재 Context 정본으로 사용하지 않는다. `Context` Entity가 정본.
- `context.assumptions` → `Assumption` Entity가 정본.

### E001-A Goal Graph

**AUTHORITATIVE**

- `graph_id`, `root_goal_id`
- `edges[*].from/to/relationship/weight`
- `weights.*` (해당 Graph 버전에 적용되는 scoring configuration)

**REFERENCE**

- `nodes[*]`는 Goal을 가리키는 참조 집합이어야 한다.

**NORMALIZATION**

현재 스키마처럼 `nodes`에 Goal 객체 전체를 embed하는 방식은 정본 중복을 만든다. v1 구현에서는 `goal_id[]` 참조를 권장한다.

### E002 Intent

**AUTHORITATIVE**

- `intent_id`, `intent_type`, `direction`, `rationale`, `confidence`, `priority`, `expected_impact`, `status`

**REFERENCE**

- `goal_id`
- `evidence[]`는 가능하면 Context/Artifact/Knowledge의 typed reference로 정규화

### E003 Context

**AUTHORITATIVE**

- `context_id`, `scope`
- `current_state`, `environment`, `user_profile`, `history`, `available_resources`
- `items_meta[*].source`, `collected_at`, `ttl_hours`

**REFERENCE**

- `goal_id`, `task_id`

**DERIVED**

- `items_meta[*].freshness` ← `collected_at + ttl_hours + now`

### E004 Constraint

**AUTHORITATIVE**

- `constraint_id`, `constraint_type`, `hardness`, `expression`, `unit`, `scope`
- `origin`, `penalty`, `relaxation`, `status`

**REFERENCE**

- `goal_id`, `task_id`

Constraint가 현재 제약 조건의 정본이다.

### E005 Task

**AUTHORITATIVE**

- `id`, `objective`, `task_type`, `expected_output`, `execution_mode`, `priority`, `retry_policy`, `state`

**REFERENCE**

- `goal_id`
- `required_capabilities[*].capability_id`

**DERIVED**

- `dependencies` ← `TaskGraph.edges`
- `assigned_resource_id` ← 최신 유효 ResourceSelection Decision. 직접 수정 금지
- `attempts` ← 해당 Task의 Execution 수

**REMOVE / NORMALIZE**

- `constraints[]` 문자열 복제는 Constraint Entity 조회/projection으로 대체

### E005-A Task Graph

**AUTHORITATIVE**

- `graph_id`, `plan_id`, `version`, `nodes`, `edges`, `status`
- `derived_from`, `previous_version`은 provenance reference

**DERIVED**

- `entry_tasks`
- `analysis.critical_path`
- `analysis.estimated_duration`
- `analysis.max_parallelism`
- `analysis.spof`
- `diff`는 두 Graph version 비교 결과

### E006 Capability / E006-A Capability Taxonomy

Capability의 의미·측정 정의·taxonomy 위치는 Taxonomy가 정본이다.

**AUTHORITATIVE**

- canonical `capability_id`
- `display_name`, `description`, 측정 정의, 상태, 버전
- hierarchy의 정방향 `parent`

**DERIVED**

- `children` ← parent 역조회
- Capability 문서의 `related`가 Taxonomy와 중복될 경우 하나의 관계 registry로 통합 권장

### E007 Resource

Resource는 **정체성과 선언된 능력**만 소유한다.

**AUTHORITATIVE**

- `id`, `name`, `type`, `provider`, `version`
- capability 선언 자체
- `cost_model`의 공급자/계약상 선언 단가
- `limitations`
- 계약/구성상 availability
- `lifecycle`

**DERIVED / MOVE TO RESOURCE PROFILE**

- `capabilities[*].observed_score`
- `capabilities[*].confidence`
- `performance.*`
- 실측 availability

`declared_score`는 Resource의 선언값으로 남길 수 있으나 실제 선택 점수의 정본은 Resource Profile이다.

### E008 Plan

**AUTHORITATIVE**

- `plan_id`, `version`, `status`
- `estimated_cost`, `estimated_duration`, `expected_success_probability`, `risk_level`, `constraint_margin`
- `supersedes`, `abort_reason`, `created_by`, `created_at`

**REFERENCE**

- `source_goal_ids`, `alternative_plan_ids`

**SNAPSHOT**

- `tasks`는 Plan 승인 시점의 실행 청사진 snapshot. 실제 Task 상태/의존성 정본은 Task + TaskGraph
- `assumptions`는 Plan 생성 당시 가정 snapshot으로만 허용. 현재 유효 가정 정본은 Assumption Entity

### E009 Decision

Decision은 생성 당시 판단을 보존하는 immutable record다.

**AUTHORITATIVE**

- `decision_id`, `decision_type`, `selection`, `alternatives_considered`, `rationale`, `confidence`, `decided_by`, `status`, `supersedes`, `forced_action`, `rejection_reason`, `decided_at`

**REFERENCE**

- `subject.goal_id/plan_id/task_id`

**SNAPSHOT**

- `utility_scores.*`
- `inputs_snapshot`

**DERIVED**

- `outcome_link` ← Decision → Execution → Outcome 역조회. 제거 권장

### E010 Memory

**AUTHORITATIVE**

- 경험 기록 자체: `memory_type`, `scope`, `content`, `confidence`, `created_at`, `status`
- `last_recalled_at`, `recall_count`는 Memory subsystem이 소유하는 runtime metadata

**REFERENCE**

- `goal_ref`, `decision_ref`, `source`, `correction_of`

### E011 Knowledge

**AUTHORITATIVE**

- `statement`, `applicability`, `confidence`, `falsification_condition`, `scope`, `status`
- `created_at`, `last_validated_at`, `expiration_policy`

**REFERENCE**

- `evidence.supporting_memory_refs`
- `evidence.contradicting_memory_refs`

**DERIVED**

- `evidence.evidence_count` ← supporting + contradicting evidence 집계

### E012 Feedback

**AUTHORITATIVE**

- 원시 `signal`, `source_type`, `created_at`, `provenance`, `status`
- `interpretation`은 Feedback 해석기의 현재 판정값으로 Feedback Entity가 소유
- `weight`, `routing`은 Learning routing configuration/result

**REFERENCE**

- `target.target_ref`

### E013 Execution

**AUTHORITATIVE**

- `execution_id`, `mode`, `attempt`, `status`, `progress`
- timestamps, `timeout_ms`, `cost`, `usage`, `error`, `failure_class`
- `contributes_to_goal`

**REFERENCE**

- `task_id`, `decision_id`, `session_id`, `resource_id`, `agent_id`
- `previous_execution_id`, `parent_execution_id`
- `input_ref`, `logs_ref`

**SNAPSHOT**

- `policy_evaluation.*`는 실행 시점 Policy 판정의 동결 기록

**DERIVED**

- `latency_ms` ← `finished_at - started_at` (저장 캐시 허용)
- `outcome_id` ← Outcome.execution_id 역조회. 제거 권장

### E014 Outcome

**AUTHORITATIVE**

- `outcome_id`, `status`, `output_summary`, `output_count`, `cost`, `latency_ms`, `usage`, `measured_at`
- `goal_progress`, `contributes_to_goal`, `errors`, `partial_reason`, `late_arrival`, `status_lifecycle`

**REFERENCE**

- `execution_id`, `supersedes`

**DERIVED**

- `task_id` ← execution chain (이미 스키마 설명도 cache로 규정)
- `artifacts` ← Artifact.outcome_id 역조회
- `evaluation_ids` ← Evaluation.outcome_id 역조회

### E015 Evaluation

**AUTHORITATIVE**

- 평가 자체: `evaluator`, `evaluator_type`, `scores.quality/goal_alignment/efficiency/satisfaction`, `verdict`, `adopted`, `rationale`, `status`, `evaluated_at`
- `decision_review.decision_quality`

**REFERENCE**

- `outcome_id`, `rubric_id`, `feedback_ids`, `supersedes`
- `decision_review.decision_id`

**SNAPSHOT**

- `rubric_version`
- `scores.weights`

**DERIVED**

- `task_id` ← Outcome→Execution→Task
- `scores.composite` ← component scores + weights
- `decision_review.prediction_error.*` ← Decision prediction vs Outcome actual

### E016 Artifact

**AUTHORITATIVE**

- `artifact_id`, content/storage metadata, `name`, `summary`, `tags`, `produced_at`, visibility/PII/status

**REFERENCE**

- `outcome_id`, `produced_by`, `derived_from`, `duplicate_of`, `schema_ref`, `retention_policy_id`

**DERIVED**

- `content_hash`는 content bytes에서 계산되는 값이므로 DERIVED. 저장하여 무결성 검증에 사용 가능
- `size_bytes`도 저장 캐시 가능하지만 실제 blob이 정본

### E017 Assumption

**AUTHORITATIVE**

- `statement`, `confidence`, `impact`, validation policy, invalidation action, monitoring/status timestamps

**REFERENCE**

- `scope.goal_id/plan_id/task_id`
- `linked_risk_id`, `fallback_plan_ref`

**DERIVED**

- `dependents` ← scope/reference graph 역조회. 제거 권장

### E018 Risk

**AUTHORITATIVE**

- `statement`, `likelihood`, `impact`, estimation basis, warning/trigger/strategy/response/owner/status`

**REFERENCE**

- `scope.goal_id/plan_id`
- `contingency_ref`, `source_assumption_id`, `materialized_event_id`, `related_risk_ids`

**DERIVED**

- `severity` ← likelihood × impact
- `severity_band` ← severity banding rule
- `residual_severity`는 대응 모델의 계산 결과이므로 계산 근거와 함께 derived 값으로 취급

### E019 Policy

Policy 정의는 자체적으로 AUTHORITATIVE다.

**REFERENCE**

- `reference`는 외부 법/규정 문서 참조

**SNAPSHOT consumers**

Policy를 적용한 Decision/Execution은 `policy_id + version`을 snapshot으로 보존한다. 현재 Policy를 과거 판정에 소급 적용하지 않는다.

### E020 Event

Event는 append-only historical record이므로 이벤트 payload 전체가 **발생 시점 SNAPSHOT**이다.

**AUTHORITATIVE**

- `event_id`, `type`, `sequence`, `emitted_by`, `emitted_at`, `schema_version`, `corrects`

**REFERENCE**

- `subject.entity_id`, `session_id`, `goal_id`, `correlation_id`

**SNAPSHOT**

- `previous_state`, `new_state`, `data`

**MOVE / SEPARATE**

- `delivery.*`는 Event 자체가 아니라 consumer delivery runtime state다. 장기적으로 별도 delivery record/store가 정본이어야 한다.

### E021 Session

**AUTHORITATIVE**

- session identity/type/actor/participants
- `budget`, timeouts, timestamps, status/phase/end_reason/summary
- `dry_run`

**REFERENCE**

- `goal_ids`, `trigger_ref`, `policy_scope`, `context_ref`

**DERIVED**

- `consumed.*` ← Execution 집계
- `execution_ids` ← Execution.session_id
- `decision_ids`, `artifact_ids`, `agent_ids`, `memory_ids` ← Session lineage 역조회

### E022 Workflow

Workflow template 정의는 AUTHORITATIVE다.

**AUTHORITATIVE**

- identity/version/type/owner
- variables, steps, control flow, policy refs, status

**REFERENCE**

- `derived_from` → Knowledge

**DERIVED**

- `usage_stats.*` ← 실제 Workflow instantiation/Outcome 집계

### E023 Agent

**AUTHORITATIVE**

- identity/type/principal/autonomy
- allowed scope, delegation limit, budget, reporting policy, status
- `assigned_scope`는 Agent assignment subsystem이 소유하는 현재 배정 상태

**REFERENCE**

- `session_id`, `reasoning_resource_id`

**DERIVED**

- `depth` ← principal chain
- `children` ← child Agent.principal 역조회
- `consumed.*` ← Agent가 만든 Execution 집계

### E024 Tool

Tool은 인터페이스 계약과 권한 요구를 소유한다.

**AUTHORITATIVE**

- identity/provider/version/category
- capabilities declaration, operations schemas/effects/idempotency
- required scopes, auth type, residency, breaking-change policy, configured rate limits/timeouts, status

**DERIVED / MOVE TO RESOURCE PROFILE or Health Store**

- `health.success_rate_24h`
- `health.p95_latency_ms`
- `health.consecutive_schema_violations`

### E025 Resource Profile

Resource Profile이 **실측 성능의 유일한 정본**이다.

**AUTHORITATIVE**

- `profile_id`, `resource_id`, `snapshot_version`, `updated_at`, `status`
- 집계 계산에 사용된 evidence/window/decay 설정
- visibility

**DERIVED**

- `capability_scores.observed_score`, `confidence`, `variance`
- `cost_model.observed_avg_cost`
- `performance.*`
- `availability.uptime_30d`
- `drift.*`

이 값들은 Execution/Outcome/Evaluation 표본으로부터 계산되지만 **운영 중 선택 엔진이 읽는 materialized canonical profile**로 저장할 수 있다. 이 경우 원시 증거의 정본은 Execution/Outcome/Evaluation이고, Profile은 공식 집계 뷰다.

**SNAPSHOT**

- 특정 Decision이 참조한 `snapshot_version`의 Profile 전체는 그 Decision 관점에서 immutable snapshot이다.

---

## 4. Mandatory Normalization Decisions for v1

다음 결정은 v1 DB 설계 전에 반드시 적용한다.

### CDM-N01 — Goal current constraints move to Constraint

`Goal.constraints`를 현재 제약 정본으로 사용하지 않는다.

- write → Constraint API
- read → Constraint(scope=Goal) 조회
- Goal API가 편의를 위해 보여줄 경우 `derived_constraints` 같은 명시적 projection 이름 사용 권장

### CDM-N02 — Goal current context moves to Context

`Goal.context`의 현재 상태/환경은 Context가 정본이다.

### CDM-N03 — Goal assumptions move to Assumption

`Goal.context.assumptions` 및 `Plan.assumptions` 문자열은 현재 상태 정본으로 사용하지 않는다.

### CDM-N04 — Goal relationships live only in GoalGraph.edges

`parent_goal`, `child_goals`, `dependencies`, `related_goals`는 write 금지 derived projection으로 취급한다.

### CDM-N05 — Task dependencies live only in TaskGraph.edges

`Task.dependencies`와 `Plan.tasks[].depends_on`은 write 금지 projection/snapshot으로 취급한다.

### CDM-N06 — Resource observed performance moves to ResourceProfile

Resource의 observed score/performance는 신규 write를 금지하고 ResourceProfile을 조회한다.

### CDM-N07 — Backlinks become derived views

다음은 직접 수정하지 않는다.

- `Execution.outcome_id`
- `Outcome.artifacts`
- `Outcome.evaluation_ids`
- `Decision.outcome_link`
- `Session.execution_ids`
- `Session.decision_ids`
- `Session.artifact_ids`
- `Session.agent_ids`
- `Session.memory_ids`
- `Agent.children`
- `Assumption.dependents`

### CDM-N08 — Event delivery state is separated conceptually

Event는 immutable event fact이고 delivery는 mutable transport state다. 구현 DB에서는 별도 table/collection을 권장한다.

### CDM-N09 — Calculated scores are never user-writable

다음 계열은 계산 엔진만 갱신한다.

- Goal progress/completeness/computed priority
- Risk severity/band
- Evaluation composite/prediction error
- ResourceProfile observed aggregates
- Session/Agent consumed totals
- Graph analyses

### CDM-N10 — Historical decision evidence is immutable snapshot

Decision/Execution에 저장된 당시 weights/profile/policy versions는 현재 설정으로 덮어쓰지 않는다.

---

## 5. Conflict Resolution Order

같은 사실이 둘 이상의 위치에서 다르게 보이면 다음 순서로 해결한다.

1. 이 문서에서 지정한 `AUTHORITATIVE` source
2. 정방향 `REFERENCE`가 가리키는 Entity
3. Graph 관계라면 Graph edge
4. `SNAPSHOT`은 과거 시점 사실로 보존하고 현재값과 비교하지 않는다
5. `DERIVED`는 폐기 후 재계산한다

예:

```text
Goal.dependencies = [G2]
GoalGraph.edges    = G1 DEPENDS_ON G3
```

정답은 `G3`다. `Goal.dependencies`를 재생성한다.

```text
Execution.outcome_id = O1
Outcome.execution_id = E1 인 Outcome은 O2
```

정답은 `O2`다. `Execution.outcome_id`는 역방향 projection이므로 재생성한다.

---

## 6. DB Mapping Guidance

### Tables / primary stores

v1 관계형 구현의 최소 정본 저장소는 다음 구조를 권장한다.

```text
goals
intents
contexts
constraints
plans
tasks
task_graphs
task_graph_edges
capabilities
capability_relations
resources
resource_profiles
decisions
executions
outcomes
evaluations
artifacts
feedback
memories
knowledge
knowledge_evidence
assumptions
risks
policies
events
event_deliveries
sessions
workflows
agents
tools
goal_graphs
goal_graph_edges
```

역방향 목록은 배열 컬럼으로 중복 저장하지 않고 query/view로 만든다.

### Materialized views allowed

성능상 필요하면 다음은 materialized view/cache로 저장할 수 있다.

- Goal progress
- Goal computed priority
- Task attempts
- Resource Profile aggregates
- Workflow usage stats
- Session consumed totals
- Agent consumed totals
- Graph analyses

단 모든 materialized view에는 최소한 다음 메타데이터를 둔다.

```text
computed_at
source_version / source_watermark
computation_version
```

---

## 7. Migration Rules

기존 스키마에서 v1 구현으로 옮길 때:

1. 정본 필드를 먼저 새 테이블/Entity로 이동한다.
2. 중복 필드와 새 정본을 비교해 충돌 리포트를 만든다.
3. 충돌 시 이 문서의 Conflict Resolution Order를 따른다.
4. 역방향 배열은 읽기 전용 projection으로 전환한다.
5. snapshot 필드는 `captured_at` 또는 version provenance를 남긴다.
6. derived 필드의 직접 write endpoint를 제거한다.
7. 모든 derived 값은 재생성 테스트를 통과해야 한다.

---

## 8. Conformance Invariants

### INV-CDM-01 — Single Current Truth

하나의 현재 사실에는 AUTHORITATIVE source가 정확히 하나여야 한다.

### INV-CDM-02 — Derived Reproducibility

모든 DERIVED 값은 선언된 source만으로 재계산 가능해야 한다.

### INV-CDM-03 — Snapshot Immutability

SNAPSHOT은 생성 후 원본 변경에 따라 자동 수정되지 않는다.

### INV-CDM-04 — Reference Integrity

REFERENCE는 존재하는 대상 또는 명시적으로 허용된 tombstone을 가리켜야 한다.

### INV-CDM-05 — Graph Ownership

Goal/Task 관계를 node-local field가 Graph edge보다 우선할 수 없다.

### INV-CDM-06 — No Performance Dual Truth

Resource와 ResourceProfile이 서로 다른 observed performance를 정본으로 주장할 수 없다. 실측 성능의 운영 정본은 ResourceProfile이다.

### INV-CDM-07 — No Writable Backlinks

역방향 collection/projection은 외부 write API를 가질 수 없다.

### INV-CDM-08 — Historical Reproducibility

Decision은 당시 사용한 핵심 버전/가중치/Profile/Policy를 재현할 수 있어야 한다.

---

## 9. Definition of Done for Canonical Data Model v1

이 문서는 다음이 완료되면 `Stable`로 승격한다.

- [x] Ownership classification 4종 정의
- [x] Global ownership rules 정의
- [x] 핵심 Entity별 ownership map 정의
- [x] 관계 정본 방향 정의
- [x] 주요 중복 필드 normalization 결정
- [x] DB mapping guidance 정의
- [x] migration/conflict 규칙 정의
- [ ] JSON Schema에 read-only / snapshot semantics 반영
- [ ] `tools/validate-canonical.py` 구현
- [ ] Golden Fixture 10개로 INV-CDM-01~08 검증
- [ ] Volume 1~7의 구형 중복 표현 정리

---

## 10. Immediate Next Step

Canonical Data Model을 문서로 확정한 다음 작업은 **스키마를 이 규칙에 맞추는 것**이다.

우선순위:

1. `goal.schema.json` 정규화
2. `task.schema.json` / `task-graph.schema.json` 정규화
3. `resource.schema.json` / `resource-profile.schema.json` 정규화
4. backlink 필드를 read-only projection으로 정의
5. `validate-canonical.py`로 이 규칙을 자동 검사

이 단계가 끝난 뒤에야 PostgreSQL ERD를 정본으로 설계한다.
