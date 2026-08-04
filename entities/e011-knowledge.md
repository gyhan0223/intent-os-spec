# Entity 011: Knowledge

- **Version:** v2.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Knowledge is a validated generalization derived from multiple memories, which the system uses to make better decisions.**

> Knowledge는 여러 Memory로부터 도출되어 검증을 통과한 일반화이며, 시스템이 더 나은 결정을 내리는 데 사용된다.

여기서 중요한 단어는 **Validated Generalization**이다.

일반화되지 않은 것은 [Memory](e010-memory.md)이고, 검증되지 않은 것은 가설일 뿐이다. **둘 다 통과해야 Knowledge다.**

### 1.1 Learning의 입력과 출력

| 분류 | 예 | 설명 |
|---|---|---|
| **Process** | Learning | Memory를 읽어 Knowledge를 만드는 **수행 과정** |
| **Entity** | [Memory](e010-memory.md) | Learning이 읽는 **개별 사례 기록** |
| **Entity** | **Knowledge** | Learning이 쓰는 **일반화된 산출물** |

```
Memory (개별 사례들)
   ↓
Learning (Process)
   ↓
Knowledge (일반화된 앎)
   ↓
Decision Engine / Planner (소비자)
```

Knowledge는 만들어진 뒤 Process와 독립적으로 **존재**하며, Decision Engine과 Planner가 읽는다.

---

## 2. Knowledge는 무엇이 아닌가?

이게 정의보다 훨씬 중요하다.

### Knowledge는 Memory가 아니다

❌ `2026-08-04, 윈터캠프 광고, Claude 사용, 상담 30% 증가` — 이건 **개별 사례**([Memory](e010-memory.md))다.

✅ `교육 마케팅 + 한국어 감성 카피 → Claude 계열 Resource 높은 적합도` — 이것이 Knowledge다.

| | Memory | Knowledge |
|---|---|---|
| 성격 | 사례 (Instance) | 일반화 (Generalization) |
| 개수 | 사건마다 1건 | 패턴마다 1건 |
| 시제 | "그때 그랬다" | "이런 상황에서는 대체로 이렇다" |
| 검증 | 불필요 (사실 기록) | **필수** |
| 반증 | 해당 없음 | **가능해야 한다** |

### Knowledge는 Assumption이 아니다

❌ `광고비 300만원이 12월까지 유지된다` — 이건 [Assumption](e017-assumption.md)이다.

| | Knowledge | Assumption |
|---|---|---|
| 근거 | 축적된 경험 (N ≥ 5) | 없음. 믿기로 한 것 |
| 대상 | 일반 경향 | 특정 Goal의 전제 |
| 시제 | "대체로 이렇다" | "앞으로 이럴 것이다" |
| 틀렸을 때 | Confidence 하향 → 재검증 | **Replanning** |

**둘 다 반증 조건을 갖는다는 점은 같다.** 차이는 근거의 유무와 파급 범위다.

### Knowledge는 Constraint가 아니다

❌ `예산 300만원 초과 금지` — 이건 [Constraint](e004-constraint.md)다.

Constraint는 위반하면 안 되는 **강제 규칙**이고, Knowledge는 **확률적 경향**이다. Knowledge는 언제나 반증될 수 있고, Constraint는 반증되지 않는다 — 완화될 뿐이다.

### Knowledge는 Policy가 아니다

❌ `학부모 데이터는 국내 리전 Resource만 사용` — 이건 [Policy](e019-policy.md)다.

Policy는 **금지**하고 Knowledge는 **권고**한다. Policy가 배제한 후보는 Knowledge가 아무리 좋다고 해도 선택될 수 없다([INV-11](e000a-entity-relationships.md)).

### Knowledge는 LLM 내부 지식이 아니다

❌ `Claude가 파라미터 안에 가지고 있는 세상 지식` — 이건 Resource의 속성이다.

