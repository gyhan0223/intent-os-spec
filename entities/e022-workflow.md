# Entity 022: Workflow

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Workflow is a reusable, versioned control-flow template over Capabilities that defines the order and conditions of execution, independent of any specific Goal.**

> Workflow는 Capability 위에 정의된 **재사용 가능하고 버전을 갖는 제어 흐름 템플릿**이며, 실행의 순서와 조건을 규정하되 특정 Goal에 종속되지 않는다.

여기서 중요한 단어는 **재사용 가능(Reusable)** 이다.

Plan은 이번 윈터캠프를 위한 **일회성 계획**이다. Workflow는 "학원 시즌 캠페인은 이렇게 흘러간다"는 **패턴**이다. 다음 여름캠프에서 Plan은 새로 만들지만 Workflow는 그대로 쓴다.

```
Workflow  wf_seasonal_campaign  v2.1     ← 재사용. 여름·겨울·봄 캠프에 전부 적용
    │ 인스턴스화
    ▼
Plan      plan_014 (윈터캠프)             ← 일회성. 이 Goal 전용
```

---

## 2. Workflow는 무엇이 아닌가?

### Workflow는 Plan이 아니다

❌ `윈터캠프 100명 모집을 위한 7개 Task 계획` — 이건 [Plan](e008-plan.md)이다.

| | Plan | Workflow |
|---|---|---|
| 소속 | 특정 Goal | Goal 독립 |
| 수명 | Goal이 끝나면 종료 | 영구. 버전만 올라간다 |
| 내용 | 무엇을 할 것인가 (구체적 Task) | 어떻게 흘러가는가 (제어 흐름) |
| 재사용 | 불가 | 가능 |
| 예 | `plan_014` | `wf_seasonal_campaign` |

Plan은 Workflow의 **인스턴스**다. 다만 Workflow 없이 만들어지는 Plan도 있다(Rule WFL-008).

### Workflow는 Task Graph가 아니다

❌ `T1 → T2 → T4 의존 관계` — 이건 [Task Graph](e005a-task-graph.md)다.

**의존과 제어 흐름은 다르다.**

```
Task Graph   T4는 T3이 끝나야 시작할 수 있다        (제약)
Workflow     T3이 끝나면 T4를 시작한다.
             단 조사 결과 신뢰도가 0.6 미만이면
             T3을 한 번 더 수행한다                  (제어)
```

Task Graph는 **무엇이 무엇을 막는가**만 말한다. Workflow는 **분기·반복·대기·보상**을 말한다. Task Graph로는 "실패하면 되돌린다"를 표현할 수 없다.

### Workflow는 Execution이 아니다

❌ `exe_220이 1.82초 만에 완료` — 이건 [Execution](e013-execution.md)이다.

Workflow는 **설계도**, Execution은 **실행 사실**이다. 하나의 Workflow가 수백 번 인스턴스화된다.

### Workflow는 Execution Mode가 아니다

❌ `sequential / parallel / conditional` — 이건 [Task](e005-task.md)의 `execution_mode`다.

Execution Mode는 **Task 하나의 실행 방식**이고 Workflow는 **여러 Task에 걸친 흐름 전체**다. Workflow는 Execution Mode를 포함하지만 그보다 크다.

### Workflow는 하드코딩된 파이프라인이 아니다

❌ `Perplexity → Claude → 김 카피라이터`

Resource 이름이 등장하면 Workflow가 아니다(Rule WFL-002). Workflow의 각 단계는 **Capability로만** 표현된다. 그래야 다음 실행에서 더 나은 Resource로 자동 교체된다.

---

## 3. Design Principles

### Rule WFL-001 — Workflow는 Goal에 독립이다

Workflow 정의에 특정 Goal ID·Task ID가 등장하면 그것은 Plan이다.

### Rule WFL-002 — Workflow는 Resource를 지정하지 않는다

각 단계는 `required_capabilities`로 표현한다. [INV-09](e000a-entity-relationships.md) Layer Isolation의 Workflow 측 적용이다.

- ✅ `step: 조사 / capabilities: [research.web, analysis.competitor]`
- ❌ `step: 조사 / resource: perplexity:sonar`

### Rule WFL-003 — 제어 흐름을 명시한다

Workflow가 표현할 수 있는 제어 구조는 다음 6개뿐이다.

