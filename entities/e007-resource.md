# Entity 007: Resource

- **Version:** v2.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Resource is any executing entity — AI, tool, human, or a combination — that provides Capabilities to perform Tasks.**

> Resource는 Task 수행에 필요한 Capability를 제공하는 모든 실행 주체이며, AI, 도구, 인간, 그리고 이들의 조합을 포함한다.

여기서 중요한 것은 **"모든(Any)"** 이다.

Intent OS는 실행 주체가 무엇인지 묻지 않는다. **어떤 능력을 제공하는지**만 묻는다. (Principle 03 — Resource Agnostic, [Volume 1](../v1-core-concepts.md))

### 1.1 정체성과 측정의 분리

**v2.0에서 Resource는 "무엇인가"만 담는다. "얼마나 잘하는가"는 [Resource Profile](e025-resource-profile.md)(Entity 025)로 분리되었다.**

```
Resource          Claude 5는 Anthropic이 만든 LLM이고 카피 작성 능력을 선언한다
                  ← 버전 업 때만 바뀐다
Resource Profile  한국 교육 마케팅 카피에서 observed 93, p95 지연 1,240ms, 표본 214
                  ← 매일 바뀐다
```

한 객체에 두면 **정체성을 조회할 때마다 측정값이 바뀌어 있다.** [Decision](e009-decision.md)의 `inputs_snapshot`은 "그 시점의 측정값"을 동결해야 하는데, 그 대상이 Profile이다([Rule D-004](e009-decision.md)).

---

## 2. Resource는 무엇이 아닌가?

### Resource는 "AI 모델"만이 아니다

❌ `Resource = LLM 목록` — 가장 흔한 오해다.

다음은 전부 **동등한 Resource**다.

```
Resource
├── AI Resource        (LLM, Image Model, Video Model)
├── Tool Resource      (Search Engine, Browser, Database, Analytics Tool, API)
├── Human Resource     (카피라이터, 검수자, 상담원, 도메인 전문가)
└── Hybrid Resource    (AI 초안 + 인간 검수 같은 조합)
```

`카피 작성` Task의 후보에는 Claude와 **인간 카피라이터가 나란히 올라간다.** 선택 기준은 이름이 아니라 Capability, 비용, 신뢰도다.

### Resource는 Capability가 아니다

❌ `언어 생성` — 이건 능력이지 주체가 아니다.

Resource는 Capability를 **제공(provide)** 하고, Capability는 Resource와 무관하게 정의된다([Capability Taxonomy](e006a-capability-taxonomy.md)).

**방향이 중요하다.** Resource가 Capability를 선언하지, Capability가 Resource를 나열하지 않는다([INV-09](e000a-entity-relationships.md)).

### Resource는 Resource Profile이 아니다

❌ `Claude는 카피 작성 93점` — 이건 [Resource Profile](e025-resource-profile.md)이다.

| | Resource | Resource Profile |
|---|---|---|
| 내용 | 무엇인가 (id, type, provider, 선언 능력) | 얼마나 잘하는가 (관측 점수, 실측 비용·지연) |
| 변경 빈도 | 버전 업 시 | 실행마다 |
| 출처 | 등록 (선언) | 관측 |
| Decision의 참조 | 후보 식별 | `inputs_snapshot`의 동결 대상 |

`Resource 1:1 Resource Profile`이며, **Profile 없는 Resource는 Active가 될 수 없다**([INV-15](e000a-entity-relationships.md)).

### Resource는 Agent가 아니다

❌ `마케팅 담당 에이전트` — 이건 [Agent](e023-agent.md)(Entity 023)다.

**Agent는 Resource를 사용하는 쪽이다.** Agent는 스스로 결정하고, Resource는 시키는 대로 한다.

```
Agent   "경쟁 학원 가격을 알아내라"를 받고 → 검색 Resource를 3번 호출하고 판단한다
Resource "홍대 학원 가격"을 받고 → 검색 결과를 반환한다. 끝
```

