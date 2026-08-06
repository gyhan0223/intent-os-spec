# Entity 006: Capability

- **Version:** v2.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04
- **Schema:** [`capability.schema.json`](../intent-os-spec/schemas/capability.schema.json)

---

## 1. Definition

### 공식 정의

> **Capability is a named, hierarchical unit of ability required to perform a Task, independent of who or what provides it.**

> Capability는 Task 수행에 필요한 능력의 명명된 단위이며, 누가(무엇이) 그 능력을 제공하는지와 무관하게 정의된다.

Capability는 **Intent OS에서 가장 중요한 추상화 계층**이다. (Principle 02 — Capability Before Resource, [Volume 1](../v1-core-concepts.md))

```
❌ 이 일을 GPT에게 맡길까, Claude에게 맡길까?
⭕ 이 일에 필요한 능력은 무엇인가?
   → 그 능력을 가장 잘 제공하는 Resource는 무엇인가?
```

Task와 Resource는 서로를 모른다. **둘은 오직 Capability를 통해서만 만난다.**

```
Task ──(요구)──▶ Capability ◀──(제공)── Resource
```

---

## 2. Capability는 무엇이 아닌가?

### Capability는 Resource가 아니다

❌ `Claude` — 이건 Resource다.

Capability는 "글을 잘 쓰는 능력"이고, Claude는 그 능력을 제공하는 주체 중 하나일 뿐이다. 같은 Capability를 사람 카피라이터도, 다른 모델도 제공할 수 있다.

### Capability는 Skill 이름이 아니다

❌ `"글쓰기 스킬"` — 자유 문자열은 Capability가 아니다.

`글쓰기`, `writing`, `카피 작성`, `copywriting`이 서로 다른 문자열로 존재하면 매칭이 불가능하다. Capability는 **Taxonomy에 등록된 canonical id**를 가져야 한다. (§6)

### Capability는 Task가 아니다

❌ `광고 카피 작성` — 이건 Task다.

Task는 "이번에 할 일"이고, Capability는 "그 일을 하는 데 필요한 재사용 가능한 능력"이다. Task는 소비되고 사라지지만 Capability는 시스템에 영속한다.

### Capability는 모델의 기능(Feature)이 아니다

❌ `128k context window`, `tool use 지원` — 이건 Resource의 사양이다.

사양은 Resource Profile([e007-resource.md](e007-resource.md))에 기록한다. Capability는 "무엇을 할 수 있는가"이지 "어떤 스펙인가"가 아니다.

---

## 3. Design Principles

### Rule CP-001 — Taxonomy에 등록된 canonical id를 가져야 한다

✅ `language.generation.copywriting`

❌ `글빨` — 등록되지 않은 표현. Alias로 매핑되거나 신규 등록 절차를 거쳐야 한다.

### Rule CP-002 — Resource 중립적으로 정의되어야 한다

Capability 정의 안에 특정 Resource의 이름이나 사양이 들어가면 안 된다.

❌ `gpt.copywriting` / ✅ `language.generation.copywriting`

### Rule CP-003 — 관찰 가능해야 한다

Capability는 Execution 결과로부터 **측정 가능**해야 한다. 측정할 수 없는 능력은 Decision Engine이 사용할 수 없다.

- ✅ `language.generation.copywriting` — 산출 카피의 품질/전환율로 측정 가능
- ⚠️ `센스` — 측정 기준이 없다. 더 구체적인 Capability로 분해해야 한다.

### Rule CP-004 — 하나의 능력만 표현해야 한다

❌ `조사하고 글쓰기` — 두 능력이다. `research.search` + `language.generation`으로 분리한다.

### Rule CP-005 — 계층 위치가 명확해야 한다

모든 Capability는 상위 Capability를 가지거나(leaf/중간 노드), 최상위 도메인이어야 한다(root). 고립된 Capability는 Taxonomy가 관리하지 않는다.

---

## 4. Attributes

```
Capability
├── Capability ID (canonical)
├── Display Name
├── Parent
├── Aliases
├── Description
├── Level Scale
├── Related Capabilities
├── Measurement
└── Status
```

