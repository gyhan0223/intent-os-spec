# Entity 005-A: Task Graph

- **Version:** v1.0 Draft
- **Status:** Core Architecture
- **Last Updated:** 2026-08-04

---

## Why Not Just a List

[Task](e005-task.md) 명세는 노드 하나를 정의했다. 그런데 실행에서 중요한 것은 노드가 아니라 **구조**다.

```
할 일 목록                          Task Graph
─────────                          ──────────
1. 시장 조사                        어느 것이 동시에 가능한가
2. 경쟁 분석                        어느 것이 전체를 지연시키는가
3. 타겟 분석                        하나가 실패하면 무엇이 무너지는가
4. 광고 카피 작성                    계획을 바꿀 때 무엇을 살릴 수 있는가
```

목록은 이 네 질문에 하나도 답하지 못한다. [Goal Graph](e001a-goal-graph.md)가 Goal에 대해 했던 일을 Task에 대해 하는 것이 이 문서다.

> [e005 §12 Open Issues](e005-task.md)가 제기한 "Task Graph는 별도 명세가 필요한가"에 대한 답이다.

---

## 1. Definition

### 공식 정의

> **Task Graph is the directed acyclic graph of Tasks within a Plan, whose edges express execution dependencies and whose structure determines parallelism, critical path, failure propagation, and what survives replanning.**

> Task Graph는 하나의 Plan에 속한 Task들의 **방향성 비순환 그래프**이며, 간선은 실행 의존을 표현하고 그 구조가 병렬성·임계 경로·실패 전파·재계획 시 보존 범위를 결정한다.

### 형식 정의

$$TG = (V, E)$$

| 기호 | 의미 |
|---|---|
| $V$ | Task 집합 |
| $E \subseteq V \times V$ | 의존 간선. $(a, b) \in E$ 는 "b는 a가 완료되어야 시작 가능"을 뜻한다 |

**제약:** $TG$ 는 DAG여야 한다. 순환이 있으면 Runtime이 교착 상태에 빠진다([INV-08](e000a-entity-relationships.md)).

---

## 2. Task Graph는 무엇이 아닌가?

### Task Graph는 Task 목록이 아니다

❌ `T1, T2, T3, T4, T5, T6, T7`

목록에는 간선이 없다. 간선이 없으면 병렬 실행도, 임계 경로도, 실패 전파도 계산할 수 없다.

### Task Graph는 Workflow가 아니다

❌ `조건이 만족될 때까지 반복한다` — 이건 [Workflow](e022-workflow.md)다.

**의존과 제어는 다르다.**

| | Task Graph | Workflow |
|---|---|---|
| 표현 | 무엇이 무엇을 막는가 | 어떻게 흘러가는가 |
| 구조 | 정적 DAG | 분기·반복·대기·보상 |
| 수명 | Plan에 종속 | Goal 독립. 재사용 |
| 순환 | 금지 | `loop`로 명시적 허용 |

Task Graph는 **제약의 표현**이고 Workflow는 **흐름의 설계**다. Workflow가 인스턴스화되면 Task Graph가 생성된다([e022 §9.2](e022-workflow.md)).

### Task Graph는 Goal Graph가 아니다

❌ `모집 100명 ← 인지도 상승 ← 광고 노출`

| | [Goal Graph](e001a-goal-graph.md) | Task Graph |
|---|---|---|
| 노드 | Goal (미래 상태) | Task (행위) |
| 간선 | DEPENDS_ON, ENABLES, CONFLICTS_WITH … | dependencies 한 종류 |
| 생성 | 사용자 + Goal Engine | Planner |
| 소비 | Planner | Runtime Engine |
| 수명 | Goal과 함께 (장기) | Plan과 함께 (단기) |

Goal Graph는 **왜**를 담고 Task Graph는 **어떻게**를 담는다.

### Task Graph는 간트 차트가 아니다

❌ `T4는 8/6~8/8`

간트 차트는 **시각(時刻)** 을 담는다. Task Graph는 **순서**만 담는다. 실제 시각은 Resource 배정 이후에야 추정 가능하다. 그래프에 날짜를 박으면 Resource 선택 전에 일정을 고정하게 되고, 이는 [INV-09](e000a-entity-relationships.md) Layer Isolation 위반이다.

