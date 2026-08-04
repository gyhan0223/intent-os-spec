# Entity 007: Resource

- **Version:** v2.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04
- **Schema:** [`resource.schema.json`](../intent-os-spec/schemas/resource.schema.json)

---

## 1. Definition

### 공식 정의

> **Resource is any executing entity — AI, tool, human, or a combination — that provides Capabilities to perform Tasks.**

> Resource는 Task 수행에 필요한 Capability를 제공하는 모든 실행 주체이며, AI, 도구, 인간, 그리고 이들의 조합을 포함한다.

여기서 중요한 것은 **"모든(Any)"** 이다.

Intent OS는 실행 주체가 무엇인지 묻지 않는다. **어떤 능력을 제공하는지**만 묻는다. (Principle 03 — Resource Agnostic, [Volume 1](../v1-core-concepts.md))

---

## 2. Resource는 무엇이 아닌가?

### Resource는 "AI 모델"만이 아니다

❌ `Resource = LLM 목록` — 가장 흔한 오해다.

다음은 전부 **동등한 Resource**다.

```
Resource
├── AI Resource        (LLM, Image Model, Video Model, Agent)
├── Tool Resource      (Search Engine, Browser, Database, Analytics Tool, API)
├── Human Resource     (카피라이터, 검수자, 상담원, 도메인 전문가)
└── Hybrid Resource    (AI 초안 + 인간 검수 같은 조합)
```

`카피 작성` Task의 후보에는 Claude와 **인간 카피라이터가 나란히 올라간다.** 선택 기준은 이름이 아니라 Capability, 비용, 신뢰도다.

### Resource는 Capability가 아니다

❌ `언어 생성` — 이건 능력이지 주체가 아니다.

Resource는 Capability를 **제공(provide)** 하고, Capability는 Resource와 무관하게 정의된다. ([e006-capability.md](e006-capability.md))

### Resource는 Task의 소유자가 아니다

❌ `이 Task는 원래 Claude 담당` — Intent OS에 고정 담당은 없다.

Task와 Resource의 연결은 매 실행마다 Decision Engine이 새로 결정한다. 어제 Claude가 하던 일을 오늘 다른 Resource가 할 수 있다. ([Volume 4-B §12 Resource Evolution](../v4b-resource-intelligence.md))

### Resource는 Solution이 아니다

❌ `유튜브 광고` — 이건 Method/Solution이다. `유튜브 광고 플랫폼 API`가 Resource다.

---

## 3. Design Principles

### Rule R-001 — 최소 하나의 Capability를 선언해야 한다

Capability가 없는 Resource는 매칭 대상이 될 수 없으므로 Registry에 등록할 수 없다.

### Rule R-002 — 선언은 신뢰의 시작점일 뿐이다

```
Declared Capability + Observed Performance = Final Capability Score
```

Resource가 스스로 선언한 점수(`declared_score`)는 관찰된 점수(`observed_score`)로 계속 보정된다. ([Volume 6 §5 Capability Declaration System](../v6-developer-platform.md))

### Rule R-003 — Universal Resource Interface를 따라야 한다

종류가 무엇이든 동일한 인터페이스로 호출 가능해야 한다.

```
identify / capabilities / execute / estimate_cost / estimate_latency / evaluate_result
```

인간 전문가도 예외가 아니다 — 요청 전달과 결과 회수의 어댑터가 있으면 동일한 Resource다. ([Volume 6 §3 Resource Adapter Framework](../v6-developer-platform.md))

### Rule R-004 — 비용과 지연을 추정 가능해야 한다

`estimate_cost`, `estimate_latency`가 불가능한 Resource는 Decision Score를 계산할 수 없다.

### Rule R-005 — Resource Profile은 살아있는 데이터다

등록 시점의 Profile을 고정값으로 취급하면 안 된다. 성능은 버전 업데이트로 오르기도, **떨어지기도** 한다. (§8 Drift)

---

## 4. Attributes

```
Resource
├── Identity (id, name, provider, version)
├── Type
├── Capabilities (+ score, confidence)
├── Cost Model
├── Latency
├── Reliability
├── Availability
├── Limitations
├── Performance History
└── Lifecycle State
```