Intent OS의 Knowledge는 **시스템이 자기 경험으로 만든, 모델 외부에 존재하는 자산**이다. 모델을 교체해도 남고, 모델은 접근할 수 없는 내용을 담는다. [Volume 5 §1.2](../v5-learning-engine.md): Intent OS는 모델을 학습시키지 않는다. **어떤 상황에서 어떤 Resource를 어떻게 활용해야 성공하는가**를 학습한다.

### Knowledge는 Resource Profile이 아니다

❌ `Claude의 교육/ko 카피 점수 93, 표본 214` — 이건 [Resource Profile](e025-resource-profile.md)이다.

| | Resource Profile | Knowledge |
|---|---|---|
| 대상 | **하나의** Resource의 측정값 | 상황과 전략에 관한 일반 법칙 |
| 형태 | 수치 | 명제 |
| 갱신 | Evaluation마다 자동 | 패턴 검증을 거쳐야 |
| 예 | `copywriting: 93 (conf 0.95)` | `파일럿 선행 시 실패율 62% 감소` |

**Profile은 "누가 잘하는가", Knowledge는 "어떻게 해야 잘 되는가"다.**

### Knowledge는 Learning이 아니다

❌ `패턴을 추출하고 검증하는 것` — 이건 **Process**다. Knowledge는 그 Process의 **산출물(Entity)** 이다.

---

## 3. Design Principles

### Rule K-001 — 복수의 Memory를 근거로 가져야 한다

`Single Memory ≠ Knowledge`. 근거 Memory가 최소 임계값(도메인별 설정, 기본 N ≥ 5) 이상이어야 한다([Rule M-005](e010-memory.md)와 짝을 이룬다).

❌ `어제 Claude가 잘했으니 Claude가 카피에 최적이다` — 사례 1건. Knowledge가 될 수 없다.

### Rule K-002 — 반증 가능해야 한다 (Falsifiable)

Knowledge는 "어떤 새로운 Memory가 나타나면 이 Knowledge가 흔들리는가"를 스스로 정의해야 한다. **반증 조건이 없는 문장은 Knowledge가 아니라 슬로건이다.**

[Assumption Rule ASM-001](e017-assumption.md)과 같은 원칙이다.

### Rule K-003 — Confidence를 가진다

모든 Knowledge는 0~1의 Confidence를 가지며, Decision Engine은 이 값을 가중치로 사용한다. **Confidence 1.0은 존재하지 않는다.**

### Rule K-004 — 근거로 역추적 가능해야 한다

```
Knowledge → 근거 Memory 목록 → Evaluation → Outcome → Execution → Decision → Task → Goal
```

사용자가 *"왜 Claude를 추천했어?"* 라고 물으면 이 사슬로 설명한다([e000a §7](e000a-entity-relationships.md)의 표준 실행 사슬을 역으로 순회).

### Rule K-005 — 적용 조건(Applicability)을 명시해야 한다

`Claude가 좋다`는 Knowledge가 아니다. **어떤 상황에서** 좋은지가 있어야 한다.

✅ `Task: 마케팅 카피 + Audience: 한국 학부모 + Tone: 감성 → Claude 적합도 높음`

적용 조건의 축은 [Resource Profile의 Context 축](e025-resource-profile.md)과 일치해야 한다 — 다르면 Knowledge가 가리키는 상황과 Profile이 측정한 상황이 어긋난다.

### Rule K-006 — 반대 근거를 버리지 않는다

`contradicting_memory_refs`를 함께 보관한다. **반대 근거의 비율이 곧 재검증 트리거**다. 지지 근거만 모으면 확증 편향이 시스템에 구조적으로 박힌다.

### Rule K-007 — Deprecated Knowledge를 삭제하지 않는다

반증된 Knowledge도 이력으로 남긴다. "우리가 한때 이렇게 믿었고 왜 틀렸는가"가 다음 일반화의 재료다.

---

## 4. Attributes

