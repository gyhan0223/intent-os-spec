#!/usr/bin/env python3
"""Entity 명세의 JSON 예시가 대응 스키마를 통과하는지 검사한다.

entities/e000-spec-format.md §11 체크리스트의
"§8의 JSON 예시가 실제 스키마를 통과하는가" 항목을 자동화한 것이다.

사용법:
    python3 tools/validate-examples.py

의존성: jsonschema (pip install jsonschema)
"""

import glob
import json
import os
import re
import sys

SCHEMA_DIR = "intent-os-spec/schemas"
ENTITY_DIR = "entities"

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


def load_registry():
    """로컬 스키마 파일로 $ref 해소용 레지스트리를 만든다 (네트워크 접근 없이)."""
    from jsonschema import Draft202012Validator  # noqa: F401
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


def main():
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("jsonschema가 필요하다: pip install jsonschema", file=sys.stderr)
        return 2

    registry = load_registry()
    schemas = {
        os.path.basename(p): json.load(open(p))
        for p in glob.glob(f"{SCHEMA_DIR}/*.json")
    }

    total = passed = failed = 0
    for doc, schema_name in sorted(DOC_TO_SCHEMA.items()):
        path = os.path.join(ENTITY_DIR, doc)
        if not os.path.exists(path) or schema_name not in schemas:
            continue
        schema = schemas[schema_name]
        required = set(schema.get("required") or [])
        validator = Draft202012Validator(schema, registry=registry)

        for block in re.findall(r"```json\n(.*?)\n```", open(path).read(), re.S):
            try:
                obj = json.loads(block)
            except json.JSONDecodeError:
                continue  # 부분 스니펫은 건너뛴다
            if not isinstance(obj, dict) or not obj:
                continue
            # 필수 키를 하나도 갖지 않으면 그 Entity의 예시가 아니다
            if required and not (required & set(obj)):
                continue

            total += 1
            errors = sorted(validator.iter_errors(obj), key=lambda e: list(e.path))
            if errors:
                failed += 1
                print(f"FAIL {doc} -> {schema_name}")
                for err in errors[:5]:
                    print(f"       {list(err.path)}: {err.message[:160]}")
            else:
                passed += 1

    print(f"\n{total}개 예시 검사: {passed} 통과, {failed} 실패")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
