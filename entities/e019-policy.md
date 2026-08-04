# Entity 019: Policy

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Policy is a machine-enforceable rule that governs what the system may or may not do, defined independently of any specific Goal, and taking precedence over optimization.**

> Policy는 시스템이 **무엇을 해도 되고 무엇을 하면 안 되는지**를 규정하는 기계 강제 가능한 규칙이며, 특정 Goal과 무관하게 정의되고 최적화보다 우선한다.

여기서 중요한 것은 **최적화보다 우선(Takes Precedence over Optimization)** 이다.

Decision Engine은 Utility가 가장 높은 선택을 한다. 그런데 **최적해가 규정 위반이면 그것은 해가 아니다.**

```
Utility 최고:  가장 싼 해외 Resource에 학부모 개인정보 전송  →  Policy 위반
                                                            ↓
                                      후보 생성 단계에서 제거된다
```

우선순위는 다음과 같다([INV-11](e000a-entity-relationships.md)).

```
Policy  >  Hard Constraint  >  Decision Utility  >  Soft Constraint
```

---

## 2. Policy는 무엇이 아닌가?

### Policy는 Constraint가 아니다

❌ `광고비는 300만원을 넘을 수 없다` — 이건 [Constraint](e004-constraint.md)다.

**이 구분이 가장 자주 틀린다.**

| | Constraint | Policy |
|---|---|---|
| 소속 | 특정 Goal / Task에 붙는다 | Goal과 무관하게 존재한다 |
| 출처 | 사용자가 Goal과 함께 말한다 | 조직·법규·보안이 정한다 |
| 수명 | Goal이 끝나면 사라진다 | 항구적 |
| 협상 | Soft면 완화 가능 | 협상 불가 (예외는 승인 절차로만) |
| 예 | "이번 캠프 예산 300만원" | "건당 1만원 초과 실행은 인간 승인 필요" |

같은 "돈"을 다뤄도 계층이 다르다. **Constraint는 이 Goal의 사정, Policy는 조직의 규칙이다.**

### Policy는 Preference가 아니다

❌ `가능하면 한국어를 잘하는 모델을 쓰자` — 이건 선호이고 Utility 가중치로 표현된다.

Policy는 **위반이 곧 차단**이다. 선호는 감점일 뿐이다. 차단할 수 없는 것을 Policy로 만들면 아무도 지키지 않는다.

### Policy는 Guideline이 아니다

❌ `카피는 친근한 톤으로 쓰는 것이 좋다`

기계가 판정할 수 없으면 Policy가 아니다(Rule POL-002). 이런 항목은 [Evaluation](e015-evaluation.md)의 Rubric으로 가야 한다.

### Policy는 Configuration이 아니다

❌ `기본 타임아웃 120초`

설정은 동작을 조정하는 값이고, Policy는 **허용 여부를 판정하는 규칙**이다. 설정을 바꾸면 결과가 달라지고, Policy를 어기면 실행이 멈춘다.

### Policy는 Decision Engine의 알고리즘이 아니다

❌ `Utility 가중치를 상황에 따라 조정한다`

이건 Decision Engine의 내부 로직([Volume 4-A](../v4a-decision-engine-detail.md))이다. Policy는 그 로직 **바깥에서** 결과를 검열한다. 검열자가 피검열자의 일부이면 검열이 성립하지 않는다.

---

## 3. Design Principles

### Rule POL-001 — Policy는 Goal에 독립이다

Policy 정의에 특정 Goal ID가 등장하면 그것은 Constraint다. Policy는 **모든 Goal에, 또는 조건에 부합하는 모든 상황에** 적용된다.

### Rule POL-002 — 기계 강제 가능해야 한다

Policy는 `condition`과 `effect`로 표현되며, `condition`은 시스템이 판정할 수 있는 값으로만 구성된다.

- ✅ `IF artifact.contains_pii == true AND artifact.visibility == "public" THEN deny`
- ❌ `IF 카피가 브랜드에 어울리지 않으면 THEN deny`

판정 불가능한 규칙은 Policy가 아니라 문서다.

### Rule POL-003 — Policy는 Decision보다 우선한다

Policy에 의해 배제된 후보는 **Utility를 계산하지도 않는다.** 계산한 뒤 걸러내면 "최적해였는데 막혔다"는 유혹이 생기고, 로그에 금지된 선택지의 점수가 남는다.