```
Knowledge
├── Identity
│   ├── knowledge_id
│   ├── knowledge_type
│   └── scope
├── Content
│   ├── statement
│   └── applicability
├── Evidence
│   ├── supporting_memory_refs[]
│   ├── contradicting_memory_refs[]
│   └── evidence_count
├── Validation
│   ├── confidence
│   ├── falsification_condition
│   ├── last_validated_at
│   └── expiration_policy
└── Status
    ├── status
    ├── created_at
    └── superseded_by
```

| 속성 | 의미 | 예 |
|---|---|---|
| **knowledge_id** | 고유 식별자 | `knw_0007` |
| **knowledge_type** | Resource / Task / User / Domain (§4.1) | `Resource` |
| **statement** | 일반화 명제 | `교육 마케팅 감성 카피에는 Claude 계열이 적합하다` |
| **applicability** | 적용 조건 (Rule K-005) | `task=marketing_copy, audience=한국 학부모` |
| **confidence** | 신뢰도 (Rule K-003) | `0.91` |
| **supporting_memory_refs** | 지지 근거 | `[mem_0142, mem_0155, …]` |
| **contradicting_memory_refs** | 반대 근거 (Rule K-006) | `[mem_0201]` |
| **evidence_count** | 근거 총수 | `23` |
| **falsification_condition** | 반증 조건 (Rule K-002) | `동일 조건 최근 30건 중 실패 30% 초과` |
| **scope** | User-level / Global | `Global` |
| **last_validated_at** | 마지막 재검증 | `2026-08-03` |
| **expiration_policy** | 만료 정책 | `모델 메이저 업데이트 시 재검증` |
| **status** | 생명주기 상태 (§6) | `Active` |
| **superseded_by** | 대체 Knowledge (Rule K-007) | `null` |

### 4.1 Knowledge Types

[Volume 5 §7](../v5-learning-engine.md)의 4분류를 따른다.

```
Knowledge
├── Resource Knowledge — Resource의 강점/약점/비용
├── Task Knowledge     — Task 유형별 최적 접근
├── User Knowledge     — 사용자별 선호와 패턴
└── Domain Knowledge   — 도메인별 요구사항
```

| Type | 예 | 주 소비자 |
|---|---|---|
| **Resource Knowledge** | `Claude — 한국어 설득 구조 강점, 실시간 검색 약점` | Decision Engine |
| **Task Knowledge** | `시즌 캠페인은 파일럿 선행 시 실패율 62% 감소` | Planner |
| **User Knowledge** | `이 대표는 속도보다 품질을 선호한다` | Goal Engine, Decision Engine |
| **Domain Knowledge** | `교육 마케팅은 학기 시작 6~8주 전 집행이 효과적` | Planner |

**Resource Knowledge와 [Resource Profile](e025-resource-profile.md)의 경계에 주의한다.** 수치는 Profile, 명제는 Knowledge다. `Claude 93점`은 Profile, `Claude는 한국어 설득 구조가 강점`은 Knowledge다.

---

## 5. Invariants

### INV-K-01 — 근거 Memory가 임계값 미만이면 Active가 될 수 없다

| | |
|---|---|
| **위반 시** | `Candidate`로 강등한다. 근거 없는 일반화가 Decision에 반영되면 우연이 법칙으로 굳는다 (Rule K-001) |

### INV-K-02 — falsification_condition이 없으면 생성되지 않는다

| | |
|---|---|
| **위반 시** | 생성 거부. 반증할 수 없는 명제는 검증할 수도 없다 (Rule K-002) |

### INV-K-03 — confidence는 1.0이 될 수 없다

| | |
|---|---|
| **위반 시** | 0.99로 절삭. 확실한 앎은 Knowledge가 아니라 [Constraint](e004-constraint.md)나 [Policy](e019-policy.md)다 |

### INV-K-04 — 모든 Knowledge는 근거로 역추적 가능하다

