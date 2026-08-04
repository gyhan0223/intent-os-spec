# Entity 018: Risk

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Risk is an identified possibility of an adverse event that would harm Goal achievement, carrying an estimated likelihood, impact, an early-warning signal, and a defined response.**

> Risk는 Goal 달성을 해칠 수 있는 **나쁜 사건의 가능성**으로서 식별된 것이며, 추정 발생확률·영향도·조기 경보 신호·정해진 대응책을 함께 갖는다.

여기서 중요한 단어는 **식별된(Identified)** 이다.

식별되지 않은 위험은 Risk가 아니라 그냥 불확실성이다. **Risk Entity의 존재 이유는 "막연한 불안"을 "관리 가능한 항목"으로 바꾸는 것이다.**

```
불확실성   "광고가 잘 안 될 수도 있는데…"        → 관리 불가
Risk       "인스타그램 CTR이 목표 1.5% 미만일
            가능성 0.4, 영향 high, 대응: 검색
            광고로 예산 40% 이전"                 → 관리 가능
```

---

## 2. Risk는 무엇이 아닌가?

### Risk는 Assumption이 아니다

❌ `광고비 300만원이 유지된다` — 이건 [Assumption](e017-assumption.md)이다.

```
Assumption   광고비 300만원이 유지된다     (참이라고 믿는 것)
    │
    │ 이 믿음이 깨질 가능성
    ▼
Risk         광고비가 삭감된다             (일어나면 나쁜 사건)
             likelihood 0.3 × impact 0.8
```

**Assumption은 긍정문, Risk는 부정문이다.** 하나의 Assumption에는 대개 하나의 Risk가 대응하지만, Assumption 없이 존재하는 Risk도 있다(경쟁사의 신규 진입 등).

### Risk는 Constraint가 아니다

❌ `광고비는 300만원을 넘을 수 없다` — 이건 [Constraint](e004-constraint.md)다.

| | Constraint | Risk |
|---|---|---|
| 성격 | 절대 넘으면 안 되는 선 | 일어날지도 모르는 사건 |
| 상태 | 항상 유효 | 확률적 |
| 위반/발생 시 | 즉시 차단 | 대응책 발동 |

### Risk는 Failure가 아니다

❌ `exe_219가 429 오류로 실패함` — 이건 이미 일어난 [Execution](e013-execution.md)의 실패다.

Risk는 **아직 일어나지 않은** 것이다. 일어나면 `Materialized`로 전이하고, 그 순간부터는 대응(Issue 처리)의 영역이다.

```
Risk (미발생)  →  Materialized (발생)  →  대응 Task 실행
```

### Risk는 낮은 Confidence가 아니다

❌ `Decision의 confidence가 0.54다` — 이건 예측 신뢰도이고, [Decision](e009-decision.md)의 Escalation 조건이다.

낮은 Confidence는 Risk의 **원인 지표**일 수는 있지만 Risk 자체는 아니다. Risk는 "무엇이 일어나서 무엇을 해치는가"를 문장으로 서술한 것이다.

### Risk는 Issue가 아니다

Issue는 **이미 문제가 된 것**이다. Risk는 문제가 될 가능성이다. 둘을 같은 목록에서 관리하면 "대응해야 할 것"과 "지켜봐야 할 것"이 섞인다.

---

## 3. Design Principles

### Rule RSK-001 — Severity는 발생확률 × 영향도다

$$Severity = Likelihood \times Impact$$

| Severity | 범위 | 취급 |
|---|---|---|
| Critical | 0.6 ~ 1.0 | 즉시 대응 계획 필수. 인간 승인 필요 |
| High | 0.35 ~ 0.6 | 대응 계획 필수 |
| Medium | 0.15 ~ 0.35 | 모니터링 + 대응 계획 |
| Low | 0.0 ~ 0.15 | 모니터링만 |