### Rule POL-004 — 권위(Authority)를 명시한다

누가 이 규칙을 만들었고 무엇에 근거하는가. `authority` 없는 Policy는 이의 제기 시 방어할 수 없다.

| authority | 예 |
|---|---|
| `legal` | 개인정보보호법 |
| `organization` | 학원 내부 규정 |
| `security` | 정보보안 정책 |
| `contractual` | Resource 제공자와의 계약 |
| `user` | 사용자가 설정한 전역 규칙 |

### Rule POL-005 — 위반은 반드시 기록된다

차단만 하고 기록하지 않으면 "왜 안 되는지" 아무도 모른다. 모든 위반은 [Event](e020-event.md)(`policy.violated`)를 발생시킨다.

### Rule POL-006 — 충돌은 우선순위로 해소한다

두 Policy가 충돌하면 아래 순서로 해소한다.

```
1. 더 제한적인 쪽(deny)이 이긴다        — Deny Overrides
2. 동일하면 authority가 높은 쪽이 이긴다 — legal > security > organization > contractual > user
3. 그래도 같으면 priority 값이 높은 쪽
4. 그래도 같으면 escalate (인간 판단)
```

**Deny Overrides가 첫 번째인 이유:** 규칙이 애매할 때 하지 않는 쪽이 안전하다.

### Rule POL-007 — 예외는 승인과 만료를 가진다

Policy 예외(Exception)는 허용하되 반드시 `approved_by`, `reason`, `expires_at`을 갖는다. **만료 없는 예외는 Policy를 무력화한다.**

### Rule POL-008 — 강제 지점(Enforcement Point)을 명시한다

같은 Policy라도 언제 검사하느냐에 따라 효과가 다르다(§4.2). 사후 감사만 하는 Policy는 사고를 막지 못한다.

---

## 4. Attributes

```
Policy
├── Identity
│   ├── policy_id
│   ├── name
│   ├── type
│   └── version
├── Authority
│   ├── authority
│   ├── owner
│   └── reference
├── Rule
│   ├── applies_to
│   ├── condition
│   ├── effect
│   └── priority
├── Enforcement
│   ├── enforcement_points[]
│   └── on_violation
├── Exception
│   └── exceptions[]
└── Status
    ├── status
    ├── effective_from
    └── effective_until
```

| 속성 | 의미 | 예 |
|---|---|---|
| **policy_id** | 식별자 | `pol_007` |
| **name** | 이름 | `개인정보 외부 전송 금지` |
| **type** | 분류 (§4.1) | `privacy` |
| **authority** | 권위 근거 | `legal` |
| **owner** | 책임자 | `human:대표` |
| **reference** | 근거 문서 | `개인정보보호법 제17조` |
| **applies_to** | 적용 대상 Entity | `["Artifact", "Execution"]` |
| **condition** | 판정 조건 | §8 참조 |
| **effect** | 결과 | `deny` / `require_approval` / `warn` / `log` |
| **priority** | 동일 조건 시 우선순위 | `100` |
| **enforcement_points** | 검사 시점 (§4.2) | `["pre_decision", "pre_execution"]` |
| **on_violation** | 위반 시 조치 | `block_and_alert` |
| **exceptions** | 승인된 예외 목록 | `[]` |
| **status** | 상태 (§6) | `Active` |
| **effective_from** | 발효일 | `2026-01-01` |

### 4.1 Policy Types

```
Policy
├── privacy        개인정보 처리
├── security       접근 통제, 자격증명
├── compliance     법규·심의·업계 규정
├── cost           비용 상한, 승인 임계
├── human_oversight 인간 승인 필요 조건
├── quality        최소 품질 기준
├── data_retention 보존·삭제
├── resource_usage 허용 Resource, 지역, 제공자
└── brand          브랜드·표현 금지 사항
```

