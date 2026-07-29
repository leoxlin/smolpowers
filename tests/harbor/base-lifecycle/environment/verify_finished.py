import subprocess
from pathlib import Path


ROOT = Path("/app")
DOCS = ROOT / "docs/superpowers"


def only_match(directory: Path, pattern: str) -> Path:
    matches = list(directory.glob(pattern))
    assert len(matches) == 1, matches
    return matches[0]


subprocess.run(
    ["python", "-m", "unittest", "tests/test_greeting.py"],
    cwd=ROOT,
    check=True,
)

spec = only_match(DOCS / "specs", "*-base-lifecycle-design.md")
plan = only_match(DOCS / "plans", "*-base-lifecycle.md")
assert "**Status:** Current" in spec.read_text()
assert "- [ ]" not in plan.read_text()
assert not (ROOT / ".smolpowers.json").exists()

subprocess.run(
    ["git", "diff", "HEAD", "--quiet", "--", ".gitignore", "tests/test_greeting.py"],
    cwd=ROOT,
    check=True,
)
production_diff = subprocess.run(
    ["git", "diff", "--quiet", "HEAD", "--", "greeting.py"],
    cwd=ROOT,
)
assert production_diff.returncode == 1
subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True)
print("BASE_SMOLPOWERS_VERIFIED")
