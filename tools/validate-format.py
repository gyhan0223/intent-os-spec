#!/usr/bin/env python3
"""명세 문서와 스키마가 e000-spec-format.md의 형식 규격을 지키는지 검사한다.

`validate-examples.py`가 "예시가 스키마를 통과하는가"를 본다면, 이 스크립트는
**"문서와 스키마 자체가 규격대로 생겼는가"**를 본다. e000 §11 체크리스트를
기계가 대신 도는 것이다.

검사 항목
---------

A. Entity 문서 (`entities/`)
   A1. 헤더 3필드 (`Version` / `Status` / `Last Updated`)와 허용값
   A2. 12개 필수 섹션이 **번호 순서대로** 존재 (e000 §1)
   A3. `Rule <PREFIX>-<NNN>` 4개 이상 (e000 §1 최소 요건 §3)
   A4. `INV-<PREFIX>-<NN>` 3개 이상 (e000 §1 최소 요건 §5)
   A5. Rule/INV의 Prefix가 e000 §3 표에 등록된 것과 일치
   A6. §8 Canonical Representation의 스키마 링크가 실재하는 파일을 가리킴
   A7. Entity 간 불변식(`INV-<NN>`)을 새로 정의하지 않음 (e000 §3)
   A8. `[e007 §6]` 형태의 상호 참조가 실재하는 섹션을 가리킴
   A9. §7의 Cardinality 표기가 e000a §3 전체표와 일치 — 같은 수치를 두 곳에
       적으면 반드시 갈리므로, 표를 정본으로 두고 파생을 검사한다

   Prefix 표는 e000 §3에서 **직접 파싱한다.** 표를 고치면 검사도 따라 바뀐다.

B. JSON Schema (`intent-os-spec/schemas/`)
   B1. `$schema`가 draft 2020-12
   B2. `title` / `description` 존재 (e000 §8)
   B3. `properties`를 가진 모든 객체에 `additionalProperties: false`
       — 없으면 `titel` 같은 오타가 "추가 필드"로 통과한다
   B4. 모든 property에 `description`

C. 문서 예외
   부속 문서(Annex)는 A2를 면제받되 헤더에 `- **Format:** Annex`를 선언해야
   한다 (e000 §7.1). 선언 없는 미준수는 실패다.

사용법:
    python3 tools/validate-format.py
    python3 tools/validate-format.py --only docs
    python3 tools/validate-format.py --only schemas
"""

# tools/validate-all.py 가 읽는 CI 선언.
CI_LABEL = "형식 검증 (섹션 · 번호 · 스키마 위생)"

import glob
import json
import os
import re
import sys

SCHEMA_DIR = "intent-os-spec/schemas"
ENTITY_DIR = "entities"
SPEC_FORMAT_DOC = "entities/e000-spec-format.md"
RELATIONSHIPS_DOC = "entities/e000a-entity-relationships.md"

# 12개 필수 섹션. 값은 제목에 반드시 들어가야 하는 표현이며,
# 하나라도 맞으면 통과한다 (§2는 한국어로 쓰므로 대안을 둔다).
REQUIRED_SECTIONS = [
    (1, ["Definition"]),
    (2, ["무엇이 아닌가", "What it is NOT"]),
    (3, ["Design Principles"]),
    (4, ["Attributes"]),
    (5, ["Invariants"]),
    (6, ["Lifecycle"]),
    (7, ["Relationships"]),
    (8, ["Canonical Representation"]),
    (9, ["Validation Rules"]),
    (10, ["Examples"]),
    (11, ["Edge Cases"]),
    (12, ["Open Issues"]),
]

MIN_RULES = 4
MIN_INVARIANTS = 3

# 12개 섹션 규격에서 면제되는 문서.
# - Meta: 규격을 정의하는 문서 자신 (e000, e000a)
# - Annex: e000 §7 분할 규칙으로 갈라져 나온 부속 문서
META_DOCS = {"e000-spec-format.md", "e000a-entity-relationships.md", "README.md"}