| 속성 | 의미 | 예 |
|---|---|---|
| **Capability ID** | Taxonomy 내 canonical id | `language.generation.copywriting` |
| **Display Name** | 사람이 읽는 이름 | `카피라이팅` |
| **Parent** | 상위 Capability | `language.generation` |
| **Aliases** | 자연어 매핑용 동의어 | `카피 작성`, `ad copy`, `광고 문구` |
| **Description** | 능력의 정의 | 설득 목적의 짧은 마케팅 문구 생성 능력 |
| **Level Scale** | 숙련도 표현 방식 | L1~L5 + 0~100 Score |
| **Related Capabilities** | 그래프 관계 | `REQUIRES: psychology.persuasion` |
| **Measurement** | 관찰 방법 | 산출물 품질 평가, 전환율, 사용자 피드백 |
| **Status** | Taxonomy 내 상태 (§6) | Draft / Active / Merged / Deprecated / Retired |

### 4.1 Capability Taxonomy

Capability는 계층 구조를 가진다. [Volume 1](../v1-core-concepts.md) §3.4의 Communication 트리를 canonical id 체계로 확장하면 다음과 같다.

```
language                            (언어)
├── generation                      (생성)
│   ├── copywriting                 (카피라이팅)
│   ├── technical_writing           (기술 문서)
│   ├── storytelling                (스토리텔링)
│   └── long_form                   (장문 작성)
├── translation                     (번역)
├── summarization                   (요약)
└── persuasion                      (설득 구조 설계)

research                            (조사)
├── search                          (검색)
├── data_collection                 (데이터 수집)
└── fact_verification               (사실 검증)

analysis                            (분석)
├── data                            (데이터 분석)
├── competitor                      (경쟁 분석)
├── audience                        (타겟/고객 분석)
└── pattern_discovery               (패턴 발견)

creative                            (창의)
├── ideation                        (아이디어 발상)
├── visual_design                   (시각 디자인)
└── brand_strategy                  (브랜드 전략)

reasoning                           (추론)
├── planning                        (계획 수립)
├── mathematical                    (수리)
└── causal                          (인과 추론)

interaction                         (상호작용)
├── consultation                    (상담)
├── negotiation                     (협상)
└── empathy                         (감성 이해)
```

**주의:** 계층은 편의상 트리로 표기하지만, 실제 Capability는 **Graph**다. `copywriting`은 `persuasion`을 필요로 하고, `persuasion`은 `psychology`와 연결된다. ([Volume 4-B §6 Capability Ontology](../v4b-resource-intelligence.md) 참조)

```
copywriting ──REQUIRES──▶ persuasion ──REQUIRES──▶ psychology
     │                                                  │
     └────SUPPORTS──▶ brand_strategy                    ▼
                                                    reasoning
```

| 관계 | 의미 |
|---|---|
| `REQUIRES` | 이 능력 없이는 성립하지 않는다 |
| `SUPPORTS` | 있으면 품질이 올라간다 |
| `COMPOSES` | 여러 능력이 합쳐져 상위 능력을 이룬다 |

### 4.2 명명 규칙 (Canonical ID)

Capability ID는 다음 문법을 따른다.

```ebnf
CapabilityID ::= Domain ( "." Segment )*
Domain       ::= LowercaseWord
Segment      ::= LowercaseWord ( "_" LowercaseWord )*
```

#### 규칙

1. **소문자 + 점(.) 구분.** 점은 계층을 의미한다. `language.generation.copywriting`
2. **깊이는 원칙적으로 2~4단계.** 1단계는 도메인 root, 5단계 이상은 과도한 세분화다.
3. **복합어는 밑줄(_).** `technical_writing` (하이픈, 공백, 대문자 금지)
4. **언어·도메인 변형은 하위 노드가 아니라 Context로 처리한다.** `language.generation.copywriting.korean` ❌ — 한국어 성능은 Context-Aware Ranking([Volume 4-B §9](../v4b-resource-intelligence.md))의 소관이다.
5. **자연어는 Alias 테이블로 매핑한다.** `광고 문구 써줘` → alias `광고 문구` → `language.generation.copywriting`

