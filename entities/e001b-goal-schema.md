# Entity 001-B: Goal JSON Schema (Canonical Goal Representation v2)

- **Version:** v2.0 Draft
- **Status:** Core Entity
- **Format:** Annex — e001 Goal의 부속 문서 (e000 §7.1)
- **Last Updated:** 2026-08-04
- **Schema:** [`goal.schema.json`](../intent-os-spec/schemas/goal.schema.json)

---

## 1. Why v2

v1 스키마는 MVP에는 충분했지만, AI OS의 핵심 Entity로 쓰기에는 부족했다. 운영체제 수준에서 특히 부족했던 것은 다음 아홉 가지다.

| 부족했던 것 | v2에서의 해결 |
|---|---|
| Goal의 계층 구조 | `parent_goal`, `child_goals` |
| Goal 간 의존성 | `dependencies`, `related_goals` |
| Goal 소유자 | `stakeholders` — role 기반, Owner 정확히 1명 강제 |
| Goal 생성 출처 | `metadata.source`, `metadata.origin_ref` |
| Goal 변경 이력 | `metadata.history` |
| Goal 버전 | `version` |
| Goal 신뢰도 | `quality.confidence` |
| Goal 충돌 | `related_goals[].relationship = CONFLICTS_WITH` + `resolution` |
| Goal 우선순위 계산 정보 | `priority.factors`, `priority.computed_score` |

또한 v1에서 평평한 문자열이었던 필드들이 구조화되었다.

- `objective: string` → `objective: { description, desired_state, secondary_metrics }`
- `constraints: string[]` → `constraints: { budget, deadline, location, legal, resource_limits }`
- `priority: string` → `priority: { level, weight, factors, computed_score }`
- `status: string` → `status: { phase, progress, entered_at }`
- `stakeholders: string[]` → `stakeholders: [{ role, name, type }]`

---

## 2. Design Principles

1. **Goal은 What만 담는다.** Method, Resource, Task는 어떤 필드에도 들어갈 수 없다 (Rule G-002~G-004).
2. **측정 가능성이 1급 시민이다.** Success Metric은 자유 문자열이 아니라 `{ metric, operator, target, unit }` 구조다. Runtime이 목표 달성 여부를 기계적으로 판정할 수 있어야 한다.
3. **관계의 정본은 Goal Graph다.** `dependencies` / `related_goals`는 Goal 단독 조회를 위한 로컬 뷰이며, source of truth는 [Goal Graph](e001a-goal-graph.md)의 edges다. 둘이 불일치하면 Graph가 이긴다.
4. **상태는 State Machine이 관리한다.** `status.phase`는 스키마가 enum으로 형태만 검증하고, 전이의 합법성은 [State Machine](e001c-goal-state-machine.md)이 검증한다.
5. **모든 변경은 추적 가능하다.** 필드가 바뀌면 `version`이 증가하고 `metadata.history`에 기록된다.

---

## 3. Field Reference

### 3.1 Identity

| 필드 | 타입 | 필수 | 의미 |
|---|---|:---:|---|
| `goal_id` | string | ✅ | 전역 유일 식별자. `goal_` + ULID 권장 |
| `version` | integer ≥ 1 | ✅ | 변경 시마다 +1. 이력은 `metadata.history`에 |
| `title` | string | ✅ | 사람이 읽는 이름 |
| `goal_type` | enum | ✅ | Outcome / Optimization / Learning / Exploration / Maintenance / Creation / Decision / Automation |

### 3.2 Objective

| 필드 | 타입 | 의미 |
|---|---|---|
| `objective.description` | string (필수) | 원하는 미래 상태의 서술. 방법/AI/Tool 이름 금지 |
| `objective.desired_state.metric` | string | 측정 대상 지표. 예: `registered_students` |
| `objective.desired_state.operator` | enum | `>=` `<=` `>` `<` `==` `!=` `between` `exists` `maximize` `minimize` |
| `objective.desired_state.target` | number \| string \| array | 목표값. `between`이면 `[min, max]` |
| `objective.desired_state.unit` | string | 단위 |
| `objective.desired_state.baseline` | number \| string \| null | 시작 시점 값. progress 계산 기준 |
| `objective.secondary_metrics` | array | 보조 지표. desired_state와 동일 구조 |

### 3.3 Motivation

`motivation: string[]` — 왜 이 Goal을 원하는가. Motivation에 따라 전략이 달라지므로 여러 개를 허용한다. 예: `["매출 증가", "브랜드 인지도 향상"]`

### 3.4 Constraints

| 필드 | 타입 | 예 |
|---|---|---|
| `constraints.budget` | `{ max, min, currency }` | `{ "max": 5000000, "currency": "KRW" }` |
| `constraints.deadline` | date | `"2027-01-10"` |
| `constraints.location` | string[] | `["서울"]` |
| `constraints.legal` | string[] | 규제/법적 제약 |
| `constraints.resource_limits` | `[{ resource, limit, unit }]` | 특정 Resource 사용량 한도 |
| `constraints.other` | string[] | 분류 밖의 제약 |

