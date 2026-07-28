import os
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
COMPATIBILITY = ROOT / "skills/smol-activate/references/compatibility.md"


def test_upstream_contract_documentation() -> None:
    compatibility = COMPATIBILITY.read_text()
    for token in ("workflow_owner", "output_path", "tracked_artifact", "return_to_caller"):
        assert token in compatibility
    assert "| `superpowers:subagent-driven-development` | Execute |" in compatibility
    assert "| `superpowers:executing-plans` | Execute and Finish |" in compatibility
    assert "superpowers:test-driven-development" in compatibility
    assert "companion" in compatibility

    for skill in (
        "smol-activate",
        "smol-design",
        "smol-plan",
        "smol-execute",
        "smol-finish",
    ):
        assert "phase object" in (ROOT / f"skills/{skill}/SKILL.md").read_text()

    readme = (ROOT / "README.md").read_text()
    for token in (
        "superpowers:test-driven-development",
        "smolpowers:smol-execute",
        "phases:",
        "owner:",
        "companions:",
    ):
        assert token in readme


def test_actual_upstream_substitution(tmp_path: Path) -> None:
    upstream_root = Path(
        os.environ.get("SUPERPOWERS_ROOT", ROOT.parent / "superpowers")
    )
    task_brief = upstream_root / (
        "skills/subagent-driven-development/scripts/task-brief"
    )
    if not task_brief.is_file() or not os.access(task_brief, os.X_OK):
        pytest.skip("set SUPERPOWERS_ROOT to an upstream Superpowers checkout")

    for skill in ("brainstorming", "writing-plans", "subagent-driven-development"):
        contents = (upstream_root / f"skills/{skill}/SKILL.md").read_text()
        assert "workflow_owner" in contents
        assert "return_to_caller" in contents

    for skill in ("brainstorming", "writing-plans"):
        contents = (upstream_root / f"skills/{skill}/SKILL.md").read_text()
        assert "output_path" in contents
        assert "tracked_artifact" in contents

    template = (ROOT / "skills/smol-plan/references/plan-template.md").read_text()
    plan = tmp_path / "plan.md"
    brief = tmp_path / "task-1.md"
    plan.write_text(template.replace("Task N", "Task 1"))
    subprocess.run(
        [str(task_brief), str(plan), "1", str(brief)],
        capture_output=True,
        check=True,
        text=True,
    )
    contents = brief.read_text()
    assert "### Task 1:" in contents
    assert "**Files:**" in contents
    assert "**Outcome:**" in contents