✅ `analysis.competitor` / ✅ `research.fact_verification`

❌ `Copywriting` (대문자) / ❌ `claude.writing` (Resource 이름) / ❌ `잘쓰기` (미등록 자유 문자열)

### 4.3 Capability Level

같은 Capability라도 Resource마다 수준이 다르다. 수준은 두 가지 표현을 함께 사용한다.

#### 7.1 Score (0~100)

연속적인 성능 점수. Capability DNA([Volume 4-B §4](../v4b-resource-intelligence.md))의 값과 동일한 축이다.

#### 7.2 Level (L1~L5)

Task의 요구 수준을 표현하기 위한 이산 등급.

| Level | 이름 | Score 구간 | 의미 |
|---|---|--:|---|
| **L1** | Basic | 0~39 | 단순 반복 수행 가능 |
| **L2** | Functional | 40~59 | 일반적인 품질로 수행 가능 |
| **L3** | Proficient | 60~79 | 상업적으로 쓸 수 있는 수준 |
| **L4** | Advanced | 80~92 | 전문가 수준 |
| **L5** | Expert | 93~100 | 해당 분야 최상위 |

예)

```
Task: 윈터캠프 광고 카피 3종 작성
  required: language.generation.copywriting ≥ L3
  required: analysis.audience ≥ L2
```

#### 7.3 Score에는 Confidence가 붙는다

선언된 점수와 관찰된 점수는 다르다. Intent OS는 Score보다 **Confidence를 더 중요하게 본다.** ([Volume 4-B §10](../v4b-resource-intelligence.md))

| | Score | Confidence |
|---|--:|--:|
| 1000회 실행으로 검증된 Resource | 91 | 0.97 |
| 어제 등록된 신규 Resource | 95 | 0.20 |

---

## 5. Invariants

### INV-CP-01 — 모든 Capability는 Taxonomy 안의 한 자리를 차지한다

Rule CP-001·CP-005가 생성 검사라면 이쪽은 항상 성립해야 하는 상태다. 부모도 없고 root도 아닌 Capability는 매칭 경로에서 영원히 발견되지 않는다.

| | |
|---|---|
| **위반 시** | 해당 Capability를 `Draft`로 되돌리고 매칭 후보에서 제외한다. 이미 이 Capability를 요구하는 Task가 있으면 Task를 `Pending`으로 되돌린다 |
| **탐지** | 등록 시점, Taxonomy 개정 시점 |

### INV-CP-02 — canonical id는 재사용되지 않는다

`language.generation.copywriting`이 폐기된 뒤 다른 뜻으로 되살아나면, 과거 Decision의 근거가 조용히 다른 의미로 읽힌다.

| | |
|---|---|
| **위반 시** | 등록을 거부한다. 폐기된 id는 `Deprecated`로 남고 `superseded_by`로 후속 id를 가리킨다. **지우지 않는다** |

### INV-CP-03 — Capability 정의에 Resource 이름이 없다

Rule CP-002의 상태 표현이다. 정의뿐 아니라 alias·description 어디에도 없어야 한다.

| | |
|---|---|
| **위반 시** | 해당 표현을 제거한다. 제거할 수 없으면 그 Capability는 능력이 아니라 사양이므로 [Resource Profile](e025-resource-profile.md)로 옮긴다 |

### INV-CP-04 — 측정 방법이 없는 Capability로는 점수를 매기지 않는다

`measurement_method: deferred`인 Capability에 `observed_score`가 붙어 있으면, 근거 없는 숫자가 Decision을 움직인다.

| | |
|---|---|
| **위반 시** | 점수를 무효로 표시하고 Utility 계산에서 제외한다. 값을 0으로 바꾸지 않는다 — **측정 안 함과 0점은 다르다** |

### INV-CP-05 — REQUIRES 관계에 순환이 없다

`A REQUIRES B`, `B REQUIRES A`이면 어느 쪽도 성립 조건을 만족할 수 없다.

| | |
|---|---|
| **위반 시** | 관계 추가를 거부하고 순환 경로를 반환한다. 상호 의존은 `SUPPORTS`로 표현한다 |

