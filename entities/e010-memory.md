# Entity 010: Memory

- **Version:** v2.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Memory is a persisted record of an experience — a decision, an execution, and how it turned out — that the system can later recall.**

> Memory는 시스템이 나중에 회상할 수 있도록 영속화된 경험의 기록이다. 결정, 실행, 그리고 그것이 어떻게 되었는가가 그 대상이다.

여기서 중요한 단어는 **Record**이다.

Memory는 "기억하는 행위"가 아니라 **저장되어 존재하는 기록 단위**이다.

### 1.1 Memory는 어디서 오는가

```
Decision 009 ──▶ Execution 013 ──▶ Outcome 014 ──▶ Evaluation 015
                                                         │
                                                         ▼
                                                    Memory 010
                                                         │ 패턴 추출 + 검증
                                                         ▼
                                                   Knowledge 011
```

> **v1.0 정정:** v1.0은 "Outcome(Runtime State)이 영속화되면 Memory가 된다"고 서술했다. **Outcome은 Runtime State가 아니라 Entity 014다**([e000a §1](e000a-entity-relationships.md)). 그리고 Memory의 직접 입력은 Outcome이 아니라 **[Evaluation](e015-evaluation.md)** 이다 — 무엇이 좋은 결과였는지 판정되지 않은 기록은 학습 재료가 되지 못한다.

| 분류 | 예 | 설명 |
|---|---|---|
| **Process** | Learning | 경험을 읽고 일반화하는 **수행 과정** |
| **Entity** | Outcome (014) | 실행이 낳은 **측정 기록** |
| **Entity** | Evaluation (015) | 그 결과에 대한 **판정** |
| **Entity** | **Memory** (010) | 판정까지 포함해 영속화된 **경험 기록** |

---

## 2. Memory는 무엇이 아닌가?

이게 정의보다 훨씬 중요하다.

### Memory는 Learning이 아니다

❌ `과거 실행에서 패턴을 추출하기` — 이건 **Learning(Process)** 이다.

Memory는 Learning이 읽는 **재료**다. 재료와 요리는 다르다.

### Memory는 Outcome이 아니다

❌ `카피 3종 생성, 0.42 USD, 1,820ms` — 이건 [Outcome](e014-outcome.md)이다.

| | Outcome | Memory |
|---|---|---|
| 범위 | 한 번의 실행 | 상황·행동·결과·판정을 묶은 경험 |
| 판정 | 없음 (측정만) | 포함 |
| 목적 | 감사·정산 | **회상(Recall)** |
| 회상 통계 | 없음 | `recall_count`, `last_recalled_at` |

Outcome이 맥락(어떤 Goal, 어떤 Decision, 어떤 Resource)·판정과 함께 묶여야 Memory가 된다.

### Memory는 Context가 아니다

❌ `현재 등록자 20명` — 이건 [Context](e003-context.md)다.

**Context는 Memory에서 선별해 로드한 현재 추론용 스냅샷이다**([e003 §2](e003-context.md)). Memory는 저장소, Context는 그 위의 뷰다.

### Memory는 Artifact가 아니다

❌ `광고 카피 3종 텍스트` — 이건 [Artifact](e016-artifact.md)다.

| | Artifact | Memory |
|---|---|---|
| 소비자 | 사람 / 외부 시스템 | Decision Engine |
| 내용 | 결과물 자체 | 결과물이 나온 경위와 판정 |

Memory는 Artifact를 참조할 수는 있지만 담지 않는다.

### Memory는 LLM의 컨텍스트 윈도우가 아니다

❌ `대화 중 모델이 잠시 기억하는 내용` — 이건 [Session](e021-session.md)의 대화 버퍼이며 Session이 끝나면 사라진다.

Memory는 **Session과 모델에 독립적으로 존재하는 시스템의 자산**이다. Claude를 GPT로 교체해도 Memory는 남는다([INV-16](e000a-entity-relationships.md), Principle 03 — Resource Agnostic).