| | |
|---|---|
| **위반 시** | 설명 요청에 답할 수 없다. 참조가 끊긴 Knowledge는 `Challenged`로 전이하고 재검증한다 (Rule K-004) |

### INV-K-05 — 반대 근거를 삭제할 수 없다

| | |
|---|---|
| **위반 시** | 삭제 차단. 확증 편향이 구조화된다 (Rule K-006) |

### INV-K-06 — Deprecated Knowledge는 Decision에 참조되지 않는다

| | |
|---|---|
| **위반 시** | 반증된 앎이 계속 결정을 왜곡한다. 조회 계층에서 필터링하고 참조 시도를 경보로 기록 |
| **주의** | 참조 금지이지 삭제가 아니다 (Rule K-007) |

### INV-K-07 — Knowledge는 Policy나 Hard Constraint를 이길 수 없다

| | |
|---|---|
| **위반 시** | Knowledge가 아무리 강하게 권고해도 금지된 후보는 선택될 수 없다 ([INV-11](e000a-entity-relationships.md)) |

### INV-K-08 — applicability의 축은 Resource Profile의 Context 축과 정합한다

| | |
|---|---|
| **위반 시** | Knowledge가 가리키는 상황과 Profile이 측정한 상황이 어긋나 보정이 잘못된 점수에 적용된다. 축 불일치를 경보로 발행 |

---

## 6. Lifecycle

```
Candidate → Validating → Active ──▶ Challenged ──▶ Revalidated ──▶ Active
                                          │
                                          ├──▶ Branched   (적용 조건 세분화)
                                          └──▶ Deprecated ──▶ Archived
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Candidate** | 패턴은 발견됐으나 근거 부족 | Pattern Extraction |
| **Validating** | 검증 진행 중. Low-risk Task에서 시험 적용 | 근거 임계 도달 |
| **Active** | Decision Engine / Planner가 참조 | 검증 통과 |
| **Challenged** | 모순 Memory 비율이 임계값 초과. 재검증 대기 | 반증 조건 충족 |
| **Branched** | Context 차이가 발견되어 하위 Knowledge로 분기 | 재검증 결과 |
| **Deprecated** | 반증됨 또는 만료됨. **참조 금지, 이력 보존** | 재검증 실패 |
| **Archived** | 보존 전용 | 보존 정책 |

### 6.1 반증과 재검증

Knowledge는 절대적이지 않다. 세상이 변하기 때문이다.

```
새 Memory 유입
  ↓
관련 Knowledge와 대조
  ↓ 모순 발견
contradicting_memory_refs에 등록 (INV-K-05 — 버리지 않는다)
  ↓
모순 비율 > falsification_condition?
  ├── No  → Confidence 소폭 하향
  └── Yes → Challenged → 재검증
              ├── Context 차이 발견 → Branched (적용 조건 세분화)
              ├── 일시적 이상       → Active 복귀
              └── 실제 변화 확인    → Deprecated + 새 Candidate 생성
```

### 6.2 Drift와의 연결

Resource는 버전 업데이트로 성능이 조용히 변한다. [Resource Profile](e025-resource-profile.md)의 Drift가 `Degraded`로 확정되면, 해당 Resource에 대한 모든 Resource Knowledge가 **일괄 Challenged**가 된다.

```
resource.drift_detected (Claude, observed 93 → 85)
  ↓ 구독
knw_0007 "교육 마케팅 감성 카피 → Claude 적합" → Challenged
  ↓ Controlled Testing 재실행 ([Volume 5 §9](../v5-learning-engine.md))
Confidence 0.91 → 0.74 로 갱신, Active 복귀
```

**Profile의 3-윈도우 규칙**([INV-RPF-07](e025-resource-profile.md))**이 먼저 작동한다.** 일시적 장애로 Knowledge가 흔들리지 않도록, Drift가 확정된 뒤에만 Challenged로 전이한다.

---

## 7. Relationships

```
Memory 010 ──패턴 추출 + 검증──▶ Knowledge 011
                                     │ 참조
              ┌──────────────────────┼──────────────────┐
              ▼                      ▼                  ▼
      Decision 009            Planner → Plan 008    Goal Engine
              │                      │
              ▼                      ▼
        더 나은 Decision        Workflow 022 (Procedural 승격)
              │
              ▼
       새 Execution → 새 Memory ──(지지 또는 반증으로 순환)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Memory](e010-memory.md) | Knowledge의 유일한 근거 원천 | `Memory N:1 Knowledge` |