### 3.5 Priority

우선순위는 등급 하나가 아니라 **계산 근거를 포함한 객체**다.

| 필드 | 타입 | 의미 |
|---|---|---|
| `priority.level` | enum | Low / Medium / High / Critical |
| `priority.weight` | 0~1 | 정규화된 가중치. Planner 스케줄링에 사용 |
| `priority.factors` | object | Goal Score의 입력값: `impact`, `urgency`, `risk`, `strategic_alignment` |
| `priority.computed_score` | number \| null | $Score = w_p P + w_i I + w_u U - w_r R + w_c C$ 결과 ([Goal Graph §10](e001a-goal-graph.md)) |
| `priority.computed_at` | date-time | 마지막 계산 시각 |

### 3.6 Context

| 필드 | 의미 |
|---|---|
| `context.current_state` | `desired_state.metric`에 대응하는 현재 값. 예: `{ "registered_students": 42 }` |
| `context.environment` | 시장, 경쟁, 계절 등 외부 환경 |
| `context.assumptions` | 가정. 깨지면 재검증 트리거 |

### 3.7 Stakeholders

```json
"stakeholders": [
  { "role": "Owner", "name": "Academy", "type": "organization" }
]
```

- `role`: `Owner` / `Sponsor` / `Approver` / `Contributor` / `Affected`
- **Owner는 정확히 1명이어야 한다.** 스키마의 `contains` + `minContains: 1` + `maxContains: 1`로 강제된다. 소유자 없는 Goal은 시스템이 책임 주체를 알 수 없으므로 Executable 상태로 전이할 수 없다.
- `type`: `user` / `organization` / `agent` / `system` — Goal은 사람뿐 아니라 다른 지능형 주체도 만들 수 있다.

### 3.8 Relationships

| 필드 | 타입 | 의미 |
|---|---|---|
| `parent_goal` | string \| null | 상위 Goal. Root Goal이면 null (Invariant 2) |
| `child_goals` | string[] | 하위 Goal 목록 |
| `dependencies` | `[{ goal_id, relationship, weight }]` | `DEPENDS_ON` / `REQUIRES` / `BLOCKS` |
| `related_goals` | `[{ goal_id, relationship, weight, resolution }]` | `ENABLES` / `SUPPORTS` / `CONFLICTS_WITH` |

**Goal 충돌**은 `CONFLICTS_WITH` 관계로 표현한다. `resolution`이 null이면 미해소 충돌이며, 미해소 충돌이 있는 Goal은 Executable로 전이할 수 없다 ([State Machine Guard](e001c-goal-state-machine.md) 참조).

### 3.9 Status

| 필드 | 타입 | 의미 |
|---|---|---|
| `status.phase` | enum (필수) | State Machine의 12개 상태 중 하나 |
| `status.progress` | 0~1 | baseline→target 대비 current_state 진행률 |
| `status.entered_at` | date-time | 현재 phase 진입 시각 |
| `status.blocked_reason` | string \| null | Suspended/Failed 사유 |

### 3.10 Quality

| 필드 | 타입 | 의미 |
|---|---|---|
| `quality.confidence` | 0~1 | 이 Goal이 사용자의 실제 의도를 반영한다는 시스템의 신뢰도 |
| `quality.completeness` | 0~100 | Goal Completeness Score ([e001d](e001d-goal-validation.md)) |
| `quality.completeness_level` | 1 \| 2 \| 3 | Raw / Structured / Executable |

### 3.11 Metadata

| 필드 | 타입 | 의미 |
|---|---|---|
| `metadata.created_by` | string (필수) | 생성 주체: 사용자 ID, agent ID, `system` |
| `metadata.created_at` | date-time (필수) | 생성 시각 |
| `metadata.updated_at` | date-time | 마지막 수정 시각 |
| `metadata.source` | enum (필수) | `conversation` / `api` / `inference` / `decomposition` / `import` / `trigger` / `system` |
| `metadata.origin_ref` | string \| null | 출처 참조: 대화 ID, 상위 Goal ID 등 |
| `metadata.history` | array | 버전별 변경 이력: `{ version, changed_at, changed_by, change_type, description, changes }` |

`source` 값의 의미:

- `conversation` — 사용자와의 대화에서 추출
- `api` — 외부 시스템이 API로 직접 생성
- `inference` — 시스템이 Request로부터 추론 (confidence가 특히 중요)
- `decomposition` — 상위 Goal의 분해로 생성 (`origin_ref` = 상위 goal_id)
- `import` — 외부 도구(Jira, Notion 등)에서 가져옴
- `trigger` — 스케줄/이벤트 트리거가 생성
- `system` — 시스템 유지 목적으로 자동 생성