### Memory는 Knowledge가 아니다

❌ `교육 마케팅 카피에는 Claude 계열이 적합하다` — 이건 일반화된 앎, 즉 [Knowledge](e011-knowledge.md)다.

Memory는 **개별 사례**다. `2026-08-04, 윈터캠프 광고 카피, Claude 선택, 상담 30% 증가` — 이것이 Memory다.

### Memory는 Log가 아니다

시스템 Log는 디버깅용 원시 기록이며 [Execution](e013-execution.md)의 `logs_ref`에 있다. Memory는 **회상을 전제로 구조화된 기록**이며 Goal·Decision·Outcome·Evaluation이 연결되어 있어야 한다.

---

## 3. Design Principles

### Rule M-001 — 맥락 없는 결과는 Memory가 될 수 없다

[Volume 5 Principle 02](../v5-learning-engine.md) 그대로다. 저장해야 하는 것은 결과물이 아니라 **"왜 이 선택을 했고, 결과가 어땠는가"** 이다.

❌ 나쁜 Memory:

```
사용자에게 광고 문구 제공
```

✅ 좋은 Memory:

```
Goal:              윈터캠프 학생 100명 모집
Situation:         한국 학부모 대상, 겨울 모집 시즌, 예산 300만원
Action:            Claude 선택 (Utility 0.91), 감성 소구 전략
Result:            상담 신청 30% 증가
Evaluation:        quality 0.93 / decision_quality 0.90 / verdict accept
Confidence:        0.92
```

### Rule M-002 — Memory는 사후에 수정하지 않는다

Memory는 "그때 실제로 일어난 일"의 기록이다. 내용이 틀렸다면 수정하는 것이 아니라 **정정 Memory를 새로 기록**하고 원본과 연결한다. 기록을 덮어쓰면 Learning의 근거가 오염된다([INV-06](e000a-entity-relationships.md)).

### Rule M-003 — 모든 Memory는 출처(Provenance)를 가진다

어떤 Execution, 어떤 Decision, 어떤 Evaluation에서 나왔는지 추적 가능해야 한다. 출처 없는 Memory는 검증할 수 없고, 검증할 수 없는 Memory는 [Knowledge](e011-knowledge.md)로 승격될 수 없다.

### Rule M-004 — Memory는 Scope를 가진다

특정 사용자의 경험을 다른 사용자의 Decision에 함부로 사용하면 안 된다(§4.2).

### Rule M-005 — 단일 Memory는 시스템을 바꾸지 못한다

`Single Memory ≠ Learning Update`. 한 건의 기록만으로 [Resource Profile](e025-resource-profile.md)이나 [Knowledge](e011-knowledge.md)를 갱신하지 않는다([Volume 5 §13](../v5-learning-engine.md), [INV-RPF-07](e025-resource-profile.md)의 3-윈도우 규칙과 같은 원칙).

### Rule M-006 — 실패도 기록한다

성공한 경험만 저장하면 Learning이 편향된다. **실패한 Execution과 `reject` 판정을 받은 Evaluation도 Memory가 된다.** 실패 사례가 없으면 "무엇을 피해야 하는가"를 배울 수 없다.

### Rule M-007 — 결정 품질과 결과 품질을 함께 보존한다

[Evaluation](e015-evaluation.md)이 분리 판정한 `decision_quality`와 `outcome_quality`를 둘 다 담는다. 결과만 저장하면 **"좋은 결정, 나쁜 운"** 사례에서 시스템이 잘못 학습한다([Rule EVA-004](e015-evaluation.md)).

---

## 4. Attributes