**Severity가 아니라 Likelihood와 Impact를 각각 기록한다.** 곱만 남기면 "거의 안 일어나지만 일어나면 치명적"과 "자주 일어나지만 사소함"이 구분되지 않는다.

### Rule RSK-002 — 대응 전략이 필수다

| 전략 | 의미 | 예 |
|---|---|---|
| `avoid` | 위험을 만드는 활동 자체를 하지 않는다 | 신규 채널 테스트를 이번 시즌엔 제외 |
| `mitigate` | 발생확률 또는 영향을 낮춘다 | 광고 예산을 2개 채널로 분산 |
| `transfer` | 위험을 외부로 옮긴다 | 성과 기반 계약으로 대행사에 이전 |
| `accept` | 감수한다 | 경쟁사 할인은 통제 불가. 감수 |
| `contingency` | 발생 시에만 발동할 대비책을 준비한다 | CTR 미달 시 검색 광고로 예산 이전 |

`accept`는 **명시적 승인이 필요하다**(Rule RSK-005).

### Rule RSK-003 — 소유자(Owner)가 있어야 한다

주인 없는 Risk는 관리되지 않는다. `owner`는 인간 또는 [Agent](e023-agent.md)다.

### Rule RSK-004 — 조기 경보 지표가 있어야 한다

"언제 이 Risk가 현실이 되고 있다고 판단하는가"를 관측 가능한 지표로 표현한다.

- ✅ `일 CTR < 1.0%가 3일 연속`
- ❌ `광고 성과가 나쁘면`

이 지표가 없으면 Risk는 문서로만 존재하고 아무도 보지 않는다.

### Rule RSK-005 — accept는 명시적 승인이 필요하다

시스템이 스스로 "이 위험은 감수하자"고 결정할 수 없다. `accepted_by`와 `accepted_at`이 필수다. 이는 [Assumption](e017-assumption.md)의 INV-ASM-06과 같은 원칙이다.

### Rule RSK-006 — Risk는 Plan 또는 Goal에 귀속된다

떠다니는 Risk는 없다. Plan이 폐기되면 그 Plan에만 속한 Risk도 `Closed`가 된다.

### Rule RSK-007 — 발생한 Risk는 지우지 않는다

`Materialized`된 Risk는 **가장 값진 학습 데이터**다. "이 유형의 Risk를 우리는 0.3으로 봤는데 실제로 일어났다"가 다음 계획의 확률 추정을 보정한다.

### Rule RSK-008 — 비가역 작업의 Risk는 별도로 다룬다

되돌릴 수 없는 작업(광고 집행, 메시지 발송, 외부 공개)은 impact를 한 단계 올려 평가한다. [Artifact §6.1](e016-artifact.md)의 `Published` 비대칭성과 같은 이유다.

---

## 4. Attributes

```
Risk
├── Identity
│   ├── risk_id
│   ├── scope           (goal_id / plan_id)
│   └── type
├── Assessment
│   ├── statement
│   ├── likelihood
│   ├── impact
│   ├── severity
│   └── assessed_at
├── Detection
│   ├── early_warning
│   └── trigger_condition
├── Response
│   ├── strategy
│   ├── response_plan
│   ├── contingency_ref
│   └── residual_severity
├── Ownership
│   ├── owner
│   ├── accepted_by
│   └── accepted_at
├── Link
│   ├── source_assumption_id
│   └── materialized_event_id
└── Status
    └── status
```

