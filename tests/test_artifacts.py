import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def test_artifact_paths_follow_configuration(tmp_path: Path) -> None:
    default_repo = tmp_path / "default"
    default_repo.mkdir()
    output = subprocess.check_output(
        [
            "bash",
            str(ROOT / "skills/smol-activate/scripts/load-config.sh"),
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

    custom_repo = tmp_path / "custom"
    custom_repo.mkdir()
    (custom_repo / ".smolpowers.yml").write_text(
        "docsRoot: project-notes\nstateRoot: /tmp/smol-state\n"
    )
    output = subprocess.check_output(
        [
            "bash",
            str(ROOT / "skills/smol-activate/scripts/load-config.sh"),
            str(custom_repo),
        ],
        text=True,
    )
    config = json.loads(output)
    assert Path(config["docsRoot"]) / "specs/2026-07-27-example-design.md" == (
        custom_repo / "project-notes/specs/2026-07-27-example-design.md"
    )
    assert config["stateRoot"] == "/tmp/smol-state"
