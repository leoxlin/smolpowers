import json
import os
from pathlib import Path

from lifecycle_eval import evaluate_lifecycle


trajectory = json.loads(Path("/logs/agent/trajectory.json").read_text())
result = evaluate_lifecycle(
    trajectory,
    json.loads(os.environ["EXPECTED_SKILLS"]),
)
print(json.dumps(result, indent=2))
assert result["passed"], result
