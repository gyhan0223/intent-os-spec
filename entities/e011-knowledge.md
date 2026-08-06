# Entity 011: Knowledge

- **Version:** v2.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04
- **Schema:** [`knowledge.schema.json`](../intent-os-spec/schemas/knowledge.schema.json)

---

## 1. Definition

### 공식 정의

> **Knowledge is a validated generalization derived from multiple memories, which the system uses to make better decisions.**

> Knowledge는 여러 Memory로부터 도출되어 검증을 통과한 일반화이며, 시스템이 더 나은 결정을 내리는 데 사용된다.

여기서 중요한 단어는 **Validated Generalization**이다.

일반화되지 않은 것은 Memory이고, 검증되지 않은 것은 가설일 뿐이다. 둘 다 통과해야 Knowledge다.

### Entity / Process / Runtime State 구분

| 분류 | 예 | 설명 |
|---|---|---|
| **Process** | Learning | Memory를 읽어 Knowledge를 만드는 **수행 과정** |
| **Entity** | Memory | Learning이 읽는 **개별 사례 기록** |
| **Entity** | **Knowledge** | Learning이 쓰는 **일반화된 산출물** |

Learning(Process)의 입력이 Memory라면, 출력이 Knowledge다. Knowledge는 만들어진 뒤에는 Process와 독립적으로 **존재**하며, Decision Engine과 Planner가 읽는다.

```
Memory (개별 사례들)
   ↓
Learning (Process)
   ↓
Knowledge (일반화된 앎)
   ↓
Decision Engine / Planner (소비자)
```

---

## 2. Knowledge는 무엇이 아닌가?

이게 정의보다 훨씬 중요하다.

### Knowledge는 Memory가 아니다

❌ `2026-08-01, A 미술학원 윈터캠프 광고, Claude 사용, 전환율 상승` — 이건 **개별 사례(Memory)** 다.

✅ `교육 마케팅 + 한국어 감성 카피 → Claude 계열 Resource 높은 적합도` — 이것이 Knowledge다.

| | Memory | Knowledge |
|---|---|---|
| 성격 | 사례 (Instance) | 일반화 (Generalization) |
| 개수 | 사건마다 1건 | 패턴마다 1건 |
| 시제 | "그때 그랬다" | "이런 상황에서는 대체로 이렇다" |
| 검증 | 불필요 (사실 기록) | **필수** |

### Knowledge는 LLM 내부 지식이 아니다

❌ `Claude가 파라미터 안에 가지고 있는 세상 지식` — 이건 Resource의 속성이다.

Intent OS의 Knowledge는 **시스템이 자기 경험으로 만든, 모델 외부에 존재하는 자산**이다. 모델을 교체해도 남고, 모델은 접근할 수 없는 내용(예: `이 사용자는 GPT 결과물을 두 번 연속 폐기했다`에서 나온 일반화)을 담는다. [Volume 5 §1.2](../v5-learning-engine.md): Intent OS는 모델을 학습시키지 않는다. **어떤 상황에서 어떤 Resource를 어떻게 활용해야 성공하는가**를 학습한다.

### Knowledge는 Learning이 아니다

❌ `패턴을 추출하고 검증하는 것` — 이건 **Process**다. Knowledge는 그 Process의 **산출물(Entity)** 이다.

### Knowledge는 Rule(Constraint)이 아니다

⚠️ `예산 300만원 초과 금지`는 Constraint([e004], 예정)다. Constraint는 위반하면 안 되는 **강제 규칙**이고, Knowledge는 **확률적 경향**이다. Knowledge는 언제나 반증될 수 있다.

---

## 3. Design Principles

### Rule K-001 — 복수의 Memory를 근거로 가져야 한다

`Single Memory ≠ Knowledge`. 근거 Memory가 최소 임계값(도메인별 설정, 기본 N ≥ 5) 이상이어야 한다.

❌ `어제 Claude가 잘했으니 Claude가 카피에 최적이다` — 사례 1건. Knowledge가 될 수 없다.

### Rule K-002 — 반증 가능해야 한다 (Falsifiable)

Knowledge는 "어떤 새로운 Memory가 나타나면 이 Knowledge가 흔들리는가"를 스스로 정의해야 한다. 반증 조건이 없는 문장은 Knowledge가 아니라 슬로건이다.

### Rule K-003 — Confidence를 가진다

모든 Knowledge는 0~1의 Confidence를 가지며, Decision Engine은 이 값을 가중치로 사용한다. Confidence 1.0은 존재하지 않는다.

### Rule K-004 — 근거로 역추적 가능해야 한다