HEADER_STATUS_ALLOWED = {
    "Core Entity",
    "Core Architecture",
    "Meta Specification",
    "Supporting Entity",
}

RE_HEADING = re.compile(r"^##\s+(\d+)\.\s+(.+?)\s*$", re.M)
RE_HEADER_FIELD = re.compile(r"^-\s+\*\*(\w[\w ]*):\*\*\s*(.+?)\s*$", re.M)
RE_VERSION = re.compile(r"^v\d+\.\d+\s+(Draft|Stable)$")
RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_RULE = re.compile(r"Rule\s+([A-Z]{1,4})-(\d{3})\b")
RE_INV_ENTITY = re.compile(r"\bINV-([A-Z]{1,4})-(\d{2})\b")
RE_INV_GLOBAL = re.compile(r"\bINV-(\d{2})\b")
RE_SCHEMA_LINK = re.compile(r"intent-os-spec/schemas/([\w.\-]+\.json)")
# e000 §3 Prefix 표: | 001 Goal | `G` | 015 Evaluation | `EVA` |
RE_PREFIX_ROW = re.compile(r"(\d{3}(?:-[A-Z])?)\s+[^|]*?\|\s*`([A-Z]{1,4})`")
# 파일명 e005a-task-graph.md → 005-A
RE_DOC_ID = re.compile(r"^e(\d{3})([a-z])?-")
# 코드 블록 안에서 쓰는 출처 표기: `e015 Rule EVA-004` / `e022 INV-WFL-03`
RE_DOC_CITE = re.compile(r"\be\d{3}[a-z]?\s")
# 상호 참조: [e007 §6](e007-resource.md) / [Goal Graph §14](e001a-goal-graph.md)
RE_CROSS_REF = re.compile(r"\[[^\[\]]*?\b(e\d{3}[a-z]?)\b[^\[\]]*?§\s*([\d.]+)[^\[\]]*?\]")
# e000a §3 표: | Task | 요구한다 | Capability | `N:M` | ... |
RE_CARD_ROW = re.compile(r"^\| ([^|]+) \| ([^|]+) \| ([^|]+) \| `([^`]+)` \|", re.M)
# Entity 문서 §7 표기: `Task 1:0..N Execution`
RE_CARD_USE = re.compile(
    r"`([A-Za-z][A-Za-z ]*?) (1:0\.\.N|1:1\.\.N|1:0\.\.1|1:1|1:N|N:M|N:1) ([A-Za-z][A-Za-z ]*?)`")


def fail(report, doc, message):
    report(f"FAIL {doc}: {message}")


# ---------------------------------------------------------------- A. 문서


def load_prefix_table(report):
    """e000 §3 표에서 Entity 번호 → Rule Prefix 매핑을 읽는다."""
    if not os.path.exists(SPEC_FORMAT_DOC):
        return {}
    text = open(SPEC_FORMAT_DOC).read()
    section = re.search(r"^## 3\. .*?(?=^## 4\.)", text, re.S | re.M)
    if not section:
        fail(report, SPEC_FORMAT_DOC, "§3 번호 규칙 섹션을 찾을 수 없다")
        return {}
    return dict(RE_PREFIX_ROW.findall(section.group(0)))


def doc_entity_id(filename):
    """e005a-task-graph.md → '005-A' / e013-execution.md → '013'"""
    m = RE_DOC_ID.match(filename)
    if not m:
        return None
    num, suffix = m.group(1), m.group(2)
    return f"{num}-{suffix.upper()}" if suffix else num


