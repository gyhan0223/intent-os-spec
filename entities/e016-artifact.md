# Entity 016: Artifact

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04

---

## 1. Definition

### 공식 정의

> **Artifact is a concrete, addressable output produced by an Execution and preserved independently of the process that created it.**

> Artifact는 하나의 Execution이 만들어낸 **구체적이고 주소를 가진 산출물**이며, 그것을 만든 과정과 독립적으로 보존된다.

여기서 중요한 단어는 **독립적으로 보존(Preserved Independently)** 이다.

Execution 기록이 아카이브되어도, Session이 끝나도, Goal이 완료되어도 **Artifact는 남는다.** 사용자가 결국 손에 쥐는 것은 Artifact뿐이다.

### Intent OS에서 무엇이 Artifact인가

```
PDF · 이미지 · 영상 · 코드 · 보고서 · 표 · 슬라이드 · 광고 카피 · 랜딩페이지 HTML
· 분석 결과 데이터셋 · 상담 스크립트 · 외부 시스템에 생성된 리소스(광고 캠페인)
```

전부 Artifact다. 형식은 다르지만 **"실행이 남긴 것"** 이라는 점에서 동일하게 다룬다.

---

## 2. Artifact는 무엇이 아닌가?

### Artifact는 Outcome이 아니다

❌ `카피 3종 생성, 0.42 USD, 오류 없음` — 이건 [Outcome](e014-outcome.md)이다.

Outcome은 **그릇**, Artifact는 **담긴 것**이다.

```
Outcome out_331               ← 실행의 결과 기록 (측정값)
└── artifacts: ["art_450"]    ← 참조
        └── Artifact art_450  ← 실제 카피 3종 텍스트
```

Artifact 없는 Outcome은 정상이다. **Outcome 없는 Artifact는 존재할 수 없다**([INV-05](e000a-entity-relationships.md)).

### Artifact는 Resource가 아니다

❌ `광고 플랫폼 API` — 이건 [Resource](e007-resource.md)다.

Resource는 **만드는 주체**, Artifact는 **만들어진 것**이다. 단, Artifact가 Resource로 승격되는 경우는 있다 — 생성한 프롬프트 템플릿이나 스크립트가 재사용 가능한 도구가 되면 [Tool](e024-tool.md)로 등록한다. 그때도 **원본 Artifact는 그대로 남는다.**

### Artifact는 Memory나 Knowledge가 아니다

❌ `교육 마케팅에서는 Claude가 강하다` — 이건 [Knowledge](e011-knowledge.md)다.

| | Artifact | Memory / Knowledge |
|---|---|---|
| 대상 | 사용자가 쓰는 결과물 | 시스템이 쓰는 학습 자산 |
| 소비자 | 사람 / 외부 시스템 | Decision Engine |
| 예 | 광고 카피 3종 | "예비 고3 학부모 타겟에는 내신 언급이 효과적" |

### Artifact는 대화의 응답이 아니다

❌ `"네, 카피를 작성했습니다. 첫 번째는…"` — 대화 응답은 [Session](e021-session.md)의 대화 버퍼에 속한다.

Session이 끝나면 대화는 사라져도 된다. Artifact는 사라지면 안 된다. **이 구분이 없으면 결과물이 대화 로그에 묻힌다.**

### Artifact는 반드시 파일이 아니다

❌ `Artifact = 저장소의 파일`

외부 시스템에 생성된 상태도 Artifact다. 광고 플랫폼에 만들어진 캠페인, CRM에 등록된 리드, 발송된 메시지는 파일이 아니지만 **주소를 갖고 추적 가능한 산출물**이므로 Artifact다(`type: external_ref`).

---

## 3. Design Principles

### Rule ART-001 — 모든 Artifact는 정확히 하나의 Outcome에 속한다

출처 없는 산출물은 신뢰할 수 없다. "이 카피 누가 만들었지?"에 답하지 못하면 감사도 재현도 불가능하다.