```
Memory
├── Identity
│   ├── memory_id
│   ├── memory_type
│   └── scope
├── Provenance
│   ├── goal_ref
│   ├── decision_ref
│   ├── execution_ref
│   └── evaluation_ref
├── Content
│   ├── situation
│   ├── action
│   └── result
├── Quality
│   ├── outcome_quality
│   ├── decision_quality
│   └── confidence
├── Recall
│   ├── recall_count
│   └── last_recalled_at
└── Status
    ├── status
    ├── created_at
    └── corrects
```

| 속성 | 의미 | 예 |
|---|---|---|
| **memory_id** | 고유 식별자 | `mem_0142` |
| **memory_type** | Episodic / Semantic / Procedural (§4.1) | `Episodic` |
| **scope** | 적용 범위 (§4.2) | `User-level` |
| **goal_ref** | 어떤 Goal 아래의 경험인가 | `goal_001` |
| **decision_ref** | 어떤 Decision의 결과인가 | `dec_101` |
| **execution_ref** | 어떤 실행인가 (Rule M-003) | `exe_220` |
| **evaluation_ref** | 어떤 판정인가 | `eva_512` |
| **situation** | 상황 | `윈터캠프 광고 카피 작성, 예비 고3 학부모 대상` |
| **action** | 행동 | `Claude 선택 (Utility 0.91), 감성 소구 전략` |
| **result** | 결과 | `상담 신청 30% 증가` |
| **outcome_quality** | 결과 품질 (Rule M-007) | `0.93` |
| **decision_quality** | 결정 품질 (Rule M-007) | `0.90` |
| **confidence** | 이 기록의 신뢰도 | `0.92` |
| **recall_count** | 회상된 횟수 | `7` |
| **last_recalled_at** | 마지막 회상 시각 | `2026-08-03T09:12:00Z` |
| **status** | 생명주기 상태 (§6) | `Active` |
| **corrects** | 정정 대상 Memory (Rule M-002) | `null` |

**`recall_count`는 의외로 중요하다.** 자주 회상되고 결과가 좋았던 Memory는 [Knowledge](e011-knowledge.md) 승격의 1차 후보가 된다.

### 4.1 Memory Types

모든 Memory는 정확히 하나의 Type을 가진다.

```
Memory
├── Episodic Memory   — 개별 실행의 기록
├── Semantic Memory   — 반복 관찰로 굳어진 사실
└── Procedural Memory — 성공한 절차·전략의 기록
```

| Type | 무엇을 기록하는가 | 예 |
|---|---|---|
| **Episodic** | 특정 시점의 개별 사건 | `2026-08-04, 윈터캠프 광고, Claude 사용, 상담 30% 증가` |
| **Semantic** | 반복 관찰로 굳어진 사실 | `이 사용자는 상세한 결과물을 선호한다` |
| **Procedural** | 성공했던 절차/전략 | `학원 모집: 조사 → 카피 → 파일럿 → 본 집행 순서가 효과적` |

세 Type의 관계:

```
Episodic (사건 1건)
   ↓ 반복 관찰
Semantic (사실)          Procedural (절차)
   ↓ 검증                     ↓ 검증
Knowledge 011로 승격      Workflow 022로 승격
```

**Procedural Memory의 승격지는 두 곳이다.** 일반 법칙이면 [Knowledge](e011-knowledge.md)로, 재사용 가능한 실행 순서면 [Workflow](e022-workflow.md)로 간다([e022 §7.1](e022-workflow.md)).

Semantic Memory와 Knowledge의 차이에 주의한다. Semantic Memory는 **아직 검증 전의 일반화 후보**이고, 검증을 통과해야 Knowledge가 된다.

### 4.2 Memory Scope

| Scope | 의미 | 예 |
|---|---|---|
| **Goal-level** | 특정 Goal 안에서만 유효 | `이번 윈터캠프에서는 인스타 광고 반응이 좋았다` |
| **User-level** | 특정 사용자에게만 유효 | `이 학원 대표는 속도보다 품질을 선호한다` |
| **Global** | 익명화되어 전체 시스템에 유효 | `교육 마케팅 카피 작업의 평균 만족도 데이터` |

