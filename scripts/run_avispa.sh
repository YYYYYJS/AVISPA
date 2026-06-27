#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

resolve_cmd() {
  local name="$1"
  local fallback="$2"

  if command -v "$name" >/dev/null 2>&1; then
    command -v "$name"
    return 0
  fi

  if [[ -n "$fallback" && -x "$fallback" ]]; then
    printf '%s\n' "$fallback"
    return 0
  fi

  printf 'Required command not found: %s\n' "$name" >&2
  return 1
}

hlpsl2if_bin="$(resolve_cmd hlpsl2if /home/span/span/bin/translator/hlpsl2if)"
ofmc_bin="$(resolve_cmd ofmc /home/span/span/bin/backends/ofmc/ofmc)"
clatse_bin="$(resolve_cmd cl-atse /home/span/span/bin/backends/cl/cl-atse)"

mkdir -p if results

run_model() {
  local stem="$1"
  local hlpsl_file="models/${stem}.hlpsl"
  local if_source="models/${stem}.if"
  local if_target="if/${stem}.if"
  local log_prefix="results/${stem}"

  "$hlpsl2if_bin" "$hlpsl_file" > "${log_prefix}_hlpsl2if.txt" 2>&1
  cp -f "$if_source" "$if_target"
  rm -f "$if_source"
  "$ofmc_bin" "$if_target" > "${log_prefix}_ofmc.txt" 2>&1

  if command -v timeout >/dev/null 2>&1; then
    timeout 60 "$clatse_bin" "$if_target" > "${log_prefix}_clatse.txt" 2>&1
  else
    "$clatse_bin" "$if_target" > "${log_prefix}_clatse.txt" 2>&1
  fi
}

run_model spaka_local_auth_key_update
run_model spaka_cross_region
