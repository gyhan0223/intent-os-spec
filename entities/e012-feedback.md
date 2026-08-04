# Entity 012: Feedback

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Feedback is an evaluative signal about an outcome, originating from a user, from user behavior, or from the system itself, that drives improvement.**

> Feedback은 실행 결과(Outcome)에 대한 평가 신호이다. 사용자, 사용자의 행동, 또는 시스템 자신으로부터 발생하며, 시스템 개선의 입력이 된다.

여기서 중요한 단어는 **Evaluative Signal**이다.

Feedback은 결과 그 자체가 아니라, **결과가 좋았는지 나빴는지에 대한 판단의 재료**다.

### Entity / Process / Runtime State 구분

| 분류 | 예 | 설명 |
|---|---|---|
| **Runtime State** | Outcome | 실행이 만든 **결과 상태** |
| **Entity** | **Feedback** | 그 결과에 대한 **평가 신호의 기록** |
| **Process** | Learning | Feedback을 소비해 Memory/Knowledge를 갱신하는 **수행 과정** |

Outcome은 "무엇이 나왔는가"이고, Feedback은 "그것이 어땠는가"이다. Learning(Process)은 Feedback(Entity)을 읽어 Memory와 Knowledge(Entity)를 갱신한다.

```
Execution (Process)
   ↓
Outcome (Runtime State)      ← 무엇이 나왔는가
   ↓
Feedback (Entity)            ← 그것이 어땠는가
   ↓
Learning (Process)
   ↓
Memory / Knowledge 갱신 (Entity)
```

---

## 2. Feedback은 무엇이 아닌가?

이게 정의보다 훨씬 중요하다.

### Feedback은 Outcome이 아니다

❌ `광고 카피 3종이 생성됨` — 이건 **Outcome(Runtime State)** 이다.

✅ `사용자가 그중 2종을 폐기하고 1종을 수정 요청함` — 이것이 Feedback이다.

Outcome은 평가 없이 존재할 수 있지만, Feedback은 반드시 **대상 Outcome을 가리켜야** 한다.

### Feedback은 새로운 Goal이 아니다

❌ `이번엔 학부모 말고 학생 대상으로 써줘` — 표면적으로는 수정 요청(Feedback)처럼 보이지만, 대상 Audience가 바뀌었으므로 **Goal/Intent의 변경**이 섞여 있다.

시스템은 이를 분리해야 한다.

```
Feedback:    기존 카피는 대상에게 맞지 않았다 (부정 신호)
Goal 변경:   Audience: 학부모 → 학생
```

### Feedback은 Memory가 아니다

⚠️ Feedback은 발생 즉시 관련 Memory에 **첨부**되지만, Feedback 자체는 별도 Entity다. 하나의 Memory에 여러 Feedback이 시차를 두고 붙을 수 있다. (생성 직후 만족 → 일주일 뒤 성과 부진)

### Feedback은 Learning이 아니다

❌ `Feedback으로 Resource 점수를 조정하기` — 이건 **Process**다. Feedback은 그 Process의 **입력 신호(Entity)** 다. 신호와 처리 과정을 혼동하면 "Feedback 1건 = 즉시 학습"이라는 위험한 설계가 나온다.

---

## 3. Feedback의 조건

### Rule F-001 — 반드시 대상(Target)을 가진다

무엇에 대한 평가인지(Outcome / Execution / Decision / Plan)가 명시되지 않은 신호는 Feedback으로 저장하지 않는다.

### Rule F-002 — 원시 신호와 해석을 분리한다

`사용자가 결과를 3회 재생성했다`는 **원시 신호(사실)** 다. `사용자가 불만족했다`는 **해석**이다. Feedback Entity는 원시 신호를 보존하고, 해석은 별도 필드에 Confidence와 함께 기록한다. 재시도는 불만족일 수도, 단순 탐색일 수도 있다.

### Rule F-003 — Single Feedback ≠ Learning Update

Feedback 1건으로 Knowledge나 Resource 프로필을 갱신하지 않는다. ([Volume 5 §13 Learning Safety](../v5-learning-engine.md)) 단, **명시적 Constraint 위반 신고**(법률, 안전)는 예외로 즉시 반영한다.

### Rule F-004 — Implicit Feedback은 Explicit Feedback보다 낮은 가중치를 가진다

행동 추론은 틀릴 수 있다. 기본 가중치: `Explicit > Systemic > Implicit`.

### Rule F-005 — Feedback도 출처(Provenance)를 가진다

누가/무엇이, 언제, 어떤 채널로 발생시켰는지 기록한다. 악의적·오염된 Feedback을 사후 격리하기 위해서다.

---

## 4. Feedback Attributes

```
Feedback
├── Feedback ID
├── Source Type (Explicit / Implicit / Systemic)
├── Target
│     ├── Target Type (Outcome / Decision / Plan / Resource)
│     └── Target Ref
├── Signal (원시 신호)
├── Interpretation (해석)
│     ├── Sentiment (Positive / Negative / Neutral / Mixed)
│     └── Interpretation Confidence
├── Weight
├── Routing (갱신 대상 Entity 목록)
├── Provenance
├── Created At
└── Status
```

