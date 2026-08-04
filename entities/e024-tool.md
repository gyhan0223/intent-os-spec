# Entity 024: Tool

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Tool is a Resource with a deterministic, schema-defined interface whose invocation has declared side effects, permissions, and idempotency semantics.**

> Tool은 **결정론적이고 스키마로 정의된 인터페이스**를 가진 Resource이며, 그 호출은 선언된 부수효과·권한·멱등성 의미를 갖는다.

여기서 중요한 것은 **선언된 부수효과(Declared Side Effects)** 다.

```
Claude에게 카피를 요청  →  텍스트가 돌아온다. 세계는 변하지 않는다
Slack에 메시지 발송     →  텍스트가 돌아온다. 그리고 세계가 변했다
```

두 번째가 Tool이다.

### 왜 Resource에서 분리하는가

Tool은 [Resource](e007-resource.md)의 **부분집합**이다. 그런데 별도 명세가 필요하다. 관리해야 할 축이 다르기 때문이다.

| 축 | LLM 등 일반 Resource | Tool |
|---|---|---|
| 출력 | 확률적 | 결정론적 |
| 핵심 관리 대상 | **품질 점수** (observed_score) | **스키마 계약** (입출력) |
| 실패 원인 | 능력 부족, 품질 미달 | 권한 없음, 스키마 불일치, 대상 부재 |
| 선택 기준 | Utility 비교 | 대개 **대안이 없다** |
| 위험 | 나쁜 결과물 | **세계의 변경** |
| 승인 | 대체로 불필요 | 쓰기 작업은 필요 |

카피 작성에는 Claude·GPT·인간이라는 후보가 있다. **캘린더에 일정을 잡는 데는 캘린더 API밖에 없다.** 선택의 문제가 아니라 권한과 계약의 문제다.

---

## 2. Tool은 무엇이 아닌가?

### Tool은 Resource와 무관한 것이 아니다

❌ `Tool은 Resource와 별개의 계층이다`

Tool은 Resource의 부분집합이며 **Universal Resource Interface를 그대로 따른다**([e007 Rule R-003](e007-resource.md)). Decision Engine은 Tool도 Resource로서 후보에 올린다.

```
Resource
├── AI Resource     (llm, image_model, …)
├── Tool Resource   ← 본 문서가 상세히 다룬다
├── Human Resource
└── Hybrid Resource
```

분리하는 것은 **명세이지 계층이 아니다.**

### Tool은 Capability가 아니다

❌ `웹 검색` — 이건 [Capability](e006-capability.md)(`research.web`)다.

Tool은 그 Capability를 **제공하는 구체적 수단**이다. 같은 `research.web`을 검색 API·브라우저·Perplexity가 각각 제공한다.

### Tool은 Agent가 아니다

❌ `브라우저 자동화 에이전트`

[Agent](e023-agent.md)는 스스로 결정하고 Tool은 시키는 대로 한다. **Tool은 목적을 갖지 않는다.**

```
Agent   "경쟁 학원 가격을 알아내라"를 받고 → 검색 Tool을 3번 호출하고 판단한다
Tool    "홍대 학원 가격"을 받고 → 검색 결과를 반환한다. 끝
```

### Tool은 인증 정보가 아니다

❌ `Slack API 토큰`

토큰은 Tool의 **연결 자격**이지 Tool이 아니다. 같은 Tool을 여러 계정으로 연결할 수 있고, 자격이 만료돼도 Tool 정의는 남는다.

### Tool은 함수 호출(Function Calling)이 아니다

❌ `LLM에게 넘기는 함수 스키마`

Function Calling은 **LLM이 Tool을 쓰게 하는 기법**이다. Intent OS에서 Tool은 LLM 없이도 직접 호출된다. Tool은 시스템의 Entity이지 프롬프트의 일부가 아니다.

---

## 3. Design Principles

### Rule TOL-001 — 입출력 스키마를 선언한다

