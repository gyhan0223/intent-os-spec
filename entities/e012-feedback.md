# Entity 012: Feedback

- **Version:** v2.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Feedback is an evaluative signal about an outcome, originating from a user, from user behavior, or from the system itself, that serves as input to Evaluation.**

> Feedback은 실행 결과에 대한 평가 신호이다. 사용자, 사용자의 행동, 또는 시스템 자신으로부터 발생하며, [Evaluation](e015-evaluation.md)의 입력이 된다.

여기서 중요한 단어는 **Signal(신호)** 이다.

Feedback은 판정이 아니라 **판정의 재료**다. 신호가 곧 결론이 아니라는 점이 이 Entity의 전부다.

### 1.1 Feedback은 어디로 가는가

```
Execution 013 ──▶ Outcome 014 ──▶ Evaluation 015 ──▶ Memory 010 ──▶ Knowledge 011
                                       ▲
                                       │ 입력
                                  Feedback 012
```

> **v1.0 정정:** v1.0은 `Outcome(Runtime State) → Feedback → Learning → Memory/Knowledge` 흐름을 서술했다. 두 가지가 틀렸다.
>
> 1. **Outcome은 Runtime State가 아니라 Entity 014다**([e000a §1](e000a-entity-relationships.md)).
> 2. **Feedback은 Learning으로 직행하지 않는다.** [Evaluation](e015-evaluation.md)의 입력이 되고, Evaluation이 Memory를 낳는다. 판정 단계를 건너뛰면 "재생성 3회"라는 원시 신호가 곧바로 학습에 반영된다.

| 분류 | 예 | 설명 |
|---|---|---|
| **Entity** | [Outcome](e014-outcome.md) (014) | 실행이 만든 **측정 기록** |
| **Entity** | **Feedback** (012) | 그 결과에 대한 **외부 평가 신호** |
| **Entity** | [Evaluation](e015-evaluation.md) (015) | 신호와 측정을 종합한 **판정** |
| **Process** | Learning | Memory를 읽어 Knowledge를 만드는 **수행 과정** |

---

## 2. Feedback은 무엇이 아닌가?

이게 정의보다 훨씬 중요하다.

### Feedback은 Evaluation이 아니다

❌ `품질 0.55, verdict: reject` — 이건 [Evaluation](e015-evaluation.md)이다.

**Feedback은 입력, Evaluation은 산출이다.**

```
Feedback(별점 2개) ─┐
Outcome(측정값)    ─┼──▶ Evaluation Engine ──▶ Evaluation(판정)
Goal(기준)         ─┘
```

| | Feedback | Evaluation |
|---|---|---|
| 출처 | **시스템 외부** | 시스템 내부 판정기 |
| 성격 | 원시 신호 | 4축 점수 + verdict |
| 필수성 | 없을 수 있다 | 모든 Outcome에 대해 수행 |
| 개수 | Outcome당 0..N | Outcome당 0..N |

Feedback 없이도 Evaluation은 만들어진다(자동 평가). 반대로 Feedback만 있고 Evaluation이 없으면 그것은 **아직 판정되지 않은 원시 신호**다.

### Feedback은 Outcome이 아니다

❌ `광고 카피 3종이 생성됨` — 이건 [Outcome](e014-outcome.md)이다.

✅ `사용자가 그중 2종을 폐기하고 1종을 수정 요청함` — 이것이 Feedback이다.

Outcome은 평가 없이 존재할 수 있지만, Feedback은 반드시 **대상을 가리켜야** 한다.

### Feedback은 새로운 Goal이 아니다

❌ `이번엔 학부모 말고 학생 대상으로 써줘` — 표면적으로는 수정 요청처럼 보이지만, 대상 Audience가 바뀌었으므로 **Goal/Intent의 변경**이 섞여 있다.

시스템은 이를 분리해야 한다.

```
Feedback:    기존 카피는 대상에게 맞지 않았다 (부정 신호)
Goal 변경:   Audience: 학부모 → 학생
```

분리하지 않으면 **Resource가 부당하게 낮은 점수를 받는다** — 카피는 학부모용으로 잘 쓰였는데 대상이 바뀌었을 뿐이다.

