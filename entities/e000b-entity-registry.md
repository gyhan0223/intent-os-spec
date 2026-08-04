# Entity 000-B: Entity Registry (Frozen Roster)

- **Version:** v2.0 — **FROZEN**
- **Status:** Meta Specification
- **Last Updated:** 2026-08-04

---

## 0. 동결 선언

> **Intent OS의 Core Entity는 25개다. 이 목록은 v2.0에서 동결되었다.**

이 문서는 "어떤 Entity가 존재하는가"에 대한 **단일 권위(Single Source of Truth)** 다. 다른 문서가 이 목록과 다르게 말하면 이 문서가 옳다.

### 왜 동결하는가

Entity를 계속 늘리면 세 가지가 무너진다.

| 무너지는 것 | 이유 |
|---|---|
| **관계 모델** | Entity 하나가 늘면 Cardinality 행이 최대 25개 늘어난다. 27개에서 30개가 되면 관계는 배로 늘어난다 |
| **불변식** | 새 Entity마다 기존 16개 전역 불변식을 재검토해야 한다 |
| **구현 가능성** | 목록이 움직이는 명세는 구현할 수 없다. 구현자는 무엇이 최종인지 알아야 한다 |

명세의 목적은 **개발자 여러 명이 각자 구현해도 같은 결과를 만드는 것**이다. 그러려면 대상 집합이 먼저 닫혀야 한다.

---

## 1. 동결이 고정하는 것 / 고정하지 않는 것

| | 고정된다 (변경 시 major) | 고정되지 않는다 (계속 개정) |
|---|---|---|
| **번호** | `E013 = Execution` 영구 | — |
| **이름** | `Execution`을 `Run`으로 개명 불가 | `display_name`, 한국어 표현 |
| **Rule Prefix** | `EXE`는 Execution 전용, 영구 예약 | Rule 개수와 내용 |
| **계층 위치** | Entity / Process / Runtime State 분류 | — |
| **개수** | 25개 (+ 구조 문서 3개) | — |
| **속성** | — | 필드 추가·삭제·타입 변경 |
| **불변식** | — | 추가·수정 (단 삭제는 major) |
| **스키마** | `$id` 경로 | 필드 정의 |
| **Lifecycle** | — | 상태 추가·전이 변경 |

> **동결된 것은 "무엇이 존재하는가"이지 "그것이 무엇인가"가 아니다.**

각 Entity의 내부 명세는 v1.0 Draft이며 계속 개정된다. 동결된 것은 **목록과 식별자**다.

---

## 2. Registry — Core Entity 25개

| No | Entity | Prefix | 계층 | 스키마 | 준수 |
|---|---|---|---|---|---|
| 001 | Goal | `G` | 기반 | `goal.schema.json` | L2 |
| 002 | Intent | `I` | 기반 | `intent.schema.json` | L2 |
| 003 | Context | `C` | 기반 | `context.schema.json` | L2 |
| 004 | Constraint | `CN` | 기반 | `constraint.schema.json` | L2 |
| 005 | Task | `T` | 분해 | `task.schema.json` | L2 |
| 006 | Capability | `CP` | 분해 | `capability.schema.json` | L2 |
| 007 | Resource | `R` | 분해 | `resource.schema.json` | L2 |
| 008 | Plan | `P` | 분해 | `plan.schema.json` | L2 |
| 009 | Decision | `D` | 결정 | `decision.schema.json` | L2 |
| 010 | Memory | `M` | 학습 | `memory.schema.json` | L2 |
| 011 | Knowledge | `K` | 학습 | `knowledge.schema.json` | L2 |
| 012 | Feedback | `F` | 평가 | `feedback.schema.json` | L2 |
| 013 | Execution | `EXE` | 실행 | `execution.schema.json` | L2 |
| 014 | Outcome | `OUT` | 실행 | `outcome.schema.json` | L2 |
| 015 | Evaluation | `EVA` | 평가 | `evaluation.schema.json` | L2 |
| 016 | Artifact | `ART` | 실행 | `artifact.schema.json` | L2 |
| 017 | Assumption | `ASM` | 거버넌스 | `assumption.schema.json` | L2 |
| 018 | Risk | `RSK` | 거버넌스 | `risk.schema.json` | L2 |
| 019 | Policy | `POL` | 거버넌스 | `policy.schema.json` | L2 |
| 020 | Event | `EVT` | 운영 | `event.schema.json` | L2 |
| 021 | Session | `SES` | 운영 | `session.schema.json` | L2 |
| 022 | Workflow | `WFL` | 운영 | `workflow.schema.json` | L2 |
| 023 | Agent | `AGT` | 운영 | `agent.schema.json` | L2 |
| 024 | Tool | `TOL` | 운영 | `tool.schema.json` | L2 |
| 025 | Resource Profile | `RPF` | 운영 | `resource-profile.schema.json` | L2 |

