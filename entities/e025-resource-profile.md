# Entity 025: Resource Profile

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Resource Profile is the living, versioned, context-scoped record of a Resource's measured performance — separated from the Resource's identity so that capability scores, cost, latency, and reliability can evolve independently of what the Resource is.**

> Resource Profile은 하나의 Resource가 **실제로 어떻게 수행하는지**에 대한 살아있는·버전을 갖는·Context별 측정 기록이며, Resource의 정체성과 분리되어 능력 점수·비용·지연·신뢰도가 독립적으로 변할 수 있게 한다.

여기서 중요한 것은 **분리(Separation)** 다.

```
Resource         "Claude 5는 Anthropic이 만든 LLM이다"        ← 거의 변하지 않는다
Resource Profile "한국 교육 마케팅 카피에서 observed 93,
                  최근 30일 성공률 92%, p95 지연 1,240ms"      ← 매일 변한다
```

두 가지를 한 객체에 두면 **정체성을 조회할 때마다 측정값이 바뀌어 있다.** [Decision](e009-decision.md)의 `inputs_snapshot`은 "그 시점의 측정값"을 동결해야 하는데, 그 대상이 바로 Profile이다.

---

## 2. Resource Profile은 무엇이 아닌가?

### Profile은 Resource가 아니다

❌ `Claude 5 / Anthropic / v5.0` — 이건 [Resource](e007-resource.md)의 Identity다.

| | Resource | Resource Profile |
|---|---|---|
| 내용 | 무엇인가 (id, name, type, provider) | 얼마나 잘하는가 (점수, 비용, 지연) |
| 변경 빈도 | 버전 업 시 | 실행마다 |
| 출처 | 등록 | 관측 |
| 버전 | Resource 버전 | Profile 스냅샷 버전 |

### Profile은 Capability가 아니다

❌ `language.generation.copywriting` — 이건 [Capability](e006-capability.md)다. **능력의 정의**이지 **그 능력의 수행 수준**이 아니다.

```
Capability        language.generation.copywriting  (정의)
Resource          anthropic:claude-5               (주체)
Resource Profile  그 주체의 그 능력 = 93점          (측정)
```

Profile은 이 **(주체 × 능력 × Context)** 삼중항의 값을 담는다.

### Profile은 Benchmark가 아니다

❌ `MMLU 88.7점`

벤치마크는 **공개 시험 점수**이고 Profile은 **현장 성적**이다. [Volume 4-B](../v4b-resource-intelligence.md)의 원칙이 그대로 적용된다.

> **Benchmark < Production Data**

공식 벤치마크 95점보다 "한국 교육 마케팅에서 실제 92% 성공"을 더 신뢰한다. 벤치마크는 Profile의 `declared` 영역에 참고값으로만 들어간다.

### Profile은 Genome이 아니다

❌ `이 모델은 장문에서 일관성이 떨어지고 지시 준수가 강하다`

[Resource Genome](../v4c-resource-genome.md)은 **행동 특성의 표현**이고 Profile은 **수치 측정값**이다. Genome이 "어떤 성격인가"라면 Profile은 "얼마나 잘했는가"다. Profile은 `genome_ref`로 Genome을 참조한다.

### Profile은 절대 순위표가 아니다

❌ `Claude 93 > GPT 89 > Gemini 85`

**Intent OS에 절대 순위는 없다.** 모든 점수는 Context에 종속된다(Rule RPF-002).

```
language.generation.copywriting
├── context: {domain: 교육, lang: ko, audience: 학부모}  → Claude 93 / GPT 87
└── context: {domain: 커머스, lang: en, audience: B2B}    → Claude 88 / GPT 92
```

---

## 3. Design Principles

### Rule RPF-001 — Resource와 1:1이다

모든 Resource는 정확히 하나의 Profile을 갖는다. [Tool](e024-tool.md)과 인간 Resource도 예외가 아니다.

### Rule RPF-002 — 점수는 Context별로 관리한다

단일 점수는 존재하지 않는다. `capability_scores`는 `(capability, context)` 키를 갖는 배열이다.

