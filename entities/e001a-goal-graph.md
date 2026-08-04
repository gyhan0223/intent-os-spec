# Entity 001-A: Goal Graph

- **Version:** v2.0 Draft
- **Status:** Core Architecture
- **Last Updated:** 2026-08-04

---

## 0. Why Not Just an Object

[Entity 001](e001-goal.md)은 Goal 하나를 객체로 정의했다. 그것만으로는 **프로젝트 관리 도구(Jira, Asana, Notion)** 수준이다.

우리가 만들려는 것은 **운영체제**다.

운영체제는 객체 하나보다 **객체들의 관계**를 더 중요하게 생각한다. Linux에서 중요한 것은 Process 하나가 아니라 **Process Tree**인 것처럼.

```
기존 AI          Prompt → Answer
기존 Task Manager Task → Task → Task
Intent OS        Goal → Goal Network → Planning → Execution
```

차이점은 **Goal들이 서로 영향을 준다**는 것이다. 그래서 Goal을 "점"이 아니라 **"그래프"** 로 정의한다.

> **Planning, Decision, Learning은 모두 Goal Graph를 기준으로 동작한다.**
> Intent OS는 Goal 하나를 실행하지 않는다. **Goal Graph 전체를 최적화한다.**

---

## 1. Definition

### 공식 정의

> **Goal Graph is the directed acyclic graph of all Goals in the system, whose typed edges express influence, dependency, and conflict, and which serves as the single input to the Planner.**

> Goal Graph는 시스템 내 모든 Goal의 **방향성 비순환 그래프**이며, 유형을 가진 간선이 영향·의존·충돌을 표현하고, Planner의 단일 입력이 된다.

### 형식 정의

$$GG = (V, E)$$

| 기호 | 의미 |
|---|---|
| $V$ | [Goal](e001-goal.md) 집합 $\{G_1, G_2, \dots, G_n\}$ |
| $E \subseteq V \times V \times T$ | 유형($T$)을 가진 방향 간선의 집합 |
| $T$ | 관계 유형 6종 (§4.1) |

**제약:** $GG$ 는 DAG여야 한다. 순환은 Planner를 무한 루프에 빠뜨린다([INV-08](e000a-entity-relationships.md)).

---

## 2. Goal Graph는 무엇이 아닌가?

### Goal Graph는 Goal Tree가 아니다

❌ 트리로 충분하다는 가정

```
Tree                 Graph
A                    A
├── B                ├── B ──┐
└── C                │       ├──▶ D
                     └── C ──┘
```

D는 B와 C 둘 다에서 영향을 받는다. **실제 비즈니스는 항상 Graph다.** 트리로 모델링하면 "브랜드 인지도"가 "학생 모집"과 "재등록" 양쪽에 기여한다는 사실을 표현할 수 없다.

### Goal Graph는 Task Graph가 아니다

❌ `T3 → T5 → T7` — 이건 [Task Graph](e005a-task-graph.md)(Entity 005-A)다.

| | Goal Graph | Task Graph |
|---|---|---|
| 노드 | Goal (미래 상태) | Task (행위) |
| 간선 | **6종** (DEPENDS_ON, ENABLES, …) | **1종** (depends_on) |
| 생성 | 사용자 + Goal Engine | Planner |
| 소비 | Planner | Runtime Engine |
| 수명 | 장기 (Goal과 함께) | 단기 (Plan과 함께) |
| 담는 것 | **왜** | **어떻게** |

간선 유형이 6종인 이유는 Goal 간 영향이 단순 선후 관계가 아니기 때문이다. Task Graph는 "무엇이 무엇을 막는가"만 알면 되므로 1종으로 충분하다([Rule TG-001](e005a-task-graph.md)).

### Goal Graph는 Workflow가 아니다

❌ `운영 → 측정 → 개선 → 운영` — 순환이다. Goal Graph는 DAG이므로 표현할 수 없다.

반복 운영은 [Workflow](e022-workflow.md)(Entity 022)의 명시적 `loop`로 표현한다(§12).

