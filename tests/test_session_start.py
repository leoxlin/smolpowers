import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*command: str) -> str:
    env = os.environ.copy()
    env["CLAUDE_PLUGIN_ROOT"] = str(ROOT)
    return subprocess.run(
        command,
        capture_output=True,
        check=True,
        env=env,
        text=True,
    ).stdout


def test_session_start_bootstrap() -> None:
    output = run("bash", str(ROOT / "hooks/session-start"))
    payload = json.loads(output)
    assert set(payload) == {"hookSpecificOutput"}
    hook = payload["hookSpecificOutput"]
    assert hook["hookEventName"] == "SessionStart"
    context = hook["additionalContext"]
    assert "smolpowers:smol-activate bootstrap" in context
    assert "Design → Plan → Execute → Finish" in context
    assert "TODO" not in context


def test_hook_wrapper_delegates_to_session_start() -> None:
    direct = run("bash", str(ROOT / "hooks/session-start"))
    wrapped = run("bash", str(ROOT / "hooks/run-hook.cmd"), "session-start")
    assert wrapped == direct
