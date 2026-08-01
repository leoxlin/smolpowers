import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LOADER = ROOT / "skills/smol-activate/scripts/load-config.py"


def defaults() -> dict:
    return {
        "designDir": "docs/superpowers/specs",
        "planDir": "docs/superpowers/plans",
        "activation": "default",
        "phases": {
            "design": {"skills": ["smol-design"]},
            "plan": {"skills": ["smol-plan"]},
            "execute": {
                "skills": ["smol-execute"],
                "tdd": "proportional",
            },
            "finish": {"skills": ["smol-finish"]},
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
    assert actual == defaults()
    assert stderr == ""


def test_user_config_merges_with_defaults(tmp_path: Path) -> None:
    project = tmp_path / "partial"
    write_config(
        project,
        """
        {
            "designDir": "notes/designs",
            "planDir":"notes/plans",
            "activation":"always",
            "phases": {
                "execute":{
                    "skills": ["test-driven-development", "smol-execute"],
                    "tdd": "strict"
                }
            }
        }
        """,
    )
    actual, stderr = load(project)
    expected = defaults()
    expected["designDir"] = "notes/designs"
    expected["planDir"] = "notes/plans"
    expected["activation"] = "always"
    expected["phases"]["execute"] = {
        "skills": ["test-driven-development", "smol-execute"],
        "tdd": "strict",
    }
    assert actual == expected
    assert stderr == ""


@pytest.mark.parametrize("activation", ["manual", "default", "always"])
def test_activation_value_is_preserved(tmp_path: Path, activation: str) -> None:
    project = tmp_path / activation
    write_config(project, f'{{"activation":"{activation}"}}\n')
    actual, stderr = load(project)
    assert actual["activation"] == activation
    assert stderr == ""


def test_user_keys_are_preserved(tmp_path: Path) -> None:
    project = tmp_path / "extra-keys"
    write_config(
        project,
        '{"extension":"value","phases":{"design":{"option":true}}}\n',
    )
    actual, stderr = load(project)
    assert actual["extension"] == "value"
    assert actual["phases"]["design"] == {
        "option": True,
        "skills": ["smol-design"],
    }
    assert stderr == ""


def test_malformed_json_warns_and_uses_defaults(tmp_path: Path) -> None:
    project = tmp_path / "malformed"
    write_config(project, "{not json\n")
    actual, stderr = load(project)
    assert actual == defaults()
    assert stderr.splitlines() == ["smolpowers: reading config failed, using defaults"]


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