Tool은 `input_schema`와 `output_schema`(JSON Schema)를 갖는다. 스키마 없는 Tool은 등록할 수 없다. 결정론적 계약이 Tool의 존재 이유다.

### Rule TOL-002 — 부수효과를 선언한다

| effect | 의미 | 승인 |
|---|---|---|
| `read` | 세계를 바꾸지 않는다 | 불필요 |
| `write` | 상태를 만들거나 바꾼다 | Policy에 따라 |
| `irreversible` | 되돌릴 수 없다 | **필수** |
| `external_visible` | 외부에 노출된다 (발송·게시) | **필수** |

선언되지 않은 부수효과는 **버그가 아니라 사고**다.

### Rule TOL-003 — 필요한 권한을 선언한다

`required_scopes`로 표현한다. 최소 권한 원칙을 따르며, Tool이 선언한 것보다 넓은 권한으로 연결하지 않는다.

- ✅ `calendar.events.read`, `calendar.events.write`
- ❌ `calendar.*`

### Rule TOL-004 — 멱등성을 선언한다

| idempotency | 의미 | 재시도 |
|---|---|---|
| `idempotent` | 몇 번 호출해도 결과가 같다 | 안전 |
| `idempotent_with_key` | 멱등 키를 주면 안전하다 | 키 필수 |
| `non_idempotent` | 호출할 때마다 상태가 변한다 | **재시도 금지** |

`non_idempotent` Tool을 [Execution](e013-execution.md)이 자동 재시도하면 메시지가 두 번 발송된다.

### Rule TOL-005 — Tool도 Capability를 제공한다

Resource와 동일하다([e007 Rule R-001](e007-resource.md)). Capability 선언이 없으면 매칭 대상이 되지 못한다.

### Rule TOL-006 — 쓰기 Tool은 Policy 게이트를 통과한다

`effect ∈ {write, irreversible, external_visible}`인 Tool의 호출은 [Policy](e019-policy.md) 평가가 강제된다.

### Rule TOL-007 — 버전과 호환성 정책을 가진다

외부 API는 통보 없이 바뀐다. Tool은 `version`과 `breaking_change_policy`를 갖고, 스키마 불일치를 감지하면 `Degraded`로 전이한다.

### Rule TOL-008 — 실패 의미를 구분한다

Tool의 실패는 LLM의 실패와 원인이 다르다. 이를 [Execution](e013-execution.md)의 `failure_class`로 정확히 매핑해야 재시도 전략이 옳게 결정된다(§4.2).

---

## 4. Attributes

```
Tool
├── Identity
│   ├── tool_id
│   ├── name
│   ├── provider
│   ├── version
│   └── category
├── Contract
│   ├── input_schema
│   ├── output_schema
│   ├── operations[]
│   └── error_codes[]
├── Semantics
│   ├── effect
│   ├── idempotency
│   ├── rate_limit
│   └── timeout_ms
├── Security
│   ├── required_scopes[]
│   ├── auth_type
│   └── data_residency
├── Capability
│   └── capabilities[]
└── Status
    ├── status
    └── health
```

| 속성 | 의미 | 예 |
|---|---|---|
| **tool_id** | 식별자 | `tool_adplatform_campaign` |
| **provider** | 제공자 | `AdPlatform` |
| **version** | 버전 | `v3` |
| **category** | 분류 (§4.1) | `external_platform` |
| **input_schema** | 입력 계약 | JSON Schema |
| **output_schema** | 출력 계약 | JSON Schema |
| **operations** | 지원 작업 | `["create", "pause", "update_budget"]` |
| **effect** | 부수효과 (TOL-002) | `irreversible` |
| **idempotency** | 멱등성 (TOL-004) | `idempotent_with_key` |
| **rate_limit** | 호출 제한 | `{ "per_minute": 60 }` |
| **required_scopes** | 필요 권한 | `["ads.campaign.write"]` |
| **auth_type** | 인증 방식 | `oauth2` |
| **data_residency** | 데이터 처리 지역 | `kr` |
| **capabilities** | 제공 능력 | `["advertising.campaign_execution"]` |
| **status** | 상태 (§6) | `Active` |
| **health** | 최근 가용성 | `{ "success_rate_24h": 0.99 }` |

