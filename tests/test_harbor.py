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
        "override", agents, Path("/unused-superpowers")
    )
    assert config.n_concurrent_trials == 2
    assert [agent.name for agent in config.agents] == ["codex", "pi"]
    assert [agent.model_name for agent in config.agents] == [
        "openai/gpt-5",
        "anthropic/claude-sonnet",
    ]
    assert len(config.agents[0].skills) == 9


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
