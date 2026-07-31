import json
import shlex
from typing import override

from harbor.agents.installed.codex import Codex
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

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