#### Scope 규칙

1. Memory는 생성 시 **가장 좁은 Scope**로 시작한다(기본: Goal-level).
2. Scope 확장(Goal → User → Global)은 자동으로 일어나지 않는다. 패턴 검증과 **익명화**를 거쳐야 한다.
3. User-level Memory를 Global로 올릴 때 개인 식별 정보는 제거되어야 한다([Policy](e019-policy.md)의 `privacy` 유형이 강제).

---

## 5. Invariants

### INV-M-01 — Memory는 불변이다

| | |
|---|---|
| **위반 시** | 저장 계층이 쓰기를 거부한다. 정정은 새 Memory + `corrects` 링크로만 (Rule M-002) |
| **허용되는 변경** | `recall_count`, `last_recalled_at`, `status`, `confidence`(감쇠)만 |

### INV-M-02 — 모든 Memory는 출처 사슬을 갖는다

`execution_ref`를 따라가면 Decision → Task → Goal에 도달해야 한다.

| | |
|---|---|
| **위반 시** | 생성 거부. 출처 없는 Memory는 Knowledge 승격 자격이 없다 (Rule M-003) |

### INV-M-03 — 단일 Memory가 Knowledge나 Profile을 갱신할 수 없다

| | |
|---|---|
| **위반 시** | 갱신을 차단한다. 최소 근거 수(도메인별, 기본 5건)를 요구한다 (Rule M-005) |
| **근거** | 한 번의 우연으로 시스템 전체가 흔들리면 안 된다 |

### INV-M-04 — Scope 확장 시 개인 식별 정보가 제거된다

| | |
|---|---|
| **위반 시** | 확장을 차단하고 `policy.violated` Event를 발행한다 |

### INV-M-05 — 하위 Scope Memory를 다른 사용자의 Decision에 사용할 수 없다

| | |
|---|---|
| **위반 시** | 회상 결과에서 제외한다. Scope 필터는 Recall의 첫 단계다 (§9.2) |

### INV-M-06 — Decay는 confidence만 낮추고 기록을 지우지 않는다

| | |
|---|---|
| **위반 시** | 삭제 차단. 낡은 경험도 "그때는 그랬다"는 사실이다 |
| **예외** | 사용자의 명시적 삭제 요구 (§12) |

### INV-M-07 — 실패 Memory를 선택적으로 누락할 수 없다

| | |
|---|---|
| **위반 시** | 저장 파이프라인의 결함이다. 성공률 통계가 실제보다 높게 계산된다 (Rule M-006, [INV-04](e000a-entity-relationships.md)와 같은 원칙) |

---

## 6. Lifecycle

```
Created → Active → Decaying → Dormant → (Expired | Archived | Deleted)
             │
             └──▶ Promoted   (Knowledge / Workflow 생성에 기여)
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Created** | Evaluation 완료 후 영속화된 직후 | `evaluation.completed` |
| **Active** | 회상 대상. Decision·Learning이 참조 | 검증 통과 |
| **Decaying** | 신뢰도 감쇠 진행 중. 참조 시 가중치 하락 | 시간 경과 또는 모순 발생 |
| **Dormant** | 신뢰도가 임계값 이하. 기본 회상에서 제외 | Effective Confidence < 임계 |
| **Promoted** | 패턴 검증을 거쳐 Knowledge/Workflow 생성에 기여함 | 승격 |
| **Expired** | 유효기간 만료 (특정 모델 버전에 종속된 기록 등) | 만료 정책 |
| **Archived** | 보존은 하되 회상 불가 | 보존 정책 |
| **Deleted** | 사용자 요구 등으로 완전 삭제 | 삭제 요청 (§12) |

### 6.1 Retention & Decay

오래된 경험은 현재를 덜 대표한다. AI 생태계는 빠르게 변하기 때문이다.

$$Effective\ Confidence = Confidence \times DecayFactor(age, domain)$$

- 감쇠 속도는 **도메인에 따라 다르다.** `Claude가 카피라이팅에 강했다`는 모델 세대가 바뀌면 빠르게 낡는다. 반면 `이 사용자는 품질을 선호한다`는 천천히 낡는다.
- **Decay는 삭제가 아니다**(INV-M-06). 신뢰 가중치만 낮아지고 기록은 남는다.
- 새 Memory가 낡은 Memory와 모순되면 낡은 쪽의 Decay가 가속된다. 이는 [Resource Profile의 Drift 감지](e025-resource-profile.md)와 연결된다.

예)

```
mem_0031 (2025-11): "GPT가 코딩 Task에서 최고 성능"
  ↓ 새 모델 출시 + 모순되는 Memory 다수 발생
