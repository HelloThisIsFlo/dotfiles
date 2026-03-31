# fzf.fish plugin configuration (PatrickF1/fzf.fish)

# Use eza for directory previews (icons via EZA_ICONS_AUTO)
set fzf_preview_dir_cmd eza --all --color=always

# Use delta-autotheme for git diff previews (Git Log + Git Status searches)
set fzf_diff_highlighter delta-autotheme --paging=never --width=20

# Show hidden files in Search Directory
set fzf_fd_opts --hidden

# History timestamp format
set fzf_history_time_format "%Y-%m-%d %H:%M"
