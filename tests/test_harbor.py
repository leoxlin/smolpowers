import argparse
import os
from pathlib import Path

import pytest
from harbor.models.task.task import Task

import run_harbor


def test_harbor_tasks_are_valid() -> None:
    for task in run_harbor.CASES.values():
        assert Task.is_valid_dir(task)
        loaded = Task(task)
        assert loaded.config.agent.user == "agent"
        assert loaded.config.verifier.user == "root"
        assert loaded.config.environment.network_mode.value == "public"


def test_staged_tasks_use_isolated_smolurl(tmp_path: Path) -> None:
    source_files = {
        path.relative_to(run_harbor.SMOLURL): path.read_bytes()
        for path in run_harbor.SMOLURL.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }

    for case in run_harbor.CASES:
        staged = run_harbor.stage_task(case, tmp_path)

        assert Task.is_valid_dir(staged)
        assert not list(staged.rglob("__pycache__"))
        assert (staged / "tests/lifecycle_eval.py").is_file()
        assert (staged / "tests/verify_lifecycle.py").is_file()
        for relative_path, content in source_files.items():
            assert (staged / "environment/fixture" / relative_path).read_bytes() == content

        configured = case != "base"
        assert (staged / "environment/fixture/.smolpowers.json").exists() == configured
        if case == "base":
            plugin = staged / "environment/plugin"
            assert (plugin / ".codex-plugin/plugin.json").is_file()
            assert (plugin / ".agents/plugins/marketplace.json").is_file()
            assert (plugin / "hooks/hooks.json").is_file()
            assert sorted(path.parent.name for path in plugin.glob("skills/*/SKILL.md")) == [
                "smol-activate",
                "smol-design",
                "smol-execute",
                "smol-finish",
                "smol-plan",
            ]

        (staged / "environment/fixture/app.py").write_text("changed\n")
        assert (run_harbor.SMOLURL / "app.py").read_bytes() == source_files[
            Path("app.py")
        ]


def test_agent_mapping() -> None:
    assert run_harbor.parse_agent("codex=openai/gpt-5") == run_harbor.AgentModel(
        "codex", "openai/gpt-5"
    )
    with pytest.raises(argparse.ArgumentTypeError):
        run_harbor.parse_agent("codex")
    with pytest.raises(argparse.ArgumentTypeError):
        run_harbor.parse_agent("unknown=model")


def test_override_job_config() -> None:
    agents = [
        run_harbor.AgentModel("codex", "openai/gpt-5"),
        run_harbor.AgentModel("pi", "openai-codex/gpt-5"),
    ]
    config = run_harbor.build_job_config(
        "override",
        agents,
        Path("/unused-superpowers"),
        run_harbor.CASES["override"],
    )
    assert config.n_concurrent_trials == 2
    assert [agent.name for agent in config.agents] == ["codex", None]
    assert [agent.import_path for agent in config.agents] == [
        None,
        "harbor_agents:SubscriptionPi",
    ]
    assert [agent.model_name for agent in config.agents] == [
        "openai/gpt-5",
        "openai-codex/gpt-5",
    ]
    assert len(config.agents[0].skills) == 9
    assert config.agents[0].kwargs == {
        "reasoning_effort": "medium",
        "reasoning_summary": "detailed",
    }
    assert config.agents[1].kwargs == {}


def test_base_job_config() -> None:
    config = run_harbor.build_job_config(
        "base",
        [run_harbor.AgentModel("codex", "openai/gpt-5")],
        Path("/unused-superpowers"),
        run_harbor.CASES["base"],
    )
    assert config.debug
    assert config.tasks[0].path == run_harbor.CASES["base"]
    assert config.agents[0].name is None
    assert config.agents[0].import_path == "harbor_agents:PluginCodex"
    assert config.agents[0].skills == []
    assert config.agents[0].kwargs == {
        "reasoning_effort": "medium",
        "reasoning_summary": "detailed",
    }
    assert config.agents[0].env == {
        "SMOLPOWERS_ACTIVATION_LOG": "/logs/agent/smolpowers-activation.json"
    }


def test_validation_fails_before_run_for_missing_upstream(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="writing-plans"):
        run_harbor.validate_inputs(
            ["superpowers"],
            [run_harbor.AgentModel("codex", "openai/gpt-5")],
            tmp_path,
        )


