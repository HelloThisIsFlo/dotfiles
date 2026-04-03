# mise — modern asdf replacement

# mise auto-activates in fish: MISE_FISH_AUTO_ACTIVATE = 1 by default
# Using manual activation because it's more explicit (auto-activation magically adds paths at the end of PATH)
set -gx MISE_FISH_AUTO_ACTIVATE 0
# See 89__mise-paths.fish for activation

# Default, but making it explicit so it's the same across all machines
set -gx MISE_CONFIG_DIR $HOME/.config/mise
