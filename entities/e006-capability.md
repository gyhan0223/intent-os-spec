# Entity 006: Capability

- **Version:** v2.0 Draft
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

### 1.1 이 문서와 Taxonomy(006-A)의 역할 분담

| | 본 문서 (006) | [Capability Taxonomy](e006a-capability-taxonomy.md) (006-A) |
|---|---|---|
| 답하는 질문 | Capability란 **무엇인가** | 이름을 **어떻게 관리하는가** |
| 다루는 것 | 정의, 의미 관계(REQUIRES/SUPPORTS), 숙련도 | 명명 규칙, 계층, 별칭, 측정 정의, 버전 |
| 권위 | 개념과 의미 관계 | **식별자·매칭·난이도** |

> **v1.0 → v2.0 변경:** v1.0의 §5(Taxonomy 트리)와 §6(명명 규칙)은 [Entity 006-A](e006a-capability-taxonomy.md)로 이관되었다. Rule Prefix도 `C` → **`CP`** 로 변경되었다 — [Context](e003-context.md)가 이미 `C`를 쓰고 있어 충돌했기 때문이다([e000 §3](e000-spec-format.md)).

---

## 2. Capability는 무엇이 아닌가?

### Capability는 Resource가 아니다

❌ `Claude` — 이건 [Resource](e007-resource.md)다.

Capability는 "글을 잘 쓰는 능력"이고, Claude는 그 능력을 제공하는 주체 중 하나일 뿐이다. 같은 Capability를 사람 카피라이터도, 다른 모델도 제공한다.

**방향이 중요하다.** Resource가 Capability를 선언하지, Capability가 Resource를 나열하지 않는다([INV-09](e000a-entity-relationships.md)). 그래서 **아무도 제공하지 않는 Capability도 존재할 수 있다** — 그것이 시스템의 공백을 드러낸다.

### Capability는 Skill 이름이 아니다

❌ `"글쓰기 스킬"` — 자유 문자열은 Capability가 아니다.

`글쓰기`, `writing`, `카피 작성`, `copywriting`이 서로 다른 문자열로 존재하면 매칭이 불가능하다. Capability는 **[Taxonomy](e006a-capability-taxonomy.md)에 등록된 canonical id**를 가져야 한다.

### Capability는 Task가 아니다

❌ `광고 카피 작성` — 이건 [Task](e005-task.md)다.

Task는 "이번에 할 일"이고, Capability는 "그 일을 하는 데 필요한 재사용 가능한 능력"이다. Task는 소비되고 사라지지만 Capability는 시스템에 영속한다.

### Capability는 모델의 사양(Feature)이 아니다

❌ `128k context window`, `tool use 지원` — 이건 Resource의 사양이다.

사양은 [Resource](e007-resource.md)의 `limitations`나 [Profile](e025-resource-profile.md)에 기록한다. Capability는 "무엇을 할 수 있는가"이지 "어떤 스펙인가"가 아니다.

### Capability는 점수가 아니다

❌ `Claude의 카피 작성 93점` — 이건 [Resource Profile](e025-resource-profile.md)의 `capability_scores`다.

Capability는 **측정의 대상**이지 측정값이 아니다. 하나의 Capability에 대해 Resource마다·Context마다 다른 점수가 존재한다.

---

## 3. Design Principles

### Rule CP-001 — Taxonomy에 등록된 canonical id를 가져야 한다

✅ `language.generation.copywriting`

❌ `글빨` — 등록되지 않은 표현. Alias로 매핑되거나 신규 등록 절차를 거쳐야 한다([e006a §9.3](e006a-capability-taxonomy.md)).

### Rule CP-002 — Resource 중립적으로 정의되어야 한다

Capability 정의 안에 특정 Resource의 이름이나 사양이 들어가면 안 된다.

❌ `gpt.copywriting` / ✅ `language.generation.copywriting`

정의문 자체도 중립적이어야 한다.

- ✅ `목적과 타겟이 주어지면 설득력 있는 짧은 문안을 작성한다`
- ❌ `프롬프트를 받아 텍스트를 생성한다` — LLM을 전제한 서술이다. 김 카피라이터도 이 능력을 제공한다

