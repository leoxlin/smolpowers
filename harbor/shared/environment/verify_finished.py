import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path("/app")
BASELINE = Path("/opt/fixture")
CONFIG = ROOT / ".smolpowers.json"


def only_match(directory: Path, pattern: str) -> Path:
    matches = list(directory.glob(pattern))
    assert len(matches) == 1, matches
    return matches[0]


subprocess.run(
    ["python", "-m", "unittest", "discover", "-s", "tests"],
    cwd=ROOT,
    check=True,
)

sys.path.insert(0, str(ROOT))
from app import create_app  # noqa: E402

with tempfile.TemporaryDirectory() as directory:
    database = Path(directory) / "links.sqlite3"
    first_client = create_app({"TESTING": True, "DATABASE": database}).test_client()
    link = first_client.post(
        "/links", json={"url": "https://example.com/persistent"}
    ).get_json()
    with sqlite3.connect(database) as connection:
        saved_link = connection.execute("SELECT code, url FROM links").fetchone()
    assert saved_link == (link["code"], link["url"])
    restarted_client = create_app(
        {"TESTING": True, "DATABASE": database}
    ).test_client()
    response = restarted_client.get(f"/{link['code']}")
    assert response.status_code == 302
    assert response.headers["Location"] == link["url"]

config = json.loads(CONFIG.read_text()) if CONFIG.exists() else {}
docs = ROOT / config.get("specDir", "docs/superpowers")
spec = only_match(docs / "specs", "*-design.md")
plan = only_match(docs / "plans", "*.md")
assert plan.stem == spec.stem.removesuffix("-design")

protected = [".gitignore", "requirements.txt"]
if config:
    protected.append(".smolpowers.json")
else:
    protected.append("AGENTS.md")
for relative_path in protected:
    assert (ROOT / relative_path).read_bytes() == (
        BASELINE / relative_path
    ).read_bytes()
assert (ROOT / "app.py").read_bytes() != (BASELINE / "app.py").read_bytes()

phase_log = ROOT / config.get("stateDir", ".superpowers") / "phase-calls.log"
if phase_log.exists():
    calls = phase_log.read_text().splitlines()
    configured_overrides = [
        name
        for name, phase in config.get("phases", {}).items()
        if phase.get("owner", "").startswith("integration-")
    ]
    assert [call.split("|", 1)[0] for call in calls] == configured_overrides
    expected_roots = f"|{docs}|{phase_log.parent}"
    assert all(call.endswith(expected_roots) for call in calls)
