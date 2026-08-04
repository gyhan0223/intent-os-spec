# Entity 001-A: Goal Graph Specification

- **Version:** v1.0 Draft
- **Status:** Core Architecture
- **Last Updated:** 2026-08-03

---

## 0. Why Not Just an Object

지금까지 Goal을 하나의 객체(Object)처럼 정의했는데, 이건 **프로젝트 관리 도구(Jira, Asana, Notion)** 수준의 사고방식이다.

우리가 만들려는 것은 **운영체제**다.

운영체제는 객체 하나보다 **객체들의 관계(Relationship)** 를 더 중요하게 생각한다. Linux에서 중요한 것은 Process 하나가 아니라 **Process Tree**인 것처럼.

그래서 Goal을 "점(Node)"이 아니라 **"그래프(Graph)"** 로 정의한다.

---

## 1. Purpose

Goal Graph는 Intent OS 내부에서 모든 Goal의 관계를 표현하는 **최상위 데이터 구조**이다.

Intent OS는 Goal 하나를 실행하지 않는다. **Goal Graph 전체를 최적화한다.**

> **Planning, Decision, Learning은 모두 Goal Graph를 기준으로 동작한다.**

---

## 2. Why Goal Graph Exists

기존 AI:

```
Prompt → Answer
```

기존 Task Manager:

```
Task → Task → Task
```

Intent OS:

```
Goal → Goal Network → Planning → Execution
```

차이점은 **Goal들이 서로 영향을 준다**는 것이다.

---

## 3. Formal Definition

수학적으로 Goal Graph는 다음과 같이 정의한다.

$$GG = (V, E)$$

- $V$ — Goal들의 집합: $V = \{G_1, G_2, G_3, \dots, G_n\}$
- $E$ — Goal 사이의 관계(Relationship)의 집합

---

## 4. Goal Node

그래프의 노드는 Goal이다.

```
G1: 학생 100명 모집
G2: 브랜드 인지도 향상
G3: 유튜브 채널 성장
G4: 매출 증가
```

---

## 5. Goal Relationship

여기가 핵심이다. Goal들은 여러 관계를 가진다.

| 관계 | 의미 | 예 |
|---|---|---|
| `DEPENDS_ON` | 선행 Goal이 없으면 어렵다 | 학생 모집 → 브랜드 구축 |
| `ENABLES` | 다른 Goal을 가능하게 만든다 | 유튜브 성장 → 브랜드 인지도 |
| `CONFLICTS_WITH` | 서로 충돌한다 | 광고비 절감 ↔ 학생 모집 최대화 |
| `REQUIRES` | 필수 관계 | 앱 출시 → 개발 완료 |
| `SUPPORTS` | 도움은 되지만 필수는 아니다 | 후기 확보 → 학생 모집 |
| `BLOCKS` | 완전히 막는다 | 법적 문제 → 서비스 출시 |

---

## 6. Goal Hierarchy

Goal은 계층을 가진다.

```
Company Goal
│
├── Revenue
│     ├── Student Acquisition
│     ├── Retention
│     └── Upsell
│
└── Brand
      ├── YouTube
      ├── SNS
      └── PR
```

하지만 이건 Tree가 아니다.

---

## 7. Goal Tree vs Goal Graph

Tree:

```
A
├── B
└── C
```

Graph:

```
A
├── B
│     ↘
│       D
└── C ↗
```

D는 B와 C 둘 다 영향을 준다.

**실제 비즈니스는 항상 Graph이다.**

---

## 8. Goal State

모든 Goal은 상태를 가진다.

```
Draft → Clarifying → Confirmed → Planning → Executing → Monitoring → Completed → Archived
```

---

## 9. Goal Weight

Goal마다 중요도가 다르다.

```
Priority
Impact
Urgency
Risk
Confidence
```

예)

```
학생 모집
  Priority: 10
  Impact:   9
  Urgency:  10
  Risk:     5
```

---

## 10. Goal Score

Goal의 우선순위는 하나의 숫자가 아니다. 예를 들어,

$$Score = w_p P + w_i I + w_u U - w_r R + w_c C$$

- $P$ — Priority
- $I$ — Impact
- $U$ — Urgency
- $R$ — Risk
- $C$ — Confidence

이 Score는 Planner가 **어떤 Goal을 먼저 처리할지** 결정할 때 사용된다.

