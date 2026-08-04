# Entity 006-A: Capability Taxonomy

- **Version:** v1.0 Draft
- **Status:** Core Architecture
- **Last Updated:** 2026-08-04

---

## 0. Why a Taxonomy

[Capability](e006-capability.md)는 Intent OS에서 **Task와 Resource를 잇는 유일한 통로**다.

```
Task ──요구──▶ Capability ◀──제공── Resource
```

이 통로의 이름이 흔들리면 매칭 전체가 무너진다.

```
Task가 요구:      language.generation.copywriting
Resource가 선언:  copywriting
Resource가 선언:  text-generation
Resource가 선언:  마케팅_카피_작성
   ↓
매칭 실패. 최적의 Resource가 후보에 오르지 못한다.
```

이름 하나가 안 맞아서 좋은 Resource를 놓치는 것은 **알고리즘의 문제가 아니라 명명의 문제**다. Taxonomy는 이 문제를 해결한다.

> **Taxonomy는 Capability의 이름·계층·측정 방법을 규정하는 단일 권위(Single Source of Truth)다.**

---

## 1. Definition

### 공식 정의

> **Capability Taxonomy is the versioned, hierarchical namespace of all Capability identifiers, together with the rules for naming, matching, aliasing, measuring, and evolving them.**

> Capability Taxonomy는 모든 Capability 식별자의 **버전을 갖는 계층적 이름공간**이며, 명명·매칭·별칭·측정·진화에 관한 규칙을 함께 정의한다.

### 형식 정의

$$CT = (N, \prec, A, M)$$

| 기호 | 의미 |
|---|---|
| $N$ | Capability 식별자 집합 |
| $\prec$ | 부모-자식 관계. $a \prec b$ 는 "a는 b의 하위 능력" |
| $A$ | 별칭 사상(Alias Map). 비표준 이름 → 표준 이름 |
| $M$ | 각 Capability의 측정 정의 |

**제약:** $(N, \prec)$ 는 **트리**여야 한다. Capability는 부모를 정확히 하나만 갖는다(Rule CT-004).

---

## 2. Capability Taxonomy는 무엇이 아닌가?

### Taxonomy는 Capability가 아니다

❌ `language.generation.copywriting의 정의` — 이건 [Capability Entity](e006-capability.md)다.

Capability는 **하나의 능력**이고 Taxonomy는 **모든 능력의 이름 체계**다. Goal과 [Goal Graph](e001a-goal-graph.md)의 관계와 같다.

### Taxonomy는 Resource 목록이 아니다

❌ `language.generation.copywriting: [Claude, GPT, 김 카피라이터]`

[INV-09](e000a-entity-relationships.md) Layer Isolation. **Resource가 Capability를 선언하지, Capability가 Resource를 나열하지 않는다.** 방향이 반대가 되면 새 Resource를 등록할 때마다 Taxonomy를 고쳐야 한다.

### Taxonomy는 Task 유형 분류가 아니다

❌ `Research Task / Analysis Task / Creation Task` — 이건 [Task Types](e005-task.md)다.

Task Type은 **일의 성격**이고 Capability는 **필요한 능력**이다. 하나의 Creation Task가 `language.generation.copywriting`과 `analysis.audience` 두 능력을 요구할 수 있다.

### Taxonomy는 특정 모델의 스킬 목록이 아니다

❌ `Claude가 잘하는 것들`

Taxonomy는 **Resource 중립적**이다. 아무도 제공하지 않는 Capability도 Taxonomy에 존재할 수 있다. 그것이 "우리에게 없는 능력"을 발견하는 방법이다(§10 예시 4).

### Taxonomy는 점수표가 아니다

❌ `language.generation.copywriting: Claude 93점`

점수는 [Resource Profile](e025-resource-profile.md)에 있다. Taxonomy에는 **무엇을 어떻게 측정하는가**(측정 정의)만 있고 측정값은 없다.

---

## 3. Design Principles

### Rule CT-001 — 명명 규칙: `domain.action.specialization`

```
language.generation.copywriting
   │        │           └── 특화 (선택)
   │        └── 행위
   └── 도메인
```

