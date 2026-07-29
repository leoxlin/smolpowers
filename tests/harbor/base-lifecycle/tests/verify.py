import json
import subprocess
from pathlib import Path


subprocess.run(["python", "/opt/verify_finished.py"], check=True)

logs_root = Path("/logs/agent")
install = json.loads((logs_root / "plugin-install.json").read_text())
assert install["pluginId"] == "smolpowers@smolpowers"

plugin_list = json.loads((logs_root / "plugin-list.json").read_text())
assert [
    (plugin["pluginId"], plugin["installed"], plugin["enabled"])
    for plugin in plugin_list["installed"]
] == [("smolpowers@smolpowers", True, True)]

skill_loading = json.loads((logs_root / "skill-loading.json").read_text())
assert skill_loading["skills"] == [
    "smol-activate",
    "smol-design",
    "smol-execute",
    "smol-finish",
    "smol-plan",
]

activation = json.loads((logs_root / "smolpowers-activation.json").read_text())
assert activation == {
    "hookEventName": "SessionStart",
    "skill": "smol-activate",
    "activation": "full",
}

transcript = "\n".join(
    path.read_bytes().decode(errors="replace")
    for path in logs_root.rglob("*")
    if path.is_file()
)
assert "BASE_SMOLPOWERS_VERIFIED" in transcript