| 개념 | 담당 |
|---|---|
| Goal Graph | 무엇을 달성할 것인가 |
| [Workflow](e022-workflow.md) | 어떻게 반복적으로 운영할 것인가 |

### Goal Graph는 조직도가 아니다

❌ `대표 → 실장 → 강사`

Goal Graph의 계층은 **목표의 포함 관계**이지 사람의 보고 라인이 아니다. 소유자는 각 Goal의 `stakeholders.owner`에 있다([Rule G-007](e001-goal.md)).

---

## 3. Design Principles

### Rule GG-001 — 간선은 유형과 방향을 가진다

`SUPPORTS`와 `DEPENDS_ON`은 서로 다른 의미이며 임의로 바꿀 수 없다. 유형 없는 간선은 추가할 수 없다.

### Rule GG-002 — DAG를 유지한다

순환 검사는 **간선 추가 시점**에 수행한다. 그래프 완성 후 검사하면 어디서 잘못됐는지 알기 어렵다([Rule TG-002](e005a-task-graph.md)와 같은 원칙).

### Rule GG-003 — 고립된 Goal을 관리하지 않는다

모든 Goal은 최소 하나의 상위 목적 또는 Root Goal과 연결되어야 한다. 고립된 Goal은 어느 상위 목적에도 기여하지 않으므로 자원을 배분할 근거가 없다.

**단, Root Goal 자체는 예외다.** Root는 상위가 없다.

### Rule GG-004 — Completed Goal은 직접 수정하지 않는다

변경이 필요하면 새 버전을 만들거나 후속 Goal을 만든다([INV-G-05](e001-goal.md)).

### Rule GG-005 — 변경은 전파된다

Goal이 변경되면 영향받는 모든 Goal을 갱신해야 한다(§9.2 Goal Propagation). **전파하지 않으면 그래프가 조용히 불일치 상태가 된다.**

### Rule GG-006 — Score는 그래프 위치를 반영한다

Goal의 우선순위는 자기 속성만으로 결정되지 않는다. 하위 Goal이 많거나 여러 Goal을 `ENABLES`하는 노드는 더 중요하다(§4.3).

### Rule GG-007 — 충돌을 숨기지 않는다

`CONFLICTS_WITH`는 제거 대상이 아니라 **명시 대상**이다. 충돌하는 두 Goal이 동시에 Active일 수 있으며, 해소는 사용자 판단이다(§11).

---

## 4. Attributes

Goal Graph 자체가 갖는 속성이다. 노드의 속성은 [e001 §4](e001-goal.md)에 있다.

```
Goal Graph
├── Identity
│   ├── graph_id
│   ├── owner_scope        (조직 / 사용자)
│   └── version
├── Structure
│   ├── nodes[]            (goal_id)
│   ├── edges[]            ({from, to, relationship})
│   └── root_goals[]
└── Analysis
    ├── blocked_goals[]
    ├── conflict_pairs[]
    └── critical_goals[]
```

| 속성 | 의미 | 예 |
|---|---|---|
| **graph_id** | 식별자 | `gg_org_001` |
| **nodes** | Goal 목록 | `["goal_001", "goal_004", …]` |
| **edges** | 유형 간선 | `[{from: "goal_004", to: "goal_001", relationship: "SUPPORTS"}]` |
| **root_goals** | 상위가 없는 Goal | `["goal_000"]` |
| **blocked_goals** | `BLOCKS` 간선의 대상 | `["goal_009"]` |
| **conflict_pairs** | 충돌 쌍 | `[["goal_001", "goal_007"]]` |
| **critical_goals** | 하위 도달 집합이 큰 Goal (§4.3) | `["goal_004"]` |

### 4.1 Goal Relationship Types

여기가 핵심이다. Goal들은 여섯 가지 관계를 가진다.

