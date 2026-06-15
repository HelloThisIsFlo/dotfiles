complete -c codex-sessions -f

complete -c codex-sessions \
    -n "not __fish_seen_subcommand_from archive restore" \
    -a archive \
    -d "Archive active sessions before DATE"

complete -c codex-sessions \
    -n "not __fish_seen_subcommand_from archive restore" \
    -a restore \
    -d "Restore archived sessions from DATE onward"

complete -c codex-sessions \
    -n "__fish_seen_subcommand_from archive restore" \
    -l apply \
    -d "Actually move files"

complete -c codex-sessions \
    -n "__fish_seen_subcommand_from archive restore" \
    -l show-files \
    -d "Show exact files"

complete -c codex-sessions \
    -n "__fish_seen_subcommand_from archive restore" \
    -l top \
    -x \
    -a "8 12 20 50" \
    -d "Project rows to show"

complete -c codex-sessions \
    -n "__fish_seen_subcommand_from archive restore" \
    -l sessions-dir \
    -r \
    -d "Active sessions directory"

complete -c codex-sessions \
    -n "__fish_seen_subcommand_from archive restore" \
    -l archive-dir \
    -r \
    -d "Archive directory"

complete -c codex-sessions \
    -n "__fish_seen_subcommand_from archive restore" \
    -l color \
    -x \
    -a "auto always never" \
    -d "Terminal color mode"

complete -c codex-sessions \
    -s h \
    -l help \
    -d "Show help"
