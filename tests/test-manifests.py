#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"


def load(path: str):
    return json.loads((ROOT / path).read_text())


claude = load(".claude-plugin/plugin.json")
claude_market = load(".claude-plugin/marketplace.json")
kimi = load(".kimi-plugin/plugin.json")
codex = load(".codex-plugin/plugin.json")
codex_market = load(".agents/plugins/marketplace.json")
hooks = load("hooks/hooks.json")
package = load("package.json")

for label, manifest in {
    "Claude": claude,
    "Kimi": kimi,
    "Codex": codex,
    "Pi": package,
}.items():
    assert manifest["name"] == "smolpowers", f"{label}: wrong name"
    assert manifest["version"] == VERSION, f"{label}: version drift"

assert claude["author"] == {
    "name": "Leo Xuzhang Lin",
    "email": "me@leoxlin.com",
}
entry = claude_market["plugins"][0]
assert entry["name"] == "smolpowers" and entry["version"] == VERSION

assert kimi["skills"] == "./skills/"
assert kimi["sessionStart"]["skill"] == "smol-activate"
instructions = kimi["skillInstructions"]
for token in [
    "AskUserQuestion",
    "TodoList",
    "Agent",
    "Skill",
    "Read",
    "Write",
    "Edit",
    "Bash",
    "Grep",
    "Glob",
    "FetchURL",
    "WebSearch",
]:
    assert token in instructions, f"Kimi mapping misses {token}"
for unsupported in ["tools", "commands", "apps", "inject", "bootstrap"]:
    assert unsupported not in kimi, f"Kimi manifest contains unsupported {unsupported}"

assert codex["skills"] == "./skills/"
assert codex["hooks"] == {}, "Codex must suppress Claude hook auto-discovery"
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

license_text = (ROOT / "LICENSE").read_text()
assert "Copyright (c) 2025 Jesse Vincent" in license_text
assert "Copyright (c) 2026 Leo Xuzhang Lin" in license_text
assert ".superpowers/" in (ROOT / ".gitignore").read_text().splitlines()

print("Harness manifests and synchronized versions look good")
