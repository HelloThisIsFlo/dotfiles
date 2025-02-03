#!/bin/sh

# exit immediately if password-manager-binary is already in $PATH
type bw >/dev/null 2>&1 && exit

case "$(uname -s)" in
Darwin)
    brew install bitwarden-cli
    ;;
Linux)
    # commands to install password-manager-binary on Linux
    ;;
*)
    echo "unsupported OS"
    exit 1
    ;;
esac
