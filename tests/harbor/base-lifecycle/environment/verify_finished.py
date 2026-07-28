import subprocess
from pathlib import Path


ROOT = Path("/app")
DOCS = ROOT / ".superpowers/docs"


def only_match(directory: Path, pattern: str) -> Path:
    matches = list(directory.glob(pattern))
    assert len(matches) == 1, matches
    return matches[0]


subprocess.run(
    ["python", "-m", "unittest", "tests/test_greet.py"],
    cwd=ROOT,
    check=True,
)
greet = ROOT / "bin/greet.sh"
assert greet.is_file()
assert greet.stat().st_mode & 0o111

spec = only_match(DOCS / "specs", "*-base-lifecycle-design.md")
plan = only_match(DOCS / "plans", "*-base-lifecycle.md")
assert "**Status:** Current" in spec.read_text()
assert "- [ ]" not in plan.read_text()
assert not (ROOT / ".smolpowers.json").exists()

subprocess.run(
    ["git", "diff", "HEAD", "--quiet", "--", "README.md", "tests/test_greet.py"],
    cwd=ROOT,
    check=True,
)
subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True)
print("BASE_SMOLPOWERS_VERIFIED")