| 속성 | 의미 | 예 |
|---|---|---|
| **risk_id** | 식별자 | `rsk_007` |
| **scope** | 귀속 대상 | `{ "goal_id": "goal_001", "plan_id": "plan_014" }` |
| **type** | 분류 (§4.1) | `cost` |
| **statement** | 위험 서술 | `광고비가 9월부터 삭감되어 목표 모집 인원에 미달한다` |
| **likelihood** | 발생확률 | `0.3` |
| **impact** | 영향도 | `0.8` |
| **severity** | 곱 (자동 계산) | `0.24` → Medium |
| **early_warning** | 조기 경보 지표 | `{ "metric": "monthly_spend_ratio", "threshold": 0.6 }` |
| **trigger_condition** | 발생 판정 조건 | `월 집행 가능액 < 3,000,000 KRW` |
| **strategy** | 대응 전략 | `contingency` |
| **response_plan** | 대응 내용 | `유료 광고 비중 축소, SEO·자연 유입 강화` |
| **contingency_ref** | 대비 계획 참조 | `plan_014_fallback` |
| **residual_severity** | 대응 후 잔여 위험 | `0.10` |
| **owner** | 담당 | `human:대표` |
| **source_assumption_id** | 대응하는 가정 | `asm_012` |
| **materialized_event_id** | 발생 시점의 Event | `null` |
| **status** | 상태 (§6) | `Monitored` |

### 4.1 Risk Types

```
Risk
├── resource     Resource 가용성·성능 관련
├── cost         비용 초과·예산 삭감
├── schedule     일정 지연
├── quality      결과 품질 미달
├── dependency   선행 Task·외부 시스템 의존
├── compliance   규정·정책·법규 위반
├── external     경쟁·시장·규제 등 외부 요인
└── irreversible 되돌릴 수 없는 작업의 위험
```

| Type | 예 | 주 대응 |
|---|---|---|
| `resource` | 김 카피라이터가 12월에 불가용 | contingency (AI 검수 대체) |
| `cost` | 광고비 삭감 | contingency |
| `schedule` | 랜딩페이지가 12/1 전에 완성되지 않음 | mitigate (병렬화) |
| `quality` | 카피가 브랜드 톤에 맞지 않음 | mitigate (인간 검수 추가) |
| `dependency` | 광고 플랫폼 API 장애 | mitigate (대체 채널 준비) |
| `compliance` | 과장 광고 표현으로 심의 반려 | avoid (금칙어 사전 검사) |
| `external` | 경쟁 학원의 대규모 할인 | accept |
| `irreversible` | 잘못된 카피로 300만원 집행 | mitigate (10만원 파일럿 선행) |

### 4.2 Risk Matrix

| | Impact 낮음 (0.0~0.3) | Impact 중간 (0.3~0.7) | Impact 높음 (0.7~1.0) |
|---|---|---|---|
| **Likelihood 높음 (0.7~1.0)** | Medium — 모니터링 | High — 대응 필수 | **Critical — 즉시 대응** |
| **Likelihood 중간 (0.3~0.7)** | Low | Medium | High |
| **Likelihood 낮음 (0.0~0.3)** | Low | Low | **Medium — 단, 비가역이면 High** |

**우하단이 함정이다.** "거의 안 일어나지만 일어나면 끝장"인 위험은 확률만 보면 무시되지만, 되돌릴 수 없으면 Critical로 취급해야 한다(Rule RSK-008).

---

## 5. Invariants

### INV-RSK-01 — 모든 Risk는 owner를 가진다

| | |
|---|---|
| **위반 시** | 생성 시 Plan의 소유자를 기본값으로 지정하고 경고를 남긴다 |

### INV-RSK-02 — severity가 High 이상이면 response_plan이 필수다

| | |
|---|---|
| **위반 시** | Plan을 `Active`로 전이할 수 없다. 대응 계획 작성을 요구 |

### INV-RSK-03 — strategy가 accept면 accepted_by와 accepted_at이 존재한다

| | |
|---|---|
| **위반 시** | 승인 요청으로 전환. 시스템이 스스로 감수를 결정할 수 없다 (Rule RSK-005) |

### INV-RSK-04 — likelihood와 impact는 0.0~1.0 범위다

| | |
|---|---|
| **위반 시** | 생성 거부. 범위 밖 값은 평가 척도 오류의 신호다 |

### INV-RSK-05 — Materialized된 Risk는 삭제되지 않는다

| | |
|---|---|
| **위반 시** | 삭제 차단. 확률 추정 보정의 근거 데이터다 (Rule RSK-007) |

