# Entity 010: Memory

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Memory is a persisted record of an experience — an execution, a decision, or an outcome — that the system can later recall.**

> Memory는 시스템이 나중에 회상할 수 있도록 영속화된 경험의 기록이다. 실행, 결정, 결과가 그 대상이다.

여기서 중요한 단어는 **Record**이다.

Memory는 "기억하는 행위"가 아니라 **저장되어 존재하는 기록 단위**이다.

### Entity / Process / Runtime State 구분

이 구분을 먼저 명확히 한다.

| 분류 | 예 | 설명 |
|---|---|---|
| **Process** | Learning | 경험을 읽고 일반화하는 **수행 과정** |
| **Runtime State** | Outcome | 실행 직후 생기는 **일시적 상태** |
| **Entity** | **Memory** | Outcome이 영속화되어 **존재하는 기록** |

즉, Learning(Process)이 **읽고 쓰는 대상**이 Memory(Entity)다. Outcome(Runtime State)은 기록되는 순간 Memory가 된다.

```
Execution (Process)
   ↓
Outcome (Runtime State)
   ↓ 영속화 (Memorization)
Memory (Entity)
   ↓ 읽기
Learning (Process)
```

---

## 2. Memory는 무엇이 아닌가?

이게 정의보다 훨씬 중요하다.

### Memory는 Learning이 아니다

❌ `과거 실행에서 패턴을 추출하기` — 이건 Memory가 아니다. **Learning(Process)** 이다.

Memory는 Learning이 읽는 **재료**다. 재료와 요리는 다르다.

### Memory는 Outcome이 아니다

❌ `방금 실행한 광고 카피의 CTR 8%` — 실행 직후에는 **Outcome(Runtime State)** 이다.

이 Outcome이 맥락(어떤 Goal, 어떤 Decision, 어떤 Resource)과 함께 영속화되어야 비로소 Memory가 된다.

### Memory는 LLM의 컨텍스트 윈도우가 아니다

❌ `대화 중 모델이 잠시 기억하는 내용` — 이건 세션이 끝나면 사라진다.

Memory는 **세션과 모델에 독립적으로 존재하는 시스템의 자산**이다. Claude를 GPT로 교체해도 Memory는 남는다. 이는 [Volume 1 Principle 03 — Resource Agnostic](../v1-core-concepts.md)과 일치한다.

### Memory는 Knowledge가 아니다

❌ `교육 마케팅 카피에는 Claude 계열이 적합하다` — 이건 일반화된 앎, 즉 **Knowledge**([e011-knowledge.md](e011-knowledge.md))다.

Memory는 **개별 사례**다. `2026-08-01, A 미술학원 윈터캠프 광고, Claude 선택, 전환율 상승` — 이것이 Memory다.

### Memory는 Log가 아니다

⚠️ 시스템 Log는 디버깅용 원시 기록이다. Memory는 **회상(Recall)을 전제로 구조화된 기록**이며, Goal·Decision·Outcome이 연결되어 있어야 한다. Log에서 Memory를 만들 수는 있지만, Log 자체는 Memory가 아니다.

---

## 3. Memory의 조건

Memory는 반드시 아래 규칙을 만족해야 한다.

### Rule M-001 — 맥락(Context) 없는 결과는 Memory가 될 수 없다

[Volume 5 Principle 02](../v5-learning-engine.md)의 원칙 그대로다. 저장해야 하는 것은 결과물이 아니라 **"왜 이 선택을 했고, 결과가 어땠는가"** 이다.

❌ 나쁜 Memory:

```
사용자에게 광고 문구 제공
```

✅ 좋은 Memory:

```
Goal:              교육 서비스 홍보
Context:           한국 학부모 대상, 겨울 모집 시즌
Selected Resource: Claude
Reason:            한국어 설득 구조 우수
Outcome:           전환율 증가
Confidence:        92%
```

### Rule M-002 — Memory는 사후에 수정하지 않는다 (Immutable)