### Rule CP-003 — 관찰 가능해야 한다

Capability는 Execution 결과로부터 **측정 가능**해야 한다. 측정 정의(난이도·방법·최소 표본)는 [Taxonomy](e006a-capability-taxonomy.md)가 갖는다.

- ✅ `language.generation.copywriting` — 산출 카피의 품질/전환율로 측정 가능
- ⚠️ `센스` — 측정 기준이 없다. 더 구체적인 Capability로 분해해야 한다

측정 정의가 없으면 Capability는 `Active`가 될 수 없다([INV-CT-05](e006a-capability-taxonomy.md)).

### Rule CP-004 — 하나의 능력만 표현해야 한다

❌ `조사하고 글쓰기` — 두 능력이다. `research.web` + `language.generation.copywriting`으로 분리한다.

예외는 **합성 Capability**다([Rule CT-009](e006a-capability-taxonomy.md)). 여러 능력의 조합이 하나처럼 자주 쓰이면 `composed_of`를 갖는 노드로 명시적으로 등록한다.

### Rule CP-005 — 계층 위치가 명확해야 한다

모든 Capability는 부모를 정확히 하나 가지거나 최상위 도메인이어야 한다([Rule CT-004](e006a-capability-taxonomy.md)). 고립된 Capability는 Taxonomy가 관리하지 않는다.

### Rule CP-006 — 의미 관계는 계층과 별개다

계층(`parent`)은 **포함 관계**이고, 의미 관계(`related`)는 **의존·보완 관계**다. 둘을 섞지 않는다(§4.2).

```
계층    copywriting ⊂ language.generation        (트리)
의미    copywriting REQUIRES analysis.audience   (그래프)
```

### Rule CP-007 — 폐기해도 삭제하지 않는다

쓰이지 않는 Capability도 지우지 않는다. 과거 [Decision](e009-decision.md)과 [Resource Profile](e025-resource-profile.md)이 그 이름을 참조하고 있다([INV-CT-04](e006a-capability-taxonomy.md)).

---

## 4. Attributes

```
Capability
├── Identity
│   ├── capability_id
│   ├── display_name
│   └── parent
├── Definition
│   ├── description
│   └── aliases[]
├── Semantics
│   └── related[]           (REQUIRES / SUPPORTS / COMPOSES)
├── Level
│   └── level_scale
└── Status
    └── status
```

| 속성 | 의미 | 예 |
|---|---|---|
| **capability_id** | Taxonomy 내 canonical id | `language.generation.copywriting` |
| **display_name** | 사람이 읽는 이름 | `광고 카피 작성` |
| **parent** | 상위 Capability | `language.generation` |
| **description** | 능력의 정의 (Resource 중립) | 목적·타겟·채널이 주어지면 설득력 있는 짧은 문안을 작성한다 |
| **aliases** | 자연어·외부 이름 매핑 | `카피 작성`, `광고 문구`, `copywriting` |
| **related** | 의미 관계 (§4.2) | `REQUIRES: analysis.audience` |
| **level_scale** | 숙련도 표현 (§4.1) | `L1~L5 + 0~100 Score` |
| **status** | Taxonomy 내 상태 (§6) | Active |

측정 정의(`difficulty`, `measurement_method`, `min_sample`)는 **[Taxonomy 노드](e006a-capability-taxonomy.md)가 갖는다.** 여기에 중복 보관하지 않는다.

### 4.1 Capability Level

같은 Capability라도 Resource마다 수준이 다르다. 수준은 두 가지 표현을 함께 쓴다.

#### Score (0~100)

연속적인 성능 점수. [Resource Profile](e025-resource-profile.md)의 `capability_scores`에 (Capability × Context)별로 저장된다.

#### Level (L1~L5)

Task의 **요구 수준**을 표현하기 위한 이산 등급.

| Level | 이름 | Score 구간 | 의미 |
|---|---|--:|---|
| **L1** | Basic | 0~39 | 단순 반복 수행 가능 |
| **L2** | Functional | 40~59 | 일반적인 품질로 수행 가능 |
| **L3** | Proficient | 60~79 | 상업적으로 쓸 수 있는 수준 |
| **L4** | Advanced | 80~92 | 전문가 수준 |
| **L5** | Expert | 93~100 | 해당 분야 최상위 |