### Feedback은 Memory가 아니다

Feedback은 [Evaluation](e015-evaluation.md)을 거쳐 [Memory](e010-memory.md)에 반영되지만, Feedback 자체는 별도 Entity다. **하나의 Outcome에 여러 Feedback이 시차를 두고 붙을 수 있다**(생성 직후 만족 → 2주 뒤 성과 부진).

### Feedback은 Event가 아니다

❌ `feedback.received` — 이건 [Event](e020-event.md)다.

**Feedback은 내용이고 Event는 그 도착 사실이다.** Event는 시스템 내부에서 발생한 사실이고, Feedback은 외부에서 들어온 평가다([e020 §2](e020-event.md)).

### Feedback은 Learning이 아니다

❌ `Feedback으로 Resource 점수를 조정하기` — 이건 **Process**다. 신호와 처리 과정을 혼동하면 "Feedback 1건 = 즉시 학습"이라는 위험한 설계가 나온다(Rule F-003).

---

## 3. Design Principles

### Rule F-001 — 반드시 대상(Target)을 가진다

무엇에 대한 평가인지(Outcome / Execution / Decision / Plan / Artifact)가 명시되지 않은 신호는 Feedback으로 저장하지 않는다.

### Rule F-002 — 원시 신호와 해석을 분리한다

`사용자가 결과를 3회 재생성했다`는 **원시 신호(사실)** 다. `사용자가 불만족했다`는 **해석**이다.

Feedback Entity는 원시 신호를 보존하고, 해석은 별도 필드에 Confidence와 함께 기록한다. **재시도는 불만족일 수도, 단순 탐색일 수도 있다.**

### Rule F-003 — Single Feedback ≠ Learning Update

Feedback 1건으로 [Knowledge](e011-knowledge.md)나 [Resource Profile](e025-resource-profile.md)을 갱신하지 않는다([Volume 5 §13](../v5-learning-engine.md), [Rule M-005](e010-memory.md), [INV-RPF-07](e025-resource-profile.md)의 3-윈도우 규칙과 같은 원칙).

**예외:** 명시적 [Policy](e019-policy.md) 위반 신고(법률, 안전)는 즉시 반영한다.

### Rule F-004 — Implicit은 Explicit보다 낮은 가중치를 가진다

행동 추론은 틀릴 수 있다. 기본 가중치: `Explicit > Systemic > Implicit`.

### Rule F-005 — 출처(Provenance)를 가진다

누가/무엇이, 언제, 어떤 채널로 발생시켰는지 기록한다. **악의적·오염된 Feedback을 사후 격리하기 위해서다**(§6, Quarantined).

### Rule F-006 — Goal 변경 성분을 분리한다

§2에서 서술한 대로, Feedback에 섞인 Goal/Intent 변경 요구를 분리해 각각의 경로로 보낸다. 분리하지 않으면 Resource와 Decision이 부당하게 평가된다.

### Rule F-007 — 이의 제기는 기존 Evaluation을 Disputed로 만든다

Feedback이 이미 완료된 Evaluation과 모순되면 그 Evaluation을 `Disputed`로 전이시킨다([e015 §6.1](e015-evaluation.md)). **자동 평가가 틀렸다는 사실 자체가 학습 데이터다.**

---

## 4. Attributes

```
Feedback
├── Identity
│   ├── feedback_id
│   ├── source_type
│   └── created_at
├── Target
│   ├── target_type
│   └── target_ref
├── Content
│   ├── signal              (원시 신호 — Rule F-002)
│   └── interpretation
│         ├── sentiment
│         └── confidence
├── Processing
│   ├── weight
│   ├── routing[]
│   └── goal_change_extracted
├── Provenance
│   ├── actor
│   └── channel
└── Status
    └── status
```