### 4.1 Tool Categories

```
Tool
├── search            검색 엔진, 지식 검색
├── browser           웹 페이지 접근·조작
├── calendar          일정 조회·생성
├── messaging         메일·메신저 발송
├── storage           파일·문서 저장소
├── analytics         지표 조회
├── crm               고객·상담 데이터
├── code_exec         코드 실행 환경
└── external_platform 광고·결제 등 외부 플랫폼
```

| Category | 예 | 대표 effect | 멱등성 |
|---|---|---|---|
| `search` | 검색 API | `read` | idempotent |
| `browser` | 헤드리스 브라우저 | `read` (조작 시 `write`) | 조건부 |
| `calendar` | 캘린더 API | `write` | idempotent_with_key |
| `messaging` | 메신저·메일 발송 | `external_visible` | **non_idempotent** |
| `storage` | 문서 저장소 | `write` | idempotent_with_key |
| `analytics` | 광고 지표 조회 | `read` | idempotent |
| `crm` | 학원 상담 이력 DB | `read` / `write` | 조건부 |
| `code_exec` | 스크립트 실행 | `write` | non_idempotent |
| `external_platform` | 광고 플랫폼 API | `irreversible` | idempotent_with_key |

**`messaging`이 가장 위험하다.** 발송은 되돌릴 수 없고 멱등하지도 않다. 재시도 로직의 버그 하나가 학부모에게 같은 메시지를 5번 보낸다.

### 4.2 Tool 실패의 분류

Tool 실패를 [Execution](e013-execution.md)의 `failure_class`로 매핑한다.

| Tool 오류 | failure_class | 재시도 |
|---|---|---|
| 401 / 403 권한 없음 | `policy_violation` | ❌ 금지 |
| 404 대상 없음 | `input_insufficient` | ❌ 입력 수정 필요 |
| 400 스키마 불일치 | `resource_incapable` | ❌ Tool 버전 확인 |
| 429 rate limit | `resource_unavailable` | ✅ 백오프 후 |
| 5xx 서버 오류 | `resource_unavailable` | ✅ |
| 타임아웃 | `timeout` | 멱등성에 따라 |

**타임아웃이 가장 까다롭다.** `non_idempotent` Tool에서 타임아웃이 나면 **성공했는지 실패했는지 알 수 없다.** 재시도하면 중복 실행 위험, 안 하면 누락 위험이다(§11).

---

## 5. Invariants

### INV-TOL-01 — 스키마 없는 Tool은 등록되지 않는다

| | |
|---|---|
| **위반 시** | 등록 거부. 계약 없는 Tool은 검증도 재시도도 불가능하다 |

### INV-TOL-02 — 선언되지 않은 부수효과를 가진 호출은 차단된다

| | |
|---|---|
| **위반 시** | `read`로 선언된 Tool이 쓰기를 시도하면 즉시 차단하고 Tool을 `Quarantined`로 전이 |
| **탐지** | 어댑터 계층의 호출 감사 |

### INV-TOL-03 — non_idempotent Tool은 자동 재시도되지 않는다

| | |
|---|---|
| **위반 시** | Runtime의 재시도 로직이 이를 반드시 확인한다. 위반은 중복 발송 사고로 직결된다 |

### INV-TOL-04 — required_scopes를 초과하는 자격으로 연결할 수 없다

| | |
|---|---|
| **위반 시** | 연결 거부. 최소 권한 원칙 위반 |

### INV-TOL-05 — irreversible / external_visible Tool은 Policy 평가 없이 호출되지 않는다

| | |
|---|---|
| **위반 시** | 호출 차단 + `policy.violated` Event ([INV-11](e000a-entity-relationships.md)) |