Effective Confidence: 0.90 → 0.41
  ↓
Status: Decaying → Dormant
```

Decay 계수는 [Resource Profile](e025-resource-profile.md)의 `decay_lambda`와 같은 축을 쓴다 — **두 곳에서 다른 감쇠율을 쓰면 Profile 점수와 Memory 회상이 어긋난다.**

---

## 7. Relationships

```
Decision 009 ──▶ Execution 013 ──▶ Outcome 014 ──▶ Evaluation 015
                                                        │
Feedback 012 ──────────────────────────────────────────┤
                                                        ▼
                                                   Memory 010
                                                    │      │
                              패턴 추출 + 검증 ──────┘      └──▶ Context 003 (선별 로드)
                                    ▼
                            Knowledge 011 / Workflow 022
                                    │
                                    └──개선──▶ Decision 009
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Evaluation](e015-evaluation.md) | Memory의 직접 입력. 판정 없는 기록은 학습 재료가 아니다 | `Evaluation 1:0..N Memory` |
| [Decision](e009-decision.md) | Memory는 Decision의 근거와 결과를 기록한다 | `Decision 1:0..N Memory` |
| [Execution](e013-execution.md) | 출처 사슬의 시작점 | `Execution 1:0..N Memory` |
| [Goal](e001-goal.md) | 모든 Memory는 특정 Goal의 맥락에서 생성된다 | `Goal 1:0..N Memory` |
| [Knowledge](e011-knowledge.md) | 여러 Memory가 하나의 Knowledge로 승격된다 | `Memory N:1 Knowledge` |
| [Workflow](e022-workflow.md) | Procedural Memory가 Workflow로 승격될 수 있다 | `Memory N:0..1 Workflow` |
| [Context](e003-context.md) | Context는 Memory에서 로드된 스냅샷이다 | `Memory 1:0..N Context` |
| [Feedback](e012-feedback.md) | Feedback이 Evaluation을 거쳐 Memory에 반영된다 | `Feedback N:M Memory` (Evaluation 경유) |
| [Resource Profile](e025-resource-profile.md) | Profile은 Memory 집합에서 계산되지 않고 **Evaluation에서 직접 갱신된다** | 병렬 소비자 |
| [Session](e021-session.md) | Session 종료 요약이 Memory가 된다 | `Session 1:0..N Memory` |
| [Risk](e018-risk.md) | Materialized Risk 이력이 확률 추정을 보정한다 | `Risk 1:0..N Memory` |

> **주의:** [Resource Profile](e025-resource-profile.md)은 Memory를 거치지 않고 [Evaluation](e015-evaluation.md)에서 직접 갱신된다. Memory와 Profile은 **같은 원천을 소비하는 두 소비자**이지 순차 관계가 아니다.

Learning Engine 관점의 전체 흐름은 [Volume 5](../v5-learning-engine.md), World 수준의 장기 기억은 [Volume 4-F §20](../v4f-world-model.md)을 참조한다.

---

## 8. Canonical Representation

