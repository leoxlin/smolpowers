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

config_file="$repo_root/.smolpowers.yml"
default_docs="docs/superpowers"
default_state=".superpowers"
default_tdd="proportional"
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

default_phases() {
  printf \
    '{"design":{"owner":"%s","companions":[]},"plan":{"owner":"%s","companions":[]},"execute":{"owner":"%s","companions":[],"tdd":"%s"},"finish":{"owner":"%s","companions":[]}}' \
    "$(json_escape "$default_design")" \
    "$(json_escape "$default_plan")" \
    "$(json_escape "$default_execute")" \
    "$(json_escape "$default_tdd")" \
    "$(json_escape "$default_finish")"
}

emit() {
  local docs state
  docs="$(resolve_path "$1")"
  state="$(resolve_path "$2")"
  printf '{"docsRoot":"%s","stateRoot":"%s","phases":%s}\n' \
    "$(json_escape "$docs")" "$(json_escape "$state")" "$3"
}

emit_defaults() {
  emit "$default_docs" "$default_state" "$(default_phases)"
}

fallback() {
  printf '%s\n' "smolpowers: invalid configuration; using defaults" >&2
  emit_defaults
}

if [[ ! -f "$config_file" ]]; then
  emit_defaults
  exit 0
fi

if ! command -v yq >/dev/null 2>&1; then
  fallback
  exit 0
fi

safe_string='
  . | (
    type == "!!str" and
    length > 0 and
    (contains("\u0000") | not) and
    (contains("\n") | not) and
    (contains("\r") | not)
  )
'

validate_document() {
  local document_count
  document_count="$(yq ea -r '[.] | length' "$config_file" 2>/dev/null)" \
    || return 1
  [[ "$document_count" == 1 ]] || return 1

  yq -e "
    type == \"!!map\" and
    ((keys - [
      \"design\", \"docsRoot\", \"execute\", \"finish\", \"phases\", \"plan\",
      \"stateRoot\", \"tdd\"
    ]) | length == 0) and
    ([.docsRoot, .stateRoot] | all_c(
      . == null or ($safe_string)
    ))
  " "$config_file" >/dev/null 2>&1
}

validate_phase() {
  local name="$1"
  local allowed='["owner", "companions"]'
  local tdd_check=true

  [[ "$(yq -r ".phases | has(\"$name\")" "$config_file" 2>/dev/null)" == true ]] \
    || return 0

  if [[ "$name" == execute ]]; then
    allowed='["owner", "companions", "tdd"]'
    tdd_check='
      .tdd == null or
      .tdd == "proportional" or
      .tdd == "strict"
    '
  fi

  yq -e "
    .phases.$name | (
      type == \"!!map\" and
      ((keys - $allowed) | length == 0) and
      (.owner == null or (.owner | $safe_string)) and
      (.companions == null or (
        .companions | (
          type == \"!!seq\" and all_c($safe_string)
        )
      )) and
      ($tdd_check)
    )
  " "$config_file" >/dev/null 2>&1
}

validate_preferred() {
  yq -e '
    (([
      has("design"), has("plan"), has("execute"), has("finish"), has("tdd")
    ] | any_c(.)) | not) and
    (.phases | type == "!!map") and
    ((.phases | keys) - ["design", "execute", "finish", "plan"] | length == 0)
  ' "$config_file" >/dev/null 2>&1 &&
    validate_phase design &&
    validate_phase plan &&
    validate_phase execute &&
    validate_phase finish
}

validate_legacy() {
  yq -e "
    [.design, .plan, .execute, .finish] | all_c(
      . == null or
      ($safe_string) or
      (
        type == \"!!seq\" and
        length > 0 and
        all_c($safe_string)
      )
    )
  " "$config_file" >/dev/null 2>&1 &&
    yq -e '
      .tdd == null or
      .tdd == "proportional" or
      .tdd == "strict"
    ' "$config_file" >/dev/null 2>&1
}

preferred_phase() {
  local name="$1"
  local default_owner="$2"
  local owner companions

  owner="$(
    DEFAULT_OWNER="$default_owner" \
      yq -r ".phases.$name.owner // strenv(DEFAULT_OWNER)" \
        "$config_file" 2>/dev/null
  )" || return 1
  companions="$(
    yq -o=json -I=0 ".phases.$name.companions // []" \
      "$config_file" 2>/dev/null
  )" || return 1

  printf '{"owner":"%s","companions":%s}' \
    "$(json_escape "$owner")" "$companions"
}

legacy_phase() {
  local name="$1"
  local default_owner="$2"
  local phase_type owner companions

  phase_type="$(yq -r ".$name | type" "$config_file" 2>/dev/null)" \
    || return 1
  if [[ "$phase_type" == "!!seq" ]]; then
    owner="$(yq -r ".${name}[-1]" "$config_file" 2>/dev/null)" || return 1
    companions="$(
      yq -o=json -I=0 ".${name}[0:-1]" "$config_file" 2>/dev/null
    )" || return 1
  elif [[ "$phase_type" == "!!str" ]]; then
    owner="$(yq -r ".$name" "$config_file" 2>/dev/null)" || return 1
    companions='[]'
  else
    owner="$default_owner"
    companions='[]'
  fi

  printf '{"owner":"%s","companions":%s}' \
    "$(json_escape "$owner")" "$companions"
}

if ! validate_document; then
  fallback
  exit 0
fi

if [[ "$(yq -r 'has("phases")' "$config_file" 2>/dev/null)" == true ]]; then
  validate_preferred || {
    fallback
    exit 0
  }
  design="$(preferred_phase design "$default_design")" || exit 1
  plan="$(preferred_phase plan "$default_plan")" || exit 1
  execute="$(preferred_phase execute "$default_execute")" || exit 1
  finish="$(preferred_phase finish "$default_finish")" || exit 1
  tdd="$(
    DEFAULT_TDD="$default_tdd" \
      yq -r '.phases.execute.tdd // strenv(DEFAULT_TDD)' \
        "$config_file" 2>/dev/null
  )" || exit 1
else
  validate_legacy || {
    fallback
    exit 0
  }
  design="$(legacy_phase design "$default_design")" || exit 1
  plan="$(legacy_phase plan "$default_plan")" || exit 1
  execute="$(legacy_phase execute "$default_execute")" || exit 1
  finish="$(legacy_phase finish "$default_finish")" || exit 1
  tdd="$(
    DEFAULT_TDD="$default_tdd" \
      yq -r '.tdd // strenv(DEFAULT_TDD)' "$config_file" 2>/dev/null
  )" || exit 1
fi

docs="$(
  DEFAULT_DOCS="$default_docs" \
    yq -r '.docsRoot // strenv(DEFAULT_DOCS)' "$config_file" 2>/dev/null
)" || exit 1
state="$(
  DEFAULT_STATE="$default_state" \
    yq -r '.stateRoot // strenv(DEFAULT_STATE)' "$config_file" 2>/dev/null
)" || exit 1
phases="$(
  printf \
    '{"design":%s,"plan":%s,"execute":%s,"finish":%s}' \
    "$design" "$plan" \
    "${execute%\}},\"tdd\":\"$(json_escape "$tdd")\"}" \
    "$finish"
)"
emit "$docs" "$state" "$phases"