다만 §4.1의 Resource Type 목록에는 `agent`가 있다. **모순이 아니다** — 판별 기준은 "Intent OS가 그 결정 루프를 소유하는가"다. 소유하지 않는 외부 에이전트 제품은 블랙박스이므로 Resource로 등록한다([e023 §2](e023-agent.md)).

### Resource는 Task의 소유자가 아니다

❌ `이 Task는 원래 Claude 담당` — Intent OS에 고정 담당은 없다.

Task와 Resource의 연결은 매 실행마다 Decision Engine이 새로 결정한다. 어제 Claude가 하던 일을 오늘 다른 Resource가 할 수 있다([Volume 4-B §12](../v4b-resource-intelligence.md)).

### Resource는 Solution이 아니다

❌ `유튜브 광고` — 이건 Method/Solution이다. `유튜브 광고 플랫폼 API`가 Resource다.

---

## 3. Design Principles

### Rule R-001 — 최소 하나의 Capability를 선언해야 한다

Capability가 없는 Resource는 매칭 대상이 될 수 없으므로 Registry에 등록할 수 없다.

선언하는 Capability는 [Capability Taxonomy](e006a-capability-taxonomy.md)의 표준 id여야 하며, 비표준 이름은 Alias Map으로 흡수한다([Rule CT-006](e006a-capability-taxonomy.md)).

### Rule R-002 — 선언은 신뢰의 시작점일 뿐이다

```
Declared Capability + Observed Performance = Final Capability Score
```

Resource가 스스로 선언한 점수(`declared_score`)는 관찰된 점수(`observed_score`)로 계속 보정된다. **표본이 적을 때만 declared에 의존하고, 표본이 쌓이면 observed가 지배한다**([Rule RPF-003](e025-resource-profile.md)).

### Rule R-003 — Universal Resource Interface를 따라야 한다

종류가 무엇이든 동일한 인터페이스로 호출 가능해야 한다.

```
identify / capabilities / execute / estimate_cost / estimate_latency / evaluate_result
```

인간 전문가도 예외가 아니다 — 요청 전달과 결과 회수의 어댑터가 있으면 동일한 Resource다([Volume 6 §3](../v6-developer-platform.md)).

### Rule R-004 — 비용과 지연을 추정 가능해야 한다

`estimate_cost`, `estimate_latency`가 불가능한 Resource는 Utility를 계산할 수 없다.

정액 계약이라 건별 비용을 알 수 없는 경우에도 **안분값을 제시해야 한다.** `null`은 비용 0으로 오인되어 Utility를 왜곡한다([Rule OUT-004](e014-outcome.md)).

### Rule R-005 — 성능은 선언이 아니라 관찰로 유지된다

등록 시점의 값을 고정으로 취급하면 안 된다. 성능은 버전 업데이트로 오르기도, **떨어지기도** 한다.

관찰과 갱신의 실체는 [Resource Profile](e025-resource-profile.md)이 담당한다(§6.2).

### Rule R-006 — 이력은 삭제하지 않는다

`Removed` 상태여도 성능 이력을 지우지 않는다. 후속 버전·유사 Genome 추론([Volume 4-C §12](../v4c-resource-genome.md))의 근거 데이터이기 때문이다.

---

## 4. Attributes

**v2.0에서 Resource는 선언 정보만 갖는다.** 관측 정보는 [Resource Profile](e025-resource-profile.md)에 있다.

```
Resource
├── Identity
│   ├── id
│   ├── name
│   ├── provider
│   └── version
├── Type
│   └── type
├── Declaration
│   ├── declared_capabilities[]
│   ├── published_cost_model
│   ├── declared_availability
│   └── limitations[]
├── Interface
│   ├── adapter_ref
│   └── data_residency
└── Registry
    ├── profile_id
    ├── genome_ref
    └── lifecycle
```