```json
{
  "memory_id": "mem_0142",
  "memory_type": "Episodic",
  "scope": "Goal-level",
  "goal_ref": "goal_001",
  "decision_ref": "dec_101",
  "execution_ref": "exe_220",
  "evaluation_ref": "eva_512",
  "content": {
    "situation": "윈터캠프 광고 카피 작성, 예비 고3 학부모 대상, 예산 300만원, 겨울 모집 시즌",
    "action": "Claude 선택 (Utility 0.91, 후보 4개 중 1위), 감성 소구 + 내신 관리 언급 전략",
    "result": "카피 3종 산출, 인간 검수 통과, 랜딩 유입 중 61% 기여, 상담 신청 30% 증가"
  },
  "outcome_quality": 0.93,
  "decision_quality": 0.90,
  "confidence": 0.92,
  "recall_count": 7,
  "last_recalled_at": "2026-08-18T09:12:00Z",
  "created_at": "2026-08-04T09:31:20Z",
  "corrects": null,
  "status": "Active"
}
```

실패 경험도 같은 구조로 기록된다(Rule M-006).

```json
{
  "memory_id": "mem_0138",
  "memory_type": "Episodic",
  "scope": "Goal-level",
  "goal_ref": "goal_001",
  "decision_ref": "dec_100",
  "execution_ref": "exe_219",
  "evaluation_ref": "eva_505",
  "content": {
    "situation": "윈터캠프 광고 카피 작성, 예비 고3 학부모 대상",
    "action": "GPT 선택 (Utility 0.88). 당시 inputs_snapshot에 rate limit 징후 없음",
    "result": "429 Too Many Requests로 실패. 0.11 USD 손실, 31초 지연"
  },
  "outcome_quality": 0.0,
  "decision_quality": 0.85,
  "confidence": 0.95,
  "recall_count": 3,
  "created_at": "2026-08-04T09:13:00Z",
  "corrects": null,
  "status": "Active"
}
```

**`outcome_quality` 0.0인데 `decision_quality` 0.85다.** 이 두 값을 함께 저장하는 것이 Rule M-007의 목적이다. 결과만 저장했다면 시스템은 "GPT는 나쁘다"고 잘못 학습했을 것이다.

**이 구조만 Learning Engine으로 전달된다.**

기계가 읽을 수 있는 스키마: [`memory.schema.json`](../intent-os-spec/schemas/memory.schema.json)

---

## 9. Validation Rules

### 9.1 저장 (Memorization)

```
evaluation.completed Event 수신
  ↓
Evaluation.status = Skipped ? ── Yes → 저장하지 않음 (판정이 없다)
  ↓
맥락 수집 (Goal / Decision / Execution / Outcome / Context 스냅샷)
  ↓
Rule M-001 검증 (맥락 완전성)
  situation / action / result 중 하나라도 비면 반려
  ↓
출처 사슬 검증 (INV-M-02)
  execution_ref → decision_ref → task → goal 도달 확인
  ↓
outcome_quality / decision_quality 양쪽 존재 확인 (Rule M-007)
  ↓
Memory Type 분류 (§4.1)
  ↓
Scope 결정 (기본: Goal-level, INV-M-05)
  ↓
중복/모순 검사
  ├── 중복 → 기존 Memory의 confidence 강화
  └── 모순 → 양쪽 모두 보존 + 모순 관계 기록 (§11)
  ↓
저장 → 동결 (INV-M-01) → Event 발행 (memory.created)
  ↓
후속 트리거
  ├── Knowledge 승격 후보 검사 → e011 §9
  └── Procedural 패턴이면 Workflow 후보 검사 → e022 §7.1
```

**Evaluation이 없으면 Memory를 만들지 않는다.** 판정되지 않은 기록은 회상해도 쓸모가 없다.

### 9.2 회상 (Recall)

