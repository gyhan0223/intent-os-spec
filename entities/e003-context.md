# Entity 003: Context

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Context is the structured representation of the current world state that surrounds a Goal — everything the system must know about "now" to reason correctly about the future.**

> Context는 Goal을 둘러싼 현재 세계 상태의 구조화된 표현이다. 미래(Goal)를 올바르게 추론하기 위해 시스템이 "지금"에 대해 알아야 하는 모든 것이다.

핵심 단어는 **Current(현재)** 이다.

Goal이 **미래 상태**라면, Context는 **현재 상태**다. Planner는 이 둘의 차이(Gap)를 좁히는 경로를 계산한다.

```
Context (현재)  ──── Gap ────▶  Goal (미래)
```

지금까지 Context는 Goal의 속성 중 하나였다 ([e001-goal.md §4](e001-goal.md)). 그러나 Context는 Goal만 참조하는 것이 아니다. **Intent 추론, Task 실행, Decision 모두가 Context를 참조한다.** 그래서 독립 Entity로 승격한다.

---

## 2. Context는 무엇이 아닌가?

이게 정의보다 훨씬 중요하다.

### Context는 Goal이 아니다

❌ `학생 100명 모집` — 미래 상태다. Goal이다.

✅ `현재 등록자 20명` — 현재 상태다. Context다.

### Context는 Constraint가 아니다

`예산 300만원`은 두 얼굴을 가진다.

- **Context 관점:** "현재 가용 예산이 300만원이다" — 사실(Fact)
- **Constraint 관점:** "300만원을 초과하면 안 된다" — 규칙(Rule)

Context는 **세계를 서술**하고, Constraint는 **행동을 제한**한다. 사실은 Context에, 규칙은 [Constraint (e004)](e004-constraint.md)에 저장한다.

### Context는 Memory가 아니다

Memory(e010, 예정)는 시스템이 축적하는 **장기 저장소**다. Context는 그중 **지금 이 Goal의 추론에 필요한 부분만 선별해 로드한 스냅샷**이다.

```
Memory (전체 저장소)
   ↓ 선별 + 로드
Context (현재 추론용 스냅샷)
```

### Context는 Knowledge가 아니다

Knowledge(e011, 예정)는 일반 법칙이다 (`교육 업종 광고는 학기 전에 효과가 높다`). Context는 특정 상황의 사실이다 (`이 학원의 현재 등록자는 20명이다`).

---

## 3. Context의 조건

### Rule C-001 — 사실(Fact)만 담아야 한다

✅ `현재 등록자 20명` / `지역: 홍대` / `경쟁 학원 3곳 존재`

❌ `홍보를 강화해야 한다` — 판단이다. Intent의 영역이다.

### Rule C-002 — 모든 항목은 출처(Source)를 가져야 한다

출처 없는 Context는 검증할 수 없고, 검증할 수 없는 Context 위의 추론은 신뢰할 수 없다.

### Rule C-003 — 모든 항목은 수집 시각(Collected At)을 가져야 한다

Freshness(§6) 계산의 전제 조건이다.

### Rule C-004 — Scope가 명시되어야 한다

Global / Goal-level / Task-level 중 하나 (§5).

### Rule C-005 — 실행은 Context를 보존해야 한다

[Volume 3 §8 Runtime Optimization Principles](../v3-runtime.md)의 "Preserve Context"와 동일한 원칙이다. 모든 실행 단계는 이전 단계의 Context를 유지·전달해야 한다.

---

## 4. Context Attributes

Context는 최소한 아래 영역을 가진다.

```
Context
├── Current State
├── Environment
├── User Profile
├── History
├── Available Resources
├── Scope
├── Freshness
└── Source
```

| 영역 | 의미 | 예 |
|---|---|---|
| **Current State** | Goal 대상의 현재 값 | `현재 등록자 20명`, `상담 문의 주 5건` |
| **Environment** | 외부 환경 | `지역 홍대`, `경쟁 학원 3곳`, `겨울방학 시즌` |
| **User Profile** | 사용자/조직 정보 | `신규 학원, 개원 6개월, 대표 1인 운영` |
| **History** | 과거 이력 | `지난 여름캠프 등록 35명, 블로그 광고 CTR 2%` |
| **Available Resources** | 가용 자원 | `예산 300만원, 마케팅 인력 0명, 인스타 계정 보유` |
| **Scope** | 적용 범위 | Global / Goal / Task |
| **Freshness** | 신선도 상태 | Fresh / Stale / Expired |
| **Source** | 각 항목의 출처 | 사용자 입력 / 시스템 관측 / 외부 API / 추정 |

