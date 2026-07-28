import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"


def load(path: str):
    return json.loads((ROOT / path).read_text())


def test_harness_manifests_and_versions() -> None:
    claude = load(".claude-plugin/plugin.json")
    claude_market = load(".claude-plugin/marketplace.json")
    kimi = load(".kimi-plugin/plugin.json")
    codex = load(".codex-plugin/plugin.json")
    codex_market = load(".agents/plugins/marketplace.json")
    hooks = load("hooks/hooks.json")
    package = load("package.json")

    for manifest in [claude, kimi, codex, package]:
        assert manifest["name"] == "smolpowers"
        assert manifest["version"] == VERSION

    assert claude["author"] == {
        "name": "Leo Xuzhang Lin",
        "email": "me@leoxlin.com",
    }
    entry = claude_market["plugins"][0]
    assert entry["name"] == "smolpowers" and entry["version"] == VERSION

    assert kimi["skills"] == "./skills/"
    assert kimi["sessionStart"]["skill"] == "smol-activate"

    assert codex["skills"] == "./skills/"
    assert codex["hooks"] == {}
    codex_entry = codex_market["plugins"][0]
    assert codex_entry["name"] == "smolpowers"
    assert codex_entry["source"] == {"source": "url", "url": "./"}
    assert codex_entry["policy"] == {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL",
    }

    session_hook = hooks["hooks"]["SessionStart"][0]
    assert session_hook["matcher"] == "startup|clear|compact"
    command = session_hook["hooks"][0]
    assert command["shell"] == "bash"
    assert command["command"].endswith('run-hook.cmd" session-start')

    assert package["type"] == "module"
    assert package["pi"]["skills"] == ["./skills"]
    assert package["pi"]["extensions"] == ["./.pi/extensions/smolpowers.js"]
    assert "dependencies" not in package
