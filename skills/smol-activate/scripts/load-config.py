import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

WARNING = "smolpowers: reading config failed, using defaults"
DEFAULT_CONFIG = {
    "designDir": "docs/superpowers/specs",
    "planDir": "docs/superpowers/plans",
    "activation": "manual",
    "phases": {
        "design": {
            "skills": ["smol-design"],
        },
        "plan": {
            "skills": ["smol-plan"],
        },
        "execute": {
            "skills": ["smol-execute"],
            "tdd": "proportional",
        },
        "finish": {
            "skills": ["smol-finish"],
        },
    },
}
ENVIRONMENT_PATHS = {
    "SMOL_DESIGN_DIR": ("designDir",),
    "SMOL_PLAN_DIR": ("planDir",),
    "SMOL_ACTIVATION": ("activation",),
    "SMOL_PHASES_DESIGN_SKILLS": ("phases", "design", "skills"),
    "SMOL_PHASES_PLAN_SKILLS": ("phases", "plan", "skills"),
    "SMOL_PHASES_EXECUTE_SKILLS": ("phases", "execute", "skills"),
    "SMOL_PHASES_EXECUTE_TDD": ("phases", "execute", "tdd"),
    "SMOL_PHASES_FINISH_SKILLS": ("phases", "finish", "skills"),
    "SMOL_PHASES_FINISH_COMMIT": ("phases", "finish", "commit"),
    "SMOL_PHASES_FINISH_PUSH": ("phases", "finish", "push"),
}


def config_merge(a: dict, b: dict) -> dict:
    result = a.copy()
    for key, value in b.items():
        if key not in result:
            result[key] = value
        elif isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = config_merge(result[key], value)
    return result


def config_set(config: dict, keys: tuple[str], value):
    for key in keys[:-1]:
        config = config.setdefault(key, {})
    config[keys[-1]] = value


def environment_override() -> dict:
    config = {}
    for name, path in ENVIRONMENT_PATHS.items():
        if name not in os.environ:
            continue
        value = os.environ[name]
        if name.endswith("SKILLS"):
            value = value.split(",")
        config_set(config, path, value)
    return config


def load(repo_root: Path) -> dict:
    config_file = repo_root / ".smolpowers.json"
    user_config = json.loads(config_file.read_text()) if config_file.is_file() else {}
    return config_merge(
        environment_override(), config_merge(user_config, DEFAULT_CONFIG)
    )


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
    try:
        config = load(repository_root(args.repo_root))
    except OSError, ValueError:
        config = DEFAULT_CONFIG
        print(WARNING, file=sys.stderr)
    json.dump(config, sys.stdout, ensure_ascii=False, separators=(",", ":"))
    print()


if __name__ == "__main__":
    main()
