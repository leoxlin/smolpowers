from importlib.resources import files
from pathlib import Path
import re

import pytest
import tiktoken
import yaml


ROOT = Path(__file__).resolve().parents[1]
MAX_SKILL_TOKENS = 600
MAX_SKILL_METADATA_TOKENS = 50
SKILL_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
MARKDOWN_LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")


def skill_paths() -> list[Path]:
    paths = sorted(ROOT.glob("skills/*/SKILL.md"))
    assert paths
    return paths


def skill_metadata(path: Path) -> dict:
    return yaml.safe_load(path.read_text().split("---", 2)[1])


def test_skills_fit_token_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    tokenizer_cache = files("litellm.litellm_core_utils.tokenizers")
    monkeypatch.setenv("TIKTOKEN_CACHE_DIR", str(tokenizer_cache))
    encoding = tiktoken.get_encoding("o200k_base")
    for path in skill_paths():
        contents = path.read_text()
        metadata = skill_metadata(path)
        descriptor = f"{metadata['name']}\n{metadata['description']}"
        assert len(encoding.encode(contents)) <= MAX_SKILL_TOKENS, metadata["name"]
        assert (
            len(encoding.encode(descriptor)) <= MAX_SKILL_METADATA_TOKENS
        ), metadata["name"]


def test_skills_follow_shared_metadata_contract() -> None:
    for path in skill_paths():
        metadata = skill_metadata(path)
        name = metadata["name"]
        description = metadata["description"]
        assert set(metadata) == {"name", "description"}, path
        assert SKILL_NAME.fullmatch(name), path
        assert len(name) <= 64, path
        assert name == path.parent.name, path
        assert isinstance(description, str) and description.strip(), path
        assert len(description) <= 1024, path


def test_local_skill_links_resolve() -> None:
    for path in sorted(ROOT.glob("skills/**/*.md")):
        for raw_target in MARKDOWN_LINK.findall(path.read_text()):
            target = raw_target.split("#", 1)[0]
            if not target or "://" in target or target.startswith("/"):
                continue
            assert (path.parent / target).is_file(), f"{path}: {raw_target}"


def test_phase_prompts_route_through_activation() -> None:
    for path in skill_paths():
        metadata_path = path.parent / "agents/openai.yaml"
        metadata = yaml.safe_load(metadata_path.read_text())
        prompt = metadata["interface"]["default_prompt"]
        assert f"${path.parent.name}" in prompt, metadata_path
        if path.parent.name != "smol-activate":
            assert prompt.startswith("Use $smol-activate"), metadata_path
