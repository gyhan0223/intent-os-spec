# Intent OS System Routing Benchmark v0.1

- **Version:** v0.1 Draft
- **Benchmark ID:** `system-routing-v0.1`
- **Status:** Pre-implementation Benchmark Protocol
- **Scope:** System-level evaluation of resource selection and routing
- **Related:** [Volume 4-D — Autonomous Benchmarking](../v4d-autonomous-benchmarking.md)

> 이 벤치마크는 "어떤 AI가 가장 좋은가?"를 측정하지 않는다.
> **같은 Resource pool이 주어졌을 때 Intent OS가 사용자의 직접 선택 또는 고정 기본 모델보다 더 좋은 의사결정을 하는가**를 측정한다.

---

## 1. Research Question

Intent OS의 자동 라우팅이 다음 두 기준선보다 실제 사용자 결과를 개선하는가?

| Arm | 설명 |
|---|---|
| **A — Manual Choice** | 사용자가 각 Task마다 사용할 Resource를 직접 선택 |
| **B — Fixed Default** | 사전에 정한 하나의 기본 Resource를 모든 Task에 사용 |
| **C — Intent OS** | Intent OS가 Goal → Intent → Task → Capability → Resource 흐름으로 자동 선택 |

핵심 가설은 "항상 가장 강한 모델을 쓰는 것"이 아니라 다음이다.

> **Intent OS는 품질을 유지하거나 높이면서 사용자의 선택 부담, 재작업, 비용 또는 지연을 줄인다.**

---

## 2. What This Benchmark Is Not

이 문서는 [Volume 4-D](../v4d-autonomous-benchmarking.md)의 Resource 자체 벤치마크와 목적이 다르다.

- Volume 4-D: `Resource X의 Capability는 얼마나 좋은가?`
- 본 문서: `Intent OS의 Resource 선택 정책은 좋은가?`

따라서 동일한 Resource pool을 세 Arm에 제공해야 한다. Resource pool이 다르면 라우터가 아니라 Resource 차이를 측정하게 된다.

---

## 3. Experimental Unit

기본 실험 단위는 **Task × Arm**이다.

v0.1 Suite는 30개 Task를 사용하며 각 Task를 세 Arm에서 한 번씩 실행한다.

```text
30 Tasks × 3 Arms = 90 Trials
```

가능하면 3회 반복하여 변동성을 측정한다.

```text
30 Tasks × 3 Arms × 3 Repetitions = 270 Trials
```

첫 구현에서는 90 Trials로 시작해도 된다.

---

## 4. Resource Pool Freeze

한 Benchmark Run에서는 Resource pool을 고정한다.

필수 기록:

- Resource ID / Provider / Model or Tool version
- 가격표 snapshot
- Context limit
- Tool-use 지원 여부
- Web/search 지원 여부
- 호출 파라미터
- 실행 날짜
- 지역/언어 설정

### 4.1 Fixed Default 선택

Arm B의 Fixed Default는 **실험 시작 전에** 하나를 지정하며 결과를 보고 바꾸면 안 된다.

선정 원칙:

1. 범용성이 높은 Resource
2. 세 Arm 모두 사용할 수 있는 Resource pool의 구성원
3. 당시 제품의 실제 기본값으로 쓸 법한 선택

---

## 5. Fairness Rules

세 Arm의 차이는 **Resource 선택 방식**이어야 한다.

| 항목 | 규칙 |
|---|---|
| Task prompt | 동일 |
| 사용자 제공 Context | 동일 |
| Resource pool | 동일 |
| 최대 재시도 | 동일 |
| Tool 접근 권한 | 동일한 Resource에는 동일 |
| 출력 최대 길이 | 동일 |
| 시간 제한 | 동일 |
| 평가 Rubric | 동일 |
| 평가자에게 Arm/Model 이름 공개 | 금지 |
| 결과 순서 | 무작위화 |

### 5.1 Intent OS에만 허용되는 것

Intent OS Arm은 다음 내부 처리를 추가로 수행할 수 있다.

- Goal/Intent 해석
- Task decomposition
- Capability matching
- Resource scoring
- Tool selection
- Routing/fallback

이 비용과 지연은 **Arm C의 총비용과 총지연에 포함**한다.

---

## 6. Task Suite

v0.1은 6개 범주 × 5개 Task = 30개로 구성한다.