### INV-TOL-06 — 스키마가 깨진 Tool은 Active로 남을 수 없다

| | |
|---|---|
| **위반 시** | 출력이 `output_schema`를 3회 연속 위반하면 `Degraded`로 자동 전이하고 후보군에서 제외 |

---

## 6. Lifecycle

Tool은 [Resource Lifecycle](e007-resource.md)을 따르되 두 상태가 추가된다.

```
Registered → Evaluating → Active ──▶ Degraded ──▶ Active
                             │           │
                             │           ▼
                             └──▶ Quarantined ──▶ Deprecated ──▶ Removed
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Registered** | 등록됨. 스키마 검증 완료 | 등록 |
| **Evaluating** | 저위험 호출로 검증 중 | Cold Start |
| **Active** | 정식 사용 | 검증 통과 |
| **Degraded** | 스키마 불일치·가용성 저하. 신규 배정 중단 | INV-TOL-06 또는 `success_rate_24h < 0.8` |
| **Quarantined** | 위험 감지로 격리 | 미선언 부수효과 감지 (INV-TOL-02) |
| **Deprecated** | 제공 중단 예고 | 제공자 공지 또는 대체 Tool 도입 |
| **Removed** | 제거. 호출 이력은 보존 | 최종 제거 |

### 6.1 Degraded의 의미

외부 API는 조용히 바뀐다.

```
2026-08-20  AdPlatform이 응답 필드명을 campaign_id → id로 변경 (공지 없음)
   ↓
호출 3건 연속 output_schema 위반
   ↓
tool_adplatform_campaign → Degraded
   ↓
① 신규 Decision의 후보에서 제외
② 운영자 알림 + Event(resource.drift_detected)
③ 진행 중 Execution은 완료 시도
   ↓
스키마 갱신 (v3 → v3.1) → 검증 → Active 복귀
```

**`Degraded`가 없으면 스키마가 깨진 Tool을 계속 호출하며 실패를 쌓는다.**

---

## 7. Relationships

```
Resource 007 ──부분집합──▶ Tool 024 ──제공──▶ Capability 006
                              │
                              ├──호출──▶ Execution 013
                              ├──사용──▶ Agent 023
                              ├──게이트▶ Policy 019
                              └──승격──▶ Artifact 016 (재사용 가능한 산출물)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Resource](e007-resource.md) | Tool은 Resource의 부분집합 | `Resource 1:0..1 Tool` |
| [Capability](e006-capability.md) | Tool이 Capability를 제공 | `Tool N:M Capability` |
| [Execution](e013-execution.md) | Tool 호출이 Execution이 된다 | `Tool 1:0..N Execution` |
| [Agent](e023-agent.md) | Agent가 Tool을 호출 | `Agent N:M Tool` |
| [Policy](e019-policy.md) | 쓰기 Tool의 게이트 | `Policy 1:N Tool` |
| [Artifact](e016-artifact.md) | 재사용 가능한 Artifact가 Tool로 승격 가능 | `Artifact 1:0..1 Tool` |
| [Resource Profile](e025-resource-profile.md) | Tool도 Profile을 갖는다 | `Tool 1:1 Resource Profile` |
| [Risk](e018-risk.md) | irreversible Tool은 Risk의 주요 원천 | `Tool 1:0..N Risk` |

---

## 8. Canonical Representation