| 규칙 | 내용 |
|---|---|
| 소문자 + `.` 구분 | `language.generation.copywriting` |
| 단어 내부는 `_` | `analysis.customer_data` |
| 깊이 최대 4 | `domain.action.specialization.variant` |
| 단수형 | `analysis` (❌ `analyses`) |
| 영어 | 한국어 이름은 `display_name`에 |
| 벤더명 금지 | ❌ `claude.copywriting` |
| 도구명 금지 | ❌ `search.google` — `research.web`이 맞다 |

### Rule CT-002 — 최상위 도메인은 고정이다

임의로 늘리지 않는다. 새 최상위 도메인 추가는 Taxonomy 메이저 버전을 올린다.

```
language     자연어 이해·생성
analysis     데이터·상황 분석
research     정보 수집·조사
reasoning    계획·추론·판단
creation     비언어 창작 (이미지·영상·음성)
automation   반복 실행·연동
communication 전달·상담·협상
verification 검증·검수·사실 확인
advertising  광고 집행 (도메인 특화)
```

**마지막 `advertising`처럼 도메인 특화 최상위를 두는 것은 예외다.** 범용 도메인으로 표현할 수 없을 때만 추가한다.

### Rule CT-003 — 능력은 Resource 중립적으로 서술한다

- ✅ `한국어 광고 카피를 작성한다`
- ❌ `프롬프트를 받아 텍스트를 생성한다` — LLM을 전제한 서술이다

김 카피라이터도 이 능력을 제공한다. **인간이 읽어도 말이 되는 서술이어야 한다.**

### Rule CT-004 — 트리 구조다. 부모는 하나다

다중 상속을 허용하면 매칭이 모호해진다. 두 부모가 필요해 보이면 대개 능력 정의가 잘못되었다.

### Rule CT-005 — 매칭은 하향 포함, 상향 미포함이다

```
Resource가 language.generation을 제공한다고 선언
Task가 language.generation.copywriting을 요구
  ↓
매칭되는가?  ❌ NO — 상위 선언은 하위를 보장하지 않는다

Resource가 language.generation.copywriting을 제공
Task가 language.generation을 요구
  ↓
매칭되는가?  ✅ YES — 하위는 상위를 만족한다
```

**이 비대칭이 핵심이다.** "글을 쓸 줄 안다"가 "광고 카피를 쓸 줄 안다"를 뜻하지 않는다. 반대는 성립한다.

### Rule CT-006 — 별칭(Alias)으로 외부 이름을 흡수한다

외부 Resource는 자기 방식으로 능력을 선언한다. 등록 시 Alias Map으로 표준 이름에 사상한다.

```
"copywriting"        → language.generation.copywriting
"text-generation"    → language.generation
"마케팅 카피 작성"     → language.generation.copywriting
```

**Taxonomy를 바꾸지 않고 외부 다양성을 흡수한다.**

### Rule CT-007 — 각 Capability는 측정 정의를 갖는다

점수를 매길 수 없는 능력은 Decision Engine이 쓸 수 없다. 측정 정의는 다음을 포함한다(§4.1).

```
difficulty · measurement_method · evaluation_rubric · scale · min_sample
```

### Rule CT-008 — 폐기는 삭제가 아니다

쓰이지 않는 Capability도 지우지 않는다. 과거 [Decision](e009-decision.md)과 [Resource Profile](e025-resource-profile.md)이 그 이름을 참조하고 있다. `Deprecated` 표시 + `superseded_by` 링크를 남긴다.

### Rule CT-009 — 합성 능력(Composite)을 표현할 수 있다

여러 능력의 조합이 하나의 능력처럼 자주 쓰이면 합성 Capability로 등록한다([Volume 4-B §17](../v4b-resource-intelligence.md)).

```
marketing.campaign_production
  = research.web + analysis.audience + language.generation.copywriting + verification.compliance
```

합성 능력은 `composed_of`를 가지며, 이를 만족하는 Resource는 대개 [Hybrid Resource](e007-resource.md)다.

---

## 4. Attributes

Taxonomy의 각 노드가 갖는 속성이다.

```
Capability Node
├── Identity
│   ├── capability_id
│   ├── display_name
│   ├── parent
│   └── children[]
├── Definition
│   ├── description
│   ├── expected_input
│   └── expected_output
├── Measurement
│   ├── difficulty
│   ├── measurement_method
│   ├── evaluation_rubric_ref
│   ├── scale
│   └── min_sample
├── Composition
│   └── composed_of[]
├── Aliases
│   └── aliases[]
└── Status
    ├── status
    ├── introduced_in
    └── superseded_by
```