| 구조 | 의미 |
|---|---|
| `sequence` | 순서대로 실행 |
| `parallel` | 동시 실행. 전부 완료되면 다음 |
| `branch` | 조건에 따라 경로 선택 |
| `loop` | 조건이 만족될 때까지 반복 (**상한 필수**) |
| `wait` | 외부 사건·시간을 기다린다 |
| `compensate` | 실패 시 이전 단계를 되돌린다 |

이 6개로 표현할 수 없는 흐름은 **Workflow를 분할해야 한다는 신호**다.

### Rule WFL-004 — 무한 반복을 허용하지 않는다

`loop`는 반드시 `max_iterations`를 갖는다. 상한 없는 반복은 예산을 태운다.

### Rule WFL-005 — 실패 경로를 정의한다

각 단계는 실패했을 때의 행동을 갖는다.

| on_failure | 의미 |
|---|---|
| `retry` | 재시도 (상한 필수) |
| `skip` | 건너뛰고 계속 |
| `fail_workflow` | 전체 중단 |
| `compensate` | 보상 단계 실행 후 중단 |
| `branch_to` | 대체 경로로 이동 |

### Rule WFL-006 — 버전을 가진다

Workflow는 여러 Plan이 참조한다. 수정하면 진행 중인 Plan이 영향을 받는다. 따라서 **수정이 아니라 새 버전 발행**만 허용한다.

실행 중인 Plan은 시작 시점의 버전을 계속 사용한다(Version Pinning).

### Rule WFL-007 — 비가역 단계를 표시한다

되돌릴 수 없는 단계(광고 집행, 메시지 발송)는 `irreversible: true`를 갖는다. 이 단계 앞에는 `compensate`가 아니라 **사전 승인 게이트**가 필요하다.

### Rule WFL-008 — Workflow는 선택이지 의무가 아니다

모든 Plan이 Workflow를 필요로 하지는 않는다. 단순한 Plan은 Task Graph의 의존 순서만으로 충분하다. Workflow는 **반복되는 패턴이 발견되었을 때** 만든다.

---

## 4. Attributes

```
Workflow
├── Identity
│   ├── workflow_id
│   ├── name
│   ├── version
│   └── type
├── Definition
│   ├── steps[]
│   ├── entry_step
│   └── variables[]
├── Governance
│   ├── owner
│   ├── policy_refs[]
│   └── budget_hint
├── Provenance
│   ├── derived_from        (학습으로 추출된 경우)
│   └── usage_stats
└── Status
    └── status
```

각 `step`의 구조는 다음과 같다.

| 필드 | 의미 | 예 |
|---|---|---|
| `step_id` | 단계 식별자 | `s3_copywriting` |
| `name` | 이름 | `광고 카피 작성` |
| `control` | 제어 구조 (§3 WFL-003) | `sequence` |
| `required_capabilities` | 필요 능력 | `["language.generation.copywriting"]` |
| `expected_output` | 기대 산출물 | `카피 3종 + 타겟 근거` |
| `next` | 다음 단계 | `s4_review` |
| `condition` | branch의 조건 | `evaluation.composite >= 0.8` |
| `max_iterations` | loop 상한 (WFL-004) | `3` |
| `on_failure` | 실패 처리 (WFL-005) | `retry` |
| `irreversible` | 비가역 여부 (WFL-007) | `false` |
| `compensation` | 보상 단계 | `null` |

### 4.1 Workflow Types

```
Workflow
├── linear        일직선 순차
├── branching     조건 분기 포함
├── iterative     반복(품질 임계 도달까지) 포함
├── event_driven  외부 사건 대기 포함
└── saga          비가역 단계 + 보상 트랜잭션 포함
```

| Type | 예 | 특징 |
|---|---|---|
| `linear` | 조사 → 분석 → 보고서 | 가장 단순. 대부분의 Workflow |
| `branching` | 전환율에 따라 랜딩 개선 vs 광고 확대 | `condition` 필수 |
| `iterative` | 카피 품질 0.85 이상 나올 때까지 최대 3회 | `max_iterations` 필수 |
| `event_driven` | 인간 검수 회신을 기다렸다가 진행 | `wait` 단계 포함 |
| `saga` | 광고 집행 후 실패 시 캠페인 중단 | `compensation` 필수 |

