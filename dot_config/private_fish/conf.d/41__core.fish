# Core shell config — aliases, abbreviations, navigation
alias vi  nvim
alias vim nvim

# ── Navigation ───────────────────────────────────────────────────────

# Dynamic multi-dot: .. → cd ../, ... → cd ../../, .... → cd ../../../, etc.
function _multicd
    echo cd (string repeat -n (math (string length -- $argv[1]) - 1) ../)
end
abbr -a dotdot --regex '^\.\.+$' --function _multicd

# ── File operations ──────────────────────────────────────────────────

# Create a new executable bash script with boilerplate and open in nvim
function vix -a filename --description "Create executable bash script and open in nvim"
    test -z "$filename"; and echo "Usage: vix FILENAME"; and return 1
    printf '#!/bin/bash\nset -euo pipefail\nDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"\n\ncd "$DIR"\n\n\n\ncd - >/dev/null\n' > $filename
    chmod u+x $filename
    nvim -c 'startinsert' +7 $filename
end

function mkcd -a dir_name --description "Create directory and cd into it"
    test -z "$dir_name"; and echo "Usage: mkcd DIRNAME"; and return 1
    mkdir -p $dir_name; and cd $dir_name
end

# Make executable the most recently created file in cwd
function x --description "chmod +x the most recently created file in cwd"
    chmod u+x (command ls -tr | tail -1)
end