| Category | Code | 수 | 목적 |
|---|---:|---:|---|
| Writing & Communication | W | 5 | 문체·제약·사용자 의도 적합성 |
| Research & Freshness | R | 5 | 검색·출처·최신성 판단 |
| Reasoning & Planning | P | 5 | 다중 제약, 계획, 트레이드오프 |
| Structured Transformation | S | 5 | JSON/표/규칙 준수, 정확성 |
| Coding & Debugging | C | 5 | 코드 생성, 오류 수정, 테스트 사고 |
| Tool & Resource Choice | T | 5 | 계산/검색/도구 사용 여부 판단 |

Task 정의는 [`cases/system-routing-v0.1.json`](cases/system-routing-v0.1.json)에 둔다.

### 6.1 Development / Holdout Split

- `development`: 20개 — Router 개발 중 반복 실행 가능
- `holdout`: 10개 — 최종 비교 전까지 Router tuning에 사용하지 않음

Holdout 결과를 보고 Rule/Weight를 수정했다면 해당 결과는 폐기하고 새 Holdout version을 만든다.

---

## 7. Trial Procedure

각 Task는 다음 순서로 실행한다.

### Arm A — Manual Choice

1. 사용자에게 Task와 Resource catalog를 표시
2. 타이머 시작
3. 사용자가 Resource를 선택
4. `selection_time_ms` 기록
5. 선택 Resource로 실행
6. 결과 확인
7. 필요하면 최대 2회 재작업
8. 만족도 입력

### Arm B — Fixed Default

1. 같은 Task 입력
2. 사전에 지정된 Resource로 즉시 실행
3. 필요하면 최대 2회 재작업
4. 만족도 입력

`selection_time_ms = 0`

### Arm C — Intent OS

1. 같은 Task 입력
2. Intent OS가 내부 해석·라우팅
3. 선택한 Resource/Tool 실행
4. 필요하면 최대 2회 재작업
5. 만족도 입력

라우팅 계산 시간은 `router_overhead_ms`와 `execution_latency_ms`에 포함한다.

---

## 8. Metrics

### M1. Result Quality — 0..100

**Primary metric.**

Task별 Rubric을 기반으로 Blind Evaluation한다.

공통 품질 축:

| 축 | 기본 가중치 |
|---|---:|
| Correctness | 35% |
| Completeness | 20% |
| Instruction Following | 20% |
| Usefulness | 15% |
| Presentation / Clarity | 10% |

Task 유형에 따라 `quality_rubric`에서 가중치를 덮어쓸 수 있다.

#### 평가 절차

1. Arm/Resource 식별 정보를 제거
2. 결과 순서를 무작위화
3. 최소 2개의 독립 Judge로 0..100 채점
4. Judge 간 차이가 15점 초과면 Human Review
5. 최종 점수 = 유효 Judge 점수의 평균

정답형 Task는 가능한 경우 deterministic check를 우선한다.

---

### M2. User Selection Time

```text
selection_time_ms =
  Resource catalog를 본 시점
  → 실행을 확정한 시점
```

- Manual Choice: 실제 측정
- Fixed Default: `0`
- Intent OS: 사용자 선택이 없으므로 `0`

단, Intent OS의 계산 시간은 여기서 숨기지 않고 latency에 포함한다.

---

### M3. Total Cost

```text
total_cost_usd =
  model inference
+ router inference
+ tool/API calls
+ retry/fallback executions
```

**평가 Judge 비용은 treatment cost에서 제외**하고 `evaluation_cost_usd`로 별도 기록한다.

이렇게 해야 평가 방법이 비싼지 여부가 시스템 자체 비용을 왜곡하지 않는다.

---

### M4. Total Latency

두 값을 기록한다.

```text
execution_latency_ms
= 사용자가 실행을 확정한 시점 → 첫 최종 결과

time_to_accepted_ms
= Task 시작 → 사용자가 결과를 수락한 시점
```

Intent OS의 Goal parsing, routing, fallback 시간은 모두 포함한다.

보고 시 mean뿐 아니라 **p50/p95**를 같이 사용한다.

---

### M5. Rework Count

첫 답변 이후 사용자가 추가 수정 또는 재실행을 요청한 횟수.