Knowledge → 근거 Memory 목록 → 원본 Execution까지 추적 가능해야 한다. 사용자가 *"왜 Claude를 추천했어?"* 라고 물으면 이 사슬로 설명한다. ([Volume 4-F Appendix ③ Explainable World Reasoning](../v4f-world-model.md))

### Rule K-005 — 적용 조건(Applicability)을 명시해야 한다

`Claude가 좋다`는 Knowledge가 아니다. **어떤 상황에서** 좋은지가 있어야 한다.

✅ `Task: 마케팅 카피 + Audience: 한국 학부모 + Tone: 감성 → Claude 적합도 높음`

---

## 4. Attributes

```
Knowledge
├── Knowledge ID
├── Knowledge Type
├── Statement (일반화 명제)
├── Applicability (적용 조건)
├── Confidence
├── Evidence
│     ├── Supporting Memory Refs
│     ├── Contradicting Memory Refs
│     └── Evidence Count
├── Falsification Condition
├── Scope
├── Created At
├── Last Validated At
├── Expiration Policy
└── Status
```

| 속성 | 의미 | 예 |
|---|---|---|
| **Knowledge ID** | 고유 식별자 | `knw_0007` |
| **Knowledge Type** | Resource / Task / User / Domain | `Resource` |
| **Statement** | 일반화 명제 | `교육 마케팅 감성 카피에는 Claude 계열이 적합하다` |
| **Applicability** | 적용 조건 | `task=marketing_copy, audience=한국 학부모` |
| **Confidence** | 신뢰도 | `0.91` |
| **Supporting Memories** | 지지 근거 | `[mem_0142, mem_0155, ...] (23건)` |
| **Contradicting Memories** | 반대 근거 | `[mem_0201] (1건)` |
| **Falsification Condition** | 반증 조건 | `동일 조건 실패 사례가 최근 30건 중 30% 초과` |
| **Scope** | User-level / Global | `Global` |
| **Last Validated At** | 마지막 재검증 시각 | `2026-08-03` |
| **Expiration Policy** | 만료 정책 | `모델 메이저 업데이트 시 재검증` |
| **Status** | 생명주기 상태 | `Active` |

Contradicting Memory를 **버리지 않고 함께 보관**하는 것이 핵심이다. 반대 근거의 비율이 곧 재검증 트리거다.

### 4.1 Knowledge Types

[Volume 5 §7 Knowledge Manager](../v5-learning-engine.md)의 4분류를 그대로 따른다.

```
Knowledge
├── Resource Knowledge — Resource의 강점/약점/비용
├── Task Knowledge     — Task 유형별 최적 접근
├── User Knowledge     — 사용자별 선호와 패턴
└── Domain Knowledge   — 도메인별 요구사항
```

| Type | 예 |
|---|---|
| **Resource Knowledge** | `Claude — Strength: Writing / Weakness: Complex Coding / Cost: Medium` |
| **Task Knowledge** | `Marketing Copy — Best Resource: Claude, Average Confidence: 91%` |
| **User Knowledge** | `사용자 A — Quality > Speed, 상세한 결과물 선호` |
| **Domain Knowledge** | `Medical Research — 높은 정확도, 다중 검증, Human Review 필수` |

---

## 5. Invariants

### INV-K-01 — 모든 Knowledge는 복수의 Memory에 근거한다

Rule K-001의 상태 표현이다. 근거가 하나로 줄어들면(Memory 삭제·병합 등) 그것은 더 이상 경향이 아니라 사건이다.

| | |
|---|---|
| **위반 시** | Knowledge를 `Provisional`로 강등하고 Decision 참조에서 제외한다. 삭제하지 않는다 — 근거가 다시 쌓이면 복귀할 수 있다 |
| **탐지** | 근거 Memory 변경 시점, 야간 정합성 검사 |

### INV-K-02 — 반증 조건 없는 Knowledge는 활성 상태가 될 수 없다

Rule K-002의 상태 표현이다. **틀렸다고 판정할 방법이 없는 명제는 지식이 아니라 믿음이다.**

| | |
|---|---|
| **위반 시** | `Active`로 올리지 않고 `Provisional`에 머문다. Planner는 참조할 수 있으나 Confidence 가중치가 낮게 적용된다 |

### INV-K-03 — 근거로 역추적할 수 없는 Knowledge는 참조되지 않는다

`supporting_memories`가 실재하지 않는 id를 가리키면 그 지식은 검증 불가다.

| | |
|---|---|
| **위반 시** | 참조를 차단하고 근거 복원을 요청한다. 복원되지 않으면 `Retired`로 내린다 |