Memory는 "그때 실제로 일어난 일"의 기록이다. 내용이 틀렸다면 수정하는 것이 아니라 **정정 Memory를 새로 기록**하고 원본과 연결한다. 기록을 덮어쓰면 Learning의 근거가 오염된다.

### Rule M-003 — 모든 Memory는 출처(Provenance)를 가진다

어떤 Execution, 어떤 Decision에서 나왔는지 추적 가능해야 한다. 출처 없는 Memory는 검증할 수 없고, 검증할 수 없는 Memory는 Knowledge로 승격될 수 없다.

### Rule M-004 — Memory는 Scope를 가진다

특정 사용자의 경험을 다른 사용자의 Decision에 함부로 사용하면 안 된다. (→ §6 Memory Scope)

### Rule M-005 — 단일 Memory는 시스템을 바꾸지 못한다

`Single Memory ≠ Learning Update`. 한 건의 기록만으로 Resource 성능 프로필이나 Knowledge를 갱신하지 않는다. ([Volume 5 §13 Learning Safety](../v5-learning-engine.md))

---

## 4. Memory Attributes

Memory는 최소한 아래 속성을 가진다.

```
Memory
├── Memory ID
├── Memory Type
├── Scope
├── Goal Reference
├── Decision Reference
├── Content
│     ├── Situation (무슨 상황이었나)
│     ├── Action (무엇을 했나)
│     └── Result (어떻게 됐나)
├── Confidence
├── Source (Provenance)
├── Created At
├── Last Recalled At
├── Recall Count
└── Status
```

| 속성 | 의미 | 예 |
|---|---|---|
| **Memory ID** | 고유 식별자 | `mem_0142` |
| **Memory Type** | Episodic / Semantic / Procedural | `Episodic` |
| **Scope** | 적용 범위 | `User-level` |
| **Goal Reference** | 어떤 Goal 아래의 경험인가 | `goal_001 (학생 100명 모집)` |
| **Decision Reference** | 어떤 Decision의 결과인가 | `dec_0088 (Claude 선택)` |
| **Content — Situation** | 상황 | `윈터캠프 광고 카피 작성, 학부모 대상` |
| **Content — Action** | 행동 | `Claude 선택, 감성 소구 전략` |
| **Content — Result** | 결과 | `상담 신청 30% 증가` |
| **Confidence** | 이 기록의 신뢰도 (0~1) | `0.92` |
| **Source** | 출처 | `exec_2210` |
| **Created At** | 기록 시각 | `2026-08-01T14:00:00Z` |
| **Last Recalled At** | 마지막 회상 시각 | `2026-08-03T09:12:00Z` |
| **Recall Count** | 회상된 횟수 | `7` |
| **Status** | 생명주기 상태 | `Active` |

Recall Count는 의외로 중요하다. **자주 회상되고 결과가 좋았던 Memory는 Knowledge 승격의 1차 후보**가 된다.

---

## 5. Memory Types

모든 Memory는 정확히 하나의 Type을 가진다.

```
Memory
├── Episodic Memory   — 개별 실행의 기록
├── Semantic Memory   — 일반화된 사실의 기록
└── Procedural Memory — 성공한 절차·전략의 기록
```

| Type | 무엇을 기록하는가 | 예 |
|---|---|---|
| **Episodic** | 특정 시점의 개별 사건 | `2026-08-01, 윈터캠프 광고, Claude 사용, 전환율 상승` |
| **Semantic** | 반복 관찰로 굳어진 사실 | `이 사용자는 상세한 결과물을 선호한다` |
| **Procedural** | 성공했던 절차/전략 | `학원 모집 캠페인: 후기 확보 → 랜딩페이지 개선 → 광고 순서가 효과적` |

세 Type의 관계:

```
Episodic (사건 1건)
   ↓ 반복 관찰
Semantic (사실)          Procedural (절차)
   ↓ 검증                     ↓ 검증
Knowledge (Entity 011)로 승격
```

