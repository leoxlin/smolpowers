"""Pure lifecycle evaluation shared by Harbor verifiers and reporting."""

import json
import re


SKILL_PATH_RE = re.compile(r"(?<![\w.-])skills[/\\]([\w.-]+)[/\\]SKILL\.md\b")
EXPECTED_SKILLS = {
    "codex-smol": [
        "smol-activate",
        "smol-design",
        "smol-plan",
        "smol-execute",
        "smol-finish",
    ],
    "codex-mix": [
        "smol-activate",
        "smol-design",
        "writing-plans",
        "test-driven-development",
        "smol-execute",
        "smol-finish",
    ],
    "kimi-code-smol": [
        "smol-activate",
        "smol-design",
        "smol-plan",
        "smol-execute",
        "smol-finish",
    ],
    "kimi-code-mix": [
        "smol-activate",
        "smol-design",
        "writing-plans",
        "test-driven-development",
        "smol-execute",
        "smol-finish",
    ],
}


def _canonical_skill(value: str) -> str:
    return value.rsplit(":", 1)[-1]


def _is_skill_tool(function_name: str) -> bool:
    return re.split(r"__|\.", function_name)[-1].lower() == "skill"


def activation_evidence(trajectory: dict) -> list[dict]:
    evidence = []
    for step in trajectory.get("steps") or []:
        for call in step.get("tool_calls") or []:
            arguments = call.get("arguments") or {}
            if _is_skill_tool(str(call.get("function_name") or "")):
                value = arguments.get("skill") or arguments.get("name")
                if isinstance(value, str):
                    evidence.append(
                        {
                            "skill": _canonical_skill(value),
                            "step_id": step.get("step_id"),
                            "source": "tool",
                        }
                    )
            argument_text = json.dumps(arguments, ensure_ascii=False)
            evidence.extend(
                {
                    "skill": match.group(1),
                    "step_id": step.get("step_id"),
                    "source": "path",
                }
                for match in SKILL_PATH_RE.finditer(argument_text)
            )
    return evidence


def evaluate_lifecycle(trajectory: dict, expected: list | tuple) -> dict:
    expected = list(expected)
    observed = activation_evidence(trajectory)
    first_positions = {}
    for index, item in enumerate(observed):
        first_positions.setdefault(item["skill"], (index, item["step_id"]))
    missing = [skill for skill in expected if skill not in first_positions]

    def before_or_same(left, right) -> bool:
        return left[0] <= right[0] or (left[1] is not None and left[1] == right[1])

    present = [
        first_positions[skill] for skill in expected if skill in first_positions
    ]
    ordered = all(
        before_or_same(left, right)
        for left, right in zip(present, present[1:])
    )
    return {
        "expected": expected,
        "observed": observed,
        "missing": missing,
        "passed": not missing and ordered,
    }


def normalize_checks(values: dict | None) -> dict:
    values = values or {}
    if "skills_in_order" in values or "requested_change_completed" in values:
        skills = values.get("skills_in_order")
        requested = values.get("requested_change_completed")
        return {
            "kind": "named",
            "skills_in_order": skills,
            "requested_change_completed": requested,
            "passed": skills == requested == 1,
        }
    if "reward" in values:
        return {
            "kind": "legacy",
            "skills_in_order": None,
            "requested_change_completed": None,
            "passed": values["reward"] == 1,
        }
    return {
        "kind": "missing",
        "skills_in_order": None,
        "requested_change_completed": None,
        "passed": False,
    }