| 속성 | 의미 | 예 |
|---|---|---|
| **id** | Registry 내 고유 식별 | `anthropic:claude-5`, `human:copywriter_kim` |
| **name** | 표시 이름 | `Claude 5` |
| **provider** | 제공자 | `Anthropic` |
| **version** | 버전 | `5.0` |
| **type** | Resource 분류 (§4.1) | `llm` |
| **declared_capabilities** | 선언한 능력 + 선언 점수 | `copywriting declared 90` |
| **published_cost_model** | 공표된 비용 구조 | 토큰당 과금 / 건당 5만원 |
| **declared_availability** | 선언된 가용 시간 | `24/7` / `평일 10-19시` |
| **limitations** | 알려진 제약 | `실시간 검색 불가` |
| **adapter_ref** | Universal Interface 어댑터 | `adapter_anthropic_v3` |
| **data_residency** | 데이터 처리 지역 | `kr` |
| **profile_id** | 측정 기록 (INV-15) | `rp_claude5` |
| **genome_ref** | 행동 특성 표현 | `genome_claude5` |
| **lifecycle** | Registry 내 상태 (§6) | Active |

> **v1.0 → v2.0 필드 이동:** `capabilities[].observed_score`, `performance`(reliability·latency·success_rate·drift), `availability`(실측)는 [Resource Profile](e025-resource-profile.md)로 이동했다. Resource에는 **선언값만** 남는다. 중복 보관하면 어느 쪽이 진실인지 알 수 없게 된다.

### 4.1 Resource Types

[resource.schema.json](../intent-os-spec/schemas/resource.schema.json)의 `type` enum과 일치한다.

| Type | 예 | 비고 |
|---|---|---|
| `llm` | Claude, GPT, Gemini | 확률적. 품질 점수 관리가 핵심 |
| `image_model` | 이미지 생성 모델 | |
| `video_model` | 영상 생성 모델 | |
| `search_engine` | 검색 엔진, Perplexity류 | |
| `api` | 광고 플랫폼 API, 결제 API | [Tool](e024-tool.md) 명세가 상세를 다룬다 |
| `database` | 학원 CRM DB, 상담 이력 DB | |
| `tool` | 브라우저, Analytics Tool, 자동화 도구 | 결정론적. 스키마 계약이 핵심 |
| `agent` | **외부** 에이전트 제품 (블랙박스) | 내부 결정 루프를 소유하면 [Agent](e023-agent.md) Entity다 |
| `human` | 카피라이터, 검수자, 상담원 | |
| `hybrid` | AI 초안 + 인간 검수 조합 | |

**`tool`과 `api` 타입은 [Entity 024: Tool](e024-tool.md)이 상세히 다룬다.** Tool은 Resource의 부분집합이며 Universal Resource Interface를 그대로 따르되, 관리 축이 다르다 — 일반 Resource는 품질 점수를, Tool은 **부수효과·권한·멱등성**을 관리한다.

**Hybrid에 대한 주의:** 자주 쓰이는 조합(`Research → Perplexity, Writing → Claude, 검수 → 인간`)은 그 **조합 자체를 하나의 Resource로 등록**하고 성능을 학습할 수 있다([Volume 4-B §17](../v4b-resource-intelligence.md), [Rule CT-009](e006a-capability-taxonomy.md)의 합성 Capability와 대응).

---

## 5. Invariants

### INV-R-01 — Active Resource는 Resource Profile을 가진다

[INV-15](e000a-entity-relationships.md)의 Resource 측 표현이다.

| | |
|---|---|
| **위반 시** | Resource를 `Evaluating`으로 강등하고 후보군에서 제외 |
| **근거** | Profile이 없으면 cost/latency 추정이 불가능해 Utility를 계산할 수 없다 |

### INV-R-02 — Resource는 최소 하나의 Capability를 선언한다