### 구조 문서 3개

Entity가 아니라 **Entity들의 구조**를 정의한다. 별도 번호를 쓰지 않고 부모 Entity의 하위 번호를 쓴다.

| No | 문서 | Prefix | 정의 대상 | 스키마 |
|---|---|---|---|---|
| 001-A | [Goal Graph](e001a-goal-graph.md) | `GG` | Goal 간 관계 그래프 | `goal-graph.schema.json` |
| 005-A | [Task Graph](e005a-task-graph.md) | `TG` | Task 간 의존 그래프 | `task-graph.schema.json` |
| 006-A | [Capability Taxonomy](e006a-capability-taxonomy.md) | `CT` | Capability 이름공간 | `capability-taxonomy.schema.json` |

### 절 확장 문서 3개

Entity 001의 명세가 커져 분리된 것이다([e000 §7](e000-spec-format.md)). **12개 섹션 형식이 적용되지 않는다** — 이들은 그 자체가 e001의 한 섹션이기 때문이다.

| 문서 | e001의 어느 절인가 |
|---|---|
| [e001b-goal-schema.md](e001b-goal-schema.md) | §8 Canonical Representation |
| [e001c-goal-state-machine.md](e001c-goal-state-machine.md) | §6 Lifecycle |
| [e001d-goal-validation.md](e001d-goal-validation.md) | §9 Validation Rules |

---

## 3. Entity가 아닌 것

동결 과정에서 **Entity 후보로 검토했으나 제외한 개념들**이다. 나중에 "이건 왜 없지?"라는 질문이 반복되는 것을 막기 위해 기록한다.

### Process — 수행하는 것 (저장하지 않는다)

| 개념 | 어디에 있는가 |
|---|---|
| Planning | [Volume 3 Stage 3](../v3-runtime.md). 산출물이 [Plan](e008-plan.md) Entity다 |
| Deciding | [Volume 4](../v4-decision-engine.md). 산출물이 [Decision](e009-decision.md) Entity다 |
| Executing | [Volume 3 Stage 5](../v3-runtime.md). 제어 블록이 [Execution](e013-execution.md) Entity다 |
| Evaluating | [Volume 3 Stage 6](../v3-runtime.md). 산출물이 [Evaluation](e015-evaluation.md) Entity다 |
| Learning | [Volume 5](../v5-learning-engine.md). 산출물이 [Memory](e010-memory.md)·[Knowledge](e011-knowledge.md) Entity다 |
| Prediction | [Volume 4-A](../v4a-decision-engine-detail.md). 산출물이 Decision의 `utility_scores`다 |
| Replanning | Planning의 특수 경우. 새 [Plan](e008-plan.md) 버전을 낳는다 |

### Runtime State — Entity의 필드

| 개념 | 어느 필드인가 |
|---|---|
| State | 각 Entity의 `status`. 독립 Entity가 아니다 |
| Progress | `Goal.progress`, `Execution.progress` |
| Budget | [Constraint](e004-constraint.md)의 예산 항목 + `Session.budget` |
| Metric | `Goal.success_criteria`의 지표 정의 + `Outcome.goal_progress` |
| Score | [Resource Profile](e025-resource-profile.md)의 `capability_scores` |