---

## 3. Design Principles

### Rule TG-001 — 간선은 한 종류뿐이다

Task Graph의 간선은 `depends_on` 하나다. Goal Graph처럼 관계 유형을 늘리지 않는다.

이유: Runtime은 "지금 실행 가능한 Task가 무엇인가"만 알면 된다. 관계가 여러 종류면 그 판단이 복잡해진다. 조건부 실행이 필요하면 Workflow로 표현한다.

### Rule TG-002 — DAG여야 한다

순환 검사는 **간선 추가 시점**에 수행한다. 그래프 완성 후 검사하면 어디서 잘못됐는지 알기 어렵다.

### Rule TG-003 — 모든 Task는 도달 가능해야 한다

진입 Task(선행 없음)에서 시작해 모든 Task에 도달할 수 있어야 한다. 고립된 Task는 실행되지 않는다.

### Rule TG-004 — 간선은 실제 의존만 표현한다

- ✅ `T4(카피 작성)는 T3(타겟 분석)의 산출물을 입력으로 쓴다`
- ❌ `T4는 T3보다 나중에 하고 싶다` — 이건 선호이지 의존이 아니다

**불필요한 간선은 병렬성을 죽인다.** 의존이 아닌데 간선을 그으면 동시에 할 수 있는 일이 순차가 된다.

판별 질문: **T3의 산출물 없이 T4를 시작할 수 있는가?** 있으면 간선을 긋지 않는다.

### Rule TG-005 — 임계 경로를 계산할 수 있어야 한다

각 Task의 추정 소요 시간이 있으면 임계 경로(Critical Path)를 계산한다. 임계 경로 위의 Task가 지연되면 **전체가 지연된다.**

### Rule TG-006 — 실패는 하류로 전파된다

Task가 최종 실패하면 그것에 의존하는 모든 하류 Task가 실행 불가(`Blocked`)가 된다. 상류로는 전파되지 않는다.

### Rule TG-007 — 재계획은 완료된 것을 보존한다

Plan이 바뀌어도 이미 `Completed`/`Evaluated`된 Task와 그 [Artifact](e016-artifact.md)는 살아남는다(§7). **이것이 Dynamic Planning의 핵심이다.**

### Rule TG-008 — 그래프 변경은 Plan 버전을 올린다

Task를 추가·삭제하거나 간선을 바꾸면 새 Plan 버전이 된다([e008](e008-plan.md)의 Versioning). 그래프를 조용히 수정하지 않는다.

---

## 4. Attributes

Task Graph 자체가 갖는 속성이다. 노드의 속성은 [e005 §4](e005-task.md)에 있다.

```
Task Graph
├── Identity
│   ├── graph_id
│   ├── plan_id
│   └── version
├── Structure
│   ├── nodes[]          (task_id)
│   ├── edges[]          ({from, to})
│   └── entry_tasks[]
├── Analysis
│   ├── critical_path[]
│   ├── estimated_duration
│   ├── max_parallelism
│   └── spof[]           (단일 실패점)
└── Provenance
    ├── derived_from     (workflow_id 또는 null)
    └── previous_version
```

| 속성 | 의미 | 예 |
|---|---|---|
| **graph_id** | 식별자 | `tg_014` |
| **plan_id** | 소속 Plan | `plan_014` |
| **version** | 그래프 버전 | `1` |
| **nodes** | Task 목록 | `["task_001", …, "task_007"]` |
| **edges** | 의존 간선 | `[{ "from": "task_003", "to": "task_004" }, …]` |
| **entry_tasks** | 선행 없는 Task | `["task_001", "task_003", "task_006"]` |
| **critical_path** | 임계 경로 | `["task_003", "task_004", "task_005", "task_007"]` |
| **estimated_duration** | 임계 경로 소요 | `P6D` |
| **max_parallelism** | 최대 동시 실행 수 | `3` |
| **spof** | 단일 실패점 (§5.1) | `["task_004"]` |
| **derived_from** | 인스턴스화한 Workflow | `wf_seasonal_campaign@2.1` |

