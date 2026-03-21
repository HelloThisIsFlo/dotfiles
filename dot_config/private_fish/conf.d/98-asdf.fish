# asdf shims — simplified from official docs (https://asdf-vm.com/guide/getting-started.html)
#
# Official snippet uses `set -gx --prepend PATH` with an `if not contains` guard.
# Two problems with that:
#   1. `brew shellenv` uses `fish_add_path --move` which forces Homebrew to the
#      front of PATH, overriding any earlier prepend.
#   2. If shims are already in PATH (e.g. inherited from parent zsh), the guard
#      skips the prepend entirely.
#
# Fix: fish_add_path --move (fights fire with fire), load last (99-) so asdf wins.
# ASDF_DATA_DIR set explicitly (it's the default, but avoids implicit behavior).
set -gx ASDF_DATA_DIR "$HOME/.asdf"
fish_add_path --global --move --path $ASDF_DATA_DIR/shims
