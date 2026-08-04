# Entity 008: Plan

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Plan is an executable blueprint produced by the Planner that transforms a Goal Graph into a structured set of Tasks, dependencies, resource requirements, and assumptions.**

> Plan은 Planner가 Goal Graph를 입력으로 받아 생성한, Task·의존 구조·자원 요구·가정을 포함하는 **실행 청사진**이다.

여기서 중요한 단어는 **산출물(Artifact)** 이다.

Plan은 "계획을 세우는 행위"가 아니라, 그 행위가 만들어낸 **결과물 객체**이다.

---

## 2. Plan은 무엇이 아닌가?

이게 정의보다 훨씬 중요하다.

### Plan은 Planning이 아니다

Planning은 **Process**(시스템이 수행하는 것)이고, Plan은 그 Process가 생성한 **Entity**(시스템에 존재하는 것)이다.

| 분류 | 이름 | 의미 |
|---|---|---|
| **Process** | Planning | Goal Graph를 분석해 실행 청사진을 만드는 행위 |
| **Entity** | Plan | Planning의 산출물. 저장·버전 관리·비교 가능한 객체 |
| **Runtime State** | Execution Progress | Plan을 실행하는 도중의 진행 상태 |

❌ `Planner가 지금 계획 중` — 이건 Plan이 아니다. Planning이라는 Process의 진행 상태다.

### Plan은 Goal이 아니다

❌ `학생 100명 모집` — Goal이다. Plan은 그 Goal을 **어떻게** 달성할지의 청사진이다.

### Plan은 Task가 아니다

❌ `인스타그램 광고 집행` — Task 하나다. Plan은 Task들의 **집합 + 의존 구조 + 가정**이다.

### Plan은 Prompt Chain이 아니다

❌ `프롬프트 A → 프롬프트 B → 프롬프트 C` — 이건 실행 스크립트일 뿐이다. Plan은 비용·리스크·대안까지 포함한다.

---

## 3. Plan의 조건

Plan은 반드시 아래 조건을 만족해야 한다.

### Rule P-001 — 정확히 하나의 Goal Graph(부분 그래프 포함)에서 파생되어야 한다

모든 Plan은 `source_goal_ids`로 기원을 추적할 수 있어야 한다. 기원 없는 Plan은 시스템이 관리하지 않는다.

### Rule P-002 — Task 의존 구조는 DAG여야 한다

Goal Graph와 동일하게 순환 의존(`A → B → A`)은 허용하지 않는다. 반복 운영은 Workflow Graph / Control Loop([Volume 3](../v3-runtime.md))의 영역이다.

### Rule P-003 — 예상 비용과 예상 시간이 존재해야 한다

- ✅ `예상 비용 280만원 / 예상 기간 6주`
- ❌ `일단 해보자` — 추정 없는 Plan은 Draft를 벗어날 수 없다.

### Rule P-004 — 가정(Assumptions)을 명시해야 한다

Plan은 가정 위에 세워진다. 가정이 깨지면 Replanning이 트리거되므로(§9), 가정은 반드시 기계가 검사할 수 있는 형태로 기록한다.

✅ `광고 예산 300만원은 유지된다` / `윈터캠프 일정은 변경되지 않는다`

### Rule P-005 — Resource를 확정하지 않는다

Plan은 Task별 **Capability 요구**까지만 기술한다. 어떤 Resource(Claude, GPT, Human Expert 등)를 쓸지는 Decision Engine이 결정하고, 그 기록은 [Entity 009: Decision](e009-decision.md)이다.

- ❌ `Task 3: Claude로 광고 카피 작성`
- ✅ `Task 3: 광고 카피 작성 (required: Korean Writing, Persuasion)`

### Rule P-006 — Active Plan은 Goal당 동시에 하나만 존재한다

같은 Goal에 대해 여러 버전의 Plan이 존재할 수 있지만, `Active` 상태는 항상 하나다. 나머지는 `Superseded`가 된다.

