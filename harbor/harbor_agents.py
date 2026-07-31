import shlex
from pathlib import Path

from harbor.agents.installed.pi import Pi
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext
from harbor.models.trial.paths import EnvironmentPaths


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
