# Entity 005: Task

- **Version:** v1.0 Draft
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

❌ `학생 100명 모집` — 이건 Task가 아니다. Goal이다.

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

Prompt는 특정 Resource(LLM)에게 보내는 **실행 시점의 입력 표현**이다. Task는 Resource가 결정되기 전에 존재하는 **Resource 중립적** 객체다. 같은 Task라도 Resource가 Claude면 Prompt로, 사람이면 업무 지시서로 변환된다.

### Task는 Execution이 아니다

❌ `광고 카피 작성 중 (34% 진행)` — 이건 Execution(Process)이다.

Task는 Entity고 Execution은 Task가 수행되는 **과정**이다. ([README.md](README.md) §1의 Entity / Process 구분 참조)

---

## 3. Task의 조건

Task는 반드시 아래 조건을 만족해야 한다.

### Rule T-001 — 독립적으로 실행 가능해야 한다

의존하는 Task가 완료되었다는 전제 하에, **추가 정보 없이 하나의 Resource에 할당 가능해야 한다.**

- ✅ `윈터캠프 타겟(예비 고3 학부모)용 인스타그램 광고 카피 3종 작성`
- ❌ `마케팅 잘하기` — 할당 불가능. 분해가 필요하다.

### Rule T-002 — 기대 출력(Expected Output)이 정의되어야 한다

✅ `경쟁 학원 5곳의 가격/커리큘럼 비교표`

❌ `경쟁사 좀 알아보기` — 무엇이 나오면 완료인지 알 수 없다.

### Rule T-003 — Required Capabilities를 명시해야 한다

**이것이 Task의 가장 중요한 속성이다.** Decision Engine은 Task의 `required_capabilities`와 Resource의 `capabilities`를 매칭해서 실행 주체를 선택한다. Capability가 비어 있는 Task는 라우팅할 수 없다.

### Rule T-004 — Resource 이름을 포함하면 안 된다

❌ `Claude로 카피 작성`

분석 결과:

```
Task:       광고 카피 작성
Capability: language.generation.copywriting
Resource:   (Decision Engine이 결정)
```

Resource 선택은 Task의 소관이 아니다. (Principle 03 — Resource Agnostic, [Volume 1](../v1-core-concepts.md))

### Rule T-005 — 반드시 Goal에 연결되어야 한다

어떤 Goal에도 기여하지 않는 Task는 시스템이 관리하지 않는다. Goal Graph Invariant 2("고립된 Goal은 관리하지 않는다")와 동일한 원칙이다.

---

## 4. Task Attributes

Task는 최소한 아래 속성을 가진다.

```
Task
├── Objective
├── Goal Link
├── Required Capabilities
├── Dependencies
├── Expected Output
├── Execution Mode
├── Constraints
├── Priority
├── Retry Policy
└── State
```

| 속성 | 의미 | 예 |
|---|---|---|
| **Objective** | 무엇을 하는가 | `인스타그램 광고 카피 3종 작성` |
| **Goal Link** | 어느 Goal에 기여하는가 | `goal_001 (학생 100명 모집)` |
| **Required Capabilities** | 필요한 능력 목록 | `language.generation.copywriting`, `analysis.audience` |
| **Dependencies** | 선행 Task | `task_002 (타겟 분석)` 완료 후 |
| **Expected Output** | 완료 판정 기준이 되는 산출물 | `카피 3종 + 각 카피의 타겟 근거` |
| **Execution Mode** | 실행 방식 | `sequential` / `parallel` / `conditional` |
| **Constraints** | Task 수준 제약 | `건당 비용 5,000원 이하`, `24시간 이내` |
| **Priority** | Task Graph 내 우선순위 | High |
| **Retry Policy** | 실패 시 행동 | 최대 2회 재시도 후 Resource 재선택 |
| **State** | 상태 머신의 현재 상태 | Pending |

---

## 5. Task Decomposition

Goal은 직접 실행되지 않는다. **Planner가 Goal을 Task로 분해한다.**

```
Goal: 윈터캠프 100명 모집
  ↓ Decomposition
Task Graph:
  T1  시장 조사
  T2  경쟁 분석
  T3  타겟 분석
  T4  광고 카피 작성        (T3 의존)
  T5  랜딩페이지 개선        (T2, T4 의존)
  T6  상담 프로세스 설계
  T7  성과 분석             (T5, T6 의존)
```

### 분해 규칙