| 속성 | 의미 | 예 |
|---|---|---|
| **feedback_id** | 고유 식별자 | `fb_0553` |
| **source_type** | 출처 분류 (§4.1) | `Implicit` |
| **target_type / target_ref** | 무엇에 대한 평가인가 (Rule F-001) | `Outcome` / `out_331` |
| **signal** | 원시 신호 (Rule F-002) | `사용자가 결과를 사용하지 않고 3회 재생성` |
| **sentiment** | 해석된 방향 | `Negative` |
| **interpretation confidence** | 해석의 확신도 | `0.7` |
| **weight** | 반영 가중치 (Rule F-004) | `0.4` |
| **routing** | 어떤 갱신에 쓰이는가 (§7.1) | `["Evaluation", "Memory"]` |
| **goal_change_extracted** | 분리된 Goal 변경 성분 (Rule F-006) | `null` |
| **actor / channel** | 발생 주체와 채널 (Rule F-005) | `human:대표` / `UI 재생성 버튼` |
| **status** | 처리 상태 (§6) | `Routed` |

### 4.1 Feedback Source Types

모든 Feedback은 정확히 하나의 Source Type을 가진다.

```
Feedback
├── Explicit  — 사용자가 의도적으로 준 평가
├── Implicit  — 사용자 행동에서 추론된 신호
└── Systemic  — 시스템이 스스로 측정한 신호
```

| Type | 신호 예 | 특징 | 기본 weight |
|---|---|---|---|
| **Explicit** | 별점, `이 부분 고쳐줘`, `이건 쓰지 마` | 가장 신뢰도 높음. 그러나 드물다 | 1.0 |
| **Implicit** | 재생성, 결과 미사용, 복사 여부, 세션 이탈 | 풍부하지만 해석이 필요하다 | 0.4 |
| **Systemic** | Metric 달성 여부, 비용 초과, SLA 위반 | 객관적. Goal의 Metric과 직결 | 0.8 |

**Systemic Feedback의 기준은 [Goal](e001-goal.md)의 Success Metric이다.** 그래서 Goal에 Metric이 없으면 Systemic Feedback이 생성되지 않는다.

---

## 5. Invariants

### INV-F-01 — 모든 Feedback은 존재하는 대상을 가리킨다

| | |
|---|---|
| **위반 시** | 저장 거부. 대상 없는 평가는 어디에도 반영할 수 없다 (Rule F-001) |

### INV-F-02 — 원시 신호는 수정되지 않는다

`signal`은 관측된 사실이다. `interpretation`은 재해석될 수 있지만 `signal`은 불변이다.

| | |
|---|---|
| **위반 시** | 쓰기 거부. 신호를 고치면 해석 규칙의 정확도를 검증할 수 없게 된다 (Rule F-002) |

### INV-F-03 — 단일 Feedback이 Knowledge나 Profile을 갱신할 수 없다

| | |
|---|---|
| **위반 시** | 갱신 차단. 집계 버킷을 거쳐 임계값에 도달해야 한다 (Rule F-003) |
| **예외** | Policy 위반 신고는 즉시 반영 |

### INV-F-04 — interpretation은 confidence를 동반한다

| | |
|---|---|
| **위반 시** | 해석을 사실로 취급하게 된다. confidence 없는 해석은 저장 거부 |

### INV-F-05 — Quarantined Feedback은 집계에 포함되지 않는다

| | |
|---|---|
| **위반 시** | 오염된 신호가 Global Knowledge를 왜곡한다. 집계 쿼리에서 제외하고 이미 반영되었다면 재집계 |

### INV-F-06 — Goal 변경 성분은 Feedback 가중치에 포함되지 않는다

대상이 바뀐 것을 Resource의 실패로 계산하면 안 된다.

| | |
|---|---|
| **위반 시** | Resource 점수가 부당하게 하락한다. 분리 검사를 처리 파이프라인에 강제한다 (Rule F-006) |

### INV-F-07 — Feedback은 Evaluation을 거쳐야 Memory에 도달한다

| | |
|---|---|
| **위반 시** | 판정되지 않은 원시 신호가 학습 재료가 된다. Memory 생성 시 `evaluation_ref` 존재를 강제한다 ([e010 §9.1](e010-memory.md)) |

---

## 6. Lifecycle