### INV-RSK-06 — residual_severity는 severity 이하다

대응책이 위험을 키울 수는 없다.

| | |
|---|---|
| **위반 시** | 대응 계획 자체가 새로운 Risk를 만들고 있다는 신호. 별도 Risk로 분리하고 원 Risk의 잔여 위험을 재산정 |

### INV-RSK-07 — Critical Risk가 미해결이면 비가역 Execution을 시작할 수 없다

| | |
|---|---|
| **위반 시** | Execution 생성을 차단하고 Event를 발행 ([e013 §9](e013-execution.md)의 사전 검사) |
| **근거** | 300만원 집행처럼 되돌릴 수 없는 작업에 미대응 Critical Risk가 걸려 있으면 안 된다 |

---

## 6. Lifecycle

```
Identified → Assessed → Mitigating → Monitored ──▶ Closed
                 │           │            │
                 │           │            ▼
                 │           └──────▶ Materialized ──▶ Resolved ──▶ Closed
                 │
                 └──▶ Accepted (명시적 승인) ──▶ Monitored
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Identified** | 식별됨. 아직 평가 전 | Planner 또는 사람이 등록 |
| **Assessed** | likelihood·impact 산정 완료 | 평가 수행 |
| **Accepted** | 감수 승인됨 | 인간의 명시적 승인 (INV-RSK-03) |
| **Mitigating** | 대응책 실행 중 | 대응 Task 시작 |
| **Monitored** | 대응 완료 또는 감수. 지표 감시 중 | 대응 Task 완료 |
| **Materialized** | 실제로 발생함 | `trigger_condition` 충족 |
| **Resolved** | 발생한 위험의 수습 완료 | 대응 Task 완료 |
| **Closed** | 관리 종료 (Goal 완료, Plan 폐기, 기간 경과) | Plan 종료 |

### 6.1 Materialized 처리 흐름

```
early_warning 지표 도달
  ↓
Event 발행 (risk.warning)  → owner에게 알림
  ↓
trigger_condition 충족?
  ├── No  → Monitored 유지, 감시 주기 단축
  └── Yes → Materialized
       ↓
     ① source_assumption의 상태를 Invalidated로 전이 (있는 경우)
     ② strategy별 분기
        contingency → contingency_ref 활성화
        mitigate    → 대응 Task 즉시 실행
        accept      → 영향 기록만, 계획 유지
        avoid/transfer → 해당 활동 중단
     ③ Plan 재평가 (Suspended 또는 Replanning)
     ④ 확률 추정 보정 신호 발행 → Memory (e010)
```

**②의 순서가 중요하다.** Assumption 무효화가 먼저 일어나야 [INV-10](e000a-entity-relationships.md)이 지켜진다.

---

## 7. Relationships

```
Assumption 017 ──1:0..1──▶ Risk 018 ──▶ Plan 008 (대응 계획)
                              │
Goal 001 ──1:0..N────────────┤
Plan 008 ──1:0..N────────────┤
                              ├──차단──▶ Execution 013 (Critical 미해결 시)
                              ├──발생──▶ Event 020
                              └──보정──▶ Memory 010 → Knowledge 011
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Assumption](e017-assumption.md) | 가정이 깨질 가능성이 Risk다 | `Assumption 1:0..1 Risk` |
| [Plan](e008-plan.md) | Risk는 Plan에 귀속된다 | `Plan 1:0..N Risk` |
| [Goal](e001-goal.md) | Goal 수준의 Risk도 존재한다 | `Goal 1:0..N Risk` |
| [Decision](e009-decision.md) | Utility 공식의 `Risk` 항에 반영된다 | `Risk N:M Decision` |
| [Execution](e013-execution.md) | Critical Risk는 비가역 실행을 차단한다 | `Risk 1:N Execution` |
| [Constraint](e004-constraint.md) | 대비 개념. 확실 vs 확률적 | — |
| [Policy](e019-policy.md) | 어떤 Risk 수준에서 승인이 필요한지 규정 | `Policy 1:N Risk` |
| [Memory](e010-memory.md) | 발생 이력이 확률 추정을 보정한다 | `Risk 1:0..N Memory` |