### INV-CP-06 — Alias는 두 canonical id를 동시에 가리키지 않는다

`카피 작성`이 `language.generation.copywriting`과 `creative.ideation` 양쪽에 매핑되면, 자연어 입력의 해석이 갈린다.

| | |
|---|---|
| **위반 시** | 나중에 등록된 매핑을 거부한다. 정말 두 뜻이면 alias가 모호한 것이므로 alias 자체를 분리한다 |

Entity 간 불변식은 [e000a-entity-relationships.md](e000a-entity-relationships.md)가 단일 권위다.

---

## 6. Lifecycle

Capability는 Taxonomy 안에서 상태를 갖는다. Taxonomy는 표준이므로 **삭제가 없고 폐기만 있다.**

```
Draft → Active ──▶ Deprecated ──▶ Retired
           │            ▲
           └──▶ Merged ─┘
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Draft** | 등록 제안됨. 매칭에 쓰이지 않는다 | 신규 등록 요청 |
| **Active** | 표준으로 확정. 매칭·측정에 쓰인다 | 검증 통과 (§9) |
| **Merged** | 다른 Capability에 흡수됨 | 중복 판정. `superseded_by`가 가리키는 id로 매칭이 넘어간다 |
| **Deprecated** | 더 쓰지 않기로 함. 기존 참조는 유효 | 폐기 결정 |
| **Retired** | 참조가 모두 정리됨. 조회 전용 | 참조 카운트 0 |

**어느 상태에서도 canonical id는 회수되지 않는다**(INV-CP-02). 과거 Decision이 그 id로 근거를 남겼기 때문이다.

---

## 7. Relationships

```
Task ──(required_capabilities)──▶ Capability ◀──(capabilities)── Resource
                                      │
                                      ▼
                              Decision Engine (매칭·선택)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Task](e005-task.md) | Task는 Capability를 요구한다. Capability 없는 Task는 라우팅 불가 | `Task N:M Capability` |
| [Resource](e007-resource.md) | Resource는 Capability를 제공하고, 제공 수준이 측정된다 | `Capability N:M Resource` |
| [Goal](e001-goal.md) | Goal은 Capability를 직접 참조하지 않는다 (Task를 거쳐서만) | 직접 관계 없음 ([Rule REL-004](e000a-entity-relationships.md)) |
| [Capability Taxonomy](e006a-capability-taxonomy.md) | 계층과 관계의 정본. Capability 문서는 노드 하나를 정의한다 | `Capability Taxonomy 1:N Capability` |
| [Decision](e009-decision.md) | Capability Matching 결과가 Decision의 입력이다 | `Capability N:M Decision` |
| [Resource Profile](e025-resource-profile.md) | Capability별 관측 점수가 여기 쌓인다 | `Capability N:M Resource Profile` |
| [Knowledge](e011-knowledge.md) | Taxonomy 자체가 시스템 Knowledge의 일부다 | `Capability 1:0..N Knowledge` |

**Task도 Resource도 Capability를 참조하고, Capability는 어느 쪽도 참조하지 않는다.** 표준이 사용처를 알면 표준이 아니다.

### 7.1 Capability DNA와의 관계

본 문서의 Capability는 **Taxonomy(정의 체계)** 이고, [Volume 4-B](../v4b-resource-intelligence.md)의 Capability DNA는 **측정 결과(Resource별 점수 벡터)** 다.

| | 본 문서 (Entity 006) | Volume 4-B |
|---|---|---|
| 대상 | Capability의 정의와 명명 | Resource가 가진 Capability의 측정 |
| 산출물 | Taxonomy, canonical id | Capability Vector, Confidence, Drift |
| 변경 주기 | 느리다 (표준) | 빠르다 (실행마다 갱신) |

Capability DNA의 키(`writing`, `reasoning` 등)는 장기적으로 본 Taxonomy의 canonical id로 정규화되어야 한다. (Open Issue, §13)

---

## 8. Canonical Representation

Taxonomy에 등록되는 Capability는 내부적으로 동일한 구조를 가진다.