```
Captured → Interpreted → Routed → Aggregated → Consumed → Archived
                │
                └──▶ Quarantined (오염 의심)
                └──▶ Split       (Goal 변경 성분 분리)
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Captured** | 원시 신호 수집됨 | UI 이벤트 / Metric 관측 / 사용자 발화 |
| **Split** | Goal 변경 성분이 분리됨 | Rule F-006 검사 |
| **Interpreted** | Sentiment/Confidence 해석 완료 | 해석 규칙 적용 |
| **Routed** | 갱신 대상 결정됨 | §7.1 |
| **Aggregated** | 동일 대상의 다른 Feedback과 집계됨 | 집계 버킷 적재 |
| **Consumed** | Evaluation에 반영 완료 | Evaluation 생성/갱신 |
| **Quarantined** | 이상 패턴(스팸, 조작 의심)으로 격리 | 오염 검사 |
| **Archived** | 보존 전용 | 보존 정책 |

---

## 7. Relationships

```
Outcome 014 ◀──평가 대상── Feedback 012 ──입력──▶ Evaluation 015
                              │                        │
       Goal 001 ◀──변경 제안──┤                        ▼
                              │                   Memory 010 ──▶ Knowledge 011
       Event 020 ◀──도착 사실─┘                        │
                                                       ▼
                                          Resource Profile 025 (satisfaction 축)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Evaluation](e015-evaluation.md) | Feedback은 Evaluation의 입력 신호다 | `Feedback N:M Evaluation` |
| [Outcome](e014-outcome.md) | 평가 대상. **직접 반영하지 않고 Evaluation을 거친다** | `Outcome 1:0..N Feedback` |
| [Goal](e001-goal.md) | Systemic Feedback의 기준은 Goal의 Success Metric | `Goal 1:0..N Feedback` |
| [Decision](e009-decision.md) | 결정 자체에 대한 이의 제기 | `Decision 1:0..N Feedback` |
| [Plan](e008-plan.md) | 전략 수준 Feedback | `Plan 1:0..N Feedback` |
| [Artifact](e016-artifact.md) | 산출물 수정·폐기가 Implicit 신호가 된다 | `Artifact 1:0..N Feedback` |
| [Memory](e010-memory.md) | Evaluation을 거쳐 반영된다 (INV-F-07) | 간접 |
| [Knowledge](e011-knowledge.md) | 집계된 Feedback이 지지/반증 근거가 된다 | 간접 |
| [Event](e020-event.md) | `feedback.received`가 도착 사실을 알린다 | `Feedback 1:N Event` |

### 7.1 Feedback Routing

**어떤 Feedback이 어떤 갱신으로 이어지는가.** 이것이 Feedback 명세의 핵심이다.

| Feedback 내용 | 라우팅 대상 | 예 |
|---|---|---|
| 결과물 품질 평가 | **Evaluation** → Resource Profile | `Claude의 copywriting observed_score 조정 근거` |
| 전략 자체에 대한 평가 | **Knowledge** (Task/Domain) | `감성 소구 전략 → 이 도메인에서 유효` 지지/반증 |
| 사용자 취향 신호 | **Knowledge** (User) | `이 대표는 짧은 카피를 선호` |
| 목표 재해석 요구 | **Goal** | `사실 학생 수보다 객단가가 문제였어` → Goal 수정 제안 |
| Metric 달성/미달 | **Evaluation** (deferred) | 상담 신청 +30% → `goal_alignment` 확정 |
| 실행 오류/비용 초과 | **Plan / Constraint** | 재시도 정책, 예산 가드 조정 근거 |
| Policy 위반 신고 | **Policy** (즉시) | 과장 광고 표현 신고 → 즉시 차단 |

```
Feedback (Interpreted)
  ↓
target_type 확인
  ↓
평가 축 분류 (품질? 전략? 취향? 목표? 비용? 규정?)
  ↓
라우팅 대상 결정 (복수 가능)
  ↓
각 대상의 집계 버킷에 적재
  ↓
버킷이 임계값 도달 → Evaluation 생성/갱신 → Memory → Knowledge
```

하나의 Feedback이 **여러 대상에 동시에 라우팅**될 수 있다. `톤이 너무 가벼워요`는 Resource 품질과 User Knowledge 양쪽의 근거가 된다.

### 7.2 Feedback Loop

Intent OS가 시간이 지날수록 좋아지는 유일한 이유가 이 루프다.