1. **각 Task는 Rule T-001~T-005를 만족할 때까지 분해한다.**
2. **분해 결과의 합집합이 Goal 달성을 커버해야 한다.** 빠진 영역이 있으면 Planner는 Task를 추가한다.
3. **Task 간 중복 작업은 제거한다.** 두 Task가 같은 산출물을 만들면 하나로 합치고 의존 관계로 연결한다.
4. **분해는 재귀적이다.** Task가 아래 "크기 기준"을 넘으면 Sub-Task로 다시 분해한다.

### Task 크기 기준 — 더 분해해야 하는가?

다음 중 하나라도 해당되면 **더 분해한다.**

| 판정 질문 | 예 |
|---|---|
| 서로 다른 Capability 도메인을 3개 이상 요구하는가? | `조사 + 카피 작성 + 디자인` → 3개 Task로 분리 |
| Expected Output이 2개 이상인가? | `비교표와 광고 시안` → 분리 |
| 단일 Resource가 처리하기 어려운가? | 검색과 장문 작성을 동시에 요구 → 분리 |
| 실패 시 부분 재시도가 필요한가? | 카피만 다시 쓰면 되는데 조사까지 다시 하게 되는 구조 → 분리 |

반대로, 다음이면 **분해를 멈춘다.**

- 단일 Capability 집합으로 수행 가능하다.
- Expected Output이 하나다.
- 더 쪼개면 조율 비용이 실행 비용보다 커진다.

---

## 6. Task Graph

Task는 혼자 존재하지 않는다. `dependencies`로 연결된 **DAG(Directed Acyclic Graph)** 를 이룬다.

```
        T1 시장 조사        T3 타겟 분석
            │                   │
            ▼                   ▼
        T2 경쟁 분석        T4 광고 카피 작성
            │                   │
            └───────┬───────────┘
                    ▼
            T5 랜딩페이지 개선
                    │
                    ▼
            T7 성과 분석
```

Task Graph는 [Goal Graph](e001a-goal-graph.md)와 대칭 구조다.

| | Goal Graph | Task Graph |
|---|---|---|
| 노드 | Goal (미래 상태) | Task (행위) |
| 관계 | DEPENDS_ON, ENABLES, CONFLICTS_WITH … | dependencies (선행 완료) |
| 생성 주체 | 사용자 + Goal Engine | Planner |
| 소비 주체 | Planner | Runtime Engine |
| 불변식 | 순환 금지 (DAG) | 순환 금지 (DAG) |

**Invariant:** Task Graph에 순환이 생기면 Runtime이 교착 상태에 빠진다. Planner는 Task Graph 생성 시 순환 검사를 반드시 수행한다.

---

## 7. Task State Machine

Task의 상태는 다음 6개뿐이다. ([task.schema.json](../intent-os-spec/schemas/task.schema.json)의 `state` enum과 동일하다.)

```
Pending → Assigned → Running → Completed → Evaluated
                        │
                        ▼
                     Failed ──(재시도)──▶ Pending
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Pending** | 실행 대기 | 생성됨, 또는 재시도 결정됨 |
| **Assigned** | Resource 할당됨 | Decision Engine이 Resource 선택 |
| **Running** | 실행 중 | Runtime이 Execution 시작 |
| **Completed** | 산출물 생성됨 | Expected Output 산출 |
| **Evaluated** | 평가 완료 | Evaluation Engine이 품질/기여도 판정 |
| **Failed** | 실행 실패 | 오류, 타임아웃, 품질 미달 |

**주의:** `Completed ≠ 성공`이다. Completed는 "산출물이 나왔다"는 뜻이고, 좋은 결과인지는 **Evaluated에서 판정**한다. 평가에서 품질 미달이면 Failed로 전이할 수 있다.

### 실패 처리와 재시도

Failed 상태의 Task는 Retry Policy에 따라 처리된다.

```
Failed
  ↓
원인 분류
  ├── Resource 일시 장애      → 같은 Resource로 재시도 (max_retries 이내)
  ├── Resource 능력 부족      → Decision Engine이 다른 Resource 선택 (reassign)
  ├── Task가 너무 큼          → Planner가 재분해 (decompose)
  ├── 입력 정보 부족          → 사용자/상위 Task로 escalate
  └── 재시도 한도 초과        → abort → Goal Graph에 영향 전파