```text
0 = 첫 결과 수락
1 = 한 번 수정 후 수락
2 = 두 번 수정 후 수락 또는 종료
```

자동 내부 retry는 사용자 재작업이 아니므로 `internal_retry_count`에 별도로 기록한다.

---

### M6. User Satisfaction

각 Trial 종료 직후 1~7 Likert로 기록한다.

| 점수 | 의미 |
|---:|---|
| 1 | 전혀 만족하지 않음 |
| 4 | 보통 |
| 7 | 매우 만족 |

질문은 고정한다.

> "이 결과를 실제 목적에 사용한다면 얼마나 만족합니까?"

---

## 9. Derived Metrics

원시 지표를 숨기지 않는다는 전제하에 다음 파생 지표를 사용한다.

### 9.1 First-Pass Acceptance Rate

```text
FPAR = trials with rework_count == 0 / total trials
```

### 9.2 Accepted Task Rate

```text
ATR = accepted trials / total trials
```

### 9.3 Cost per Accepted Task

```text
CPAT = total treatment cost / accepted trials
```

### 9.4 Quality per Dollar

```text
QPD = mean quality / mean cost
```

비용이 0인 로컬/무료 Resource가 있으면 QPD는 비교하지 않고 CPAT를 우선한다.

### 9.5 Quality-Adjusted Latency

```text
QAL = mean quality / p50 latency_seconds
```

보조 지표이며 품질·지연 원시값과 함께만 보고한다.

---

## 10. Success Criteria

Benchmark 시작 전에 아래 기준을 고정한다.

### 10.1 Minimum Viable Routing

Intent OS는 다음을 모두 만족해야 한다.

1. **Manual 대비 품질 비열등**
   - `Quality(Intent OS) - Quality(Manual) >= -3.0`
2. **Fixed Default 대비 품질 우위**
   - `Quality(Intent OS) - Quality(Fixed) >= +5.0`
3. **Manual 대비 선택 부담 제거**
   - median `selection_time_ms` 감소율 ≥ 80%
4. **Manual 대비 비용 폭증 금지**
   - `Cost(Intent OS) <= Cost(Manual) × 1.15`
5. **Manual 대비 지연 폭증 금지**
   - p50 `execution_latency(Intent OS) <= Manual × 1.20`
6. **재작업 악화 금지**
   - `Rework(Intent OS) <= Rework(Manual)`
7. **만족도 악화 금지**
   - `Satisfaction(Intent OS) >= Satisfaction(Manual) - 0.2`

### 10.2 Strong Routing

다음 중 3개 이상이면 Strong으로 분류한다.

- Manual 대비 품질 `+3` 이상
- Fixed 대비 품질 `+8` 이상
- Manual 대비 비용 `10%` 이상 절감
- Manual 대비 재작업 `20%` 이상 감소
- Manual 대비 time-to-accepted `20%` 이상 감소
- Manual 대비 만족도 `+0.5` 이상

---

## 11. Statistics

Task가 동일하므로 **paired comparison**을 사용한다.

권장:

- Arm별 mean / median / p50 / p95
- Task pair별 delta
- bootstrap 95% CI
- Category별 breakdown
- Holdout 결과 별도 보고

v0.1의 30 Task는 제품 출시 수준의 통계적 확증이 아니라 **라우팅 정책의 방향성 검증**을 위한 것이다.

동일 결론이 필요한 경우 Task 수와 사용자 수를 늘린다.

---

## 12. Randomization & Bias Control

다음 편향을 통제한다.

### Order Effect

같은 Task의 Arm 순서를 무작위화한다.

### Model Identity Bias

Quality Judge에는 Provider/Model/Arm 정보를 주지 않는다.

### Router Overfitting

Holdout Task를 Router tuning에 사용하지 않는다.

### Prompt Leakage

Task별 기대 정답, Rubric, Judge comment를 Router에 입력하지 않는다.

### Human Selection Expertise

Manual Arm은 사용자의 모델 지식에 영향을 받으므로 사용자의 self-rated expertise를 기록한다.

```text
novice / intermediate / expert
```

---

## 13. Freshness Tasks

최신 정보가 필요한 Task는 재현성을 위해 다음을 저장한다.

- 실행 UTC timestamp
- 검색 결과 또는 Source snapshot identifier
- 각 Arm이 접근 가능한 동일 Web/Search Tool
- 평가 시점의 사실 기준

