import shlex
from pathlib import Path
from typing import override

from harbor.agents.installed.codex import Codex
from harbor.agents.installed.pi import Pi
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext
from harbor.models.trial.paths import EnvironmentPaths


class NpxSkillsCodex(Codex):
    """Codex with injected skills installed by the Skills CLI."""

    @override
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        await self.exec_as_agent(
            environment,
            command=(
                "if [ -s ~/.nvm/nvm.sh ]; then . ~/.nvm/nvm.sh; fi; "
                f"npx --yes skills add {shlex.quote(self.skills_dir)} "
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
        await super().run(skill_note + instruction, environment, context)


class SubscriptionPi(Pi):
    """Pi authenticated with the host's OpenAI Codex subscription login."""

    HOST_AUTH_JSON = Path.home() / ".pi" / "agent" / "auth.json"

    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        staged = (EnvironmentPaths.agent_dir / "pi-auth.json").as_posix()
        await self.exec_as_agent(
            environment,
            command=f"mkdir -p {shlex.quote(EnvironmentPaths.agent_dir.as_posix())}",
        )
        await environment.upload_file(self.HOST_AUTH_JSON, staged)
        # upload_file copies as root; fix ownership so the agent user can read it
        if environment.default_user is not None:
            await self.exec_as_root(
                environment,
                command=f"chown {environment.default_user} {shlex.quote(staged)}",
            )
        await self.exec_as_agent(
            environment,
            command=(
                'mkdir -p "$HOME/.pi/agent" && '
                f'cp {shlex.quote(staged)} "$HOME/.pi/agent/auth.json" && '
                'chmod 600 "$HOME/.pi/agent/auth.json"'
            ),
        )
        await super().run(instruction, environment, context)
