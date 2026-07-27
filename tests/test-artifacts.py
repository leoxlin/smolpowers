#!/usr/bin/env python3
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
template = (ROOT / "skills/design/references/plan-template.md").read_text()

for heading in [
    "# [Feature Name] Implementation Plan",
    "**Goal:**",
    "**Architecture:**",
    "## Global Constraints",
    "### Task N:",
    "**Files:**",
    "**Outcome:**",
    "- [ ]",
    "Run:",
]:
    assert heading in template, f"plan template misses {heading}"

spec_template = (ROOT / "skills/plan/references/spec-template.md").read_text()
for heading in ["# [Feature Name] Design", "## Goal", "## Success", "## Scope"]:
    assert heading in spec_template, f"spec template misses {heading}"

with tempfile.TemporaryDirectory() as tmp:
    sample = Path(tmp) / "sample.md"
    sample.write_text(template.replace("Task N", "Task 1"))
    result = subprocess.run(
        ["bash", str(ROOT / "tests/upstream-task-parser.sh"), str(sample), "1"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.startswith("### Task 1:"), "upstream parser could not find task"
    assert "**Files:**" in result.stdout and "**Outcome:**" in result.stdout

    default_repo = Path(tmp) / "default"
    default_repo.mkdir()
    output = subprocess.check_output(
        [
            "bash",
            str(ROOT / "skills/using-smolpowers/scripts/load-config.sh"),
            str(default_repo),
        ],
        text=True,
    )
    config = json.loads(output)
    assert Path(config["docsRoot"]) / "specs/2026-07-27-example-design.md" == (
        default_repo / "docs/superpowers/specs/2026-07-27-example-design.md"
    )
    assert Path(config["docsRoot"]) / "plans/2026-07-27-example.md" == (
        default_repo / "docs/superpowers/plans/2026-07-27-example.md"
    )

    custom_repo = Path(tmp) / "custom"
    custom_repo.mkdir()
    (custom_repo / ".smolpowers.json").write_text(
        '{"docsRoot":"project-notes","stateRoot":"/tmp/smol-state"}\n'
    )
    output = subprocess.check_output(
        [
            "bash",
            str(ROOT / "skills/using-smolpowers/scripts/load-config.sh"),
            str(custom_repo),
        ],
        text=True,
    )
    config = json.loads(output)
    assert Path(config["docsRoot"]) / "specs/2026-07-27-example-design.md" == (
        custom_repo / "project-notes/specs/2026-07-27-example-design.md"
    )
    assert config["stateRoot"] == "/tmp/smol-state"

print("Artifact templates, paths, and upstream task parsing look good")