```
Task: 윈터캠프 광고 카피 3종 작성
  required: language.generation.copywriting ≥ L3
  required: analysis.audience ≥ L2
```

#### Score보다 Confidence가 중요하다

선언된 점수와 관찰된 점수는 다르다([Volume 4-B §10](../v4b-resource-intelligence.md)).

| | Score | Confidence | 판단 |
|---|--:|--:|---|
| 1000회 실행으로 검증된 Resource | 91 | 0.97 | 신뢰 가능 |
| 어제 등록된 신규 Resource | 95 | 0.20 | 저위험 Task에서만 |

**95점이 91점보다 나은 선택이 아니다.** 이것이 [Profile](e025-resource-profile.md)이 점수와 confidence를 함께 반환하는 이유다([e025 §9.3](e025-resource-profile.md)).

### 4.2 의미 관계 (Semantic Relations)

계층은 트리지만 **의미 관계는 그래프**다([Volume 4-B §6](../v4b-resource-intelligence.md)).

```
language.generation.copywriting
   │ REQUIRES
   ▼
analysis.audience ──REQUIRES──▶ research.web
   │
   │ SUPPORTS
   ▼
verification.brand_tone
```

| 관계 | 의미 | 매칭에서의 효과 |
|---|---|---|
| `REQUIRES` | 이 능력 없이는 성립하지 않는다 | 후보가 둘 다 가져야 한다 |
| `SUPPORTS` | 있으면 품질이 올라간다 | 가산점 |
| `COMPOSES` | 여러 능력이 합쳐져 상위 능력을 이룬다 | [합성 Capability](e006a-capability-taxonomy.md)의 `composed_of`와 대응 |

**`parent`와 `REQUIRES`를 혼동하면 안 된다**(Rule CP-006). `copywriting`의 부모는 `language.generation`이지 `analysis.audience`가 아니다.

---

## 5. Invariants

### INV-CP-01 — Capability는 Resource를 참조하지 않는다

[INV-09](e000a-entity-relationships.md) Layer Isolation의 Capability 측 표현이다.

| | |
|---|---|
| **위반 시** | 필드 추가를 거부한다. 새 Resource를 등록할 때마다 Taxonomy를 고쳐야 하는 구조가 된다 |
| **근거** | 아무도 제공하지 않는 Capability가 존재할 수 있어야 시스템의 공백이 보인다 |

### INV-CP-02 — capability_id는 전역 고유하며 재사용되지 않는다

| | |
|---|---|
| **위반 시** | 등록 거부 ([INV-CT-02](e006a-capability-taxonomy.md)). 같은 이름의 다른 능력은 존재할 수 없다 |

### INV-CP-03 — Active Capability는 측정 정의를 갖는다

| | |
|---|---|
| **위반 시** | `Draft`로 강등. 측정할 수 없는 능력을 Task가 요구하면 평가가 불가능해진다 |
| **연쇄** | Draft Capability를 요구하는 Task는 생성이 거부된다 ([e005 §9](e005-task.md)) |

### INV-CP-04 — related 관계는 순환하지 않는다

`REQUIRES` 체인이 순환하면 매칭이 무한 루프에 빠진다.

| | |
|---|---|
| **위반 시** | 관계 생성 거부. 순환 경로를 반환 |
| **주의** | `SUPPORTS`는 상호 참조가 가능하다. 순환 검사는 `REQUIRES`와 `COMPOSES`에만 적용한다 |

### INV-CP-05 — Deprecated Capability는 삭제되지 않는다

| | |
|---|---|
| **위반 시** | 삭제 차단. 과거 Decision·Profile의 참조가 끊긴다 (Rule CP-007) |

### INV-CP-06 — 상위 선언은 하위를 만족시키지 않는다

매칭의 비대칭성이다([Rule CT-005](e006a-capability-taxonomy.md)).

| | |
|---|---|
| **위반 시** | 매칭 로직 결함. `language.generation`만 선언한 Resource가 `copywriting` Task에 배정되면 선언되지 않은 능력을 기대하는 것이다 |
| **예외** | `exploration` 모드에서 낮은 confidence 후보로만 허용 (§9.1 ③) |