| 속성 | 의미 | 예 |
|---|---|---|
| **capability_id** | 표준 식별자 | `language.generation.copywriting` |
| **display_name** | 사람이 읽는 이름 | `광고 카피 작성` |
| **parent** | 부모 (CT-004) | `language.generation` |
| **children** | 자식 목록 | `["language.generation.copywriting.ad", …]` |
| **description** | Resource 중립적 서술 (CT-003) | `목적과 타겟이 주어지면 설득력 있는 짧은 문안을 작성한다` |
| **expected_input** | 기대 입력 | `타겟 정의, 소구점, 채널, 분량 제약` |
| **expected_output** | 기대 산출 | `문안 N종 + 각 문안의 소구 근거` |
| **difficulty** | 난이도 (§4.1) | `4` |
| **measurement_method** | 측정 방법 | `llm_rubric + human_sample` |
| **evaluation_rubric_ref** | 평가 기준 | `rubric_copywriting_v2` |
| **scale** | 점수 척도 | `0-100` |
| **min_sample** | 신뢰 가능 최소 표본 | `30` |
| **composed_of** | 합성 구성 (CT-009) | `null` |
| **aliases** | 별칭 (CT-006) | `["copywriting", "마케팅 카피 작성"]` |
| **status** | 상태 (§6) | `Active` |
| **introduced_in** | 도입 버전 | `1.0` |

### 4.1 Difficulty와 측정

`difficulty`는 1~5의 정수이며, **평가 방법과 필요 표본 수를 결정한다.**

| difficulty | 의미 | 측정 방법 | min_sample |
|---|---|---|---|
| 1 | 형식적 변환. 정답이 명확 | 규칙 기반 자동 | 5 |
| 2 | 단순 조회·요약 | 규칙 + 스키마 검증 | 10 |
| 3 | 분석·구조화. 검증 가능 | LLM Rubric | 20 |
| 4 | 창작·설득. 정답 없음 | LLM Rubric + 인간 표본 | 30 |
| 5 | 전략적 판단. 장기 결과로만 검증 | Deferred Evaluation | 50 |

예시:

| Capability | difficulty | 근거 |
|---|---|---|
| `language.transformation.summarize` | 2 | 원문 대비 검증 가능 |
| `analysis.competitor` | 3 | 사실 검증 가능, 해석은 주관 |
| `language.generation.copywriting` | 4 | 정답이 없다. 성과로만 판정 |
| `reasoning.strategy` | 5 | 몇 달 뒤 결과로만 검증 가능 |

**difficulty 5는 즉시 평가가 불가능하다.** [Evaluation](e015-evaluation.md)의 `deferred` 유형이 강제된다.

### 4.2 Taxonomy 개요

```
language
├── understanding
│   ├── intent_extraction
│   └── sentiment
├── generation
│   ├── copywriting          (difficulty 4)
│   │   ├── ad
│   │   └── landing_page
│   ├── long_form
│   └── script
└── transformation
    ├── summarize            (difficulty 2)
    ├── translate
    └── restructure

analysis
├── audience                 (difficulty 3)
├── competitor               (difficulty 3)
├── metrics                  (difficulty 2)
├── customer_data            (difficulty 3)
└── financial

research
├── web                      (difficulty 2)
├── document
└── interview

reasoning
├── planning                 (difficulty 4)
├── strategy                 (difficulty 5)
├── prioritization
└── coordination

creation
├── image
├── video
└── audio

automation
├── scheduling
├── data_pipeline
└── report_generation

communication
├── consultation             (difficulty 4)
├── notification
└── negotiation

verification
├── fact_check               (difficulty 3)
├── compliance               (difficulty 3)
└── brand_tone               (difficulty 4)

advertising
├── campaign_execution
├── budget_control
└── creative_review
```

---

## 5. Invariants

### INV-CT-01 — Taxonomy는 트리다

| | |
|---|---|
| **위반 시** | 다중 부모 등록 거부. 순환도 금지 |
| **근거** | Rule CT-004. 다중 상속은 매칭을 모호하게 만든다 |