| 관계 | 의미 | 예 | Planner의 반응 |
|---|---|---|---|
| `DEPENDS_ON` | 선행 Goal이 없으면 어렵다 | 학생 모집 → 브랜드 구축 | 선행을 먼저 계획 |
| `REQUIRES` | 선행 없이는 **불가능**하다 | 앱 출시 → 개발 완료 | 선행 미완이면 실행 차단 |
| `ENABLES` | 다른 Goal을 가능하게 만든다 | 유튜브 성장 → 브랜드 인지도 | 하위 Goal의 Score 상향 |
| `SUPPORTS` | 도움은 되지만 필수는 아니다 | 후기 확보 → 학생 모집 | 여유 자원이 있을 때 배분 |
| `CONFLICTS_WITH` | 서로 충돌한다 | 광고비 절감 ↔ 학생 모집 최대화 | 트레이드오프 제시 (§11) |
| `BLOCKS` | 완전히 막는다 | 법적 문제 → 서비스 출시 | 대상 Goal을 `Suspended`로 |

**`DEPENDS_ON`과 `REQUIRES`의 차이가 중요하다.** 전자는 "없으면 어렵다"(연기 가능), 후자는 "없으면 불가능"(차단). 이 구분이 Planner의 행동을 가른다.

`CONFLICTS_WITH`는 **유일한 무방향 관계**다. 나머지 다섯은 방향을 가진다.

### 4.2 Goal Hierarchy

Goal은 계층을 가진다. 계층은 `parent_goal` / `child_goals`로 표현되며, 위 6종 관계와는 **별개의 축**이다.

```
Company Goal
│
├── Revenue
│     ├── Student Acquisition ◀──SUPPORTS── Review Collection
│     ├── Retention
│     └── Upsell
│
└── Brand
      ├── YouTube ──ENABLES──▶ (Brand Awareness)
      ├── SNS
      └── PR
```

계층은 트리이지만 **6종 관계 간선이 계층을 가로지른다.** 그래서 전체는 Graph다.

### 4.3 Goal Score

Goal의 우선순위는 하나의 숫자가 아니다.

$$Score = w_p P + w_i I + w_u U - w_r R + w_c C$$

| 기호 | 의미 | 출처 |
|---|---|---|
| $P$ | Priority | 사용자 선언 |
| $I$ | Impact | 상위 Goal 기여도 |
| $U$ | Urgency | 마감까지 남은 시간 |
| $R$ | Risk | [Risk Entity](e018-risk.md)의 severity 합 |
| $C$ | Confidence | `quality.confidence` |

**Rule GG-006에 따라 그래프 위치가 반영된다.** 하위 도달 집합이 큰 Goal은 $I$가 높아진다.

$$I(g) = base(g) + \alpha \cdot |\{u \in V : g \rightsquigarrow u \text{ via ENABLES/SUPPORTS}\}|$$

이 Score는 Planner가 **어떤 Goal을 먼저 처리할지** 결정할 때 사용되며, [Intent Priority](e002-intent.md)와 [Task 우선순위](e005a-task-graph.md)로 상속된다.

---

## 5. Invariants

### INV-GG-01 — 순환이 존재하지 않는다

[INV-08](e000a-entity-relationships.md)의 Goal Graph 측 표현이다.

| | |
|---|---|
| **위반 시** | 간선 추가를 롤백하고 순환 경로를 오류로 반환한다 |
| **탐지** | 간선 추가 시점 (증분 순환 검사) |
| **근거** | `A → B → A`는 Planner를 무한 루프에 빠뜨린다 |

### INV-GG-02 — 고립된 Goal은 실행되지 않는다

| | |
|---|---|
| **위반 시** | Goal을 `Suspended`로 두고 Planner에 전달하지 않는다. Root Goal은 예외 (Rule GG-003) |

### INV-GG-03 — 간선은 유형을 가진다

| | |
|---|---|
| **위반 시** | 생성 거부. 유형 없는 간선은 Planner가 해석할 수 없다 (Rule GG-001) |

### INV-GG-04 — Completed Goal은 수정되지 않는다

| | |
|---|---|
| **위반 시** | 쓰기 거부 ([INV-G-05](e001-goal.md)). 완료된 목표의 목표치를 사후에 낮추면 성과 평가가 무의미해진다 |

### INV-GG-05 — REQUIRES 선행이 미완인 Goal은 Executing이 될 수 없다

| | |
|---|---|
| **위반 시** | 상태 전이를 차단한다. `DEPENDS_ON`은 연기만 유발하지만 `REQUIRES`는 차단이다 |

