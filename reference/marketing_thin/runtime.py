from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable


@dataclass(frozen=True)
class ResourceSpec:
    resource_id: str
    label: str
    supported_task_types: frozenset[str]
    quality: float
    success: float
    reliability: float
    cost_efficiency: float
    latency_efficiency: float


RESOURCES: tuple[ResourceSpec, ...] = (
    ResourceSpec(
        "tool:web-search",
        "Web Search",
        frozenset({"Research"}),
        quality=0.80,
        success=0.94,
        reliability=0.95,
        cost_efficiency=0.92,
        latency_efficiency=0.76,
    ),
    ResourceSpec(
        "model:fast",
        "Fast Model",
        frozenset({"Research", "Creation", "Verification"}),
        quality=0.72,
        success=0.90,
        reliability=0.94,
        cost_efficiency=0.96,
        latency_efficiency=0.96,
    ),
    ResourceSpec(
        "model:balanced",
        "Balanced Model",
        frozenset({"Creation", "Verification"}),
        quality=0.88,
        success=0.93,
        reliability=0.95,
        cost_efficiency=0.78,
        latency_efficiency=0.82,
    ),
    ResourceSpec(
        "model:quality",
        "Quality Model",
        frozenset({"Creation", "Verification"}),
        quality=0.96,
        success=0.95,
        reliability=0.94,
        cost_efficiency=0.58,
        latency_efficiency=0.62,
    ),
)

UTILITY_WEIGHTS = {
    "quality": 0.35,
    "success": 0.25,
    "reliability": 0.15,
    "cost": 0.15,
    "latency": 0.10,
}

TERMINAL_EXECUTION_STATES = {"Completed", "Failed", "TimedOut", "Aborted"}


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)


class RuleRouter:
    """Phase-0 router: deterministic rules over explicit Resource profiles."""

    @staticmethod
    def _bonus(task_type: str, resource_id: str) -> float:
        if task_type == "Research" and resource_id == "tool:web-search":
            return 0.20
        if task_type == "Creation" and resource_id == "model:balanced":
            return 0.12
        if task_type == "Creation" and resource_id == "model:quality":
            return 0.08
        if task_type == "Verification" and resource_id == "model:quality":
            return 0.18
        return 0.0

    def rank(self, task: dict[str, Any]) -> list[tuple[ResourceSpec, float]]:
        task_type = task["task_type"]
        candidates = [r for r in RESOURCES if task_type in r.supported_task_types]
        ranked: list[tuple[ResourceSpec, float]] = []
        for resource in candidates:
            utility = (
                UTILITY_WEIGHTS["quality"] * resource.quality
                + UTILITY_WEIGHTS["success"] * resource.success
                + UTILITY_WEIGHTS["reliability"] * resource.reliability
                + UTILITY_WEIGHTS["cost"] * resource.cost_efficiency
                + UTILITY_WEIGHTS["latency"] * resource.latency_efficiency
                + self._bonus(task_type, resource.resource_id)
            )
            ranked.append((resource, _clamp(utility)))
        return sorted(ranked, key=lambda item: (-item[1], item[0].resource_id))


class PromptCompiler:
    def compile(
        self,
        goal: dict[str, Any],
        task: dict[str, Any],
        prior_artifacts: Iterable[str],
    ) -> str:
        prior = "\n\n".join(prior_artifacts) or "(none)"
        return (
            "ROLE: Senior Korean education marketing operator\n"
            f"GOAL: {goal['objective']['description']}\n"
            f"TASK: {task['objective']}\n"
            f"EXPECTED OUTPUT: {task.get('expected_output', '')}\n"
            f"CONSTRAINTS: {', '.join(task.get('constraints', [])) or '(none)'}\n"
            "PRIOR ARTIFACTS:\n"
            f"{prior}\n"
            "Return a concise, execution-ready result in Korean."
        )