Context 축은 [Context Entity](e003-context.md)의 Scope 계층을 따른다.

| 축 | 예 |
|---|---|
| `domain` | 교육 / 커머스 / 의료 |
| `language` | ko / en |
| `audience` | 학부모 / 학생 / B2B |
| `task_type` | Creation / Analysis / Research |

### Rule RPF-003 — declared와 observed를 분리한다

```
declared_score   제공자·개발자가 선언한 값. 신뢰의 시작점일 뿐이다
observed_score   실제 실행에서 측정된 값. 최종 판단의 근거
```

[e007 Rule R-002](e007-resource.md)의 공식을 구조로 표현한 것이다.

$$Final = f(declared, observed, sample\_size, recency)$$

**표본이 적을 때만 declared에 의존한다.** 표본이 쌓이면 observed가 지배한다.

### Rule RPF-004 — 스냅샷 버전을 갖는다

Profile은 계속 변하므로, Decision이 참조하려면 **동결된 버전**이 필요하다.

```
Decision dec_101
  inputs_snapshot: { resource_profile_version: "rp_claude5_2026-08-04T09:00Z" }
```

이 버전을 조회하면 **그 시점의 Profile을 그대로 재현**할 수 있다. [e009 Rule D-004](e009-decision.md)가 요구하는 재현성의 실체가 여기 있다.

### Rule RPF-005 — 오래된 관찰은 감쇠한다

$$w(t) = e^{-\lambda \cdot age}$$

6개월 전 데이터의 가중치는 오늘의 0.3 수준이다([e007 §8](e007-resource.md)). 모델은 업데이트되고 시장은 변한다. 1년 전 성적으로 오늘을 판단하면 안 된다.

### Rule RPF-006 — 신뢰도(Confidence)를 함께 기록한다

점수만으로는 부족하다. **표본 3건의 93점과 표본 200건의 93점은 다른 정보다.**

$$confidence = g(sample\_size, variance, recency)$$

Decision Engine은 낮은 신뢰도의 높은 점수를 신중히 다뤄야 한다.

### Rule RPF-007 — Drift는 Profile의 상태다

성능 변화는 예외 상황이 아니라 **정상적으로 추적되는 상태**다. `drift` 블록을 상시 유지한다.

### Rule RPF-008 — Profile 없는 Resource는 Active가 될 수 없다

[INV-15](e000a-entity-relationships.md). Profile이 없으면 cost·latency 추정이 불가능해 Utility를 계산할 수 없다.

---

## 4. Attributes

```
Resource Profile
├── Identity
│   ├── profile_id
│   ├── resource_id
│   ├── snapshot_version
│   └── updated_at
├── Capability Scores
│   └── [ { capability, context, declared, observed,
│           sample_size, confidence, last_observed_at } ]
├── Cost Model
│   ├── unit
│   ├── rates
│   └── observed_avg_cost
├── Performance
│   ├── latency { p50, p95, p99 }
│   ├── reliability
│   ├── success_rate
│   └── throughput
├── Availability
│   ├── schedule
│   ├── uptime_30d
│   └── rate_limit
├── Drift
│   ├── detected
│   ├── direction
│   ├── magnitude
│   └── detected_at
├── Limitations
│   └── limitations[]
└── Links
    ├── genome_ref
    └── evidence { execution_count, window }
```

| 속성 | 의미 | 예 |
|---|---|---|
| **profile_id** | 식별자 | `rp_claude5` |
| **resource_id** | 대상 Resource | `anthropic:claude-5` |
| **snapshot_version** | 동결 버전 (RPF-004) | `rp_claude5_2026-08-04T09:00Z` |
| **capability_scores** | (능력 × Context)별 점수 | §8 참조 |
| **observed_avg_cost** | 실측 평균 비용 | `{ "amount": 0.39, "currency": "USD", "per": "execution" }` |
| **latency** | 지연 분포 | `{ "p50": 820, "p95": 1240, "p99": 2100 }` |
| **reliability** | 결과 일관성 | `0.95` |
| **success_rate** | 최근 성공률 | `0.92` |
| **uptime_30d** | 가용성 | `0.998` |
| **drift** | 성능 변화 상태 (RPF-007) | `{ "detected": false }` |
| **limitations** | 알려진 제약 | `["실시간 검색 불가"]` |
| **genome_ref** | Genome 참조 | `genome_claude5` |
| **evidence** | 근거 표본 | `{ "execution_count": 214, "window": "P30D" }` |