### 4.1 Task 상태와 그래프 상태

| Task 상태 | 그래프 관점의 의미 |
|---|---|
| `Pending` | 선행이 미완료. 대기 |
| `Ready` | 선행이 전부 완료. 실행 가능 (파생 상태) |
| `Assigned` / `Running` | 실행 중 |
| `Completed` / `Evaluated` | 완료. **재계획 시 보존 대상** |
| `Failed` | 실패. 재시도 또는 하류 차단 |
| `Blocked` | 상류 실패로 실행 불가 (파생 상태) |
| `Orphaned` | Goal 연결이 끊김 ([INV-01](e000a-entity-relationships.md)) |

**`Ready`와 `Blocked`는 저장하지 않는다.** 그래프 구조와 다른 Task의 상태로부터 계산된다.

---

## 5. Invariants

### INV-TG-01 — 순환이 존재하지 않는다

전역 불변식 [INV-08](e000a-entity-relationships.md)의 Task Graph 측 표현이다.

| | |
|---|---|
| **위반 시** | 간선 추가를 롤백하고 순환 경로를 오류로 반환 |
| **탐지** | 간선 추가 시점 (증분 순환 검사) |

### INV-TG-02 — 모든 노드는 entry에서 도달 가능하다

| | |
|---|---|
| **위반 시** | 고립 Task를 `Orphaned`로 표시하고 실행하지 않는다. Planner에 반려 |

### INV-TG-03 — 모든 Task는 동일한 Plan에 속한다

| | |
|---|---|
| **위반 시** | 간선 추가 거부. Plan 간 의존은 Goal Graph로 표현한다 |

### INV-TG-04 — Completed Task의 선행은 전부 Completed다

| | |
|---|---|
| **위반 시** | 실행 순서가 깨졌다는 뜻이다. 정합성 경보 발행 + 해당 Outcome을 학습 데이터에서 제외 |

### INV-TG-05 — 재계획 후에도 완료된 Task의 이력은 보존된다

Rule TG-007의 불변식 표현이다.

| | |
|---|---|
| **위반 시** | Task 삭제를 차단한다. 새 그래프에서 빠지더라도 `Superseded`로 표시할 뿐 지우지 않는다 |

### INV-TG-06 — Blocked Task에는 Execution이 생성되지 않는다

| | |
|---|---|
| **위반 시** | Execution 생성 거부. 입력이 없는 실행은 비용만 태운다 |

### 5.1 단일 실패점(SPOF)

하나의 Task가 실패하면 몇 개의 하류가 막히는가.

$$SPOF(t) = |\{ u \in V : t \rightsquigarrow u \}|$$

`spof`는 이 값이 임계치(예: 전체 노드의 40%)를 넘는 Task의 목록이다. SPOF는 [Risk](e018-risk.md) 식별의 자동 입력이 된다([e018 §9.1](e018-risk.md) ②).

---

## 6. Lifecycle

Task Graph는 Plan에 종속된 구조이므로 자체 상태는 단순하다.

```
Constructed → Validated → Active ──▶ Superseded
                              │
                              ├──▶ Completed
                              └──▶ Suspended ──▶ Active
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Constructed** | Planner가 생성 | 분해 완료 |
| **Validated** | 순환·도달성·크기 검사 통과 | 검증 |
| **Active** | Runtime이 실행 중 | Plan 활성화 |
| **Suspended** | 실행 중지 | 가정 무효화, 예산 초과 |
| **Superseded** | 새 버전으로 대체 | 재계획 |
| **Completed** | 모든 Task가 종료 상태 | 실행 완료 |

---

### 6.1 Dynamic Planning — 그래프 재구성

**이 절이 이 문서의 핵심이다.** [e005 §12](e005-task.md)이 미해결로 남긴 문제에 답한다.

#### 6.1.1 문제

```
실행 중:  T1 ✅  T2 ✅  T3 ✅  T4 🔄(실행 중)  T5 ⬜  T6 ⬜  T7 ⬜
   ↓