| [Decision](e009-decision.md) | Decision Engine이 점수 보정에 사용 | `Knowledge N:M Decision` |
| [Plan](e008-plan.md) | Planner가 전략 선택에 사용 | `Knowledge N:M Plan` |
| [Workflow](e022-workflow.md) | Procedural Knowledge가 Workflow로 승격된다 | `Knowledge 1:0..N Workflow` |
| [Resource Profile](e025-resource-profile.md) | Drift 확정 시 Resource Knowledge를 일괄 Challenged | `Resource Profile 1:0..N Knowledge` |
| [Goal](e001-goal.md) | Domain/User Knowledge가 Goal 검증 질문을 줄인다 | `Knowledge N:M Goal` |
| [Feedback](e012-feedback.md) | Feedback이 Evaluation·Memory를 거쳐 Confidence를 바꾼다 | `Feedback N:M Knowledge` (간접) |
| [Policy](e019-policy.md) | **Policy가 Knowledge를 이긴다** (INV-K-07) | `Policy 1:N Knowledge` |
| [Risk](e018-risk.md) | Materialized Risk 이력이 확률 추정 Knowledge를 만든다 | `Risk N:M Knowledge` |

### 7.1 Knowledge의 소비자

Knowledge는 저장하기 위해 존재하지 않는다. **읽히기 위해 존재한다.**

| 소비자 | 언제 참조하는가 | 예 |
|---|---|---|
| **Decision Engine** | Resource 선택 시 | Claude 86 → 94점 보정 (교육 마케팅 경험 반영) |
| **Planner** | 전략/Plan 선택 시 | `조사 → 카피 → 파일럿 → 본 집행` 순서 채택 |
| **Goal Engine** | Goal 검증·질문 생성 시 | User Knowledge로 질문 생략 (`이 사용자의 예산 감도: 낮음`) |
| **Risk 식별** | Plan 생성 시 | 과거 Materialized Risk 유형의 likelihood 초기값 |
| **Prediction (Process)** | Outcome 예측 시 | 유사 조건 Knowledge의 Confidence를 사전확률로 사용 |

Decision Engine 반영 예([Volume 5 §8](../v5-learning-engine.md)):

| Resource | Before Learning | After (교육 마케팅 Knowledge 반영) |
|---|---|---|
| Claude | 86 | **94** |
| GPT | 85 | 87 |
| Gemini | 84 | 82 |

**이 보정은 [Resource Profile](e025-resource-profile.md)의 점수를 덮어쓰지 않는다.** Profile은 관측값이고 Knowledge 보정은 Decision 시점의 가중이다. 둘을 섞으면 관측 데이터가 오염된다.

---

## 8. Canonical Representation

```json
{
  "knowledge_id": "knw_0007",
  "knowledge_type": "Resource",
  "statement": "교육 마케팅 감성 카피에는 Claude 계열 Resource의 적합도가 높다",
  "applicability": {
    "domain": "교육",
    "language": "ko",
    "audience": "학부모",
    "task_type": "Creation"
  },
  "confidence": 0.91,
  "evidence": {
    "supporting_memory_refs": ["mem_0142", "mem_0155", "mem_0163"],
    "contradicting_memory_refs": ["mem_0201"],
    "evidence_count": 23
  },
  "falsification_condition": "동일 applicability 조건의 최근 30건 중 verdict=reject 비율 30% 초과",
  "scope": "Global",
  "created_at": "2026-07-15T00:00:00Z",
  "last_validated_at": "2026-08-03T00:00:00Z",
  "expiration_policy": "모델 메이저 업데이트 시 재검증",
  "status": "Active",
  "superseded_by": null
}
```