### 다른 Entity에 흡수됨

| 개념 | 어디로 |
|---|---|
| Prompt | `Execution.input_ref`. Resource별 실행 표현이지 Entity가 아니다 |
| Log | `Execution.logs_ref`. 구조화되지 않은 하위 데이터다 |
| Conversation | [Session](e021-session.md)의 대화 버퍼. Session과 함께 소멸한다 |
| Notification | [Event](e020-event.md)의 소비 결과. Event 자체가 아니다 |
| Report | [Artifact](e016-artifact.md)(`type: document`) |
| Message | [Tool](e024-tool.md)(`category: messaging`)의 호출 결과 Artifact |
| Approval | [Policy](e019-policy.md)의 `require_approval` 효과 + Event |
| Issue | 발생한 [Risk](e018-risk.md)(`status: Materialized`) |
| Hypothesis | 검증하려고 만든 것. [Assumption](e017-assumption.md)이 아니다. 실험 Task로 표현한다 |
| Skill | [Capability](e006-capability.md)의 다른 이름. 중복 등록 금지 |
| Model | [Resource](e007-resource.md)(`type: llm`) |
| Persona / Segment | [Artifact](e016-artifact.md)(`type: data`) 또는 [Context](e003-context.md) |

### 보류 — 필요성은 인정되나 아직 결정되지 않음

동결 목록에 넣지 않았다. 추가하려면 §4의 절차를 밟아야 한다.

| 후보 | 왜 필요할 수 있는가 | 왜 아직 넣지 않았는가 |
|---|---|---|
| **Rubric** | [Evaluation](e015-evaluation.md)이 `rubric_id`로 참조하지만 구조가 정의되지 않았다 | [Policy](e019-policy.md)의 하위 개념으로 흡수 가능한지 미결 ([e015 §12](e015-evaluation.md)) |
| **Connection** | 하나의 [Tool](e024-tool.md)을 여러 계정으로 연결할 수 없다 | Tool의 필드 확장으로 해결 가능한지 미결 ([e024 §12](e024-tool.md)) |
| **Budget** | 조직 → Goal → Session → Agent 예산 계층이 표현되지 않는다 | Constraint의 확장으로 충분한지 미결 ([e021 §12](e021-session.md)) |
| **Experiment** | A/B 테스트, Shadow 비교의 설계를 담을 곳이 없다 | Workflow + Shadow Execution 조합으로 충분한지 미결 |

---

## 4. Entity 추가 절차

동결은 "영원히 못 바꾼다"가 아니라 **"바꾸려면 절차를 밟아라"** 다.

### 4.1 심사 질문 5개

**전부 Yes여야 추가할 수 있다.** 하나라도 No면 기존 Entity의 필드나 Process로 표현한다.

```
① 1년 뒤에 식별자로 조회해야 하는가?
   No → Process 또는 Runtime State다

② 기존 25개 Entity의 필드로 표현할 수 없는가?
   No → 그 Entity의 속성을 확장하라

③ 고유한 Lifecycle(2개 이상의 상태 전이)을 갖는가?
   No → 값 객체(Value Object)다. 필드로 충분하다

④ 다른 Entity가 이것을 식별자로 참조해야 하는가?
   No → 내부 구조체다

⑤ 고정 도메인(학원 윈터캠프 모집)으로 설명할 수 있는가?
   No → 정의가 아직 구체적이지 않다
```

### 4.2 절차