class DeterministicAdapter:
    """Offline adapter used to verify orchestration without provider credentials.

    It deliberately does not impersonate a live model/search provider. Replacing
    this adapter is the only integration step required for live Resources.
    """

    def execute(
        self,
        resource: ResourceSpec,
        task: dict[str, Any],
        prompt: str,
        prior_artifacts: list[str],
    ) -> dict[str, Any]:
        task_type = task["task_type"]
        if task_type == "Research":
            text = (
                "# 조사 브리프\n"
                "- 핵심 타깃: 겨울방학 동안 학업 루틴과 입시 준비를 함께 잡으려는 학생·학부모\n"
                "- 주요 불안: 단기 특강의 일회성, 관리 공백, 결과를 확인하기 어려움\n"
                "- 메시지 기회: 수업 자체보다 매일의 관리 과정과 주간 성과 확인을 구체적으로 제시\n"
                "- 전환 장치: 프로그램 설명보다 상담 예약 CTA를 하나로 통일\n"
                "- 검증 필요: 실제 가격·기간·정원·성과 수치는 게시 전 운영 데이터로 확인"
            )
        elif task_type == "Creation":
            research = prior_artifacts[-1] if prior_artifacts else ""
            text = (
                "# 윈터스쿨 모집 마케팅 문서\n\n"
                "## 핵심 메시지\n"
                "겨울방학을 '많이 공부한 기간'이 아니라 '매일 관리되고 결과가 남는 기간'으로 만듭니다.\n\n"
                "## 타깃\n"
                "학업 루틴이 흔들리기 쉽고, 방학 동안의 변화가 실제 성적으로 이어지는지 확인하고 싶은 학생과 학부모.\n\n"
                "## 카피 3종\n"
                "1. 방학은 길지만, 성적이 오르는 하루는 설계되어 있습니다.\n"
                "2. 매일 공부하고, 매주 확인하고, 다음 주 계획까지 연결합니다.\n"
                "3. 수업만 듣는 윈터스쿨이 아니라 기록이 남는 윈터스쿨.\n\n"
                "## CTA\n"
                "현재 학습 상태와 방학 목표를 기준으로 상담을 예약하세요.\n\n"
                "## 조사 반영\n"
                f"{research[:420]}"
            )
        else:
            draft = prior_artifacts[-1] if prior_artifacts else ""
            text = (
                "# 검수 완료본\n\n"
                "## 검수 기준\n"
                "- 목표 정합성: 상담 전환으로 이어지는 단일 CTA 유지\n"
                "- 구체성: 관리 과정과 확인 가능한 결과를 중심으로 표현\n"
                "- 안전성: 확인되지 않은 수치·최상급 표현은 사용하지 않음\n\n"
                "## 최종 문서\n"
                f"{draft}\n\n"
                "## 게시 전 확인\n"
                "가격, 운영 기간, 정원, 실제 성과 수치는 운영자가 사실 확인 후 삽입합니다."
            )

        usage = {
            "input_chars": len(prompt),
            "output_chars": len(text),
            "api_calls": 1,
        }
        return {"text": text, "usage": usage}


class SimpleEvaluator:
    RUBRIC_ID = "rubric:marketing-thin:v1"
    WEIGHTS = {"quality": 0.4, "goal_alignment": 0.4, "efficiency": 0.2, "satisfaction": 0.0}

    def evaluate(
        self,
        task: dict[str, Any],
        text: str,
        resource: ResourceSpec,
        user_rating: int | None,
    ) -> tuple[dict[str, float | None], list[str], str]:
        checks = [
            len(text) >= 180,
            "#" in text,
            "TODO" not in text,
            task["task_type"] != "Creation" or "CTA" in text,
            task["task_type"] != "Verification" or "검수" in text,
        ]
        quality = 0.55 + 0.09 * sum(checks)
        goal_alignment = 0.92 if task["task_type"] in {"Creation", "Verification"} else 0.86
        efficiency = (resource.cost_efficiency + resource.latency_efficiency) / 2
        satisfaction = None if user_rating is None else _clamp((user_rating - 1) / 4)

        base_weights = dict(self.WEIGHTS)
        if satisfaction is not None:
            base_weights = {"quality": 0.35, "goal_alignment": 0.35, "efficiency": 0.15, "satisfaction": 0.15}
        composite = (
            base_weights["quality"] * quality
            + base_weights["goal_alignment"] * goal_alignment
            + base_weights["efficiency"] * efficiency
            + base_weights["satisfaction"] * (satisfaction or 0.0)
        )
        composite = _clamp(composite)
        verdict = "accept" if composite >= 0.75 else "accept_with_revision" if composite >= 0.6 else "reject"
        rationale = [
            f"rubric checks passed: {sum(checks)}/{len(checks)}",
            f"task type {task['task_type']} matches the routed Resource profile",
            "goal alignment is measured with an Expected Output proxy in Phase 0",
        ]
        return (
            {
                "quality": _clamp(quality),
                "goal_alignment": _clamp(goal_alignment),
                "efficiency": _clamp(efficiency),
                "satisfaction": satisfaction,
                "composite": composite,
                "weights": base_weights,
                "alignment_proxy": True,
            },
            rationale,
            verdict,
        )


