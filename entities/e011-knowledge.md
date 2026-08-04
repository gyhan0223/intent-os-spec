# Entity 011: Knowledge

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

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

## 3. Knowledge의 조건

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

## 4. Knowledge Attributes

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

---

## 5. Knowledge Types

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

## 6. Knowledge Lifecycle

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

---

## 7. Promotion — Memory에서 Knowledge로

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

## 8. 반증과 재검증 (Falsification & Revalidation)

Knowledge는 절대적이지 않다. 세상이 변하기 때문이다.

### 반증 흐름

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

### Drift와의 연결

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

## 9. Knowledge의 소비자

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

## 10. Canonical Knowledge Representation

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

## 11. 다른 Entity와의 관계

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

| Entity | 관계 |
|---|---|
| [Memory](e010-memory.md) | Knowledge의 유일한 근거 원천 |
| [Feedback](e012-feedback.md) | Feedback이 Memory의 평가를 바꾸면 Knowledge Confidence도 재계산된다 |
| [Goal](e001-goal.md) | Domain/User Knowledge가 Goal 검증 질문을 줄인다 |
| [Task](e005-task.md) | Task Knowledge의 적용 단위 |
| Resource (예정) | Resource Knowledge의 대상. Drift 시 일괄 재검증 |

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