**`saga`가 가장 중요하다.** 비가역 작업을 포함하는 Workflow는 "실패하면 어떻게 되돌리는가"를 반드시 정의해야 한다. 되돌릴 수 없다면 그 앞에 승인 게이트를 둔다.

---

## 5. Invariants

### INV-WFL-01 — Workflow 그래프는 DAG다 (loop 제외)

명시적 `loop` 단계 외의 순환은 금지된다. 전역 불변식 [INV-08](e000a-entity-relationships.md)의 Workflow 측 표현이다.

| | |
|---|---|
| **위반 시** | 발행 거부. 순환 경로를 오류로 반환 |

### INV-WFL-02 — 모든 loop는 max_iterations를 가진다

| | |
|---|---|
| **위반 시** | 발행 거부. 기본값을 임의로 부여하지 않는다 — 설계자가 정해야 한다 |

### INV-WFL-03 — Workflow에 Resource 식별자가 등장할 수 없다

| | |
|---|---|
| **위반 시** | 발행 거부. Resource 이름을 Capability로 치환하도록 요구 |

### INV-WFL-04 — 발행된 버전은 수정되지 않는다

| | |
|---|---|
| **위반 시** | 저장 계층이 거부. 진행 중인 Plan의 동작이 도중에 바뀌면 안 된다 |

### INV-WFL-05 — irreversible 단계 앞에는 승인 게이트 또는 Rehearsal이 있다

| | |
|---|---|
| **위반 시** | 발행 시 경고, 실행 시 [Policy](e019-policy.md) `require_approval`을 강제 삽입 |
| **근거** | [Risk RSK-008](e018-risk.md), [Artifact §6.1](e016-artifact.md)과 같은 원칙 |

### INV-WFL-06 — 모든 step은 entry_step에서 도달 가능하다

| | |
|---|---|
| **위반 시** | 발행 거부. 도달 불가 단계는 설계 오류다 |

---

## 6. Lifecycle

Workflow는 **정의의 수명**과 **인스턴스의 수명**이 다르다.

### 6.1 정의의 수명

```
Draft → Review → Published ──▶ Deprecated ──▶ Retired
           │
           └──▶ Rejected
```

| 상태 | 의미 |
|---|---|
| **Draft** | 작성 중 |
| **Review** | 검토 중 |
| **Published** | 발행됨. Plan이 인스턴스화 가능 |
| **Deprecated** | 신규 인스턴스화 중단. 진행 중인 Plan은 계속 |
| **Retired** | 참조하는 Plan이 모두 종료됨 |

### 6.2 인스턴스의 수명

Plan이 Workflow를 인스턴스화하면 **Workflow Instance**가 생긴다.

```
Instantiated → Running → Completed
                  │  ▲
                  ▼  │
               Waiting┘
                  │
                  ├──▶ Compensating ──▶ RolledBack
                  └──▶ Failed
```

| 상태 | 의미 |
|---|---|
| **Instantiated** | Plan에 바인딩됨. 아직 시작 전 |
| **Running** | 단계 진행 중 |
| **Waiting** | `wait` 단계에서 외부 사건 대기 |
| **Compensating** | 보상 단계 실행 중 |
| **RolledBack** | 보상 완료. 되돌릴 수 있는 범위까지 복구됨 |
| **Completed** | 마지막 단계 완료 |
| **Failed** | 보상 불가한 실패 |

**`RolledBack`이 "원상복구"를 뜻하지 않는다.** 이미 집행된 광고비는 돌아오지 않는다. 되돌릴 수 있는 것만 되돌렸다는 뜻이다.

---

## 7. Relationships

