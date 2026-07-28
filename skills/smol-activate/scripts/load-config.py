# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

import argparse
import json
import subprocess
import sys
from pathlib import Path, PureWindowsPath


DEFAULT_SPEC = "docs/superpowers"
DEFAULT_STATE = ".superpowers"
DEFAULT_ACTIVATION = "full"
DEFAULT_TDD = "proportional"
DEFAULT_OWNERS = {
    "design": "smolpowers:smol-design",
    "plan": "smolpowers:smol-plan",
    "execute": "smolpowers:smol-execute",
    "finish": "smolpowers:smol-finish",
}
PHASES = tuple(DEFAULT_OWNERS)
WARNING = "smolpowers: invalid configuration; using defaults"


def resolve_path(repo_root: Path, value: str) -> str:
    if Path(value).is_absolute() or PureWindowsPath(value).is_absolute():
        return value
    return str(repo_root / value)


def default_phases() -> dict:
    phases = {
        name: {"owner": owner, "companions": []}
        for name, owner in DEFAULT_OWNERS.items()
    }
    phases["execute"]["tdd"] = DEFAULT_TDD
    return phases


def safe_string(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and not any(character in value for character in "\0\n\r")
    )


def validate_phase(value: object, allow_tdd: bool) -> bool:
    if not isinstance(value, dict):
        return False
    allowed = {"owner", "companions"} | ({"tdd"} if allow_tdd else set())
    companions = value.get("companions")
    return (
        set(value) <= allowed
        and (value.get("owner") is None or safe_string(value["owner"]))
        and (
            companions is None
            or (
                isinstance(companions, list)
                and all(safe_string(companion) for companion in companions)
            )
        )
        and (
            not allow_tdd
            or value.get("tdd") is None
            or value["tdd"] in ("proportional", "strict")
        )
    )


def validate(config: object) -> None:
    legacy_keys = set(PHASES) | {"tdd"}
    allowed = legacy_keys | {
        "activation",
        "specDir",
        "phases",
        "stateDir",
    }
    if not isinstance(config, dict) or not set(config) <= allowed:
        raise ValueError
    if config.get("activation") not in (None, "lite", "full", "ultra"):
        raise ValueError
    if not all(
        config.get(name) is None or safe_string(config[name])
        for name in ("specDir", "stateDir")
    ):
        raise ValueError

    if "phases" in config:
        phases = config["phases"]
        if legacy_keys & set(config) or not isinstance(phases, dict):
            raise ValueError
        if not set(phases) <= set(PHASES):
            raise ValueError
        if not all(
            name not in phases
            or validate_phase(phases[name], name == "execute")
            for name in PHASES
        ):
            raise ValueError
        return

    for name in PHASES:
        value = config.get(name)
        if value is None:
            continue
        if safe_string(value):
            continue
        if (
            not isinstance(value, list)
            or not value
            or not all(safe_string(member) for member in value)
        ):
            raise ValueError
    if config.get("tdd") not in (None, "proportional", "strict"):
        raise ValueError


def normalize_phases(config: dict) -> dict:
    if "phases" in config:
        normalized = default_phases()
        for name, phase in config["phases"].items():
            normalized[name]["owner"] = phase.get("owner") or DEFAULT_OWNERS[name]
            normalized[name]["companions"] = phase.get("companions") or []
            if name == "execute":
                normalized[name]["tdd"] = phase.get("tdd") or DEFAULT_TDD
        return normalized

    normalized = default_phases()
    for name in PHASES:
        value = config.get(name)
        if value is None:
            continue
        if isinstance(value, list):
            normalized[name]["owner"] = value[-1]
            normalized[name]["companions"] = value[:-1]
        else:
            normalized[name]["owner"] = value
    normalized["execute"]["tdd"] = config.get("tdd") or DEFAULT_TDD
    return normalized


def normalize(repo_root: Path, config: dict) -> dict:
    return {
        "specDir": resolve_path(
            repo_root, config.get("specDir") or DEFAULT_SPEC
        ),
        "stateDir": resolve_path(
            repo_root, config.get("stateDir") or DEFAULT_STATE
        ),
        "activation": config.get("activation") or DEFAULT_ACTIVATION,
        "phases": normalize_phases(config),
    }


def reject_nonstandard_constant(value: str) -> None:
    raise ValueError(f"invalid JSON constant: {value}")


def load(repo_root: Path) -> tuple[dict, bool]:
    config_file = repo_root / ".smolpowers.json"
    if not config_file.is_file():
        return normalize(repo_root, {}), False
    try:
        config = json.loads(
            config_file.read_text(), parse_constant=reject_nonstandard_constant
        )
        validate(config)
        return normalize(repo_root, config), False
    except (OSError, ValueError):
        return normalize(repo_root, {}), True


def repository_root(value: str | None) -> Path:
    if value is not None:
        root = Path(value).resolve(strict=True)
        if not root.is_dir():
            raise NotADirectoryError(value)
        return root
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        check=True,
        text=True,
    )
    return Path(result.stdout.strip()).resolve(strict=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load and normalize Smolpowers configuration."
    )
    parser.add_argument("repo_root", nargs="?")
    args = parser.parse_args()

    config, warned = load(repository_root(args.repo_root))
    if warned:
        print(WARNING, file=sys.stderr)
    json.dump(config, sys.stdout, ensure_ascii=False, separators=(",", ":"))
    print()


if __name__ == "__main__":
    main()
