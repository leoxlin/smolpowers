import os
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def test_actual_upstream_substitution(tmp_path: Path) -> None:
    upstream_root = Path(
        os.environ.get("SUPERPOWERS_ROOT", ROOT.parent / "superpowers")
    )
    task_brief = upstream_root / (
        "skills/subagent-driven-development/scripts/task-brief"
    )
    if not task_brief.is_file() or not os.access(task_brief, os.X_OK):
        pytest.skip("set SUPERPOWERS_ROOT to an upstream Superpowers checkout")

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
