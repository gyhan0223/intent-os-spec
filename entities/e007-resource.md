# Entity 007: Resource

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

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

## 3. Resource의 조건

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

## 4. Resource Attributes (Resource Profile)

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

---

## 5. Resource Types

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

## 6. Resource Lifecycle

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

---

## 7. Resource 등록과 발견

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

---

## 8. 성능 이력과 Drift

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

## 9. Canonical Resource Representation

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

## 10. Resource 등록 검증 알고리즘

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

## 11. Resource 선택은 누구의 소관인가

**본 문서는 Resource가 "무엇인지"만 정의한다. "어떤 Resource를 고르는지"는 정의하지 않는다.**

| 질문 | 담당 |
|---|---|
| Resource란 무엇인가 | 본 문서 (Entity 007) |
| Resource를 어떻게 측정하는가 | [Volume 4-B — Resource Intelligence](../v4b-resource-intelligence.md) |
| Resource의 행동 특성을 어떻게 표현하는가 | [Volume 4-C — Resource Genome](../v4c-resource-genome.md) |
| 어떤 Resource를 선택하는가 | Decision Engine ([Volume 4](../v4-decision-engine.md)), Decision Entity (Entity 009, 예정) |

Entity 정의에 선택 로직을 섞으면 Resource가 특정 선택 전략에 종속된다. 계층을 분리한다.

---

## 12. 다른 Entity와의 관계

```
Capability ◀──(제공)── Resource ──(수행)──▶ Execution ──▶ Outcome
     ▲                     ▲                                 │
     │                     │                                 ▼
   Task ──(요구)──── Decision Engine ◀──────────────── Feedback/Learning
```

| Entity | 관계 |
|---|---|
| [Capability](e006-capability.md) | Resource는 Capability를 제공한다. 제공 수준은 계속 측정된다 |
| [Task](e005-task.md) | Resource는 Task에 **할당**된다. 소유하지 않는다 |
| [Goal](e001-goal.md) | Resource는 Goal을 모른다. Goal 정보는 Context로만 전달된다 |
| Decision (Entity 009, 예정) | Decision의 출력이 Task-Resource 할당이다 |
| Feedback (Entity 012, 예정) | Feedback이 observed_score와 Drift 감지의 입력이다 |

---

## 13. Open Issues (v1.0)

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
