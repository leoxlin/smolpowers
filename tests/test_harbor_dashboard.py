import json
from pathlib import Path

import harbor_dashboard


def write_trajectory(trial_dir: Path) -> dict:
    trajectory = {
        "schema_version": "ATIF-v1.7",
        "session_id": "session-1",
        "agent": {"name": "codex", "version": "0.1.0", "model_name": "gpt-5"},
        "steps": [
            {
                "step_id": 1,
                "timestamp": "2026-07-29T13:27:46.296Z",
                "source": "system",
                "message": "permissions",
            },
            {
                "step_id": 2,
                "timestamp": "2026-07-29T13:27:50.677Z",
                "source": "agent",
                "model_name": "openai/gpt-5",
                "message": "reading the plan skill",
                "reasoning_content": "I should load smol-plan first.",
                "tool_calls": [
                    {
                        "tool_call_id": "call_1",
                        "function_name": "exec_command",
                        "arguments": {
                            "cmd": "sed -n 1,200p /plugin/skills/smol-plan/SKILL.md"
                        },
                    }
                ],
                "observation": {
                    "results": [
                        {"source_call_id": "call_1", "content": "# Smol Plan"}
                    ]
                },
                "metrics": {
                    "prompt_tokens": 100,
                    "completion_tokens": 10,
                    "extra": {"reasoning_output_tokens": 7},
                },
            },
            {
                "step_id": 3,
                "timestamp": "2026-07-29T13:27:56.659Z",
                "source": "agent",
                "model_name": "openai/gpt-5",
                "message": "done",
                "tool_calls": [
                    {
                        "tool_call_id": "call_2",
                        "function_name": "apply_patch",
                        "arguments": {"patch": "*** Begin Patch"},
                    }
                ],
                "metrics": {"prompt_tokens": 200, "completion_tokens": 20},
            },
        ],
        "final_metrics": {
            "total_prompt_tokens": 300,
            "total_completion_tokens": 30,
            "total_cached_tokens": 250,
            "total_cost_usd": 0.01,
            "extra": {"reasoning_output_tokens": 7},
        },
    }
    agent_dir = trial_dir / "agent"
    agent_dir.mkdir(parents=True)
    (agent_dir / "trajectory.json").write_text(json.dumps(trajectory))
    return trajectory


def test_trace_overview_counts_steps_tools_and_skills(tmp_path: Path) -> None:
    write_trajectory(tmp_path)
    overview = harbor_dashboard.trace_overview(tmp_path)
    assert overview == {
        "steps": 3,
        "tool_calls": 2,
        "reasoning": 1,
        "skills": ["smol-plan"],
        "lifecycle": [],
        "reasoning_tokens": 7,
    }


def test_trace_overview_missing_returns_none(tmp_path: Path) -> None:
    assert harbor_dashboard.trace_overview(tmp_path) is None


def test_load_trace_normalizes_steps(tmp_path: Path) -> None:
    write_trajectory(tmp_path)
    trace = harbor_dashboard.load_trace(tmp_path)

    assert trace is not None
    assert trace["session_id"] == "session-1"
    assert trace["agent_name"] == "codex"
    assert trace["model_name"] == "gpt-5"
    assert trace["sources"] == ["agent", "system"]
    assert trace["tools"] == [
        {"name": "exec_command", "n": 1},
        {"name": "apply_patch", "n": 1},
    ]
    assert trace["skills"] == ["smol-plan"]
    assert trace["n_reasoning"] == 1
    assert trace["final"] == {
        "prompt_tokens": 300,
        "completion_tokens": 30,
        "cached_tokens": 250,
        "cost_usd": 0.01,
        "reasoning_tokens": 7,
    }

    system, agent, plain = trace["steps"]
    assert system["source"] == "system"
    assert system["reasoning"] == ""
    assert system["tool_calls"] == []

    assert agent["reasoning"] == "I should load smol-plan first."
    assert agent["skills"] == ["smol-plan"]
    assert agent["tool_calls"][0]["name"] == "exec_command"
    assert "smol-plan/SKILL.md" in agent["tool_calls"][0]["arguments"]
    assert agent["tool_calls"][0]["skills"] == ["smol-plan"]
    assert agent["observation"] == "# Smol Plan"
    assert agent["prompt_tokens"] == 100
    assert agent["reasoning_tokens"] == 7
    assert agent["time"] != "—"

    assert plain["reasoning"] == ""
    assert plain["reasoning_tokens"] is None


def test_load_trace_missing_returns_none(tmp_path: Path) -> None:
    assert harbor_dashboard.load_trace(tmp_path) is None