```json
{
  "tool_id": "tool_adplatform_campaign",
  "name": "광고 플랫폼 캠페인 관리",
  "provider": "AdPlatform",
  "version": "v3",
  "category": "external_platform",
  "capabilities": ["advertising.campaign_execution", "advertising.budget_control"],
  "operations": [
    {
      "name": "create",
      "effect": "irreversible",
      "idempotency": "idempotent_with_key",
      "input_schema": {
        "type": "object",
        "required": ["name", "daily_budget_krw", "creative_ref", "start_date", "end_date"],
        "properties": {
          "name": { "type": "string" },
          "daily_budget_krw": { "type": "integer", "minimum": 10000 },
          "creative_ref": { "type": "string" },
          "start_date": { "type": "string", "format": "date" },
          "end_date": { "type": "string", "format": "date" },
          "idempotency_key": { "type": "string" }
        }
      },
      "output_schema": {
        "type": "object",
        "required": ["campaign_id", "status"],
        "properties": {
          "campaign_id": { "type": "string" },
          "status": { "type": "string", "enum": ["active", "pending_review"] }
        }
      },
      "requires_approval": true
    },
    {
      "name": "pause",
      "effect": "write",
      "idempotency": "idempotent",
      "input_schema": {
        "type": "object",
        "required": ["campaign_id"],
        "properties": { "campaign_id": { "type": "string" } }
      },
      "output_schema": {
        "type": "object",
        "properties": { "campaign_id": { "type": "string" }, "status": { "type": "string" } }
      },
      "requires_approval": false
    }
  ],
  "error_codes": [
    { "code": "INSUFFICIENT_BALANCE", "failure_class": "constraint_violation", "retryable": false },
    { "code": "CREATIVE_REJECTED", "failure_class": "policy_violation", "retryable": false },
    { "code": "RATE_LIMITED", "failure_class": "resource_unavailable", "retryable": true }
  ],
  "rate_limit": { "per_minute": 60, "per_day": 5000 },
  "timeout_ms": 30000,
  "required_scopes": ["ads.campaign.read", "ads.campaign.write"],
  "auth_type": "oauth2",
  "data_residency": "kr",
  "breaking_change_policy": "schema_check_on_every_call",
  "status": "Active",
  "health": { "success_rate_24h": 0.99, "p95_latency_ms": 1240 }
}
```

읽기 전용 Tool은 훨씬 단순하다.

```json
{
  "tool_id": "tool_analytics_read",
  "name": "광고 성과 지표 조회",
  "provider": "AdPlatform",
  "version": "v3",
  "category": "analytics",
  "capabilities": ["analysis.metrics"],
  "operations": [
    {
      "name": "get_metrics",
      "effect": "read",
      "idempotency": "idempotent",
      "requires_approval": false
    }
  ],
  "required_scopes": ["ads.metrics.read"],
  "auth_type": "oauth2",
  "data_residency": "kr",
  "status": "Active"
}
```

기계가 읽을 수 있는 스키마: [`tool.schema.json`](../intent-os-spec/schemas/tool.schema.json)

---

## 9. Validation Rules

### 9.1 등록 검증

```
Tool 등록 요청
  ↓
input_schema / output_schema 존재 및 파싱 검증 (INV-TOL-01) ── 없으면 반려
  ↓
operation별 effect 선언 확인 (TOL-002) ── 없으면 반려
  ↓
effect ∈ {irreversible, external_visible} 인 operation
  → requires_approval = true 강제 (INV-TOL-05)
  ↓
idempotency 선언 확인 (TOL-004) ── 없으면 non_idempotent로 보수적 가정
  ↓
required_scopes 확인 (TOL-003)
  ├── 와일드카드(*) 포함 → 반려. 명시적 열거 요구
  └── 연결 자격이 선언 범위를 넘는가 (INV-TOL-04) → 초과 시 반려
  ↓
capabilities 선언 확인 (TOL-005) ── Taxonomy 정규화 (e006a)
  ↓
error_codes → failure_class 매핑 확인 (TOL-008)
  ↓
data_residency 확인 → Policy(리전 제한)와 정합 검사
  ↓
Registered → Cold Start 계획 생성 (read 작업만으로) → Evaluating
```

**Cold Start를 `read` 작업으로만 한다.** 검증하려고 광고를 집행할 수는 없다.

### 9.2 호출 파이프라인