| | |
|---|---|
| **위반 시** | 등록 거부. 매칭 대상이 될 수 없는 Resource는 Registry에 존재할 이유가 없다 |

### INV-R-03 — Resource id는 전역 고유하며 재사용되지 않는다

| | |
|---|---|
| **위반 시** | 등록 거부. `provider:name` 네임스페이스로 충돌을 방지한다 |
| **근거** | 과거 [Decision](e009-decision.md)의 `selection`이 그 id를 가리키고 있다 |

### INV-R-04 — Resource는 Task나 Goal을 참조하지 않는다

Resource는 자기가 무엇에 쓰이는지 모른다.

| | |
|---|---|
| **위반 시** | 필드 추가를 거부. Resource가 Task를 알면 고정 담당이 생긴다 |
| **근거** | [Rule REL-001](e000a-entity-relationships.md) — 하위가 상위를 참조한다. Resource는 가장 하위다 |

### INV-R-05 — Removed Resource의 이력은 삭제되지 않는다

| | |
|---|---|
| **위반 시** | 삭제 차단 ([INV-RPF-06](e025-resource-profile.md)). Profile과 Execution 이력은 보존된다 |

### INV-R-06 — 선언 능력이 Taxonomy에 없으면 Active가 될 수 없다

| | |
|---|---|
| **위반 시** | `Registered`에 머문다. Alias 해소 또는 Capability 등록 절차를 거쳐야 한다 ([e006a §9.3](e006a-capability-taxonomy.md)) |
| **근거** | 자동 등록을 허용하면 `copywriting` / `copy-writing` / `copy_writing`이 각각 노드가 되어 Taxonomy가 무너진다 |

### INV-R-07 — Deprecated Resource는 신규 배정을 받지 않는다

| | |
|---|---|
| **위반 시** | 후보 생성 단계에서 제외. 진행 중인 Execution은 완료시킨다 |

---

## 6. Lifecycle

```
Registered → Evaluating → Active → Optimized
                  ▲          │         │
                  │          ▼         ▼
                  └──── Degraded    Deprecated → Removed
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Registered** | Registry 등록 완료. 선언 정보만 존재 | 등록 |
| **Evaluating** | Cold Start — 저위험 Task로 검증 중 | 등록 검증 통과 |
| **Active** | 정식 후보군 편입. 실사용 데이터 축적 중 | Profile `Calibrating` 진입 (INV-R-01) |
| **Optimized** | 충분한 이력으로 Context별 강점이 파악됨 | Profile `Established` |
| **Degraded** | Drift 확정으로 성능 하락 | Profile `Degraded` ([e025 §9.2](e025-resource-profile.md)) |
| **Deprecated** | 신규 할당 중단 (구버전, 제공 중단 예고) | 운영자 결정 또는 제공자 공지 |
| **Removed** | Registry에서 제거. **이력 데이터는 보존** | 최종 제거 |

**Resource의 lifecycle은 Profile의 status를 따라간다.** Profile이 `Degraded`로 확정되면 Resource도 `Degraded`가 된다. 판단의 근거는 항상 관측이다.

### 6.1 등록과 발견

Resource는 Resource Registry([Volume 6 §4](../v6-developer-platform.md))에 등록된다.

```
외부 Resource (AI / Tool / Human / API)
  ↓
Resource Adapter (Universal Resource Interface로 변환)
  ↓
Capability Declaration (무엇을 잘하는지 선언)
  ↓
Taxonomy 정규화 (Alias 해소 / 미등록 능력 처리)
  ↓
Registry 등록 → Registered
  ↓
Resource Profile 생성 (Initialized)
  ↓