def test_resolve_trial_dir(tmp_path: Path) -> None:
    trial = tmp_path / "job-a" / "task__abc"
    trial.mkdir(parents=True)
    assert harbor_dashboard.resolve_trial_dir(tmp_path, "job-a", "task__abc") == trial
    assert harbor_dashboard.resolve_trial_dir(tmp_path, "job-a", "..") is None
    assert harbor_dashboard.resolve_trial_dir(tmp_path, "..", "task__abc") is None
    assert harbor_dashboard.resolve_trial_dir(tmp_path, "job-a", "task%2Fabc") is None
    assert harbor_dashboard.resolve_trial_dir(tmp_path, "job-a", "missing") is None


def test_load_trial_exposes_trace_overview(tmp_path: Path) -> None:
    trial = tmp_path / "task__abc"
    trial.mkdir()
    (trial / "result.json").write_text(
        json.dumps(
            {
                "trial_name": "task__abc",
                "task_name": "base",
                "agent_info": {"name": "codex", "model_info": {"name": "gpt-5"}},
                "agent_result": {
                    "n_input_tokens": 300,
                    "n_cache_tokens": 250,
                    "n_output_tokens": 30,
                },
                "verifier_result": {
                    "rewards": {
                        "skills_in_order": 1,
                        "requested_change_completed": 1,
                    }
                },
            }
        )
    )
    write_trajectory(trial)

    loaded = harbor_dashboard.load_trial(trial)
    assert loaded["dir"] == "task__abc"
    assert loaded["status"] == "passed"
    assert loaded["checks"]["kind"] == "named"
    assert loaded["tokens_total"] == 330
    assert loaded["cache_tokens"] == 250
    assert loaded["reasoning_tokens"] == 7
    assert loaded["trace"]["steps"] == 3
    assert loaded["trace"]["skills"] == ["smol-plan"]
    assert loaded["trace"]["lifecycle"][0] == {
        "skill": "smol-activate",
        "step_id": None,
        "href": None,
    }
    assert loaded["trace"]["lifecycle"][2] == {
        "skill": "smol-plan",
        "step_id": 2,
        "href": "#step-2",
    }


def test_load_trial_does_not_support_legacy_verifier(tmp_path: Path) -> None:
    trial = tmp_path / "task__legacy"
    trial.mkdir()
    (trial / "result.json").write_text(
        json.dumps(
            {
                "trial_name": "task__legacy",
                "task_name": "task",
                "agent_info": {"name": "codex", "model_info": {"name": "gpt-5"}},
                "verifier_result": {"rewards": {"reward": 0}},
            }
        )
    )

    loaded = harbor_dashboard.load_trial(trial)
    assert loaded["status"] == "failed"
    assert loaded["checks"]["kind"] == "missing"
    assert loaded["evaluation_label"] == "missing"


def test_rollups_calculate_pass_rates_and_average_total_tokens() -> None:
    trials = [
        {
            "agent": "codex",
            "model": "gpt-5",
            "status": "passed",
            "checks": {
                "kind": "named",
                "passed": True,
                "skills_in_order": 1,
                "requested_change_completed": 1,
            },
            "input_tokens": 100,
            "output_tokens": 20,
            "cost_usd": None,
        },
        {
            "agent": "codex",
            "model": "gpt-5",
            "status": "failed",
            "checks": {
                "kind": "named",
                "passed": False,
                "skills_in_order": 0,
                "requested_change_completed": 1,
            },
            "input_tokens": 200,
            "output_tokens": 40,
            "cost_usd": None,
        },
    ]
    jobs = [
        {
            "trials": trials,
            "input_tokens": 300,
            "output_tokens": 60,
            "cost_usd": None,
        }
    ]

    row = harbor_dashboard.agent_rollup(jobs)[0]
    stats = harbor_dashboard.page_stats(jobs)
    assert row["overall_rate"] == 0.5
    assert row["skills_rate"] == 0.5
    assert row["requested_rate"] == 1
    assert row["average_tokens"] == 180
    assert stats["overall_rate"] == "50%"
    assert stats["skills_rate"] == "50%"
    assert stats["requested_rate"] == "100%"
    assert stats["tokens_total"] == "360"


def test_render_trace_includes_step_content(tmp_path: Path) -> None:
    write_trajectory(tmp_path)
    trace = harbor_dashboard.load_trace(tmp_path)
    html = harbor_dashboard.render_trace(
        trace, Path(harbor_dashboard.__file__).parent, "job-a", "task__abc"
    )
    assert "I should load smol-plan first." in html
    assert "exec_command" in html
    assert "# Smol Plan" in html
    assert 'id="step-2"' in html