`applicability`의 축(`domain` / `language` / `audience` / `task_type`)이 [Resource Profile의 Context 축](e025-resource-profile.md)과 동일하다 — INV-K-08의 요구사항이다.

Task Knowledge는 다음과 같다.

```json
{
  "knowledge_id": "knw_0090",
  "knowledge_type": "Task",
  "statement": "시즌 캠페인에서 본 집행 전 파일럿을 선행하면 비가역 실패율이 크게 낮아진다",
  "applicability": {
    "domain": "교육",
    "task_type": "Automation"
  },
  "confidence": 0.87,
  "evidence": {
    "supporting_memory_refs": ["mem_0210", "mem_0233", "mem_0251"],
    "contradicting_memory_refs": [],
    "evidence_count": 12
  },
  "falsification_condition": "파일럿 선행 그룹의 실패율이 비선행 그룹과 통계적으로 차이 없음 (최근 20건)",
  "scope": "Global",
  "created_at": "2026-07-28T00:00:00Z",
  "last_validated_at": "2026-08-04T00:00:00Z",
  "status": "Active"
}
```

이 Knowledge가 [Workflow](e022-workflow.md) `wf_seasonal_campaign`의 `derived_from`이 된다.

**이 구조만 Decision Engine과 Planner로 전달된다.**

기계가 읽을 수 있는 스키마: [`knowledge.schema.json`](../intent-os-spec/schemas/knowledge.schema.json)

---

## 9. Validation Rules

### 9.1 Promotion — Memory에서 Knowledge로

Intent OS에서 가장 중요한 승격 경로다.

```
Memory 축적 (Episodic / Semantic / Procedural)
  ↓
Pattern Extraction (Learning Engine)
  ↓
Candidate Knowledge 생성
  ↓
statement 반증 가능성 검사 (Rule K-002, INV-K-02)
  └── falsification_condition을 관측 가능한 조건으로 표현 불가 → 반려
  ↓
applicability 명시 확인 (Rule K-005)
  └── 축이 Resource Profile의 Context 축과 정합한가 (INV-K-08)
  ↓
근거 수 검사 (Rule K-001, INV-K-01)
  evidence_count ≥ 임계값 (기본 5, 도메인별 설정)
  ↓
모순 비율 검사
  |contradicting| / evidence_count ≤ 임계값
  ↓
역추적 가능성 검사 (Rule K-004, INV-K-04)
  각 Memory → Evaluation → Execution → Decision → Goal 도달 확인
  ↓
Validating — Low-risk Task에서 시험 적용
  Exploration 예산 내에서 수행 ([Volume 5 §10](../v5-learning-engine.md))
  ↓
시험 결과 양호?
  ├── Yes → Active + Event 발행 (knowledge.activated)
  └── No  → Candidate 복귀 또는 Rejected
```

**승격은 자동이지만 즉시가 아니다.** Candidate 상태에서 Exploration 예산(전체 실행의 10%) 안에서 시험된 후에만 Active가 된다.

### 9.2 Confidence 갱신

```
새 Memory 도착
  ↓
applicability 매칭
  ↓
지지인가 반대인가
  ├── 지지 → supporting_memory_refs 추가, confidence 소폭 상향
  └── 반대 → contradicting_memory_refs 추가 (INV-K-05)
             ↓
           모순 비율 > falsification_condition?
             ├── No  → confidence 소폭 하향
             └── Yes → Challenged (§6.1)
  ↓
evidence_count 갱신
  ↓
confidence < 임계값 → Challenged
```

**단일 Memory가 Knowledge를 뒤집지 못한다**([Rule M-005](e010-memory.md)). 반증도 누적되어야 한다.

---

## 10. Examples

### 10.1 예시 1 — 승격 전체 흐름

