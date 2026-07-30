import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path("/app")
BASELINE = Path("/opt/fixture")


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
from app import create_app

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

spec = only_match(ROOT / "artifacts/specs", "*-mixed-superpowers-design.md")
plan = only_match(ROOT / "artifacts/plans", "*-mixed-superpowers.md")
assert "**Status:** Current" in spec.read_text()
assert "> **For agentic workers:** REQUIRED SUB-SKILL:" in plan.read_text()
assert "- [ ]" not in plan.read_text()

for protected in (
    ".gitignore",
    ".smolpowers.json",
    "requirements.txt",
    "tests/test_api.py",
):
    assert (ROOT / protected).read_bytes() == (BASELINE / protected).read_bytes()
assert (ROOT / "app.py").read_bytes() != (BASELINE / "app.py").read_bytes()
print("MIXED_SUPERPOWERS_VERIFIED")
