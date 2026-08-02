"""Verify activation decisions and write the Harbor reward."""

import json
import traceback
from pathlib import Path


ROOT = Path("/app")
BASELINE = Path("/opt/fixture")
EXPECTED = {
    "explicit-activation": True,
    "explicit-opt-out": False,
    "analysis-only": False,
    "documentation-only": False,
    "tests-only": False,
    "git-only": False,
    "mechanical-correction": False,
    "configuration-schema": True,
    "interface-refactor": True,
}


def verify() -> None:
    actual = json.loads((ROOT / "activation-results.json").read_text())
    decisions = actual.get("decisions")
    assert isinstance(decisions, list), actual
    assert all(
        isinstance(item, dict)
        and isinstance(item.get("id"), str)
        and isinstance(item.get("activate"), bool)
        for item in decisions
    ), decisions

    actual_by_id = {item["id"]: item["activate"] for item in decisions}
    assert len(actual_by_id) == len(decisions), decisions
    assert actual_by_id == EXPECTED, actual_by_id

    for name in [".smolpowers.json", "activation-cases.json"]:
        assert (ROOT / name).read_bytes() == (BASELINE / name).read_bytes(), name

    changed = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.iterdir()
        if path.name != ".git" and not (BASELINE / path.name).exists()
    }
    assert changed == {"activation-results.json"}, changed


def main() -> None:
    reward = 1
    try:
        verify()
    except Exception:
        traceback.print_exc()
        reward = 0
    output = Path("/logs/verifier/reward.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"reward": reward}))


if __name__ == "__main__":
    main()