---

## 6. Lifecycle

Capability 노드의 수명은 [Taxonomy §6.1](e006a-capability-taxonomy.md)과 동일하다.

```
Proposed → Draft → Active ──▶ Deprecated ──▶ Retired
              │
              └──▶ Rejected
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Proposed** | 등록 제안됨 | Resource 등록 중 미지 능력 발견, 또는 사람이 제안 |
| **Draft** | 정의 작성 중. 측정 정의 미완 | 검토 시작 |
| **Active** | 정식 사용. 매칭 대상 | 측정 정의 완비 (INV-CP-03) |
| **Deprecated** | 신규 사용 중단. 기존 참조는 유효 | 대체 능력 도입 |
| **Retired** | 참조가 모두 사라짐. 이름은 영구 예약 | 마이그레이션 완료 |
| **Rejected** | 등록 거부 | 검증 실패 |

### 6.1 Deprecated의 실제 흐름

```
v1.0  language.generation.marketing_copy   Active
v2.0  language.generation.copywriting      Active     ← 더 일반적인 이름으로 정리
      language.generation.marketing_copy   Deprecated
                                           superseded_by: …copywriting
                                           aliases에 marketing_copy 추가
  ↓
과거 dec_045는 여전히 marketing_copy를 참조 → 조회 가능 (INV-CP-05)
새 Task는 copywriting을 요구
Resource Profile의 점수는 마이그레이션 스크립트로 이관
```

---

## 7. Relationships

```
Task 005 ──요구──▶ Capability 006 ◀──선언── Resource 007 / Tool 024
                        │  ▲                       │
    Taxonomy 006-A ─정의─┘  │                Resource Profile 025
                            │                (Capability × Context별 점수)
    Workflow 022 ──step──────┤
    Agent 023 ──scope────────┘
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Capability Taxonomy](e006a-capability-taxonomy.md) | 이름·계층·측정 정의의 권위 | `Taxonomy 1:N Capability` |
| [Task](e005-task.md) | Task는 Capability를 **요구**한다 | `Task N:M Capability` |
| [Resource](e007-resource.md) | Resource는 Capability를 **선언**한다 | `Resource N:M Capability` |
| [Tool](e024-tool.md) | Tool도 Capability를 제공한다 | `Tool N:M Capability` |
| [Resource Profile](e025-resource-profile.md) | (Capability × Context)별 점수의 키 | `Resource Profile N:M Capability` |
| [Workflow](e022-workflow.md) | 각 step이 Capability로 표현된다 | `Workflow N:M Capability` |
| [Agent](e023-agent.md) | 권한 범위를 Capability로 표현 | `Agent N:M Capability` |
| [Decision](e009-decision.md) | Matching 결과가 Decision의 후보 입력이다 | `Capability N:M Decision` |
| [Goal](e001-goal.md) | Goal은 Capability를 직접 참조하지 않는다 (Task를 거친다) | **직접 관계 없음** |
| Capability | 계층(parent) + 의미 관계(related) | `Capability N:M Capability` |

### 7.1 Capability DNA와의 관계

본 문서의 Capability는 **정의**이고, [Volume 4-B](../v4b-resource-intelligence.md)의 Capability DNA는 **측정 결과**다.

| | Entity 006 | Volume 4-B (Capability DNA) |
|---|---|---|
| 대상 | Capability의 정의와 의미 관계 | Resource가 가진 Capability의 측정 |
| 산출물 | canonical id, related 그래프 | Capability Vector, Confidence, Drift |
| 변경 주기 | 느리다 (표준) | 빠르다 (실행마다) |
| 저장 위치 | Taxonomy | [Resource Profile](e025-resource-profile.md) |

**v2.0에서 Capability DNA의 저장처가 확정되었다** — [Resource Profile](e025-resource-profile.md)의 `capability_scores`다. DNA의 키는 본 Taxonomy의 canonical id를 쓴다.

---

## 8. Canonical Representation

