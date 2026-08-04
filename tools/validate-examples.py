#!/usr/bin/env python3
"""문서의 JSON 예시가 대응 스키마를 통과하는지 검사한다.

두 가지를 검사한다.

1. **Entity 명세** (`entities/`) — `DOC_TO_SCHEMA` 매핑에 따라 문서 전체의 JSON
   블록을 해당 스키마로 검증한다. entities/e000-spec-format.md §11 체크리스트의
   "§8의 JSON 예시가 실제 스키마를 통과하는가" 항목을 자동화한 것이다.

2. **Volume 명세** (루트 `v*.md`) — 한 문서가 여러 Entity의 예시를 섞어 쓰므로
   문서 단위 매핑이 불가능하다. 대신 각 JSON 블록 바로 앞에 마커를 요구한다.

       <!-- validate: goal.schema.json -->
       ```json
       { ... }
       ```

   스키마에 매이지 않는 개념 예시는 `none`으로 명시한다.

       <!-- validate: none -->

   **마커 없는 JSON 블록은 실패로 처리한다.** 볼륨 문서의 예시가 검증망
   밖에 있던 것이 v0.1의 실제 결함이었으므로, 누락을 침묵시키지 않는다.

사용법:
    python3 tools/validate-examples.py

의존성: jsonschema, referencing (pip install jsonschema referencing)
"""

import glob
import json
import os
import re
import sys

SCHEMA_DIR = "intent-os-spec/schemas"
ENTITY_DIR = "entities"
VOLUME_GLOB = "v*.md"

# 문서 → 스키마 매핑. 최상위 id 키만으로는 구분되지 않는 경우가 있어 명시한다.
# (예: goal-graph와 task-graph는 둘 다 graph_id로 시작한다)
DOC_TO_SCHEMA = {
    "e001b-goal-schema.md": "goal.schema.json",
    "e001a-goal-graph.md": "goal-graph.schema.json",
    "e002-intent.md": "intent.schema.json",
    "e003-context.md": "context.schema.json",
    "e004-constraint.md": "constraint.schema.json",
    "e005-task.md": "task.schema.json",
    "e005a-task-graph.md": "task-graph.schema.json",
    "e006-capability.md": "capability.schema.json",
    "e006a-capability-taxonomy.md": "capability-taxonomy.schema.json",
    "e007-resource.md": "resource.schema.json",
    "e008-plan.md": "plan.schema.json",
    "e009-decision.md": "decision.schema.json",
    "e010-memory.md": "memory.schema.json",
    "e011-knowledge.md": "knowledge.schema.json",
    "e012-feedback.md": "feedback.schema.json",
    "e013-execution.md": "execution.schema.json",
    "e014-outcome.md": "outcome.schema.json",
    "e015-evaluation.md": "evaluation.schema.json",
    "e016-artifact.md": "artifact.schema.json",
    "e017-assumption.md": "assumption.schema.json",
    "e018-risk.md": "risk.schema.json",
    "e019-policy.md": "policy.schema.json",
    "e020-event.md": "event.schema.json",
    "e021-session.md": "session.schema.json",
    "e022-workflow.md": "workflow.schema.json",
    "e023-agent.md": "agent.schema.json",
    "e024-tool.md": "tool.schema.json",
    "e025-resource-profile.md": "resource-profile.schema.json",
}

# 마커가 붙은 JSON 블록. 마커와 블록 사이 공백 줄은 허용한다.
MARKED_BLOCK = re.compile(
    r"<!--\s*validate:\s*([\w.\-]+)\s*-->\s*\n+```json\n(.*?)\n```", re.S
)
ANY_JSON_BLOCK = re.compile(r"```json\n(.*?)\n```", re.S)


def load_registry():
    """로컬 스키마 파일로 $ref 해소용 레지스트리를 만든다 (네트워크 접근 없이)."""
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012

    resources = []
    for path in glob.glob(f"{SCHEMA_DIR}/*.json"):
        schema = json.load(open(path))
        resource = Resource(contents=schema, specification=DRAFT202012)
        if schema.get("$id"):
            resources.append((schema["$id"], resource))
        resources.append((os.path.basename(path), resource))
    return Registry().with_resources(resources)


