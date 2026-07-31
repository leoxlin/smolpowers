import shlex
from pathlib import Path

from harbor.agents.installed.base import CliFlag
from harbor.agents.installed.codex import Codex
from harbor.agents.installed.pi import Pi
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext
from harbor.models.trial.paths import EnvironmentPaths


class PluginCodex(Codex):
    CLI_FLAGS = [
        *Codex.CLI_FLAGS,
        CliFlag(
            "bypass_hook_trust",
            cli="--dangerously-bypass-hook-trust",
            type="bool",
            default=True,
        ),
    ]

    def _build_register_skills_command(self) -> str:
        skills = (
            '["smol-activate","smol-design","smol-execute","smol-finish","smol-plan"]'
        )
        return (
            "if [ -s ~/.nvm/nvm.sh ]; then . ~/.nvm/nvm.sh; fi; "
            "codex plugin marketplace add /opt/smolpowers --json "
            "> /logs/agent/marketplace-install.json && "
            "codex plugin add smolpowers@smolpowers --json "
            "> /logs/agent/plugin-install.json && "
            "codex plugin list --json > /logs/agent/plugin-list.json && "
            'plugin_root="$(jq -r .installedPath '
            '/logs/agent/plugin-install.json)" && '
            "for skill in smol-activate smol-design smol-execute smol-finish "
            'smol-plan; do test -f "$plugin_root/skills/$skill/SKILL.md"; done && '
            f"printf '%s\\n' '{{\"skills\":{skills}}}' "
            "> /logs/agent/skill-loading.json"
        )


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