```
Tool 호출 요청 (Execution 생성)
  ↓
Tool status ∈ {Active} 확인 ── Degraded/Quarantined면 거부
  ↓
input을 input_schema로 검증 ── 불일치 시 즉시 실패 (호출하지 않는다)
  ↓
effect 기반 Policy 평가 (TOL-006, INV-TOL-05)
  ├── read                          → 통과
  ├── write                         → Policy 평가
  └── irreversible/external_visible → Policy 평가 + 승인 확인
  ↓
rate_limit 검사 ── 초과 시 대기 또는 Queued 유지
  ↓
idempotency 처리
  ├── idempotent          → 그대로 호출
  ├── idempotent_with_key → idempotency_key 생성/재사용
  └── non_idempotent      → 재시도 불가 표시 (INV-TOL-03)
  ↓
호출 (timeout_ms 적용)
  ↓
output을 output_schema로 검증
  ├── 통과   → Outcome 생성
  └── 불일치 → 실패 기록 + 연속 위반 카운트 증가 (INV-TOL-06)
  ↓
error_code → failure_class 매핑 (TOL-008)
  ↓
Execution 종료 → Outcome 생성 (e014)
```

---

## 10. Examples

### 예시 1 — 읽기 Tool (승인 불필요)

```
task_002  홍대 경쟁 학원 5곳 가격 조사
  ↓ required_capabilities: [research.web]
후보: tool_search / perplexity:sonar / human:조사원
  ↓ Decision dec_090: tool_search (비용 1/50, 지연 1/20)
  ↓
exe_205  tool_search.query  read  idempotent
         Policy 평가: read → 통과 (승인 불필요)
         220ms / 0.002 USD
  ↓
out_290  succeeded → art_302 (비교표)
```

### 예시 2 — 비가역 Tool (승인 필수)

```
task_010  윈터캠프 인스타그램 캠페인 본 집행 285만원
  ↓ required_capabilities: [advertising.campaign_execution]
후보: tool_adplatform_campaign  ← 대안이 없다
  ↓ Decision dec_210 (alternatives_considered: [], forced: true)
  ↓
exe_301 생성 시도
  ↓
Policy 평가
  ├── pol_012 (고액 실행 승인)  → require_approval
  └── tool operation requires_approval: true → 필수
  ↓
approval.requested → 대표
  ↓ 대표 승인 (14:58)
  ↓
호출: create(name, daily_budget_krw: 190000, creative_ref: art_450,
             idempotency_key: "exe_301")
  ↓
out_402  succeeded → art_512 (external_ref: camp_88421)
```

`idempotency_key`에 `execution_id`를 쓴다. 네트워크 오류로 재호출해도 캠페인이 둘 생기지 않는다.

### 예시 3 — 스키마 드리프트

```
2026-08-20  AdPlatform v3가 응답 필드를 조용히 변경
  exe_450  output: { "id": "camp_9021", ... }   ← campaign_id 없음
  ↓ output_schema 위반 (required: campaign_id)
  실패 1회
  exe_451  실패 2회
  exe_452  실패 3회
  ↓ INV-TOL-06
tool_adplatform_campaign → Degraded
  ↓
Event: resource.drift_detected
후보군에서 제외 → 진행 중이던 Plan은 Suspended
  ↓
운영자가 스키마 갱신 (campaign_id ← id 매핑 추가, v3 → v3.1)
  ↓ 재검증 (read 작업)
Active 복귀
```

**3회 실패 후 자동 격리가 없으면 남은 예산을 실패로 다 태운다.**

### 예시 4 — non_idempotent Tool의 재시도 금지

```
task_015  대기자 명단 학부모 40명에게 모집 마감 안내 발송
  ↓
tool_messaging.send  external_visible  non_idempotent
  ↓
exe_520  호출 → 30초 타임아웃
  ↓
Runtime의 재시도 판단
  ├── failure_class: timeout
  ├── Tool idempotency: non_idempotent
  └── INV-TOL-03 → 자동 재시도 금지
  ↓
결과: Execution → TimedOut
      Outcome → status: failed, partial_reason: "발송 여부 불명"
      Task → escalate (인간이 발송 로그를 확인해야 한다)
```