---

## 4. Full Example

```json
{
  "goal_id": "goal_01HZX9M4Y4QF2X",
  "version": 3,
  "title": "2027 윈터스쿨 학생 모집",
  "goal_type": "Outcome",

  "objective": {
    "description": "학생 100명 모집",
    "desired_state": {
      "metric": "registered_students",
      "operator": ">=",
      "target": 100,
      "unit": "students",
      "baseline": 0
    }
  },

  "motivation": ["매출 증가", "브랜드 인지도 향상"],

  "constraints": {
    "budget": { "max": 5000000, "currency": "KRW" },
    "deadline": "2027-01-10",
    "location": ["서울"],
    "legal": [],
    "resource_limits": []
  },

  "priority": {
    "level": "High",
    "weight": 0.91,
    "factors": { "impact": 9, "urgency": 10, "risk": 5 },
    "computed_score": 8.7,
    "computed_at": "2026-08-04T12:10:00Z"
  },

  "context": {
    "current_state": { "registered_students": 42 },
    "environment": {},
    "assumptions": ["겨울방학 일정 유지"]
  },

  "stakeholders": [
    { "role": "Owner", "name": "Academy", "type": "organization" }
  ],

  "parent_goal": "goal_01HZX9AAAAAAAA",
  "child_goals": [],

  "dependencies": [
    { "goal_id": "goal_01HZX9BBBBBBBB", "relationship": "DEPENDS_ON", "weight": 0.7 }
  ],

  "related_goals": [
    {
      "goal_id": "goal_01HZX9CCCCCCCC",
      "relationship": "CONFLICTS_WITH",
      "resolution": "예산 분할 조정으로 해소"
    }
  ],

  "status": {
    "phase": "Planning",
    "progress": 0.42,
    "entered_at": "2026-08-04T12:10:00Z"
  },

  "quality": {
    "confidence": 0.94,
    "completeness": 92,
    "completeness_level": 3
  },

  "metadata": {
    "created_by": "user_gyhan",
    "created_at": "2026-08-04T12:00:00Z",
    "updated_at": "2026-08-04T12:10:00Z",
    "source": "conversation",
    "origin_ref": null,
    "history": [
      {
        "version": 1,
        "changed_at": "2026-08-04T12:00:00Z",
        "changed_by": "user_gyhan",
        "change_type": "created",
        "description": "대화에서 Goal 추출"
      },
      {
        "version": 2,
        "changed_at": "2026-08-04T12:05:00Z",
        "changed_by": "system",
        "change_type": "clarified",
        "description": "예산/기한/지역 제약 보강",
        "changes": {
          "constraints.deadline": { "from": null, "to": "2027-01-10" }
        }
      },
      {
        "version": 3,
        "changed_at": "2026-08-04T12:10:00Z",
        "changed_by": "system",
        "change_type": "status_changed",
        "description": "Executable → Planning"
      }
    ]
  }
}
```

---

## 5. v1 → v2 Migration

| v1 필드 | v2 필드 |
|---|---|
| `objective` (string) | `objective.description` |
| `target_state.value` / `unit` | `objective.desired_state.target` / `unit` |
| `success_metrics` (string[]) | `objective.desired_state` + `secondary_metrics` |
| `motivation` (string) | `motivation` (string[]) |
| `constraints` (string[]) | `constraints.*` (구조화) — 매핑 불가 항목은 `constraints.other` |
| `priority` (string) | `priority.level` |
| `deadline` | `constraints.deadline` |
| `context` (자유 object) | `context.current_state` / `environment` / `assumptions` |
| `stakeholders` (string[]) | `stakeholders[]` — role은 기본 `Affected`, Owner는 별도 지정 필요 |
| `assumptions` | `context.assumptions` |
| `status` (string) | `status.phase` — 상태명 매핑: Draft→Created, Clarifying→Created, Confirmed→Structured, Learning→Monitoring, 나머지 동일 |
| `completeness_score` | `quality.completeness` |
| `completeness_level` | `quality.completeness_level` |
| (없음) | `version`, `title`, `parent_goal`, `child_goals`, `dependencies`, `related_goals`, `quality.confidence`, `metadata` — 마이그레이션 시 기본값 생성 필요 |

---

## 6. Open Issues

- `desired_state.target`이 정성적인 경우(예: Creation Goal의 "브랜드 아이덴티티 제작")의 판정 방법 — Quality Measure의 형식화 필요
- `constraints`의 스키마를 Constraint Entity(004)가 정의되면 `$ref`로 교체
- `stakeholders[].name`을 자유 문자열이 아닌 주체 ID로 강제할지 여부
- 다중 통화, 기간형 deadline(`duration`) 지원
