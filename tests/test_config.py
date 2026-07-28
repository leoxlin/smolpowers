import json
import os
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
LOADER = ROOT / "skills/smol-activate/scripts/load-config.sh"


def defaults(project: Path) -> dict:
    return {
        "docsRoot": str(project / "docs/superpowers"),
        "stateRoot": str(project / ".superpowers"),
        "phases": {
            "design": {
                "owner": "smolpowers:smol-design",
                "companions": [],
            },
            "plan": {
                "owner": "smolpowers:smol-plan",
                "companions": [],
            },
            "execute": {
                "owner": "smolpowers:smol-execute",
                "companions": [],
                "tdd": "proportional",
            },
            "finish": {
                "owner": "smolpowers:smol-finish",
                "companions": [],
            },
        },
    }


def load(project: Path, *, path: str | None = None) -> tuple[dict, str]:
    env = os.environ.copy()
    if path is not None:
        env["PATH"] = path
    result = subprocess.run(
        ["/bin/bash", str(LOADER), str(project)],
        capture_output=True,
        check=True,
        env=env,
        text=True,
    )
    return json.loads(result.stdout), result.stderr


def write_config(project: Path, content: str) -> None:
    project.mkdir()
    (project / ".smolpowers.yml").write_text(content)


def test_absent_config_uses_defaults(tmp_path: Path) -> None:
    project = tmp_path / "absent"
    project.mkdir()
    actual, stderr = load(project)
    assert actual == defaults(project)
    assert stderr == ""


def test_json_config_is_ignored(tmp_path: Path) -> None:
    project = tmp_path / "json-only"
    project.mkdir()
    (project / ".smolpowers.json").write_text('{"docsRoot":"ignored"}\n')
    actual, stderr = load(project)
    assert actual == defaults(project)
    assert stderr == ""


def test_relative_roots_are_resolved(tmp_path: Path) -> None:
    project = tmp_path / "relative"
    write_config(project, "docsRoot: notes/work\nstateRoot: var/smol\n")
    actual, stderr = load(project)
    expected = defaults(project)
    expected["docsRoot"] = str(project / "notes/work")
    expected["stateRoot"] = str(project / "var/smol")
    assert actual == expected
    assert stderr == ""


def test_nested_phase_configuration(tmp_path: Path) -> None:
    project = tmp_path / "preferred"
    write_config(
        project,
        """\
phases:
  design:
    owner: superpowers:brainstorming
  execute:
    owner: smolpowers:smol-execute
    companions:
      - superpowers:test-driven-development
    tdd: strict
  finish:
    owner: superpowers:finishing-a-development-branch
    companions: []
""",
    )
    actual, stderr = load(project)
    assert actual["phases"]["design"] == {
        "owner": "superpowers:brainstorming",
        "companions": [],
    }
    assert actual["phases"]["plan"] == {
        "owner": "smolpowers:smol-plan",
        "companions": [],
    }
    assert actual["phases"]["execute"] == {
        "owner": "smolpowers:smol-execute",
        "companions": ["superpowers:test-driven-development"],
        "tdd": "strict",
    }
    assert actual["phases"]["finish"] == {
        "owner": "superpowers:finishing-a-development-branch",
        "companions": [],
    }
    assert stderr == ""


def test_partial_nested_phase_uses_defaults(tmp_path: Path) -> None:
    project = tmp_path / "preferred-partial"
    write_config(
        project,
        """\
phases:
  execute:
    companions:
      - superpowers:test-driven-development
""",
    )
    actual, stderr = load(project)
    assert actual["phases"]["execute"] == {
        "owner": "smolpowers:smol-execute",
        "companions": ["superpowers:test-driven-development"],
        "tdd": "proportional",
    }
    assert stderr == ""