| Type | 예 | effect |
|---|---|---|
| `privacy` | 개인정보 포함 Artifact의 외부 공개 금지 | `deny` |
| `security` | 미승인 Tool의 실행 금지 | `deny` |
| `compliance` | 광고 심의 금칙어 포함 카피 발행 금지 | `deny` |
| `cost` | 건당 10,000원 초과 실행은 승인 필요 | `require_approval` |
| `human_oversight` | 비가역 실행(광고 집행)은 인간 승인 필수 | `require_approval` |
| `quality` | Evaluation composite < 0.6인 Artifact는 Published 불가 | `deny` |
| `data_retention` | Outcome은 90일, PII Artifact는 30일 후 삭제 | `log` + 자동 실행 |
| `resource_usage` | 학부모 데이터는 국내 리전 Resource만 사용 | `deny` |
| `brand` | 과장 표현("100% 합격") 사용 금지 | `deny` |

### 4.2 Enforcement Points

```
pre_decision   후보 생성 단계에서 걸러낸다        ← 가장 강력
pre_execution  실행 직전에 차단한다
during         실행 중 감시하고 중단한다
post_outcome   결과 생성 후 검사한다
continuous     주기적으로 전체를 감사한다
```

| 지점 | 막을 수 있는 것 | 막을 수 없는 것 |
|---|---|---|
| `pre_decision` | 금지된 Resource 선택 자체 | 실행 중 발생하는 위반 |
| `pre_execution` | 예산 초과 실행, 미승인 비가역 작업 | 결과물 내용의 위반 |
| `during` | 폭주하는 비용, 장시간 실행 | 이미 발생한 부분 결과 |
| `post_outcome` | 위반 Artifact의 공개 | 이미 발생한 비용 |
| `continuous` | 누적 위반, 만료된 예외 | 실시간 사고 |

**하나의 Policy가 여러 지점에 걸릴 수 있다.** 개인정보 정책은 `pre_decision`(해외 Resource 배제) + `post_outcome`(PII 스캔) + `continuous`(보존 만료 검사) 세 지점 모두에서 작동한다.

---

## 5. Invariants

### INV-POL-01 — Policy가 deny한 것은 어떤 Utility로도 선택될 수 없다

전역 불변식 [INV-11](e000a-entity-relationships.md)의 Policy 측 표현이다.

| | |
|---|---|
| **위반 시** | 해당 Decision을 무효화하고 Execution을 즉시 중단. 사고로 기록 |
| **탐지** | Decision 생성 시 + Execution 시작 시 이중 검사 |

### INV-POL-02 — 모든 Policy 위반은 Event를 남긴다

| | |
|---|---|
| **위반 시** | 조용한 차단은 금지다. 기록 없는 차단은 디버깅 불가능한 시스템을 만든다 |

### INV-POL-03 — 예외는 만료 시각을 가진다

| | |
|---|---|
| **위반 시** | 만료 없는 예외는 생성 거부. 기본 만료를 30일로 강제 부여 |

### INV-POL-04 — 만료된 예외는 자동으로 무효다

| | |
|---|---|
| **위반 시** | `continuous` 감사에서 만료 예외를 발견하면 즉시 비활성화하고 알림 |

### INV-POL-05 — Deprecated Policy는 신규 검사에 사용되지 않지만 과거 판정 기록은 보존된다

| | |
|---|---|
| **위반 시** | 과거 Decision이 왜 차단되었는지 설명할 수 없게 된다. 삭제를 차단 |

### INV-POL-06 — Policy는 자기 자신을 예외로 둘 수 없다

| | |
|---|---|
| **위반 시** | 생성 거부. Policy 검사를 우회하는 Policy는 규칙 체계를 무너뜨린다 |

---

## 6. Lifecycle

```
Drafted → Review → Active ──▶ Deprecated ──▶ Retired
             │        │
             │        └──▶ Suspended ──▶ Active
             └──▶ Rejected
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Drafted** | 작성됨 | 등록 |
| **Review** | 검토 중 | 제출 |
| **Active** | 발효. 강제됨 | 승인 + `effective_from` 도달 |
| **Suspended** | 일시 중지 | 긴급 중지 승인 |
| **Deprecated** | 신규 적용 중단. 기존 판정은 유효 | 대체 Policy 발효 |
| **Retired** | 종료 | `effective_until` 경과 |
| **Rejected** | 반려 | 검토 실패 |

### 6.1 Policy 변경의 소급 문제

Policy가 바뀌면 **과거 판정을 다시 하지 않는다.**

```
2026-08-01  pol_012 (건당 5,000원 초과 승인 필요) 발효
2026-08-04  dec_101 승인 없이 실행 (0.42 USD ≈ 580원, 문제없음)
2026-09-01  pol_012 개정 (건당 500원 초과 승인 필요)
            → dec_101을 소급 위반으로 판정하지 않는다