```

실패 이력은 버려지지 않는다. **Resource Intelligence([Volume 4-B](../v4b-resource-intelligence.md))의 학습 데이터가 된다.**

---

## 8. Execution Mode

Task Graph 실행 방식은 세 가지다. ([Volume 3](../v3-runtime.md) Stage 5와 동일)

| Mode | 의미 | 예 |
|---|---|---|
| **sequential** | 선행 Task 완료 후 실행 | 조사 → 분석 → 보고서 |
| **parallel** | 의존이 없는 Task 동시 실행 | 시장 조사 ‖ 경쟁 분석 ‖ 고객 분석 |
| **conditional** | 조건에 따라 실행 여부 결정 | `IF 전환율 < 목표 → 랜딩페이지 개선` |

---

## 9. Task Types

Task는 요구하는 Capability의 성격에 따라 분류된다. Task Type은 Decision Engine의 후보 생성(Candidate Generation)을 좁혀준다.

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

| Type | 예시 |
|---|---|
| **Research Task** | `홍대 지역 경쟁 학원 조사` |
| **Analysis Task** | `광고 채널별 CAC 비교` |
| **Creation Task** | `광고 카피 3종 작성` |
| **Transformation Task** | `상담 녹취록 요약` |
| **Decision Task** | `광고 예산 배분안 선택` |
| **Communication Task** | `학부모 안내 메시지 발송` |
| **Automation Task** | `주간 모집 현황 리포트 생성` |
| **Verification Task** | `랜딩페이지 카피 사실 검증` |

---

## 10. Canonical Task Representation

모든 Task는 내부적으로 동일한 구조를 가진다.

```json
{
  "id": "task_004",
  "goal_id": "goal_001",
  "objective": "인스타그램 광고 카피 3종 작성",
  "required_capabilities": [
    "language.generation.copywriting",
    "analysis.audience"
  ],
  "dependencies": ["task_003"],
  "expected_output": "카피 3종 + 각 카피의 타겟 근거",
  "execution_mode": "sequential",
  "priority": "High",
  "retry_policy": { "max_retries": 2, "on_failure": "reassign" },
  "state": "Pending"
}
```

**이 구조만 Runtime으로 전달된다.**

기계가 읽을 수 있는 스키마: [`task.schema.json`](../intent-os-spec/schemas/task.schema.json)

---

## 11. Task Validation Algorithm

Planner가 생성한 Task는 Runtime에 전달되기 전에 검증된다.

```
Task 후보
  ↓
Goal 연결 확인 (T-005)
  ↓
Resource/Tool 이름 검출 (T-004) ── 검출 시 → Capability로 치환
  ↓
Required Capabilities 존재 확인 (T-003) ── 없으면 → Capability 추론
  ↓
Expected Output 확인 (T-002) ── 없으면 → Planner에 반려
  ↓
크기 기준 검사 (§5) ── 초과 시 → 재분해
  ↓
Task Graph 순환 검사 ── 순환 시 → Planner에 반려
  ↓
Canonical Task 생성
```

---

## 12. 다른 Entity와의 관계

```
Goal ──(분해)──▶ Task ──(요구)──▶ Capability ──(제공)──▶ Resource
                  │
                  └──(수행됨)──▶ Execution ──▶ Outcome ──▶ Feedback
```

| Entity | 관계 |
|---|---|
| [Goal](e001-goal.md) | Task는 정확히 하나의 Goal에 기여한다. Goal 없는 Task는 없다 |
| [Capability](e006-capability.md) | Task는 Capability를 **요구**한다 (`required_capabilities`) |
| [Resource](e007-resource.md) | Task는 Resource를 직접 지정하지 않는다. Decision Engine이 매칭한다 |
| Plan (Entity 008, 예정) | Plan은 Task Graph + 실행 전략의 상위 개념이다 |
| Constraint (Entity 004, 예정) | Goal의 Constraint는 Task로 상속·전파된다 |

---

## 13. Open Issues (v1.0)

### Task Graph는 별도 명세가 필요한가

Goal이 [Goal Graph](e001a-goal-graph.md)로 확장된 것처럼, Task Graph도 노드 정의(본 문서)와 그래프 명세(관계, 전파, 질의)를 분리하는 것이 자연스럽다. 특히 다음이 미정이다.

- Dynamic Planning 시 Task Graph의 **부분 재생성 규칙** — 실행 중 계획 변경 시 이미 Completed된 Task를 어떻게 보존하는가
- Goal Propagation([Goal Graph §14](e001a-goal-graph.md))이 Task Graph로 전파되는 규칙

### 앞으로 보강해야 할 항목

- Task 우선순위 계산식 (Goal Score와의 연동)
- `conditional` 모드의 조건 표현 문법 (Formal Grammar)
- Task 수준 Constraint의 상속 규칙 (Entity 004 확정 후)
- Retry Policy의 비용 상한 (재시도 폭주 방지)
- 실제 예시 30~50개