Semantic Memory와 Knowledge의 차이에 주의한다. Semantic Memory는 **아직 검증 전의 일반화 후보**이고, 검증을 통과해야 Knowledge가 된다. (→ [e011-knowledge.md §7](e011-knowledge.md))

---

## 6. Memory Scope

Memory는 적용 범위가 다르다.

| Scope | 의미 | 예 |
|---|---|---|
| **Goal-level** | 특정 Goal 안에서만 유효 | `이번 윈터캠프 캠페인에서는 인스타 광고 반응이 좋았다` |
| **User-level** | 특정 사용자에게만 유효 | `이 학원 대표는 속도보다 품질을 선호한다` |
| **Global** | 익명화되어 전체 시스템에 유효 | `교육 마케팅 카피 작업의 평균 만족도 데이터` |

### Scope Rule

1. Memory는 생성 시 **가장 좁은 Scope**로 시작한다. (기본: Goal-level)
2. Scope 확장(Goal → User → Global)은 자동으로 일어나지 않는다. 패턴 검증과 **익명화**를 거쳐야 한다.
3. User-level Memory를 Global로 올릴 때 개인 식별 정보는 제거되어야 한다.

---

## 7. Memory Lifecycle

```
Created → Active → Decaying → Dormant → (Expired | Archived | Deleted)
                ↘ Promoted (Knowledge로 승격)
```

| 상태 | 의미 |
|---|---|
| **Created** | Outcome이 영속화된 직후 |
| **Active** | 회상 대상. Decision·Learning이 참조 |
| **Decaying** | 신뢰도 감쇠 진행 중. 참조 시 가중치 하락 |
| **Dormant** | 신뢰도가 임계값 이하. 기본 회상에서 제외 |
| **Promoted** | 패턴 검증을 거쳐 Knowledge 생성에 기여함 |
| **Expired** | 유효기간 만료 (예: 특정 모델 버전에 종속된 기록) |
| **Archived** | 보존은 하되 회상 불가 |
| **Deleted** | 사용자 요구 등으로 완전 삭제 |

---

## 8. Retention & Decay

오래된 경험은 현재를 덜 대표한다. AI 생태계는 빠르게 변하기 때문이다.

### Decay 원칙

$$Effective\ Confidence = Confidence \times DecayFactor(age, domain)$$

- 감쇠 속도는 **도메인에 따라 다르다.** `Claude 3.5가 카피라이팅에 강했다`는 모델 세대가 바뀌면 빠르게 낡는다. 반면 `이 사용자는 품질을 선호한다`는 천천히 낡는다.
- Decay는 **삭제가 아니다.** 신뢰 가중치만 낮아지고 기록은 남는다.
- 새로운 Memory가 낡은 Memory와 모순되면, 낡은 쪽의 Decay가 가속된다. 이는 [Volume 4-B](../v4b-resource-intelligence.md)의 Drift 감지와 연결된다.

예)

```
mem_0031 (2025-11): "GPT가 코딩 Task에서 최고 성능"
  ↓ 새 모델 출시 + 모순되는 Memory 다수 발생
Effective Confidence: 0.90 → 0.41
  ↓
Status: Decaying → Dormant
```

---

## 9. Canonical Memory Representation

모든 Memory는 내부적으로 동일한 구조를 가진다.

```json
{
  "memory_id": "mem_0142",
  "memory_type": "Episodic",
  "scope": "User-level",
  "goal_ref": "goal_001",
  "decision_ref": "dec_0088",
  "content": {
    "situation": "윈터캠프 광고 카피 작성, 한국 학부모 대상",
    "action": "Claude 선택, 감성 소구 전략 사용",
    "result": "상담 신청 30% 증가"
  },
  "confidence": 0.92,
  "source": "exec_2210",
  "created_at": "2026-08-01T14:00:00Z",
  "recall_count": 7,
  "status": "Active"
}
```