### Rule ART-002 — Provenance(출처 사슬)를 가진다

Artifact 하나에서 Goal까지 거슬러 올라갈 수 있어야 한다.

```
Artifact art_450
  → Outcome out_331
    → Execution exe_220 (resource: anthropic:claude-5)
      → Decision dec_101
        → Task task_004
          → Intent int_003
            → Goal goal_001
```

이 사슬은 **저장하지 않고 참조로 계산한다.** `outcome_id` 하나만 있으면 나머지는 순회로 얻어진다([Rule REL-002](e000a-entity-relationships.md)).

### Rule ART-003 — 내용은 불변이다

Artifact를 수정하지 않는다. 고쳐야 하면 **새 Artifact를 만들고** `derived_from`으로 원본을 가리킨다.

```
art_450  카피 3종 (Claude 초안)
   ↑ derived_from
art_463  카피 3종 (김 카피라이터 검수본)
```

두 버전이 모두 남아야 "검수가 얼마나 개선했는가"를 측정할 수 있다.

### Rule ART-004 — 내용 주소화(Content-Addressable)

`content_hash`(SHA-256)를 갖는다. 같은 내용이 두 번 생성되면 해시로 즉시 식별된다.

이것이 필요한 이유:

| 용도 | 설명 |
|---|---|
| 중복 검출 | 같은 결과를 두 번 만들었다면 Decision 로직에 낭비가 있다 |
| 무결성 검증 | 저장소에서 내용이 바뀌었는지 확인 |
| 표절·재생성 판별 | Resource가 이전 산출물을 그대로 반복하는지 감지 |

### Rule ART-005 — 자기 자신을 설명해야 한다

`media_type`, `size_bytes`, `encoding`, (구조화 데이터면) `schema_ref`를 갖는다. 무엇인지 모르는 Artifact는 다음 Task의 입력으로 쓸 수 없다.

### Rule ART-006 — 다음 Task의 입력이 될 수 있다

Task Graph에서 선행 Task의 Artifact가 후행 Task의 입력이 된다. 이때 참조는 `artifact_id`로 하며, **내용을 복사해 넘기지 않는다.**

### Rule ART-007 — 보존 정책을 가진다

무한 보존은 비용이다. 모든 Artifact는 `retention` 정책을 갖는다. 다만 **정책은 [Policy](e019-policy.md)가 정하고 Artifact는 참조만 한다.**

### Rule ART-008 — 채택 여부와 존재는 별개다

Collaborative 실행에서 채택되지 않은 결과물도 Artifact로 남는다. `adopted`는 [Evaluation](e015-evaluation.md)이 판정하는 속성이며, 미채택 Artifact도 Resource 성능 분석의 자료다.

---

## 4. Attributes

```
Artifact
├── Identity
│   ├── artifact_id
│   ├── outcome_id
│   └── content_hash
├── Content
│   ├── type
│   ├── media_type
│   ├── location
│   ├── size_bytes
│   ├── encoding
│   └── schema_ref
├── Description
│   ├── name
│   ├── summary
│   └── tags[]
├── Provenance
│   ├── produced_by          (resource_id)
│   ├── derived_from[]
│   └── produced_at
├── Governance
│   ├── retention_policy_id
│   ├── visibility
│   └── contains_pii
└── Status
    └── status
```