```
Goal 001
  ↓
Decision 009 (Resource/전략 선택)
  ↓
Execution 013
  ↓
Outcome 014
  ↓
Feedback 012 (Explicit + Implicit + Systemic)
  ↓
Evaluation 015 (4축 판정 + decision_quality)
  ↓
Memory 010 → Knowledge 011 / Resource Profile 025
  ↓
다음 Decision 개선
  ↓
(반복)
```

이 루프는 [Volume 5 §11](../v5-learning-engine.md)의 Entity 관점 표현이다.

---

## 8. Canonical Representation

```json
{
  "feedback_id": "fb_0553",
  "source_type": "Implicit",
  "target": {
    "target_type": "Outcome",
    "target_ref": "out_331"
  },
  "signal": "사용자가 결과를 사용하지 않고 3회 재생성",
  "interpretation": {
    "sentiment": "Negative",
    "confidence": 0.7
  },
  "weight": 0.4,
  "routing": ["Evaluation", "Memory"],
  "goal_change_extracted": null,
  "provenance": {
    "actor": "human:대표",
    "channel": "UI 재생성 버튼"
  },
  "created_at": "2026-08-04T10:22:00Z",
  "status": "Routed"
}
```

Explicit Feedback으로 이의를 제기하는 경우는 다음과 같다.

```json
{
  "feedback_id": "fb_0881",
  "source_type": "Explicit",
  "target": {
    "target_type": "Evaluation",
    "target_ref": "eva_512"
  },
  "signal": "대표: \"이 카피는 우리 학원 톤이 아니다. 너무 자극적이다\"",
  "interpretation": {
    "sentiment": "Negative",
    "confidence": 0.95
  },
  "weight": 1.0,
  "routing": ["Evaluation", "Knowledge"],
  "goal_change_extracted": null,
  "provenance": {
    "actor": "human:대표",
    "channel": "대화"
  },
  "created_at": "2026-08-04T11:40:00Z",
  "status": "Consumed"
}
```

이 Feedback이 `eva_512`를 `Disputed`로 만들고(Rule F-007), 인간 재평가 `eva_530`을 낳는다.

**이 구조만 Evaluation Engine으로 전달된다.**

기계가 읽을 수 있는 스키마: [`feedback.schema.json`](../intent-os-spec/schemas/feedback.schema.json)

---

## 9. Validation Rules

```
신호 감지 (UI 이벤트 / Metric 관측 / 사용자 발화)
  ↓
Feedback인가? (대상 있는 평가 신호인가 — Rule F-001)
  ├── No  → 폐기 또는 Goal/Intent 변경 처리로 이관
  └── Yes
       ↓
target 존재 확인 (INV-F-01)
  ↓
Source Type 분류 (§4.1)
  ↓
Goal 변경 성분 분리 (Rule F-006, INV-F-06) ── §9.1
  └── 분리되면 status: Split, Goal 수정 제안 생성
  ↓
signal 기록 (불변 — INV-F-02)
  ↓
해석 (Sentiment + Confidence — INV-F-04)
  ↓
가중치 부여 (Rule F-004)
  Explicit 1.0 / Systemic 0.8 / Implicit 0.4
  × interpretation.confidence
  ↓
오염 검사 (이상 빈도, 조작 패턴)
  ├── 의심 → Quarantined (INV-F-05)
  └── 정상
       ↓
Routing (§7.1)
  ↓
기존 Evaluation과 모순? (Rule F-007)
  └── Yes → 해당 Evaluation을 Disputed로 전이
  ↓
집계 버킷 적재 → 임계값 도달 시 Evaluation 생성/갱신 (INV-F-03)
  ↓
Event 발행 (feedback.received)
```

### 9.1 Goal 변경 성분 분리

**이 단계가 없으면 Resource가 부당하게 평가된다.**

