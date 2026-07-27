#!/usr/bin/env bash
# Focused parser fixture adapted from Superpowers v6.2.0 task-brief.
# Source: https://github.com/obra/superpowers/blob/3dcbd5c4b48e02263fbf4a3c01e3fe4f81d584d9/skills/subagent-driven-development/scripts/task-brief
set -euo pipefail

plan="$1"
n="$2"

awk -v n="$n" '
  /^```/ { infence = !infence }
  !infence && /^#+[ \t]+Task[ \t]+[0-9]+/ {
    intask = ($0 ~ ("^#+[ \t]+Task[ \t]+" n "([^0-9]|$)"))
  }
  intask { print }
' "$plan"