def check_header(text, doc, report):
    fields = dict(RE_HEADER_FIELD.findall(text[:1200]))
    ok = True
    for name in ("Version", "Status", "Last Updated"):
        if name not in fields:
            fail(report, doc, f"헤더 블록에 `**{name}:**` 이 없다 (e000 §2)")
            ok = False
    if "Version" in fields and not RE_VERSION.match(fields["Version"]):
        fail(report, doc, f"Version 형식 위반 `{fields['Version']}` "
                          "— `v<major>.<minor> Draft|Stable` (e000 §2)")
        ok = False
    if "Last Updated" in fields and not RE_DATE.match(fields["Last Updated"]):
        fail(report, doc, f"Last Updated 형식 위반 `{fields['Last Updated']}` "
                          "— YYYY-MM-DD (e000 §2)")
        ok = False
    if "Status" in fields:
        base = fields["Status"].split("—")[0].strip()
        if base not in HEADER_STATUS_ALLOWED:
            fail(report, doc, f"Status 허용값 아님 `{base}` (e000 §2)")
            ok = False
    return ok, fields


def check_sections(text, doc, report):
    """12개 섹션이 번호 순서대로 있는지 본다."""
    headings = {int(n): title for n, title in RE_HEADING.findall(text)}
    ok = True
    for num, keywords in REQUIRED_SECTIONS:
        title = headings.get(num)
        if title is None:
            fail(report, doc, f"§{num} 섹션이 없다 — 기대: {keywords[0]} (e000 §1)")
            ok = False
        elif not any(k in title for k in keywords):
            fail(report, doc, f"§{num} 제목이 규격과 다르다 — `{title}` / "
                              f"기대: {keywords[0]} (e000 §1)")
            ok = False
    extra = sorted(n for n in headings if n > 12)
    if extra:
        titles = ", ".join(f"§{n} {headings[n]}" for n in extra)
        fail(report, doc, f"규격 밖 섹션 번호: {titles} "
                          "— 가장 가까운 필수 섹션의 하위 절로 옮긴다 (e000 §1)")
        ok = False
    if 0 in headings:
        fail(report, doc, f"§0 `{headings[0]}` — 규격에 §0은 없다. "
                          "§1 Definition 앞의 도입부는 번호 없는 산문으로 쓴다 (e000 §1)")
        ok = False
    return ok


def check_numbering(text, doc, expected_prefix, registered, report):
    """Rule/INV 개수와 Prefix를 본다.

    다른 Entity의 번호를 **인용**하는 것은 정상이다. 인용은 출처를 밝힌 줄에서만
    허용한다. 출처 표기는 두 가지다.

        [Rule REL-004](e000a-entity-relationships.md)   ← 링크
        e015 Rule EVA-004                               ← 코드 블록 안 (링크 불가)

    출처 없이 남의 Prefix를 쓰면 오탐이 아니라 실제 오류로 본다.
    """
    ok = True
    own_rules, own_invs = set(), set()
    foreign = set()

    for line in text.splitlines():
        cited = "](e0" in line or RE_DOC_CITE.search(line)
        for prefix, num in RE_RULE.findall(line):
            if prefix == expected_prefix:
                own_rules.add(num)
            elif cited:
                foreign.add(prefix)
            else:
                fail(report, doc, f"Rule Prefix `{prefix}` — 이 문서의 등록 Prefix는 "
                                  f"`{expected_prefix}`. 인용이면 해당 Entity 문서로 "
                                  "링크를 건다 (e000 §3)")
                ok = False
        for prefix, num in RE_INV_ENTITY.findall(line):
            if prefix == expected_prefix:
                own_invs.add(num)
            elif cited:
                foreign.add(prefix)
            else:
                fail(report, doc, f"INV Prefix `{prefix}` — 이 문서의 등록 Prefix는 "
                                  f"`{expected_prefix}`. 인용이면 해당 Entity 문서로 "
                                  "링크를 건다 (e000 §3)")
                ok = False

    for prefix in sorted(foreign | ({expected_prefix} if expected_prefix else set())):
        if prefix not in registered:
            fail(report, doc, f"미등록 Prefix `{prefix}` — e000 §3 표에 등록한다")
            ok = False

    if len(own_rules) < MIN_RULES:
        fail(report, doc, f"Rule 번호 {len(own_rules)}개 — {MIN_RULES}개 이상 필요 "
                          "(e000 §1 최소 요건 §3)")
        ok = False
    if len(own_invs) < MIN_INVARIANTS:
        fail(report, doc, f"INV 번호 {len(own_invs)}개 — {MIN_INVARIANTS}개 이상 필요 "
                          "(e000 §1 최소 요건 §5)")
        ok = False
    return ok