| 속성 | 의미 | 예 |
|---|---|---|
| **Identity** | Registry 내 고유 식별 | `anthropic:claude-5`, `human:copywriter_kim` |
| **Type** | Resource 분류 | `llm` / `tool` / `human` / `hybrid` … |
| **Capabilities** | 제공 능력 + 수준 + 신뢰도 | `copywriting 91 (conf 0.95)` |
| **Cost Model** | 비용 구조 | 토큰당 과금 / 건당 5만원 / 월 정액 |
| **Latency** | 응답 지연 | `800ms` / 인간 검수자 `4시간` |
| **Reliability** | 결과의 일관성·성공률 | `0.95` |
| **Availability** | 사용 가능 여부·시간대 | `24/7` / `평일 10-19시` |
| **Limitations** | 제약 | `한국어 이미지 텍스트 취약`, `주말 불가` |
| **Performance History** | 실행 이력 통계 | 최근 30일 성공률 92% |
| **Lifecycle State** | Registry 내 상태 | Active |

cost / latency / reliability / availability 네 축은 Decision Score Model([Volume 3](../v3-runtime.md) Stage 4)의 직접 입력이다. 축들은 서로 독립적이다 — 인간 카피라이터는 지연이 4시간이지만 특정 Capability에서는 최고 수준일 수 있다.

### 4.1 Resource Types

[resource.schema.json](../intent-os-spec/schemas/resource.schema.json)의 `type` enum과 일치한다.

| Type | 예 |
|---|---|
| `llm` | Claude, GPT, Gemini |
| `image_model` | 이미지 생성 모델 |
| `video_model` | 영상 생성 모델 |
| `search_engine` | 검색 엔진, Perplexity류 |
| `api` | 광고 플랫폼 API, 결제 API |
| `database` | 학원 CRM DB, 상담 이력 DB |
| `tool` | 브라우저, Analytics Tool, 자동화 도구 |
| `agent` | 복수 단계를 스스로 수행하는 에이전트 |
| `human` | 카피라이터, 검수자, 상담원 |
| `hybrid` | AI 초안 + 인간 검수 조합, Composite Resource |

**Hybrid에 대한 주의:** [Volume 4-B §17](../v4b-resource-intelligence.md)의 Composite Capability처럼, 자주 쓰이는 조합(`Research → Perplexity, Writing → Claude, 검수 → 인간`)은 그 **조합 자체를 하나의 Resource로 등록**하고 성능을 학습할 수 있다.

---

## 5. Invariants

### INV-R-01 — Active Resource는 최소 하나의 Capability를 갖는다

Rule R-001이 등록 시점의 검사라면 이쪽은 항상 성립해야 하는 상태다. Capability가 0개인 Resource는 어떤 Task에도 매칭되지 않으면서 후보 목록만 늘린다.

| | |
|---|---|
| **위반 시** | `Deprecated`로 내리고 후보 생성에서 제외한다. Capability가 전부 폐기된 경우가 대부분이므로 폐기 사유를 함께 기록한다 |
| **탐지** | 등록 시점, Capability 폐기 시점 |

### INV-R-02 — 선언 점수와 관측 점수는 섞이지 않는다

`declared_score`와 `observed_score`가 같은 필드에 합쳐지면 "누가 주장한 값"과 "실제로 확인된 값"을 구분할 수 없다. Rule R-002가 무너지는 지점이다.

| | |
|---|---|
| **위반 시** | 값을 분리 복원한다. 복원할 수 없으면 둘 다 선언값으로 간주하고 신뢰도를 낮춘다. **의심스러우면 관측이 아니라 선언으로 본다** |

### INV-R-03 — 관측 점수는 근거가 되는 Execution 없이 존재하지 않는다

측정 표본이 0인데 `observed_score`가 있으면 그 숫자는 아무것도 관측하지 않은 값이다.

| | |
|---|---|
| **위반 시** | 점수를 부재로 되돌린다. **0으로 두지 않는다** — 0은 "가장 못한다"는 뜻이고 부재는 "모른다"는 뜻이다 |
| **탐지** | Profile 재계산 시점 |

### INV-R-04 — Resource는 Goal을 직접 참조하지 않는다

Resource가 Goal을 알면 특정 Goal에 최적화된 Resource가 생기고, Resource Agnostic 원칙이 깨진다.

| | |
|---|---|
| **위반 시** | 참조를 제거한다. Goal 정보가 실행에 필요하면 Context로 전달한다([Rule REL-004](e000a-entity-relationships.md)) |

### INV-R-05 — Drift가 감지된 Resource의 예측값은 그대로 쓰이지 않는다