| 속성 | 의미 | 예 |
|---|---|---|
| **artifact_id** | 식별자 | `art_450` |
| **outcome_id** | 소속 Outcome | `out_331` |
| **content_hash** | SHA-256 | `sha256:9f2a…` |
| **type** | 분류 (§4.1) | `text` |
| **media_type** | MIME | `text/markdown` |
| **location** | 저장 위치 | `blob://artifacts/art_450` |
| **size_bytes** | 크기 | `1284` |
| **schema_ref** | 구조화 데이터의 스키마 | `null` |
| **name** | 사람이 읽는 이름 | `윈터캠프 인스타 광고 카피 3종` |
| **summary** | 요약 (200자 이내) | `내신 관리 소구 2종, 합격 실적 소구 1종` |
| **tags** | 검색용 태그 | `["카피", "인스타그램", "윈터캠프"]` |
| **produced_by** | 만든 Resource | `anthropic:claude-5` |
| **derived_from** | 파생 원본 | `[]` |
| **produced_at** | 생성 시각 | `2026-08-04T09:30:01.820Z` |
| **retention_policy_id** | 보존 정책 | `pol_retention_default` |
| **visibility** | 공개 범위 | `internal` |
| **contains_pii** | 개인정보 포함 여부 | `false` |
| **status** | 상태 (§6) | `Adopted` |

### 4.1 Artifact Types

```
Artifact
├── text          카피, 스크립트, 요약
├── document      보고서, 제안서 (PDF, DOCX)
├── image         광고 이미지, 썸네일
├── video         홍보 영상
├── audio         상담 녹음, 안내 음성
├── code          자동화 스크립트, 랜딩페이지 HTML
├── data          비교표, 분석 데이터셋
├── structured    JSON/CSV 등 스키마를 갖는 데이터
└── external_ref  외부 시스템에 생성된 상태
```

| Type | 예 | 저장 방식 |
|---|---|---|
| `text` | 광고 카피 3종 | 본문 저장 |
| `document` | 경쟁 학원 분석 리포트 PDF | 블롭 저장 |
| `image` | 인스타그램 광고 소재 | 블롭 저장 |
| `code` | 랜딩페이지 개선 HTML/CSS | 본문 저장 + 버전 관리 |
| `data` | 경쟁 학원 5곳 가격·커리큘럼 비교표 | 구조화 저장 + `schema_ref` |
| `external_ref` | 광고 플랫폼에 생성된 캠페인 `camp_88421` | 참조만 저장 |

**`external_ref`는 특별하다.** 내용을 소유하지 않으므로 `content_hash`가 없을 수 있고, 외부에서 삭제되면 참조가 끊긴다. 이를 위해 `last_verified_at`을 별도로 둔다.

---

## 5. Invariants

### INV-ART-01 — 모든 Artifact는 정확히 하나의 Outcome에 속한다

전역 불변식 [INV-05](e000a-entity-relationships.md)의 Artifact 측 표현이다.

| | |
|---|---|
| **위반 시** | 고아 Artifact를 GC 후보로 표시하되 보존 기간까지 삭제하지 않는다 |

### INV-ART-02 — 내용은 불변이다

`content_hash`가 바뀌면 그것은 다른 Artifact다.

| | |
|---|---|
| **위반 시** | 저장 계층이 덮어쓰기를 거부. 무결성 경보 발행 |
| **탐지** | 조회 시 해시 재계산 (샘플링) |

### INV-ART-03 — derived_from 체인은 순환하지 않는다

| | |
|---|---|
| **위반 시** | 링크 생성 거부. 파생 계보 추적이 무한 루프에 빠진다 |

### INV-ART-04 — contains_pii가 true면 visibility는 public이 될 수 없다

| | |
|---|---|
| **위반 시** | 공개 요청을 차단하고 [Policy](e019-policy.md) 위반 Event를 발행 |

### INV-ART-05 — Session이 끝나도 Artifact는 삭제되지 않는다

[INV-16](e000a-entity-relationships.md)의 Artifact 측 표현이다.

| | |
|---|---|
| **위반 시** | 삭제를 차단한다. 삭제는 오직 보존 정책 만료 또는 명시적 삭제 요청으로만 |

### INV-ART-06 — Purged Artifact의 메타데이터는 남는다

내용을 지워도 `artifact_id`, `content_hash`, `produced_by`, `produced_at`은 보존한다.

| | |
|---|---|
| **위반 시** | Provenance 사슬이 끊어져 과거 Outcome을 설명할 수 없게 된다 |

