import json
import sys
from pathlib import Path

from lifecycle_eval import evaluate_lifecycle, expected_skills


trajectory = json.loads(Path("/logs/agent/trajectory.json").read_text())
result = evaluate_lifecycle(trajectory, expected_skills(sys.argv[1]))
print(json.dumps(result, indent=2))
assert result["passed"], result