Cold Start 평가 → Evaluating → Active
```

발견(Discovery)의 방향은 두 가지다.

1. **개발자가 등록한다** — Resource SDK / Plugin System ([Volume 6](../v6-developer-platform.md))
2. **시스템이 발견한다** — Autonomous Benchmarking Engine이 새 모델을 스스로 찾아 등록한다 ([Volume 4-D](../v4d-autonomous-benchmarking.md))

### 6.2 성능은 관찰로 유지된다

측정·감쇠·Drift 감지의 상세는 [Resource Profile](e025-resource-profile.md)이 다룬다. Resource 수준에서 지켜야 할 원칙은 두 가지다([Volume 4-B](../v4b-resource-intelligence.md)).

#### ① Benchmark < Production Data

공식 벤치마크 95점보다 **"한국 교육 마케팅에서 실제 92% 성공"** 을 더 신뢰한다. 벤치마크는 Profile의 `declared` 영역에 참고값으로만 들어간다.

#### ② 절대 순위는 없다

```
❌  Claude 93 > GPT 89 > Gemini 85

✅  language.generation.copywriting
    ├── {교육, ko, 학부모}  → Claude 93 / GPT 87
    └── {커머스, en, B2B}   → Claude 88 / GPT 92
```

모든 점수는 Context에 종속된다([Rule RPF-002](e025-resource-profile.md)). 하나의 순위표를 만들려는 시도는 이 원칙을 깨뜨린다.

---

## 7. Relationships

```
Capability 006 ◀──선언── Resource 007 ──1:1──▶ Resource Profile 025
      ▲                      │  ▲                      ▲
      │                      │  └── Tool 024 (부분집합)  │
   Task 005 ──요구──▶ Decision 009 ──▶ Execution 013 ──관측──┘
                                          ▲
                                     Agent 023 (사용)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Capability](e006-capability.md) | Resource가 Capability를 **선언**한다 | `Resource N:M Capability` |
| [Resource Profile](e025-resource-profile.md) | 정확히 하나의 Profile | `Resource 1:1 Resource Profile` |
| [Tool](e024-tool.md) | Tool은 Resource의 부분집합 | `Resource 1:0..1 Tool` |
| [Decision](e009-decision.md) | 선택지. Decision의 출력이 Task-Resource 할당이다 | `Resource N:M Decision` |
| [Execution](e013-execution.md) | 실행 주체. 성능 이력의 귀속 대상 | `Resource 1:0..N Execution` |
| [Agent](e023-agent.md) | Agent가 Resource를 **사용한다** | `Agent N:M Resource` |
| [Task](e005-task.md) | Resource는 Task에 **할당**된다. 소유하지 않는다 | **직접 관계 없음** (INV-R-04) |
| [Goal](e001-goal.md) | Resource는 Goal을 모른다. Goal 정보는 Context로만 전달된다 | **직접 관계 없음** |
| [Policy](e019-policy.md) | 허용 Resource·리전을 규정 | `Policy 1:N Resource` |
| [Feedback](e012-feedback.md) | Profile 갱신의 입력 (Evaluation 경유) | `Resource 1:0..N Feedback` |

### 7.1 Resource 선택은 누구의 소관인가

**본 문서는 Resource가 "무엇인지"만 정의한다. "어떤 Resource를 고르는지"는 정의하지 않는다.**

| 질문 | 담당 |
|---|---|
| Resource란 무엇인가 | 본 문서 (Entity 007) |
| Resource를 어떻게 측정하는가 | [Entity 025 — Resource Profile](e025-resource-profile.md) |
| Resource의 행동 특성을 어떻게 표현하는가 | [Volume 4-C — Resource Genome](../v4c-resource-genome.md) |
| 어떤 Resource를 선택하는가 | [Entity 009 — Decision](e009-decision.md), [Volume 4](../v4-decision-engine.md) |
| 무엇을 하지 못하게 하는가 | [Entity 019 — Policy](e019-policy.md) |

Entity 정의에 선택 로직을 섞으면 Resource가 특정 선택 전략에 종속된다. 계층을 분리한다.

---

## 8. Canonical Representation