```json
{
  "capability_id": "language.generation.copywriting",
  "display_name": "광고 카피 작성",
  "parent": "language.generation",
  "description": "목적·타겟·채널이 주어지면 설득력 있는 짧은 문안을 작성한다. 각 문안이 왜 그 타겟에 유효한지 근거를 함께 제시한다.",
  "aliases": ["카피 작성", "광고 문구", "copywriting", "ad copy"],
  "related": [
    { "capability_id": "analysis.audience", "relation": "REQUIRES" },
    { "capability_id": "verification.brand_tone", "relation": "SUPPORTS" }
  ],
  "level_scale": { "type": "L1-L5", "score_range": "0-100" },
  "status": "Active"
}
```

기계가 읽을 수 있는 스키마: [`capability.schema.json`](../intent-os-spec/schemas/capability.schema.json)

측정 정의를 포함한 완전한 Taxonomy 노드는 [`capability-taxonomy.schema.json`](../intent-os-spec/schemas/capability-taxonomy.schema.json)이다.

> **v1.0 → v2.0 id 마이그레이션.** v1.0 §5의 트리와 [e006a §4.2](e006a-capability-taxonomy.md)의 트리가 어긋나 있었다. 후자가 권위다.
>
> | v1.0 | v2.0 |
> |---|---|
> | `research.search` | `research.web` |
> | `research.fact_verification` | `verification.fact_check` |
> | `analysis.data` | `analysis.metrics` |
> | `creative.*` | `creation.*` |
> | `interaction.consultation` | `communication.consultation` |
> | `language.summarization` | `language.transformation.summarize` |
> | `language.persuasion` | 폐기 — `analysis.audience` REQUIRES 관계로 대체 |
> | `creative.brand_strategy` | 폐기 — `verification.brand_tone` SUPPORTS 관계로 대체 |

---

## 9. Validation Rules

새 Capability 등록 요청(Planner의 Capability 추론 또는 Resource 등록 시 발생)은 다음을 거친다.

```
Capability 후보 (예: "블로그 글빨")
  ↓
Alias 탐색 ── 기존 id에 매핑 가능? ──▶ 기존 id 반환, Alias 추가 (patch 버전)
  ↓ (매핑 불가)
명명 규칙 검사 (Rule CP-001) ── e006a §9.1
  ├── 대문자·공백·깊이 초과 → 거부
  └── 벤더명·도구명 검출 (Rule CP-002) → 거부 + 대체 이름 제안
  ↓
단일 능력 검사 (Rule CP-004) ── 복합이면 분해 제안
  ↓
Resource 중립성 검사 (Rule CP-002)
  └── description에 "프롬프트", "모델", "API" 검출 → 경고
  ↓
측정 가능성 검사 (Rule CP-003) ── 불가하면 하위 분해 요구
  ↓
계층 위치 결정 (Rule CP-005) ── 부모 노드 지정, 트리 무결성 검사
  ↓
related 순환 검사 (INV-CP-04)
  ↓
canonical id 부여 → Proposed → Draft 등록
  ↓
측정 정의 완비 → Active 승격 (INV-CP-03)
```

**자동으로 Active가 되지 않는다.** 측정 정의 없이 Active를 허용하면 평가할 수 없는 Task가 생긴다.

### 9.1 Capability Matching

Decision Engine의 첫 단계는 Task의 `required_capabilities`와 Resource의 `declared_capabilities`를 매칭하는 것이다.

```
Task.required_capabilities
  ↓
① Alias 해소 → canonical id 정규화 (e006a §9.2 ①)
  ↓
② Exact Match — 같은 id를 선언한 Resource 수집
  ↓
③ Hierarchy Match — 하향 포함만 허용 (INV-CP-06)
   Resource가 copywriting 선언 → language.generation 요구 매칭  ✅
   Resource가 language.generation 선언 → copywriting 요구 매칭  ❌
   (exploration 모드에서만 낮은 confidence 후보로 포함)
  ↓
④ Level Filter — required level 미달 후보 제거
   Profile의 (Capability × Context) 점수를 조회 (e025 §9.3)
  ↓
⑤ Confidence Filter — confidence < threshold 후보는
   저위험 Task에서만 허용 (Cold Start Strategy)
  ↓
⑥ Graph Expansion — REQUIRES 관계 능력의 보유 여부를 확인
   REQUIRES 미보유 → 후보 제외
   SUPPORTS 보유   → 가산점
  ↓
⑦ 교집합 — 모든 required_capabilities를 만족하는 후보만 남긴다
   ├── 비어 있음 → Pipeline / Hybrid 조합 탐색 → 그래도 없으면 escalate
   └── 있음      → Decision Engine으로 전달
```

