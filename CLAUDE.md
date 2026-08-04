# CLAUDE.md

이 저장소에서 작업할 때 참고할 지침.

## 프로젝트 성격

Intent OS 기술 명세서. 코드가 아니라 **문서(Markdown) + JSON Schema** 저장소다.

**1인 프로젝트다.** 리뷰어가 없다.

## 작업 방식

- **작업이 끝나면 확인받지 말고 바로 커밋하고 푸시한다.** "커밋할까요?" 라고 묻지 않는다.
- **`main`에 직접 푸시한다.** 작업용 브랜치를 따로 만들 필요 없다.
- **PR은 만들지 않는다.** 사용자가 명시적으로 요청할 때만 만든다.
- 커밋 메시지는 한국어로 쓴다. 무엇을 왜 바꿨는지 본문에 정리한다.

## 문서 작성 규칙

- 모든 명세 문서는 **한국어**로 쓴다. 문체는 `~이다 / ~한다`체.
- **Entity 명세는 `entities/e000-spec-format.md`의 12개 필수 섹션을 강제한다.** 새 Entity 문서를 쓰기 전에 반드시 읽는다.

  ```
  1 Definition          5 Invariants      9  Validation Rules
  2 What it is NOT      6 Lifecycle       10 Examples
  3 Design Principles   7 Relationships   11 Edge Cases
  4 Attributes          8 Canonical Rep.  12 Open Issues
  ```

  - 섹션 번호는 **고정**이다. 추가 내용(Types, 알고리즘 등)은 가장 가까운 필수 섹션의 하위 절로 넣는다.
  - 헤더 블록: `**Version:**` / `**Status:**` / `**Last Updated:**`
  - 공식 정의는 영문 blockquote + 한국어 번역
  - **"X는 무엇이 아닌가"** — 인접 개념 3개 이상, 각각 ❌ 반례. 이 명세의 핵심 서술 방식이다.
  - `Rule <PREFIX>-<NNN>` / `INV-<PREFIX>-<NN>` 번호 규칙. Prefix는 e000 §3 표에 등록한다. **다른 Entity의 번호를 인용할 때는 출처를 밝힌다** — 링크(`[Rule REL-004](e000a-...)`)나 문서 id 표기(`e015 Rule EVA-004`).
  - **부속 문서(Annex)는 12개 섹션을 면제받되 헤더에 `**Format:** Annex`를 선언한다** (e000 §7.1). 선언 없는 미준수는 검증 실패다.
  - §7 Relationships에는 반드시 **Cardinality**(`1:N`, `N:M` 등)를 표기한다.
  - §5 Invariants의 각 항목에는 **위반 시 시스템 반응**을 함께 쓴다.
- **Volume 문서의 Completion Criteria는 근거 절을 함께 적는다.** 체크박스 나열은 쓰지 않는다.

  | 항목 | 근거 | 판정 |
  |---|---|---|
  | ... | §N | ✅ / ⚠️ 부분 / ❌ |

  근거 없는 ✅는 인정하지 않는다. 미충족 항목을 체크로 덮지 말고 **⚠️/❌로 남기고 무엇이 빠졌는지 적는다.**
- **기호는 뜻이 하나다** (e000 §9.1). `🔬`는 연구 단계(지금 채울 수 없는 것), `⚠️`는 부분 충족(채워야 하는데 안 채운 것), `📌`는 명세 정정. 겹쳐 쓰지 않는다.
- **같은 수치가 두 문서에 나오면 한쪽을 정본으로 정하고 다른 쪽은 참조만 한다.** 임계값·가중치를 양쪽에 복제하면 반드시 갈린다.
- **Rule과 Invariant를 섞지 않는다.** Rule은 "이렇게 만들어라"(생성 시 1회 검사), Invariant는 "이 상태가 되면 안 된다"(항상 검사).
- 표, ASCII 트리, ✅/❌ 예시를 적극적으로 쓴다. 설명을 늘어뜨리지 않는다.
- 예시는 고정 도메인(학원 학생 모집, 윈터캠프, 광고 예산 300만원, 김 카피라이터 등)을 이어서 쓴다. 새 도메인을 만들지 않는다.