### 7.1 Decision Utility와의 연결

[Volume 4-A §8](../v4a-decision-engine-detail.md)의 Utility 공식에는 `Risk` 항이 있다.

$$Utility = (Q \times W_q) + (S \times W_s) + (R \times W_r) - (C \times W_c) - (L \times W_l) - Risk$$

여기서 `Risk`는 **해당 후보를 선택했을 때의 잔여 위험 합계**다.

```
후보 Claude   관련 Risk: rsk_012 (품질 미달, residual 0.05)     → Risk 항 0.05
후보 GPT      관련 Risk: rsk_015 (rate limit, residual 0.12)   → Risk 항 0.12
후보 김 카피   관련 Risk: rsk_020 (일정 지연, residual 0.18)     → Risk 항 0.18
```

Risk Entity가 없으면 이 항은 임의의 숫자가 된다. **Risk를 명시적으로 관리해야 Utility가 설명 가능해진다.**

---

## 8. Canonical Representation

```json
{
  "risk_id": "rsk_007",
  "scope": { "goal_id": "goal_001", "plan_id": "plan_014" },
  "type": "cost",
  "statement": "광고비가 9월부터 삭감되어 윈터캠프 목표 모집 인원 100명에 미달한다",
  "likelihood": 0.3,
  "impact": 0.8,
  "severity": 0.24,
  "severity_band": "Medium",
  "assessed_at": "2026-08-01T10:30:00Z",
  "early_warning": {
    "metric": "monthly_spend_ratio",
    "threshold": 0.6,
    "window": "P10D"
  },
  "trigger_condition": "월 집행 가능액 < 3000000 KRW",
  "strategy": "contingency",
  "response_plan": "유료 광고 비중을 60%→35%로 축소하고 SEO·자연 유입 강화. 상담 전환율 개선 Task 우선순위 상향",
  "contingency_ref": "plan_014_fallback",
  "residual_severity": 0.10,
  "owner": "human:대표",
  "accepted_by": null,
  "accepted_at": null,
  "source_assumption_id": "asm_012",
  "materialized_event_id": null,
  "status": "Monitored"
}
```

기계가 읽을 수 있는 스키마: [`risk.schema.json`](../intent-os-spec/schemas/risk.schema.json)

---

## 9. Validation Rules

```
Risk 생성 요청
  ↓
scope 존재 확인 (Goal / Plan) ── 없으면 반려 (RSK-006)
  ↓
statement 검사 — "무엇이 일어나서 무엇을 해치는가" 형식인가
  ── 부정 사건 + 결과가 명시되지 않으면 반려
  ↓
likelihood / impact 범위 검사 (INV-RSK-04)
  ↓
severity = likelihood × impact 계산 → severity_band 부여
  ↓
type = irreversible 이면 impact 한 단계 상향 (RSK-008)
  ↓
early_warning 관측 가능성 검사 (RSK-004) ── 없으면 반려
  ↓
strategy 확인 (RSK-002)
  ├── accept       → accepted_by 필수 (INV-RSK-03). 없으면 승인 요청
  ├── contingency  → contingency_ref 필수
  └── mitigate     → response_plan 필수
  ↓
severity_band ∈ {High, Critical} 이면 response_plan 필수 (INV-RSK-02)
  ↓
residual_severity ≤ severity 확인 (INV-RSK-06)
  ↓
owner 확인 (INV-RSK-01) ── 없으면 Plan owner 상속 + 경고
  ↓
source_assumption_id 있으면 존재 확인 및 양방향 링크 설정
  ↓
Identified 생성 → 평가 큐 등록 → Event 발행
```

### 9.1 Risk 식별 — Planner의 의무