---

## 4. Goal Graph → Planner → Plan

[Entity 001-A §16](e001a-goal-graph.md)의 관점을 그대로 유지한다.

```
Goal Graph
  ↓
Planner  (= 컴파일러)
  ↓
Plan     (= 컴파일 산출물)
  ↓
Execution Graph (Runtime에 로드된 형태)
```

Planner는 Goal 하나를 보고 계획을 세우지 않는다. **Goal Graph 전체를 입력으로 받아** 목표 간 의존성·충돌·우선순위를 함께 고려한 Plan을 생성한다.

비유하면:

| 컴파일러 세계 | Intent OS |
|---|---|
| Source Code | Goal Graph |
| Compiler | Planner |
| Object Code | Plan |
| Loader/Runtime | Runtime Engine ([Volume 3](../v3-runtime.md)) |

---

## 5. Plan Attributes

Plan은 최소한 아래 속성을 가진다.

```
Plan
├── Plan ID / Version
├── Source Goal IDs
├── Tasks
├── Dependency Structure
├── Estimated Cost
├── Estimated Duration
├── Expected Success Probability
├── Risk Level
├── Assumptions
├── Alternatives
└── Status
```

| 속성 | 의미 | 예 |
|---|---|---|
| **Plan ID / Version** | 식별자와 버전 | `plan_014`, `v3` |
| **Source Goal IDs** | 어떤 Goal(들)에서 파생되었는가 | `goal_001` (학생 100명 모집) |
| **Tasks** | 실행 단위 목록 | 시장 조사, 광고 카피 작성, 랜딩 페이지 개선 |
| **Dependency Structure** | Task 간 의존 관계 (DAG) | 시장 조사 → 광고 카피 작성 |
| **Estimated Cost** | 예상 비용 | `280만원` (예산 300만원 이하) |
| **Estimated Duration** | 예상 기간 | `6주` (마감 2026-11-30 이전) |
| **Expected Success Probability** | 예상 성공 확률 | `0.82` |
| **Risk Level** | 종합 리스크 | Low / Medium / High |
| **Assumptions** | 이 Plan이 성립하는 전제 | 광고 예산 유지, 캠프 일정 불변 |
| **Alternatives** | 고려된 대안 Plan | `plan_014_alt1` (SEO 중심안) |
| **Status** | Plan의 상태 | Draft / Approved / Active / … |

---

## 6. Plan 구성 예시

Goal: `2026년 11월까지 윈터캠프 학생 100명 모집, 예산 300만원 이하`

```
Plan plan_014 (v1)
│
├── T1: 시장 조사 (Search, Data Analysis)
├── T2: 타겟 페르소나 정의 (Analysis)          ← depends on T1
├── T3: 광고 카피 작성 (Korean Writing, Persuasion) ← depends on T2
├── T4: 랜딩 페이지 개선 (Design, Copywriting)  ← depends on T2
├── T5: 광고 집행 (Ad Operation)               ← depends on T3, T4
└── T6: 성과 분석 및 조정 (Data Analysis)       ← depends on T5

Estimated Cost:     280만원
Estimated Duration: 6주
Success Prob.:      0.82
Risk:               Medium
Assumptions:        예산 300만원 유지 / 캠프 일정 불변 / 광고 계정 정지 없음
Alternatives:       plan_014_alt1 (SEO 중심, 저비용·장기)
```

T3와 T4는 의존이 없으므로 **병렬 실행 가능**하다. 이 정보가 Runtime의 Parallel Execution([Volume 3 §5.2](../v3-runtime.md)) 판단 근거가 된다.

---

## 7. Plan Lifecycle

```
Draft → Approved → Active → Completed
                     │
                     ├──→ Superseded   (새 버전으로 대체)
                     └──→ Aborted      (Goal 취소/실패)
```