가정 무효화 (예산 300만 → 200만)
   ↓
새 Plan이 필요하다. 그런데 T1·T2·T3의 결과를 버릴 것인가?
```

전부 다시 하면 이미 쓴 비용과 시간이 사라진다. 그대로 두면 새 계획과 맞지 않을 수 있다.

#### 6.1.2 Graph Diff

새 그래프 $TG'$ 와 기존 $TG$ 를 비교해 Task를 4분류한다.

| 분류 | 조건 | 조치 |
|---|---|---|
| **Preserved** | $TG'$ 에 동일 Task 존재 + 상태가 `Completed`/`Evaluated` | 그대로 승계. Artifact 재사용 |
| **Invalidated** | $TG'$ 에 존재하지만 입력이 바뀜 | 재실행 대상. `Pending`으로 리셋 |
| **Removed** | $TG'$ 에 없음 | `Superseded` 표시. **삭제하지 않는다** (INV-TG-05) |
| **Added** | $TG'$ 에만 존재 | 새 Task로 생성 |

**동일 Task 판정 기준:** `objective` + `required_capabilities` + `expected_output`이 같으면 동일하다. `task_id`가 아니다 — Planner가 매번 새 ID를 만들 수 있기 때문이다.

#### 6.1.3 재구성 알고리즘

```
재계획 트리거 (가정 무효화 / 예산 변경 / 실패 누적 / 사용자 요청)
  ↓
① 진행 중 Execution 처리
   ├── 진행률 > 0.8  → 완료 대기
   └── 그 외          → Aborted (비용 기록)
  ↓
② Planner가 새 Task Graph 초안 TG' 생성
   입력: Goal, 갱신된 Constraint/Assumption, 기존 그래프의 Completed 결과
  ↓
③ Graph Diff 수행 (§7.2)
  ↓
④ Preserved Task의 유효성 재검증
   질문: 그 산출물이 새 계획의 맥락에서도 유효한가
   ├── 유효   → 승계. Artifact 그대로 사용
   └── 무효   → Invalidated로 재분류
  ↓
⑤ TG' 검증 (순환·도달성·크기)
  ↓
⑥ 새 Plan 버전 발행 (TG-008)
   plan_014 → Superseded
   plan_015 → Active, graph_version 2, previous_version: tg_014@1
  ↓
⑦ Event 발행 (plan.superseded, plan.activated)
  ↓
⑧ Runtime 재개
```

#### 6.1.4 실제 적용

```
plan_014 (예산 300만원)          plan_015 (예산 200만원)
T1 시장 조사      ✅ Completed  →  Preserved  (조사 결과는 예산과 무관)
T2 경쟁 분석      ✅ Completed  →  Preserved
T3 타겟 분석      ✅ Completed  →  Preserved
T4 광고 카피 작성  🔄 Running    →  Preserved  (진행률 0.9 → 완료 대기)
T5 랜딩 개선      ⬜ Pending    →  Preserved  (우선순위만 상향)
T6 인스타 광고 집행 ⬜ Pending    →  Invalidated (예산 180만 → 100만으로 변경)
T7 성과 분석      ⬜ Pending    →  Preserved
                                 →  Added: T8 SEO 콘텐츠 제작
                                 →  Added: T9 자연 유입 최적화
