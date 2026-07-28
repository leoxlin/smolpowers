#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = {
    "smol-activate": "Load",
    "smol-design": "Inspect",
    "smol-plan": "Validate",
    "smol-execute": "Review",
    "smol-finish": "Verify",
}


def frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    assert match, "missing YAML frontmatter"
    values = {}
    for line in match.group(1).splitlines():
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values, match.group(2)


for name, imperative in SKILLS.items():
    folder = ROOT / "skills" / name
    skill_path = folder / "SKILL.md"
    assert skill_path.is_file(), f"{name}: missing SKILL.md"
    text = skill_path.read_text()
    metadata, body = frontmatter(text)

    assert set(metadata) == {"name", "description"}, f"{name}: invalid frontmatter keys"
    assert metadata["name"] == name, f"{name}: frontmatter/folder mismatch"
    assert metadata["description"], f"{name}: empty description"
    assert len(re.findall(r"\b[\w'-]+\b", text)) < 2400, f"{name}: exceeds 2,400 words"
    assert "TODO" not in text and "[TODO:" not in text, f"{name}: placeholder remains"
    assert re.search(rf"(?m)^({imperative}|{imperative.lower()})\b", body), (
        f"{name}: instructions must use imperative form"
    )

    metadata_path = folder / "agents" / "openai.yaml"
    assert metadata_path.is_file(), f"{name}: missing agents/openai.yaml"
    openai_yaml = metadata_path.read_text()
    assert "display_name:" in openai_yaml
    assert "short_description:" in openai_yaml
    assert f"${name}" in openai_yaml, f"{name}: default prompt does not name the skill"

    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", body):
        if "://" in target or target.startswith("#"):
            continue
        assert (folder / target).is_file(), f"{name}: broken resource link {target}"

print("Skill structure and metadata look good")
