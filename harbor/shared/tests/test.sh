#!/usr/bin/env bash

skills_in_order=0
requested_change_completed=0

python /tests/verify_lifecycle.py && skills_in_order=1
python /tests/verify.py && requested_change_completed=1

mkdir -p /logs/verifier
python -c "
import json
json.dump(
    {
        'skills_in_order': $skills_in_order,
        'requested_change_completed': $requested_change_completed,
    },
    open('/logs/verifier/reward.json', 'w'),
)
"
exit 0