---

## 6. Lifecycle

```
Produced → Adopted → Published ──▶ Superseded
    │         │                        │
    │         └──▶ Rejected            │
    │                                  ▼
    └──────────────────────────▶ Archived ──▶ Purged
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| **Produced** | 생성됨. 아직 평가 전 | Execution 종료 |
| **Adopted** | 채택됨. 후속 Task의 입력으로 사용 가능 | Evaluation `verdict: accept` |
| **Rejected** | 채택되지 않음. 기록은 유지 | Evaluation `verdict: reject` 또는 미채택 |
| **Published** | 외부로 전달됨 (발송·게시·납품) | 외부 전달 액션 |
| **Superseded** | 개선본으로 대체됨 | 새 Artifact가 `derived_from`으로 참조 |
| **Archived** | 활성 조회 대상에서 제외 | 보존 정책의 활성 기간 경과 |
| **Purged** | 내용 삭제. 메타데이터만 유지 | 보존 기간 만료 또는 삭제 요청 |

### 6.1 Published가 중요한 이유

> **외부로 나간 Artifact는 되돌릴 수 없다.**

광고가 집행되고 메시지가 발송된 뒤에는 `Rejected`로 전이할 수 없다. `Published` 상태의 Artifact를 무효화하려면 **취소 Task를 새로 생성**해야 한다. 이 비대칭성이 [Risk](e018-risk.md) 평가에서 "비가역 작업"을 별도로 다루는 이유다.

---

## 7. Relationships

```
Outcome 014 ──1:0..N──▶ Artifact 016 ──derived_from──▶ Artifact 016
                             │
                             ├──입력──▶ Task 005 (후행 Task)
                             ├──판정──▶ Evaluation 015 (adopted)
                             ├──지배──▶ Policy 019 (보존·공개)
                             └──승격──▶ Tool 024 (재사용 가능해지면)
```

| Entity | 관계 | Cardinality |
|---|---|---|
| [Outcome](e014-outcome.md) | 유일한 소속처 | `Outcome 1:0..N Artifact` |
| [Execution](e013-execution.md) | 생성 주체 (Outcome 경유) | `Execution 1:0..N Artifact` |
| [Resource](e007-resource.md) | `produced_by`. 성능 분석의 표본 | `Resource 1:0..N Artifact` |
| [Task](e005-task.md) | 후행 Task의 입력이 된다 | `Artifact N:M Task` |
| [Evaluation](e015-evaluation.md) | 채택 여부를 판정 | `Artifact 1:0..N Evaluation` |
| [Policy](e019-policy.md) | 보존·공개·PII 정책을 강제 | `Policy 1:N Artifact` |
| [Tool](e024-tool.md) | 재사용 가능한 Artifact는 Tool로 승격 가능 | `Artifact 1:0..1 Tool` |
| [Session](e021-session.md) | Session보다 오래 산다 | `Session 1:0..N Artifact` (참조) |

---

## 8. Canonical Representation

```json
{
  "artifact_id": "art_450",
  "outcome_id": "out_331",
  "content_hash": "sha256:9f2a41c7d3b8e0165a4c2f9b7e18d40c93ab5e6f21d8c0a7b4e3f19d6c852a0b",
  "type": "text",
  "media_type": "text/markdown",
  "location": "blob://artifacts/art_450",
  "size_bytes": 1284,
  "encoding": "utf-8",
  "schema_ref": null,
  "name": "윈터캠프 인스타그램 광고 카피 3종",
  "summary": "내신 관리 소구 2종, 합격 실적 소구 1종. 예비 고3 학부모 타겟",
  "tags": ["카피", "인스타그램", "윈터캠프", "예비고3"],
  "produced_by": "anthropic:claude-5",
  "derived_from": [],
  "produced_at": "2026-08-04T09:30:01.820Z",
  "retention_policy_id": "pol_retention_default",
  "visibility": "internal",
  "contains_pii": false,
  "status": "Adopted"
}
```

외부 시스템 산출물(`external_ref`)은 다음과 같다.

```json
{
  "artifact_id": "art_512",
  "outcome_id": "out_402",
  "content_hash": null,
  "type": "external_ref",
  "media_type": "application/vnd.adplatform.campaign",
  "location": "adplatform://campaigns/camp_88421",
  "name": "윈터캠프 인스타그램 캠페인",
  "summary": "일 예산 8만원, 2026-08-05 ~ 2026-08-19 집행",
  "produced_by": "adplatform:ads_api",
  "produced_at": "2026-08-04T15:02:00Z",
  "last_verified_at": "2026-08-04T15:02:00Z",
  "visibility": "internal",
  "contains_pii": false,
  "status": "Published"
}
```

기계가 읽을 수 있는 스키마: [`artifact.schema.json`](../intent-os-spec/schemas/artifact.schema.json)

---

## 9. Validation Rules

```
Artifact 생성 요청
  ↓
