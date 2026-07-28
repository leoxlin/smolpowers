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
default_activation="full"
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
  printf '{"docsRoot":"%s","stateRoot":"%s","activation":"%s","phases":%s}\n' \
    "$(json_escape "$docs")" "$(json_escape "$state")" \
    "$(json_escape "$3")" "$4"
}

emit_defaults() {
  emit "$default_docs" "$default_state" "$default_activation" "$(default_phases)"
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

# shellcheck disable=SC2016
filter='
  def safe_string:
    type == "string" and length > 0 and (test("[\u0000\n\r]") | not);
  def legacy_phase:
    safe_string or
    (type == "array" and length > 0 and all(safe_string));
  def phase($allow_tdd):
    type == "object" and
    ((keys - (
      ["owner", "companions"] +
      (if $allow_tdd then ["tdd"] else [] end)
    )) | length == 0) and
    (.owner? == null or (.owner | safe_string)) and
    (.companions? == null or (
      .companions | type == "array" and all(safe_string)
    )) and
    (
      ($allow_tdd | not) or
      .tdd? == null or
      .tdd == "proportional" or
      .tdd == "strict"
    );
  def optional_phase($name; $allow_tdd):
    (.phases | has($name) | not) or
    (.phases[$name] | phase($allow_tdd));
  def valid:
    type == "object" and
    ((keys - [
      "activation", "design", "docsRoot", "execute", "finish", "phases", "plan",
      "stateRoot", "tdd"
    ]) | length == 0) and
    (.activation? == null or
      .activation == "lite" or
      .activation == "full" or
      .activation == "ultra") and
    ([.docsRoot?, .stateRoot?] | all(
      . == null or safe_string
    )) and
    (
      if has("phases") then
        (([has("design"), has("plan"), has("execute"), has("finish"), has("tdd")]
          | any) | not) and
        (.phases | type == "object") and
        ((.phases | keys) - ["design", "execute", "finish", "plan"] | length == 0) and
        optional_phase("design"; false) and
        optional_phase("plan"; false) and
        optional_phase("execute"; true) and
        optional_phase("finish"; false)
      else
        ([.design?, .plan?, .execute?, .finish?] | all(
          . == null or legacy_phase
        )) and
        (.tdd? == null or .tdd == "proportional" or .tdd == "strict")
      end
    );
  def nested_phase($name; $default_owner):
    (.phases[$name] // {}) as $phase |
    {
      owner: ($phase.owner // $default_owner),
      companions: ($phase.companions // [])
    };
  def legacy_phase_object($value; $default_owner):
    ($value // $default_owner) as $phase |
    if ($phase | type) == "array" then
      {
        owner: $phase[-1],
        companions: $phase[0:-1]
      }
    else
      {
        owner: $phase,
        companions: []
      }
    end;

  select(valid) |
  {
    docsRoot: (.docsRoot // $default_docs),
    stateRoot: (.stateRoot // $default_state),
    activation: (.activation // $default_activation),
    phases: (
      if has("phases") then
        {
          design: nested_phase("design"; $default_design),
          plan: nested_phase("plan"; $default_plan),
          execute: (
            nested_phase("execute"; $default_execute) +
            {tdd: (.phases.execute.tdd // $default_tdd)}
          ),
          finish: nested_phase("finish"; $default_finish)
        }
      else
        {
          design: legacy_phase_object(.design; $default_design),
          plan: legacy_phase_object(.plan; $default_plan),
          execute: (
            legacy_phase_object(.execute; $default_execute) +
            {tdd: (.tdd // $default_tdd)}
          ),
          finish: legacy_phase_object(.finish; $default_finish)
        }
      end
    )
  }
'

if ! normalized="$(
  jq -ce \
    --arg default_docs "$default_docs" \
    --arg default_state "$default_state" \
    --arg default_activation "$default_activation" \
    --arg default_tdd "$default_tdd" \
    --arg default_design "$default_design" \
    --arg default_plan "$default_plan" \
    --arg default_execute "$default_execute" \
    --arg default_finish "$default_finish" \
    "$filter" "$config_file" 2>/dev/null
)"; then
  fallback
  exit 0
fi

docs="$(jq -r '.docsRoot' <<<"$normalized")"
state="$(jq -r '.stateRoot' <<<"$normalized")"
activation="$(jq -r '.activation' <<<"$normalized")"
phases="$(jq -c '.phases' <<<"$normalized")"
emit "$docs" "$state" "$activation" "$phases"