class MarketingThinRuntime:
    def __init__(self, base_time: datetime | None = None) -> None:
        self.base_time = base_time or datetime(2026, 8, 7, 10, 0, tzinfo=timezone.utc)
        self.router = RuleRouter()
        self.compiler = PromptCompiler()
        self.adapter = DeterministicAdapter()
        self.evaluator = SimpleEvaluator()

    def _goal(self, raw_goal: str) -> dict[str, Any]:
        return {
            "goal_id": "goal_DEMO001",
            "version": 1,
            "title": "윈터스쿨 모집 마케팅 문서 완성",
            "goal_type": "Creation",
            "objective": {
                "description": raw_goal,
                "desired_state": {
                    "metric": "reviewed_marketing_document",
                    "operator": "exists",
                    "target": "ready",
                    "unit": "document",
                    "baseline": None,
                },
            },
            "status": {
                "phase": "Completed",
                "progress": 1.0,
                "entered_at": _iso(self.base_time + timedelta(seconds=12)),
            },
            "metadata": {
                "created_by": "reference_runtime",
                "created_at": _iso(self.base_time),
                "source": "conversation",
                "history": [
                    {
                        "version": 1,
                        "changed_at": _iso(self.base_time),
                        "changed_by": "reference_runtime",
                        "change_type": "created",
                        "description": "Structured from the CLI goal input.",
                    }
                ],
            },
        }

    @staticmethod
    def _intent(goal: dict[str, Any]) -> dict[str, Any]:
        return {
            "intent_id": "intent_DEMO001",
            "goal_id": goal["goal_id"],
            "intent_type": "Promotion",
            "direction": "교육 서비스의 겨울방학 모집 메시지를 조사 근거와 검수 절차를 거쳐 완성한다",
            "rationale": "마케팅 문서 생성은 조사, 카피 작성, 검수로 최소 분해할 수 있다.",
            "confidence": 0.94,
            "priority": "High",
            "evidence": ["사용자 입력 목표", "마케팅 도메인 Thin Reference 범위"],
            "expected_impact": "게시 가능한 모집 메시지 초안 1종 확보",
            "status": "Expanded",
        }

    @staticmethod
    def _tasks(goal: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "id": "task_research",
                "goal_id": goal["goal_id"],
                "objective": "윈터스쿨 모집 메시지에 필요한 타깃 불안과 전환 포인트를 조사한다",
                "task_type": "Research",
                "required_capabilities": ["research.web", "marketing.audience_analysis"],
                "dependencies": [],
                "expected_output": "타깃, 불안, 메시지 기회, CTA를 포함한 조사 브리프",
                "execution_mode": "sequential",
                "constraints": ["확인되지 않은 사실을 확정적으로 쓰지 않는다"],
                "priority": "High",
                "retry_policy": {"max_retries": 1, "on_failure": "reassign"},
                "state": "Evaluated",
                "attempts": 1,
            },
            {
                "id": "task_copy",
                "goal_id": goal["goal_id"],
                "objective": "조사 브리프를 바탕으로 윈터스쿨 모집 카피와 CTA를 작성한다",
                "task_type": "Creation",
                "required_capabilities": ["language.generation.copywriting", "marketing.strategy"],
                "dependencies": ["task_research"],
                "expected_output": "핵심 메시지, 타깃, 카피 3종, 단일 CTA가 포함된 마케팅 문서",
                "execution_mode": "sequential",
                "constraints": ["과장된 최상급 표현 금지", "CTA는 상담 예약 하나로 통일"],
                "priority": "High",
                "retry_policy": {"max_retries": 1, "on_failure": "reassign"},
                "state": "Evaluated",
                "attempts": 1,
            },
            {
                "id": "task_review",
                "goal_id": goal["goal_id"],
                "objective": "작성된 모집 문서를 목표 정합성, 구체성, 사실 안전성 기준으로 검수한다",
                "task_type": "Verification",
                "required_capabilities": ["language.review", "marketing.claim_verification"],
                "dependencies": ["task_copy"],
                "expected_output": "검수 기준과 게시 전 확인사항이 포함된 최종 문서",
                "execution_mode": "sequential",
                "constraints": ["검증되지 않은 가격, 정원, 성과 수치는 사실 확인 대상으로 남긴다"],
                "priority": "High",
                "retry_policy": {"max_retries": 1, "on_failure": "reassign"},
                "state": "Evaluated",
                "attempts": 1,
            },
        ]

    def run(self, raw_goal: str, user_rating: int | None = None) -> dict[str, Any]:
        if user_rating is not None and user_rating not in {1, 2, 3, 4, 5}:
            raise ValueError("user_rating must be an integer from 1 to 5")

        goal = self._goal(raw_goal)
        intent = self._intent(goal)
        tasks = self._tasks(goal)
        decisions: list[dict[str, Any]] = []
        executions: list[dict[str, Any]] = []
        outcomes: list[dict[str, Any]] = []
        artifacts: list[dict[str, Any]] = []
        evaluations: list[dict[str, Any]] = []
        artifact_contents: dict[str, str] = {}

        for index, task in enumerate(tasks):
            ranked = self.router.rank(task)
            selected, selected_utility = ranked[0]
            task["assigned_resource_id"] = selected.resource_id

            decision_id = f"decision_{index + 1:02d}"
            execution_id = f"execution_{index + 1:02d}"
            outcome_id = f"outcome_{index + 1:02d}"
            artifact_id = f"artifact_{index + 1:02d}"
            evaluation_id = f"evaluation_{index + 1:02d}"

            previous_contents = [artifact_contents[a["artifact_id"]] for a in artifacts]
            prompt = self.compiler.compile(goal, task, previous_contents)
            result = self.adapter.execute(selected, task, prompt, previous_contents)

            t0 = self.base_time + timedelta(seconds=index * 4 + 1)
            t1 = t0 + timedelta(milliseconds=800 + index * 100)
            measured = t1 + timedelta(milliseconds=100)
            evaluated = measured + timedelta(milliseconds=100)
            latency_ms = int((t1 - t0).total_seconds() * 1000)
            cost_amount = round((result["usage"]["input_chars"] + result["usage"]["output_chars"]) / 100000, 6)

            alternatives = [
                {"candidate": resource.resource_id, "utility": utility}
                for resource, utility in ranked
            ]
            decision = {
                "decision_id": decision_id,
                "decision_type": "ResourceSelection",
                "subject": {"goal_id": goal["goal_id"], "task_id": task["id"]},
                "selection": selected.resource_id,
                "alternatives_considered": alternatives,
                "rationale": [
                    f"rule-based ranking selected {selected.label} for {task['task_type']}",
                    f"selected utility={selected_utility:.4f}",
                ],
                "utility_scores": {
                    "selected_utility": selected_utility,
                    "weights": UTILITY_WEIGHTS,
                },
                "inputs_snapshot": {
                    "router": "marketing-thin-rule-router:v1",
                    "resource_profile_count": len(RESOURCES),
                    "task_type": task["task_type"],
                },
                "confidence": 0.92 if len(ranked) == 1 else _clamp(0.75 + min(0.2, ranked[0][1] - ranked[1][1])),
                "decided_by": "decision_engine:marketing-thin:v1",
                "status": "Applied",
                "outcome_link": outcome_id,
                "decided_at": _iso(t0 - timedelta(milliseconds=100)),
            }
            decisions.append(decision)

            execution = {
                "execution_id": execution_id,
                "task_id": task["id"],
                "decision_id": decision_id,
                "resource_id": selected.resource_id,
                "mode": "single",
                "attempt": 1,
                "status": "Completed",
                "progress": 1.0,
                "contributes_to_goal": True,
                "created_at": _iso(t0 - timedelta(milliseconds=50)),
                "started_at": _iso(t0),
                "finished_at": _iso(t1),
                "latency_ms": latency_ms,
                "cost": {"amount": cost_amount, "currency": "USD", "estimated": True},
                "usage": result["usage"],
                "error": None,
                "failure_class": None,
                "outcome_id": outcome_id,
            }
            executions.append(execution)

            text = result["text"]
            artifact = {
                "artifact_id": artifact_id,
                "outcome_id": outcome_id,
                "content_hash": _sha256(text),
                "type": "text",
                "media_type": "text/markdown",
                "location": f"memory://{artifact_id}",
                "size_bytes": len(text.encode("utf-8")),
                "encoding": "utf-8",
                "name": task["expected_output"],
                "summary": text.replace("\n", " ")[:180],
                "tags": ["thin-reference", "marketing", task["task_type"].lower()],
                "produced_by": selected.resource_id,
                "derived_from": [artifacts[-1]["artifact_id"]] if artifacts else [],
                "produced_at": _iso(t1),
                "visibility": "internal",
                "contains_pii": False,
                "status": "Adopted",
            }
            artifacts.append(artifact)
            artifact_contents[artifact_id] = text

            outcome = {
                "outcome_id": outcome_id,
                "execution_id": execution_id,
                "task_id": task["id"],
                "status": "succeeded",
                "artifacts": [artifact_id],
                "output_summary": artifact["summary"],
                "output_count": 1,
                "cost": execution["cost"],
                "latency_ms": latency_ms,
                "usage": result["usage"],
                "measured_at": _iso(measured),
                "goal_progress": [
                    {
                        "goal_id": goal["goal_id"],
                        "metric": "reviewed_marketing_document",
                        "delta": 1 if task["id"] == "task_review" else 0,
                    }
                ],
                "contributes_to_goal": True,
                "evaluation_ids": [evaluation_id],
                "status_lifecycle": "Evaluated",
            }
            outcomes.append(outcome)

            rating_for_task = user_rating if task["id"] == "task_review" else None
            scores, rationale, verdict = self.evaluator.evaluate(task, text, selected, rating_for_task)
            evaluation = {
                "evaluation_id": evaluation_id,
                "outcome_id": outcome_id,
                "task_id": task["id"],
                "evaluator": "eval_engine:marketing-thin:v1",
                "evaluator_type": "automatic",
                "rubric_id": self.evaluator.RUBRIC_ID,
                "rubric_version": "1",
                "scores": scores,
                "decision_review": {
                    "decision_id": decision_id,
                    "decision_quality": selected_utility,
                },
                "verdict": verdict,
                "adopted": verdict != "reject",
                "rationale": rationale,
                "status": "Completed",
                "evaluated_at": _iso(evaluated),
            }
            evaluations.append(evaluation)

        final_artifact_id = artifacts[-1]["artifact_id"]
        bundle = {
            "goal": goal,
            "intent": intent,
            "tasks": tasks,
            "decisions": decisions,
            "executions": executions,
            "outcomes": outcomes,
            "artifacts": artifacts,
            "evaluations": evaluations,
            "artifact_contents": artifact_contents,
            "final_artifact_id": final_artifact_id,
            "resource_catalog": [r.resource_id for r in RESOURCES],
        }
        validate_core_invariants(bundle)
        return bundle