### INV-K-04 — 반증 사례는 Confidence에 반드시 반영된다

반증을 무시하면 시스템은 자기가 틀렸다는 증거를 보고도 같은 판단을 계속한다.

| | |
|---|---|
| **위반 시** | Confidence를 재계산한다. 반증이 지지를 넘어서면 `Falsified`로 전이하고, 그 Knowledge를 근거로 삼은 진행 중 Decision을 재검토 대상으로 표시한다 |
| **탐지** | 새 Memory·Feedback 도착 시점 |

### INV-K-05 — 적용 조건 밖에서 Knowledge가 쓰이지 않는다

`applicability`가 "학원 · 학부모 대상 · 인스타그램"인 지식이 B2B 이메일 캠페인에 적용되면, 근거 없는 일반화가 결정에 들어간다.

| | |
|---|---|
| **위반 시** | 적용을 차단한다. 정말 넓게 통한다고 보면 **적용 조건을 넓히는 별도 검증**을 거친다. 조용히 확장하지 않는다 |

### INV-K-06 — Falsified Knowledge는 조용히 사라지지 않는다

| | |
|---|---|
| **위반 시** | 삭제를 거부한다. 반증된 지식이 남아 있어야 "왜 그렇게 믿었는가"와 "무엇이 그것을 뒤집었는가"를 함께 배울 수 있다 |

Entity 간 불변식은 [e000a-entity-relationships.md](e000a-entity-relationships.md)가 단일 권위다.

---

## 6. Lifecycle

```
Candidate → Validating → Active → Challenged → (Revalidated → Active)
                                             ↘ Deprecated → Archived
```

| 상태 | 의미 |
|---|---|
| **Candidate** | 패턴은 발견됐으나 근거 부족 (Semantic Memory 수준) |
| **Validating** | 검증 진행 중. Low-risk Task에서 시험 적용 |
| **Active** | Decision Engine / Planner가 참조 |
| **Challenged** | 모순 Memory 비율이 임계값 초과. 재검증 대기 |
| **Deprecated** | 반증됨 또는 만료됨. 참조 금지, 이력은 보존 |
| **Archived** | 보존 전용 |

### 6.1 반증과 재검증 (Falsification & Revalidation)

Knowledge는 절대적이지 않다. 세상이 변하기 때문이다.

#### 반증 흐름

```
새 Memory 유입
  ↓
관련 Knowledge와 대조
  ↓ 모순 발견
Contradicting Memory로 등록
  ↓
모순 비율 > Falsification Condition?
  ├── No  → Confidence 소폭 하향
  └── Yes → Status: Challenged → 재검증
              ├── Context 차이 발견 → Knowledge 분기 (적용 조건 세분화)
              ├── 일시적 이상 → Active 복귀
              └── 실제 변화 확인 → Deprecated + 새 Candidate 생성
```

#### Drift와의 연결

Resource(AI 모델)는 버전 업데이트로 성능이 조용히 변한다. [Volume 4-B](../v4b-resource-intelligence.md)의 Drift 감지가 발동하면, 해당 Resource에 대한 모든 Resource Knowledge는 **일괄 Challenged 상태**가 된다.

```
GPT 성능 Drift 감지 (코딩 품질 하락)
  ↓
knw_0021 "Legal Analysis → GPT Family" → Challenged
  ↓
Controlled Testing ([Volume 5 §9]) 재실행
  ↓
Confidence 0.89 → 0.74 로 갱신, Active 복귀
```

---

## 7. Relationships