```
Memory 축적 (23건)
  situation: 교육 / ko / 학부모 / 카피 작성
  action:    Claude 선택
  result:    평균 outcome_quality 0.89
  ↓ Pattern Extraction
Candidate: "교육 마케팅 감성 카피 → Claude 적합"
  ↓ 검증
  근거 23건 ≥ 5              ✅
  모순 1건 / 23 = 4.3% ≤ 30% ✅
  applicability 명시          ✅
  반증 조건 정의              ✅
  ↓ Validating (Exploration 예산 내 5회 시험)
  5회 중 5회 verdict=accept   ✅
  ↓
knw_0007 Active (confidence 0.91)
```

### 10.2 예시 2 — Branched (적용 조건 세분화)

```
knw_0007 "교육 마케팅 감성 카피 → Claude 적합"  confidence 0.91
  ↓ 새 Memory 8건 유입 — 전부 반대 근거
  모순 비율 9/31 = 29% → 임계 30% 근접
  ↓ 1건 더 → 32% 초과
Challenged
  ↓ 재검증: Context 차이 탐색
발견: 반대 근거 9건은 전부 audience=학생 (학부모 아님)
  ↓ Branched
knw_0007  applicability: {domain:교육, language:ko, audience:학부모}  conf 0.94 ↑
knw_0112  applicability: {domain:교육, language:ko, audience:학생}    conf 0.61
```

**Knowledge가 틀린 것이 아니라 너무 넓었던 것이다.** 반대 근거를 버렸다면(INV-K-05 위반) 이 분기를 발견하지 못했을 것이다.

### 10.3 예시 3 — Drift에 의한 일괄 Challenged

```
2026-09-18  Resource Profile: Claude Degraded 확정 (93 → 85, 3-윈도우)
  ↓ resource.drift_detected Event
Resource Knowledge 일괄 조회: knw_0007, knw_0044, knw_0058
  ↓ 전부 Challenged
  ↓ Controlled Testing 재실행
knw_0007  confidence 0.91 → 0.74  → Active 복귀
knw_0044  confidence 0.88 → 0.31  → Deprecated (superseded_by: knw_0130)
knw_0058  confidence 0.79 → 0.77  → Active 복귀 (영향 없음)
```

**세 Knowledge가 같은 Drift에 다르게 반응했다.** 일괄 폐기하지 않고 각각 재검증하는 이유다.

### 10.4 예시 4 — Knowledge 충돌

```
User Knowledge   knw_0203  "이 대표는 인간 검수를 선호한다"        conf 0.88
Task Knowledge   knw_0090  "파일럿 선행이 실패율을 낮춘다"          conf 0.87
Resource Knowledge knw_0007 "교육 카피는 Claude 적합"              conf 0.91

Task: 윈터캠프 카피 작성
  ↓ 충돌 없음 — 셋 다 양립 가능
Decision: Claude 초안 → 김 카피라이터 검수 → 파일럿 집행
```

```
User Knowledge   knw_0210  "이 대표는 GPT 결과물을 선호한다"       conf 0.72
Resource Knowledge knw_0007 "교육 카피는 Claude 적합"              conf 0.91
  ↓ 충돌
해소 순서 (§12 미결, v2.0 기본안):
  명시적 사용자 선호 > Task Knowledge > Global Knowledge
  ↓
GPT 선택. 단 Decision의 rationale에 충돌 사실과 해소 근거를 기록
  ↓ 이후 Evaluation에서 결과 검증 → 두 Knowledge의 confidence 재계산
```

