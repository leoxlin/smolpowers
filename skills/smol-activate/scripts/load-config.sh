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
default_design="smolpowers:smol-design"
default_plan="smolpowers:smol-plan"
default_execute="smolpowers:smol-execute"
default_finish="smolpowers:smol-finish"

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
  printf '{"docsRoot":"%s","stateRoot":"%s","design":%s,"plan":%s,"execute":%s,"finish":%s}\n' \
    "$(json_escape "$docs")" "$(json_escape "$state")" \
    "$3" "$4" "$5" "$6"
}

json_string() {
  printf '"%s"' "$(json_escape "$1")"
}

emit_defaults() {
  emit "$default_docs" "$default_state" \
    "$(json_string "$default_design")" "$(json_string "$default_plan")" \
    "$(json_string "$default_execute")" "$(json_string "$default_finish")"
}

fallback() {
  printf '%s\n' "smolpowers: invalid configuration; using defaults" >&2
  emit_defaults
}

if [[ ! -f "$config_file" ]]; then
  emit_defaults
  exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
  fallback
  exit 0
fi

validation='
  def safe_string:
    type == "string" and length > 0 and (test("[\u0000\n\r]") | not);
  def phase:
    safe_string or
    (type == "array" and length > 0 and all(safe_string));

  type == "object" and
  ((keys - ["design", "docsRoot", "execute", "finish", "plan", "stateRoot"]) | length == 0) and
  ([.docsRoot?, .stateRoot?] | all(
    . == null or
    safe_string
  )) and
  ([.design?, .plan?, .execute?, .finish?] | all(
    . == null or
    phase
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

if ! design="$(
  jq -c --arg default "$default_design" '.design // $default' "$config_file"
)" || ! plan="$(
  jq -c --arg default "$default_plan" '.plan // $default' "$config_file"
)" || ! execute="$(
  jq -c --arg default "$default_execute" '.execute // $default' "$config_file"
)" || ! finish="$(
  jq -c --arg default "$default_finish" '.finish // $default' "$config_file"
)"; then
  fallback
  exit 0
fi

emit "$docs" "$state" "$design" "$plan" "$execute" "$finish"
