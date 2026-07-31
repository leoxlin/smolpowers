import os
from importlib.resources import files
from pathlib import Path

import tiktoken
import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL_ORDER = [
    "smol-activate",
    "smol-design",
    "smol-plan",
    "smol-execute",
    "smol-finish",
]


def main() -> None:
    tokenizer_cache = files("litellm.litellm_core_utils.tokenizers")
    os.environ["TIKTOKEN_CACHE_DIR"] = str(tokenizer_cache)
    encoding = tiktoken.get_encoding("o200k_base")

    rows = []
    for skill_name in SKILL_ORDER:
        skill_path = ROOT / "skills" / skill_name / "SKILL.md"
        contents = skill_path.read_text()
        skill = yaml.safe_load(contents.split("---", 2)[1])["name"]
        paths = [
            skill_path,
            *sorted((skill_path.parent / "references").rglob("*.md")),
        ]
        for path in paths:
            rows.append(
                (
                    skill,
                    path.name,
                    len(encoding.encode(path.read_text())),
                )
            )

    skill_width = max([len("Skill"), *(len(skill) for skill, _, _ in rows)])
    file_width = max([len("File"), *(len(file) for _, file, _ in rows)])
    token_width = max([len("Tokens"), *(len(str(tokens)) for _, _, tokens in rows)])
    print(
        f"| {'Skill':<{skill_width}} | {'File':<{file_width}} | "
        f"{'Tokens':>{token_width}} |"
    )
    print(
        f"| {'-' * skill_width} | {'-' * file_width} | "
        f"{'-' * (token_width - 1)}: |"
    )
    for skill, file, tokens in rows:
        print(
            f"| {skill:<{skill_width}} | {file:<{file_width}} | "
            f"{tokens:>{token_width}} |"
        )


if __name__ == "__main__":
    main()