| 속성 | 의미 | 예 |
|---|---|---|
| **Feedback ID** | 고유 식별자 | `fb_0553` |
| **Source Type** | 출처 분류 | `Implicit` |
| **Target** | 무엇에 대한 평가인가 | `outcome_0871 (윈터캠프 카피 v2)` |
| **Signal** | 원시 신호 | `사용자가 결과를 사용하지 않고 3회 재생성` |
| **Sentiment** | 해석된 방향 | `Negative` |
| **Interpretation Confidence** | 해석의 확신도 | `0.7` |
| **Weight** | 학습 반영 가중치 | `0.4` |
| **Routing** | 어떤 Entity 갱신에 쓰이는가 | `[Resource Profile, Memory]` |
| **Provenance** | 발생 주체/채널 | `user_A / UI 재생성 버튼` |
| **Status** | 처리 상태 | `Routed` |

---

## 5. Feedback Source Types

모든 Feedback은 정확히 하나의 Source Type을 가진다.

```
Feedback
├── Explicit  — 사용자가 의도적으로 준 평가
├── Implicit  — 사용자 행동에서 추론된 신호
└── Systemic  — 시스템이 스스로 측정한 신호
```

| Type | 신호 예 | 특징 |
|---|---|---|
| **Explicit** | 별점, 좋아요/싫어요, `이 부분 고쳐줘`, `이건 쓰지 마` | 가장 신뢰도 높음. 그러나 드물다 |
| **Implicit** | 재생성/재시도, 결과 미사용, 복사 여부, 세션 이탈, 추가 질문 | 풍부하지만 해석이 필요하다 |
| **Systemic** | Success Metric 달성 여부 (`CTR 8% 목표 → 실제 5%`), 비용 초과, 실행 실패, SLA 위반 | 객관적. Goal의 Metric과 직결 |

### 예 — 하나의 Outcome, 세 종류의 Feedback

```
Outcome: 윈터캠프 인스타 광고 카피 게시

Explicit:  대표가 "톤이 너무 가벼워요" 수정 요청
Implicit:  마케팅팀이 카피 원문을 복사해감 (사용됨 = 약한 긍정)
Systemic:  2주 후 상담 신청 +30% (Goal Metric 달성 = 강한 긍정)
```

세 신호가 상충할 수 있다. 그래서 Feedback은 **집계 후에만** Learning에 반영된다.

---

## 6. Feedback Lifecycle

```
Captured → Interpreted → Routed → Aggregated → Consumed → Archived
                      ↘ Quarantined (오염 의심)
```

| 상태 | 의미 |
|---|---|
| **Captured** | 원시 신호 수집됨 |
| **Interpreted** | Sentiment/Confidence 해석 완료 |
| **Routed** | 갱신 대상 Entity 결정됨 |
| **Aggregated** | 동일 대상의 다른 Feedback과 집계됨 |
| **Consumed** | Learning이 반영 완료 |
| **Quarantined** | 이상 패턴(스팸, 조작 의심)으로 격리 |
| **Archived** | 보존 전용 |

---

## 7. Feedback Routing

**어떤 Feedback이 어떤 Entity를 갱신하는가.** 이것이 Feedback 명세의 핵심이다.

| Feedback 내용 | 갱신 대상 | 예 |
|---|---|---|
| 결과물 품질 평가 | **Resource 성능 프로필** | `Claude의 marketing_copy 점수 조정 근거` |
| 전략 자체에 대한 평가 | **Knowledge** (Task/Domain) | `감성 소구 전략 → 이 도메인에서 유효` 지지/반증 |
| 사용자 취향 신호 | **Knowledge** (User) | `사용자 A는 짧은 카피 선호` |
| 목표 재해석 요구 | **Goal** | `사실 학생 수보다 객단가가 문제였어` → Goal 수정 제안 |
| Metric 달성/미달 | **Memory** (Result 보강) + Goal Status | 상담 신청 +30% → mem_0142의 result 확정 |
| 실행 오류/비용 초과 | **Plan / Runtime 정책** | 재시도 정책, 예산 가드 조정 근거 |

### Routing 알고리즘

```
Feedback (Interpreted)
  ↓
Target Type 확인
  ↓
평가 축 분류 (품질? 전략? 취향? 목표? 비용?)
  ↓
갱신 대상 Entity 목록 결정 (복수 가능)
  ↓
각 대상의 집계 버킷에 적재
  ↓
버킷이 Learning 임계값 도달 → Learning Engine 호출
```

하나의 Feedback이 **여러 대상에 동시에 라우팅**될 수 있다. `톤이 너무 가벼워요`는 Resource 프로필(품질)과 User Knowledge(취향) 양쪽의 근거가 된다.

---

## 8. Feedback Loop — 전체 흐름

Intent OS가 시간이 지날수록 좋아지는 유일한 이유가 이 루프다.