Freshness Task는 서로 다른 날짜에 Arm을 실행하면 안 된다. 가능하면 30분 이내에 세 Arm을 모두 실행한다.

---

## 14. Failure Handling

Trial 실패도 데이터다.

다음 상태를 기록한다.

```text
completed
timeout
provider_error
tool_error
policy_block
invalid_output
budget_exceeded
user_abandoned
```

실패 Trial을 결과에서 임의로 삭제하지 않는다.

Provider outage처럼 Arm과 무관한 외부 장애가 명확한 경우에만 `excluded_reason`을 기록하고 재실행한다.

---

## 15. Reproducibility Record

각 Benchmark Run은 최소 다음을 보존한다.

```text
benchmark_id
run_id
started_at
finished_at
resource_pool_snapshot
fixed_default_resource_id
router_version
router_config_hash
case_suite_version
randomization_seed
trial records
judge configuration
evaluation cost
```

Intent OS의 Decision entity가 존재하면 `decision_id`를 Trial에 연결한다.

---

## 16. Report Format

최종 보고서는 최소 다음 표를 포함한다.

| Metric | Manual | Fixed | Intent OS | Δ vs Manual | Δ vs Fixed |
|---|---:|---:|---:|---:|---:|
| Quality | | | | | |
| Selection Time | | | | | |
| Cost | | | | | |
| Latency p50 | | | | | |
| Latency p95 | | | | | |
| Rework | | | | | |
| Satisfaction | | | | | |
| First-Pass Acceptance | | | | | |

그리고 반드시 Category breakdown을 함께 제공한다.

"전체 평균에서 Intent OS 승리"만으로는 어떤 라우팅 규칙이 잘못됐는지 알 수 없다.

---

## 17. Benchmark Decision

결과 판정은 세 단계다.

```text
FAIL
  Minimum Viable Routing 기준 미충족

PASS
  Minimum Viable Routing 기준 충족

STRONG PASS
  Minimum Viable Routing + Strong Routing 조건 3개 이상
```

PASS하지 못해도 Resource 자체가 나쁘다는 뜻은 아니다.

실패 원인을 다음 중 하나로 분해한다.

```text
intent_parsing
task_decomposition
capability_mapping
resource_scoring
resource_selection
tool_selection
fallback
execution
evaluation
```

이 분해가 Intent OS 개선 루프의 입력이 된다.

---

## 18. Recommended First Run

첫 실제 Run은 복잡하게 시작하지 않는다.

### Resource Pool

3개의 AI Resource + Web/Search Tool + Calculator/Utility Tool.

예시:

```text
Resource A — fast / low cost
Resource B — balanced
Resource C — high reasoning quality
Tool W     — web/search
Tool U     — calculator/utility
```

### Execution

```text
30 Tasks
× 3 Arms
× 1 repetition
= 90 Trials
```

### Output

1. `run.json`
2. 블라인드 품질 평가
3. `tools/score-system-benchmark.py run.json`
4. Category별 실패 분석
5. Router rule/weight 수정 여부 결정

---

## 19. Relationship to Intent OS Entities

Benchmark record는 새로운 Core Entity가 아니다.

기존 Entity를 사용한다.

| Benchmark 개념 | Intent OS Entity |
|---|---|
| 사용자 목표 | Goal |
| 작업 | Task |
| 사용 가능한 모델/도구 | Resource / Tool |
| 자동 선택 | Decision |
| API 실행 | Execution |
| 측정 결과 | Outcome |
| 품질 판정 | Evaluation |
| 사용자 수정 요청 | Feedback |
| Context별 성능 축적 | Resource Profile |

Benchmark 전용 Run/Trial JSON은 **실험 데이터 포맷**이지 새로운 도메인 Entity가 아니다.

---

## 20. Completion Criteria