**이 구조만 Learning Engine으로 전달된다.**

기계가 읽을 수 있는 스키마: [`memory.schema.json`](../intent-os-spec/schemas/memory.schema.json)

---

## 10. Memory Algorithms

### 10.1 저장 (Memorization)

```
Outcome 발생
  ↓
맥락 수집 (Goal / Decision / Resource / Context)
  ↓
Rule M-001 검증 (맥락 완전성)
  ↓
Memory Type 분류
  ↓
Scope 결정 (기본: 가장 좁은 Scope)
  ↓
중복/모순 검사
  ↓
Canonical Memory 생성 → 저장
```

### 10.2 회상 (Recall)

```
질의 (예: "교육 마케팅 + 학부모 대상 + 카피 작성")
  ↓
Scope 필터 (현재 사용자/Goal 범위)
  ↓
유사 상황 Memory 검색
  ↓
Effective Confidence 계산 (Decay 반영)
  ↓
상위 N개 반환 → Decision Engine / Planner
  ↓
Recall Count 갱신
```

회상은 검색이 아니라 **의사결정 지원**이다. 반환 기준은 "비슷한 문자열"이 아니라 **"비슷한 상황(Situation)"** 이다.

---

## 11. 다른 Entity와의 관계

```
Decision (e009) ──실행──→ Execution (Process) ──→ Outcome (Runtime State)
                                                      ↓ 영속화
Feedback (e012) ──평가 신호 첨부──────────────→  Memory (e010)
                                                      ↓ 패턴 발견 + 검증
                                                  Knowledge (e011)
                                                      ↓ 참조
                                          Decision Engine / Planner
```

| Entity | 관계 |
|---|---|
| [Goal](e001-goal.md) | 모든 Memory는 특정 Goal의 맥락에서 생성된다 |
| Decision (예정) | Memory는 Decision의 근거와 결과를 기록한다 |
| [Knowledge](e011-knowledge.md) | Memory가 승격되어 Knowledge가 된다 |
| [Feedback](e012-feedback.md) | Feedback은 Memory에 평가 신호를 덧붙인다 |
| Resource (예정) | Resource 성능 프로필은 Memory 집합에서 계산된다 |

Learning Engine 관점의 전체 흐름은 [Volume 5](../v5-learning-engine.md), World 수준의 장기 기억은 [Volume 4-F §20 World Memory](../v4f-world-model.md)를 참조한다.

---

## 12. Open Issues (v1.0)

### 사용자의 삭제 권리 (Right to be Forgotten)

Memory는 사용자의 데이터다. 사용자가 삭제를 요구하면 시스템은 지워야 한다.

문제는 **이미 Knowledge로 승격된 경우**다.

```
mem_0142 (삭제 요청됨)
  ↓ 이미 기여함
knw_0007 "교육 마케팅 → Claude 적합"
```

Memory를 지우면 Knowledge의 근거가 사라진다. Knowledge까지 폐기할 것인가, 근거 수만 차감할 것인가? v1.0에서는 **원본 Memory 삭제 + Knowledge의 evidence_count 차감 + 임계값 미달 시 Knowledge 재검증**을 기본안으로 두되, 확정하지 않는다.

### Memory 저장 비용과 선별 기준

모든 Outcome을 저장하면 저장소와 회상 비용이 폭발한다. "기록할 가치가 있는 경험"의 기준(놀라움 정도, Goal 중요도, 실패 여부 등)이 필요하다.

### 모순되는 Memory의 병합

같은 상황에서 상반된 결과가 기록될 수 있다. 단순 평균은 위험하다. Context 차이를 찾아 분기하는 알고리즘이 필요하다.

### 앞으로 보강해야 할 항목

- Memory 유사도(Situation Similarity) 계산 명세
- Scope 승격 시 익명화 규칙의 형식 정의
- Decay Factor의 도메인별 파라미터 표
- 실제 예시 30~50개