```
Memory (e010) ──패턴 추출 + 검증──→ Knowledge (e011)
                                        ↓ 참조
                          Decision Engine / Planner
                                        ↓
                                   더 나은 Decision
                                        ↓
                                   새 Execution → 새 Memory
                                        ↓
                              (지지 또는 반증으로 순환)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Memory](e010-memory.md) | Knowledge의 유일한 근거 원천. 하나로는 승격되지 않는다 (INV-K-01) | `Memory N:M Knowledge` |
| [Feedback](e012-feedback.md) | Feedback이 Memory의 평가를 바꾸면 Knowledge Confidence도 재계산된다 | `Knowledge 1:0..N Feedback` |
| [Goal](e001-goal.md) | Domain/User Knowledge가 Goal 검증 질문을 줄인다 | `Knowledge N:M Goal` |
| [Task](e005-task.md) | Task Knowledge의 적용 단위 | `Knowledge N:M Task` |
| [Decision](e009-decision.md) | Knowledge는 Decision의 입력이다. 반증되면 진행 중 Decision이 재검토된다 | `Knowledge N:M Decision` |
| [Resource](e007-resource.md) | Resource Knowledge의 대상. Drift 시 일괄 재검증 | `Knowledge N:M Resource` |
| [Capability](e006-capability.md) | Taxonomy 자체가 시스템 Knowledge의 일부다 | `Capability 1:0..N Knowledge` |

**Knowledge는 Memory를 참조하고 Memory는 Knowledge를 모른다**([Rule REL-002](e000a-entity-relationships.md)).

### 7.1 Knowledge의 소비자

Knowledge는 저장하기 위해 존재하지 않는다. **읽히기 위해 존재한다.**

| 소비자 | 언제 참조하는가 | 예 |
|---|---|---|
| **Decision Engine** | Resource 선택 시 | Claude 86 → 94점 보정 (Education Marketing 경험 반영) |
| **Planner** | 전략/Plan 선택 시 | `후기 확보 → 랜딩페이지 → 광고` 순서 전략 채택 |
| **Goal Engine** | Goal 검증·질문 생성 시 | User Knowledge로 질문 생략 (`이 사용자의 예산 감도: 낮음`) |
| **Prediction (Process)** | Outcome 예측 시 | 유사 조건 Knowledge의 Confidence를 사전확률로 사용 |

Decision Engine 반영 예 ([Volume 5 §8](../v5-learning-engine.md)):

| Resource | Before Learning | After (Education Marketing Knowledge 반영) |
|---|---|---|
| Claude | 86 | **94** |
| GPT | 85 | 87 |
| Gemini | 84 | 82 |

---

## 8. Canonical Representation

```json
{
  "knowledge_id": "knw_0007",
  "knowledge_type": "Resource",
  "statement": "교육 마케팅 감성 카피에는 Claude 계열 Resource의 적합도가 높다",
  "applicability": {
    "task": "marketing_copy",
    "audience": "한국 학부모",
    "tone": "감성"
  },
  "confidence": 0.91,
  "evidence": {
    "supporting_memory_refs": ["mem_0142", "mem_0155"],
    "contradicting_memory_refs": ["mem_0201"],
    "evidence_count": 23
  },
  "falsification_condition": "동일 조건 최근 30건 중 실패 비율 30% 초과",
  "scope": "Global",
  "created_at": "2026-07-15T00:00:00Z",
  "last_validated_at": "2026-08-03T00:00:00Z",
  "status": "Active"
}
```

**이 구조만 Decision Engine과 Planner로 전달된다.**

기계가 읽을 수 있는 스키마: [`knowledge.schema.json`](../intent-os-spec/schemas/knowledge.schema.json)

---

## 9. Validation Rules

### 9.1 Promotion — Memory에서 Knowledge로

Intent OS에서 가장 중요한 승격 경로다.

```
Memory (개별 사례 축적)
  ↓
Pattern Extraction (Learning Engine — Pattern Extractor)
  ↓
Candidate Knowledge 생성
  ↓
검증 (Validation)
  ├── 근거 수 ≥ 임계값?
  ├── 모순 비율 ≤ 임계값?
  ├── 적용 조건이 명확한가?
  └── Low-risk 시험 적용 결과 양호?
  ↓ 모두 통과
Active Knowledge
```

예)

```
Raw Data (500회 반복):
  Task:     Legal Document Review
  Resource: GPT
  Outcome:  High
        ↓
Pattern:
  Legal Analysis Task → GPT Family → High Reliability
        ↓ 검증 통과
knw_0021 (Confidence 0.89, Evidence 500)
```

승격은 **자동이지만 즉시가 아니다.** Candidate 상태에서 Exploration 예산(전체 실행의 10%, [Volume 5 §10](../v5-learning-engine.md)) 안에서 시험된 후에만 Active가 된다.

---

## 10. Examples

### 예시 1 — 승격된 Knowledge 하나

```
know_042
  statement    "예비 고3 학부모 대상 광고는 불안 소구보다
                구체적 일정 제시가 클릭률이 높다"
  type         Domain
  applicability 업종=학원 / 대상=학부모 / 채널=인스타그램 / 지역=수도권
  confidence   0.74
  supporting   mem_612 (CTR 3.2%), mem_640 (2.9%)
  refuting     mem_701 (불안 소구 1.4% — 반대 방향이므로 지지 근거)
  falsifiable  "일정 제시형 CTR이 불안 소구형보다 3회 연속 낮으면 반증"
  status       Active
```

`falsifiable` 항목이 이 지식을 믿음과 갈라놓는다(INV-K-02). 무엇이 일어나면 이것을 버릴지가 미리 적혀 있다.

### 예시 2 — Knowledge가 Decision을 바꾸는 순간

```
task_014  겨울방학 특강 인스타 카피 작성
  적용 조건 검사: 업종=학원 ✅ / 대상=학부모 ✅ / 채널=인스타그램 ✅
  ↓