| 상태 | 의미 |
|---|---|
| **Draft** | Planner가 생성했으나 아직 검증/승인 전 |
| **Approved** | 검증 통과. 실행 대기 (High Impact Plan은 Human 승인 포함) |
| **Active** | Runtime이 실행 중인 유일한 버전 |
| **Superseded** | Replanning으로 새 버전에 자리를 내줌. 기록은 보존 |
| **Completed** | 모든 Task 완료, Goal 평가로 이관 |
| **Aborted** | 실행 중단. 사유가 반드시 기록되어야 한다 |

`Superseded`와 `Aborted`는 다르다. Superseded는 **Goal은 그대로, 방법만 교체**된 것이고, Aborted는 **Goal 자체가 취소되거나 실패**한 것이다.

---

## 8. Plan Versioning

Plan은 수정하지 않는다. **새 버전을 만든다.**

```
plan_014 v1 (Active)
  ↓  광고 예산 300만원 → 100만원 (Goal Propagation)
plan_014 v1 (Superseded)
plan_014 v2 (Active)  ← 저비용 채널 중심으로 재컴파일
```

이 규칙이 중요한 이유:

1. **감사 가능성** — "그때 왜 그렇게 계획했는가"를 답할 수 있다.
2. **Learning Engine의 입력** — 버전 간 차이와 결과 차이가 학습 데이터가 된다.
3. **Goal Graph Invariant와의 일관성** — Completed Goal을 수정하지 않는 것([e001a §15](e001a-goal-graph.md))과 같은 원칙이다.

---

## 9. Replanning Triggers

Plan은 고정되지 않는다([Volume 3 §Stage 3 — Dynamic Planning](../v3-runtime.md)). 다음 조건에서 Planner가 새 버전을 생성한다.

| Trigger | 예 |
|---|---|
| **Assumption Violation** | 광고 예산 300만원 → 100만원 |
| **Goal Propagation** | 상위 Goal 변경이 하위 Goal 목표치를 바꿈 (모집 100명 → 65명) |
| **Execution Deviation** | 예상 CTR 8% 대비 실제 3% — 허용 편차 초과 |
| **Resource Failure Cascade** | 대체 Resource로도 Task를 수행할 수 없음 |
| **Low Confidence** | 남은 구간의 예상 성공 확률이 임계값 이하로 하락 |
| **User Request** | 사용자가 방향 전환을 요청 |

Replanning은 전체 재컴파일이 아닐 수 있다. 영향받는 부분 그래프만 다시 계획하는 **Partial Replanning**이 기본이다.

---

## 10. Plan Quality Metrics

Planner는 Plan을 하나만 만들지 않는다. 후보 Plan들을 품질 지표로 비교하고, 최종 선택은 Decision Engine의 **Plan Selection Decision**([e009 §5](e009-decision.md))으로 기록된다.

| 지표 | 의미 | 예 |
|---|---|---|
| **Expected Success Probability** | Goal 달성 예상 확률 | 0.82 |
| **Estimated Cost** | 총 예상 비용 | 280만원 |
| **Estimated Duration** | 총 예상 기간 | 6주 |
| **Risk Level** | 가정 취약성 + 실행 불확실성 | Medium |
| **Constraint Margin** | 제약 대비 여유 | 예산 여유 20만원, 기간 여유 1주 |

예)

| | plan_014 (광고 중심) | plan_014_alt1 (SEO 중심) |
|---|---|---|
| Success Prob. | 0.82 | 0.61 |
| Cost | 280만원 | 90만원 |
| Duration | 6주 | 14주 |
| Risk | Medium | Low |

마감이 11월이라면 alt1은 Duration에서 탈락한다. **좋은 Plan은 절대 순위가 아니라 제약 조건 위에서의 최적해다.**

---

## 11. Canonical Plan Representation

모든 Plan은 내부적으로 동일한 구조를 가진다.