```
Goal
  ↓
Decision (Resource/전략 선택)
  ↓
Execution (Process)
  ↓
Outcome (Runtime State)
  ↓
Feedback (Explicit + Implicit + Systemic)   ← e012
  ↓
Learning (Process)
  ↓
Memory 보강 / Knowledge 갱신                ← e010, e011
  ↓
다음 Decision 개선
  ↓
(반복)
```

예 — 학원 모집 캠페인 1사이클:

```
1. Goal:      학생 100명 모집
2. Decision:  카피 작성에 Claude 선택 (예측 점수 86)
3. Execution: 광고 카피 생성 → 집행
4. Outcome:   상담 신청 +30%
5. Feedback:  Systemic(Metric 달성) + Explicit(대표 만족)
6. Learning:  mem_0142 확정, knw_0007 지지 근거 +1
7. 다음 Decision: 유사 조건에서 Claude 예측 점수 86 → 94
```

이 루프는 [Volume 5 §11 Learning Feedback Loop](../v5-learning-engine.md)의 Entity 관점 표현이다.

---

## 9. Canonical Feedback Representation

```json
{
  "feedback_id": "fb_0553",
  "source_type": "Implicit",
  "target": {
    "target_type": "Outcome",
    "target_ref": "outcome_0871"
  },
  "signal": "사용자가 결과를 사용하지 않고 3회 재생성",
  "interpretation": {
    "sentiment": "Negative",
    "confidence": 0.7
  },
  "weight": 0.4,
  "routing": ["ResourceProfile", "Memory"],
  "provenance": {
    "actor": "user_A",
    "channel": "UI 재생성 버튼"
  },
  "created_at": "2026-08-04T10:22:00Z",
  "status": "Routed"
}
```

**이 구조만 Learning Engine으로 전달된다.**

기계가 읽을 수 있는 스키마: [`feedback.schema.json`](../intent-os-spec/schemas/feedback.schema.json)

---

## 10. Feedback 처리 알고리즘

```
신호 감지 (UI 이벤트 / Metric 관측 / 사용자 발화)
  ↓
Feedback인가? (대상 있는 평가 신호인가)
  ├── No  → 폐기 또는 Goal/Intent 변경 처리로 이관
  └── Yes
       ↓
Source Type 분류 (Explicit / Implicit / Systemic)
  ↓
Goal 변경 성분 분리 (Rule F-002, §2)
  ↓
해석 (Sentiment + Confidence)
  ↓
가중치 부여 (Rule F-004)
  ↓
오염 검사 (이상 빈도, 조작 패턴)
  ├── 의심 → Quarantined
  └── 정상
       ↓
Routing (§7)
  ↓
집계 → 임계값 도달 시 Learning 반영
```

---

## 11. 다른 Entity와의 관계

```
Outcome (Runtime State)
   ↓ 평가
Feedback (e012)
   ├──→ Memory (e010)          : 기록에 평가 신호 첨부
   ├──→ Knowledge (e011)       : 지지/반증 근거로 집계
   ├──→ Resource (예정)         : 성능 프로필 갱신 근거
   ├──→ Goal (e001)            : 목표 재해석/수정 제안
   └──→ Plan (e008)            : 전략 유효성 재평가
```

| Entity | 관계 |
|---|---|
| [Goal](e001-goal.md) | Systemic Feedback의 기준은 Goal의 Success Metric이다 |
| [Plan](e008-plan.md) | 전략 수준 Feedback은 Plan 평가로 라우팅된다 |
| [Memory](e010-memory.md) | Feedback은 Memory의 result/confidence를 보강한다 |
| [Knowledge](e011-knowledge.md) | 집계된 Feedback이 Knowledge의 지지/반증 근거가 된다 |
| Decision (예정) | Feedback 반영의 최종 목적지는 다음 Decision의 개선이다 |

---

## 12. Open Issues (v1.0)

### 지연된 Feedback의 귀속 (Attribution)

`2주 후 상담 신청 +30%`는 어느 Decision 덕분인가? 그 사이에 카피 수정, 예산 변경, 계절 요인이 섞여 있다. 인과 귀속은 [Volume 4-F §11 Causal Graph](../v4f-world-model.md)의 미해결 문제와 동일하다. v1.0에서는 **시간창 기반의 약한 귀속 + 낮은 가중치**로 처리한다.

### Implicit Feedback 해석의 오류율

`재생성 3회 = 불만족`이라는 해석 규칙 자체가 학습·검증 대상이다. 해석 규칙을 Knowledge로 취급할 것인지 결정이 필요하다.

### Feedback 조작 (Poisoning)

악의적 사용자가 특정 Resource를 반복적으로 낮게 평가하면 Global Knowledge가 오염될 수 있다. Quarantine 휴리스틱의 형식 정의가 없다.

### 부정 Feedback의 UX 비용

Explicit Feedback을 더 모으려고 사용자에게 평가를 강요하면 경험이 나빠진다. Implicit 신호 품질을 올리는 쪽이 우선이다.

### 앞으로 보강해야 할 항목

- 집계 함수의 형식 정의 (Source Type별 가중 평균? 베이지안?)
- Goal 변경 성분 분리 알고리즘의 상세화
- Feedback → Routing 규칙표의 완전 열거
- 실제 예시 30~50개