### 4.1 왜 평균이 아니라 분포인가

`latency`를 평균 하나로 두면 안 된다.

```
Resource A  평균 900ms   p50 850   p95 1,050   p99 1,200
Resource B  평균 900ms   p50 400   p95 3,800   p99 9,500
```

평균이 같지만 B는 **20번에 한 번 3.8초를 기다린다.** 사용자 대기가 있는 Task에서는 A가 압도적으로 낫다. Utility 계산에 p95를 쓸지 p50을 쓸지는 Task의 성격이 결정한다.

### 4.2 Human Resource의 Profile

인간도 같은 구조를 쓴다([e007 §9](e007-resource.md)).

| 속성 | AI Resource | Human Resource |
|---|---|---|
| `latency.p50` | `820` (ms) | `14400000` (4시간) |
| `unit` | `token` | `task` |
| `schedule` | `24/7` | `평일 10:00-19:00` |
| `uptime_30d` | API 가용성 | 응답률 |
| `drift` | 모델 업데이트 | 컨디션·업무량 변화 |

**같은 스키마로 다룬다는 원칙이 여기서 실제로 지켜진다.** 다만 인간 Profile의 공개 범위와 윤리 규칙은 별도 문제다(§12).

---

## 5. Invariants

### INV-RPF-01 — Resource당 Profile은 정확히 1개다

| | |
|---|---|
| **위반 시** | 중복 Profile 생성 거부. 스냅샷은 Profile의 버전이지 별도 Profile이 아니다 |

### INV-RPF-02 — Active Resource는 Profile을 갖는다

전역 불변식 [INV-15](e000a-entity-relationships.md)의 Profile 측 표현이다.

| | |
|---|---|
| **위반 시** | Resource를 `Evaluating`으로 강등하고 후보군에서 제외 |

### INV-RPF-03 — 스냅샷은 불변이다

| | |
|---|---|
| **위반 시** | 과거 Decision을 재현할 수 없게 된다. 저장 계층이 쓰기 거부 ([INV-06](e000a-entity-relationships.md)) |

### INV-RPF-04 — Context 없는 점수는 존재하지 않는다

| | |
|---|---|
| **위반 시** | `context: global`을 명시적으로 부여한다. 암묵적 전역 점수는 금지 (Rule RPF-002) |

### INV-RPF-05 — confidence는 sample_size와 함께 기록된다

| | |
|---|---|
| **위반 시** | 표본 없는 신뢰도는 근거가 없다. 생성 거부 |

### INV-RPF-06 — Removed Resource의 Profile은 삭제되지 않는다

[e007 §6](e007-resource.md)의 불변식과 같다.

| | |
|---|---|
| **위반 시** | 삭제 차단. 후속 버전·유사 Genome 추론의 근거 데이터다 |

### INV-RPF-07 — Drift가 감지된 Capability의 점수는 즉시 반영되지 않는다

급격한 점수 변동은 일시적 장애일 수 있다. **Drift 확정 전에는 후보 순위만 낮추고 점수는 유지**한다.

| | |
|---|---|
| **위반 시** | 일시적 장애로 장기 점수가 파괴된다 |
| **확정 기준** | 3개 연속 관측 윈도우에서 동일 방향 이탈 |

---

## 6. Lifecycle

Profile의 수명은 Resource를 따라가되, **스냅샷은 독립적으로 축적**된다.

