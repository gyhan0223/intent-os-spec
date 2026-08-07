# Marketing Thin Reference Implementation

Intent OS 전체를 만들기 전에 핵심 흐름 하나를 실행 가능한 코드로 검증하는 Phase-0 구현이다.

## Scope

- Domain: 교육 마케팅 문서 생성
- Tasks: `Research -> Creation -> Verification`
- Resources: 모델 3개 + 웹 검색 1개
- Router: Rule Based + deterministic utility ranking
- Prompt Compiler: Goal/Task/Constraint/선행 Artifact 조합
- Execution/Outcome: Task별 실행과 1:1 결과 기록
- Artifact: Outcome별 텍스트 산출물
- Evaluation: 자동 Rubric + 선택적 사용자 평점(1~5)
- Invariants: Goal reachability, Task DAG, Decision provenance, Execution/Outcome 1:1, Artifact ownership, timestamp ordering

## Resource Catalog

| Resource | Role |
|---|---|
| `tool:web-search` | Research 우선 |
| `model:fast` | 저비용/저지연 대안 |
| `model:balanced` | Creation 우선 |
| `model:quality` | Verification 우선 |

기본 Adapter는 외부 Provider를 가장하지 않는 **오프라인 결정론적 Stub**이다. 네트워크/API Key 없이 CI에서 orchestration을 재현하기 위한 장치이며, 실제 Provider 연동 시 `DeterministicAdapter.execute(...)`와 동일한 계약으로 교체한다.

## Flow

```text
Raw Goal
  -> Goal
  -> Intent
  -> Research Task -------> Web Search Resource
  -> Creation Task -------> Balanced Model Resource
  -> Verification Task ---> Quality Model Resource
  -> Execution x3
  -> Outcome x3
  -> Artifact x3
  -> Evaluation x3
  -> Final reviewed marketing document
```

## Run

저장소 루트에서:

```bash
python -m reference.marketing_thin
```

다른 Goal/평점:

```bash
python -m reference.marketing_thin \
  --goal "윈터스쿨 상담 예약을 늘릴 마케팅 문서를 조사부터 검수까지 완성한다" \
  --rating 4
```

## Test

```bash
python -m unittest discover -s reference/marketing_thin/tests -v
```

Smoke Test는 다음을 검증한다.

1. Route가 `web-search -> balanced -> quality`로 재현된다.
2. Goal/Intent/Task/Decision/Execution/Outcome/Artifact/Evaluation이 기존 canonical JSON Schema를 통과한다.
3. 종료 Execution마다 Outcome이 정확히 하나 존재한다.
4. 모든 Execution은 ResourceSelection Decision을 추적할 수 있다.
5. Task Graph가 DAG다.
6. 사용자 평점이 최종 Evaluation의 `satisfaction`으로 흐른다.

## Not Included Yet

- 실제 OpenAI/Anthropic/Google/Search API 호출
- DB/Persistence
- 비동기 Queue
- 재시도/대체 Resource 실행
- Learning Engine 업데이트
- 실제 전환율/매출 기반 Deferred Evaluation

이 구현의 성공 기준은 카피 품질 자체가 아니라 아래 시스템 계약이 실제 코드로 완주되는 것이다.

```text
Goal -> Intent -> Task -> Resource Decision -> Execution -> Outcome -> Artifact -> Evaluation
```
