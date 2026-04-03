#!/bin/bash
set -euo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd "$DIR"

mise implode -y 2>/dev/null || true
chezmoi state reset --force
rm -rf ~/.config/fish

cd - >/dev/null