### INV-GG-06 — BLOCKS의 대상은 Suspended가 된다

| | |
|---|---|
| **위반 시** | 막힌 Goal에 자원이 계속 배분된다. 상태 전이를 강제한다 |

### INV-GG-07 — 변경은 영향 범위에 전파된다

| | |
|---|---|
| **위반 시** | 그래프가 조용히 불일치 상태가 된다. 예산이 바뀌었는데 하위 Goal 목표치가 그대로면 Plan이 잘못된 전제 위에 선다 (Rule GG-005) |

### INV-GG-08 — CONFLICTS_WITH는 자동으로 해소되지 않는다

| | |
|---|---|
| **위반 시** | 시스템이 임의로 한쪽 Goal을 폐기하면 사용자의 의도가 사라진다. 트레이드오프를 제시하고 판단을 요청한다 (Rule GG-007) |

---

## 6. Lifecycle

Goal Graph는 노드가 계속 추가·제거되는 **살아있는 구조**이므로 자체 상태가 단순하다.

```
Empty → Active ──▶ Archived
           │
           └──▶ Inconsistent ──▶ Active   (전파 완료 후 복구)
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Empty** | 노드 없음 | 초기화 |
| **Active** | 정상. Planner가 참조 | 첫 Goal 추가 |
| **Inconsistent** | 전파 미완. 일부 Goal이 낡은 전제 위에 있음 | Propagation 진행 중 (§9.2) |
| **Archived** | 조직/사용자 종료 | 계정 종료 |

**`Inconsistent` 상태에서는 새 Plan을 생성하지 않는다.** 전파가 끝나지 않은 그래프로 계획하면 곧 폐기될 Plan을 만들게 된다.

노드([Goal](e001-goal.md))의 생명주기는 별도다 → [Entity 001-C](e001c-goal-state-machine.md).

---

## 7. Relationships

```
Goal Graph 001-A
   │
   ├──노드──▶ Goal 001
   ├──입력──▶ Planner ──▶ Plan 008 ──▶ Task Graph 005-A
   ├──전파──▶ Context 003 (변경 감지의 진원지)
   ├──반영──▶ Risk 018 / Assumption 017 (Score의 R 항)
   └──질의──▶ Session 021 (사용자 조회)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Goal](e001-goal.md) | 그래프의 노드 | `Goal Graph 1:N Goal` |
| [Plan](e008-plan.md) | Planner가 Goal Graph 전체를 입력으로 받는다 | `Goal Graph 1:N Plan` |
| [Task Graph](e005a-task-graph.md) | 대칭 구조. Goal Graph가 왜, Task Graph가 어떻게 | 대응 관계 |
| [Context](e003-context.md) | Context 변경이 Propagation의 주된 진원지다 | `Context N:M Goal Graph` |
| [Assumption](e017-assumption.md) | 가정 무효화가 Propagation을 유발한다 | `Assumption 1:0..N Goal Graph` |
| [Risk](e018-risk.md) | Goal Score의 $R$ 항 | `Risk N:M Goal` |
| [Workflow](e022-workflow.md) | 순환 운영은 Workflow가 담당한다 (§2, §12) | 역할 분담 |

### 7.1 Goal Graph와 Planner

이 부분이 기존 AI 에이전트와 가장 큰 차별점이다.

```
대부분의 AI 에이전트          Intent OS
Goal                        Goal Graph
  ↓                           ↓
Plan                        Planner  (= 컴파일러)
                              ↓
                            Plan + Task Graph
```

Planner는 Goal 하나를 보고 계획을 세우는 것이 아니라, **Goal Graph 전체를 입력으로 받아 실행 구조를 생성하는 컴파일러**다([e008 §1.1](e008-plan.md)).

여러 목표가 동시에 존재하는 실제 조직에서는 목표 간 **의존성·충돌·우선순위**를 함께 고려해야 하기 때문이다.

---

## 8. Canonical Representation

