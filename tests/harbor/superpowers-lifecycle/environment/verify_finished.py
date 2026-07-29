import subprocess
from pathlib import Path


ROOT = Path("/app")


def only_match(directory: Path, pattern: str) -> Path:
    matches = list(directory.glob(pattern))
    assert len(matches) == 1, matches
    return matches[0]


subprocess.run(
    ["python", "-m", "unittest", "tests/test_greeting.py"],
    cwd=ROOT,
    check=True,
)

spec = only_match(ROOT / "artifacts/specs", "*-mixed-superpowers-design.md")
plan = only_match(ROOT / "artifacts/plans", "*-mixed-superpowers.md")
assert "**Status:** Current" in spec.read_text()
assert "> **For agentic workers:** REQUIRED SUB-SKILL:" in plan.read_text()
assert "- [ ]" not in plan.read_text()

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
subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True)
print("MIXED_SUPERPOWERS_VERIFIED")