### INV-CT-02 — capability_id는 전역 고유하다

| | |
|---|---|
| **위반 시** | 등록 거부. 같은 이름의 다른 능력은 존재할 수 없다 |

### INV-CT-03 — Alias는 정확히 하나의 표준 id로 사상된다

| | |
|---|---|
| **위반 시** | 모호한 별칭은 등록 거부. 사람 확인을 요구 |
| **근거** | 하나의 별칭이 두 능력을 가리키면 매칭이 비결정적이 된다 |

### INV-CT-04 — Deprecated Capability는 삭제되지 않는다

| | |
|---|---|
| **위반 시** | 삭제 차단. 과거 Decision·Profile의 참조가 끊긴다 (Rule CT-008) |

### INV-CT-05 — 모든 Active Capability는 측정 정의를 갖는다

| | |
|---|---|
| **위반 시** | `Draft`로 강등. 측정할 수 없는 능력은 Decision Engine이 쓸 수 없다 |

### INV-CT-06 — 자식의 difficulty는 부모 이상이다

특화될수록 쉬워지지 않는다.

| | |
|---|---|
| **위반 시** | 등록 시 경고. 계층 정의가 잘못되었을 가능성이 높다 |

### INV-CT-07 — 합성 Capability는 자기 자신을 포함하지 않는다

| | |
|---|---|
| **위반 시** | 순환 정의. 등록 거부 |

---

## 6. Lifecycle

### 6.1 Capability 노드의 수명

```
Proposed → Draft → Active ──▶ Deprecated ──▶ Retired
              │
              └──▶ Rejected
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Proposed** | 등록 제안됨 | Resource 등록 중 미지 능력 발견, 또는 사람이 제안 |
| **Draft** | 정의 작성 중. 측정 정의 미완 | 검토 시작 |
| **Active** | 정식 사용. 매칭 대상 | 측정 정의 완비 (INV-CT-05) |
| **Deprecated** | 신규 사용 중단. 기존 참조는 유효 | 대체 능력 도입 |
| **Retired** | 참조가 모두 사라짐. 이름은 영구 예약 | — |

### 6.2 Taxonomy 버전

Taxonomy 전체가 버전을 갖는다.

| 변경 | 버전 |
|---|---|
| 최상위 도메인 추가·삭제 | **major** |
| 기존 노드의 부모 변경 | **major** |
| 새 하위 노드 추가 | minor |
| 별칭 추가 | patch |
| 측정 정의 수정 | minor |

**major 변경은 기존 Resource Profile의 점수를 무효화할 수 있다.** 부모가 바뀌면 매칭 결과가 달라지기 때문이다. major 변경 시 영향받는 Profile 목록을 함께 발행한다.

---

## 7. Relationships

```
Capability Taxonomy 006-A
   │
   ├──정의──▶ Capability 006 (개별 능력)
   ├──요구──◀ Task 005 (required_capabilities)
   ├──선언──◀ Resource 007 / Tool 024 (capabilities)
   ├──단계──◀ Workflow 022 (step의 required_capabilities)
   ├──범위──◀ Agent 023 (scope.allowed_capabilities)
   └──측정──▶ Resource Profile 025 (capability_scores의 키)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Capability](e006-capability.md) | Taxonomy가 개별 Capability의 이름·계층을 정의 | `Taxonomy 1:N Capability` |
| [Task](e005-task.md) | Task가 Capability를 요구 | `Task N:M Capability` |
| [Resource](e007-resource.md) | Resource가 Capability를 제공 | `Resource N:M Capability` |
| [Tool](e024-tool.md) | Tool도 Capability를 제공 | `Tool N:M Capability` |
| [Workflow](e022-workflow.md) | 각 step이 Capability로 표현된다 | `Workflow N:M Capability` |
| [Agent](e023-agent.md) | 권한 범위를 Capability로 표현 | `Agent N:M Capability` |
| [Resource Profile](e025-resource-profile.md) | 점수의 키 | `Resource Profile N:M Capability` |

---

## 8. Canonical Representation

