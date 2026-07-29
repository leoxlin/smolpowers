from harbor.agents.installed.base import CliFlag
from harbor.agents.installed.codex import Codex


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
