"""Verify the lifecycle and requested change, then write Harbor rewards."""

# pyright: reportMissingImports=false

import json
import re
import sqlite3
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

ROOT = Path("/app")
BASELINE = Path("/opt/fixture")
CONFIG = ROOT / ".smolpowers.json"
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
    "kimi-smol": [
        "smol-activate",
        "smol-design",
        "smol-plan",
        "smol-execute",
        "smol-finish",
    ],
    "kimi-mix": [
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

    present = [first_positions[skill] for skill in expected if skill in first_positions]
    ordered = all(
        before_or_same(left, right) for left, right in zip(present, present[1:])
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


def verify_lifecycle() -> None:
    trajectory = json.loads(Path("/logs/agent/trajectory.json").read_text())
    agent_name = trajectory["agent"]["name"]
    expected = EXPECTED_SKILLS.get(agent_name)
    if expected is None:
        print(f"No lifecycle expectation for agent {agent_name}; check skipped.")
        return
    result = evaluate_lifecycle(trajectory, expected)
    print(json.dumps(result, indent=2))
    assert result["passed"], result


def only_match(directory: Path, pattern: str) -> Path:
    matches = list(directory.glob(pattern))
    assert len(matches) == 1, matches
    return matches[0]


def verify_requested_change() -> None:
    subprocess.run(
        ["python", "-m", "unittest", "discover", "-s", "tests"],
        cwd=ROOT,
        check=True,
    )

    sys.path.insert(0, str(ROOT))
    from app import create_app

    with tempfile.TemporaryDirectory() as directory:
        database = Path(directory) / "links.sqlite3"
        first_client = create_app({"TESTING": True, "DATABASE": database}).test_client()
        link = first_client.post(
            "/links", json={"url": "https://example.com/persistent"}
        ).get_json()
        with sqlite3.connect(database) as connection:
            saved_link = connection.execute("SELECT code, url FROM links").fetchone()
        assert saved_link == (link["code"], link["url"])
        restarted_client = create_app(
            {"TESTING": True, "DATABASE": database}
        ).test_client()
        response = restarted_client.get(f"/{link['code']}")
        assert response.status_code == 302
        assert response.headers["Location"] == link["url"]

    config = json.loads(CONFIG.read_text()) if CONFIG.exists() else {}
    designs = ROOT / config.get("designDir", "docs/superpowers/specs")
    plans = ROOT / config.get("planDir", "docs/superpowers/plans")
    spec = only_match(designs, "*-design.md")
    plan = only_match(plans, "*.md")
    assert plan.stem == spec.stem.removesuffix("-design")
    assert (ROOT / "app.py").read_bytes() != (BASELINE / "app.py").read_bytes()

    phase_log = ROOT / ".smol-state" / "phase-calls.log"
    if phase_log.exists():
        calls = phase_log.read_text().splitlines()
        configured_overrides = [
            name
            for name, phase in config.get("phases", {}).items()
            if phase.get("skills") and phase["skills"][-1].startswith("integration-")
        ]
        assert [call.split("|", 1)[0] for call in calls] == configured_overrides
        expected_roots = f"|{designs}|{plans}"
        assert all(call.endswith(expected_roots) for call in calls)


def check(function) -> int:
    try:
        function()
    except Exception:
        traceback.print_exc()
        return 0
    return 1


def main() -> None:
    rewards = {
        "skills_in_order": check(verify_lifecycle),
        "requested_change_completed": check(verify_requested_change),
    }
    output = Path("/logs/verifier/reward.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(rewards))


if __name__ == "__main__":
    main()