```json
{
  "graph_id": "gg_org_001",
  "owner_scope": "org:hongdae_academy",
  "version": 4,
  "nodes": ["goal_000", "goal_001", "goal_004", "goal_005", "goal_007"],
  "edges": [
    { "from": "goal_001", "to": "goal_000", "relationship": "SUPPORTS" },
    { "from": "goal_004", "to": "goal_001", "relationship": "SUPPORTS" },
    { "from": "goal_005", "to": "goal_001", "relationship": "DEPENDS_ON" },
    { "from": "goal_007", "to": "goal_001", "relationship": "CONFLICTS_WITH" }
  ],
  "root_goals": ["goal_000"],
  "analysis": {
    "blocked_goals": [],
    "conflict_pairs": [["goal_001", "goal_007"]],
    "critical_goals": ["goal_001"]
  },
  "status": "Active"
}
```

그래프 형태는 다음과 같다.

```
                    goal_000 (연 매출 성장)
                         ▲ SUPPORTS
                    goal_001 (윈터캠프 100명 모집)  ◀──CONFLICTS_WITH──▶ goal_007 (광고비 20% 절감)
                    ▲                    ▲
        SUPPORTS    │                    │  DEPENDS_ON
                goal_004              goal_005
             (랜딩 전환율 3%)      (월 상담 문의 40건)
```

기계가 읽을 수 있는 스키마: [`goal-graph.schema.json`](../intent-os-spec/schemas/goal-graph.schema.json)

---

## 9. Validation Rules

### 9.1 간선 추가 검증

```
간선 추가 요청 (from, to, relationship)
  ↓
두 Goal 존재 확인
  ↓
relationship 유형 확인 (INV-GG-03) ── 미지정 시 거부
  ↓
증분 순환 검사 (INV-GG-01)
  └── CONFLICTS_WITH는 무방향이므로 순환 검사에서 제외
  ↓
중복 간선 검사
  └── 같은 쌍에 다른 유형이 이미 있으면 경고 (의미 충돌 가능)
  ↓
간선 추가 → analysis 재계산
  ├── root_goals
  ├── blocked_goals (BLOCKS 대상)
  ├── conflict_pairs
  └── critical_goals (§4.3의 도달 집합)
  ↓
영향받는 Goal의 Score 재계산 (Rule GG-006)
  ↓
Event 발행 (goal_graph.edge_added)
```

### 9.2 Goal Propagation

**Intent OS에서 가장 중요한 알고리즘 중 하나다.**

Goal이 변경되면 영향을 받는 모든 Goal을 자동으로 갱신해야 한다.

```
변경 감지 (Goal 목표치 / Context / Assumption 무효화)
  ↓
Goal Graph → Inconsistent
  ↓
영향 범위 계산
  변경된 Goal에서 역방향으로 도달 가능한 노드 집합
  (SUPPORTS / ENABLES / DEPENDS_ON / REQUIRES 를 따라)
  ↓
각 영향 Goal에 대해
  ├── 목표치 재계산 (하위 기여도 변화 반영)
  ├── Score 재계산 (§4.3)
  ├── Assumption 재검증 트리거 → e017 §9.2
  └── Active Plan이 있으면 Replanning 트리거 → e008 §6.2
  ↓
전파 완료 → Active 복귀
  ↓
Event 발행 (goal.propagated)
```

예)

```
광고 예산: 300만원 → 200만원 (Context 변경)
  ↓ 영향 범위: goal_001, goal_004, goal_005
goal_001  목표 100명 → 예상 도달 65명
          Score 0.88 → 0.71 (Urgency 상승, Confidence 하락)
goal_004  랜딩 전환율 3% → 4.5% (예산 감소를 전환율로 보상해야 함)
goal_005  상담 문의 40건 → 55건
  ↓
asm_012 Invalidated → plan_014 Suspended → Replanning
```

**전파의 실제 발화 지점은 대부분 [Context](e003-context.md) 변경이다**([e003 §9.2](e003-context.md)).

### 9.3 Goal Graph Query

Intent OS는 Goal Graph를 질의할 수 있어야 한다.