```json
{
  "id": "anthropic:claude-5",
  "name": "Claude 5",
  "type": "llm",
  "provider": "Anthropic",
  "version": "5.0",
  "declared_capabilities": [
    { "capability_id": "language.generation.copywriting", "declared_score": 90 },
    { "capability_id": "language.transformation.summarize", "declared_score": 94 },
    { "capability_id": "reasoning.planning", "declared_score": 89 }
  ],
  "published_cost_model": {
    "unit": "token",
    "rates": { "input_per_1k": 0.003, "output_per_1k": 0.015, "currency": "USD" }
  },
  "declared_availability": "24/7",
  "limitations": ["실시간 검색 불가", "이미지 내 한국어 텍스트 인식 취약"],
  "adapter_ref": "adapter_anthropic_v3",
  "data_residency": "kr",
  "profile_id": "rp_claude5",
  "genome_ref": "genome_claude5",
  "lifecycle": "Active"
}
```

인간 Resource도 **같은 구조**를 가진다.

```json
{
  "id": "human:copywriter_kim",
  "name": "김 카피라이터",
  "type": "human",
  "provider": "external_contract",
  "declared_capabilities": [
    { "capability_id": "language.generation.copywriting" },
    { "capability_id": "verification.brand_tone" }
  ],
  "published_cost_model": {
    "unit": "task",
    "rates": { "per_task": 50000, "currency": "KRW" }
  },
  "declared_availability": "평일 10:00-19:00",
  "limitations": ["주말 불가", "동시 처리 1건"],
  "adapter_ref": "adapter_human_email",
  "data_residency": "kr",
  "profile_id": "rp_copywriter_kim",
  "lifecycle": "Active"
}
```

`declared_score`가 없는 것에 주목한다. **인간은 자기 점수를 선언하지 않는다.** 전부 관측으로 얻어지며 [Profile](e025-resource-profile.md)에 있다.

기계가 읽을 수 있는 스키마: [`resource.schema.json`](../intent-os-spec/schemas/resource.schema.json)

---

## 9. Validation Rules

```
등록 요청
  ↓
Identity 중복 검사 (INV-R-03) ── 중복 시 버전 등록으로 전환
  ↓
Capability 선언 확인 (Rule R-001, INV-R-02) ── 없으면 반려
  ↓
Capability id 정규화 (INV-R-06) ── e006a §9.3
  ├── Alias Map 조회 → 표준 id 치환
  ├── 미등록 → 유사 후보 3개 제시 → 사람 판정
  └── Draft 상태 Capability 선언 → Registered에 머문다
  ↓
Interface 적합성 검사 (Rule R-003)
  └── identify / capabilities / execute / estimate_cost / estimate_latency 응답 확인
  ↓
Cost/Latency 추정 검증 (Rule R-004)
  └── 추정 불가 → 안분 규칙 제시 요구. null 허용하지 않음
  ↓
data_residency 확인 → Policy(리전 제한)와 정합 검사
  ↓
Registry 등록 → Registered
  ↓
Resource Profile 생성 (Initialized, INV-R-01)
  ↓
Cold Start 평가 계획 생성 → Evaluating
```

### 9.1 Cold Start 원칙

신규 Resource를 검증할 때 지켜야 할 것.

| 원칙 | 이유 |
|---|---|
| **저위험 Task만 배정한다** | 검증하려고 300만원 광고를 집행할 수는 없다 |
| **비가역 Task를 배정하지 않는다** | `irreversible: true` Task는 `Evaluating` Resource에 배정 금지 |
| **Shadow Execution을 우선한다** | 실제 반영 없이 병행 실행해 점수를 수집한다([e013 §4.1](e013-execution.md)) |
| **표본이 min_sample에 도달할 때까지 Active로 올리지 않는다** | Capability별 `min_sample`은 Taxonomy가 정한다([e006a §4.1](e006a-capability-taxonomy.md)) |

---

## 10. Examples

### 예시 1 — 같은 Task, 세 종류의 Resource

