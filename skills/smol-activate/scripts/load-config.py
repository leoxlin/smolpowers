import argparse
import json
import subprocess
import sys
from pathlib import Path, PureWindowsPath


DEFAULT_SPEC = "docs/superpowers"
DEFAULT_STATE = ".superpowers"
DEFAULT_ACTIVATION = "full"
DEFAULT_TDD = "proportional"
TDD_MODES = ("proportional", "strict")
DEFAULT_OWNERS = {
    "design": "smol-design",
    "plan": "smol-plan",
    "execute": "smol-execute",
    "finish": "smol-finish",
}
PHASES = tuple(DEFAULT_OWNERS)
LEGACY_KEYS = set(PHASES) | {"tdd"}
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


def normalize_skill(value: str) -> str:
    name = value.rpartition(":")[2]
    if not safe_string(name):
        raise ValueError
    return name


def to_nested(config: dict) -> dict:
    """Return phase configuration in nested form, converting legacy keys."""
    if "phases" in config:
        return config["phases"]
    phases = {}
    for name in PHASES:
        value = config.get(name)
        if value is None:
            continue
        if isinstance(value, str):
            phases[name] = {"owner": value}
        elif isinstance(value, list) and value:
            phases[name] = {"owner": value[-1], "companions": value[:-1]}
        else:
            raise ValueError
    if config.get("tdd") is not None:
        phases.setdefault("execute", {})["tdd"] = config["tdd"]
    return phases


def validate_phase(value: object, allow_tdd: bool) -> bool:
    if not isinstance(value, dict):
        return False
    allowed = {"owner", "companions"} | ({"tdd"} if allow_tdd else set())
    if not set(value) <= allowed:
        return False
    companions = value.get("companions")
    return (
        (value.get("owner") is None or safe_string(value["owner"]))
        and (
            companions is None
            or (
                isinstance(companions, list)
                and all(safe_string(companion) for companion in companions)
            )
        )
        and value.get("tdd") in (None, *TDD_MODES)
    )


def validate(config: object) -> None:
    allowed = LEGACY_KEYS | {"activation", "specDir", "phases", "stateDir"}
    if not isinstance(config, dict) or not set(config) <= allowed:
        raise ValueError
    if config.get("activation") not in (None, "lite", "full", "ultra"):
        raise ValueError
    if not all(
        config.get(name) is None or safe_string(config[name])
        for name in ("specDir", "stateDir")
    ):
        raise ValueError
    if config.get("tdd") not in (None, *TDD_MODES):
        raise ValueError
    if "phases" in config and LEGACY_KEYS & set(config):
        raise ValueError
    phases = to_nested(config)
    if not isinstance(phases, dict) or not set(phases) <= set(PHASES):
        raise ValueError
    if not all(
        name not in phases
        or validate_phase(phases[name], name == "execute")
        for name in PHASES
    ):
        raise ValueError


def normalize_phases(config: dict) -> dict:
    phases = default_phases()
    for name, phase in to_nested(config).items():
        phases[name]["owner"] = normalize_skill(
            phase.get("owner") or DEFAULT_OWNERS[name]
        )
        phases[name]["companions"] = [
            normalize_skill(companion)
            for companion in phase.get("companions") or []
        ]
        if name == "execute":
            phases[name]["tdd"] = phase.get("tdd") or DEFAULT_TDD
    return phases


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
