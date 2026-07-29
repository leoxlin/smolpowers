import subprocess
from pathlib import Path


ROOT = Path("/app")
DOCS = ROOT / "docs/superpowers"
BASELINE = Path("/opt/fixture")


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

for protected in (".gitignore", "tests/test_greeting.py"):
    assert (ROOT / protected).read_bytes() == (BASELINE / protected).read_bytes()
assert (ROOT / "greeting.py").read_bytes() != (BASELINE / "greeting.py").read_bytes()
print("BASE_SMOLPOWERS_VERIFIED")