```
제안
  ↓
§4.1 심사 질문 5개 통과
  ↓
§3의 "Entity가 아닌 것" 표와 충돌 검사
  ── 이미 기각된 개념이면 기각 사유를 반박해야 한다
  ↓
Prefix 예약 → e000 §3 표에 등록
  ↓
번호 부여 = 현재 최대 번호 + 1 (재사용 금지, §5)
  ↓
12개 섹션 명세 작성 → e000 §11 체크리스트
  ↓
e000a §3 Cardinality 전체표에 행 추가
e000a §2 Entity 지도에 위치 표시
e000a §5 전역 불변식 재검토 (새 불변식이 필요한가)
  ↓
JSON Schema 작성 → tools/validate-examples.py의 DOC_TO_SCHEMA 등록
  ↓
Registry v(major+1) 발행
```

**목록 변경은 항상 major 버전이다.** v2.0 → v3.0. minor로 슬쩍 늘리지 않는다.

### 4.3 폐기 절차

Entity를 없앨 때도 같은 무게로 다룬다.

```
Deprecated 표시 (신규 참조 금지, 기존 참조는 유효)
  ↓
참조하는 모든 Entity에서 마이그레이션
  ↓
참조 0건 확인
  ↓
Retired — 문서는 남긴다. 번호와 Prefix는 영구 예약
  ↓
Registry v(major+1) 발행
```

**문서를 지우지 않는다.** 과거 [Decision](e009-decision.md)의 `inputs_snapshot`이 그 Entity를 참조하고 있을 수 있다.

---

## 5. 번호와 Prefix의 영구 예약

| 규칙 | 이유 |
|---|---|
| 번호는 재사용하지 않는다 | `E013`이 다른 Entity를 가리키게 되면 옛 링크가 조용히 다른 뜻이 된다 |
| Prefix는 재사용하지 않는다 | `Rule EXE-003`이 다른 규칙을 가리키게 된다 |
| 폐기된 번호는 빈칸으로 남는다 | 목록에 구멍이 있는 것이 잘못된 값보다 낫다 |

현재 예약된 번호: **001~025** (빈칸 없음)
다음 가용 번호: **026**

---

## 6. 동결 시점의 상태

| 항목 | 값 |
|---|---|
| Registry 버전 | v2.0 |
| Core Entity | 25개 |
| 구조 문서 | 3개 |
| 절 확장 문서 | 3개 |
| JSON Schema | 29개 |
| 전역 불변식 | 16개 ([e000a §5](e000a-entity-relationships.md)) |
| Cardinality 관계 | 28개 ([e000a §3](e000a-entity-relationships.md)) |
| 준수 등급 | 전 Entity **L2** (12개 섹션 + 스키마) |

### 변경 이력

| 버전 | 날짜 | 변경 |
|---|---|---|
| v1.0 | 2026-08-04 | Core Entity 12개 (Goal ~ Feedback) |
| **v2.0** | **2026-08-04** | **Entity 013~025 추가 (13개). Execution·Outcome을 Process·Runtime State에서 Entity로 정정. 구조 문서 005-A·006-A 추가. 목록 동결** |

---

## 7. Open Issues (v2.0)

### 보류 후보 4개의 결정 시한

§3의 Rubric·Connection·Budget·Experiment는 "필요성은 인정되나 미결"이다. 결정을 미루면 각 Entity의 Open Issue에 계속 남는다. Reference Implementation([Volume 7](../v7-reference-implementation.md)) 착수 전까지는 결론이 필요하다 — 구현이 시작되면 임시방편이 사실상의 표준이 된다.

### 도메인 확장 시의 압력

현재 25개는 학원 마케팅 도메인에서 검증되었다. 다른 도메인(의료·법률·제조)을 다루면 §4.1의 질문 ⑤("고정 도메인으로 설명할 수 있는가")가 오히려 추가를 막는 족쇄가 될 수 있다. 도메인이 늘 때 예시 도메인을 어떻게 확장할지 정해야 한다.

### 구조 문서의 번호 체계

001-A, 005-A, 006-A는 부모 Entity의 하위 번호를 쓴다. 그런데 여러 Entity에 걸치는 구조(예: Decision–Execution–Outcome 사슬 자체)를 문서화해야 한다면 부모가 없다. 별도 번호대(예: S001)가 필요한지 미정이다.