**40명에게 같은 메시지를 두 번 보내는 것보다 사람이 확인하는 편이 낫다.**

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **non_idempotent Tool의 타임아웃** | 재시도하지 않는다(예시 4). `escalate`하고 사람이 외부 상태를 확인한다. 자동 판단할 수 없는 유일한 실패 유형이다 |
| **읽기 Tool이 쓰기를 수행** | INV-TOL-02 위반. 즉시 `Quarantined`. 선언과 실제가 다른 Tool은 신뢰할 수 없다 |
| **Tool 인증이 만료됨** | Tool 정의는 유지하고 연결(Connection)만 만료 표시한다. `failure_class: policy_violation`으로 매핑하고 재인증을 요구한다 |
| **같은 Capability를 여러 Tool이 제공** | 정상이다. Decision Engine이 비용·지연·신뢰도로 선택한다. Tool이라고 해서 선택 대상이 아닌 것이 아니다 |
| **대안 없는 Tool (Forced Action)** | Decision을 `alternatives_considered: []` + `forced: true`로 남긴다([INV-02](e000a-entity-relationships.md) 예외 조항). 기록 자체를 생략하지 않는다 |
| **rate limit에 지속적으로 걸림** | `Degraded`가 아니라 스케줄링 문제다. Execution을 `Queued`에 유지하고 백오프한다. 반복되면 Tool의 `rate_limit`을 실측값으로 보정한다 |
| **Tool 출력이 스키마는 맞는데 내용이 틀림** | Tool의 문제가 아니라 [Evaluation](e015-evaluation.md)의 영역이다. 스키마 검증은 형식만 본다 |
| **외부 플랫폼이 Tool 버전을 폐기** | `Deprecated` → 대체 Tool 등록 → 참조하는 Workflow의 Capability 매칭이 자동으로 새 Tool을 찾는다. **Workflow가 Resource를 지정하지 않는 이유가 여기서 드러난다**([e022 INV-WFL-03](e022-workflow.md)) |
| **Artifact를 Tool로 승격** | 반복 사용되는 스크립트·프롬프트 템플릿은 Tool로 등록 가능하다. 이때 `input_schema`를 새로 정의해야 하며, 원본 Artifact는 그대로 남는다([e016 §2](e016-artifact.md)) |

---

## 12. Open Issues (v1.0)

### Tool과 Resource 스키마의 통합

현재 `tool.schema.json`과 `resource.schema.json`이 분리되어 있으나, Tool은 Resource의 부분집합이다. `resource.schema.json`이 `$ref`로 Tool 확장을 참조하는 구조가 옳은지, 별도로 두는 것이 옳은지 결정이 필요하다.

### 연결(Connection) Entity의 필요성

`auth_type`과 `required_scopes`는 Tool에 있지만, 실제 자격 증명과 계정 바인딩은 별도 개념이다. 하나의 Tool을 여러 계정으로 연결하는 경우(학원 계정 2개)를 표현할 수 없다.

### 타임아웃 후 상태 조회 프로토콜

`non_idempotent` Tool의 타임아웃을 자동 해소하려면 "방금 그 작업이 성공했는지" 물을 수 있어야 한다. 조회 operation을 필수화할지, 선택으로 둘지 미정이다.

### 스키마 자동 복구

§10 예시 3의 필드명 변경은 기계적으로 감지·수정 가능한 유형이다. 자동 매핑 제안 기능이 필요한지, 사람 확인을 항상 요구할지 결정이 필요하다.

### 앞으로 보강해야 할 항목

- Connection Entity 정의 여부
- Tool 카테고리별 표준 operation 명명 규칙
- `code_exec` 카테고리의 샌드박스 요구사항
- 실제 예시 30~50개
