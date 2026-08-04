# Entity 000: Specification Format

- **Version:** v1.0 Draft
- **Status:** Meta Specification
- **Last Updated:** 2026-08-04

---

## 0. 이 문서는 무엇인가

Entity 명세를 **어떻게 쓸 것인가**를 정의하는 메타 명세다.

Entity가 27개로 늘어나면 개별 문서의 품질보다 **문서 간 형식의 일관성**이 더 큰 문제가 된다. 형식이 흔들리면 구현자가 문서마다 다른 방식으로 읽게 되고, 결국 해석의 여지가 생긴다.

목표는 하나다.

> **개발자 여러 명이 각자 구현해도 같은 결과를 만드는 명세서**

이를 위해 모든 Entity 명세는 아래 형식을 **강제**한다.

---

## 1. 필수 섹션 (12개)

RFC 수준 명세의 핵심 10개 섹션에, 이 저장소의 관례 2개(Attributes / Open Issues)를 더한 12개다.

| § | 섹션 | 필수 | 무엇을 답하는가 |
|---|---|---|---|
| 1 | **Definition** | ✅ | 이것은 무엇인가 |
| 2 | **What it is NOT** | ✅ | 인접 개념과 어떻게 구분되는가 |
| 3 | **Design Principles** | ✅ | 어떤 규칙을 만족해야 하는가 |
| 4 | **Attributes** | ✅ | 어떤 필드를 가지는가 |
| 5 | **Invariants** | ✅ | 절대 깨지면 안 되는 것은 무엇인가 |
| 6 | **Lifecycle** | ✅ | 어떤 상태를 거치는가 |
| 7 | **Relationships** | ✅ | 다른 Entity와 어떻게 연결되는가 |
| 8 | **Canonical Representation** | ✅ | 기계가 읽는 형태는 무엇인가 |
| 9 | **Validation Rules** | ✅ | 생성 시 무엇을 검사하는가 |
| 10 | **Examples** | ✅ | 실제로 어떻게 생기는가 |
| 11 | **Edge Cases** | ✅ | 무엇이 애매한가, 그때 어떻게 하는가 |
| 12 | **Open Issues** | ✅ | 아직 정하지 못한 것은 무엇인가 |

**§1~§12의 번호는 고정이다.** Entity마다 섹션 번호가 달라지면 문서 간 상호 참조(`e013 §5`)가 성립하지 않기 때문이다.

§13 이상을 만들지 않는다. §0도 만들지 않는다. **"왜 이 Entity가 따로 필요한가"를 먼저 말해야 하는 문서는 §1 앞에 번호 없는 도입부를 하나 둔다.**

```markdown
## Why Not Just a List        ← 번호 없음. 도입부는 1개까지
## 1. Definition
```

**Types**, **Algorithm**, **Metrics**, **Taxonomy** 처럼 Entity 성격에 따라 필요한 내용은 새 섹션을 만들지 않고 **가장 가까운 필수 섹션의 하위 절**로 넣는다.

| 추가 내용 | 들어갈 위치 |
|---|---|
| Types / 분류 | §4 Attributes 의 하위 절 |
| 상태 전이표 / 전이 조건 | §6 Lifecycle 의 하위 절 |
| 계산식 / 알고리즘 | §9 Validation Rules 의 하위 절 |
| 측정 지표 | §5 Invariants 또는 §9 의 하위 절 |

### 섹션별 최소 요건

| § | 최소 요건 |
|---|---|
| 1 | 영문 blockquote 공식 정의 + 한국어 번역 + 핵심 단어 1개 해설 |
| 2 | 인접 개념 3개 이상. 각각 ❌ 반례 + 올바른 분류 |
| 3 | 번호 규칙(`Rule XX-001`) 4개 이상 |
| 4 | ASCII 트리 + 속성표(속성 / 의미 / 예) |
| 5 | 번호 규칙(`INV-XX-01`) 3개 이상. **위반 시 시스템 반응**을 함께 기술 |
| 6 | 상태 다이어그램 + 상태표(상태 / 의미 / 진입 조건) |
| 7 | ASCII 관계도 + 관계표 + **Cardinality** 명시 |
| 8 | 완결된 JSON 예시 + `intent-os-spec/schemas/` 스키마 링크 |
| 9 | 검증 파이프라인 흐름도 + 실패 시 조치 |
| 10 | 도메인 예시 2개 이상 (§13 도메인 규칙) |
| 11 | 애매한 상황 3개 이상 + 판정 규칙 |
| 12 | 미해결 항목 + "앞으로 보강해야 할 항목" 목록 |