**History가 있어야 Prediction이 가능하다.** 지난 여름캠프 데이터가 없으면 윈터캠프 모집 예측은 일반 Knowledge에만 의존해야 한다.

---

## 5. Context Scope

Context는 세 가지 범위를 가진다.

```
Global Context
└── Goal-level Context
      └── Task-level Context
```

| Scope | 의미 | 예 |
|---|---|---|
| **Global** | 모든 Goal이 공유 | 사용자 프로필, 조직 정보, 지역, 시간대 |
| **Goal-level** | 특정 Goal에 종속 | 현재 등록자 20명, 윈터캠프 일정 |
| **Task-level** | 특정 Task 실행 중 생성/사용 | 광고 A안의 어제 CTR 3.2% |

### Scope 규칙

1. 하위 Scope는 상위 Scope를 **상속**한다. Task는 Goal Context와 Global Context를 모두 볼 수 있다.
2. 충돌 시 **더 구체적인(하위) Scope가 우선**한다.
3. Task-level Context 중 Goal 전체에 의미 있는 것은 Goal-level로 **승격(Promotion)** 될 수 있다. 예: 광고 실험에서 발견한 `학부모 타겟이 학생 타겟보다 전환율 3배` 는 Goal-level 사실이다.

---

## 6. Context Freshness

Context는 **시간이 지나면 부패한다.** 오래된 Context 위의 추론은 오답을 만든다.

```
Fresh → Stale → Expired
```

| 상태 | 의미 | 시스템 반응 |
|---|---|---|
| **Fresh** | TTL 이내 | 그대로 사용 |
| **Stale** | TTL 초과, 만료 전 | 사용 가능하나 Confidence 감점, 갱신 시도 |
| **Expired** | 만료 | 추론에 사용 금지, 재수집 필수 |

TTL은 항목의 성격에 따라 다르다.

| 항목 | TTL 예 |
|---|---|
| 광고 CTR | 1일 |
| 현재 등록자 수 | 1일 |
| 경쟁 학원 현황 | 30일 |
| 지역/조직 정보 | 180일 |

**Freshness는 Intent Confidence([e002-intent.md §8](e002-intent.md))의 입력이다.** Stale한 Context로 추론한 Intent는 Confidence가 깎인다.

---

## 7. Context 수집·갱신 규칙

### 수집 (Collection)

Context는 네 가지 경로로 수집된다.

| 경로 | 예 | 신뢰도 |
|---|---|---|
| **사용자 입력** | "예산은 300만원이야" | 높음 |
| **시스템 관측** | 실행 결과, 등록 DB 조회 | 높음 |
| **외부 소스** | 검색, API, 시장 데이터 | 중간 |
| **추정(Inferred)** | "신규 학원이므로 인지도 낮을 것" | 낮음 — 반드시 `inferred` 표시 |

**추정된 Context는 사실인 척하면 안 된다.** 추정 표시 없는 추정은 시스템 전체의 신뢰를 오염시킨다.

### 갱신 (Update)

```
Context 변경 감지
  ↓
영향 범위 계산 (어느 Goal / Intent / Plan이 이 항목을 참조하는가)
  ↓
Freshness 갱신
  ↓
Goal Propagation 트리거 (필요 시)
```

예)

```
광고 예산: 300만원 → 100만원 (사용자 입력)
  ↓
참조 추적: goal_001, intent_001(홍보), plan_003
  ↓
학생 모집 예상: 100명 → 65명
  ↓
Planner 재계산
```

이것은 [e001a-goal-graph.md §14 Goal Propagation](e001a-goal-graph.md)의 실제 발화 지점이 대부분 **Context 변경**임을 의미한다.

---

## 8. Canonical Context Representation