```
Workflow 022 ──인스턴스화──▶ Plan 008 ──▶ Task Graph 005-A
     │
     ├──단계별──▶ Capability 006  (Resource는 모른다)
     ├──트리거──▶ Event 020       (wait / event_driven)
     ├──지배───▶ Policy 019       (승인 게이트)
     └──추출───▶ Knowledge 011    (반복 패턴에서 학습)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Plan](e008-plan.md) | Plan이 Workflow를 인스턴스화한다 | `Plan 1:0..1 Workflow` |
| [Capability](e006-capability.md) | 각 step이 요구하는 능력 | `Workflow N:M Capability` |
| [Task](e005-task.md) | 인스턴스화 시 step → Task로 전개 | `Workflow 1:N Task` (인스턴스 경유) |
| [Event](e020-event.md) | `wait` 단계의 트리거 | `Event N:M Workflow` |
| [Policy](e019-policy.md) | 비가역 단계의 승인 게이트 | `Policy 1:N Workflow` |
| [Knowledge](e011-knowledge.md) | 반복 성공 패턴이 Workflow로 승격 | `Knowledge 1:0..N Workflow` |
| [Resource](e007-resource.md) | **직접 관계 없음** (INV-WFL-03) | — |

### 7.1 Knowledge → Workflow 승격

Workflow의 가장 강력한 출처는 **사람이 아니라 학습**이다.

```
동일 Goal 유형 12건의 성공 Plan 분석
  ↓
공통 패턴 발견: 조사 → 타겟 분석 → 카피 → 검수 → 파일럿 → 본 집행
  ↓
Knowledge know_090: "학원 시즌 캠페인은 파일럿 선행 시 실패율 62% 감소"
  ↓
Workflow wf_seasonal_campaign v1.0 자동 제안
  ↓
사람 검토 → Published
```

이는 [Volume 4-E — Strategy Graph](../v4e-strategy-graph.md)가 다루는 "전략 자체의 학습"과 같은 방향이다.

---

## 8. Canonical Representation

```json
{
  "workflow_id": "wf_seasonal_campaign",
  "name": "학원 시즌 캠페인",
  "version": "2.1",
  "type": "saga",
  "owner": "human:대표",
  "entry_step": "s1_research",
  "variables": [
    { "name": "quality_threshold", "type": "number", "default": 0.85 },
    { "name": "pilot_budget_krw", "type": "number", "default": 100000 }
  ],
  "steps": [
    {
      "step_id": "s1_research",
      "name": "시장·경쟁 조사",
      "control": "parallel",
      "branches": ["s1a_market", "s1b_competitor"],
      "next": "s2_target",
      "on_failure": "retry",
      "max_retries": 2
    },
    {
      "step_id": "s2_target",
      "name": "타겟 분석",
      "control": "sequence",
      "required_capabilities": ["analysis.audience"],
      "expected_output": "페르소나 정의",
      "next": "s3_copywriting",
      "on_failure": "fail_workflow"
    },
    {
      "step_id": "s3_copywriting",
      "name": "광고 카피 작성",
      "control": "loop",
      "required_capabilities": ["language.generation.copywriting"],
      "expected_output": "카피 3종 + 타겟 근거",
      "loop_condition": "evaluation.composite < $quality_threshold",
      "max_iterations": 3,
      "next": "s4_review",
      "on_failure": "branch_to",
      "branch_to": "s4_review"
    },
    {
      "step_id": "s4_review",
      "name": "인간 검수",
      "control": "wait",
      "required_capabilities": ["review.brand_tone"],
      "wait_for": { "event_type": "execution.completed", "timeout": "PT24H" },
      "next": "s5_pilot",
      "on_failure": "skip"
    },
    {
      "step_id": "s5_pilot",
      "name": "파일럿 집행",
      "control": "sequence",
      "required_capabilities": ["advertising.campaign_execution"],
      "irreversible": true,
      "budget_cap": "$pilot_budget_krw",
      "next": "s6_gate",
      "on_failure": "compensate",
      "compensation": "s5c_stop_pilot"
    },
    {
      "step_id": "s6_gate",
      "name": "파일럿 성과 판정",
      "control": "branch",
      "condition": "metrics.ctr >= 0.012",
      "on_true": "s7_full_launch",
      "on_false": "s3_copywriting"
    },
    {
      "step_id": "s7_full_launch",
      "name": "본 집행",
      "control": "sequence",
      "required_capabilities": ["advertising.campaign_execution"],
      "irreversible": true,
      "requires_approval": true,
      "next": null,
      "on_failure": "compensate",
      "compensation": "s7c_stop_campaign"
    }
  ],
  "usage_stats": { "instantiations": 12, "success_rate": 0.83 },
  "derived_from": "know_090",
  "status": "Published"
}
```

기계가 읽을 수 있는 스키마: [`workflow.schema.json`](../intent-os-spec/schemas/workflow.schema.json)

---

## 9. Validation Rules

### 9.1 발행 검증

```
Workflow 발행 요청
  ↓
