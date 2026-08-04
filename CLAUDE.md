# CLAUDE.md

이 저장소에서 작업할 때 참고할 지침.

## 프로젝트 성격

Intent OS 기술 명세서. 코드가 아니라 **문서(Markdown) + JSON Schema** 저장소다.

**1인 프로젝트다.** 리뷰어가 없다.

## 작업 방식

- **작업이 끝나면 확인받지 말고 바로 커밋하고 푸시한다.** "커밋할까요?" 라고 묻지 않는다.
- **PR은 만들지 않는다.** 사용자가 명시적으로 요청할 때만 만든다.
- 커밋 메시지는 한국어로 쓴다. 무엇을 왜 바꿨는지 본문에 정리한다.

## 문서 작성 규칙

- 모든 명세 문서는 **한국어**로 쓴다. 문체는 `~이다 / ~한다`체.
- 새 문서는 기존 문서, 특히 `entities/e001-goal.md`의 구조를 따른다.
  - 헤더 블록: `**Version:**` / `**Status:**` / `**Last Updated:**`
  - 공식 정의는 영문 blockquote + 한국어 번역
  - **"X는 무엇이 아닌가"** 섹션 — 인접 개념과의 구분. 이 명세의 핵심 서술 방식이다.
  - 번호 규칙(`Rule G-001` 형식), Attributes 트리 + 표, Lifecycle, Types,
    Canonical JSON Representation, 알고리즘 흐름도, 다른 Entity와의 관계, Open Issues
- 표, ASCII 트리, ✅/❌ 예시를 적극적으로 쓴다. 설명을 늘어뜨리지 않는다.
- 예시는 기존 문서의 도메인(학원 학생 모집, 윈터캠프, 광고 예산 300만원 등)을 이어서 쓴다.

## 구조

| 경로 | 내용 |
|---|---|
| `v1`~`v7-*.md` | Volume 명세 (Core Concepts ~ Reference Implementation) |
| `entities/` | Entity 명세 001~012 |
| `intent-os-spec/schemas/` | JSON Schema (draft 2020-12) |

주의: 스키마 경로는 `intent-os-spec/schemas/`다. 루트의 `schemas/`가 아니다.

## 핵심 개념 구분

명세 전반에서 이 구분을 지킨다.

| 분류 | 예 |
|---|---|
| **Entity** — 존재하는 것 | Goal, Task, Resource (12개) |
| **Process** — 수행하는 것 | Execution, Learning, Prediction |
| **Runtime State** — 실행 중/후 상태 | Outcome |

가장 중요한 규칙: **Never choose an AI before understanding the Goal.**

## 변경 후 확인

- JSON Schema를 고쳤으면 파싱 검증한다.
  `python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('intent-os-spec/schemas/*.json')]"`
- 문서를 추가했으면 `README.md`와 `entities/README.md`의 목차도 함께 갱신한다.
- 상대 링크가 깨지지 않았는지 확인한다.