```
질의 (예: "교육 마케팅 + 학부모 대상 + 카피 작성")
  ↓
Scope 필터 (INV-M-05) — 현재 사용자/Goal 범위 밖 제외
  ↓
유사 상황(Situation) 검색
  ↓
Effective Confidence 계산 (§6.1 Decay 반영)
  ↓
Dormant / Expired / Archived 제외
  ↓
상위 N개 반환 → Decision Engine / Planner
  ↓
recall_count, last_recalled_at 갱신 (INV-M-01의 허용 변경)
```

회상은 검색이 아니라 **의사결정 지원**이다. 반환 기준은 "비슷한 문자열"이 아니라 **"비슷한 상황(Situation)"** 이다.

---

## 10. Examples

### 10.1 예시 1 — 성공 경험의 회상

```
2026-08-04  mem_0142 생성 (윈터캠프 카피, Claude, quality 0.93)
   ↓
2027-01-10  새 Goal: "봄학기 특강 학생 40명 모집"
   ↓ Recall 질의: 교육 마케팅 + 학부모 + 카피
mem_0142 반환 (Effective Confidence 0.92 × Decay 0.71 = 0.65)
   ↓
Decision Engine: Claude의 이 Context 점수에 사전확률로 반영
recall_count 7 → 8
```

**5개월이 지나 감쇠했지만 여전히 유효하다.** 삭제했다면 이 정보가 사라졌을 것이다.

### 10.2 예시 2 — 실패 경험이 막은 반복

```
mem_0138 (GPT rate limit 실패, decision_quality 0.85)
   ↓ 같은 유형 Memory가 4건 더 누적
Semantic Memory 후보: "GPT는 오전 9시대 한국 리전에서 rate limit 빈발"
   ↓ Knowledge 승격 (e011 §9)
knw_0033: "09:00-10:00 KST 구간에서 GPT 선택 시 가용성 리스크 상향"
   ↓
이후 Decision의 inputs_snapshot에 시간대별 가용성 지표가 추가됨
```

**실패를 기록하지 않았다면(Rule M-006 위반) 같은 실패를 반복했을 것이다.**

### 10.3 예시 3 — Procedural Memory → Workflow

```
동일 Goal 유형 12건에서 반복 관찰된 순서
  조사 → 타겟 분석 → 카피 → 검수 → 파일럿 → 본 집행
   ↓ Procedural Memory 12건 누적
   ↓ 패턴 검증: 파일럿 선행 시 실패율 62% 감소
   ↓
know_090 (Knowledge) 생성
   ↓
wf_seasonal_campaign v1.0 (Workflow) 자동 제안 → 사람 검토 → Published
   ↓
Memory 12건 → status: Promoted
```

### 10.4 예시 4 — 모순되는 Memory

```
mem_0142 (2026-08)  "Claude, 교육 카피, quality 0.93"
mem_0301 (2026-09)  "Claude, 교육 카피, quality 0.61"   ← 모순
   ↓ 단순 평균 금지 (§12)
Context 차이 탐색
   ↓ 발견: mem_0301은 Claude 5.1 배포 후
   ↓
두 Memory 모두 보존. Context 축에 model_version 추가
mem_0142 → Decaying 가속
Resource Profile의 Drift 확정과 연동 (e025 §9.2)
```