```

Decision의 `inputs_snapshot`이 그 시점의 세계를 보존하듯([e009 Rule D-004](e009-decision.md)), Policy 판정도 **판정 시점의 Policy 버전**을 기록한다.

---

## 7. Relationships

```
Policy 019 ──지배──▶ 모든 Entity
     │
     ├── pre_decision  ──▶ Decision 009  (후보 필터)
     ├── pre_execution ──▶ Execution 013 (실행 게이트)
     ├── post_outcome  ──▶ Artifact 016  (공개·보존)
     ├── continuous    ──▶ Session 021 / Risk 018 (감사)
     └── 위반 ──▶ Event 020 (policy.violated)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| 모든 Entity | Policy는 전역적으로 지배한다 | `Policy 1:N *` |
| [Decision](e009-decision.md) | 후보 생성 전에 배제. Utility보다 우선 | `Policy 1:N Decision` |
| [Execution](e013-execution.md) | 실행 전 게이트, 실행 중 중단 | `Policy 1:N Execution` |
| [Artifact](e016-artifact.md) | 공개 범위·보존 기간을 강제 | `Policy 1:N Artifact` |
| [Constraint](e004-constraint.md) | 상위 개념. Policy가 Constraint를 이긴다 | — |
| [Risk](e018-risk.md) | 어떤 Risk 수준에서 승인이 필요한지 규정 | `Policy 1:N Risk` |
| [Evaluation](e015-evaluation.md) | 어떤 Task에 어떤 평가를 강제할지 규정 | `Policy 1:N Evaluation` |
| [Event](e020-event.md) | 위반 시 발생 | `Policy 1:0..N Event` |
| [Session](e021-session.md) | Session 범위의 Policy 집합을 결정 | `Policy N:M Session` |

---

## 8. Canonical Representation

```json
{
  "policy_id": "pol_007",
  "name": "개인정보 포함 산출물의 외부 공개 금지",
  "type": "privacy",
  "version": "1.2",
  "authority": "legal",
  "owner": "human:대표",
  "reference": "개인정보보호법 제17조",
  "applies_to": ["Artifact"],
  "condition": {
    "all": [
      { "field": "artifact.contains_pii", "op": "eq", "value": true },
      { "field": "artifact.visibility", "op": "in", "value": ["public", "external"] }
    ]
  },
  "effect": "deny",
  "priority": 100,
  "enforcement_points": ["post_outcome", "continuous"],
  "on_violation": "block_and_alert",
  "exceptions": [],
  "status": "Active",
  "effective_from": "2026-01-01",
  "effective_until": null
}
```

승인 필요 Policy는 다음과 같다.

```json
{
  "policy_id": "pol_012",
  "name": "고액 실행의 인간 승인",
  "type": "cost",
  "authority": "organization",
  "owner": "human:대표",
  "applies_to": ["Execution"],
  "condition": {
    "any": [
      { "field": "execution.estimated_cost_krw", "op": "gt", "value": 10000 },
      { "field": "task.irreversible", "op": "eq", "value": true }
    ]
  },
  "effect": "require_approval",
  "approval": { "approver_role": "owner", "timeout": "PT24H", "on_timeout": "deny" },
  "priority": 90,
  "enforcement_points": ["pre_execution"],
  "on_violation": "block_and_alert",
  "exceptions": [
    {
      "exception_id": "exc_003",
      "scope": { "goal_id": "goal_001" },
      "reason": "윈터캠프 시즌 광고 집행. 일 단위 승인 대신 주간 일괄 승인",
      "approved_by": "human:대표",
      "approved_at": "2026-08-01T09:00:00Z",
      "expires_at": "2026-12-31T23:59:59Z"
    }
  ],
  "status": "Active",
  "effective_from": "2026-01-01"
}
```

기계가 읽을 수 있는 스키마: [`policy.schema.json`](../intent-os-spec/schemas/policy.schema.json)

---

## 9. Validation Rules

### 9.1 Policy 등록 검증