**Matching은 후보를 만드는 단계까지다.** 최종 선택(비용·지연·위험 반영)은 [Decision](e009-decision.md)의 소관이다.

---

## 10. Examples

### 예시 1 — 매칭 판정

```
Task 요구: language.generation.copywriting ≥ L3, analysis.audience ≥ L2

Resource                선언                            Profile 점수      판정
anthropic:claude-5      copywriting, audience           93 / 88          ✅ L5 / L4
openai:gpt-5            copywriting, audience           87 / 84          ✅ L4 / L4
human:copywriter_kim    copywriting, brand_tone         96 / —           ❌ audience 미선언
generic:writer-x        language.generation             72               ❌ 상위 선언 (INV-CP-06)
perplexity:sonar        research.web, analysis.competitor —              ❌ 무관
```

김 카피라이터가 빠진 이유는 **실력이 아니라 선언된 능력의 조합**이다. 이는 Hybrid 후보(`Claude + 김 검수`) 탐색으로 이어진다([e007 §10 예시 2](e007-resource.md)).

### 예시 2 — 하향 포함의 비대칭

```
① Task가 language.generation을 요구
   Resource가 language.generation.copywriting을 선언
   → 매칭 ✅  (하위는 상위를 만족)

② Task가 language.generation.copywriting을 요구
   Resource가 language.generation을 선언
   → 매칭 ❌  (상위 선언이 하위를 보장하지 않는다)
```

②를 허용했다면 "글을 쓸 줄 안다"고만 선언한 Resource가 광고 카피 Task에 배정된다. **결과 품질은 실행해봐야 알게 되고, 그 비용은 이미 발생한다.**

### 예시 3 — REQUIRES에 의한 후보 제외

```
Task 요구: language.generation.copywriting ≥ L3
  ↓ §9.1 ⑥ Graph Expansion
copywriting REQUIRES analysis.audience
  ↓
후보 검사
├── claude-5      copywriting ✅ + audience ✅  → 통과
└── writer-y      copywriting ✅ + audience ❌  → 제외
```

Task가 `analysis.audience`를 명시하지 않았어도 **REQUIRES 관계가 이를 강제한다.** 타겟을 이해하지 못하는 카피는 카피가 아니다.

### 예시 4 — 능력의 공백

```
Task: 윈터캠프 홍보 영상 제작
required: creation.video, language.generation.script
  ↓ 매칭
creation.video를 선언한 Active Resource: 0개
  ↓
후보 없음 → escalate
  ↓
보고: "이 Goal은 현재 등록된 Resource로 수행할 수 없다.
       creation.video 능력을 가진 Resource 등록이 필요하다."
```

**Taxonomy에 있지만 제공자가 없는 능력**이 시스템의 공백을 드러낸다. Resource 목록에서 Taxonomy를 만들었다면(INV-CP-01 위반) 이 공백은 보이지 않는다.

### 예시 5 — Level과 Confidence의 충돌

```
Task 요구: language.generation.copywriting ≥ L4 (80점 이상)

후보 A  Profile: 91점, confidence 0.97, 표본 1000회   → L5, 신뢰 가능
후보 B  Profile: 95점, confidence 0.20, 표본 3회      → L5, 신뢰 불가
```

