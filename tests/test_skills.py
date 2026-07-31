from importlib.resources import files
from pathlib import Path

import pytest
import tiktoken
import yaml


ROOT = Path(__file__).resolve().parents[1]
MAX_SKILL_TOKENS = 600
MAX_SKILL_METADATA_TOKENS = 50


def test_skills_fit_token_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    tokenizer_cache = files("litellm.litellm_core_utils.tokenizers")
    monkeypatch.setenv("TIKTOKEN_CACHE_DIR", str(tokenizer_cache))
    encoding = tiktoken.get_encoding("o200k_base")
    skill_paths = sorted(ROOT.glob("skills/*/SKILL.md"))
    assert skill_paths
    for path in skill_paths:
        contents = path.read_text()
        metadata = yaml.safe_load(contents.split("---", 2)[1])
        descriptor = f"{metadata['name']}\n{metadata['description']}"
        assert len(encoding.encode(contents)) <= MAX_SKILL_TOKENS, metadata["name"]
        assert (
            len(encoding.encode(descriptor)) <= MAX_SKILL_METADATA_TOKENS
        ), metadata["name"]


def test_skill_names_match_folder_names() -> None:
    for path in sorted(ROOT.glob("skills/*/SKILL.md")):
        metadata = yaml.safe_load(path.read_text().split("---", 2)[1])
        assert metadata["name"] == path.parent.name
