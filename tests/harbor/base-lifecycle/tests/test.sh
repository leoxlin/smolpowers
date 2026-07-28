#!/usr/bin/env bash

if python /tests/verify.py; then
  reward=1
else
  reward=0
fi

mkdir -p /logs/verifier
printf '%s\n' "$reward" > /logs/verifier/reward.txt
exit 0