```json
{
  "plan_id": "plan_014",
  "version": 2,
  "source_goal_ids": ["goal_001"],
  "status": "Active",
  "tasks": [
    {
      "task_id": "t3",
      "name": "광고 카피 작성",
      "required_capabilities": ["Korean Writing", "Persuasion"],
      "depends_on": ["t2"]
    }
  ],
  "estimated_cost": { "value": 2800000, "currency": "KRW" },
  "estimated_duration": { "value": 6, "unit": "week" },
  "expected_success_probability": 0.82,
  "risk_level": "Medium",
  "assumptions": ["광고 예산 300만원 유지", "윈터캠프 일정 불변"],
  "alternative_plan_ids": ["plan_014_alt1"],
  "created_by": "planner",
  "created_at": "2026-08-04T09:00:00Z"
}
```

**이 구조만 Runtime으로 전달된다.**

기계가 읽을 수 있는 스키마: [`plan.schema.json`](../intent-os-spec/schemas/plan.schema.json)

---

## 12. Plan Validation Algorithm

Plan이 `Draft → Approved`로 넘어가려면 다음 검증을 통과해야 한다.

```
Plan (Draft)
  ↓
Source Goal 존재 확인
  ↓
Task DAG 검증 (순환 없음, 고아 Task 없음)
  ↓
Capability 커버리지 확인 (모든 Task에 요구 능력 명시)
  ↓
Constraint 검사 (비용 ≤ 예산, 기간 ≤ 마감)
  ↓
Assumption 검사 가능성 확인
  ↓
품질 지표 존재 확인 (Success Prob. / Cost / Duration / Risk)
  ↓
[High Impact?] ──Yes──→ Human Approval
  ↓ No
Approved
```

하나라도 실패하면 Plan은 Draft에 머물고, Planner에게 결함 목록이 반환된다.

---

## 13. 다른 Entity와의 관계

```
Goal Graph (e001a)
  ↓ 입력
Planner ──생성──→ Plan (e008)
                    ├── 포함 ──→ Task (e005)
                    ├── 요구 ──→ Capability (e006)
                    ├── 전제 ──→ Constraint (e004), Assumptions
                    └── 선택/기록 ──→ Decision (e009)
                                        ↓
                                     Resource (e007)
```

| Entity | 관계 |
|---|---|
| **Goal / Goal Graph** | Plan의 입력이자 존재 이유. Goal 변경 → Goal Propagation → Replanning |
| **Task** | Plan의 구성 단위. Task는 Plan 밖에서 독립적으로 실행되지 않는다 |
| **Capability** | Task별 요구 능력. Decision Engine의 Candidate Filtering 기준 |
| **Decision** | "어느 Plan을 채택했는가", "각 Task에 어떤 Resource를 쓰는가"의 기록 |
| **Feedback** | 실행 결과와 예측(성공 확률, 비용)의 차이가 Planner 학습 데이터가 된다 |

---

## 14. Open Issues (v1.0)

### Partial Replanning의 경계 문제

부분 재계획 시 "영향받는 부분 그래프"를 어디까지로 볼 것인가. 현재는 Assumption과 의존 Task를 따라가는 보수적 전파를 가정하지만, 과도한 재계획(Replanning Storm)을 막는 감쇠 규칙이 필요하다.

### Plan 품질 지표의 산출 근거

Expected Success Probability는 초기에는 Rule + Benchmark 기반이고, 장기적으로는 Performance Prediction Engine([Volume 4-A §7](../v4a-decision-engine-detail.md))의 예측 모델을 공유해야 한다. 두 시스템의 예측 일관성 규칙이 미정이다.

### Alternative Plan의 보존 기간

탈락한 대안 Plan을 얼마나 오래 보존할 것인가. Learning 관점에서는 전부 보존이 이상적이지만 저장 비용과의 균형 규칙이 필요하다.

### 앞으로 보강해야 할 항목

- Plan 형식 문법 (Formal Grammar)
- Partial Replanning 알고리즘 상세
- Plan 간 비교(diff) 표준 포맷
- 실제 예시 30~50개