def parse_dict(block):
    """JSON 객체로 파싱되면 반환, 아니면 None (부분 스니펫은 건너뛴다)."""
    try:
        obj = json.loads(block)
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) and obj else None


def check_entity_docs(schemas, registry, validator_cls, report):
    """Entity 문서: 문서 단위 스키마 매핑으로 검증한다."""
    total = passed = failed = 0
    for doc, schema_name in sorted(DOC_TO_SCHEMA.items()):
        path = os.path.join(ENTITY_DIR, doc)
        if not os.path.exists(path) or schema_name not in schemas:
            continue
        schema = schemas[schema_name]
        required = set(schema.get("required") or [])
        validator = validator_cls(schema, registry=registry)

        for block in ANY_JSON_BLOCK.findall(open(path).read()):
            obj = parse_dict(block)
            if obj is None:
                continue
            # 필수 키를 하나도 갖지 않으면 그 Entity의 예시가 아니다
            if required and not (required & set(obj)):
                continue

            total += 1
            errors = sorted(validator.iter_errors(obj), key=lambda e: list(e.path))
            if errors:
                failed += 1
                report(f"FAIL {doc} -> {schema_name}")
                for err in errors[:5]:
                    report(f"       {list(err.path)}: {err.message[:160]}")
            else:
                passed += 1
    return total, passed, failed


def check_volume_docs(schemas, registry, validator_cls, report):
    """Volume 문서: 블록마다 마커로 스키마를 지정한다. 마커 누락은 실패다."""
    total = passed = failed = 0
    for path in sorted(glob.glob(VOLUME_GLOB)):
        text = open(path).read()
        doc = os.path.basename(path)

        marked = {}  # 블록 본문 → 스키마명
        for schema_name, block in MARKED_BLOCK.findall(text):
            marked[block] = schema_name

        for block in ANY_JSON_BLOCK.findall(text):
            obj = parse_dict(block)
            if obj is None:
                continue  # 부분 스니펫

            total += 1
            schema_name = marked.get(block)
            if schema_name is None:
                failed += 1
                head = block.strip().splitlines()[0][:60]
                report(f"FAIL {doc}: validate 마커 없는 JSON 블록 — `{head}`")
                report("       <!-- validate: <schema>.json --> 또는 "
                       "<!-- validate: none --> 을 블록 앞에 붙인다")
                continue
            if schema_name == "none":
                passed += 1  # 개념 예시로 명시됨
                continue
            if schema_name not in schemas:
                failed += 1
                report(f"FAIL {doc}: 알 수 없는 스키마 `{schema_name}`")
                continue

            validator = validator_cls(schemas[schema_name], registry=registry)
            errors = sorted(validator.iter_errors(obj), key=lambda e: list(e.path))
            if errors:
                failed += 1
                report(f"FAIL {doc} -> {schema_name}")
                for err in errors[:5]:
                    report(f"       {list(err.path)}: {err.message[:160]}")
            else:
                passed += 1
    return total, passed, failed


def main():
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("jsonschema가 필요하다: pip install jsonschema referencing", file=sys.stderr)
        return 2

    registry = load_registry()
    schemas = {
        os.path.basename(p): json.load(open(p))
        for p in glob.glob(f"{SCHEMA_DIR}/*.json")
    }

    lines = []
    report = lines.append

    e_total, e_pass, e_fail = check_entity_docs(
        schemas, registry, Draft202012Validator, report)
    v_total, v_pass, v_fail = check_volume_docs(
        schemas, registry, Draft202012Validator, report)

    for line in lines:
        print(line)

    print(f"\nEntity  {e_total}개 예시: {e_pass} 통과, {e_fail} 실패")
    print(f"Volume  {v_total}개 예시: {v_pass} 통과, {v_fail} 실패")
    print(f"합계    {e_total + v_total}개 예시: "
          f"{e_pass + v_pass} 통과, {e_fail + v_fail} 실패")
    return 1 if (e_fail + v_fail) else 0


if __name__ == "__main__":
    sys.exit(main())