```
task_004  인스타그램 광고 카피 3종 작성
required: language.generation.copywriting + analysis.audience

후보                    type      비용        지연        Profile 점수
anthropic:claude-5      llm       0.42 USD    1,820ms     93 (conf 0.95)
openai:gpt-5            llm       0.38 USD    1,340ms     87 (conf 0.91)
human:copywriter_kim    human     50,000 KRW  4시간       96 (conf 0.88)
```

`human:copywriter_kim`이 **점수가 가장 높지만 선택되지 않았다.** 비용이 120배, 지연이 8,000배다. 그러나 브랜드 톤이 중요한 검수 Task에서는 같은 Resource가 선택된다 — **가중치가 다르기 때문이다**([e009 §4.2](e009-decision.md)).

### 예시 2 — Hybrid Resource

```json
{
  "id": "hybrid:ai_draft_human_review",
  "name": "AI 초안 + 인간 검수",
  "type": "hybrid",
  "provider": "internal",
  "declared_capabilities": [
    { "capability_id": "language.generation.copywriting", "declared_score": 96 },
    { "capability_id": "verification.brand_tone", "declared_score": 97 }
  ],
  "published_cost_model": {
    "unit": "task",
    "rates": { "per_task": 50500, "currency": "KRW" }
  },
  "declared_availability": "평일 10:00-19:00",
  "limitations": ["김 카피라이터 가용성에 종속"],
  "adapter_ref": "adapter_pipeline_v1",
  "profile_id": "rp_hybrid_ai_human",
  "lifecycle": "Active"
}
```

이 Hybrid는 [Pipeline Execution](e013-execution.md)으로 수행되며 자식 Execution 2개를 낳는다. **조합 자체가 하나의 Resource로 학습된다** — "Claude 단독"과 "Claude + 김 검수"의 점수가 따로 관리된다.

### 예시 3 — Drift로 인한 강등

```
2026-09-10  Claude 5.1 자동 배포
  ↓ Profile 관측 (e025 §9.2)
윈도우 1  observed 86 (기준 93)  → Profile: Drifting,  Resource: Active 유지
윈도우 2  observed 85            → Profile: Drifting,  Resource: Active 유지
윈도우 3  observed 85            → Profile: Degraded 확정
  ↓
Resource lifecycle: Active → Degraded
  ↓
Event: resource.drift_detected
  ├── asm_031 ("Claude 한국어 카피 성능 유지") → Invalidated
  ├── 진행 중 Task의 Resource 재선택
  └── 후보 순위 하락
```

**3회 확인 전에는 Resource를 강등하지 않는다.** 한 번의 장애로 6개월치 학습이 무너지면 안 된다([INV-RPF-07](e025-resource-profile.md)).

### 예시 4 — Policy에 의한 배제

```
task_007  학부모 상담 이력 분석
required: analysis.customer_data

후보 생성
├── overseas:model-x   data_residency: us-east   ← pol_015 (국내 리전만) → 배제
├── anthropic:claude-5 data_residency: kr        ← 통과
└── domestic:model-y   data_residency: kr        ← 통과
```