| 질의 | 계산 | 결과 예 |
|---|---|---|
| 학생 모집에 가장 큰 영향을 주는 Goal은? | 역방향 SUPPORTS/ENABLES 도달 집합 | 브랜드, SNS, 유튜브, 후기 |
| 가장 위험한 Goal은? | Risk severity 합 내림차순 | 앱 출시 |
| 현재 막혀 있는 Goal은? | `blocked_goals` | 개발 완료 |
| 충돌 중인 Goal 쌍은? | `conflict_pairs` | 광고비 절감 ↔ 학생 모집 |
| 지금 무엇부터 해야 하는가? | Score 내림차순 + REQUIRES 만족 필터 | goal_005 |

---

## 10. Examples

### 10.1 예시 1 — 계층을 가로지르는 간선

```
goal_000  연 매출 성장            (Root)
├── goal_001  윈터캠프 100명 모집
│   ├── goal_004  랜딩 전환율 3%
│   └── goal_005  월 상담 문의 40건
└── goal_010  브랜드 인지도 향상
    └── goal_011  후기 30건 확보

추가 간선 (계층을 가로지른다)
goal_011 ──SUPPORTS──▶ goal_004    (후기가 랜딩 전환율을 올린다)
goal_010 ──ENABLES───▶ goal_001    (인지도가 모집을 쉽게 만든다)
```

트리만 봤다면 `goal_011`(후기 확보)이 `goal_004`(랜딩 전환율)에 기여한다는 것을 알 수 없다. **Planner는 이 간선 때문에 후기 확보를 랜딩페이지 개선보다 먼저 계획한다.**

### 10.2 예시 2 — DEPENDS_ON vs REQUIRES

```
goal_005 (상담 문의 40건) ──DEPENDS_ON──▶ goal_001 (모집 100명)
   → 문의가 없어도 모집을 시도할 수는 있다. 어려울 뿐이다.
   → Planner: goal_005를 먼저 계획하되 goal_001을 차단하지 않는다

goal_020 (사업자 등록 완료) ──REQUIRES──▶ goal_021 (광고 집행)
   → 사업자 등록 없이는 광고를 집행할 수 없다
   → Planner: goal_020이 Completed가 아니면 goal_021의 Executing 전이를 차단 (INV-GG-05)
```

### 10.3 예시 3 — Propagation

§9.2의 예시가 실제로 어떻게 흐르는지.

```
2026-08-15 10:12  ctx_001 변경: 예산 300만 → 200만
  ↓
Goal Graph → Inconsistent
  ↓ 역방향 도달 집합 계산
영향: goal_001 (직접), goal_004 / goal_005 (하위)
  ↓
goal_001  desired_state.target 100 유지, 예상 도달 65 기록
          Score 0.88 → 0.71
goal_004  target 3% → 4.5%   (예산 감소를 전환율로 보상)
goal_005  target 40 → 55건
  ↓
asm_012 Invalidated → plan_014 Suspended
  ↓
Goal Graph → Active
plan_015 생성
```

**목표치를 자동으로 낮추지 않았다.** `target 100`은 유지하고 "예상 도달 65"를 별도로 기록한다 — 목표를 낮추는 것은 사용자의 결정이다.

### 10.4 예시 4 — 충돌

```
goal_001  윈터캠프 100명 모집     Score 0.88
goal_007  광고비 20% 절감         Score 0.61
   ↕ CONFLICTS_WITH
```

시스템은 한쪽을 폐기하지 않는다(INV-GG-08). 대신 트레이드오프를 제시한다.

```
제시:
  ① goal_001 우선  → 광고비 절감 목표를 10%로 완화. 모집 예상 92명
  ② goal_007 우선  → 모집 목표를 75명으로 조정. 절감 20% 달성
  ③ 둘 다 유지     → 자연 유입(SEO) 비중 확대. 기간 6주 → 12주 필요
  ↓
사용자 선택 ① → goal_007의 target 20% → 10%로 수정 (새 version)
             → CONFLICTS_WITH 간선 유지 (긴장 관계는 사라지지 않았다)
```

### 10.5 예시 5 — BLOCKS

