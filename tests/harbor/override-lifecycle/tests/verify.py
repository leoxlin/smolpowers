import subprocess
from pathlib import Path


ROOT = Path("/app")
DOCS = ROOT / "artifacts"
STATE = ROOT / ".smol-state"


def only_match(directory: Path, pattern: str) -> Path:
    matches = list(directory.glob(pattern))
    assert len(matches) == 1, matches
    return matches[0]


calls = (STATE / "phase-calls.log").read_text().splitlines()
assert calls == [
    f"design|{DOCS}|{STATE}",
    f"plan|{DOCS}|{STATE}",
    f"execute|{DOCS}|{STATE}",
    f"finish|{DOCS}|{STATE}",
]

subprocess.run(
    ["python", "-m", "unittest", "tests/test_greeting.py"],
    cwd=ROOT,
    check=True,
)
subprocess.run(
    [
        "git",
        "diff",
        "HEAD",
        "--quiet",
        "--",
        ".gitignore",
        ".smolpowers.json",
        "tests/test_greeting.py",
    ],
    cwd=ROOT,
    check=True,
)
production_diff = subprocess.run(
    ["git", "diff", "--quiet", "HEAD", "--", "greeting.py"],
    cwd=ROOT,
)
assert production_diff.returncode == 1

spec = only_match(DOCS / "specs", "*-override-lifecycle-design.md")
plan = only_match(DOCS / "plans", "*-override-lifecycle.md")
assert "Status: Current" in spec.read_text()
assert "- [ ]" not in plan.read_text()
assert not (ROOT / "docs/superpowers").exists()
assert not (ROOT / ".superpowers").exists()
subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True)