```

**7개 중 5개가 보존되었다.** 조사·분석·카피는 예산이 줄어도 그대로 쓸 수 있다. 다시 만들었다면 약 12만원과 이틀을 낭비했을 것이다.

#### 6.1.5 보존 판정 기준

④의 "새 계획에서도 유효한가"를 판정하는 질문들이다.

| 질문 | Preserved | Invalidated |
|---|---|---|
| 산출물의 입력 가정이 바뀌었는가 | 아니오 | 예 |
| 산출물의 목표 수치가 바뀌었는가 | 아니오 | 예 |
| 산출물이 참조하는 Artifact가 Invalidated인가 | 아니오 | 예 |
| Context Freshness를 넘겼는가 ([e003](e003-context.md)) | 아니오 | 예 |

**세 번째 질문 때문에 전파가 일어난다.** T3(타겟 분석)이 무효화되면 그것을 입력으로 쓴 T4(카피)도 무효가 된다.

---

## 7. Relationships

```
Goal Graph 001-A ──(대응)──▶ Plan 008 ──1:1──▶ Task Graph 005-A
                                                    │
                                    ┌───────────────┼───────────────┐
                                    │               │               │
                              1:N nodes       1:0..1 previous  0..N spof
                                    ▼               ▼               ▼
                               Task 005      Task Graph 005-A    Risk 018
                                    │
                                    └──1:0..N──▶ Execution 013
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Plan](e008-plan.md) | Task Graph는 정확히 하나의 Plan에 속한다. Plan이 폐기되면 그래프도 `Superseded`가 된다 | `Plan 1:1 Task Graph` |
| [Task](e005-task.md) | 노드의 실체. 그래프는 `task_id`만 담고 Task 본문은 갖지 않는다 | `Task Graph 1:N Task` |
| Task Graph | `previous_version`으로 이전 버전을 가리킨다. 재계획 시 사슬이 늘어난다 | `Task Graph 1:0..1 Task Graph` |
| [Workflow](e022-workflow.md) | `derived_from`. 검증된 패턴에서 그래프를 찍어낼 수 있다 | `Workflow 1:0..N Task Graph` |
| [Goal Graph](e001a-goal-graph.md) | 대응 관계. Goal Graph는 **무엇을**, Task Graph는 **어떻게**를 담는다. 직접 참조하지 않고 Plan을 거친다 | `Goal Graph 1:0..N Task Graph` |
| [Risk](e018-risk.md) | `analysis.spof`가 Risk 식별의 자동 입력이 된다 | `Task Graph 1:0..N Risk` |
| [Execution](e013-execution.md) | 그래프는 Execution을 만들지 않는다. **실행 가능 Task를 계산해줄 뿐**이다(§9.2) | `Task Graph 1:0..N Execution` (간접) |

**참조 방향은 한 방향이다.** Task는 자신이 어느 그래프에 속하는지 모른다. 그래프가 Task를 가리킨다([Rule REL-003](e000a-entity-relationships.md)).

---

## 8. Canonical Representation

```json
{
  "graph_id": "tg_014",
  "plan_id": "plan_014",
  "version": 1,
  "nodes": ["task_001", "task_002", "task_003", "task_004", "task_005", "task_006", "task_007"],
  "edges": [
    { "from": "task_001", "to": "task_002" },
    { "from": "task_003", "to": "task_004" },
    { "from": "task_002", "to": "task_005" },
    { "from": "task_004", "to": "task_005" },
    { "from": "task_004", "to": "task_006" },
    { "from": "task_005", "to": "task_007" },
    { "from": "task_006", "to": "task_007" }
  ],
  "entry_tasks": ["task_001", "task_003"],
  "analysis": {
    "critical_path": ["task_003", "task_004", "task_006", "task_007"],
    "estimated_duration": "P6D",
    "max_parallelism": 2,
    "spof": ["task_004"]
  },
  "derived_from": "wf_seasonal_campaign@2.1",
  "previous_version": null,
  "status": "Active"
}
```

그래프 형태는 다음과 같다.

```
task_001 시장 조사 ──▶ task_002 경쟁 분석 ──┐
                                            ├──▶ task_005 랜딩 개선 ──┐
task_003 타겟 분석 ──▶ task_004 카피 작성 ──┤                         ├──▶ task_007 성과 분석
                              │             └──▶ task_006 광고 집행 ──┘
                              └─ SPOF: 하류 3개를 막는다
```

기계가 읽을 수 있는 스키마: [`task-graph.schema.json`](../intent-os-spec/schemas/task-graph.schema.json)

---

## 9. Validation Rules

### 9.1 그래프 검증