def check_global_invariant_defs(text, doc, report):
    """Entity 간 불변식(INV-NN)은 e000a에서만 정의한다. 참조는 허용."""
    ok = True
    for line in text.splitlines():
        if not RE_INV_GLOBAL.search(line):
            continue
        # 참조는 링크를 달거나 문장 안에 등장한다. 정의는 헤딩으로 나타난다.
        if line.startswith("#") and "e000a" not in line:
            fail(report, doc, f"Entity 간 불변식을 정의하고 있다 — `{line.strip()}`. "
                              "e000a에서 정의하고 여기서는 참조만 한다 (e000 §3)")
            ok = False
    return ok


def load_cardinality_table(report):
    """e000a §3 전체표에서 (좌변, 우변) → Cardinality 를 읽는다.

    이 표가 **단일 권위**다. Entity 문서 §7의 표기는 여기서 파생된다.
    """
    if not os.path.exists(RELATIONSHIPS_DOC):
        return {}
    text = open(RELATIONSHIPS_DOC).read()
    section = re.search(r"^## 3\. .*?(?=^## 4\.)", text, re.S | re.M)
    if not section:
        fail(report, RELATIONSHIPS_DOC, "§3 Cardinality 전체표를 찾을 수 없다")
        return {}
    table = {}
    for left, _, right, card in RE_CARD_ROW.findall(section.group(0)):
        table[(left.strip(), right.strip())] = card
    return table


def check_cardinality(text, doc, table, report):
    """§7의 `A 1:0..N B` 표기가 e000a §3 표와 어긋나지 않는지 본다.

    같은 수치를 두 문서에 적으면 반드시 갈린다. 갈리는 순간 잡는다.
    """
    section = re.search(r"\n## 7\. Relationships\n(.*?)(?=\n## 8\.)", text, re.S)
    if not section:
        return True
    ok = True
    for left, card, right in RE_CARD_USE.findall(section.group(1)):
        left, right = left.strip(), right.strip()
        if not right or left == right:
            continue
        expected = table.get((left, right))
        if expected is None:
            if (right, left) in table:
                fail(report, doc, f"`{left} {card} {right}` — e000a §3은 반대 방향으로 "
                                  f"적는다: `{right} {table[(right, left)]} {left}`")
                ok = False
            continue  # 표에 없는 관계는 각 문서가 정의한다
        if expected != card:
            fail(report, doc, f"`{left} {card} {right}` — e000a §3의 값은 "
                              f"`{expected}`다. 표가 정본이므로 한쪽을 고친다")
            ok = False
    return ok


def check_cross_refs(text, doc, docs_by_id, report):
    """`[e007 §6](...)` 같은 상호 참조가 실재하는 섹션을 가리키는지 본다.

    섹션을 재배치하면 링크는 멀쩡한데 번호만 어긋난다. 링크 검사기로는
    잡히지 않는 종류의 깨짐이다.
    """
    ok = True
    for target_id, section in RE_CROSS_REF.findall(text):
        path = docs_by_id.get(target_id)
        if path is None:
            continue  # 문서 자체가 없으면 링크 검사기가 잡는다
        body = open(path).read()
        top = section.split(".")[0]
        if f"\n## {top}." not in body:
            fail(report, doc, f"`{target_id} §{section}` — 대상 문서에 §{top} 이 없다")
            ok = False
        elif "." in section and f"\n### {section} " not in body \
                and f"\n#### {section} " not in body:
            fail(report, doc, f"`{target_id} §{section}` — 대상 문서에 §{section} 하위 절이 없다")
            ok = False
    return ok