```
Initialized → Calibrating → Established ──▶ Drifting ──▶ Established
                                 │              │
                                 │              └──▶ Degraded
                                 └──▶ Stale ──▶ Calibrating
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Initialized** | declared만 존재. observed 없음 | Resource 등록 |
| **Calibrating** | Cold Start 관측 중 | 첫 Execution |
| **Established** | 충분한 표본으로 신뢰 가능 | `sample_size ≥ 30` 또는 `confidence ≥ 0.8` |
| **Drifting** | 이탈 감지. 확정 전 | 1~2회 윈도우 이탈 |
| **Degraded** | Drift 확정. 점수 하향 | 3회 연속 이탈 (INV-RPF-07) |
| **Stale** | 오랫동안 관측 없음 | `last_observed_at`이 90일 초과 |

### 6.1 스냅샷 생성

```
Execution 종료 → Evaluation 완료
  ↓
observed_score 갱신 (해당 capability × context)
  ↓
변화량이 임계값(예: 2점) 초과인가?
  ├── Yes → 새 스냅샷 발행 (snapshot_version 갱신)
  └── No  → 기존 스냅샷 유지, 내부 누적만
  ↓
일 1회 정기 스냅샷 (변화가 없어도)
```

**모든 갱신마다 스냅샷을 만들지 않는다.** Decision이 참조할 수 있을 정도의 해상도(일 단위 + 유의미한 변화 시)면 충분하다.

---

## 7. Relationships

```
Resource 007 ──1:1──▶ Resource Profile 025 ──▶ snapshot (불변, N개)
     │                        ▲       │
Tool 024 ──1:1───────────────┘       │
                                      ├──참조──▶ Decision 009 (inputs_snapshot)
Evaluation 015 ──갱신───────────────▶│
Outcome 014 ──갱신──────────────────▶│
                                      └──참조──▶ Genome (Volume 4-C)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Resource](e007-resource.md) | 정확히 하나의 Profile | `Resource 1:1 Resource Profile` |
| [Tool](e024-tool.md) | Tool도 Profile을 갖는다 | `Tool 1:1 Resource Profile` |
| [Decision](e009-decision.md) | `inputs_snapshot`이 Profile 스냅샷을 참조 | `Resource Profile 1:0..N Decision` |
| [Outcome](e014-outcome.md) | 비용·지연 실측값의 원천 | `Outcome N:1 Resource Profile` |
| [Evaluation](e015-evaluation.md) | `observed_score` 갱신의 권위 있는 신호 | `Evaluation N:1 Resource Profile` |
| [Capability](e006-capability.md) | 점수의 대상 | `Resource Profile N:M Capability` |
| [Context](e003-context.md) | 점수의 범위를 결정 | `Context N:M Resource Profile` |
| [Assumption](e017-assumption.md) | `technical` 가정의 검증 대상 | `Resource Profile 1:0..N Assumption` |

---

## 8. Canonical Representation

```json
{
  "profile_id": "rp_claude5",
  "resource_id": "anthropic:claude-5",
  "snapshot_version": "rp_claude5_2026-08-04T09:00Z",
  "updated_at": "2026-08-04T09:00:00Z",
  "status": "Established",
  "capability_scores": [
    {
      "capability": "language.generation.copywriting",
      "context": { "domain": "교육", "language": "ko", "audience": "학부모" },
      "declared_score": 90,
      "observed_score": 93,
      "sample_size": 214,
      "confidence": 0.95,
      "variance": 4.1,
      "last_observed_at": "2026-08-04T09:30:01Z"
    },
    {
      "capability": "language.generation.copywriting",
      "context": { "domain": "커머스", "language": "en", "audience": "B2B" },
      "declared_score": 90,
      "observed_score": 88,
      "sample_size": 12,
      "confidence": 0.52,
      "variance": 9.8,
      "last_observed_at": "2026-07-11T14:02:00Z"
    },
    {
      "capability": "reasoning.planning",
      "context": { "domain": "global" },
      "declared_score": 89,
      "observed_score": 91,
      "sample_size": 87,
      "confidence": 0.88,
      "last_observed_at": "2026-08-03T18:20:00Z"
    }
  ],
  "cost_model": {
    "unit": "token",
    "rates": { "input_per_1k": 0.003, "output_per_1k": 0.015, "currency": "USD" },
    "observed_avg_cost": { "amount": 0.39, "currency": "USD", "per": "execution" }
  },
  "performance": {
    "latency_ms": { "p50": 820, "p95": 1240, "p99": 2100 },
    "reliability": 0.95,
    "success_rate": 0.92,
    "throughput": { "concurrent_max": 20 }
  },
  "availability": {
    "schedule": "24/7",
    "uptime_30d": 0.998,
    "rate_limit": { "per_minute": 500 }
  },
  "drift": {
    "detected": false,
    "direction": null,
    "magnitude": null,
    "detected_at": null,
    "windows_deviated": 0
  },
  "limitations": ["실시간 검색 불가", "이미지 내 한국어 텍스트 인식 취약"],
  "genome_ref": "genome_claude5",
  "evidence": { "execution_count": 214, "window": "P30D", "decay_lambda": 0.0058 }
}
```