```
Task Graph 생성 요청
  ↓
모든 노드가 동일 Plan 소속인가 (INV-TG-03) ── 아니면 반려
  ↓
간선을 하나씩 추가하며 증분 순환 검사 (INV-TG-01)
  ── 순환 발생 시 해당 간선과 경로를 반환하고 반려
  ↓
entry_tasks 계산 (진입 차수 0인 노드)
  ── 비어 있으면 순환 그래프다. 반려
  ↓
도달성 검사 (INV-TG-02) ── 고립 노드 발견 시 반려
  ↓
불필요 간선 검사 (TG-004)
  전이적 축약(Transitive Reduction) 수행
  A→B, B→C, A→C 에서 A→C는 불필요 → 제거 제안
  ↓
임계 경로 계산 (TG-005)
  ↓
SPOF 계산 (§5.1) → 임계치 초과 시 Risk 자동 생성 제안 (e018)
  ↓
크기 검사
  ├── 노드 > 50    → 하위 Goal 분리 제안
  └── 최대 깊이 > 10 → Task 크기 재검토 제안
  ↓
Validated → Plan에 바인딩
```

### 9.2 실행 가능 Task 계산 (Runtime이 매 틱 호출)

```
for each task in nodes:
    if task.state != Pending: continue

    predecessors = { e.from for e in edges if e.to == task }

    if 모든 predecessor.state ∈ {Completed, Evaluated}:
        task → Ready
    else if 어떤 predecessor.state == Failed (재시도 소진):
        task → Blocked            # 하류 전파 (TG-006)
    else:
        task → Pending 유지

Ready 목록을 우선순위로 정렬
  ① 임계 경로 위의 Task 우선
  ② Goal Score 높은 순
  ③ SPOF 우선 (일찍 실패를 발견하기 위해)
  ↓
Decision Engine에 전달 → Resource 배정
```

**③이 중요하다.** SPOF Task를 먼저 실행하면 실패를 조기에 발견해 낭비를 줄인다.

### 9.3 실패 전파

```
task_004 최종 실패 (재시도 소진)
  ↓
하류 도달 집합 계산: {task_005, task_006, task_007}
  ↓
각 하류 Task → Blocked
  ↓
Blocked 집합이 Goal 달성에 필수인가?
  ├── Yes → Plan Suspended + Replanning 트리거
  └── No  → 부분 진행. Goal Progress 하향 조정
  ↓
Event 발행 (task.blocked × 3)
```

**상류로는 전파하지 않는다.** T4가 실패해도 T3의 결과는 유효하다.

---

## 10. Examples

### 예시 1 — 병렬성

```
entry_tasks: [task_001, task_003]
  ↓ 동시 실행 가능
task_001 시장 조사   ‖   task_003 타겟 분석
  ↓                        ↓
task_002 경쟁 분석    ‖   task_004 카피 작성
```

`max_parallelism: 2`. 불필요한 간선을 하나만 그어도(`task_001 → task_003`) 병렬성이 1로 떨어지고 전체 기간이 두 배가 된다. **Rule TG-004가 실질적으로 일정을 좌우한다.**

### 예시 2 — 임계 경로

```
task_003 타겟 분석   P1D
task_004 카피 작성   P1D  (+ 인간 검수 P1D)
task_006 광고 집행   P14D  ← 가장 길다
task_007 성과 분석   P1D
──────────────────────────
임계 경로 합계        P18D
```

`task_005`(랜딩 개선, P2D)는 임계 경로 밖이다. **2일 늦어져도 전체 일정에 영향이 없다.** 반면 `task_006`이 하루 늦으면 전체가 하루 늦는다. 자원 배분의 우선순위가 여기서 나온다.

### 예시 3 — SPOF와 Risk

```
task_004 (카피 작성)
  하류 도달 집합: {task_005, task_006, task_007} = 3개
  전체 7개 중 43% > 임계치 40%
  ↓
spof: ["task_004"]
  ↓
Risk 자동 제안 (e018 §9.1 ②)
  rsk_050  type: dependency
  statement: "카피 작성 실패 시 랜딩 개선·광고 집행·성과 분석이 전부 중단된다"
  ↓
대응: task_004에 인간 검수 백업 Resource 사전 확보
```

### 예시 4 — 재계획 (§7.4 전체 흐름)