```
goal_030  과장 광고 심의 이슈 해소
   │ BLOCKS
   ▼
goal_021  광고 집행
   ↓ INV-GG-06
goal_021 → Suspended
plan_022 → Suspended
진행 중 Execution → Aborted
   ↓ goal_030 Completed
goal_021 → Executable 복귀
```

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **Goal 하나짜리 그래프** | 정상이다. `root_goals` 1개, `edges` 0개. Rule GG-003의 Root 예외에 해당한다 |
| **CONFLICTS_WITH가 순환처럼 보임** | 무방향 관계이므로 순환 검사에서 제외한다(§9.1). A↔B는 순환이 아니다 |
| **두 Goal이 서로 SUPPORTS** | 순환이다. 거부한다(INV-GG-01). 실제로는 공통 상위 Goal이 있고 둘 다 그것을 SUPPORTS하는 구조일 가능성이 높다 |
| **전파 도중 또 다른 변경 발생** | 진행 중인 Propagation에 흡수한다. 변경마다 전파를 새로 시작하면 수렴하지 않는다([Plan §11](e008-plan.md)의 Replanning Storm과 같은 문제) |
| **Root Goal이 여러 개** | 정상이다. 조직에 독립적인 최상위 목적이 여럿일 수 있다. 다만 5개를 넘으면 상위 목적이 불명확하다는 신호다 |
| **Completed Goal이 CONFLICTS_WITH를 가짐** | 간선을 유지한다. "이 둘은 긴장 관계였다"는 사실이 다음 Planning의 입력이다 |
| **BLOCKS 대상이 이미 Completed** | 간선을 무시한다. 이미 끝난 일을 막을 수 없다. 정합성 경고만 남긴다 |
| **그래프가 200노드를 넘음** | Propagation 비용이 커진다. `owner_scope`로 그래프를 분할하고 경계 간선만 유지하는 방안이 필요하다(§12) |
| **순환 운영이 필요함** | Goal Graph로 표현하지 않는다. [Workflow](e022-workflow.md)의 `loop`를 쓴다(§2) |

---

## 12. Open Issues (v2.0)

### ✅ v1.0에서 해소된 항목

| v1.0 Open Issue | 해소 |
|---|---|
| DAG와 순환 사이클 — 반복 목표를 어떻게 표현하는가 | [Workflow](e022-workflow.md)(Entity 022)의 명시적 `loop` + `max_iterations`로 확정. Goal Graph는 DAG를 유지한다 |
| Workflow Graph / Control Loop의 소재 | Volume 3가 아니라 Entity 022로 독립 |
| Goal Graph Invariants의 형식화 | INV-GG-01 ~ 08로 번호화. 위반 시 시스템 반응 명시 |

### Propagation의 수렴 보장

§9.2는 영향 범위를 계산해 갱신하지만, 갱신된 Goal이 또 다른 Goal에 영향을 주는 연쇄가 언제 멈추는지 보장하지 않는다. DAG이므로 이론상 유한하지만, 실무적으로는 감쇠 규칙(영향도가 임계값 미만이면 전파 중단)이 필요하다.

### 목표치 자동 재계산의 근거

§10.3에서 `goal_004`의 target을 3% → 4.5%로 올렸다. **이 수치의 근거가 무엇인가.** 현재는 "예산 감소분을 전환율로 보상"이라는 서술적 규칙뿐이며, 계산 모델이 없다. [Plan의 Expected Success Probability](e008-plan.md)와 같은 예측 모델을 공유해야 한다.

### 그래프 분할

§11이 지적한 문제다. 조직 전체의 Goal Graph가 커지면 Propagation과 Query 비용이 커진다. `owner_scope` 단위 분할과 경계 간선 처리 규칙이 없다.

### Score 가중치의 출처

§4.3의 $w_p, w_i, w_u, w_r, w_c$가 어디서 오는가. [Decision Utility](e009-decision.md)의 Dynamic Weight처럼 상황에 따라 달라져야 하는지, 조직 정책으로 고정해야 하는지 미정이다.

### 앞으로 보강해야 할 항목

- Propagation 감쇠 규칙
- 목표치 재계산 모델 (Plan 예측 모델과 공유)
- 그래프 분할과 경계 간선 규칙
- 실제 예시 30~50개
