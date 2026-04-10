# Personal directories — --move so these win over homebrew/system binaries
fish_add_path --global --move --path $HOME/.local/bin
fish_add_path --global --move --path $HOME/.bin

# GNU coreutils (realpath, sed, date, etc.) ahead of BSD versions.
# macOS ships BSD versions of these tools which lack flags that Linux-written
# scripts assume (e.g. `realpath -e`). Putting gnubin first makes `realpath`,
# `sed`, etc. resolve to the GNU versions, matching Linux behavior.
# Required by: tmux-autoreload (and generally helpful for Linux-flavored scripts).
fish_add_path --global --move --path /opt/homebrew/opt/coreutils/libexec/gnubin