```
2026-08-15  asm_012 Invalidated (예산 300만 → 200만)
  ↓
plan_014 Suspended
  ↓ Graph Diff
Preserved  T1 T2 T3 T4 T5 T7   (5개, 이미 쓴 비용 약 12만원 보존)
Invalidated T6                  (예산 전제가 바뀜)
Added       T8 T9               (SEO·자연 유입)
  ↓
tg_015 생성 (version 2, previous_version: tg_014@1)
  entry_tasks: [task_006b, task_008]   ← Preserved Task는 이미 완료
  critical_path: [task_006b, task_009, task_007]
  ↓
plan_015 Active
```

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **Task 하나짜리 그래프** | 정상이다. `entry_tasks` 1개, `edges` 0개. 단순 Goal에 그래프를 강제하지 않는다 |
| **완전 병렬 그래프 (간선 0개)** | 정상이다. 조사 Task 5개를 동시에 하는 경우. `max_parallelism`은 Resource 가용성이 제한한다 |
| **재계획 시 Preserved Task의 Artifact가 이미 Purged** | `Invalidated`로 재분류하고 재실행한다. Artifact 보존 정책과 재계획 가능 기간을 맞춰야 한다는 신호다 |
| **실행 중 Task에 새 의존이 추가됨** | 허용하지 않는다. 이미 시작한 Task에 선행을 추가하면 그 실행은 잘못된 입력으로 진행 중인 것이다. 새 Plan 버전에서 처리한다 |
| **동일 Task가 두 Plan에 존재** | INV-TG-03 위반이다. 각 Plan이 자기 Task를 갖는다. 결과 재사용은 [Artifact](e016-artifact.md) 참조로 한다 |
| **하류가 없는 Task가 여러 개** | 정상이다. 종료 노드(sink)가 여럿일 수 있다. 다만 각각이 Goal에 기여하는지 [INV-01](e000a-entity-relationships.md)로 검증한다 |
| **실패한 Task의 하류가 다른 경로로도 도달 가능** | `Blocked`가 아니다. 모든 선행이 실패했을 때만 Blocked다. §9.2의 조건이 `모든`인 이유다 |
| **그래프가 50노드를 넘음** | Goal 분해가 부족하다는 신호다. 하위 Goal로 나누고 각각의 Plan을 만든다. Goal Graph가 그 관계를 담는다 |
| **전이적 축약으로 제거 제안된 간선을 사용자가 유지** | 허용한다. 명시적 순서 요구(승인 절차 등)일 수 있다. 다만 `redundant: true`로 표시해 병렬성 손실을 드러낸다 |

---

## 12. Open Issues (v1.0)

### Workflow 인스턴스와의 정합

[e022 §12](e022-workflow.md)가 지적한 문제의 반대편이다. `loop`와 `branch`는 정적 Task Graph로 전개되지 않으므로, 실행 중 Workflow Instance가 Task를 추가한다. 그때 그래프 버전을 올릴 것인가, 동적 확장으로 볼 것인가가 미정이다.

### Goal Propagation의 Task Graph 전파

[Goal Graph §14](e001a-goal-graph.md)의 Propagation이 Task Graph로 내려오는 규칙이 없다. Goal의 우선순위가 바뀌면 Task 우선순위도 바뀌어야 한다.

### 추정 소요 시간의 출처

임계 경로 계산에는 Task별 소요 추정이 필요하다. 그런데 소요는 Resource에 따라 다르고, Resource는 Decision 전까지 정해지지 않는다. **닭과 달걀 문제다.** 현재는 Capability별 중앙값을 쓰는 방식을 가정하지만 근거가 약하다.

### 부분 재계획

§7은 전체 그래프를 다시 만드는 방식이다. 그래프의 일부만 교체하는 국소 재계획(Local Replanning)이 비용상 유리하지만, 정합성 보장이 어렵다.

### 앞으로 보강해야 할 항목

- 임계 경로 추정의 Resource 독립적 방법
- 국소 재계획 알고리즘
- Task 우선순위 계산식 (Goal Score 연동, [e005 §12](e005-task.md))
- 실제 예시 30~50개
