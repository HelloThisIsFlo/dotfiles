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

    npx -y @opengsd/gsd-core@latest $args
end
complete -c gsd-update -f -l statusline -d "Include --force-statusline"

function daily-review --description "Start a daily review session with Claude"
    argparse 'e/effort=' 'm/model=' -- $argv
    or return

    set -l effort (if set -q _flag_effort; echo $_flag_effort; else; echo medium; end)
    set -l model_version (if set -q _flag_model; echo $_flag_model; else; echo "4.6"; end)
    set -l model
    switch $model_version
        case 4.6
            set model "claude-opus-4-6[1m]"
        case 4.7
            set model "opus"
        case '*'
            echo "Unknown model version: $model_version (use 4.6 or 4.7)" >&2
            return 1
    end

    set -l daily_review_dir "/Users/flo/Work/Private/Standalone Agent Workspaces/Daily-Review"
    set -l current_date (pdate)

    pushd $daily_review_dir
    claude \
        --allow-dangerously-skip-permissions \
        --model $model \
        --effort $effort \
        "Good morning! Today is $current_date. Let's do the Daily Review! ultrathink"
    popd
end
complete -c daily-review -f
complete -c daily-review -s e -l effort -xa "low medium high" -d "Effort level"
complete -c daily-review -s m -l model -xa "4.6 4.7" -d "Opus version (1M context)"

# function clobsidian --description "Open Obsidian vault in Claude"
#     set -l obsidian_vault "/Users/flo/Work/Private/Dev/HomeLab/TheHome"
#     cd $obsidian_vault
#     claude \
#         --allow-dangerously-skip-permissions \
#         --model $model \
#         --effort $effort \
#         "/open $obsidian_vault"
# end