**평균 내면 0.77이라는 존재하지 않는 값이 나온다.** 모순은 대개 숨은 Context 축의 신호다.

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **Evaluation이 `Skipped`** | Memory를 만들지 않는다(§9.1). 저영향 Task의 평가 생략은 정상이며, 학습 재료가 되지 않을 뿐이다 |
| **같은 상황에서 상반된 결과** | 양쪽 모두 보존한다. 평균 내지 않는다(§10.4). Context 차이를 찾는 것이 올바른 대응이다 |
| **Memory가 폭증** | 저장·회상 비용이 커진다. 선별 기준(놀라움 정도, Goal 중요도, 실패 여부)이 필요하다(§12). **다만 실패를 먼저 버리면 안 된다**(INV-M-07) |
| **Dormant Memory가 다시 유효해짐** | 되살리지 않고 새 Memory를 기록한다. 상황이 바뀐 것이므로 새 경험이다 |
| **User-level Memory를 다른 사용자가 참조** | 차단한다(INV-M-05). Global로 올리려면 익명화 검증을 거쳐야 한다(INV-M-04) |
| **Memory 삭제 요청인데 Knowledge에 기여함** | §12의 미결 항목이다. v2.0 기본안은 원본 삭제 + Knowledge의 `evidence_count` 차감 + 임계값 미달 시 Knowledge 재검증이다 |
| **Session 종료 요약 Memory** | `memory_type: Semantic`, `scope: Goal-level`로 기록한다. Execution 하나에 대응하지 않으므로 `execution_ref`가 없을 수 있다 — **INV-M-02의 유일한 예외**이며 `goal_ref`는 필수다 |
| **정정 Memory가 또 틀림** | 정정의 정정을 만든다. `corrects` 체인은 순환하지 않아야 하며, 깊이가 3을 넘으면 원본 판정 절차에 결함이 있다는 신호다 |
| **recall_count가 0인 Memory** | 정상이다. 아직 유사 상황이 없었을 뿐이다. 삭제 기준으로 쓰지 않는다 — 드문 상황일수록 값진 기록이다 |

---

## 12. Open Issues (v2.0)

### ✅ v1.0에서 해소된 항목

| v1.0 Open Issue | 해소 |
|---|---|
| Outcome을 Runtime State로 분류 | [Outcome](e014-outcome.md)은 Entity 014로 정정. Memory의 직접 입력은 [Evaluation](e015-evaluation.md)임을 확정 |
| 결과만 저장할 때의 학습 편향 | Rule M-007 — `decision_quality`와 `outcome_quality`를 함께 보존 |
| Procedural Memory의 승격지 | Knowledge 또는 [Workflow](e022-workflow.md) 두 경로로 확정 |

### 사용자의 삭제 권리 (Right to be Forgotten)

Memory는 사용자의 데이터다. 사용자가 삭제를 요구하면 시스템은 지워야 한다. 문제는 **이미 Knowledge로 승격된 경우**다.

```
mem_0142 (삭제 요청됨)
  ↓ 이미 기여함
knw_0007 "교육 마케팅 → Claude 적합"
```

Memory를 지우면 Knowledge의 근거가 사라진다. v2.0 기본안은 **원본 삭제 + `evidence_count` 차감 + 임계값 미달 시 재검증**이지만 확정하지 않았다. [Artifact §12](e016-artifact.md), [e000a §10](e000a-entity-relationships.md)과 같은 문제다.

### Memory 저장 비용과 선별 기준

모든 Evaluation을 저장하면 저장소와 회상 비용이 폭발한다. "기록할 가치가 있는 경험"의 기준(놀라움 정도 = 예측과 실측의 차이, Goal 중요도, 실패 여부)이 필요하다. `prediction_error`가 큰 경험이 가장 값지다는 것이 유력한 가설이다.

### 모순되는 Memory의 병합

§10.4처럼 Context 차이를 찾아 분기하는 알고리즘이 필요하다. 현재는 "평균 내지 말라"는 원칙만 있다.

### Decay 계수의 단일화

§6.1은 [Resource Profile](e025-resource-profile.md)의 `decay_lambda`와 같은 축을 쓴다고 서술했으나, 두 값을 실제로 공유하는 메커니즘이 정의되지 않았다. 어긋나면 Profile 점수와 Memory 회상이 서로 다른 시간관을 갖게 된다.

### 앞으로 보강해야 할 항목

- Situation Similarity 계산 명세
- Scope 승격 시 익명화 규칙의 형식 정의
- Decay Factor의 도메인별 파라미터 표
- 실제 예시 30~50개
