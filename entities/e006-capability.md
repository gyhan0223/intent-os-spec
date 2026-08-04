# Entity 006: Capability

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

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

## 3. Capability의 조건

### Rule C-001 — Taxonomy에 등록된 canonical id를 가져야 한다

✅ `language.generation.copywriting`

❌ `글빨` — 등록되지 않은 표현. Alias로 매핑되거나 신규 등록 절차를 거쳐야 한다.

### Rule C-002 — Resource 중립적으로 정의되어야 한다

Capability 정의 안에 특정 Resource의 이름이나 사양이 들어가면 안 된다.

❌ `gpt.copywriting` / ✅ `language.generation.copywriting`

### Rule C-003 — 관찰 가능해야 한다

Capability는 Execution 결과로부터 **측정 가능**해야 한다. 측정할 수 없는 능력은 Decision Engine이 사용할 수 없다.

- ✅ `language.generation.copywriting` — 산출 카피의 품질/전환율로 측정 가능
- ⚠️ `센스` — 측정 기준이 없다. 더 구체적인 Capability로 분해해야 한다.

### Rule C-004 — 하나의 능력만 표현해야 한다

❌ `조사하고 글쓰기` — 두 능력이다. `research.search` + `language.generation`으로 분리한다.

### Rule C-005 — 계층 위치가 명확해야 한다

모든 Capability는 상위 Capability를 가지거나(leaf/중간 노드), 최상위 도메인이어야 한다(root). 고립된 Capability는 Taxonomy가 관리하지 않는다.

---

## 4. Capability Attributes

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
| **Status** | Taxonomy 내 상태 | Draft / Active / Deprecated / Merged |

---

## 5. Capability Taxonomy

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

---

## 6. Capability 명명 규칙 (Canonical ID)

Capability ID는 다음 문법을 따른다.

```ebnf
CapabilityID ::= Domain ( "." Segment )*
Domain       ::= LowercaseWord
Segment      ::= LowercaseWord ( "_" LowercaseWord )*
```

### 규칙

1. **소문자 + 점(.) 구분.** 점은 계층을 의미한다. `language.generation.copywriting`
2. **깊이는 원칙적으로 2~4단계.** 1단계는 도메인 root, 5단계 이상은 과도한 세분화다.
3. **복합어는 밑줄(_).** `technical_writing` (하이픈, 공백, 대문자 금지)
4. **언어·도메인 변형은 하위 노드가 아니라 Context로 처리한다.** `language.generation.copywriting.korean` ❌ — 한국어 성능은 Context-Aware Ranking([Volume 4-B §9](../v4b-resource-intelligence.md))의 소관이다.
5. **자연어는 Alias 테이블로 매핑한다.** `광고 문구 써줘` → alias `광고 문구` → `language.generation.copywriting`

✅ `analysis.competitor` / ✅ `research.fact_verification`

❌ `Copywriting` (대문자) / ❌ `claude.writing` (Resource 이름) / ❌ `잘쓰기` (미등록 자유 문자열)

---

## 7. Capability Level

같은 Capability라도 Resource마다 수준이 다르다. 수준은 두 가지 표현을 함께 사용한다.

### 7.1 Score (0~100)

연속적인 성능 점수. Capability DNA([Volume 4-B §4](../v4b-resource-intelligence.md))의 값과 동일한 축이다.

### 7.2 Level (L1~L5)

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

### 7.3 Score에는 Confidence가 붙는다

선언된 점수와 관찰된 점수는 다르다. Intent OS는 Score보다 **Confidence를 더 중요하게 본다.** ([Volume 4-B §10](../v4b-resource-intelligence.md))

| | Score | Confidence |
|---|--:|--:|
| 1000회 실행으로 검증된 Resource | 91 | 0.97 |
| 어제 등록된 신규 Resource | 95 | 0.20 |

---

## 8. Capability Matching

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

### Matching 판정 예시

```
Task 요구: language.generation.copywriting ≥ L3

Resource A: copywriting 87 (conf 0.95)      → ✅ 후보 (L4)
Resource B: language.generation 72 (conf 0.9) → ⚠️ 후보 (Hierarchy Match, 감점)
Resource C: copywriting 95 (conf 0.15)      → ⚠️ 저위험 Task에서만
Resource D: analysis.data 90                → ❌ 제외
```

**주의:** Matching은 후보를 만드는 단계까지다. 최종 선택(비용, 지연, 위험 반영)은 Decision Engine([Volume 4](../v4-decision-engine.md))의 소관이다.

---

## 9. Capability DNA와의 관계

본 문서의 Capability는 **Taxonomy(정의 체계)** 이고, [Volume 4-B](../v4b-resource-intelligence.md)의 Capability DNA는 **측정 결과(Resource별 점수 벡터)** 다.

| | 본 문서 (Entity 006) | Volume 4-B |
|---|---|---|
| 대상 | Capability의 정의와 명명 | Resource가 가진 Capability의 측정 |
| 산출물 | Taxonomy, canonical id | Capability Vector, Confidence, Drift |
| 변경 주기 | 느리다 (표준) | 빠르다 (실행마다 갱신) |

Capability DNA의 키(`writing`, `reasoning` 등)는 장기적으로 본 Taxonomy의 canonical id로 정규화되어야 한다. (Open Issue, §13)

---

## 10. Canonical Capability Representation

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

## 11. Capability 검증 알고리즘

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

---

## 12. 다른 Entity와의 관계

```
Task ──(required_capabilities)──▶ Capability ◀──(capabilities)── Resource
                                      │
                                      ▼
                              Decision Engine (매칭·선택)
```

| Entity | 관계 |
|---|---|
| [Task](e005-task.md) | Task는 Capability를 요구한다. Capability 없는 Task는 라우팅 불가 |
| [Resource](e007-resource.md) | Resource는 Capability를 제공하고, 제공 수준이 측정된다 |
| [Goal](e001-goal.md) | Goal은 Capability를 직접 참조하지 않는다 (Task를 거쳐서만) |
| Decision (Entity 009, 예정) | Capability Matching 결과가 Decision의 입력이다 |
| Knowledge (Entity 011, 예정) | Taxonomy 자체가 시스템 Knowledge의 일부다 |

---

## 13. Open Issues (v1.0)

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