```
Policy 등록 요청
  ↓
Goal ID 포함 여부 검사 (POL-001) ── 포함 시 반려 (Constraint로 등록하라)
  ↓
condition의 모든 field가 시스템이 판정 가능한 값인가 (POL-002)
  ── 불가능한 field 발견 시 반려
  ↓
authority 확인 (POL-004) ── 없으면 반려
  ↓
enforcement_points 확인 (POL-008) ── 비어 있으면 반려
  ↓
effect = require_approval 이면 approval 블록 필수
  ↓
기존 Active Policy와의 충돌 검사
  ├── 동일 조건 + 상반된 effect → Rule POL-006으로 해소 가능한지 확인
  └── 해소 불가 → 반려 + 충돌 목록 반환
  ↓
자기 참조 예외 검사 (INV-POL-06)
  ↓
Drafted → Review → 승인 → Active
```

### 9.2 Policy 평가 알고리즘 (실행 시)

```
평가 요청 (지점, 대상 Entity)
  ↓
해당 enforcement_point + applies_to에 매칭되는 Active Policy 수집
  ↓
각 Policy에 대해 condition 평가
  ↓
매칭된 Policy 집합 P
  ├── P가 비어 있음 → allow
  └── 예외 검사
        각 p ∈ P에 대해 유효한 exception이 있는가
        (scope 일치 AND now < expires_at)
        ── 있으면 p를 P에서 제거 + 예외 사용 Event 발행
  ↓
남은 P의 effect 병합 (Rule POL-006)
  ① deny가 하나라도 있으면 → deny
  ② require_approval이 있으면 → require_approval
  ③ warn만 있으면 → allow + 경고
  ④ 비어 있으면 → allow
  ↓
결과 기록
  ├── deny             → Event(policy.violated) + 차단
  ├── require_approval → 승인 요청 생성, 대기
  └── allow            → 통과 (판정 시점의 Policy 버전 기록)
```

### 9.3 판정 결과의 기록

모든 판정은 대상 Entity에 다음을 남긴다.

```json
{
  "policy_evaluation": {
    "evaluated_at": "2026-08-04T09:29:59Z",
    "point": "pre_execution",
    "matched_policies": ["pol_012"],
    "policy_versions": { "pol_012": "1.0" },
    "exceptions_used": ["exc_003"],
    "result": "allow"
  }
}
```

**`policy_versions`가 핵심이다.** 나중에 Policy가 개정되어도 "그때는 이 버전으로 판정했다"를 설명할 수 있다(§6.1).

---

## 10. Examples

### 예시 1 — 후보 배제 (pre_decision)

```
Task task_007  학부모 상담 이력 분석
required_capabilities: [analysis.customer_data]

후보 생성
├── overseas:model-x   region: us-east   ← pol_015 (국내 리전만) → 배제
├── anthropic:claude-5 region: kr        ← 통과
└── domestic:model-y   region: kr        ← 통과

Decision dec_140: 2개 후보만 비교. 배제된 후보는 Utility를 계산하지 않는다.
rationale: ["pol_015에 의해 해외 리전 Resource 1건 배제"]
```

배제 사실은 남기되 점수는 계산하지 않는다(Rule POL-003).

### 예시 2 — 승인 요구 (pre_execution)

```
exe_301  광고 플랫폼 API / 인스타 광고 집행 / 예상 비용 1,200,000 KRW
  ↓
pol_012 평가: estimated_cost_krw(1,200,000) > 10,000 → require_approval
  ↓
예외 검사: exc_003 (goal_001, 2026-12-31 만료) → 유효
  ↓
결과: allow (예외 사용)
  ↓
Event 발행: policy.exception_used { policy: pol_012, exception: exc_003 }
```

예외가 없었다면 대표의 승인을 24시간 기다리고, 응답이 없으면 `deny`였을 것이다.

### 예시 3 — 결과물 차단 (post_outcome)

```
out_338  랜딩페이지 개선안 (art_470)
  ↓
PII 스캔: 상담 후기에 실명 3건 포함 → contains_pii: true
  ↓
공개 요청 (visibility: public)
  ↓
pol_007 평가: contains_pii=true AND visibility=public → deny
  ↓
Artifact status: Adopted 유지, Published 전이 차단
Event: policy.violated { policy: pol_007, artifact: art_470 }
  ↓
후속 Task 자동 생성: "art_470에서 실명 3건 익명화"
```

