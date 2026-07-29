import subprocess
from pathlib import Path


subprocess.run(["python", "/opt/verify_finished.py"], check=True)

logs_root = Path("/logs/agent")
transcript = "\n".join(
    path.read_bytes().decode(errors="replace")
    for path in logs_root.rglob("*")
    if path.is_file()
)
assert "BASE_SMOLPOWERS_VERIFIED" in transcript
