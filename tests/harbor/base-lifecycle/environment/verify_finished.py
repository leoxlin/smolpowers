import re
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

spec = only_match(DOCS / "specs", "*-design.md")
plan = only_match(DOCS / "plans", "*.md")
assert plan.stem == spec.stem.removesuffix("-design")
checkbox_states = re.findall(r"^- \[([ xX])\]", plan.read_text(), re.MULTILINE)
assert checkbox_states
assert all(state.lower() == "x" for state in checkbox_states)
assert not (ROOT / ".smolpowers.json").exists()

for protected in ("AGENTS.md", ".gitignore", "tests/test_greeting.py"):
    assert (ROOT / protected).read_bytes() == (BASELINE / protected).read_bytes()
assert (ROOT / "greeting.py").read_bytes() != (BASELINE / "greeting.py").read_bytes()
print("BASE_SMOLPOWERS_VERIFIED")