Plan 생성 시 최소한 아래 관점에서 Risk를 탐색한다. [Assumption 추출](e017-assumption.md)과 짝을 이룬다.

```
Plan 초안
  ↓
① 모든 Assumption을 부정문으로 뒤집어 Risk 후보 생성
     "광고비 300만원 유지" → "광고비 삭감"
  ↓
② Task Graph의 단일 실패점(SPOF) 탐색
     선행 Task 하나가 여러 후행을 막는 지점 → dependency Risk
  ↓
③ 비가역 Task 식별
     Artifact가 Published로 가는 Task → irreversible Risk
  ↓
④ Constraint 여유 검사
     Hard Constraint에 대한 여유가 20% 미만인 항목 → cost/schedule Risk
  ↓
⑤ 과거 유사 Goal의 Materialized Risk 조회 (Memory)
     같은 유형이 반복될 가능성 → likelihood 초기값의 근거
  ↓
Risk 목록 확정 → severity 정렬 → High 이상은 response_plan 필수
```

**⑤가 학습의 접점이다.** 시스템은 과거에 실제로 발생한 Risk를 기억하고, 새 Plan에서 같은 유형의 `likelihood`를 상향한다.

---

## 10. Examples

### 예시 1 — Assumption에서 파생된 Risk

```
asm_012  광고비 월 300만원 유지  confidence 0.85
   │ 뒤집기
   ▼
rsk_007  광고비 삭감으로 모집 목표 미달
         likelihood 0.15 (= 1 − 0.85)
         impact 0.8
         severity 0.12 → Low
```

초기에는 Low였다. 그런데 8월 집행 비율이 62%로 조기 경보에 걸리면서 재평가된다.

```
2026-08-14  early_warning 도달
   ▼
rsk_007  재평가: likelihood 0.15 → 0.5
         severity 0.40 → High
         → INV-RSK-02 발동: response_plan 필수
         → contingency_ref: plan_014_fallback 준비 완료
```

### 예시 2 — 비가역 Risk

```json
{
  "risk_id": "rsk_031",
  "scope": { "goal_id": "goal_001", "plan_id": "plan_014" },
  "type": "irreversible",
  "statement": "브랜드 톤에 맞지 않는 카피로 300만원 광고가 집행되어 회수 불가능한 비용과 브랜드 훼손이 발생한다",
  "likelihood": 0.12,
  "impact": 0.95,
  "severity": 0.114,
  "severity_band": "High",
  "strategy": "mitigate",
  "response_plan": "① 김 카피라이터 인간 검수 필수 ② 10만원 파일럿 집행 후 CTR 확인 ③ 파일럿 CTR ≥ 1.2%일 때만 본 집행",
  "residual_severity": 0.03,
  "owner": "human:대표",
  "status": "Mitigating"
}
```

원래 확률만 보면 `0.114`는 Low 구간이다. `type: irreversible`이라 Rule RSK-008에 의해 impact가 상향되고 High로 분류된다. 그 결과 파일럿(Rehearsal Execution, [e013 §4.1](e013-execution.md))이 계획에 삽입된다.

### 예시 3 — Materialized

```
2026-08-15  대표: "9월부터 200만원"
   ▼
rsk_007 → Materialized
   ├── asm_012 → Invalidated
   ├── plan_014 → Suspended
   ├── contingency 발동 → plan_014_fallback 활성화
   └── Memory 기록:
       "cost 유형 Risk, 학원 도메인, 시즌 캠페인
        → 예상 likelihood 0.15 / 실제 발생
        → 다음 유사 Plan의 초기 likelihood를 0.3으로 상향"
```

### 예시 4 — Accept