```
Feedback 원문: "이번엔 학부모 말고 학생 대상으로 써줘"
  ↓
① 대상 속성(Audience/Metric/Deadline/Budget) 변경 언급이 있는가
  ↓ Yes
② 변경 성분 추출
   goal_change_extracted: { field: "audience", from: "학부모", to: "학생" }
  ↓
③ 잔여 평가 성분 판정
   "기존 결과가 나빴다"는 신호인가, 단순 방향 전환인가
   ├── 방향 전환만  → weight 0으로 설정. Resource 평가에 반영하지 않는다
   └── 불만 포함    → 잔여 성분만 Feedback으로 유지
  ↓
④ Goal 수정 제안 생성 → Goal Engine으로 라우팅
```

---

## 10. Examples

### 10.1 예시 1 — 하나의 Outcome, 세 종류의 Feedback

```
Outcome out_331: 윈터캠프 인스타 광고 카피 3종

Explicit  fb_0881  대표: "톤이 너무 가벼워요"          weight 1.0  Negative
Implicit  fb_0553  마케팅팀이 카피 원문을 복사해감      weight 0.4  Positive(약)
Systemic  fb_0902  2주 후 상담 신청 +30%              weight 0.8  Positive(강)
```

세 신호가 **상충한다.** 그래서 Feedback은 집계 후에만 Evaluation에 반영된다(INV-F-03).

```
집계 결과
  Explicit  −1.0 × 0.95(conf) = −0.95
  Implicit  +0.4 × 0.60       = +0.24
  Systemic  +0.8 × 1.00       = +0.80
  ────────────────────────────────────
  합계 +0.09 → 판정 보류, deferred Evaluation 예약
```

**단일 신호로 결론 내지 않는다.** 톤은 마음에 안 들었지만 성과는 나왔다 — 이 모순 자체가 정보다.

### 10.2 예시 2 — 이의 제기가 Evaluation을 뒤집는다

```
eva_512  automatic  verdict: accept  quality 0.93
   ↓
fb_0881  Explicit  "우리 학원 톤이 아니다"  confidence 0.95
   ↓ Rule F-007
eva_512 → Disputed
   ↓
eva_530  human:대표  quality 0.55  verdict reject
         supersedes: eva_512
         feedback_ids: [fb_0881]
   ↓ 학습 신호
rubric_copywriting_v2에 "브랜드 톤 적합성" 축이 누락됨
   ↓
Rubric 개정 후보 등록
```

**자동 평가가 틀렸다는 사실이 가장 값진 데이터다.** `eva_512`를 지우지 않는 이유다.

### 10.3 예시 3 — Goal 변경 성분 분리

```
Feedback 원문: "이번엔 학부모 말고 학생 대상으로 써줘"
  ↓ §9.1
① audience 변경 언급 감지
② goal_change_extracted: { field: "audience", from: "학부모", to: "학생" }
③ 잔여 평가 성분: 없음 (방향 전환만)
   → weight 0. Claude의 copywriting 점수에 반영하지 않는다
④ Goal 수정 제안 → goal_001의 audience 변경 → Replanning
```

분리하지 않았다면 Claude가 **잘 쓴 카피 때문에 점수가 깎였을 것이다.**

### 10.4 예시 4 — Systemic Feedback과 지연 귀속

```
2026-08-04  out_331 (카피 3종)  → eva_512  goal_alignment 0.87 (추정)
2026-08-18  fb_0902  Systemic: 모집 41 → 63명 (+22)
   ↓ routing: Evaluation (deferred)
eva_690  deferred  supersedes: eva_512
         goal_alignment 0.87 → 0.94 (확정)
         feedback_ids: [fb_0902]
```

**Systemic Feedback이 deferred Evaluation의 트리거다**([e015 §4.1](e015-evaluation.md)). 그런데 +22명이 카피 덕분인지 광고 예산 덕분인지는 여전히 미결이다(§12).

### 10.5 예시 5 — Quarantine

```
2026-09-01  특정 계정에서 30분간 fb 47건 유입
            전부 동일 Resource(claude-5)에 대한 Explicit Negative
   ↓ 오염 검사
이상 빈도 감지 (평소 일 평균 3건)
   ↓
47건 전부 Quarantined (INV-F-05)
   ↓
이미 반영된 12건 → 재집계로 롤백
   ↓
운영자 알림 + provenance.actor 조사
```