---

## 11. Goal Lifecycle

Goal은 살아있는 객체다.

```
Created → Clarified → Confirmed → Planning → Executing → Monitoring → Learning → Completed → Archived
```

**Learning이 끝나면 다음 Goal의 Planning 정확도가 올라간다.**

---

## 12. Goal Context

Goal은 혼자 존재하지 않는다.

```
Goal
  ↓
Context
  ↓
Current State / Environment / Stakeholders / Constraints / History
```

Planner는 Goal만 보면 안 된다. **Context도 반드시 고려한다.**

---

## 13. Goal Graph Query

Intent OS는 Goal Graph를 질의(Query)할 수 있어야 한다.

| 질의 | 결과 예 |
|---|---|
| 학생 모집에 가장 큰 영향을 주는 Goal은? | 브랜드, SNS, 유튜브, 후기 |
| 가장 위험한 Goal은? | 앱 출시 |
| 현재 막혀있는 Goal은? | 개발 완료 |

---

## 14. Goal Propagation

Intent OS에서 가장 중요한 알고리즘 중 하나다.

**Goal이 변경되면 영향을 받는 모든 Goal을 자동으로 업데이트해야 한다.**

예)

```
광고 예산: 300만원 → 100만원
```

그러면

```
학생 모집 예상: 100명 → 65명
```

Planner도 자동으로 다시 계산한다. 이걸 **Goal Propagation**이라고 정의한다.

---

## 15. Goal Graph Invariants

운영체제 수준의 명세라면 **절대 깨지면 안 되는 규칙(Invariant)** 을 정의해야 한다.

1. **순환 의존(Cycle)은 허용하지 않는다.** `A → B → A` 같은 구조는 Planner를 무한 루프에 빠뜨릴 수 있다.
2. **모든 Goal은 최소 하나의 상위 목적 또는 최상위 Root Goal과 연결되어야 한다.** 고립된 Goal은 시스템이 관리하지 않는다.
3. **Goal 간 관계는 방향성과 의미를 가진다.** `SUPPORTS`와 `DEPENDS_ON`은 서로 다른 의미이며 임의로 바꿀 수 없다.
4. **Completed 상태의 Goal은 직접 수정하지 않는다.** 변경이 필요하면 새 버전을 생성하거나 후속 Goal을 만든다.

이 규칙들은 시스템 전체의 일관성을 유지하는 데 중요하다.

---

## 16. Goal Graph와 Planner의 관계

이 부분이 기존 AI 에이전트들과 가장 큰 차별점이다.

대부분의 AI 에이전트는 이렇게 생각한다.

```
Goal
  ↓
Plan
```

Intent OS는 이렇게 정의한다.

```
Goal Graph
  ↓
Planner
  ↓
Execution Graph
```

즉, Planner는 Goal 하나를 보고 계획을 세우는 것이 아니라, **Goal Graph 전체를 입력으로 받아 실행 그래프(Execution Graph)를 생성하는 컴파일러**에 가깝다.

이 관점이 중요한 이유는, 여러 목표가 동시에 존재하는 실제 조직이나 서비스에서는 목표 간의 **의존성, 충돌, 우선순위**를 함께 고려해야 하기 때문이다.

---

## 17. Open Issue — DAG와 순환 사이클

§15에서 Goal Graph를 **DAG(Directed Acyclic Graph)** 로 제한했다.

하지만 실제 세계에는 반복적인 목표도 존재한다.

- 고객 피드백 수집 → 제품 개선 → 고객 만족 향상 → 더 많은 피드백
- 운영 → 측정 → 개선 → 운영

같은 순환적인 관리 사이클이 있다.

### 설계 결정 (v1.0)

**Goal Graph 자체는 DAG로 유지**하고, 반복은 별도의 **Workflow Graph** 또는 **Control Loop** 개념으로 표현한다.

| 개념 | 담당 |
|---|---|
| Goal (Graph) | 무엇을 달성할 것인가 |
| Workflow (Graph / Control Loop) | 어떻게 반복적으로 운영할 것인가 |

이렇게 하면 역할이 분명하게 분리된다. Workflow Graph / Control Loop는 **Runtime Specification**([Volume 3](../v3-runtime.md))에서 함께 정의하는 것이 가장 자연스럽다.