```json
{
  "context_id": "ctx_001",
  "scope": "Goal",
  "goal_id": "goal_001",
  "current_state": {
    "등록자": { "value": 20, "unit": "명" }
  },
  "environment": {
    "지역": "홍대",
    "시즌": "겨울방학"
  },
  "user_profile": {
    "조직": "신규 학원, 개원 6개월"
  },
  "history": [
    { "event": "여름캠프", "결과": "등록 35명" }
  ],
  "available_resources": {
    "예산": { "value": 3000000, "unit": "원" }
  },
  "items_meta": [
    {
      "key": "current_state.등록자",
      "source": "user_input",
      "collected_at": "2026-08-04T09:00:00Z",
      "ttl_hours": 24,
      "freshness": "Fresh"
    }
  ]
}
```

기계가 읽을 수 있는 스키마: [`context.schema.json`](../intent-os-spec/schemas/context.schema.json)

---

## 9. Context Loading Algorithm

Runtime의 각 단계는 Context를 이렇게 로드한다.

```
요청 (Goal / Intent / Task / Decision)
  ↓
Scope 결정 (Global + Goal + Task 병합)
  ↓
Freshness 검사
  ↓
Expired 항목 → 재수집 큐
Stale 항목   → 사용 + 갱신 시도 + Confidence 감점 표시
  ↓
Relevance 필터 (이 추론에 필요한 항목만)
  ↓
Context Snapshot 생성 → 추론 엔진 전달
```

**전체 Context를 항상 전달하지 않는다.** 필요한 부분만 선별하는 것이 비용과 정확도 모두에 유리하다.

---

## 10. 다른 Entity와의 관계

```
        ┌── Goal (e001)      : Gap 계산의 기준점
        ├── Intent (e002)    : 추론의 Evidence
Context ┼── Task (e005)      : 실행 파라미터 공급
        ├── Decision (e009)  : Resource 선택의 입력
        └── Memory (e010)    : 저장소 ↔ 스냅샷 관계
```

| Entity | 관계 |
|---|---|
| **Goal** [e001-goal.md](e001-goal.md) | Goal의 `context` 속성은 이 Entity에 대한 참조로 대체된다 |
| **Intent** [e002-intent.md](e002-intent.md) | Intent Extraction의 Gap Analysis와 Evidence가 Context에서 나온다 |
| **Constraint** [e004-constraint.md](e004-constraint.md) | Context의 사실이 Constraint의 규칙으로 변환될 수 있다 (`가용 예산 300만원` → `예산 ≤ 300만원`) |
| **Decision** (e009, 예정) | Decision Engine은 Historical Data를 Context/Memory에서 공급받는다 ([Volume 3 Stage 4](../v3-runtime.md)) |
| **Memory** (e010, 예정) | Context는 Memory에서 로드된 현재 추론용 스냅샷이다 |

---

## 11. Open Issues (v1.0)

### Context와 Memory의 경계

§2에서 "Memory에서 선별해 로드한 스냅샷"으로 정의했으나, 쓰기 방향(실행 중 생성된 Task-level Context가 언제 Memory로 영구화되는가)의 규칙이 없다. Entity 010에서 함께 확정한다.

### Freshness TTL의 산정

§6의 TTL은 예시 값이다. 항목 유형별 기본 TTL 테이블과, 학습을 통한 TTL 자동 보정(변화가 잦은 항목은 TTL 단축)이 필요하다.

### Context 충돌

사용자 입력(`등록자 25명`)과 시스템 관측(`DB상 20명`)이 충돌할 수 있다. v1.0은 "신뢰도 높은 출처 우선 + 사용자에게 고지" 원칙만 정하고, 상세 해소 프로토콜은 보강이 필요하다.

### 개인정보와 Context

User Profile과 History는 개인정보를 포함한다. 보존 기간, 접근 범위, 삭제 요청 처리는 별도 정책 명세가 필요하다.

### 앞으로 보강해야 할 항목

- Context 항목 표준 키 체계 (온톨로지)
- Context Diff / Versioning (스냅샷 간 변경 추적)
- Relevance 필터 알고리즘 상세화
- 실제 예시 30~50개