---

## 2. 헤더 블록

모든 문서는 제목 다음 줄에 아래 3개 필드를 둔다.

```markdown
# Entity 0NN: <Name>

- **Version:** v1.0 Draft
- **Status:** Core Entity
- **Last Updated:** 2026-08-04
```

| 필드 | 허용값 |
|---|---|
| **Version** | `v<major>.<minor> Draft` / `v<major>.<minor> Stable` |
| **Status** | `Core Entity` / `Core Architecture` / `Meta Specification` / `Supporting Entity` |
| **Last Updated** | `YYYY-MM-DD` |

---

## 3. 번호 규칙

### Rule 번호

`Rule <PREFIX>-<NNN>` 형식. Prefix는 Entity마다 고유하며 재사용하지 않는다.

| Entity | Prefix | Entity | Prefix |
|---|---|---|---|
| 001 Goal | `G` | 015 Evaluation | `EVA` |
| 002 Intent | `I` | 016 Artifact | `ART` |
| 003 Context | `C` | 017 Assumption | `ASM` |
| 004 Constraint | `CN` | 018 Risk | `RSK` |
| 005 Task | `T` | 019 Policy | `POL` |
| 006 Capability | `CP` | 020 Event | `EVT` |
| 007 Resource | `R` | 021 Session | `SES` |
| 008 Plan | `P` | 022 Workflow | `WFL` |
| 009 Decision | `D` | 023 Agent | `AGT` |
| 010 Memory | `M` | 024 Tool | `TOL` |
| 011 Knowledge | `K` | 025 Resource Profile | `RPF` |
| 012 Feedback | `F` | 005-A Task Graph | `TG` |
| 013 Execution | `EXE` | 006-A Capability Taxonomy | `CT` |
| 014 Outcome | `OUT` | 000-A Entity Relationships | `REL` |

**Prefix는 영구 예약이다.** Entity가 폐기되어도 Prefix는 재사용하지 않는다. 옛 문서를 참조하는 링크가 다른 의미로 해석되면 안 되기 때문이다.

### Invariant 번호

- **Entity 내부 불변식:** `INV-<PREFIX>-<NN>` (예: `INV-EXE-01`)
- **Entity 간 불변식:** `INV-<NN>` — [e000a-entity-relationships.md](e000a-entity-relationships.md)에서만 정의한다

Entity 문서 안에서 Entity 간 불변식을 새로 만들지 않는다. 참조만 한다.

---

## 4. Rule과 Invariant의 차이

이 둘을 섞어 쓰면 명세가 무너진다.

| | Rule | Invariant |
|---|---|---|
| 검사 시점 | **생성/변경 시점** (1회) | **항상** (모든 시점) |
| 위반의 의미 | 입력이 잘못됨 → 반려 | 시스템이 잘못됨 → 버그 |
| 예 | `Rule EXE-002 — Execution은 Decision을 참조해야 한다` | `INV-EXE-02 — 종료된 Execution은 정확히 하나의 Outcome을 가진다` |
| 조치 | Validation 파이프라인이 거부 | Runtime이 오류를 보고하고 안전 상태로 전이 |

간단한 판별법:

> Rule은 **"이렇게 만들어라"**, Invariant는 **"이 상태가 되면 안 된다"**.

---

## 5. Cardinality 표기

§7 Relationships에는 반드시 관계의 수(Cardinality)를 표기한다.

| 표기 | 의미 |
|---|---|
| `1:1` | 정확히 하나 |
| `1:0..1` | 없거나 하나 |
| `1:N` | 하나 이상 |
| `1:0..N` | 없거나 여럿 |
| `N:M` | 다대다 |