인간 Resource의 Profile도 같은 구조다.

```json
{
  "profile_id": "rp_copywriter_kim",
  "resource_id": "human:copywriter_kim",
  "snapshot_version": "rp_copywriter_kim_2026-08-04T09:00Z",
  "status": "Established",
  "capability_scores": [
    {
      "capability": "language.generation.copywriting",
      "context": { "domain": "교육", "language": "ko", "audience": "학부모" },
      "declared_score": null,
      "observed_score": 96,
      "sample_size": 38,
      "confidence": 0.88,
      "last_observed_at": "2026-08-04T18:10:00Z"
    },
    {
      "capability": "review.brand_tone",
      "context": { "domain": "교육", "language": "ko" },
      "observed_score": 97,
      "sample_size": 41,
      "confidence": 0.9
    }
  ],
  "cost_model": { "unit": "task", "rates": { "per_task": 50000, "currency": "KRW" } },
  "performance": {
    "latency_ms": { "p50": 14400000, "p95": 28800000, "p99": 86400000 },
    "reliability": 0.90,
    "success_rate": 0.95
  },
  "availability": { "schedule": "평일 10:00-19:00", "uptime_30d": 0.86 },
  "drift": { "detected": false },
  "limitations": ["주말 불가", "동시 처리 1건"],
  "visibility": "internal_restricted"
}
```

기계가 읽을 수 있는 스키마: [`resource-profile.schema.json`](../intent-os-spec/schemas/resource-profile.schema.json)

---

## 9. Validation Rules

### 9.1 갱신 파이프라인

```
Evaluation 완료 (evaluation.completed Event 구독)
  ↓
대상 Resource / Capability / Context 식별
  ↓
Context 정규화 (Context Taxonomy 조회)
  ── 미등록 Context → global로 폴백 + 등록 제안
  ↓
관측값 추가
  ├── quality        → observed_score 후보
  ├── Outcome.cost   → observed_avg_cost
  ├── Outcome.latency_ms → latency 분포
  └── verdict        → success_rate
  ↓
감쇠 가중 평균 계산 (RPF-005)
  new_observed = Σ(w(t) × score) / Σ(w(t))
  ↓
sample_size, variance 갱신
  ↓
confidence 재계산 (RPF-006)
  ↓
Drift 검사 (§9.2)
  ↓
변화량 > 임계값 또는 일일 정기 시각?
  ├── Yes → 새 snapshot_version 발행 (불변, INV-RPF-03)
  └── No  → 내부 누적만
  ↓
status 전이 판정 (§6)
  ↓
Event 발행 (resource.profile_updated)
```

### 9.2 Drift 감지

```
관측 윈도우(예: 최근 20건) 집계
  ↓
기준값(직전 Established 스냅샷)과 비교
  ↓
|현재 − 기준| > 임계값(예: 5점) 인가?
  ├── No  → windows_deviated = 0, Established 유지
  └── Yes → windows_deviated += 1
       ↓
     windows_deviated < 3?
       ├── Yes → Drifting
       │         · 후보 순위만 낮춘다
       │         · 점수는 유지한다 (INV-RPF-07)
       └── No  → Degraded 확정
                 · observed_score 갱신
                 · Event 발행 (resource.drift_detected)
                 · technical Assumption 검증 트리거 (e017)
                 · Resource lifecycle → Evaluating 강등 검토
```

