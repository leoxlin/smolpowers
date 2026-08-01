import json
from pathlib import Path

from lifecycle_eval import EXPECTED_SKILLS, evaluate_lifecycle


trajectory = json.loads(Path("/logs/agent/trajectory.json").read_text())
agent_name = trajectory["agent"]["name"]
expected = EXPECTED_SKILLS.get(agent_name)
if expected is None:
    print(f"No lifecycle expectation for agent {agent_name}; check skipped.")
    raise SystemExit(0)
result = evaluate_lifecycle(trajectory, expected)
print(json.dumps(result, indent=2))
assert result["passed"], result
