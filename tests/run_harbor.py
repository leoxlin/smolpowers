#!/usr/bin/env python3

import argparse
import asyncio
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


os.environ.setdefault("HARBOR_TELEMETRY", "off")

from harbor.job import Job
from harbor.models.job.config import JobConfig
from harbor.models.task.task import Task
from harbor.models.trial.config import AgentConfig, TaskConfig


ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
SUPPORTED_AGENTS = ("claude-code", "codex", "kimi-cli", "pi")
CASES = {
    "base": TESTS / "harbor/base-lifecycle",
    "override": TESTS / "harbor/override-lifecycle",
    "superpowers": TESTS / "harbor/superpowers-lifecycle",
}
SMOL_SKILLS = tuple(
    ROOT / f"skills/{name}"
    for name in ("smol-activate", "smol-design", "smol-plan", "smol-execute", "smol-finish")
)
OVERRIDE_SKILLS = tuple(
    TESTS / f"fixtures/override-skills/{name}"
    for name in (
        "integration-design",
        "integration-plan",
        "integration-execute",
        "integration-finish",
    )
)


@dataclass(frozen=True)
class AgentModel:
    agent: str
    model: str


def parse_agent(value: str) -> AgentModel:
    agent, separator, model = value.partition("=")
    if not separator or not agent or not model:
        raise argparse.ArgumentTypeError("expected AGENT=MODEL")
    if agent not in SUPPORTED_AGENTS:
        supported = ", ".join(SUPPORTED_AGENTS)
        raise argparse.ArgumentTypeError(
            f"unsupported agent {agent!r}; choose one of: {supported}"
        )
    return AgentModel(agent, model)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run authenticated Smolpowers lifecycle evaluations with Harbor."
    )
    parser.add_argument(
        "--case",
        action="append",
        choices=CASES,
        required=True,
        help="Lifecycle case to run; repeat to select both.",
    )
    parser.add_argument(
        "--agent",
        action="append",
        type=parse_agent,
        required=True,
        help="Harbor agent and model as AGENT=MODEL; repeat for multiple agents.",
    )
    parser.add_argument(
        "--superpowers-root",
        type=Path,
        help="Upstream Superpowers checkout (defaults to SUPERPOWERS_ROOT or ../superpowers).",
    )
    return parser.parse_args(argv)


def resolve_superpowers_root(argument: Path | None) -> Path:
    configured = argument or os.environ.get("SUPERPOWERS_ROOT")
    return Path(configured).expanduser().resolve() if configured else ROOT.parent / "superpowers"


def skills_for(case: str, superpowers_root: Path) -> tuple[Path, ...]:
    if case == "base":
        return SMOL_SKILLS
    if case == "override":
        return SMOL_SKILLS + OVERRIDE_SKILLS
    return SMOL_SKILLS + (
        superpowers_root / "skills/writing-plans",
        superpowers_root / "skills/test-driven-development",
    )


def validate_inputs(
    cases: list[str],
    agents: list[AgentModel],
    superpowers_root: Path,
) -> None:
    duplicate_agents = {
        spec.agent for spec in agents if sum(item.agent == spec.agent for item in agents) > 1
    }
    if duplicate_agents:
        raise ValueError(
            f"each agent may be selected once: {', '.join(sorted(duplicate_agents))}"
        )

    for case in cases:
        task = CASES[case]
        if not Task.is_valid_dir(task):
            raise ValueError(f"invalid Harbor task: {task}")
        for skill in skills_for(case, superpowers_root):
            if not (skill / "SKILL.md").is_file():
                raise FileNotFoundError(f"missing injected skill: {skill / 'SKILL.md'}")


def build_job_config(
    case: str,
    agents: list[AgentModel],
    superpowers_root: Path,
) -> JobConfig:
    return JobConfig(
        job_name=f"{case}-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}",
        jobs_dir=TESTS / "jobs",
        n_concurrent_trials=len(agents),
        tasks=[TaskConfig(path=CASES[case])],
        agents=[
            AgentConfig(
                name=spec.agent,
                model_name=spec.model,
                skills=list(skills_for(case, superpowers_root)),
            )
            for spec in agents
        ],
    )


async def run_cases(
    cases: list[str],
    agents: list[AgentModel],
    superpowers_root: Path,
) -> int:
    failures: list[str] = []
    for case in dict.fromkeys(cases):
        job = await Job.create(build_job_config(case, agents, superpowers_root))
        result = await job.run()
        if len(result.trial_results) != len(agents):
            failures.append(
                f"{case}: expected {len(agents)} trials, got {len(result.trial_results)}"
            )
        for trial in result.trial_results:
            rewards = (
                trial.verifier_result.rewards
                if trial.verifier_result is not None
                else None
            )
            passed = (
                trial.exception_info is None
                and rewards is not None
                and rewards.get("reward") == 1
            )
            status = "PASS" if passed else "FAIL"
            model = (
                trial.agent_info.model_info.name
                if trial.agent_info.model_info is not None
                else "unknown-model"
            )
            print(f"{status} {case} {trial.agent_info.name}={model}")
            if not passed:
                detail = (
                    trial.exception_info.exception_message
                    if trial.exception_info is not None
                    else f"rewards={rewards!r}"
                )
                failures.append(
                    f"{case}/{trial.agent_info.name}={model}: {detail}"
                )

    if failures:
        raise RuntimeError("\n".join(failures))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    superpowers_root = resolve_superpowers_root(args.superpowers_root)
    validate_inputs(args.case, args.agent, superpowers_root)
    return asyncio.run(run_cases(args.case, args.agent, superpowers_root))


if __name__ == "__main__":
    raise SystemExit(main())