**3회 확인 전에 점수를 바꾸지 않는 것이 핵심이다.** 한 번의 장애로 6개월치 학습이 무너지면 안 된다.

### 9.3 Final Score 산출 (Decision Engine이 호출)

```
입력: (capability, context, task_type)
  ↓
정확히 일치하는 capability_score 조회
  ├── 있음 → 사용
  └── 없음 → Context 축을 한 단계씩 일반화하며 재조회
              {교육, ko, 학부모} → {교육, ko} → {교육} → global
              ── 일반화할 때마다 confidence에 페널티 적용
  ↓
confidence 기반 declared/observed 혼합 (RPF-003)
  final = observed × c + declared × (1 − c),  c = confidence
  ↓
status 보정
  ├── Drifting  → 순위 페널티 적용
  ├── Degraded  → observed 그대로 (이미 하향됨)
  └── Stale     → confidence 추가 감쇠
  ↓
Final Score 반환 + confidence 반환
```

**두 값을 모두 반환한다.** Decision은 점수뿐 아니라 그 점수를 얼마나 믿을 수 있는지도 알아야 한다.

---

## 10. Examples

### 예시 1 — Cold Start부터 Established까지

```
2026-06-01  anthropic:claude-5 등록
            Profile Initialized  declared 90, observed 없음, confidence 0.0
   ↓ Cold Start: 저위험 Task 5건
2026-06-03  Calibrating  observed 88, sample 5, confidence 0.31
   ↓
2026-06-20  Calibrating  observed 91, sample 24, confidence 0.71
   ↓ sample 30 돌파
2026-06-25  Established  observed 92, sample 31, confidence 0.81
   ↓
2026-08-04  Established  observed 93, sample 214, confidence 0.95
```

`confidence 0.31` 구간에서는 Decision이 declared(90)에 크게 의존한다. 표본이 쌓이면서 observed가 지배한다.

### 예시 2 — Context 일반화

```
Task: 커머스 B2B 영문 카피 작성
조회: (language.generation.copywriting, {커머스, en, B2B})
  ↓
정확 일치: observed 88, sample 12, confidence 0.52
  ↓
Final = 88 × 0.52 + 90 × 0.48 = 88.96
반환: { score: 88.96, confidence: 0.52 }
  ↓
Decision Engine: confidence 0.52는 낮다
  → Multi-Agent 실행 검토 또는 Shadow Execution 병행
```

같은 Resource가 교육/ko 맥락에서는 confidence 0.95다. **한 Resource에 하나의 점수를 두면 이 차이가 사라진다.**

### 예시 3 — Drift

```
2026-09-10  Claude 5.1 배포 (Anthropic 자동 업데이트)
   ↓
윈도우 1 (9/10~9/12)  observed 86 (기준 93, 차이 7 > 5)  → Drifting, deviated 1
윈도우 2 (9/13~9/15)  observed 85                        → Drifting, deviated 2
   ↓ 이 구간에서 Claude의 후보 순위는 낮아지지만 점수는 93 유지
윈도우 3 (9/16~9/18)  observed 85                        → Degraded 확정
   ↓
observed_score 93 → 85
Event: resource.drift_detected
   ↓ 구독: Assumption 검증기
asm_031 ("Claude의 한국어 카피 성능이 유지된다") → Invalidated
   ↓ on_invalidation: substitute
dec_101을 참조하는 진행 중 Task의 Resource 재선택
```

**§9.2의 3-윈도우 규칙 덕분에** 9/10~9/15 사이의 일시적 변동으로 점수를 파괴하지 않았다.

### 예시 4 — Decision의 스냅샷 참조

```
2026-08-04 09:30  dec_101 생성
  inputs_snapshot: {
    resource_profile_versions: {
      "anthropic:claude-5": "rp_claude5_2026-08-04T09:00Z",
      "openai:gpt-5":       "rp_gpt5_2026-08-04T09:00Z",
      "human:copywriter_kim": "rp_copywriter_kim_2026-08-04T09:00Z"
    }
  }

2026-09-20  사후 검토: "8월 4일에 Claude를 고른 것이 옳았는가"
  → 세 스냅샷을 그대로 조회
  → 당시 Claude 93 / GPT 87 / 김 카피라이터 96(단 지연 4시간, 비용 50,000원)
  → decision_quality 판정 가능 (e015 Rule EVA-004)
```

