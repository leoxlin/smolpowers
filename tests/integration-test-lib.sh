#!/usr/bin/env bash

integration_agent_types() {
  local -a agents
  read -r -a agents <<<"${AGENT_TYPES:-claude-code codex kimi-code-cli pi}"
  printf '%s\n' "${agents[@]}"
}

integration_agent_bin() {
  case "$1" in
    claude-code) printf '%s\n' "${CLAUDE_BIN:-claude}" ;;
    codex) printf '%s\n' "${CODEX_BIN:-codex}" ;;
    kimi-code-cli) printf '%s\n' "${KIMI_BIN:-kimi}" ;;
    pi) printf '%s\n' "${PI_BIN:-pi}" ;;
    *)
      printf 'unknown integration agent: %s\n' "$1" >&2
      return 2
      ;;
  esac
}

integration_skill_dir() {
  case "$2" in
    claude-code) printf '%s\n' "$1/.claude/skills" ;;
    codex | kimi-code-cli) printf '%s\n' "$1/.agents/skills" ;;
    pi) printf '%s\n' "$1/.pi/skills" ;;
    *)
      printf 'unknown integration agent: %s\n' "$2" >&2
      return 2
      ;;
  esac
}

integration_require_agent() {
  local agent_bin
  agent_bin="$(integration_agent_bin "$1")"
  command -v "$agent_bin" >/dev/null 2>&1 || {
    printf '%s is not executable: %s\n' "$1" "$agent_bin" >&2
    return 1
  }
}

integration_install_skills() {
  local fixture="$1"
  local agent="$2"
  local source="$3"
  local npx_bin="${NPX_BIN:-npx}"
  shift 3

  (
    cd "$fixture" || exit
    "$npx_bin" --yes skills add "$source" \
      --skill "$@" \
      --agent "$agent" \
      -y \
      --copy
  )
}

integration_assert_skills() {
  local fixture="$1"
  local agent="$2"
  local skill_dir
  local skill
  shift 2
  skill_dir="$(integration_skill_dir "$fixture" "$agent")"

  for skill in "$@"; do
    [[ -f "$skill_dir/$skill/SKILL.md" ]] || {
      printf '%s did not install skill %s at %s\n' \
        "$agent" "$skill" "$skill_dir" >&2
      return 1
    }
  done
}

integration_run_agent() {
  local fixture="$1"
  local agent="$2"
  local prompt="$3"
  local transcript="$4"
  local last_message="$5"
  local agent_bin
  agent_bin="$(integration_agent_bin "$agent")"

  case "$agent" in
    claude-code)
      (
        cd "$fixture" || exit
        "$agent_bin" -p \
          --permission-mode bypassPermissions \
          --no-session-persistence \
          --output-format stream-json \
          --verbose \
          "$prompt"
      ) >"$transcript" 2>&1
      ;;
    codex)
      "$agent_bin" exec \
        --ephemeral \
        --color never \
        --sandbox workspace-write \
        --output-last-message "$last_message" \
        -C "$fixture" \
        "$prompt" </dev/null >"$transcript" 2>&1
      ;;
    kimi-code-cli)
      (
        cd "$fixture" || exit
        "$agent_bin" \
          --auto \
          --output-format stream-json \
          --prompt "$prompt"
      ) >"$transcript" 2>&1
      ;;
    pi)
      (
        cd "$fixture" || exit
        "$agent_bin" \
          --approve \
          --mode json \
          --print \
          --no-session \
          "$prompt"
      ) >"$transcript" 2>&1
      ;;
  esac
}
