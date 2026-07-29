import argparse
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


def test_staged_tasks_use_isolated_fake_project(tmp_path: Path) -> None:
    source_files = {
        path.relative_to(run_harbor.FAKE_PROJECT): path.read_bytes()
        for path in run_harbor.FAKE_PROJECT.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }

    for case in run_harbor.CASES:
        staged = run_harbor.stage_task(case, tmp_path)

        assert Task.is_valid_dir(staged)
        assert not list(staged.rglob("__pycache__"))
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

        (staged / "environment/fixture/greeting.py").write_text("changed\n")
        assert (run_harbor.FAKE_PROJECT / "greeting.py").read_bytes() == source_files[
            Path("greeting.py")
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
        run_harbor.AgentModel("pi", "anthropic/claude-sonnet"),
    ]
    config = run_harbor.build_job_config(
        "override",
        agents,
        Path("/unused-superpowers"),
        run_harbor.CASES["override"],
    )
    assert config.n_concurrent_trials == 2
    assert [agent.name for agent in config.agents] == ["codex", "pi"]
    assert [agent.model_name for agent in config.agents] == [
        "openai/gpt-5",
        "anthropic/claude-sonnet",
    ]
    assert len(config.agents[0].skills) == 9


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
    assert config.agents[0].env == {
        "SMOLPOWERS_ACTIVATION_LOG": "/logs/agent/smolpowers-activation.json"
    }


def test_validation_fails_before_run_for_missing_upstream(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="writing-plans"):
        run_harbor.validate_inputs(
            ["superpowers"],
            [run_harbor.AgentModel("codex", "model")],
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
