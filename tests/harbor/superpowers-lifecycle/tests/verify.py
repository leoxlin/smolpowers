import subprocess
from pathlib import Path


subprocess.run(["python", "/opt/verify_finished.py"], check=True)

logs_root = Path("/logs/agent")
transcript = "\n".join(
    path.read_bytes().decode(errors="replace")
    for path in logs_root.rglob("*")
    if path.is_file()
)
for token in (
    "MIXED_SUPERPOWERS_VERIFIED",
    "AssertionError",
    "writing-plans",
    "test-driven-development",
):
    assert token in transcript, token