성능이 기준선에서 벗어난 것을 알면서 이전 예측값으로 Utility를 계산하면, 알고 있는 오차를 그대로 결정에 넣는 것이다.

| | |
|---|---|
| **위반 시** | 해당 Resource의 예측 신뢰도를 낮추고 재측정을 우선 배정한다. Drift 방향이 아래쪽이면 후보 순위를 강등한다 |

### INV-R-06 — Deprecated Resource는 새 Decision의 후보가 되지 않는다

| | |
|---|---|
| **위반 시** | 후보에서 제거하고 이미 선택된 경우 Decision을 재실행한다. 단 **진행 중인 Execution은 중단하지 않는다** — 중단 비용이 교체 이득보다 큰 경우가 많다 |

Entity 간 불변식은 [e000a-entity-relationships.md](e000a-entity-relationships.md)가 단일 권위다.

---

## 6. Lifecycle

```
Registered → Evaluating → Active → Optimized
                             │         │
                             ▼         ▼
                         Deprecated → Removed
```

| 상태 | 의미 |
|---|---|
| **Registered** | Registry 등록 완료. 선언 정보만 존재 |
| **Evaluating** | Cold Start — 저위험 Task로 검증 중 ([Volume 4-B §11](../v4b-resource-intelligence.md)) |
| **Active** | 정식 후보군 편입. 실사용 데이터 축적 중 |
| **Optimized** | 충분한 이력으로 Context별 강점이 파악된 상태 |
| **Deprecated** | 신규 할당 중단 (구버전, 지속적 Drift, 제공 중단 예고) |
| **Removed** | Registry에서 제거. 이력 데이터는 보존 |

**Invariant:** Removed 상태여도 **성능 이력은 삭제하지 않는다.** 후속 버전·유사 Genome 추론([Volume 4-C §12](../v4c-resource-genome.md))의 근거 데이터이기 때문이다.

### 6.1 등록과 발견

Resource는 Resource Registry([Volume 6 §4](../v6-developer-platform.md))에 등록된다.

```
외부 Resource (AI / Tool / Human / API)
  ↓
Resource Adapter (Universal Resource Interface로 변환)
  ↓
Capability Declaration (무엇을 잘하는지 선언)
  ↓
Registry 등록 → Lifecycle: Registered
  ↓
Cold Start 평가 → Evaluating → Active
```

발견(Discovery)의 방향은 두 가지다.

1. **개발자가 등록한다** — Resource SDK / Plugin System ([Volume 6](../v6-developer-platform.md))
2. **시스템이 발견한다** — Autonomous Benchmarking Engine이 새 모델을 스스로 찾아 등록한다 ([Volume 4-D](../v4d-autonomous-benchmarking.md))

### 6.2 성능 이력과 Drift

Resource Profile은 **관찰로 유지된다.** 모든 Execution 후 다음이 갱신된다.

```
Execution 완료
  ↓
Outcome 평가 (품질, 비용, 지연, 사용자 만족)
  ↓
observed_score 갱신 (해당 Capability × 해당 Context)
  ↓
Expected vs Actual 비교
  ↓
차이가 임계값 초과 → Drift 감지 → Ranking 하락 / Evaluating 강등
```

핵심 원칙 두 가지. ([Volume 4-B](../v4b-resource-intelligence.md))

1. **Benchmark < Production Data** — 공식 벤치마크 95점보다 "한국 교육 마케팅에서 실제 92% 성공"을 더 신뢰한다.
2. **절대 순위는 없다** — Resource의 점수는 Context(`한국어 / 교육 / 학부모 타겟 / 윈터캠프`)별로 관리된다.

오래된 관찰은 가중치가 낮아진다(Capability Decay). 6개월 전 데이터의 가중치는 오늘의 0.3 수준이다.

---

## 7. Relationships