def test_validation_rejects_duplicate_agents() -> None:
    with pytest.raises(ValueError, match="selected once"):
        run_harbor.validate_inputs(
            ["override"],
            [
                run_harbor.AgentModel("codex", "model-a"),
                run_harbor.AgentModel("codex", "model-b"),
            ],
            Path("/unused-superpowers"),
        )


def test_validation_rejects_non_codex_base_agent() -> None:
    with pytest.raises(ValueError, match="base lifecycle supports only codex"):
        run_harbor.validate_inputs(
            ["base"],
            [run_harbor.AgentModel("pi", "model")],
            Path("/unused-superpowers"),
        )


def test_validation_rejects_non_subscription_models() -> None:
    with pytest.raises(ValueError, match="openai/… model"):
        run_harbor.validate_inputs(
            ["override"],
            [run_harbor.AgentModel("codex", "azure/gpt-5")],
            Path("/unused-superpowers"),
        )
    with pytest.raises(ValueError, match="openai-codex/… model"):
        run_harbor.validate_inputs(
            ["override"],
            [run_harbor.AgentModel("pi", "openai/gpt-5")],
            Path("/unused-superpowers"),
        )
    with pytest.raises(ValueError, match="kimi/… model"):
        run_harbor.validate_inputs(
            ["override"],
            [run_harbor.AgentModel("kimi-cli", "moonshot/k3")],
            Path("/unused-superpowers"),
        )


def test_kimi_subscription_token(tmp_path: Path) -> None:
    credentials = tmp_path / "kimi-code.json"
    credentials.write_text('{"access_token": "token-123"}')
    assert run_harbor.kimi_subscription_token(credentials) == "token-123"

    with pytest.raises(ValueError, match="cannot read Kimi subscription credentials"):
        run_harbor.kimi_subscription_token(tmp_path / "missing.json")

    credentials.write_text("{}")
    with pytest.raises(ValueError, match="lack an access token"):
        run_harbor.kimi_subscription_token(credentials)


def test_apply_subscription_auth_codex_and_pi(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    codex_auth = tmp_path / "codex-auth.json"
    codex_auth.write_text("{}")
    pi_auth = tmp_path / "pi-auth.json"
    pi_auth.write_text("{}")
    monkeypatch.setattr(run_harbor, "CODEX_AUTH_JSON", codex_auth)
    monkeypatch.setattr(run_harbor, "PI_AUTH_JSON", pi_auth)
    monkeypatch.setattr("os.environ", {})

    agents = [
        run_harbor.AgentModel("codex", "openai/gpt-5"),
        run_harbor.AgentModel("pi", "openai-codex/gpt-5"),
    ]
    run_harbor.apply_subscription_auth(agents)
    assert os.environ["CODEX_FORCE_AUTH_JSON"] == "1"
    assert "KIMI_API_KEY" not in os.environ

    codex_auth.unlink()
    with pytest.raises(ValueError, match="codex login"):
        run_harbor.apply_subscription_auth(agents)

    codex_auth.write_text("{}")
    pi_auth.unlink()
    with pytest.raises(ValueError, match="openai-codex"):
        run_harbor.apply_subscription_auth(agents)


def test_apply_subscription_auth_kimi_agents(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    credentials = tmp_path / "kimi-code.json"
    credentials.write_text('{"access_token": "token-123"}')
    monkeypatch.setattr(run_harbor, "KIMI_CREDENTIALS", credentials)
    monkeypatch.setattr("os.environ", {"KIMI_API_KEY": "preset"})

    agents = [
        run_harbor.AgentModel("kimi-cli", "kimi/k3"),
        run_harbor.AgentModel("claude-code", "kimi-for-coding"),
    ]
    run_harbor.apply_subscription_auth(agents)
    assert os.environ["KIMI_API_KEY"] == "preset"
    assert os.environ["ANTHROPIC_AUTH_TOKEN"] == "token-123"
    assert os.environ["ANTHROPIC_BASE_URL"] == run_harbor.KIMI_ANTHROPIC_BASE_URL
    assert "CODEX_FORCE_AUTH_JSON" not in os.environ

    credentials.unlink()
    with pytest.raises(ValueError, match="cannot read Kimi subscription credentials"):
        run_harbor.apply_subscription_auth(agents)