def check_schema_link(text, doc, report):
    """§8이 가리키는 스키마 파일이 실제로 있는지 본다."""
    names = set(RE_SCHEMA_LINK.findall(text))
    if not names:
        fail(report, doc, "스키마 링크가 없다 — `intent-os-spec/schemas/<name>.json` "
                          "을 헤더나 §8에 건다 (e000 §1 최소 요건 §8)")
        return False
    ok = True
    for name in sorted(names):
        if not os.path.exists(os.path.join(SCHEMA_DIR, name)):
            fail(report, doc, f"링크된 스키마 파일이 없다 — `{name}`")
            ok = False
    return ok


def check_docs(report):
    prefixes = load_prefix_table(report)
    registered = set(prefixes.values())
    cardinality = load_cardinality_table(report)
    docs_by_id = {}
    for path in glob.glob(f"{ENTITY_DIR}/e*.md"):
        m = RE_DOC_ID.match(os.path.basename(path))
        if m:
            docs_by_id[f"e{m.group(1)}{m.group(2) or ''}"] = path
    total = passed = failed = annex = 0

    for path in sorted(glob.glob(f"{ENTITY_DIR}/e*.md")):
        doc = os.path.basename(path)
        if doc in META_DOCS:
            continue
        text = open(path).read()
        total += 1

        ok, fields = check_header(text, doc, report)
        is_annex = fields.get("Format", "").strip().startswith("Annex")

        if is_annex:
            annex += 1
            # Annex도 헤더와 스키마 링크는 지킨다. 섹션 규격만 면제된다.
            ok &= check_schema_link(text, doc, report)
            ok &= check_global_invariant_defs(text, doc, report)
            ok &= check_cross_refs(text, doc, docs_by_id, report)
        else:
            ok &= check_sections(text, doc, report)
            ok &= check_numbering(
                text, doc, prefixes.get(doc_entity_id(doc)), registered, report)
            ok &= check_global_invariant_defs(text, doc, report)
            ok &= check_schema_link(text, doc, report)
            ok &= check_cross_refs(text, doc, docs_by_id, report)
            ok &= check_cardinality(text, doc, cardinality, report)

        passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

    return total, passed, failed, annex


# ------------------------------------------------------------- B. 스키마

# 값이 자유 형태라 닫을 수 없는 객체. 열어두는 이유를 여기에 남긴다.
OPEN_OBJECTS = {
    # (스키마 파일, JSON Pointer): 사유
}

# 값의 **형태**를 정의하는 자리. 여기만 닫는다.
SHAPE_MAP = ("properties", "$defs", "definitions", "patternProperties")
SHAPE_ONE = ("items", "additionalProperties")
SHAPE_LIST = ("prefixItems",)
# **조건**을 정의하는 자리. `contains`에 additionalProperties: false를 넣으면
# "Owner 항목이 하나 있는가"를 묻던 술어가 "Owner 말고 아무 필드도 없는가"로
# 바뀐다. 술어 자리는 닫지 않는다.
PREDICATE_ONE = ("contains", "propertyNames", "if", "then", "else", "not")
PREDICATE_LIST = ("allOf", "anyOf", "oneOf")


def iter_object_nodes(node, pointer="", shape=True):
    """스키마 트리를 돌며 (pointer, node, shape)를 낸다."""
    if isinstance(node, dict):
        yield pointer, node, shape
        for key, value in node.items():
            if key in SHAPE_MAP:
                if isinstance(value, dict):
                    for k, v in value.items():
                        yield from iter_object_nodes(v, f"{pointer}/{key}/{k}", shape)
            elif key in SHAPE_ONE or key in PREDICATE_ONE:
                child = shape and key in SHAPE_ONE
                if isinstance(value, dict):
                    yield from iter_object_nodes(value, f"{pointer}/{key}", child)
            elif key in SHAPE_LIST or key in PREDICATE_LIST:
                child = shape and key in SHAPE_LIST
                if isinstance(value, list):
                    for i, v in enumerate(value):
                        yield from iter_object_nodes(v, f"{pointer}/{key}/{i}", child)