```
Capability ◀──(제공)── Resource ──(수행)──▶ Execution ──▶ Outcome
     ▲                     ▲                                 │
     │                     │                                 ▼
   Task ──(요구)──── Decision Engine ◀──────────────── Feedback/Learning
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Capability](e006-capability.md) | Resource는 Capability를 제공한다. 제공 수준은 계속 측정된다 | `Resource N:M Capability` |
| [Task](e005-task.md) | Resource는 Task에 **할당**된다. 소유하지 않는다 | `Task N:M Resource` (Decision 경유) |
| [Goal](e001-goal.md) | Resource는 Goal을 모른다. Goal 정보는 Context로만 전달된다 | 직접 관계 없음 (INV-R-04) |
| [Decision](e009-decision.md) | Decision의 출력이 Task-Resource 할당이다 | `Resource 1:0..N Decision` |
| [Execution](e013-execution.md) | 실행 주체. 성능 이력의 귀속 대상이다 | `Resource 1:0..N Execution` |
| [Resource Profile](e025-resource-profile.md) | 관측 데이터의 저장소. Resource 등록 정보와 분리된다 | `Resource 1:0..1 Resource Profile` |
| [Feedback](e012-feedback.md) | Feedback이 observed_score와 Drift 감지의 입력이다 | `Resource 1:0..N Feedback` |

**Resource는 아무것도 참조하지 않는다.** Task도 Decision도 Resource를 가리킬 뿐, Resource는 자신이 어디에 쓰이는지 모른다.

### 7.1 Resource 선택은 누구의 소관인가

**본 문서는 Resource가 "무엇인지"만 정의한다. "어떤 Resource를 고르는지"는 정의하지 않는다.**

| 질문 | 담당 |
|---|---|
| Resource란 무엇인가 | 본 문서 (Entity 007) |
| Resource를 어떻게 측정하는가 | [Volume 4-B — Resource Intelligence](../v4b-resource-intelligence.md) |
| Resource의 행동 특성을 어떻게 표현하는가 | [Volume 4-C — Resource Genome](../v4c-resource-genome.md) |
| 어떤 Resource를 선택하는가 | Decision Engine ([Volume 4](../v4-decision-engine.md)), Decision Entity (Entity 009, 예정) |

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
  "capabilities": [
    {
      "name": "language.generation.copywriting",
      "declared_score": 90,
      "observed_score": 93,
      "confidence": 0.95
    },
    { "name": "reasoning.planning", "declared_score": 89, "confidence": 0.9 }
  ],
  "cost_model": { "unit": "token", "input_per_1k": 0.003, "output_per_1k": 0.015 },
  "performance": {
    "reliability": 0.95,
    "latency_ms": 800,
    "success_rate": 0.92,
    "drift_detected": false
  },
  "limitations": ["실시간 검색 불가"],
  "availability": "24/7",
  "lifecycle": "Active"
}
```

인간 Resource도 **같은 구조**를 가진다.

```json
{
  "id": "human:copywriter_kim",
  "name": "김 카피라이터",
  "type": "human",
  "capabilities": [
    { "name": "language.generation.copywriting", "observed_score": 96, "confidence": 0.88 }
  ],
  "cost_model": { "unit": "task", "per_task": 50000 },
  "performance": { "reliability": 0.9, "latency_ms": 14400000 },
  "availability": "평일 10:00-19:00",
  "lifecycle": "Active"
}
```

기계가 읽을 수 있는 스키마: [`resource.schema.json`](../intent-os-spec/schemas/resource.schema.json)

---

## 9. Validation Rules

```
등록 요청
  ↓
Identity 중복 검사 ── 중복 시 → 버전 등록으로 전환
  ↓
Capability 선언 확인 (R-001) ── 없으면 반려
  ↓
Capability id 정규화 ── Taxonomy 미등록 id → Alias 해소 또는 등록 절차
  ↓
Interface 적합성 검사 (R-003) ── execute/estimate_* 응답 확인
  ↓
Cost/Latency 추정 검증 (R-004)
  ↓
Registry 등록 (Registered)
  ↓
Cold Start 평가 계획 생성 → Evaluating
```

---

## 10. Examples

### 예시 1 — 세 종류의 Resource가 같은 인터페이스로 등록된 모습

```
anthropic:claude-5        llm     capabilities: language.generation.copywriting 88 (conf 0.82)
                                                analysis.audience             79 (conf 0.71)
                                  cost: 토큰당 / 지연 p50 1,800ms / 가용 24h

human:copywriter_kim      human   capabilities: language.generation.copywriting 94 (conf 0.91)
                                                creative.brand_strategy       86 (conf 0.77)
                                  cost: 건당 50,000 KRW / 지연 p50 4시간 / 가용 평일 10-19시

meta:ads_api              api     capabilities: execution.ad_delivery           — (측정 불가)
                                  cost: 집행액 비례 / 지연 p50 900ms / 가용 24h
```

**세 개가 같은 필드 구조를 갖는다.** 김 카피라이터의 지연이 4시간이라는 사실은 Decision이 `latency` 가중치로 다룰 뿐, 별도 코드 경로를 만들지 않는다.