`provenance`가 없었다면(Rule F-005 위반) 어느 신호를 되돌려야 할지 알 수 없었을 것이다.

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **Feedback이 영영 오지 않음** | 정상이다. Evaluation은 `satisfaction: null`로 진행한다([e015 §11](e015-evaluation.md)). **null을 0으로 대체하지 않는다** — 불만족과 무응답은 다르다 |
| **상충하는 Feedback** | 집계한다(§10.1). 다수결이 아니라 가중 합산이며, 결과가 애매하면 판정을 보류하고 deferred Evaluation을 예약한다 |
| **해석이 틀렸음이 나중에 밝혀짐** | `signal`은 그대로 두고(INV-F-02) `interpretation`을 갱신한 새 Feedback을 만든다. 해석 규칙의 오류율 자체가 학습 대상이다(§12) |
| **Implicit 신호가 노이즈** | `weight`가 이미 낮다(0.4). 추가로 `interpretation.confidence`가 곱해지므로 실효 가중치는 더 낮다 |
| **Explicit Feedback을 강요하면** | UX가 나빠진다. Implicit 신호 품질을 올리는 쪽이 우선이다(§12) |
| **Goal 변경과 불만이 모두 섞임** | 둘 다 처리한다(§9.1 ③). 잔여 평가 성분만 Feedback으로 유지하고 변경 성분은 Goal로 보낸다 |
| **Policy 위반 신고** | Rule F-003의 유일한 예외다. 집계를 기다리지 않고 즉시 [Policy](e019-policy.md) 검사를 트리거한다. 안전 문제는 통계를 기다릴 수 없다 |
| **이미 Archived된 Outcome에 Feedback 도착** | 정상 저장한다. 지연 지표는 몇 주 뒤에 온다. Outcome을 되살리지 않고 새 deferred Evaluation을 만든다 |
| **Feedback 대상이 Superseded된 Evaluation** | 최신 Evaluation으로 재라우팅한다. Superseded 체인의 끝을 따라간다 |

---

## 12. Open Issues (v2.0)

### ✅ v1.0에서 해소된 항목

| v1.0 Open Issue | 해소 |
|---|---|
| Feedback이 Learning으로 직행하는 흐름 | [Evaluation](e015-evaluation.md) Entity 신설. Feedback → Evaluation → Memory 경로 확정 (§1.1) |
| Outcome을 Runtime State로 분류 | [Outcome](e014-outcome.md)은 Entity 014로 정정 |
| Feedback → Routing 규칙표 | §7.1에서 7개 유형으로 열거. 완전 열거는 미결 |

### 지연된 Feedback의 귀속 (Attribution)

`2주 후 상담 신청 +30%`는 어느 Decision 덕분인가? 그 사이에 카피 수정, 예산 변경, 계절 요인이 섞여 있다. [Outcome §12](e014-outcome.md)의 기여도 귀속 문제와 **같은 문제다** — 배분 모델(Last-touch / Linear / Shapley)이 정해지지 않았다. v2.0은 시간창 기반의 약한 귀속 + 낮은 가중치로 처리한다.

### Implicit Feedback 해석 규칙의 검증

`재생성 3회 = 불만족`이라는 해석 규칙 자체가 학습·검증 대상이다. 이 규칙을 [Knowledge](e011-knowledge.md)로 취급하면 반증 조건과 confidence를 갖게 되어 자기 교정이 가능해진다. 결정이 필요하다.

### Feedback 조작 (Poisoning)

악의적 사용자가 특정 Resource를 반복적으로 낮게 평가하면 Global Knowledge가 오염될 수 있다. §10.5의 Quarantine 휴리스틱(이상 빈도)은 예시일 뿐 형식 정의가 없다.

### 집계 함수의 형식 정의

§10.1의 가중 합산은 예시다. Source Type별 가중 평균인가 베이지안 갱신인가. [Knowledge §12](e011-knowledge.md)·[Resource Profile §12](e025-resource-profile.md)의 confidence 산출과 **같은 공식 계열을 써야 한다.**

### 앞으로 보강해야 할 항목

- 집계 함수 확정 (Knowledge·Profile과 공유)
- Goal 변경 성분 분리 알고리즘의 상세화
- Feedback → Routing 규칙표의 완전 열거
- 실제 예시 30~50개
