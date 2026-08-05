import json
import os
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
        "specTemplate": None,
        "planTemplate": None,
        "activation": "manual",
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


def load(
    project: Path,
    environment: dict[str, str] | None = None,
    home: Path | None = None,
) -> tuple[dict, str]:
    process_environment = os.environ.copy()
    home = home or project.parent / "home"
    home.mkdir(exist_ok=True)
    process_environment["HOME"] = str(home)
    process_environment.update(environment or {})
    result = subprocess.run(
        [sys.executable, str(LOADER), str(project)],
        capture_output=True,
        check=True,
        env=process_environment,
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


def test_user_level_config_merges_with_defaults(tmp_path: Path) -> None:
    home = tmp_path / "user"
    write_config(
        home,
        '{"designDir":"shared/designs","phases":{"execute":{"tdd":"strict"}}}\n',
    )
    project = tmp_path / "project"
    project.mkdir()

    actual, stderr = load(project, home=home)

    expected = defaults()
    expected["designDir"] = "shared/designs"
    expected["phases"]["execute"]["tdd"] = "strict"
    assert actual == expected
    assert stderr == ""


def test_repository_config_has_priority_over_user_level_config(
    tmp_path: Path,
) -> None:
    home = tmp_path / "user"
    write_config(
        home,
        """
        {
            "activation": "always",
            "phases": {
                "execute": {"skills": ["user-execute"], "tdd": "strict"},
                "finish": {"commit": "user commit"}
            }
        }
        """,
    )
    project = tmp_path / "project"
    write_config(
        project,
        """
        {
            "activation": "important",
            "phases": {
                "execute": {"skills": ["project-execute"]},
                "finish": {"push": "project push"}
            }
        }
        """,
    )

    actual, stderr = load(project, home=home)

    expected = defaults()
    expected["activation"] = "important"
    expected["phases"]["execute"] = {
        "skills": ["project-execute"],
        "tdd": "strict",
    }
    expected["phases"]["finish"] = {
        "skills": ["smol-finish"],
        "commit": "user commit",
        "push": "project push",
    }
    assert actual == expected
    assert stderr == ""


def test_config_path_replaces_repository_config(tmp_path: Path) -> None:
    project = tmp_path / "project"
    write_config(project, '{"activation":"always"}\n')
    selected_file = tmp_path / "selected.json"
    selected_file.write_text('{"designDir":"selected/designs"}\n')

    actual, stderr = load(
        project,
        {"SMOL_CONFIG_PATH": str(selected_file)},
    )

    expected = defaults()
    expected["designDir"] = "selected/designs"
    assert actual == expected
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
                },
                "finish": {
                    "commit": "commit the verified change",
                    "push": "push the current branch"
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
    expected["phases"]["finish"] = {
        "skills": ["smol-finish"],
        "commit": "commit the verified change",
        "push": "push the current branch",
    }
    assert actual == expected
    assert stderr == ""


def test_environment_overrides_all_config_values(tmp_path: Path) -> None:
    project = tmp_path / "environment"
    project.mkdir()
    actual, stderr = load(
        project,
        {
            "SMOL_DESIGN_DIR": "env/designs",
            "SMOL_PLAN_DIR": "env/plans",
            "SMOL_SPEC_TEMPLATE": "env/spec.md",
            "SMOL_PLAN_TEMPLATE": "env/plan.md",
            "SMOL_ACTIVATION": "always",
            "SMOL_PHASES_DESIGN_SKILLS": "brainstorming,smol-design",
            "SMOL_PHASES_PLAN_SKILLS": "writing-plans",
            "SMOL_PHASES_EXECUTE_SKILLS": ("test-driven-development,smol-execute"),
            "SMOL_PHASES_EXECUTE_TDD": "strict",
            "SMOL_PHASES_FINISH_SKILLS": ("finishing-a-development-branch"),
            "SMOL_PHASES_FINISH_COMMIT": "commit with the repository convention",
            "SMOL_PHASES_FINISH_PUSH": "push the current branch",
        },
    )
    assert actual == {
        "designDir": "env/designs",
        "planDir": "env/plans",
        "specTemplate": "env/spec.md",
        "planTemplate": "env/plan.md",
        "activation": "always",
        "phases": {
            "design": {"skills": ["brainstorming", "smol-design"]},
            "plan": {"skills": ["writing-plans"]},
            "execute": {
                "skills": ["test-driven-development", "smol-execute"],
                "tdd": "strict",
            },
            "finish": {
                "skills": ["finishing-a-development-branch"],
                "commit": "commit with the repository convention",
                "push": "push the current branch",
            },
        },
    }
    assert stderr == ""


def test_environment_has_priority_over_file(tmp_path: Path) -> None:
    home = tmp_path / "home-config"
    write_config(home, '{"activation":"manual","designDir":"user/designs"}\n')
    project = tmp_path / "priority"
    write_config(
        project,
        """
        {
            "designDir": "file/designs",
            "planDir": "file/plans",
            "specTemplate": "file/spec.md",
            "planTemplate": "file/plan.md",
            "activation": "manual",
            "phases": {
                "design": {"skills": ["file-design"]},
                "plan": {"skills": ["file-plan"]},
                "execute": {"skills": ["file-execute"], "tdd": "proportional"},
                "finish": {
                    "skills": ["file-finish"],
                    "commit": "file commit",
                    "push": "file push"
                }
            }
        }
        """,
    )
    actual, stderr = load(
        project,
        {
            "HOME": str(home),
            "SMOL_DESIGN_DIR": "env/designs",
            "SMOL_PLAN_DIR": "env/plans",
            "SMOL_SPEC_TEMPLATE": "env/spec.md",
            "SMOL_PLAN_TEMPLATE": "env/plan.md",
            "SMOL_ACTIVATION": "always",
            "SMOL_PHASES_DESIGN_SKILLS": "env-design",
            "SMOL_PHASES_PLAN_SKILLS": "env-plan",
            "SMOL_PHASES_EXECUTE_SKILLS": "env-check,env-execute",
            "SMOL_PHASES_EXECUTE_TDD": "strict",
            "SMOL_PHASES_FINISH_SKILLS": "env-finish",
            "SMOL_PHASES_FINISH_COMMIT": "env commit",
            "SMOL_PHASES_FINISH_PUSH": "env push",
        },
    )
    assert actual == {
        "designDir": "env/designs",
        "planDir": "env/plans",
        "specTemplate": "env/spec.md",
        "planTemplate": "env/plan.md",
        "activation": "always",
        "phases": {
            "design": {"skills": ["env-design"]},
            "plan": {"skills": ["env-plan"]},
            "execute": {
                "skills": ["env-check", "env-execute"],
                "tdd": "strict",
            },
            "finish": {
                "skills": ["env-finish"],
                "commit": "env commit",
                "push": "env push",
            },
        },
    }
    assert stderr == ""


@pytest.mark.parametrize("activation", ["manual", "important", "always"])
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


def test_malformed_user_level_json_warns_and_uses_defaults(tmp_path: Path) -> None:
    home = tmp_path / "user"
    write_config(home, "{not json\n")
    project = tmp_path / "project"
    write_config(project, '{"activation":"always"}\n')

    actual, stderr = load(
        project,
        {"SMOL_DESIGN_DIR": "env/designs"},
        home=home,
    )

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