| 항목 | 판정 |
|---|---|
| Manual / Fixed / Intent OS 3-Arm 정의 | ✅ |
| 6개 핵심 측정 지표 정의 | ✅ |
| 비용·지연 포함 범위 정의 | ✅ |
| Blind quality 평가 절차 정의 | ✅ |
| 30-Task suite 구조 정의 | ✅ |
| Development/Holdout 분리 | ✅ |
| Pass/Fail 기준 정의 | ✅ |
| Run JSON Schema | [`schemas/system-benchmark-run.schema.json`](schemas/system-benchmark-run.schema.json) |
| Score calculator | [`../tools/score-system-benchmark.py`](../tools/score-system-benchmark.py) |
| 실행 하네스 (어댑터 · 러너 · 라우터) | ✅ [`harness/`](harness/), [`../tools/run-system-benchmark.py`](../tools/run-system-benchmark.py) |
| 실제 90-Trial 최초 실행 | ❌ §21 참조. 자격 증명과 피험자가 없다 |

---

## 21. 실행 하네스

§7 Trial Procedure를 실행 가능하게 만든 코드가 [`harness/`](harness/)에 있다.

```bash
# 실측
export ANTHROPIC_API_KEY=...
python3 tools/run-system-benchmark.py \
    --pool benchmarks/pools/<pool>.json \
    --operator-expertise intermediate \
    --split development \
    --out runs/<name>.json

python3 tools/score-system-benchmark.py runs/<name>.json
```

| 파일 | 역할 |
|---|---|
| [`harness/adapters.py`](harness/adapters.py) | Resource 실행. `live_api` / `human` / `synthetic` |
| [`harness/router.py`](harness/router.py) | Arm C. 참조 구현의 `RuleRouter`를 그대로 쓴다 |
| [`harness/runner.py`](harness/runner.py) | 세 Arm의 Trial 절차, 사람 측정 수집 |

### 21.1 무엇이 자동이고 무엇이 사람인가

지연·비용·출력은 기계가 잰다. 나머지는 사람에게서만 나온다.

| 측정 | 출처 | 사람 없이 가능한가 |
|---|---|---|
| M3 Cost | provider `usage` × 가격표 | ✅ |
| M4 Latency | 벽시계 | ✅ |
| Arm C 라우팅 | `RuleRouter` | ✅ |
| **Arm A 전체** | §7 "사용자가 Resource를 선택" | ❌ |
| **M2 Selection Time** | §8 "Manual Choice: 실제 측정" | ❌ |
| **M5 Rework** | §8 "사용자가 추가 수정을 요청한 횟수" | ❌ |
| **M6 Satisfaction** | §8 Likert 1~7 | ❌ |
| **M1 Quality** | §8 독립 Judge 2인 + 15점 초과 시 Human Review | ❌ |

§10.1의 두 조건이 `Rework(Intent OS) <= Rework(Manual)`과
`Satisfaction(Intent OS) >= Satisfaction(Manual) - 0.2`이다. **판정에 필요한
값의 절반이 사람에게서만 나온다.** 하네스는 이 값들을 만들어내지 않고 묻는다.
조작자가 없으면(`--no-human`) 비워두고, Manual arm은 임의 선택으로 때우는 대신
`excluded`로 남긴다.

### 21.2 근거와 배관 점검의 구분

합성 실행과 실측은 기록 형태가 완전히 같다. 구분 장치는
`provenance` 하나뿐이며, 다음이 하나라도 참이면 `evidence: false`다.

- 합성 어댑터가 한 번이라도 쓰였다
- 사람 측정(M2·M5·M6·M1 Judge) 중 하나라도 비었다

이 규칙은 세 곳에서 강제된다.

1. **스키마** — `evidence: true`인데 `adapter_kinds`에 `synthetic`이 있으면 검증 실패
2. **러너** — `evidence`를 조작자가 주장하지 못하고 실행 사실에서 유도한다
3. **채점기** — 근거 아닌 실행은 §10 판정을 거부한다 (`--allow-non-evidence` 필요)

자격 증명이 없을 때 조용히 합성으로 대체하지 않는 것도 같은 이유다.
그렇게 하면 실측인 줄 알고 돌린 실행이 합성 데이터를 낳는다.

---

## 22. Next Step

> **자격 증명과 피험자를 확보해 첫 90-Trial Run을 실행한다.**

필요한 것은 셋이다.

1. Resource pool의 API 키 — §4에 따라 실행 전 pool을 고정한다
2. 피험자 — Arm A 30회 선택 + 90 Trial의 재작업·만족도 응답
3. Blind Judge 2인 — §8 M1, 15점 초과 시 Human Review

그 결과부터는 Decision Engine의 threshold와 weight를 추측으로 고치지 않고 실제 benchmark delta를 근거로 조정한다.