Goal / Task ID 포함 여부 검사 (WFL-001) ── 포함 시 반려 (Plan으로 등록하라)
  ↓
Resource 식별자 검출 (INV-WFL-03) ── 검출 시 반려 + Capability 치환 요구
  ↓
step 그래프 구성
  ├── entry_step 존재 확인
  ├── 도달 가능성 검사 (INV-WFL-06) ── 고립 step 발견 시 반려
  └── 순환 검사 (INV-WFL-01) ── loop 외 순환 발견 시 반려
  ↓
각 loop step의 max_iterations 확인 (INV-WFL-02) ── 없으면 반려
  ↓
각 step의 on_failure 확인 (WFL-005) ── 없으면 fail_workflow 기본값 + 경고
  ↓
irreversible step 검사 (INV-WFL-05)
  선행 경로에 requires_approval 또는 Rehearsal step이 있는가
  ── 없으면 경고 + Policy 게이트 자동 삽입
  ↓
compensation step 존재 확인 (type=saga인 경우)
  ↓
capability id 정규화 (Taxonomy 조회, e006a)
  ↓
버전 부여 (WFL-006) → Published
```

### 9.2 인스턴스화

```
Plan 생성 시 Workflow 선택
  ↓
Workflow 버전 고정 (Version Pinning)
  ↓
variables 바인딩 (Goal의 Constraint에서 값 주입)
  예: pilot_budget_krw ← Goal 예산의 5%
  ↓
step → Task 전개
  각 step의 required_capabilities, expected_output을 Task로 변환
  parallel step → 독립 Task 여러 개
  loop step   → Task 1개 + 반복 정책
  ↓
Task Graph 생성 (e005a) — step의 next 관계가 dependencies가 된다
  ↓
Task Graph 순환 검사
  ↓
Plan 확정 → Workflow Instance 생성 (Instantiated)
```

**loop와 branch는 Task Graph로 완전히 전개되지 않는다.** Task Graph는 정적 DAG이고, 반복 횟수와 분기 결과는 실행 시점에 결정된다. Workflow Instance가 런타임에 Task를 추가로 생성한다.

---

## 10. Examples

### 예시 1 — 윈터캠프 (위 Canonical의 실행)

```
plan_014  wf_seasonal_campaign v2.1 인스턴스화
  quality_threshold: 0.85
  pilot_budget_krw: 150000  (Goal 예산 300만원의 5%)

s1_research   parallel   시장조사 ‖ 경쟁분석          ✅
s2_target     sequence   타겟 분석                    ✅
s3_copywriting loop      1회차 composite 0.79 < 0.85 → 2회차 0.91  ✅
s4_review     wait       김 카피라이터 회신 (4시간)     ✅
s5_pilot      irreversible 파일럿 15만원 집행          ✅
s6_gate       branch     CTR 1.4% ≥ 1.2%  → s7        ✅
s7_full_launch irreversible 본 집행 (승인 필요)
                          → 대표 승인 → 285만원 집행   ✅
```

`s3`의 loop가 없었다면 품질 0.79의 카피로 300만원을 집행했을 것이다.

### 예시 2 — 보상 트랜잭션 (saga)

```
s7_full_launch  본 집행 285만원 시작
  ↓ 집행 중 pol_015(광고 심의) 위반 감지 — 금칙어 "100% 합격"
  ↓
Workflow Instance → Compensating
  ↓
s7c_stop_campaign 실행
  ├── 광고 플랫폼 API로 캠페인 일시중지
  ├── 이미 소진된 43만원은 회수 불가          ← 되돌릴 수 없는 부분
  └── Artifact art_512 status → Archived
  ↓
RolledBack
  ↓
Outcome: 손실 43만원, 학습 신호: "s3에 금칙어 사전 검사 단계 추가 필요"
```

**RolledBack ≠ 원상복구.** 43만원은 사라졌다. Workflow v2.2에서 `s3`와 `s5` 사이에 `s3b_compliance_check` 단계가 추가된다.

### 예시 3 — Workflow 없는 Plan

```
Goal: 이번 주 상담 문의 12건 정리해서 요약해줘
  ↓
