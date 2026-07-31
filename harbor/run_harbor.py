#!/usr/bin/env python3

import argparse
import asyncio
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlparse


os.environ.setdefault("HARBOR_TELEMETRY", "off")

from harbor.job import Job
from harbor.models.job.config import JobConfig
from harbor.models.task.task import Task
from harbor.models.trial.config import AgentConfig, TaskConfig

ROOT = Path(__file__).resolve().parents[1]
HARBOR = Path(__file__).resolve().parent
SHARED = HARBOR / "shared"
SUPPORTED_AGENTS = ("claude-code", "codex", "kimi-cli", "pi")
CASES = {
    "control-base": HARBOR / "tasks/control-base",
    "override-custom": HARBOR / "tasks/override-custom",
    "override-superpowers": HARBOR / "tasks/override-superpowers",
    "control-superpowers": HARBOR / "tasks/control-superpowers",
}
SMOL_SKILLS = tuple(
    ROOT / f"skills/{name}"
    for name in (
        "smol-activate",
        "smol-design",
        "smol-plan",
        "smol-execute",
        "smol-finish",
    )
)
PI_SUBSCRIPTION_AGENT = "harbor_agents:SubscriptionPi"
NPX_SKILLS_CODEX_AGENT = "harbor_agents:NpxSkillsCodex"
CODEX_AUTH_JSON = Path.home() / ".codex/auth.json"
PI_AUTH_JSON = Path.home() / ".pi/agent/auth.json"
KIMI_CREDENTIALS = Path.home() / ".kimi-code/credentials/kimi-code.json"
KIMI_ANTHROPIC_BASE_URL = "https://api.kimi.com/coding/anthropic"
SUBSCRIPTION_MODEL_PREFIXES = {
    "codex": "openai",
    "kimi-cli": "kimi",
    "pi": "openai-codex",
}
CUSTOM_OVERRIDE_SKILLS = tuple(
    HARBOR / f"override-skills/{name}"
    for name in (
        "integration-design",
        "integration-execute",
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
    if case == "control-base":
        return SMOL_SKILLS
    if case == "override-custom":
        return SMOL_SKILLS + CUSTOM_OVERRIDE_SKILLS
    if case == "override-superpowers":
        return SMOL_SKILLS + (
            superpowers_root / "skills/writing-plans",
            superpowers_root / "skills/test-driven-development",
        )
    return tuple(
        skill.parent
        for skill in sorted((superpowers_root / "skills").glob("*/SKILL.md"))
    )


def validate_inputs(
    cases: list[str],
    agents: list[AgentModel],
    superpowers_root: Path,
) -> None:
    if "control-base" in cases and any(spec.agent != "codex" for spec in agents):
        raise ValueError("control-base lifecycle supports only codex")

    duplicate_agents = {
        spec.agent for spec in agents if sum(item.agent == spec.agent for item in agents) > 1
    }
    if duplicate_agents:
        raise ValueError(
            f"each agent may be selected once: {', '.join(sorted(duplicate_agents))}"
        )

    for spec in agents:
        prefix = SUBSCRIPTION_MODEL_PREFIXES.get(spec.agent)
        if prefix and not spec.model.startswith(f"{prefix}/"):
            raise ValueError(
                f"{spec.agent} uses a subscription login and requires a "
                f"{prefix}/… model, got {spec.model!r}"
            )

    for case in cases:
        task = CASES[case]
        if not task.is_dir():
            raise FileNotFoundError(f"missing Harbor task template: {task}")
        skills = skills_for(case, superpowers_root)
        if not skills:
            raise FileNotFoundError(
                f"missing injected skills beneath: {superpowers_root / 'skills'}"
            )
        for skill in skills:
            if not (skill / "SKILL.md").is_file():
                raise FileNotFoundError(f"missing injected skill: {skill / 'SKILL.md'}")


def stage_task(case: str, destination_root: Path) -> Path:
    staged = shutil.copytree(
        SHARED,
        destination_root / case,
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copytree(
        CASES[case],
        staged,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    if not Task.is_valid_dir(staged):
        raise ValueError(f"invalid staged Harbor task: {staged}")
    return staged


def kimi_subscription_token(credentials_path: Path) -> str:
    try:
        token = json.loads(credentials_path.read_text()).get("access_token")
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(
            f"cannot read Kimi subscription credentials: {credentials_path}"
        ) from error
    if not token:
        raise ValueError(
            f"Kimi subscription credentials lack an access token: {credentials_path}"
        )
    return token


def apply_subscription_auth(agents: list[AgentModel]) -> None:
    """Wire host subscription logins for the selected agents.

    Codex and Pi run on the Codex (ChatGPT) subscription; kimi-cli and
    claude-code run on the Kimi subscription. Variables already present in
    the environment take precedence.
    """
    selected = {spec.agent for spec in agents}
    if "codex" in selected:
        if not CODEX_AUTH_JSON.is_file():
            raise ValueError(
                "codex uses the Codex subscription; log in with `codex login` "
                f"so {CODEX_AUTH_JSON} exists"
            )
        os.environ.setdefault("CODEX_FORCE_AUTH_JSON", "1")
    if "pi" in selected and not PI_AUTH_JSON.is_file():
        raise ValueError(
            "pi uses the Codex subscription; log in to the openai-codex "
            f"provider in pi so {PI_AUTH_JSON} exists"
        )
    if selected & {"claude-code", "kimi-cli"}:
        token = kimi_subscription_token(KIMI_CREDENTIALS)
        os.environ.setdefault("KIMI_API_KEY", token)
        os.environ.setdefault("ANTHROPIC_AUTH_TOKEN", token)
        os.environ.setdefault("ANTHROPIC_BASE_URL", KIMI_ANTHROPIC_BASE_URL)


def agent_import_path(case: str, agent: str) -> str | None:
    if case in {"override-superpowers", "control-superpowers"} and agent == "codex":
        return NPX_SKILLS_CODEX_AGENT
    if agent == "pi":
        return PI_SUBSCRIPTION_AGENT
    return None


def build_job_config(
    case: str,
    agents: list[AgentModel],
    superpowers_root: Path,
    task_path: Path,
) -> JobConfig:
    return JobConfig(
        job_name=f"{case}-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}",
        jobs_dir=HARBOR / "jobs",
        debug=True,
        n_concurrent_trials=len(agents),
        tasks=[TaskConfig(path=task_path)],
        agents=[
            AgentConfig(
                name=spec.agent if agent_import_path(case, spec.agent) is None else None,
                import_path=agent_import_path(case, spec.agent),
                model_name=spec.model,
                skills=list(skills_for(case, superpowers_root)),
                # Reasoning summaries land in trajectory.json as reasoning_content.
                kwargs=(
                    {
                        "reasoning_effort": "medium",
                        "reasoning_summary": "detailed",
                    }
                    if spec.agent == "codex"
                    else {}
                ),
            )
            for spec in agents
        ],
    )


def reasoning_tokens(trial) -> int | None:
    uri = urlparse(str(trial.trial_uri))
    if uri.scheme != "file":
        return None
    try:
        trajectory = json.loads(
            (Path(unquote(uri.path)) / "agent/trajectory.json").read_text()
        )
    except (OSError, json.JSONDecodeError):
        return None
    return ((trajectory.get("final_metrics") or {}).get("extra") or {}).get(
        "reasoning_output_tokens"
    )


async def run_cases(
    cases: list[str],
    agents: list[AgentModel],
    superpowers_root: Path,
) -> int:
    failures: list[str] = []
    for case in dict.fromkeys(cases):
        with tempfile.TemporaryDirectory(prefix=f"smolpowers-{case}-") as temporary:
            task = stage_task(case, Path(temporary))
            job = await Job.create(
                build_job_config(case, agents, superpowers_root, task)
            )
            result = await job.run()
        if len(result.trial_results) != len(agents):
            failures.append(
                f"{case}: expected {len(agents)} trials, got {len(result.trial_results)}"
            )
        for trial in result.trial_results:
            values = (
                trial.verifier_result.rewards
                if trial.verifier_result is not None
                else None
            )
            failed_checks = [
                name for name, value in (values or {}).items() if value != 1
            ]
            passed = (
                trial.exception_info is None
                and bool(values)
                and not failed_checks
            )
            status = "PASS" if passed else "FAIL"
            model = (
                trial.agent_info.model_info.name
                if trial.agent_info.model_info is not None
                else "unknown-model"
            )
            usage = trial.agent_result
            input_tokens = usage.n_input_tokens if usage is not None else None
            cache_tokens = usage.n_cache_tokens if usage is not None else None
            output_tokens = usage.n_output_tokens if usage is not None else None
            total_tokens = (
                input_tokens + output_tokens
                if input_tokens is not None and output_tokens is not None
                else None
            )
            print(
                f"{status} {case} {trial.agent_info.name}={model} "
                f"tokens=total:{total_tokens} input:{input_tokens} "
                f"cached-input:{cache_tokens} output:{output_tokens} "
                f"reasoning:{reasoning_tokens(trial)}"
            )
            if not passed:
                if trial.exception_info is not None:
                    detail = trial.exception_info.exception_message
                elif failed_checks:
                    detail = "failed checks: " + ", ".join(failed_checks)
                else:
                    detail = "missing verifier result"
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
    apply_subscription_auth(args.agent)
    return asyncio.run(run_cases(args.case, args.agent, superpowers_root))


if __name__ == "__main__":
    raise SystemExit(main())