```json
{
  "taxonomy_version": "1.0",
  "capability_id": "language.generation.copywriting",
  "display_name": "광고 카피 작성",
  "parent": "language.generation",
  "children": [
    "language.generation.copywriting.ad",
    "language.generation.copywriting.landing_page"
  ],
  "description": "목적·타겟·채널이 주어지면 설득력 있는 짧은 문안을 작성한다. 각 문안이 왜 그 타겟에 유효한지 근거를 함께 제시한다.",
  "expected_input": ["타겟 정의", "소구점", "채널", "분량 제약", "브랜드 톤"],
  "expected_output": ["문안 N종", "각 문안의 소구 근거"],
  "measurement": {
    "difficulty": 4,
    "measurement_method": "llm_rubric + human_sample",
    "evaluation_rubric_ref": "rubric_copywriting_v2",
    "scale": "0-100",
    "min_sample": 30,
    "deferred_required": false
  },
  "composed_of": null,
  "aliases": ["copywriting", "text-generation-marketing", "마케팅 카피 작성", "광고 문구 작성"],
  "status": "Active",
  "introduced_in": "1.0",
  "superseded_by": null
}
```

합성 Capability는 다음과 같다.

```json
{
  "capability_id": "marketing.campaign_production",
  "display_name": "캠페인 제작 일괄",
  "parent": "marketing",
  "description": "조사부터 검수까지 캠페인 소재 제작 전 과정을 수행한다.",
  "measurement": {
    "difficulty": 5,
    "measurement_method": "deferred",
    "scale": "0-100",
    "min_sample": 50,
    "deferred_required": true
  },
  "composed_of": [
    "research.web",
    "analysis.audience",
    "language.generation.copywriting",
    "verification.compliance"
  ],
  "aliases": [],
  "status": "Active",
  "introduced_in": "1.0"
}
```

기계가 읽을 수 있는 스키마: [`capability-taxonomy.schema.json`](../intent-os-spec/schemas/capability-taxonomy.schema.json)

---

## 9. Validation Rules

### 9.1 Capability 등록

```
Capability 등록 요청
  ↓
명명 규칙 검사 (CT-001)
  ├── 대문자·공백 포함        → 거부
  ├── 깊이 > 4                → 거부
  ├── 벤더명·도구명 검출       → 거부 + 대체 이름 제안
  └── 복수형 어미              → 경고 + 단수 제안
  ↓
capability_id 중복 검사 (INV-CT-02) ── 중복 시 거부
  ↓
parent 존재 확인 ── 없으면 거부 (상위부터 등록해야 한다)
  ↓
트리 무결성 검사 (INV-CT-01) ── 다중 부모·순환 시 거부
  ↓
description Resource 중립성 검사 (CT-003)
  "프롬프트", "모델", "API" 등 구현 용어 검출 → 경고
  ↓
difficulty 검사 (INV-CT-06) ── 부모보다 낮으면 경고
  ↓
measurement 정의 확인 (INV-CT-05)
  ├── 완비 → Active 가능
  └── 미비 → Draft
  ↓
composed_of 순환 검사 (INV-CT-07)
  ↓
aliases 중복 검사 (INV-CT-03) ── 다른 능력의 별칭과 충돌 시 거부
  ↓
Taxonomy 버전 증가 (§6.2)
```

### 9.2 매칭 알고리즘

Decision Engine이 후보를 생성할 때 호출한다.

```
입력: Task.required_capabilities = [c1, c2, …]
  ↓
각 요구 능력 ci에 대해
  ↓
① 정규화
   Alias Map 조회 → 표준 id로 변환 (CT-006)
   미등록 이름 → Proposed 노드 생성 제안 + 유사도 기반 후보 제시
  ↓
② 후보 Resource 수집
   R(ci) = { r : ∃ c ∈ r.capabilities,  c = ci 또는 c ≺* ci }
                                            └─ 하향 포함 (CT-005)
  ↓
③ 상위 선언은 배제한다
   r이 ci의 부모만 선언했다면 후보에서 제외
   (단, exploration 모드에서는 낮은 confidence로 포함 가능)
  ↓
④ 교집합
   최종 후보 = ∩ R(ci)  for all ci
   ├── 비어 있음 → 단일 Resource로 불가
   │                 → Pipeline / Hybrid 조합 탐색
   │                 → 그래도 없으면 escalate
   └── 있음      → Resource Profile 조회 (e025 §9.3)
  ↓
⑤ 각 후보의 (capability × context) 점수와 confidence 반환
```

