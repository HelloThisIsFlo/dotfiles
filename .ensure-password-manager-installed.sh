#!/bin/sh

password_manager="rbw"

# Exit immediately if already installed.
type "$password_manager" >/dev/null 2>&1 && exit

case "$(uname -s)" in
Darwin)
    brew install "$password_manager"
    ;;
Linux)
    # TODO: decide on install method (cargo, package manager, or pre-built binary)
    echo "$password_manager not found — install it manually: https://github.com/doy/rbw"
    exit 1
    ;;
*)
    echo "unsupported OS"
    exit 1
    ;;
esac