outcome_id 존재 확인 (ART-001) ── 없으면 반려
  ↓
type 확인
  ├── external_ref → location 도달 가능성 검사, content_hash 생략 허용
  └── 그 외        → 내용 존재 확인 + content_hash 계산 (ART-004)
  ↓
media_type / size_bytes 확인 (ART-005) ── 없으면 반려
  ↓
동일 content_hash 존재 확인
  ├── 존재 + 동일 Outcome → 거부 (중복)
  └── 존재 + 다른 Outcome → 허용 + duplicate_of 기록 → 낭비 신호 발행
  ↓
derived_from 순환 검사 (INV-ART-03)
  ↓
PII 스캔 → contains_pii 설정
  ↓
visibility × contains_pii 정합 검사 (INV-ART-04)
  ↓
retention_policy_id 해소 (Policy 조회) ── 없으면 기본 정책 적용
  ↓
Produced 생성 → Event 발행 (artifact.produced)
```

### 9.1 삭제 요청 처리

```
삭제 요청 (사용자 / 보존 만료)
  ↓
status = Published ? ── Yes → 외부 취소 Task 생성 필요 여부 확인
  ↓
후행 Task의 입력으로 사용 중인가 ── Yes → 삭제 보류, 의존 목록 반환
  ↓
내용 삭제 (location 대상)
  ↓
메타데이터 보존 (INV-ART-06)
  ↓
status → Purged, Event 발행 (artifact.purged)
```

---

## 10. Examples

### 예시 1 — 카피 3종

```
art_450  text/markdown  1,284 bytes
         produced_by: anthropic:claude-5
         status: Adopted
```

### 예시 2 — 검수본 (파생)

```
art_450  Claude 초안              quality 0.93
   ↑ derived_from
art_463  김 카피라이터 검수본      quality 0.97
         produced_by: human:copywriter_kim
         outcome_id: out_345      ← 다른 Outcome이다