"Task는 Resource를 가진다" 같은 서술은 금지한다. **"Task 1:0..N Execution"** 처럼 쓴다.

---

## 6. 준수 등급(Conformance Level)

문서마다 완성도가 다르다. 이를 숨기지 않고 명시한다.

| Level | 조건 |
|---|---|
| **L0 — Sketch** | §1, §2만 존재 |
| **L1 — Draft** | §1~§9 존재. 스키마 없음 |
| **L2 — Specified** | 12개 섹션 전부 + JSON Schema 존재 |
| **L3 — Verified** | L2 + 검증기 구현 + 예시 30개 이상 |

목표는 **모든 Core Entity를 L2로 올린 뒤 L3로 진행**하는 것이다. 준수 현황은 [entities/README.md](README.md) §6에서 관리한다.

---

## 7. 문서 분할 기준

한 Entity의 명세가 커지면 Entity 001(Goal)처럼 분할한다.

분할 조건: **아래 중 2개 이상 해당**

| 조건 | 예 |
|---|---|
| 문서가 20KB를 넘는다 | e001-goal.md v2 |
| 그래프 구조를 별도로 다뤄야 한다 | e001a-goal-graph, e005a-task-graph |
| 상태 머신이 8개 상태를 넘는다 | e001c-goal-state-machine |
| 스키마 필드가 25개를 넘는다 | e001b-goal-schema |
| 검증 규칙이 독립된 파이프라인을 이룬다 | e001d-goal-validation |

분할 후 파일명은 `eNNN<a-z>-<subject>.md`, 원본 문서는 **정의와 목차만 남기고** 나머지를 하위 문서로 이관한다.

### 7.1 부속 문서(Annex)의 형식 예외

분할로 갈라져 나온 문서에는 두 갈래가 있다.

| 갈래 | 성격 | 형식 |
|---|---|---|
| **독립 Entity** | 자기 식별자를 갖고 저장·조회된다 | 12개 섹션 **전부 준수**. Prefix를 §3에 등록한다 |
| **부속 문서(Annex)** | 상위 Entity의 한 측면을 펼쳐 쓴 것. 자기 식별자가 없다 | 12개 섹션 **면제** |

Task Graph(005-A)와 Capability Taxonomy(006-A)는 독립 Entity다. 각각 `graph_id`, `taxonomy_id`를 갖는다.
Goal의 하위 문서 4개(001-A~001-D)는 Annex다. `goal_id` 말고 자기 식별자가 없다.

**Annex는 헤더에 이를 선언한다.** 선언 없이 형식을 벗어난 문서는 검증에서 실패로 잡힌다.

```markdown
- **Version:** v2.0 Draft
- **Status:** Core Entity
- **Format:** Annex — e001 Goal의 부속 문서 (e000 §7.1)
- **Last Updated:** 2026-08-04
- **Schema:** [`goal.schema.json`](../intent-os-spec/schemas/goal.schema.json)
```

면제되는 것은 **섹션 번호 규격뿐이다.** 헤더 블록과 스키마 링크는 Annex도 지킨다. Annex가 Rule/Invariant를 정의할 때는 상위 Entity의 Prefix를 쓴다 — `Rule G-012`이지 `Rule GG-001`이 아니다.

---

## 8. 스키마 연결 규칙

- 스키마 경로는 **`intent-os-spec/schemas/`** 다. 루트의 `schemas/`가 아니다.
- 파일명은 `<entity-name>.schema.json` (kebab-case).
- 모든 스키마는 draft 2020-12를 쓴다.
- §8 Canonical Representation의 JSON 예시는 **해당 스키마를 실제로 통과해야 한다.**
- 스키마의 `title`은 Entity 이름, `description`은 한국어 한 줄 정의를 담는다.

---

## 9. 문체 규칙

| 항목 | 규칙 |
|---|---|
| 언어 | 한국어. 문체는 `~이다 / ~한다`체 |
| 공식 정의 | 영문 blockquote + 한국어 번역 |
| 설명 길이 | 표·트리·예시로 대체 가능하면 문장을 쓰지 않는다 |
| 예시 표기 | ✅ 올바른 예 / ❌ 잘못된 예 |
| 강조 | **굵게**는 문단당 2회 이하 |
| 링크 | 다른 Entity 최초 언급 시 상대 링크를 건다 |