Task 2개: 데이터 수집 → 요약
  ↓
Plan plan_301  workflow_id: null
```

단순 Plan에 Workflow를 강제하지 않는다(Rule WFL-008). **Workflow는 반복되는 패턴이 있을 때만 만든다.**

### 예시 4 — 버전 고정

```
2026-08-04  plan_014 생성 → wf_seasonal_campaign v2.1 고정
2026-08-20  wf_seasonal_campaign v2.2 발행 (금칙어 검사 단계 추가)
2026-09-01  plan_014 여전히 진행 중 → v2.1을 계속 사용
2026-09-05  plan_020 (봄캠프) 생성 → v2.2 사용
```

진행 중인 Plan의 동작이 도중에 바뀌면 실행 결과를 설명할 수 없게 된다(INV-WFL-04).

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **loop가 max_iterations에 도달했는데 조건 미충족** | `on_failure` 정책을 따른다. 예시에서는 `branch_to:s4_review`로 인간 검수에 넘긴다. 조용히 통과시키면 품질 미달 결과가 본 집행으로 간다 |
| **wait 단계의 timeout 초과** | `on_failure` 적용. 예시의 `skip`은 "인간 검수 없이 진행"을 뜻하므로, 비가역 단계 앞이라면 `skip`이 아니라 `fail_workflow`여야 한다 |
| **branch 조건 평가에 필요한 지표가 아직 없음** | 지표 확정을 기다린다(`Waiting`). 없는 값을 기본값으로 대체해 분기하면 잘못된 경로로 간다 |
| **compensation 단계 자체가 실패** | `Failed`로 전이한다. 자동 재시도 후에도 실패하면 **인간에게 escalate**한다. 보상 실패는 조용히 넘어갈 수 없다 |
| **진행 중 Workflow가 Deprecated됨** | 진행 중 인스턴스는 영향받지 않는다(§6.1). 신규 인스턴스화만 막힌다 |
| **같은 Workflow가 동시에 여러 Plan에서 실행** | 정상이다. Workflow는 상태를 갖지 않는 템플릿이고, 상태는 인스턴스가 갖는다 |
| **Workflow 단계에 맞는 Capability를 가진 Resource가 없음** | 인스턴스화 시점에 검증한다. Resource가 없으면 Plan 생성을 거부하고 `escalate`한다. 실행 시점에 발견하면 이미 늦다 |
| **variables 바인딩 실패 (Goal에 해당 Constraint 없음)** | `default` 값을 쓰되 경고를 남긴다. `default`도 없으면 인스턴스화 거부 |
| **Workflow가 30단계를 넘음** | 분할 신호다. 하나의 Workflow는 하나의 목적을 가져야 한다. 하위 Workflow 호출이 필요한지 검토한다(§12) |

---

## 12. Open Issues (v1.0)

### Workflow의 합성(Composition)

현재 Workflow는 다른 Workflow를 호출할 수 없다. 큰 캠페인이 "조사 Workflow + 제작 Workflow + 집행 Workflow"로 구성되는 것이 자연스럽지만, 중첩 시 예산·보상·버전 고정이 복잡해진다. [Session](e021-session.md)이 중첩을 금지한 것과 같은 고민이다.

### Task Graph와의 전개 관계

§9.2에서 loop·branch가 Task Graph로 완전히 전개되지 않는다고 서술했다. 정적 Task Graph와 동적 Workflow Instance가 공존하는 구조의 정합 규칙(어느 쪽이 진실의 원천인가)이 미정이다.

### 조건 표현 문법

`condition`을 `"metrics.ctr >= 0.012"` 같은 문자열로 예시했으나 정식 문법이 없다. [Policy](e019-policy.md)의 `condition`과 통일된 표현식 언어가 필요하다.

### 자동 추출된 Workflow의 검증

§7.1처럼 Knowledge에서 Workflow를 자동 제안할 때, 12건의 표본으로 추출한 패턴이 일반화 가능한지 판정하는 기준이 없다. 과적합된 Workflow는 다음 캠페인을 망친다.

### 앞으로 보강해야 할 항목

- 조건 표현식 언어 (Policy와 공유)
- 하위 Workflow 호출 규칙
- `usage_stats` 기반 Workflow 개선 제안 알고리즘
- 실제 예시 30~50개
