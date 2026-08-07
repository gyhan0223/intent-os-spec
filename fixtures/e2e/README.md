# End-to-End Golden Fixtures

**Version:** 0.1.0  
**Status:** Draft Fixture Contract  
**Last Updated:** 2026-08-07

이 디렉터리는 Intent OS의 **시스템 전체 실행 경로**를 고정하는 Golden Fixture 모음이다. Entity별 단편 예시가 아니라, 하나의 사용자 요청이 Goal에서 시작해 Decision, Execution, Outcome, Evaluation, Memory, Resource Profile 학습까지 어떻게 연결되는지를 재현한다.

## 목적

Golden Fixture는 다음 질문에 답해야 한다.

1. 같은 입력에서 어떤 Entity들이 생성되는가?
2. 각 Entity의 참조 ID가 다음 Entity까지 끊기지 않고 이어지는가?
3. 실패, Timeout, Hard Constraint, Human Escalation 같은 비정상 경로도 표현 가능한가?
4. 기존 JSON Schema가 실제 End-to-End 흐름을 함께 표현할 수 있는가?
5. 스키마 변경 시 기존 대표 시나리오가 깨지는지를 CI에서 즉시 감지할 수 있는가?

이 Fixture는 **전역 Invariant 검증기의 대체물이 아니다.** 현재 단계에서는 (a) 개별 Entity의 JSON Schema 적합성, (b) Fixture 내부 핵심 참조 무결성만 검증한다. 전역 Invariant 16개에 대한 상태 기반 검증은 별도 작업으로 확장한다.

## Fixture Envelope

`golden-fixtures-v0.1.json`은 10개의 독립 시나리오를 가진다. 파일명을 버전으로 고정해 스키마와 Fixture의 호환성 변화를 추적한다.

```json
{
  "fixture_version": "0.1.0",
  "scenarios": [
    {
      "scenario_id": "S01",
      "title": "Happy path",
      "covers": ["goal", "intent", "planning", "decision", "execution", "evaluation", "learning"],
      "process_trace": [],
      "records": [
        { "schema": "goal.schema.json", "data": {} }
      ]
    }
  ]
}
```

- `process_trace`: Clarification, Candidate Filtering, Capability Mapping처럼 **Entity가 아닌 Process 단계**의 관찰 기록이다.
- `records`: 영속 Entity 또는 Runtime record의 실제 JSON이다. `schema`는 `intent-os-spec/schemas/` 아래의 정본 JSON Schema 파일을 가리킨다.
- `data`: 해당 Schema가 직접 검증하는 실제 Entity JSON이다.

## 10개 시나리오

| ID | 시나리오 | 핵심 검증 포인트 |
|---|---|---|
| S01 | 정상 단일 실행 | Goal → Intent → Plan → Task → Decision → Execution → Outcome → Evaluation → Memory |
| S02 | Clarification 필요 | 모호한 Goal이 사용자 응답으로 Clarified 된 뒤 실행 가능해지는 경로 |
| S03 | 낮은 Intent Confidence | 자동 선택을 멈추고 사용자 확인 후 Selected 되는 경로 |
| S04 | Resource 실패 후 Fallback | 첫 Execution 실패 → Outcome/Evaluation 기록 → 새 Decision → 대체 Resource 성공 |
| S05 | Timeout 후 Reassign | TimedOut Execution을 보존한 채 다른 Resource로 재할당 |
| S06 | Hard Constraint 필터 | Budget Hard Constraint가 후보를 Decision 이전에 제거 |
| S07 | Human Escalation | 고위험 상황에서 자동 실행 대신 인간 승인 Decision을 선행 |
| S08 | 병렬 Task Graph | 독립 Task 2개를 병렬 수행한 후 후행 Synthesis Task가 합류 |
| S09 | Deferred Evaluation | 즉시 proxy 평가 후 measurement lag 경과 뒤 실제 Goal Alignment로 재평가 |
| S10 | Learning/Profile Update | Evaluation 결과가 Memory로 저장되고 Resource Profile snapshot이 갱신 |

## 실행 흐름 계약

대표적인 Fixture는 아래 순서를 따른다.

```text
User Request
  → Goal Extraction
  → (optional) Clarification
  → Context / Constraint
  → Intent Inference
  → Plan + Task Graph
  → Capability Mapping
  → Candidate Filtering
  → Decision
  → Execution
  → Outcome
  → Evaluation
  → Memory
  → Resource Profile Update
```

중요한 점은 **Process와 Entity를 섞지 않는 것**이다. Clarification은 Process이며 Goal의 버전/상태를 바꿀 수 있지만 별도 Entity로 위조하지 않는다. Capability Mapping도 Process이며 결과는 Task.required_capabilities와 Decision.inputs_snapshot 등에 반영된다.

## 검증

```bash
python3 tools/validate-e2e-fixtures.py
```

검증기는 다음을 확인한다.

- Fixture JSON 자체의 구조
- `schema` 파일이 실제로 존재하는지
- 모든 `data`가 지정된 JSON Schema를 통과하는지
- scenario_id 중복 여부
- Intent → Goal 참조
- Task → Goal 참조
- Task Graph → Task 참조
- Decision.subject → Goal/Task 참조
- Execution → Task/Decision 참조
- Outcome → Execution 참조
- Evaluation → Outcome 참조
- Memory → Goal/Decision/Execution 참조

여기서 다루지 않는 항목(예: Goal당 Active Plan 정확히 1개, 모든 종료 Execution에 정확히 Outcome 1개, 시간 순서 전역 검사)은 후속 **Invariant Validator**의 책임이다.

## 변경 규칙

1. Canonical Schema가 바뀌면 이 Fixture도 같이 수정한다.
2. 스키마 변경으로 대표 시나리오가 깨졌는데 의도된 변경이라면 Fixture diff를 PR에 명시한다.
3. 새로운 실패 모드가 실제 구현에서 발견되면 10개를 무작정 늘리기보다 기존 시나리오의 커버리지로 흡수 가능한지 먼저 검토한다.
4. 새로운 시스템 경계가 생겨 기존 10개로 표현 불가능할 때만 S11+를 추가한다.
