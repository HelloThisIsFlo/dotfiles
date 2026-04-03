# Generate and cache Fish completions for a CLI tool.
#
# Usage: cache_completions <tool> <command-that-generates-completions>
# Example: cache_completions chezmoi "chezmoi completion fish"
#
# On first run (or fresh machine): generates completions and saves the tool's
# version. On subsequent runs: compares the current version against the cached
# one. Only regenerates if the version changed (i.e. tool was upgraded).
# If the tool isn't installed, does nothing.
#
# Cached files:
#   ~/.config/fish/completions/<tool>.fish    — the completions (Fish auto-loads these)
#   ~/.config/fish/.<tool>-completions-version — version marker (not tracked in git)
#
# Source: Built with Claude on 21/03/2026
function cache_completions --argument-names tool cmd
    command -q $tool; or return

    set -l cache ~/.config/fish/completions/$tool.fish
    set -l current_version (command $tool --version 2>/dev/null; or echo unknown)
    set -l version_file ~/.config/fish/.$tool-completions-version

    if not test -f $cache; or not test -f $version_file; or test "$current_version" != (cat $version_file)
        eval $cmd > $cache
        echo $current_version > $version_file
    end
end