```json
{
  "capability_id": "language.generation.copywriting",
  "display_name": "카피라이팅",
  "parent": "language.generation",
  "aliases": ["카피 작성", "광고 문구", "ad copy"],
  "description": "설득 목적의 짧은 마케팅 문구를 생성하는 능력",
  "related": [
    { "capability_id": "language.persuasion", "relation": "REQUIRES" },
    { "capability_id": "creative.brand_strategy", "relation": "SUPPORTS" }
  ],
  "measurement": ["output_quality", "conversion_rate", "user_feedback"],
  "status": "Active"
}
```

기계가 읽을 수 있는 스키마: [`capability.schema.json`](../intent-os-spec/schemas/capability.schema.json)

---

## 9. Validation Rules

새 Capability 등록 요청(주로 Planner의 Capability 추론 또는 Resource 등록 시 발생)은 다음을 거친다.

```
Capability 후보 (예: "블로그 글빨")
  ↓
Alias 탐색 ── 기존 id에 매핑 가능? ──▶ 기존 id 반환, Alias 추가
  ↓ (매핑 불가)
Resource 이름 검출 (C-002) ── 검출 시 반려
  ↓
단일 능력 검사 (C-004) ── 복합이면 분해 제안
  ↓
측정 가능성 검사 (C-003) ── 불가하면 하위 분해 요구
  ↓
계층 위치 결정 (C-005) ── 부모 노드 지정
  ↓
canonical id 부여 → Status: Draft로 등록
  ↓
실사용 데이터 축적 후 Active 승격
```

### 9.1 Capability Matching

Decision Engine의 첫 단계는 Task의 `required_capabilities`와 Resource의 `capabilities`를 매칭하는 것이다.

```
Task.required_capabilities
  ↓
① Alias 해소 → canonical id 정규화
  ↓
② Exact Match — 같은 id를 제공하는 Resource 후보 수집
  ↓
③ Hierarchy Match — 정확히 일치하는 Resource가 없으면
   상위 노드 제공자를 후보에 포함 (감점 적용)
   예: copywriting 제공자가 없으면 language.generation 제공자 탐색
  ↓
④ Level Filter — required level 미달 후보 제거
  ↓
⑤ Confidence Filter — confidence < threshold 후보는
   저위험 Task에서만 허용 (Cold Start Strategy)
  ↓
⑥ Graph Expansion — REQUIRES 관계로 연결된 Capability의
   보유 여부를 가산점으로 반영
  ↓
후보 Resource 목록 → Decision Engine (Score 계산은 Volume 4)
```

#### Matching 판정 예시

```
Task 요구: language.generation.copywriting ≥ L3

Resource A: copywriting 87 (conf 0.95)      → ✅ 후보 (L4)
Resource B: language.generation 72 (conf 0.9) → ⚠️ 후보 (Hierarchy Match, 감점)
Resource C: copywriting 95 (conf 0.15)      → ⚠️ 저위험 Task에서만
Resource D: analysis.data 90                → ❌ 제외
```

**주의:** Matching은 후보를 만드는 단계까지다. 최종 선택(비용, 지연, 위험 반영)은 Decision Engine([Volume 4](../v4-decision-engine.md))의 소관이다.

---

## 10. Examples

### 예시 1 — Task 하나의 Capability 요구와 매칭

```
task_004  인스타그램 광고 카피 3종 작성
  required_capabilities:
    language.generation.copywriting   (필수, 최소 L3)
    analysis.audience                 (선호)

후보 매칭
  anthropic:claude-5    copywriting 88 (conf 0.82)  → Exact Match   ✅
  openai:gpt            copywriting 85 (conf 0.79)  → Exact Match   ✅
  human:copywriter_kim  copywriting 94 (conf 0.91)  → Exact Match   ✅ (지연 4시간)
  perplexity            research.search 90          → 미보유        ❌
```

Perplexity는 점수가 높지만 요구 Capability를 갖지 않았으므로 후보에 오르지 않는다. **점수 이전에 보유 여부가 필터다.**

### 예시 2 — Hierarchy Match와 감점

