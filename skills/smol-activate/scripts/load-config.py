import argparse
import json
import subprocess
import sys
from pathlib import Path

WARNING = "smolpowers: reading config failed, using defaults"
DEFAULT_CONFIG = {
    "designDir": "docs/superpowers/specs",
    "planDir": "docs/superpowers/plans",
    "activation": "default",
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


def config_merge(a: dict, b: dict) -> dict:
    result = a.copy()
    for key, value in b.items():
        if key not in result:
            result[key] = value
        elif isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = config_merge(result[key], value)
    return result


def load(repo_root: Path) -> dict:
    config_file = repo_root / ".smolpowers.json"
    if not config_file.is_file():
        return DEFAULT_CONFIG
    user_config = json.loads(config_file.read_text())
    return config_merge(user_config, DEFAULT_CONFIG)


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