**둘 다 L5지만 같지 않다.** §4.1의 원칙에 따라 B는 저위험 Task에서만 후보가 되고, 고영향 Task에서는 A가 선택된다. Level만 보면 이 차이가 사라진다.

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **Task가 Draft 상태 Capability를 요구** | Task 생성을 거부한다(INV-CP-03 연쇄). 측정할 수 없는 능력을 요구하면 [Evaluation](e015-evaluation.md)이 불가능하다 |
| **두 Capability가 사실상 같음** | 하나를 `Deprecated`로 하고 다른 하나의 alias로 흡수한다. 중복 능력은 [Profile](e025-resource-profile.md)의 표본을 쪼개 confidence를 떨어뜨린다 |
| **아무도 제공하지 않는 Capability** | 정상이다. 삭제하지 않는다(INV-CP-01). 예시 4처럼 시스템의 공백을 드러내는 것이 이 설계의 목적이다 |
| **인간만 제공 가능한 능력** | 정상이다. `verification.brand_tone`이 그렇다. Taxonomy는 제공자의 종류를 묻지 않는다 |
| **required level이 어떤 Resource보다도 높음** | 후보가 0개가 된다. `escalate`하고 "요구 수준을 낮추거나 Hybrid 조합이 필요하다"를 보고한다. **자동으로 요구 수준을 낮추지 않는다** |
| **REQUIRES가 5단계로 이어짐** | 매칭 비용이 커진다. 깊이 상한(기본 3)을 두고 초과분은 `SUPPORTS`로 강등을 제안한다 |
| **같은 이름이 다른 도메인에서 필요** | 전체 경로가 다르므로 문제없다. `analysis.metrics`와 `advertising.budget_control`은 다른 노드다. 단 **별칭이 겹치면** INV-CT-03 위반이다 |
| **Capability는 Active인데 측정 정의가 사후에 삭제됨** | `Draft`로 자동 강등하고 경보를 발행한다. 이미 그 능력을 요구하는 Task는 실행을 계속하되 새 Task 생성은 막힌다 |
| **합성 Capability의 구성 요소가 Deprecated** | 합성 능력도 재검토 대상으로 표시한다. 구성이 바뀌면 그것은 다른 능력이다([e006a §11](e006a-capability-taxonomy.md)) |
| **Resource가 선언한 능력을 실제로 못함** | Capability 정의의 문제가 아니라 [Profile](e025-resource-profile.md)의 문제다. Cold Start에서 `observed_score`가 `declared_score`를 크게 밑돌면 confidence가 낮아진다 |

---

## 12. Open Issues (v2.0)

### ✅ v1.0에서 해소된 항목

| v1.0 Open Issue | 해소 |
|---|---|
| Taxonomy 거버넌스 (누가 어떤 절차로 노드를 추가하는가) | [e006a §6.2](e006a-capability-taxonomy.md) 버전 규칙 + [§9.3](e006a-capability-taxonomy.md) 미지 능력 처리 절차 |
| Capability DNA 키의 canonical id 정규화 | DNA의 저장처를 [Resource Profile](e025-resource-profile.md)의 `capability_scores`로 확정. 키는 canonical id |
| 도메인 root 목록의 확정 | [e006a Rule CT-002](e006a-capability-taxonomy.md)에서 9개로 고정 |
| Hierarchy Match의 방향 | INV-CP-06으로 하향 포함·상향 미포함 확정 |

### Hierarchy Match 감점 계수

`exploration` 모드에서 상위 선언 Resource를 후보에 포함할 때 confidence에 얼마의 페널티를 줄 것인가. [e025 §12](e025-resource-profile.md)의 "Context 일반화 페널티"와 같은 성격의 미결 항목이다.

### Capability Embedding과의 이원화

[Volume 4-B Appendix ①](../v4b-resource-intelligence.md)은 장기적으로 Task와 Resource를 같은 벡터 공간에 매핑하는 방향을 제안한다. 이 경우 canonical id 체계는 사라지는 것이 아니라 **벡터 공간의 라벨/앵커** 역할로 재정의되어야 한다. 두 표현의 동기화 규칙이 필요하며, 임베딩 기반 매칭은 **비결정적**이어서 [Decision의 재현성](e009-decision.md)과 충돌한다([e006a §12](e006a-capability-taxonomy.md)).

### Alias 자동 학습

자연어 표현을 canonical id로 매핑하는 Alias를 사람이 등록하고 있다. 실패한 매칭 로그에서 후보를 자동 제안하는 것이 가능하지만, 잘못된 Alias는 조용히 잘못된 Resource를 부른다.

### 앞으로 보강해야 할 항목

- Hierarchy Match 감점 계수의 기준값
- Alias 자동 학습 규칙과 검증 절차
- `related` 관계의 매칭 가산점 계수
- 실제 예시 30~50개
