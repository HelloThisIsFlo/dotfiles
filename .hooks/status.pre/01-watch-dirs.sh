#!/bin/bash
set -euo pipefail

# Skip when stdin isn't a terminal (piped, scripted, etc.)
[[ -t 0 ]] || exit 0

# Recursion guard — this script calls chezmoi commands which trigger hooks.
LOCK="/tmp/.chezmoi-watch-lock"
if [[ -f "$LOCK" ]]; then
    exit 0
fi
touch "$LOCK"
trap 'rm -f "$LOCK"' EXIT

# Read watched directories from .chezmoidata/watch_dirs.yaml via chezmoi's template engine.
DIRS=$(chezmoi execute-template '
{{- if index .watch_dirs .os -}}
{{- range index .watch_dirs .os }}{{ . }}
{{ end -}}
{{- end -}}')

[[ -z "$DIRS" ]] && exit 0

# Collect all unmanaged files across watched directories.
NEW_FILES=()
while IFS= read -r dir; do
    [[ -z "$dir" ]] && continue
    target="$HOME/$dir"
    [[ -d "$target" ]] || continue
    while IFS= read -r file; do
        [[ -n "$file" ]] && NEW_FILES+=("$file")
    done < <(chezmoi unmanaged "$target" 2>/dev/null)
done <<< "$DIRS"

[[ ${#NEW_FILES[@]} -eq 0 ]] && exit 0

# Display new files.
echo ""
echo "👀 ${#NEW_FILES[@]} new file(s) in watched directories:"
for i in "${!NEW_FILES[@]}"; do
    # Show as home-relative path.
    rel="${NEW_FILES[$i]#"$HOME"/}"
    echo "   $((i + 1)). $rel"
done
echo ""

# Batch prompt.
read -p "  [a]dd all  [i]gnore all  [s]kip all  [p]ick one-by-one: " choice

SOURCE_DIR=$(chezmoi source-path)

add_file() {
    chezmoi add "$1"
    echo "   Added: ${1#"$HOME"/}"
}

ignore_file() {
    local rel="${1#"$HOME"/}"
    echo "$rel" >> "$SOURCE_DIR/.chezmoiignore"
    echo "   Ignored: $rel"
}

case "$choice" in
    a|A)
        for f in "${NEW_FILES[@]}"; do
            add_file "$f"
        done
        ;;
    i|I)
        for f in "${NEW_FILES[@]}"; do
            ignore_file "$f"
        done
        ;;
    s|S)
        echo "   Skipped — will ask again next time."
        ;;
    p|P)
        for f in "${NEW_FILES[@]}"; do
            rel="${f#"$HOME"/}"
            read -p "  $rel — [a]dd  [i]gnore  [s]kip? " per_choice
            case "$per_choice" in
                a|A) add_file "$f" ;;
                i|I) ignore_file "$f" ;;
                *) echo "   Skipped: $rel" ;;
            esac
        done
        ;;
    *)
        echo "   Skipped — will ask again next time."
        ;;
esac

echo ""