```

`art_450`은 `Superseded`, `art_463`이 `Adopted`가 된다. **두 개를 비교하면 인간 검수의 순 기여도(+0.04)를 측정할 수 있다.**

### 예시 3 — 구조화 데이터

```json
{
  "artifact_id": "art_302",
  "outcome_id": "out_290",
  "type": "data",
  "media_type": "application/json",
  "schema_ref": "schemas/competitor-comparison.schema.json",
  "name": "홍대 경쟁 학원 5곳 비교표",
  "summary": "가격·커리큘럼·강사 수·후기 평점",
  "produced_by": "perplexity:sonar",
  "produced_at": "2026-08-03T16:40:00Z",
  "status": "Adopted"
}
```

`schema_ref`가 있으므로 후행 Task(`분석 리포트 작성`)가 이 데이터를 **파싱 없이 그대로 입력으로 받을 수 있다.**

### 예시 4 — Artifact 사슬 (Task Graph 전체)

```
T1 시장 조사    → art_301  시장 규모 데이터
T2 경쟁 분석    → art_302  경쟁 학원 비교표      (art_301 입력)
T3 타겟 분석    → art_303  페르소나 정의
T4 카피 작성    → art_450  카피 3종             (art_302, art_303 입력)
T5 랜딩 개선    → art_470  랜딩페이지 HTML       (art_450 입력)
T6 광고 집행    → art_512  캠페인 (external_ref) (art_450, art_470 입력)
```

`art_512`(집행된 캠페인)에서 역으로 거슬러 올라가면 **어떤 조사가 어떤 카피를 낳고 어떤 광고가 되었는지** 전부 추적된다.

---

## 11. Edge Cases

| 상황 | 판정 |
|---|---|
| **같은 내용이 두 Execution에서 생성** | 둘 다 Artifact로 남긴다(Outcome이 다르므로). `duplicate_of`를 기록하고 "동일 결과를 두 번 만들었다"는 낭비 신호를 발행한다 |
| **Artifact가 너무 커서 저장 불가** | 참조(`external_ref`)로 전환하고 `content_hash`만 계산해 보관. 원본 위치의 가용성은 시스템 책임 밖임을 명시 |
| **외부 참조 대상이 삭제됨** | Artifact를 지우지 않는다. `last_verified_at`과 `status: Archived`로 표시. 과거에 존재했다는 사실이 감사 대상이다 |
| **스트리밍 결과의 부분 저장** | 완결되어야 Artifact다. 중단된 스트림은 Artifact를 만들지 않고 Outcome의 `partial_reason`에 기록한다 |
| **PII가 포함된 산출물** | `contains_pii: true`. `visibility: public` 금지(INV-ART-04). 보존 기간이 별도 정책으로 짧아진다 |
| **미채택 Artifact** | `Rejected`로 남긴다. 삭제하지 않는다. 왜 채택되지 않았는지가 Resource 성능 데이터다 |
| **사용자가 Artifact를 직접 수정** | 시스템은 원본을 수정하지 않는다. 사용자 수정본을 **새 Artifact**로 등록하고 `derived_from`으로 연결한다. 이 차이가 [Feedback](e012-feedback.md)의 Implicit 신호가 된다 |
| **Artifact가 다음 Task의 입력인데 Purged됨** | 삭제 시 의존성 검사(§9.1)로 차단된다. 이미 삭제되었다면 해당 Task는 `input_insufficient`로 실패한다 |
| **Published된 광고를 내려야 함** | 상태 되돌리기가 아니라 **취소 Task**를 새로 만든다. 그 Task의 Artifact가 "캠페인 중단 기록"이 된다 |

---

## 12. Open Issues (v1.0)

### 대용량 Artifact의 저장 전략

영상·대용량 데이터셋은 `content_hash` 계산 자체가 비싸다. 청크 단위 해시(Merkle) 도입 여부와 임계 크기가 미정이다.

### 버전 vs 파생의 경계

`derived_from`은 "검수본"과 "완전히 다른 파생물"을 구분하지 못한다. `derivation_type`(revision / transformation / composition) 같은 분류가 필요하다.

### 외부 참조의 신뢰성

`external_ref`는 시스템이 소유하지 않는 상태를 가리킨다. 외부 시스템이 조용히 변경되었을 때의 감지 주기와 `last_verified_at` 갱신 정책이 없다.

### 삭제 요구와 통계 보존

사용자가 Artifact 삭제를 요구하면 내용은 지우되([INV-ART-06](e000a-entity-relationships.md)) 그 Artifact가 만든 Resource 성능 통계는 어떻게 되는가. 익명화 후 유지와 통계 재계산 중 선택이 필요하다.

### 앞으로 보강해야 할 항목

- Artifact 저장소의 추상 인터페이스 (Volume 6와 연동)
- `type`별 필수 메타데이터 표준
- Artifact 검색·질의 인터페이스 (tags·summary 기반)
- 실제 예시 30~50개
