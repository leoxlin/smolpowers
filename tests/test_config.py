import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
LOADER = ROOT / "skills/smol-activate/scripts/load-config.py"


def defaults(project: Path) -> dict:
    return {
        "specDir": str(project / "docs/superpowers"),
        "stateDir": str(project / ".superpowers"),
        "activation": "full",
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


def load(project: Path) -> tuple[dict, str]:
    result = subprocess.run(
        [sys.executable, str(LOADER), str(project)],
        capture_output=True,
        check=True,
        text=True,
    )
    return json.loads(result.stdout), result.stderr


def write_config(project: Path, content: str) -> None:
    project.mkdir()
    (project / ".smolpowers.json").write_text(content)


def test_absent_config_uses_defaults(tmp_path: Path) -> None:
    project = tmp_path / "absent"
    project.mkdir()
    actual, stderr = load(project)
    assert actual == defaults(project)
    assert stderr == ""


def test_relative_dirs_are_resolved(tmp_path: Path) -> None:
    project = tmp_path / "relative"
    write_config(
        project, '{"specDir":"notes/work","stateDir":"var/smol"}\n'
    )
    actual, stderr = load(project)
    expected = defaults(project)
    expected["specDir"] = str(project / "notes/work")
    expected["stateDir"] = str(project / "var/smol")
    assert actual == expected
    assert stderr == ""


@pytest.mark.parametrize("activation", ["lite", "full", "ultra"])
def test_activation_level(tmp_path: Path, activation: str) -> None:
    project = tmp_path / activation
    write_config(project, f'{{"activation":"{activation}"}}\n')
    actual, stderr = load(project)
    assert actual["activation"] == activation
    assert stderr == ""


def test_nested_phase_configuration(tmp_path: Path) -> None:
    project = tmp_path / "preferred"
    write_config(
        project,
        '{"phases":{'
        '"design":{"owner":"superpowers:brainstorming"},'
        '"execute":{"owner":"smolpowers:smol-execute",'
        '"companions":["superpowers:test-driven-development"],"tdd":"strict"},'
        '"finish":{"owner":"superpowers:finishing-a-development-branch",'
        '"companions":[]}}}\n',
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
        '{"phases":{"execute":{'
        '"companions":["superpowers:test-driven-development"]}}}\n',
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
        '{"design":"superpowers:brainstorming",'
        '"finish":"superpowers:finishing-a-development-branch"}\n',
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
        '{"execute":["superpowers:test-driven-development",'
        '"smolpowers:smol-execute"]}\n',
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
    write_config(project, '{"tdd":"strict"}\n')
    actual, stderr = load(project)
    assert actual["phases"]["execute"]["tdd"] == "strict"
    assert stderr == ""


def test_absolute_dirs_are_preserved(tmp_path: Path) -> None:
    project = tmp_path / "absolute"
    write_config(
        project,
        '{"specDir":"/tmp/smol-docs","stateDir":"/tmp/smol-state"}\n',
    )
    actual, stderr = load(project)
    expected = defaults(project)
    expected["specDir"] = "/tmp/smol-docs"
    expected["stateDir"] = "/tmp/smol-state"
    assert actual == expected
    assert stderr == ""


INVALID_CONFIGS = {
    "malformed": "{not json\n",
    "unknown": '{"specDir":"docs","surprise":"value"}\n',
    "atomic": '{"specDir":"custom","stateDir":""}\n',
    "unsafe": '{"specDir":"bad\\npath","stateDir":"custom"}\n',
    "legacy-invalid-owner": '{"design":""}\n',
    "legacy-empty-chain": '{"execute":[]}\n',
    "legacy-non-string-member": '{"execute":["smolpowers:smol-execute",42]}\n',
    "legacy-empty-member": '{"execute":["","smolpowers:smol-execute"]}\n',
    "legacy-invalid-tdd": '{"tdd":"sometimes"}\n',
    "invalid-activation": '{"activation":"sometimes"}\n',
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
    "phases-scalar": '{"phases":"execute"}\n',
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


def test_pep_723_metadata() -> None:
    lines = LOADER.read_text().splitlines()
    start = lines.index("# /// script") + 1
    end = lines.index("# ///", start)
    metadata = tomllib.loads(
        "\n".join(line.removeprefix("# ") for line in lines[start:end])
    )
    assert metadata == {"requires-python": ">=3.11", "dependencies": []}


def test_omitted_repository_uses_git_repository() -> None:
    explicit = subprocess.run(
        [sys.executable, str(LOADER), str(ROOT)],
        capture_output=True,
        check=True,
        text=True,
    )
    discovered = subprocess.run(
        [sys.executable, str(LOADER)],
        capture_output=True,
        check=True,
        cwd=ROOT,
        text=True,
    )
    assert discovered.stdout == explicit.stdout
    assert discovered.stderr == ""


def test_rejects_extra_argument() -> None:
    result = subprocess.run(
        [sys.executable, str(LOADER), str(ROOT), "extra"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "usage:" in result.stderr


def test_runs_with_pipx(tmp_path: Path) -> None:
    project = tmp_path / "pipx"
    project.mkdir()
    result = subprocess.run(
        ["pipx", "run", str(LOADER), str(project)],
        capture_output=True,
        check=True,
        env=os.environ
        | {
            "PATH": str(Path(sys.executable).parent),
            "PIPX_HOME": str(tmp_path / "pipx-home"),
            "PIPX_BIN_DIR": str(tmp_path / "pipx-bin"),
        },
        text=True,
    )
    assert json.loads(result.stdout) == defaults(project)
    assert result.stderr == ""