**차단으로 끝내지 않고 해결 Task를 만든다.** 이것이 Policy가 방해물이 아니라 시스템의 일부인 이유다.

### 예시 4 — 충돌 해소

```
pol_020  (organization) 비용 절감을 위해 가장 싼 Resource 우선   effect: warn
pol_015  (legal)        학부모 데이터는 국내 리전만              effect: deny

Task: 학부모 상담 이력 분석 (가장 싼 후보는 해외 리전)

Rule POL-006 적용
① deny가 존재 → deny 승 (Deny Overrides)
결과: 해외 후보 배제. pol_020은 남은 후보들 사이에서만 작동.
```

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **Policy가 모든 후보를 배제** | 실행 불가다. `Decision` 대신 `escalate`를 생성하고 사용자에게 "현재 Policy 하에서 이 Task를 수행할 Resource가 없다"고 보고한다. 임의로 Policy를 완화하지 않는다 |
| **긴급 상황에서 Policy가 방해** | 우회하지 않는다. `Suspended` 전이(승인 필요) 또는 예외 발급(승인 + 만료 필수)만이 경로다 |
| **Policy 조건이 판정 불가능한 값을 참조** | `allow`가 아니라 `escalate`로 처리한다. 판정할 수 없는 것을 통과시키면 Policy가 무의미해진다 |
| **예외가 만료되었는데 실행 중** | 실행 중인 Execution은 완료시킨다(중단이 더 큰 손해). 신규 실행은 차단하고 예외 갱신을 요구한다 |
| **Policy 개정으로 과거 판정이 위반이 됨** | 소급 적용하지 않는다(§6.1). 단 `continuous` 감사에서 "현행 Policy 기준 부적합 자산" 목록을 만들어 정리 Task를 생성한다 |
| **동일 Policy가 여러 지점에서 다른 결과** | 정상이다. `pre_decision`에서 통과한 것이 `post_outcome`에서 걸릴 수 있다(생성된 내용은 사전에 알 수 없으므로) |
| **사용자가 자기 Policy를 스스로 예외 처리** | `authority: user`인 Policy는 사용자 자신이 예외를 승인할 수 있다. 그러나 `legal`·`security`는 불가하다. 예외 승인 권한은 authority 등급에 종속된다 |
| **Policy 개수가 100개를 넘음** | 평가 지연이 실행 지연이 된다. `applies_to`와 `enforcement_points`로 인덱싱하고, 평가 시간이 임계값을 넘으면 경보를 발행한다 |
| **Policy와 Constraint가 같은 것을 규정** | 둘 다 유지한다. Policy가 먼저 평가되고, 통과하면 Constraint가 평가된다. 중복은 낭비가 아니라 이중 안전장치다 |

---

## 12. Open Issues (v1.0)

### condition 표현 문법

현재 `{ field, op, value }`의 `all`/`any` 조합으로 예시를 들었으나 정식 문법(Formal Grammar)이 없다. [Goal](e001-goal.md)의 Formal Grammar처럼 BNF 수준의 정의가 필요하다.

### Policy의 테스트 가능성

Policy를 배포하기 전에 "과거 1000건의 Decision에 이 Policy를 적용하면 몇 건이 차단되는가"를 시뮬레이션할 수 있어야 한다. Dry-run 모드의 명세가 없다.

### 자연어 Policy의 기계화

조직의 실제 규정은 자연어 문서다. 이를 `condition`으로 변환하는 과정에서 의미가 손실된다. 변환 결과의 검증 방법(사람 확인 + 반례 테스트)이 필요하다.

### 승인자 부재 시의 기본값

`on_timeout: deny`를 예시로 썼으나, 사업 관점에서는 `allow`가 필요한 경우도 있다. 어떤 Policy 유형에 어떤 기본값이 옳은지 지침이 없다.

### 앞으로 보강해야 할 항목

- Policy Formal Grammar 정의
- Dry-run / 시뮬레이션 명세
- 예외 승인 권한 매트릭스 (authority × 역할)
- Policy 평가 성능 목표 (지점별 지연 상한)
- 실제 예시 30~50개