## 구조

| 경로 | 내용 |
|---|---|
| `v1`~`v7-*.md` | Volume 명세 (Core Concepts ~ Reference Implementation) |
| `entities/e000*` | 메타 명세 — 명세 형식, Entity 관계와 전역 불변식 |
| `entities/e001`~`e025` | Entity 명세 001~025 |
| `intent-os-spec/schemas/` | JSON Schema (draft 2020-12) |
| `tools/` | 명세 검증 스크립트 3개 |
| `.github/workflows/` | push마다 검증 실행 |

주의: 스키마 경로는 `intent-os-spec/schemas/`다. 루트의 `schemas/`가 아니다.

## 핵심 개념 구분

명세 전반에서 이 구분을 지킨다. 판별 기준은 **"1년 뒤에 조회해야 하는가"** 이다.

| 분류 | 의미 | 예 |
|---|---|---|
| **Entity** — 존재하는 것 | 식별자를 갖고 저장·조회된다 (25개) | Goal, Task, Resource, Execution, Outcome |
| **Process** — 수행하는 것 | 동사. 저장하지 않는다 | Planning, Deciding, Executing, Learning, Prediction |
| **Runtime State** — 순간값 | Entity의 필드로 존재한다 | `Execution.status`, `Goal.progress` |

> **v2.0 정정:** v1.0에서 Execution을 Process, Outcome을 Runtime State로 분류했으나 정정했다.
> "실행 중"은 Process지만 `task_struct`는 Entity인 것과 같다. 둘 다 영속 조회 대상이므로 **Entity**다.

가장 중요한 규칙: **Never choose an AI before understanding the Goal.**

Entity 간 관계와 전역 불변식 16개는 `entities/e000a-entity-relationships.md`가 단일 권위다. **Entity 문서 안에서 Entity 간 불변식을 새로 만들지 않는다. 참조만 한다.**

## 변경 후 확인

**세 스크립트를 돌린다. 전부 통과해야 커밋한다.** GitHub Actions가 push마다 같은 것을 실행한다.

```bash
python3 tools/validate-format.py     # 형식: 섹션 순서, Rule 4개·INV 3개, Prefix 등록,
                                     #       헤더 3필드, 스키마 위생, 상호 참조(§N)
python3 tools/validate-examples.py   # 문서의 JSON 예시 ↔ 스키마
python3 tools/validate-links.py      # 상대 링크
```

- 새 Entity를 추가했으면 `validate-examples.py`의 `DOC_TO_SCHEMA`에도 항목을 추가한다.
- **스키마는 모든 객체에 `additionalProperties: false`, 모든 property에 `description`이 있어야 한다.** `validate-format.py`가 강제한다.
  단 `contains` / `if` / `anyOf` 같은 **술어** 자리는 닫지 않는다. 닫으면 "이 항목이 하나 있는가"를 묻던 조건이 "이것 말고 아무것도 없는가"로 바뀐다.
- **섹션을 옮겼으면 다른 문서의 `[e007 §6]` 참조가 깨진다.** `validate-format.py`가 잡아준다.
- **Volume 문서(`v*.md`)의 JSON 블록에는 반드시 마커를 붙인다.** 마커 없는 블록은 검증 실패로 잡힌다.

  ```
  <!-- validate: goal.schema.json -->   ← 해당 스키마로 검증
  <!-- validate: none -->               ← 스키마에 매이지 않는 개념 예시
  ```

  Volume 문서는 여러 Entity의 예시를 섞어 쓰므로 문서 단위 매핑이 불가능하다. `none`을 쓸 때는 **왜 스키마 밖인지 본문에 밝힌다.**
- 문서를 추가했으면 `README.md`와 `entities/README.md`의 목차도 함께 갱신한다.
- 상대 링크가 깨지지 않았는지 확인한다.
- Entity를 추가했으면 `entities/e000a-entity-relationships.md`의 **§3 Cardinality 전체표와 §2 Entity 지도**도 갱신한다. 빠뜨리면 관계 모델에 구멍이 생긴다.
- Rule Prefix를 새로 썼으면 `entities/e000-spec-format.md` §3 표에 등록한다.