**충돌을 숨기지 않는다.** rationale에 남겨야 나중에 어느 쪽이 옳았는지 판정할 수 있다.

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **근거 Memory가 전부 같은 Goal에서 나옴** | 일반화가 아니라 그 Goal의 특성일 수 있다. `evidence_count`가 충분해도 **출처 Goal의 다양성**을 함께 검사해야 한다(§12) |
| **반대 근거가 0건인데 confidence가 낮음** | 근거 수가 적은 경우다. 정상이다. confidence는 근거 수와 모순 비율 양쪽을 반영한다 |
| **Knowledge끼리 모순** | §10.4의 해소 순서를 적용하고 **rationale에 기록**한다. 자동으로 한쪽을 폐기하지 않는다 |
| **Deprecated Knowledge를 사용자가 참조 요청** | 조회는 허용하되 Decision 반영은 차단한다(INV-K-06). "과거에 이렇게 믿었다"는 설명 가능해야 한다 |
| **근거 Memory가 삭제 요청됨** | `evidence_count` 차감 → 임계값 미달 시 `Challenged` → 재검증. [Memory §12](e010-memory.md)와 공유하는 미결 항목이다 |
| **applicability가 너무 좁음** | 근거 수가 임계값에 도달하지 못해 영영 Candidate에 머문다. 상위 축으로 일반화를 시도하되, 그 결과가 §10.2처럼 다시 분기될 수 있다 |
| **Knowledge가 Policy와 충돌** | Policy가 이긴다(INV-K-07). Knowledge를 폐기하지는 않는다 — 규정이 바뀌면 다시 유효해진다 |
| **오래되었지만 반증도 지지도 없는 Knowledge** | `expiration_policy`에 따라 재검증한다. 사용되지 않는 Knowledge는 검증 기회도 없으므로 조용히 낡는다 |
| **Confidence가 계속 0.5 근처를 맴돎** | 그 상황에서 실제로 경향이 없다는 뜻일 수 있다. 3회 이상 Challenged↔Active를 반복하면 `Deprecated`하고 "경향 없음"을 기록한다 |

---

## 12. Open Issues (v2.0)

### ✅ v1.0에서 해소된 항목

| v1.0 Open Issue | 해소 |
|---|---|
| Resource Knowledge와 성능 수치의 경계 | [Resource Profile](e025-resource-profile.md) 신설. 수치는 Profile, 명제는 Knowledge (§2) |
| Drift 시 재검증 트리거 | Profile의 3-윈도우 Drift 확정과 연동 (§6.2) |
| Procedural 패턴의 재사용 | [Workflow](e022-workflow.md)로 승격 경로 확정 |

### Knowledge 충돌 해결

§10.4의 해소 순서(**명시적 사용자 선호 > Task Knowledge > Global Knowledge**)는 v2.0 기본안일 뿐이다. Confidence 격차가 큰 경우(사용자 선호 0.55 vs Task Knowledge 0.94)의 예외 규칙이 없다.

### Confidence 계산식의 형식 정의

베이지안 갱신인가 빈도 기반인가. [Resource Profile §12](e025-resource-profile.md)의 confidence 산출과 **같은 공식을 써야 한다** — 두 곳에서 다른 방식을 쓰면 "0.9"가 서로 다른 의미가 된다.

### 근거의 다양성 검사

§11이 지적한 문제다. `evidence_count`만으로는 "한 Goal에서 23번 반복"과 "23개 Goal에서 각 1번"을 구분하지 못한다. 후자가 훨씬 강한 근거다.

### Collective Knowledge의 프라이버시 경계

User-level Knowledge를 익명화해 Global로 올리는 규칙([Volume 5 §15](../v5-learning-engine.md))의 형식 정의가 없다. [Memory §4.2](e010-memory.md)의 Scope 승격 규칙과 통합되어야 한다.

### Knowledge 간 의존 그래프

하나가 Deprecated되면 그것을 전제로 만들어진 파생 Knowledge는 어떻게 되는가. 현재는 Knowledge를 독립 객체로 다루므로 연쇄 재검증이 일어나지 않는다.

### 앞으로 보강해야 할 항목

- Confidence 계산식 확정 (Resource Profile과 공유)
- 근거 다양성 지표의 정의
- Knowledge 분기(Branching) 알고리즘
- 실제 예시 30~50개
