import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def project_shell_files() -> list[Path]:
    return [
        path
        for path in sorted((ROOT / "tests").rglob("*.sh"))
        if ".venv" not in path.parts and "jobs" not in path.parts
    ]


def shell_files() -> list[Path]:
    return [
        ROOT / "hooks/session-start",
        ROOT / "hooks/run-hook.cmd",
        ROOT / "skills/smol-activate/scripts/load-config.sh",
        *project_shell_files(),
    ]


def test_shell_syntax() -> None:
    subprocess.run(["bash", "-n", *map(str, shell_files())], check=True)


def test_shellcheck() -> None:
    shellcheck = shutil.which("shellcheck")
    if not shellcheck:
        pytest.skip("shellcheck is not installed")
    checked = [
        ROOT / "hooks/session-start",
        ROOT / "skills/smol-activate/scripts/load-config.sh",
        *project_shell_files(),
    ]
    subprocess.run([shellcheck, *map(str, checked)], check=True)
