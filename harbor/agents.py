import json
import shlex
import uuid
from typing import Any, override

from harbor.agents.installed.base import BaseInstalledAgent, with_prompt_template
from harbor.agents.installed.codex import Codex
from harbor.agents.installed.kimi_cli import KimiCli
from harbor.agents.installed.node_install import nvm_node_install_snippet
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext
from harbor.models.trajectories import (
    Agent,
    FinalMetrics,
    Metrics,
    Observation,
    ObservationResult,
    Step,
    ToolCall,
    Trajectory,
)
from harbor.models.trial.paths import EnvironmentPaths
from harbor.utils.trajectory_utils import format_trajectory_json

MIX_CONFIG = {
    "specDir": "artifacts",
    "stateDir": ".smol-state",
    "phases": {
        "design": {"owner": "smol-design"},
        "plan": {"owner": "writing-plans"},
        "execute": {
            "owner": "smol-execute",
            "companions": ["test-driven-development"],
        },
        "finish": {"owner": "smol-finish"},
    },
}


class NpxSkillsCodex(Codex):
    """Codex with injected skills installed by the Skills CLI."""

    smolpowers_config: dict[str, object] | None = None

    def __init__(self, *args, lifecycle_instruction: str, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.lifecycle_instruction = lifecycle_instruction

    @override
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        skills_dir = self.skills_dir
        if skills_dir is None:
            raise ValueError("NpxSkillsCodex requires injected skills")
        if self.smolpowers_config is not None:
            config = json.dumps(self.smolpowers_config, indent=2) + "\n"
            script = (
                "from pathlib import Path; "
                f"config = {config!r}; "
                "Path('/app/.smolpowers.json').write_text(config); "
                "Path('/opt/fixture/.smolpowers.json').write_text(config)"
            )
            await self.exec_as_root(
                environment,
                command=f"python -c {shlex.quote(script)}",
            )
        await self.exec_as_agent(
            environment,
            command=(
                "if [ -s ~/.nvm/nvm.sh ]; then . ~/.nvm/nvm.sh; fi; "
                f"npx --yes skills add {shlex.quote(skills_dir)} "
                "--skill '*' --agent codex -g -y --copy"
            ),
        )
        skill_note = (
            "Codex setup installed the injected skills with `npx skills add` at "
            "`/home/agent/.agents/skills`. A skill that disables implicit "
            "invocation can be absent from the generated skill list. For each "
            "requested or configured skill, read "
            "`/home/agent/.agents/skills/<name>/SKILL.md` before you report that "
            "the skill is not installed.\n\n"
        )
        await super().run(
            skill_note + self.lifecycle_instruction + "\n\n" + instruction,
            environment,
            context,
        )

    @override
    def populate_context_post_run(self, context: AgentContext) -> None:
        super().populate_context_post_run(context)
        trajectory_path = self.logs_dir / "trajectory.json"
        if not trajectory_path.is_file():
            return
        trajectory = json.loads(trajectory_path.read_text())
        trajectory["agent"]["name"] = self.name()
        trajectory_path.write_text(json.dumps(trajectory, indent=2) + "\n")


class CodexSp(NpxSkillsCodex):
    @staticmethod
    @override
    def name() -> str:
        return "codex-sp"


class CodexSmol(NpxSkillsCodex):
    @staticmethod
    @override
    def name() -> str:
        return "codex-smol"


class CodexMix(NpxSkillsCodex):
    smolpowers_config = MIX_CONFIG

    @staticmethod
    @override
    def name() -> str:
        return "codex-mix"


class SkillsKimiCli(KimiCli):
    """Kimi CLI with injected skills and a lifecycle instruction."""

    smolpowers_config: dict[str, object] | None = None

    def __init__(self, *args, lifecycle_instruction: str, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.lifecycle_instruction = lifecycle_instruction

    @override
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        if self.skills_dir is None:
            raise ValueError("SkillsKimiCli requires injected skills")
        if self.smolpowers_config is not None:
            config = json.dumps(self.smolpowers_config, indent=2) + "\n"
            script = (
                "from pathlib import Path; "
                f"config = {config!r}; "
                "Path('/app/.smolpowers.json').write_text(config); "
                "Path('/opt/fixture/.smolpowers.json').write_text(config)"
            )
            await self.exec_as_root(
                environment,
                command=f"python -c {shlex.quote(script)}",
            )
        await super().run(
            self.lifecycle_instruction + "\n\n" + instruction,
            environment,
            context,
        )

    @override
    def populate_context_post_run(self, context: AgentContext) -> None:
        super().populate_context_post_run(context)
        trajectory_path = self.logs_dir / "trajectory.json"
        if not trajectory_path.is_file():
            return
        trajectory = json.loads(trajectory_path.read_text())
        trajectory["agent"]["name"] = self.name()
        trajectory_path.write_text(json.dumps(trajectory, indent=2) + "\n")


class KimiSp(SkillsKimiCli):
    @staticmethod
    @override
    def name() -> str:
        return "kimi-sp"


class KimiSmol(SkillsKimiCli):
    @staticmethod
    @override
    def name() -> str:
        return "kimi-smol"


class KimiMix(SkillsKimiCli):
    smolpowers_config = MIX_CONFIG

    @staticmethod
    @override
    def name() -> str:
        return "kimi-mix"


_KIMI_CODE_PACKAGE = "@moonshot-ai/kimi-code"
_KIMI_CODE_HOME = EnvironmentPaths.agent_dir / ".kimi-code"
_KIMI_CODE_OUTPUT = EnvironmentPaths.agent_dir / "kimi-code.txt"
_NODE_PATH_SETUP = (
    'if [ -s "$HOME/.nvm/nvm.sh" ]; then . "$HOME/.nvm/nvm.sh"; fi; '
    'export PATH="$HOME/.local/bin:$PATH"; '
)


class _KimiCodeWireStep:
    """One agent step grouped from kimi-code wire.jsonl loop events."""

    def __init__(self) -> None:
        self.text_parts: list[str] = []
        self.reasoning_parts: list[str] = []
        self.tool_calls: list[dict[str, Any]] = []
        self.tool_results: dict[str, Any] = {}
        self.token_usage: dict[str, Any] | None = None


class KimiCodeCli(BaseInstalledAgent):
    """Kimi Code CLI agent with injected skills and a lifecycle instruction.

    Unlike the upstream kimi-cli agent, this runs the Kimi Code CLI
    (https://github.com/MoonshotAI/kimi-code), whose plugin system consumes
    the superpowers `.kimi-plugin/plugin.json` manifest (skills, sessionStart,
    skillInstructions). When `superpowers_ref` is set, the superpowers repo is
    installed as a managed plugin instead of registering plain skills.
    """

    SUPPORTS_ATIF: bool = True

    smolpowers_config: dict[str, object] | None = None

    def __init__(
        self,
        *args,
        lifecycle_instruction: str,
        superpowers_ref: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.lifecycle_instruction = lifecycle_instruction
        self.superpowers_ref = superpowers_ref

    @override
    async def install(self, environment: BaseEnvironment) -> None:
        await self.exec_as_root(
            environment,
            command=(
                "if ! command -v curl >/dev/null 2>&1; then "
                "apt-get update && apt-get install -y curl; fi"
            ),
            env={"DEBIAN_FRONTEND": "noninteractive"},
        )
        version_spec = f"@{self._version}" if self._version else ""
        await self.exec_as_agent(
            environment,
            command=(
                "set -euo pipefail; "
                f"{nvm_node_install_snippet()} && "
                'mkdir -p "$HOME/.local" && '
                f'npm install --global --prefix "$HOME/.local" '
                f"{_KIMI_CODE_PACKAGE}{version_spec} && "
                f"{_NODE_PATH_SETUP}kimi --version"
            ),
        )

    def _runtime_env(self) -> dict[str, str]:
        api_key = self._get_env("KIMI_API_KEY")
        if not api_key:
            raise ValueError(
                "KIMI_API_KEY must be set (Kimi Code Console) for kimi-code "
                "trials; the Kimi Code subscription endpoint rejects "
                "unauthenticated requests"
            )
        model = (self.model_name or "kimi-for-coding").rsplit("/", 1)[-1]
        return {
            "KIMI_CODE_HOME": str(_KIMI_CODE_HOME),
            "KIMI_DISABLE_TELEMETRY": "true",
            "KIMI_CODE_NO_AUTO_UPDATE": "true",
            "KIMI_CODE_BACKGROUND_KEEP_ALIVE_ON_EXIT": "true",
            "NO_COLOR": "true",
            "KIMI_MODEL_NAME": model,
            "KIMI_MODEL_BASE_URL": "https://api.kimi.com/coding/v1",
            "KIMI_MODEL_API_KEY": api_key,
            "KIMI_MODEL_MAX_CONTEXT_SIZE": "262144",
        }

    async def _install_superpowers_plugin(
        self, environment: BaseEnvironment, env: dict[str, str]
    ) -> None:
        ref = self.superpowers_ref
        managed = "$KIMI_CODE_HOME/plugins/managed/superpowers"
        installed = json.dumps(
            {
                "version": 1,
                "plugins": [
                    {
                        "id": "superpowers",
                        "root": f"{_KIMI_CODE_HOME}/plugins/managed/superpowers",
                        "source": "github",
                        "enabled": True,
                        "installedAt": "1970-01-01T00:00:00.000Z",
                        "updatedAt": "1970-01-01T00:00:00.000Z",
                        "originalSource": "https://github.com/obra/superpowers",
                        "github": {
                            "owner": "obra",
                            "repo": "superpowers",
                            "ref": {"kind": "tag", "value": ref},
                        },
                    }
                ],
            }
        )
        await self.exec_as_agent(
            environment,
            command=(
                "set -euo pipefail; "
                f"mkdir -p {managed} && "
                "curl -LsSf "
                f"https://codeload.github.com/obra/superpowers/tar.gz/refs/tags/{ref} "
                f"| tar -xz -C {managed} --strip-components=1 && "
                f"printf '%s' {shlex.quote(installed)} > "
                '"$KIMI_CODE_HOME/plugins/installed.json"'
            ),
            env=env,
        )

    @override
    @with_prompt_template
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        if self.skills_dir is None and self.superpowers_ref is None:
            raise ValueError("KimiCodeCli requires injected skills or superpowers_ref")
        if self.smolpowers_config is not None:
            config = json.dumps(self.smolpowers_config, indent=2) + "\n"
            script = (
                "from pathlib import Path; "
                f"config = {config!r}; "
                "Path('/app/.smolpowers.json').write_text(config); "
                "Path('/opt/fixture/.smolpowers.json').write_text(config)"
            )
            await self.exec_as_root(
                environment,
                command=f"python -c {shlex.quote(script)}",
            )
        env = self._runtime_env()
        if self.superpowers_ref is not None:
            await self._install_superpowers_plugin(environment, env)
        elif self.skills_dir is not None:
            await self.exec_as_agent(
                environment,
                command=(
                    'mkdir -p "$KIMI_CODE_HOME/skills" && '
                    f"cp -r {shlex.quote(self.skills_dir)}/* "
                    '"$KIMI_CODE_HOME/skills/" 2>/dev/null || true'
                ),
                env=env,
            )
        prompt = self.lifecycle_instruction + "\n\n" + instruction
        instruction_shell_var = f"harbor_kimi_code_instruction_{uuid.uuid4().hex}"
        instruction_env_var = instruction_shell_var.upper()
        run_env = {**env, instruction_env_var: prompt}
        await self.exec_as_agent(
            environment,
            command=(
                f"{_NODE_PATH_SETUP}"
                f'{instruction_shell_var}="${instruction_env_var}"; '
                f"unset {instruction_env_var}; "
                f'kimi --prompt "${instruction_shell_var}" '
                "--output-format stream-json "
                f"</dev/null 2>&1 | tee {_KIMI_CODE_OUTPUT}"
            ),
            env=run_env,
        )

    def _parse_wire_events(self) -> list[dict[str, Any]]:
        sessions_root = self.logs_dir / ".kimi-code" / "sessions"
        wire_paths = sorted(
            sessions_root.glob("*/session_*/agents/main/wire.jsonl"),
            key=lambda p: p.stat().st_mtime,
        )
        if not wire_paths:
            return []
        events: list[dict[str, Any]] = []
        for line in wire_paths[-1].read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line, strict=False))
            except json.JSONDecodeError:
                continue
        return events

    @staticmethod
    def _group_events_into_steps(
        events: list[dict[str, Any]],
    ) -> list[_KimiCodeWireStep]:
        steps: list[_KimiCodeWireStep] = []
        current: _KimiCodeWireStep | None = None
        for event in events:
            if event.get("type") != "context.append_loop_event":
                continue
            loop_event = event.get("event") or {}
            etype = loop_event.get("type")
            if etype == "step.begin":
                current = _KimiCodeWireStep()
                steps.append(current)
            elif current is None:
                continue
            elif etype == "content.part":
                part = loop_event.get("part") or {}
                if part.get("type") == "text" and part.get("text"):
                    current.text_parts.append(part["text"])
                elif part.get("type") == "think" and part.get("think"):
                    current.reasoning_parts.append(part["think"])
            elif etype == "tool.call":
                current.tool_calls.append(
                    {
                        "id": loop_event.get("toolCallId") or loop_event.get("uuid"),
                        "name": loop_event.get("name") or "",
                        "arguments": loop_event.get("args") or {},
                    }
                )
            elif etype == "tool.result":
                call_id = loop_event.get("toolCallId")
                if call_id:
                    current.tool_results[call_id] = loop_event.get("result") or {}
            elif etype == "step.end":
                usage = loop_event.get("usage")
                if usage:
                    current.token_usage = usage
        return steps

    def _convert_events_to_trajectory(
        self, events: list[dict[str, Any]], session_id: str
    ) -> Trajectory | None:
        wire_steps = self._group_events_into_steps(events)
        if not wire_steps:
            return None

        steps: list[Step] = []
        total_prompt = 0
        total_completion = 0
        total_cached = 0

        for idx, ws in enumerate(wire_steps, start=1):
            message = "".join(ws.text_parts) or "(tool use)"
            reasoning = "".join(ws.reasoning_parts) or None

            tool_calls: list[ToolCall] | None = None
            observation: Observation | None = None
            if ws.tool_calls:
                tool_calls = []
                obs_results: list[ObservationResult] = []
                for tc in ws.tool_calls:
                    tool_calls.append(
                        ToolCall(
                            tool_call_id=tc["id"],
                            function_name=tc["name"],
                            arguments=tc["arguments"],
                        )
                    )
                    result = ws.tool_results.get(tc["id"])
                    if result is not None:
                        output = result.get("output")
                        if isinstance(output, (list, dict)):
                            output = json.dumps(output, ensure_ascii=False)
                        obs_results.append(
                            ObservationResult(
                                source_call_id=tc["id"],
                                content=str(output) if output is not None else None,
                            )
                        )
                if obs_results:
                    observation = Observation(results=obs_results)

            metrics: Metrics | None = None
            if ws.token_usage:
                tu = ws.token_usage
                input_other = tu.get("inputOther", 0) or 0
                output_tok = tu.get("output", 0) or 0
                cache_read = tu.get("inputCacheRead", 0) or 0
                cache_creation = tu.get("inputCacheCreation", 0) or 0
                prompt_tokens = input_other + cache_read + cache_creation
                total_prompt += prompt_tokens
                total_completion += output_tok
                total_cached += cache_read
                extra: dict[str, Any] = {}
                if cache_creation:
                    extra["input_cache_creation"] = cache_creation
                metrics = Metrics(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=output_tok,
                    cached_tokens=cache_read if cache_read else None,
                    extra=extra or None,
                )

            step_kwargs: dict[str, Any] = {
                "step_id": idx,
                "source": "agent",
                "message": message,
                "model_name": self.model_name,
            }
            if tool_calls:
                step_kwargs["tool_calls"] = tool_calls
            if observation:
                step_kwargs["observation"] = observation
            if metrics:
                step_kwargs["metrics"] = metrics
            if reasoning:
                step_kwargs["reasoning_content"] = reasoning
            steps.append(Step(**step_kwargs))

        if not steps:
            return None

        return Trajectory(
            schema_version="ATIF-v1.6",
            session_id=session_id,
            agent=Agent(
                name=self.name(),
                version=self.version() or "unknown",
                model_name=self.model_name,
            ),
            steps=steps,
            final_metrics=FinalMetrics(
                total_prompt_tokens=total_prompt or None,
                total_completion_tokens=total_completion or None,
                total_cached_tokens=total_cached or None,
                total_cost_usd=None,
                total_steps=len(steps),
            ),
        )

    @override
    def populate_context_post_run(self, context: AgentContext) -> None:
        events = self._parse_wire_events()
        if not events:
            return
        session_id = "unknown"
        for event in events:
            if event.get("type") == "turn.prompt":
                session_id = str(event.get("sessionId") or "unknown")
                break
        try:
            trajectory = self._convert_events_to_trajectory(events, session_id)
        except Exception:
            self.logger.exception("Failed to convert kimi-code events to trajectory")
            return
        if not trajectory:
            return
        trajectory_path = self.logs_dir / "trajectory.json"
        try:
            trajectory_path.write_text(
                format_trajectory_json(trajectory.to_json_dict())
            )
        except OSError as exc:
            self.logger.debug(
                f"Failed to write trajectory file {trajectory_path}: {exc}"
            )
        if trajectory.final_metrics:
            fm = trajectory.final_metrics
            context.cost_usd = fm.total_cost_usd
            context.n_input_tokens = fm.total_prompt_tokens or 0
            context.n_output_tokens = fm.total_completion_tokens or 0
            context.n_cache_tokens = fm.total_cached_tokens or 0


class KimiCodeSp(KimiCodeCli):
    @staticmethod
    @override
    def name() -> str:
        return "kimi-code-sp"


class KimiCodeSmol(KimiCodeCli):
    @staticmethod
    @override
    def name() -> str:
        return "kimi-code-smol"


class KimiCodeMix(KimiCodeCli):
    smolpowers_config = MIX_CONFIG

    @staticmethod
    @override
    def name() -> str:
        return "kimi-code-mix"