```json
{
  "risk_id": "rsk_044",
  "scope": { "goal_id": "goal_001", "plan_id": "plan_014" },
  "type": "external",
  "statement": "경쟁 학원이 12월에 대규모 할인을 시행해 전환율이 하락한다",
  "likelihood": 0.45,
  "impact": 0.5,
  "severity": 0.225,
  "strategy": "accept",
  "response_plan": "통제 불가 요인. 가격 경쟁 대신 합격 실적 소구로 차별화 유지",
  "residual_severity": 0.225,
  "owner": "human:대표",
  "accepted_by": "human:대표",
  "accepted_at": "2026-08-01T11:00:00Z",
  "status": "Monitored"
}
```

`residual_severity`가 `severity`와 같다. **감수는 위험을 줄이지 않는다.** 다만 놀라지 않게 할 뿐이다.

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **대응책이 새로운 Risk를 만듦** | 별도 Risk로 등록한다(INV-RSK-06). "예산을 검색 광고로 옮긴다"는 대응이 "검색 광고 CPC 급등" Risk를 만든다면 그것은 다른 항목이다 |
| **같은 Risk가 여러 Plan에 존재** | 각 Plan에 개별 Risk로 둔다. 원인이 같아도 영향과 대응이 다르다. `related_risk_ids`로 묶는다 |
| **Risk가 발생했는데 영향이 없었음** | `Materialized → Resolved`. **impact 추정이 틀렸다는 학습 신호**로 기록한다. 다음 추정에서 impact를 하향 |
| **likelihood를 추정할 데이터가 전혀 없음** | 0.5(최대 무지)로 두고 `estimation_basis: "no_data"`를 명시한다. 임의의 낮은 값을 넣으면 위험이 은폐된다 |
| **Goal이 완료된 뒤 Risk가 발생** | `Closed` 상태의 Risk는 다시 열지 않는다. 새 Goal의 Risk로 등록한다 |
| **owner가 퇴사·부재** | Risk를 무주공산으로 두지 않는다. Plan owner로 자동 승계하고 알림을 발행한다 |
| **Critical Risk인데 대응이 불가능** | `accept` + 인간 승인 + **Goal 목표치 조정 제안**을 함께 생성한다. 대응 불가한 Critical을 방치한 채 실행하는 것은 INV-RSK-07 위반이다 |
| **조기 경보만 계속 울리고 발생하지 않음** | 임계값이 너무 민감하다. 3회 이상 오경보 시 임계값 재조정을 제안한다. 경보 피로가 진짜 경보를 무시하게 만든다 |
| **Risk 목록이 50개를 넘음** | severity 상위 10개만 능동 관리하고 나머지는 `passive`로 표시한다. 어떤 것이 능동 관리에서 빠졌는지 명시적으로 기록한다 ([Assumption §11](e017-assumption.md)과 동일 원칙) |

---

## 12. Open Issues (v1.0)

### likelihood 추정의 데이터 기반화

현재 대부분 사람이 부여한다. Materialized 이력이 쌓이면 유형·도메인별 기저율(Base Rate)을 계산할 수 있지만, 표본이 적을 때의 추정 방법(베이지안 사전분포 등)이 미정이다.

### Risk 간 상관관계

"광고비 삭감"과 "일정 지연"은 독립이 아니다. 여러 Risk가 동시에 발생할 확률을 독립 가정으로 계산하면 과소평가된다. 상관 구조의 표현이 없다.

### Utility 공식의 Risk 항 산출

§7.1에서 `Risk` 항을 "관련 Risk의 잔여 위험 합계"로 정의했으나, 합·최댓값·가중합 중 무엇이 옳은지 근거가 없다. Decision Engine 명세와 함께 확정해야 한다.

### Impact의 단위

현재 0.0~1.0 무차원 값이다. 실제로는 "Goal 달성률 하락 %"나 "손실 금액"으로 표현하는 편이 비교 가능하다. 정규화 방법이 필요하다.

### 앞으로 보강해야 할 항목

- Risk 유형별 표준 대응 템플릿
- 오경보율(False Alarm Rate) 추적과 임계값 자동 조정
- Materialized Risk에서 Knowledge로의 승격 규칙 ([e011](e011-knowledge.md)과 연동)
- 실제 예시 30~50개
