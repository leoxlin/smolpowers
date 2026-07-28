import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_pi_extension() -> None:
    node = shutil.which("node")
    assert node, "node is required to test the Pi extension"
    subprocess.run(
        [node, "--test", str(ROOT / "tests/test-pi.mjs")],
        check=True,
    )