def test_legacy_phase_owners(tmp_path: Path) -> None:
    project = tmp_path / "legacy-owners"
    write_config(
        project,
        """\
design: superpowers:brainstorming
finish: superpowers:finishing-a-development-branch
""",
    )
    actual, stderr = load(project)
    assert actual["phases"]["design"] == {
        "owner": "superpowers:brainstorming",
        "companions": [],
    }
    assert actual["phases"]["plan"]["owner"] == "smolpowers:smol-plan"
    assert actual["phases"]["execute"]["owner"] == "smolpowers:smol-execute"
    assert actual["phases"]["finish"] == {
        "owner": "superpowers:finishing-a-development-branch",
        "companions": [],
    }
    assert stderr == ""


def test_legacy_phase_chain(tmp_path: Path) -> None:
    project = tmp_path / "legacy-chain"
    write_config(
        project,
        """\
execute:
  - superpowers:test-driven-development
  - smolpowers:smol-execute
""",
    )
    actual, stderr = load(project)
    assert actual["phases"]["execute"] == {
        "owner": "smolpowers:smol-execute",
        "companions": ["superpowers:test-driven-development"],
        "tdd": "proportional",
    }
    assert stderr == ""


def test_legacy_strict_tdd(tmp_path: Path) -> None:
    project = tmp_path / "legacy-tdd-strict"
    write_config(project, "tdd: strict\n")
    actual, stderr = load(project)
    assert actual["phases"]["execute"]["tdd"] == "strict"
    assert stderr == ""


def test_absolute_roots_are_preserved(tmp_path: Path) -> None:
    project = tmp_path / "absolute"
    write_config(project, "docsRoot: /tmp/smol-docs\nstateRoot: /tmp/smol-state\n")
    actual, stderr = load(project)
    expected = defaults(project)
    expected["docsRoot"] = "/tmp/smol-docs"
    expected["stateRoot"] = "/tmp/smol-state"
    assert actual == expected
    assert stderr == ""


INVALID_CONFIGS = {
    "malformed": "phases:\n  execute: [unclosed\n",
    "unknown": '{"docsRoot":"docs","surprise":"value"}\n',
    "atomic": '{"docsRoot":"custom","stateRoot":""}\n',
    "unsafe": '{"docsRoot":"bad\\npath","stateRoot":"custom"}\n',
    "legacy-invalid-owner": '{"design":""}\n',
    "legacy-empty-chain": '{"execute":[]}\n',
    "legacy-non-string-member": '{"execute":["smolpowers:smol-execute",42]}\n',
    "legacy-empty-member": '{"execute":["","smolpowers:smol-execute"]}\n',
    "legacy-invalid-tdd": '{"tdd":"sometimes"}\n',
    "mixed-shapes": '{"execute":"smolpowers:smol-execute","phases":{}}\n',
    "unknown-phase": '{"phases":{"deploy":{"owner":"example:deploy"}}}\n',
    "unknown-phase-property": '{"phases":{"design":{"mode":"fast"}}}\n',
    "empty-owner": '{"phases":{"design":{"owner":""}}}\n',
    "non-array-companions": (
        '{"phases":{"execute":{"companions":"example:tdd"}}}\n'
    ),
    "non-string-companion": '{"phases":{"execute":{"companions":[42]}}}\n',
    "empty-companion": '{"phases":{"execute":{"companions":[""]}}}\n',
    "misplaced-tdd": '{"phases":{"design":{"tdd":"strict"}}}\n',
    "invalid-nested-tdd": '{"phases":{"execute":{"tdd":"sometimes"}}}\n',
    "phases-scalar": "phases: execute\n",
    "multiple-documents": "docsRoot: first\n---\ndocsRoot: second\n",
}


@pytest.mark.parametrize(("name", "content"), INVALID_CONFIGS.items())
def test_invalid_config_falls_back_atomically(
    tmp_path: Path, name: str, content: str
) -> None:
    project = tmp_path / name
    write_config(project, content)
    actual, stderr = load(project)
    assert actual == defaults(project)
    assert len(stderr.splitlines()) == 1


def test_missing_yq_falls_back_to_defaults(tmp_path: Path) -> None:
    project = tmp_path / "no-yq"
    write_config(project, "docsRoot: custom\nstateRoot: state\n")
    actual, stderr = load(project, path="/nonexistent")
    assert actual == defaults(project)
    assert len(stderr.splitlines()) == 1
