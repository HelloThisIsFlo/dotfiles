#!/bin/bash
set -euo pipefail

HOOK_DIR="$(dirname "$0")/$1"
[[ -d "$HOOK_DIR" ]] || exit 0

for script in "$HOOK_DIR"/*.sh; do
    [[ -x "$script" ]] && "$script"
done
