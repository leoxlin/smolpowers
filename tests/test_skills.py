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


def test_skill_structure_and_metadata() -> None:
    for name, imperative in SKILLS.items():
        folder = ROOT / "skills" / name
        skill_path = folder / "SKILL.md"
        assert skill_path.is_file(), f"{name}: missing SKILL.md"
        text = skill_path.read_text()
        metadata, body = frontmatter(text)

        assert set(metadata) == {"name", "description"}
        assert metadata["name"] == name
        assert metadata["description"]
        assert len(re.findall(r"\b[\w'-]+\b", text)) < 2400
        assert "TODO" not in text and "[TODO:" not in text
        assert re.search(rf"(?m)^({imperative}|{imperative.lower()})\b", body)

        metadata_path = folder / "agents" / "openai.yaml"
        assert metadata_path.is_file()
        openai_yaml = metadata_path.read_text()
        assert "display_name:" in openai_yaml
        assert "short_description:" in openai_yaml
        assert f"${name}" in openai_yaml

        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", body):
            if "://" in target or target.startswith("#"):
                continue
            assert (folder / target).is_file(), f"{name}: broken resource link {target}"


def test_execute_tdd_contract() -> None:
    execute = (ROOT / "skills" / "smol-execute" / "SKILL.md").read_text()
    reference_link = "[test-driven-development.md](references/test-driven-development.md)"
    assert reference_link in execute
    assert "phases.execute.tdd" in execute
    assert "NO PRODUCTION CODE WITHOUT AN OBSERVED FAILING TEST FIRST" not in execute

    tdd_reference_path = (
        ROOT / "skills" / "smol-execute" / "references" / "test-driven-development.md"
    )
    assert tdd_reference_path.is_file()
    tdd_reference = tdd_reference_path.read_text()
    tdd_contract = [
        "## Proportional Mode",
        "## Strict Mode",
        "NO PRODUCTION CODE WITHOUT AN OBSERVED FAILING TEST FIRST",
        "### Red: Write One Failing Test",
        "### Green: Make It Pass",
        "### Refactor: Stay Green",
    ]
    for clause in tdd_contract:
        assert clause in tdd_reference
    assert [tdd_reference.index(clause) for clause in tdd_contract] == sorted(
        tdd_reference.index(clause) for clause in tdd_contract
    )


def test_configuration_contract() -> None:
    configuration = (
        ROOT / "skills" / "smol-activate" / "references" / "configuration.md"
    ).read_text()
    for clause in [
        "phases.<name>.owner",
        "phases.<name>.companions",
        "phases.execute.tdd",
        ".smolpowers.yml",
        "Mike Farah `yq` v4",
    ]:
        assert clause in configuration
    assert ".smolpowers.json" not in configuration

    loader = (
        ROOT / "skills" / "smol-activate" / "scripts" / "load-config.sh"
    ).read_text()
    assert "command -v yq" in loader
    assert "jq" not in loader