**③이 중요하다.** `language.generation`만 선언한 Resource를 `copywriting` Task에 배정하면, 선언되지 않은 능력을 기대하는 것이다.

### 9.3 미지 능력의 처리

Resource 등록 시 Taxonomy에 없는 능력을 선언하면 어떻게 하는가.

```
미등록 capability 발견
  ↓
① Alias Map 조회 ── 있으면 표준 id로 치환하고 종료
  ↓
② 문자열·의미 유사도로 후보 3개 제시
   "ad-copy-writing" → language.generation.copywriting (0.91)
                    → language.generation (0.72)
                    → creation.image (0.11)
  ↓
③ 사람 판정
   ├── 기존 능력이다   → Alias 추가 (patch 버전)
   ├── 새 하위 능력이다 → Proposed 노드 생성 → Draft
   └── 무의미하다      → 거부. Resource 등록 반려
  ↓
④ Proposed 노드는 측정 정의가 완비될 때까지 Active가 되지 않는다 (INV-CT-05)
   그 사이 해당 능력을 요구하는 Task는 생성할 수 없다
```

**자동 등록하지 않는다.** 자동 등록을 허용하면 `copywriting`, `copy-writing`, `copy_writing`이 각각 노드가 되어 Taxonomy가 무너진다.

---

## 10. Examples

### 예시 1 — 매칭 성공

```
task_004  required_capabilities: [
            "language.generation.copywriting",
            "analysis.audience"
          ]

Resource 선언
├── anthropic:claude-5   [language.generation.copywriting, analysis.audience, …]  ✅ 둘 다
├── openai:gpt-5         [language.generation.copywriting, analysis.audience, …]  ✅ 둘 다
├── human:copywriter_kim [language.generation.copywriting, verification.brand_tone] ❌ audience 없음
└── perplexity:sonar     [research.web, analysis.competitor]                       ❌
  ↓
후보: Claude, GPT
```

김 카피라이터가 빠진 이유는 실력이 아니라 **선언된 능력의 조합**이다. 이는 Hybrid 후보(`Claude + 김 카피라이터`) 탐색으로 이어진다.

### 예시 2 — 별칭 흡수

```
외부 Resource 등록
  선언: ["copywriting", "audience-analysis", "web-search"]
  ↓ Alias Map 조회
  copywriting        → language.generation.copywriting   ✅
  audience-analysis  → analysis.audience                 ✅
  web-search         → research.web                      ✅
  ↓
Taxonomy 변경 없이 등록 완료. 즉시 후보군에 편입.
```

**Taxonomy를 바꾸지 않고 외부 다양성을 흡수하는 것이 Alias의 목적이다.**

### 예시 3 — 하향 포함의 비대칭

```
① Task가 language.generation을 요구
   Resource가 language.generation.copywriting을 선언
   → 매칭 ✅  (하위는 상위를 만족)

② Task가 language.generation.copywriting을 요구
   Resource가 language.generation을 선언
   → 매칭 ❌  (상위 선언이 하위를 보장하지 않는다)
```

②를 허용했다면, "글을 쓸 줄 안다"고만 선언한 Resource가 광고 카피 Task에 배정된다. **결과 품질은 실행해봐야 알게 되고, 그 비용은 이미 발생한다.**

### 예시 4 — 능력의 공백 발견

```
Task: 윈터캠프 홍보 영상 제작
required_capabilities: [creation.video, language.generation.script]
  ↓ 매칭
creation.video를 제공하는 Active Resource: 0개
  ↓
결과: 후보 없음 → escalate
  ↓
보고: "이 Goal은 현재 등록된 Resource로 수행할 수 없다.
       creation.video 능력을 가진 Resource 등록이 필요하다."
```

**Taxonomy에 있지만 제공자가 없는 능력**이 시스템의 공백을 드러낸다. 이것이 Rule CT-003(Resource 중립)의 실질적 가치다. Resource 목록에서 Taxonomy를 만들었다면 이 공백은 보이지 않는다.

### 예시 5 — Deprecation