```
task_012  기술 블로그 장문 작성
  required: language.generation.long_form

후보
  A  language.generation.long_form  82 (conf 0.85)  → Exact          82점
  B  language.generation            91 (conf 0.90)  → Hierarchy(상위)  감점 적용
  C  language.generation.copywriting 95 (conf 0.88) → 형제 노드        후보 아님
```

B는 상위 노드 점수라 "이 세부 능력을 실제로 측정한 적은 없다"는 뜻이다. C는 점수가 가장 높지만 **형제 노드는 대체재가 아니다** — 카피라이팅을 잘한다고 장문을 잘 쓰는 것이 아니다.

### 예시 3 — 측정 불가 Capability의 분해

```
❌ "센스 있는 카피"  → measurement_method 없음 (Rule CP-003 위반)
   ↓ 분해
✅ language.generation.copywriting   측정: 산출 카피의 전환율
✅ creative.brand_strategy           측정: 브랜드 가이드 준수율 (LLM rubric)
✅ interaction.empathy               측정: deferred — 점수를 매기지 않는다 (INV-CP-04)
```

세 번째는 분해해도 여전히 측정 방법이 없다. 그래도 **없는 척하지 않고 `deferred`로 남긴다.** 다만 점수는 붙이지 않는다.

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **같은 능력에 두 canonical id가 존재** | 하나를 `Merged`로 내리고 `superseded_by`로 잇는다. 어느 쪽을 남길지는 참조 수가 많은 쪽이다. 둘 다 지우고 새로 만들면 과거 점수 이력이 끊긴다 |
| **Resource가 선언한 Capability가 Taxonomy에 없음** | 등록을 보류하고 `Draft`로 받는다. 거부하지 않는 이유는 신규 능력의 발견 경로가 여기이기 때문이다. 단 `Draft` Capability로는 매칭하지 않는다 |
| **Capability는 있는데 측정 데이터가 0건** | `observed_score`를 0이 아니라 **부재**로 둔다. 0으로 두면 Utility가 "가장 못하는 Resource"로 오판한다 |
| **상위 노드 점수만 있고 하위 노드 점수가 없음** | Hierarchy Match로 후보에는 올리되 감점한다. 실행 결과가 쌓이면 하위 노드 점수가 생기고 감점이 사라진다 |
| **Capability가 너무 세분화됨** (`copywriting.instagram.korean.parent_targeted`) | 표본이 흩어져 어느 노드도 유의미한 점수를 못 갖는다. 측정 표본이 계속 부족하면 상위로 병합한다. **분류의 목적은 측정이지 정확한 명명이 아니다** |
| **인간과 AI가 같은 Capability를 가짐** | 정상이다. Capability는 Resource 중립이다(INV-CP-03). 지연·비용 차이는 Capability가 아니라 [Resource Profile](e025-resource-profile.md)이 담는다 |
| **Task가 요구한 Capability를 아무도 갖지 않음** | Task를 실패시키지 않고 Capability 부재로 보고한다. Resource 등록이나 Task 재분해가 답이다([e005 §11](e005-task.md)) |

---

## 12. Open Issues (v1.0)

### Taxonomy 거버넌스

Taxonomy는 표준이다. 누가, 어떤 절차로 노드를 추가/병합/폐기하는가? 사용자마다 Taxonomy가 갈라지면 Global Resource Intelligence Network([Volume 4-B §19](../v4b-resource-intelligence.md))의 집계가 불가능해진다.

### Capability Embedding과의 이원화

[Volume 4-B Appendix ①](../v4b-resource-intelligence.md)은 장기적으로 Task와 Resource를 같은 벡터 공간에 매핑하는 방향을 제안한다. 이 경우 canonical id 체계는 사라지는 것이 아니라 **벡터 공간의 라벨/앵커** 역할로 재정의되어야 한다. 두 표현의 동기화 규칙이 필요하다.

### 앞으로 보강해야 할 항목

- Capability DNA 키의 canonical id 정규화 매핑표
- Hierarchy Match 감점 계수의 기준값
- Alias 자동 학습 규칙 (자연어 → canonical id)
- 도메인 root 목록의 확정 (v1.0은 language / research / analysis / creative / reasoning / interaction 6개로 시작)
- 실제 예시 30~50개