스냅샷이 없으면 이 검토가 불가능하다. **오늘의 점수로 8월의 결정을 평가하면 결과론 편향 그 자체다.**

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **표본이 3건인데 점수가 100점** | `confidence`가 낮게 나온다(0.2 이하). Decision은 declared에 의존한다. **점수만 보고 최고 Resource로 판정하면 안 된다** |
| **90일간 관측 없음** | `Stale`. 점수를 지우지 않되 confidence를 추가 감쇠한다. 다시 쓰이면 `Calibrating`으로 돌아간다 |
| **Resource 버전이 올라감** | 새 Profile을 만들지 않는다. 같은 Profile에서 Drift로 처리한다. 단 제공자가 명시적 major 버전을 발표하면 `Calibrating`으로 리셋하고 이전 스냅샷은 보존한다 |
| **한 번도 실행되지 않은 Capability** | `observed_score: null`. 0으로 두지 않는다. **측정 안 함과 0점은 다르다** ([Outcome Rule OUT-006](e014-outcome.md)과 같은 원칙) |
| **Context가 Taxonomy에 없음** | `global`로 폴백하고 Context 등록을 제안한다. 임의의 새 Context를 자동 생성하면 점수가 파편화된다 |
| **인간 Resource의 낮은 점수 공개** | `visibility: internal_restricted`. 인사 평가로 쓰이지 않도록 접근을 제한한다. 이는 기술 문제가 아니라 윤리 문제다(§12) |
| **Shadow Execution의 결과** | Profile 갱신에 **사용한다**. Goal에는 기여하지 않지만([e014 INV-OUT-05](e014-outcome.md)) 성능 측정에는 유효한 관측이다 |
| **실패한 Execution의 결과** | `success_rate`에 반영한다. `observed_score`에는 반영하지 않는다(품질을 측정할 산출물이 없다). 두 지표를 구분하는 이유다 |
| **비용이 0인 Resource (사내 도구)** | `observed_avg_cost: 0`을 그대로 둔다. Utility에서 비용 항이 0이 되므로 다른 축(품질·신뢰도)이 선택을 결정한다. 정상 동작이다 |

---

## 12. Open Issues (v1.0)

### confidence 산출 공식의 확정

Rule RPF-006은 `g(sample_size, variance, recency)`라고만 서술했다. 실제 공식(베이지안 신용구간, Wilson score 등)이 정해지지 않았다. Decision의 Escalation 임계값이 이 값에 직접 의존하므로 우선순위가 높다.

### Context 일반화의 페널티 크기

§9.3에서 Context 축을 일반화할 때마다 confidence에 페널티를 준다고 했으나, 축마다 중요도가 다르다. `language`를 일반화하는 것과 `audience`를 일반화하는 것의 손실은 같지 않다.

### 인간 Resource Profile의 윤리 규칙

`observed_score`가 인사 평가로 전용될 위험이 실재한다. 접근 통제(§11)만으로 충분한지, 인간 Profile에는 절대 점수 대신 상대 적합도만 두어야 하는지 결정이 필요하다. [e007 Open Issues](e007-resource.md)의 연장선이다.

### 스냅샷 저장 비용

Resource 50개 × 일 1회 스냅샷 × 1년 = 18,250개다. Decision이 참조하는 스냅샷만 영구 보존하고 나머지는 압축·병합하는 정책이 필요하다.

### Genome과의 역할 분담

`genome_ref`로 연결했으나 두 개념의 경계가 흐리다. "장문에서 일관성 하락"은 Genome인가 `limitations`인가. [Volume 4-C](../v4c-resource-genome.md)와의 경계 정리가 필요하다.

### 앞으로 보강해야 할 항목

- confidence 산출 공식 확정
- Context Taxonomy 정의 ([e003](e003-context.md)와 연동)
- Profile 스냅샷 보존·압축 정책
- 실제 예시 30~50개