### 9.1 기호의 의미 (겹쳐 쓰지 않는다)

기호 하나가 여러 뜻을 겸하면 독자가 "이건 아직 안 된 것인가, 원래 그런 것인가"를 구분하지 못한다. 각 기호는 뜻이 하나다.

| 기호 | 의미 | 쓰는 곳 |
|---|---|---|
| ✅ | 충족 / 올바른 예 | Completion Criteria 판정, 예시 |
| ⚠️ | **부분 충족 · 조건부 · 애매** | Completion Criteria 판정, 삼치 판정 예시, §2의 혼동 주의 |
| ❌ | 미충족 / 잘못된 예 | Completion Criteria 판정, §2 반례 |
| 🔬 | **연구 단계** — 검증되지 않은 설계 가설이다. 완성도가 아니라 **성격**의 표시다 | 문서 헤더, Volume 목록 |
| 📌 | **명세 정정** — 이전 버전의 서술을 뒤집는다 | 정정 blockquote |

🔬와 ⚠️의 차이가 핵심이다. **🔬는 "지금 채울 수 없는 것"**(데이터가 없어 검증 불가), **⚠️는 "채워야 하는데 안 채운 것"**이다. 4-E·4-F 전체는 🔬이고, 그 안의 개별 미정의 항목은 ⚠️다.

---

## 10. 예시 도메인 (고정)

명세 전반이 하나의 사례를 공유한다. 새 도메인을 만들지 않는다.

```
학원(홍대 소재) — 윈터캠프 학생 100명 모집
├── 예산        광고비 300만원
├── 기한        2026-12-31
├── 타겟        예비 고3 학부모
├── 채널        인스타그램 / 검색 광고 / 랜딩페이지 / 상담
└── Resource   Claude / GPT / Gemini / 김 카피라이터 / 광고 플랫폼 API
```

이 도메인 하나로 27개 Entity를 전부 설명할 수 있어야 한다. **설명되지 않는 Entity는 정의가 잘못된 것이다.**

---

## 11. 명세 작성 체크리스트

새 Entity 문서를 커밋하기 전에 확인한다.

```
[ ] 12개 필수 섹션이 모두 있는가
[ ] §2에 인접 개념 3개 이상, 각각 ❌ 반례가 있는가
[ ] Rule Prefix가 §3 표에 등록되어 있는가
[ ] §5의 각 Invariant에 "위반 시 시스템 반응"이 있는가
[ ] §7에 Cardinality가 표기되어 있는가
[ ] §8의 JSON 예시가 실제 스키마를 통과하는가   → python3 tools/validate-examples.py
[ ] 예시가 §10 고정 도메인을 쓰는가
[ ] e000a §3 Cardinality 전체표에 행을 추가했는가
[ ] entities/README.md 목차와 §6 준수 현황표를 갱신했는가
[ ] 루트 README.md 목차를 갱신했는가
[ ] 상대 링크가 깨지지 않았는가
```

`tools/validate-examples.py`는 §8 예시뿐 아니라 문서 전체의 JSON 블록을 검사한다. 새 Entity를 추가하면 그 스크립트의 `DOC_TO_SCHEMA`에도 항목을 추가한다.

---

## 12. Open Issues (v1.0)

### 기존 Entity 001~012의 형식 소급 적용

Entity 001~012는 이 형식이 정해지기 전에 작성되었다. 대부분 §5 Invariants와 §11 Edge Cases가 없다. 소급 적용 계획은 [entities/README.md](README.md) §6의 준수 현황표에서 관리한다.

### 형식 검증의 자동화

체크리스트(§11)는 현재 수동이다. Markdown 구조를 파싱해 필수 섹션 존재 여부를 검사하는 린터가 필요하다. → [Volume 7](../v7-reference-implementation.md)

### 앞으로 보강해야 할 항목

- 섹션별 최대 길이 가이드 (문서 비대화 방지)
- 다국어 버전(영문) 생성 규칙
- Entity 폐기(Deprecation) 절차와 표기