def check_data_document(path, name, doc, report):
    """`*.schema.json`이 아닌 파일은 스키마가 아니라 **데이터**다.

    자신을 검증할 스키마를 `$schema`로 가리켜야 하고, 실제로 통과해야 한다.
    goal-state-machine.json이 여기 해당한다.
    """
    ref = doc.get("$schema", "")
    if not ref:
        fail(report, name, "데이터 문서인데 `$schema`가 없다 — 자신을 검증할 "
                           "스키마를 가리킨다 (e000 §8)")
        return False

    target = ref.rsplit("/", 1)[-1]
    target_path = os.path.join(SCHEMA_DIR, target)
    if not os.path.exists(target_path):
        fail(report, name, f"`$schema`가 가리키는 스키마가 없다 — `{target}`")
        return False

    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return True  # 예시 검증기와 같은 의존성. 없으면 형태 검사만 하고 넘어간다

    schema = json.load(open(target_path))
    errors = sorted(Draft202012Validator(schema).iter_errors(doc),
                    key=lambda e: list(e.path))
    for err in errors[:5]:
        fail(report, name, f"{list(err.path)}: {err.message[:160]}")
    return not errors


def check_schemas(report):
    total = passed = failed = 0

    for path in sorted(glob.glob(f"{SCHEMA_DIR}/*.json")):
        name = os.path.basename(path)
        total += 1
        ok = True
        try:
            schema = json.load(open(path))
        except json.JSONDecodeError as exc:
            fail(report, name, f"JSON 파싱 실패 — {exc}")
            failed += 1
            continue

        if not name.endswith(".schema.json"):
            ok = check_data_document(path, name, schema, report)
            passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)
            continue

        dialect = schema.get("$schema", "")
        if "2020-12" not in dialect:
            fail(report, name, f"$schema가 draft 2020-12가 아니다 — "
                               f"`{dialect or '없음'}` (e000 §8)")
            ok = False
        for field in ("title", "description"):
            if not schema.get(field):
                fail(report, name, f"최상위 `{field}`이 없다 (e000 §8)")
                ok = False

        for pointer, node, shape in iter_object_nodes(schema):
            props = node.get("properties")
            if not isinstance(props, dict) or not shape:
                continue
            if node.get("additionalProperties") is not False:
                if (name, pointer) not in OPEN_OBJECTS:
                    where = pointer or "(최상위)"
                    fail(report, name, f"`{where}` 에 additionalProperties: false "
                                       "가 없다 — 오타 필드가 통과한다")
                    ok = False
            missing = [k for k, v in props.items()
                       if not (isinstance(v, dict) and v.get("description"))]
            if missing:
                where = pointer or "(최상위)"
                shown = ", ".join(missing[:8])
                more = f" 외 {len(missing) - 8}개" if len(missing) > 8 else ""
                fail(report, name, f"`{where}` description 누락 — {shown}{more}")
                ok = False

        passed, failed = (passed + 1, failed) if ok else (passed, failed + 1)

    return total, passed, failed


# ---------------------------------------------------------------- main


def main(argv):
    only = None
    if "--only" in argv:
        only = argv[argv.index("--only") + 1]

    lines = []
    report = lines.append
    exit_code = 0

    d_total = d_pass = d_fail = d_annex = 0
    s_total = s_pass = s_fail = 0

    if only in (None, "docs"):
        d_total, d_pass, d_fail, d_annex = check_docs(report)
    if only in (None, "schemas"):
        s_total, s_pass, s_fail = check_schemas(report)

    for line in lines:
        print(line)
    if lines:
        print()

    if only in (None, "docs"):
        print(f"문서    {d_total}개: {d_pass} 통과, {d_fail} 실패 "
              f"(부속 문서 {d_annex}개는 섹션 규격 면제)")
    if only in (None, "schemas"):
        print(f"스키마  {s_total}개: {s_pass} 통과, {s_fail} 실패")

    exit_code = 1 if (d_fail + s_fail) else 0
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
