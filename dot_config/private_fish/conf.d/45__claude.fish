# Claude Code
alias claude 'claude --allow-dangerously-skip-permissions'

function gsd-update --description "Update GSD across all AI CLIs"
    # ────────────────────────────────────────────────
    # Environments to update — edit this list to add/remove
    # ────────────────────────────────────────────────
    set -l envs \
        claude \
        codex \
        cursor \
        gemini
    # ────────────────────────────────────────────────

    argparse 'statusline' -- $argv
    or return

    set -l args --global
    for env in $envs
        set -a args --$env
    end

    set -l force_statusline no
    if set -q _flag_statusline
        set force_statusline yes
        set -a args --force-statusline
    end

    echo "Will update GSD in the following environments:"
    for env in $envs
        echo "  • $env"
    end
    echo ""
    echo "  scope:             global"
    echo "  force status line: $force_statusline"
    echo ""

    read -P 'Proceed? [y/N] ' -n 1 -l reply
    echo ""
    if test "$reply" != y -a "$reply" != Y
        echo "Aborted."
        return 1
    end

    npx -y get-shit-done-cc@latest $args
end
complete -c gsd-update -f -l statusline -d "Include --force-statusline"