`data_residency`가 Resource의 속성인 이유가 여기 있다. **Policy가 판정할 수 있는 값이어야 한다**([Rule POL-002](e019-policy.md)).

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **같은 모델의 새 버전 출시** | 새 Resource로 등록하지 않는다. 같은 id를 유지하고 `version`만 올린다. 성능 변화는 [Drift](e025-resource-profile.md)로 처리한다. 단 제공자가 명시적 major 버전을 발표하면 Profile을 `Calibrating`으로 리셋한다 |
| **제공자가 조용히 모델을 바꿈** | 감지 수단은 Drift뿐이다. 이것이 §6.2 ①(Benchmark < Production Data)의 실질적 이유다 |
| **인간 Resource가 퇴사** | `Deprecated` → `Removed`. **Profile과 Execution 이력은 보존한다**(INV-R-05). 단 개인정보 삭제 요구가 있으면 익명화한다 |
| **Resource가 선언한 능력을 실제로 못함** | Cold Start에서 걸러진다. `observed_score`가 `declared_score`를 크게 밑돌면 Profile의 confidence가 낮아지고 후보 순위가 떨어진다. **선언을 신뢰하지 않는 것이 Rule R-002의 목적이다** |
| **100개 능력을 선언한 Resource** | 허용하되 declared 신뢰도를 낮게 시작한다. "전부 잘한다"는 선언은 대개 사실이 아니다 |
| **비용이 0인 사내 도구** | `per_task: 0`을 그대로 둔다. Utility에서 비용 항이 0이 되어 다른 축이 선택을 결정한다. 정상 동작이다 |
| **Resource는 Active인데 Profile이 Stale** | Resource는 Active를 유지하되 Profile의 confidence가 감쇠하므로 후보 순위가 자연히 떨어진다. 강제 강등하지 않는다 — **모르는 것과 나쁜 것은 다르다** |
| **Registry에 같은 능력의 Resource가 20개** | 정상이다. 문제는 후보 생성 비용이다. Profile의 confidence 상위 N개만 Utility를 계산하는 가지치기가 필요하다(§12) |
| **외부 Agent 제품을 등록** | `type: agent`로 Resource 등록한다. 내부 결정이 기록되지 않는다는 사실을 Decision의 `rationale`에 명시한다 — **감사 불가 구간이 생긴다**([e023 §10 예시 4](e023-agent.md)) |

---

## 12. Open Issues (v2.0)

### ✅ v1.0에서 해소된 항목

| v1.0 Open Issue | 해소 |
|---|---|
| Resource Profile은 살아있는 데이터다 (Rule R-005)의 구현 | [Entity 025](e025-resource-profile.md) 신설. 스냅샷·감쇠·Drift 3-윈도우 규칙 정의 |
| Health Monitoring 필드의 스키마 반영 | Profile의 `performance`·`availability`·`drift` 블록 |
| Genome 참조 필드 | `genome_ref` 추가 |
| Cost Model의 표준 스키마 | `published_cost_model`(선언) / Profile의 `observed_avg_cost`(관측) 분리 |

### Human Resource의 특수성

인간을 동일 인터페이스로 다루는 원칙은 유지하되, 실무적으로 다른 축이 존재한다.

- **동의와 근로 조건** — 할당 자체에 수락/거절 절차가 필요하다. 현재 Universal Interface에는 `accept/decline`이 없다
- **가용성의 비결정성** — `declared_availability`가 API처럼 안정적이지 않다
- **평가의 민감성** — `observed_score`가 인사 평가로 전용될 위험이 실재한다. [Profile의 `visibility: internal_restricted`](e025-resource-profile.md)만으로 충분한지 미결

### Composite/Hybrid Resource의 내부 표현

조합 Resource를 단일 Resource로 등록할 때, 내부 파이프라인(어떤 Resource가 어떤 순서로)의 스키마 표현이 미정이다. [Workflow](e022-workflow.md)로 표현하는 것이 자연스러워 보이지만, 그러면 Resource가 Workflow를 참조하게 되어 계층이 역전된다.

### 후보 생성의 가지치기

같은 Capability를 제공하는 Resource가 수십 개일 때 전부 Utility를 계산하면 Decision 지연이 실행 지연이 된다. Profile confidence 기반 사전 필터링 규칙이 필요하다.

### Registry 간 식별자 충돌

`provider:name` 네임스페이스를 쓰지만 표준화되지 않았다. 여러 Registry를 연합할 때의 충돌 규칙이 없다.

### 앞으로 보강해야 할 항목

- 인간 Resource의 수락/거절 프로토콜
- Composite Resource의 내부 구성 스키마
- 후보 가지치기 알고리즘
- 실제 예시 30~50개