```
1.0  language.generation.marketing_copy   (Active)
2.0  language.generation.copywriting      (Active)   ← 더 일반적인 이름으로 정리
     language.generation.marketing_copy   (Deprecated)
                                          superseded_by: language.generation.copywriting
                                          aliases에 marketing_copy 추가
  ↓
과거 Decision dec_045는 여전히 marketing_copy를 참조한다 → 조회 가능 (INV-CT-04)
새 Task는 copywriting을 요구한다
Resource Profile의 marketing_copy 점수 → copywriting으로 이관 (마이그레이션 스크립트)
```

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **하나의 Resource가 100개 능력을 선언** | 허용하되 `declared_score`의 신뢰도를 낮게 시작한다. 전부 잘한다는 선언은 대개 사실이 아니다. Cold Start 검증이 걸러낸다 |
| **Task가 요구한 능력이 Draft 상태** | Task 생성을 거부한다. 측정할 수 없는 능력을 요구하면 평가가 불가능하다(INV-CT-05) |
| **두 능력이 사실상 같음** | 하나를 `Deprecated`로 하고 다른 하나의 alias로 흡수한다. 중복 능력은 Resource Profile의 표본을 쪼개 신뢰도를 떨어뜨린다 |
| **부모만 선언한 Resource를 꼭 쓰고 싶음** | `exploration` 모드로 낮은 confidence 후보에 포함시킬 수 있다. 단 [Shadow Execution](e013-execution.md)으로 먼저 검증한다 |
| **도메인 특화 능력이 계속 늘어남** | `advertising.*`처럼 최상위가 늘어나는 것은 신호다. 3개 이상 도메인 특화 최상위가 생기면 Taxonomy 구조를 재검토한다 |
| **difficulty 5인데 즉시 평가를 시도** | `deferred_required: true`가 강제한다. 즉시 평가는 `alignment_proxy`로만 기록하고 확정하지 않는다([e015 §11](e015-evaluation.md)) |
| **합성 능력의 구성 요소가 Deprecated** | 합성 능력도 재검토 대상으로 표시한다. 구성이 바뀌면 그것은 다른 능력이다 |
| **인간만 제공 가능한 능력** | 정상이다. `verification.brand_tone`이 그렇다. Taxonomy는 제공자의 종류를 묻지 않는다 |
| **같은 이름이 다른 도메인에서 필요** | 전체 경로가 다르므로 문제없다. `analysis.metrics`와 `advertising.metrics`는 다른 노드다. 단 별칭이 겹치면 INV-CT-03 위반이다 |

---

## 12. Open Issues (v1.0)

### Taxonomy의 초기 완성도

§4.2의 트리는 학원 마케팅 도메인에서 출발했다. 다른 도메인(의료·법률·제조)으로 확장할 때 최상위 도메인이 얼마나 늘어날지 알 수 없다. Rule CT-002가 실제로 지켜질지가 미지수다.

### 의미 기반 매칭

§9.3의 유사도 제시는 문자열 기반을 가정한다. 임베딩 기반 의미 매칭을 쓰면 별칭 관리 부담이 줄지만, **비결정적 매칭**이 된다. Decision의 재현성([e009 Rule D-004](e009-decision.md))과 충돌한다.

### difficulty의 객관화

현재 1~5는 사람이 부여한다. 실제 평가 표본의 분산(variance)이 크면 difficulty가 높은 것이므로, 관측 데이터에서 역산하는 방법이 가능하다. 초기값과 관측값의 조정 규칙이 필요하다.

### 합성 능력의 점수 산출

`marketing.campaign_production`의 점수를 구성 요소 점수에서 계산할 것인가, 독립적으로 측정할 것인가. 최소값·가중평균·독립 측정 중 무엇이 옳은지 근거가 없다. [Volume 4-B §17](../v4b-resource-intelligence.md)과 함께 정해야 한다.

### Taxonomy major 변경의 마이그레이션

부모가 바뀌면 매칭 결과가 달라지고 Resource Profile 점수가 무효화될 수 있다(§6.2). 자동 마이그레이션과 재검증 절차가 정의되지 않았다.

### 앞으로 보강해야 할 항목

- 최상위 도메인별 하위 트리의 완전한 열거
- 능력별 `evaluation_rubric` 정의 ([e015](e015-evaluation.md)의 Rubric과 통합)
- Alias Map의 관리 인터페이스
- 실제 예시 30~50개