know_042 적용 (confidence 0.74)
  → 프롬프트에 "구체적 일정 제시" 방향 주입
  → 후보 Resource의 예상 품질 +0.05 보정
```

같은 Task라도 채널이 이메일이었다면 적용 조건을 벗어나 **주입되지 않는다**(INV-K-05).

### 예시 3 — 반증되어 뒤집히는 과정

```
know_042  Active  confidence 0.74
  ↓ 11월 관측
mem_760  일정 제시형 CTR 1.1% / 불안 소구형 2.8%   ← 반대
mem_781  일정 제시형 0.9% / 불안 소구형 3.1%       ← 반대
mem_802  일정 제시형 1.2% / 불안 소구형 2.6%       ← 반대  (3회 연속)
  ↓ falsifiable 조건 충족 (INV-K-04)
know_042  Falsified   confidence 0.21
  ↓
know_042를 근거로 삼은 진행 중 Decision 2건 → 재검토 표시
새 가설: "11월(원서 시즌)에는 불안 소구가 더 효과적이다"
  → 시점 조건이 빠져 있었다는 것이 진짜 발견이다
```

`know_042`는 지워지지 않는다(INV-K-06). 반증 이력이 남아야 **적용 조건에 '시기'가 빠져 있었다**는 교훈이 보존된다.

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **지지 근거와 반증 근거가 팽팽함** | `Provisional`로 되돌린다. Confidence를 중간값으로 두고 Active를 유지하면, 반반인 명제가 확신처럼 쓰인다 |
| **적용 조건이 다른 두 Knowledge가 충돌** | 충돌이 아니다. 조건이 다르면 둘 다 참일 수 있다. 조건까지 같은데 결론이 반대면 **상위 조건이 하나 빠져 있다**는 신호이므로 조건 탐색을 먼저 한다 |
| **근거 Memory가 개인정보 삭제 요청으로 제거됨** | Knowledge를 지우지 않는다. 근거 수가 줄어 INV-K-01에 걸리면 `Provisional`로 강등된다. 집계 통계는 재계산한다 |
| **한 번도 적용되지 않은 Knowledge** | 유지한다. 적용 기회가 없었던 것과 틀린 것은 다르다. 다만 오래 미적용이면 적용 조건이 지나치게 좁다는 신호이므로 검토 대상으로 표시한다 |
| **외부에서 주입된 지식** (사람이 직접 입력) | `source: human_asserted`로 받되 근거 Memory가 없으므로 `Provisional`에 둔다. 사람이 말했다는 것은 근거가 아니라 출처다 |
| **Knowledge가 Constraint처럼 쓰임** | 막는다. Knowledge는 **확률적 경향**이고 Constraint는 **강제 규칙**이다. "학부모는 일정 제시를 선호한다"가 "불안 소구를 쓰면 안 된다"로 굳으면 탐색이 죽는다 |
| **Confidence가 0.99에 도달** | 1.0으로 올리지 않는다. 반증 가능성이 0인 명제는 INV-K-02가 배제한 것과 같은 상태가 된다. 상한을 두고 반증 창구를 열어 둔다 |

---

## 12. Open Issues (v1.0)

### Knowledge 충돌 해결

User Knowledge(`이 사용자는 GPT 선호`)와 Task Knowledge(`이 Task는 Claude 적합`)가 충돌하면 누가 이기는가? v1.0 기본안은 **명시적 사용자 선호 > Task Knowledge > Global Knowledge** 순서지만, Confidence 격차가 큰 경우의 예외 규칙이 필요하다.

### 근거 Memory 삭제 시의 연쇄 처리

사용자가 Memory 삭제를 요구하면 evidence_count가 줄어든다. 임계값 미달 시 Knowledge를 자동 강등할 것인가? ([e010-memory.md §12](e010-memory.md) 공유 이슈)

### Collective Knowledge의 프라이버시 경계

User-level Knowledge를 익명화해 Global로 올리는 규칙([Volume 5 §15](../v5-learning-engine.md) Collective Learning)의 형식 정의가 없다.

### 앞으로 보강해야 할 항목

- Confidence 계산식의 형식 정의 (베이지안 갱신 vs 빈도 기반)
- Knowledge 분기(적용 조건 세분화) 알고리즘
- Knowledge 간 의존 그래프 (하나가 Deprecated되면 파생 Knowledge 처리)
- 실제 예시 30~50개