def validate_core_invariants(bundle: dict[str, Any]) -> None:
    """Executable subset of the global invariants used by the Thin Reference."""
    goal_id = bundle["goal"]["goal_id"]
    tasks = {t["id"]: t for t in bundle["tasks"]}
    decisions = {d["decision_id"]: d for d in bundle["decisions"]}
    executions = {e["execution_id"]: e for e in bundle["executions"]}
    outcomes = {o["outcome_id"]: o for o in bundle["outcomes"]}
    artifacts = {a["artifact_id"]: a for a in bundle["artifacts"]}
    evaluations = {e["evaluation_id"]: e for e in bundle["evaluations"]}

    if any(task.get("goal_id") != goal_id for task in tasks.values()):
        raise AssertionError("INV-01 subset: every Task must reach the Goal")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise AssertionError("INV-08: Task Graph contains a cycle")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dep in tasks[task_id].get("dependencies", []):
            if dep not in tasks:
                raise AssertionError(f"Task dependency does not exist: {dep}")
            visit(dep)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in tasks:
        visit(task_id)

    for execution in executions.values():
        decision = decisions.get(execution["decision_id"])
        if decision is None:
            raise AssertionError("INV-03: Execution has no Decision")
        if decision["subject"].get("task_id") != execution["task_id"]:
            raise AssertionError("INV-03: Decision subject does not match Execution task")
        if decision["selection"] != execution["resource_id"]:
            raise AssertionError("INV-03: Decision selection does not match Execution Resource")

    seen_execution_ids: set[str] = set()
    for outcome in outcomes.values():
        if outcome["execution_id"] in seen_execution_ids:
            raise AssertionError("INV-04: Execution produced more than one Outcome")
        seen_execution_ids.add(outcome["execution_id"])
        execution = executions.get(outcome["execution_id"])
        if execution is None:
            raise AssertionError("Outcome references missing Execution")
        if execution["outcome_id"] != outcome["outcome_id"]:
            raise AssertionError("Execution/Outcome back references disagree")
    for execution in executions.values():
        if execution["status"] in TERMINAL_EXECUTION_STATES and execution["execution_id"] not in seen_execution_ids:
            raise AssertionError("INV-04: terminal Execution has no Outcome")

    artifact_owners: dict[str, str] = {}
    for outcome in outcomes.values():
        for artifact_id in outcome.get("artifacts", []):
            artifact = artifacts.get(artifact_id)
            if artifact is None:
                raise AssertionError("INV-05: Outcome references missing Artifact")
            if artifact["outcome_id"] != outcome["outcome_id"]:
                raise AssertionError("INV-05: Artifact belongs to a different Outcome")
            if artifact_id in artifact_owners:
                raise AssertionError("INV-05: Artifact belongs to multiple Outcomes")
            artifact_owners[artifact_id] = outcome["outcome_id"]

    for evaluation in evaluations.values():
        outcome = outcomes.get(evaluation["outcome_id"])
        if outcome is None:
            raise AssertionError("Evaluation references missing Outcome")
        if evaluation["evaluation_id"] not in outcome.get("evaluation_ids", []):
            raise AssertionError("Outcome/Evaluation back references disagree")

    def parse(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    for execution in executions.values():
        if not (
            parse(execution["created_at"])
            <= parse(execution["started_at"])
            <= parse(execution["finished_at"])
        ):
            raise AssertionError("INV-13 subset: invalid Execution timestamp order")
        outcome = outcomes[execution["outcome_id"]]
        if parse(outcome["measured_at"]) < parse(execution["finished_at"]):
            raise AssertionError("INV-13 subset: Outcome measured before Execution finished")


def run_demo(user_rating: int | None = 5) -> dict[str, Any]:
    runtime = MarketingThinRuntime()
    return runtime.run(
        "윈터스쿨 모집을 위한 조사 근거가 있는 마케팅 문서를 작성하고 최종 검수까지 완료한다",
        user_rating=user_rating,
    )


def summary_json(bundle: dict[str, Any]) -> str:
    final_id = bundle["final_artifact_id"]
    summary = {
        "goal_id": bundle["goal"]["goal_id"],
        "task_route": [
            {
                "task_id": task["id"],
                "task_type": task["task_type"],
                "resource_id": task["assigned_resource_id"],
            }
            for task in bundle["tasks"]
        ],
        "final_artifact_id": final_id,
        "final_evaluation": bundle["evaluations"][-1]["scores"],
        "final_verdict": bundle["evaluations"][-1]["verdict"],
    }
    return json.dumps(summary, ensure_ascii=False, indent=2)