### 예시 2 — 선언과 관측이 갈리는 순간

```
등록 시점 (2026-07-01)
  openai:gpt   copywriting  declared_score 95   observed_score 없음   conf —

실행 12건 후 (2026-08-04)
  openai:gpt   copywriting  declared_score 95   observed_score 81     conf 0.68
```

선언은 95였지만 이 학원의 실제 Task에서는 81이었다. **Decision은 81을 본다**(Rule R-002). 선언값은 관측이 쌓이기 전의 임시 근거일 뿐이다.

### 예시 3 — Drift 감지와 그 후

```
anthropic:claude-5  copywriting
  7월 관측 88 (표본 40)
  8월 관측 76 (표본 12)   ← 연속 3개 관측 구간에서 기준선 이탈
  ↓
drift: { detected: true, direction: down, magnitude: 0.14, windows_deviated: 3 }
  ↓ INV-R-05
예측 신뢰도 하향 → 고위험 Task에서 후보 순위 강등, 저위험 Task로 재측정 배정
```

Drift는 Resource를 즉시 배제하지 않는다. **모른다는 사실을 반영해 배정을 바꿀 뿐이다.**

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **같은 Resource가 두 Registry에 다른 id로 등록** | 성능 이력이 갈라져 어느 쪽도 유의미한 표본을 못 갖는다. `provider:name` 네임스페이스로 동일성을 판정해 병합한다. 병합 시 관측 이력은 합치되 **버전이 다르면 합치지 않는다** |
| **Resource 버전이 올라감** (claude-5 → claude-5.1) | 새 Resource로 등록한다. 같은 이름이라도 버전이 다르면 성능 이력을 합치지 않는다 — 합치면 개선도 퇴보도 감지되지 않는다 |
| **인간 Resource가 응답하지 않음** | Resource를 실패로 표시하지 않는다. 해당 Execution만 `TimedOut`이고, 반복되면 `availability`를 보정한다. 사람은 고장 나는 것이 아니라 바쁜 것이다 |
| **비용을 측정할 수 없는 Resource** (정액 계약, 사내 도구) | `cost.amount`를 계약 단가로 안분하고 `estimated: true`로 표시한다. `null`은 허용하지 않는다 — 비용 0으로 오인되면 Utility가 왜곡된다 |
| **Resource가 선언한 Capability를 실제로는 못 함** | 선언을 지우지 않는다. `observed_score`가 낮게 쌓이면서 자연히 후보에서 밀린다. 선언을 지우면 "왜 이 판단이 틀렸는가"의 근거가 사라진다 |
| **표본이 3건뿐인데 점수가 95** | 점수보다 `sample_size`가 먼저다. 표본 3개짜리 95점은 표본 200개짜리 80점보다 약하게 다룬다([e025 §4](e025-resource-profile.md)) |
| **Resource가 실행 중 폐기됨** | 진행 중 Execution은 끝까지 간다(INV-R-06). 새 Decision부터 후보에서 빠진다. 중단 비용이 교체 이득보다 큰 경우가 대부분이다 |

---

## 12. Open Issues (v1.0)

### Human Resource의 특수성

인간을 동일 인터페이스로 다루는 원칙은 유지하되, 실무적으로 다른 축이 존재한다.

- 동의와 근로 조건 — 할당 자체에 수락/거절 절차가 필요하다
- 가용성의 비결정성 — `availability`가 API처럼 안정적이지 않다
- 평가의 민감성 — `observed_score` 공개 범위와 윤리 규칙이 필요하다

### Composite/Hybrid Resource의 표현

조합 Resource를 단일 Resource로 등록할 때, 내부 구성(파이프라인)의 스키마 표현이 미정이다. [Volume 4-E — Strategy Graph](../v4e-strategy-graph.md)와의 역할 분담을 정해야 한다.

### 앞으로 보강해야 할 항목

- Cost Model의 표준 스키마 (토큰/건당/시간당/정액 통합 표현)
- Health Monitoring 필드의 스키마 반영 ([Volume 4-B §14](../v4b-resource-intelligence.md))
- Genome 참조 필드 (resource ↔ genome 연결, [Volume 4-C](../v4c-resource-genome.md))
- Registry 간 Resource 식별자 충돌 규칙 (`provider:name` 네임스페이스 표준화)
- 실제 예시 30~50개

