#!/usr/bin/env bash
set -euo pipefail

if (( $# > 1 )); then
  printf '%s\n' "usage: load-config.sh [repo-root]" >&2
  exit 2
fi

if (( $# == 1 )); then
  repo_root="$(cd "$1" && pwd -P)"
else
  repo_root="$(git rev-parse --show-toplevel)"
fi

config_file="$repo_root/.smolpowers.json"
default_docs="docs/superpowers"
default_state=".superpowers"

json_escape() {
  local value="$1"
  value="${value//\\/\\\\}"
  value="${value//\"/\\\"}"
  value="${value//$'\n'/\\n}"
  value="${value//$'\r'/\\r}"
  value="${value//$'\t'/\\t}"
  printf '%s' "$value"
}

resolve_path() {
  case "$1" in
    /* | [A-Za-z]:[\\/]* | \\\\*) printf '%s' "$1" ;;
    *) printf '%s/%s' "$repo_root" "$1" ;;
  esac
}

emit() {
  local docs state
  docs="$(resolve_path "$1")"
  state="$(resolve_path "$2")"
  printf '{"docsRoot":"%s","stateRoot":"%s"}\n' \
    "$(json_escape "$docs")" "$(json_escape "$state")"
}

fallback() {
  printf '%s\n' "smolpowers: invalid configuration; using defaults" >&2
  emit "$default_docs" "$default_state"
}

if [[ ! -f "$config_file" ]]; then
  emit "$default_docs" "$default_state"
  exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
  fallback
  exit 0
fi

validation='
  type == "object" and
  ((keys - ["docsRoot", "stateRoot"]) | length == 0) and
  ([.docsRoot?, .stateRoot?] | all(
    . == null or
    (type == "string" and length > 0 and (test("[\\u0000\\n\\r]") | not))
  ))
'

if ! jq -e "$validation" "$config_file" >/dev/null 2>&1; then
  fallback
  exit 0
fi

if ! docs="$(
  jq -r --arg default "$default_docs" '.docsRoot // $default' "$config_file"
)" || ! state="$(
  jq -r --arg default "$default_state" '.stateRoot // $default' "$config_file"
)"; then
  fallback
  exit 0
fi

emit "$docs" "$state"
