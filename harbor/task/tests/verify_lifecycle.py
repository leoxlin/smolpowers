import json
from pathlib import Path

from lifecycle_eval import EXPECTED_SKILLS, evaluate_lifecycle


trajectory = json.loads(Path("/logs/agent/trajectory.json").read_text())
result = evaluate_lifecycle(
    trajectory,
    EXPECTED_SKILLS[trajectory["agent"]["name"]],
)
print(json.dumps(result, indent=2))
assert result["passed"], result
