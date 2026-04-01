# Core shell config — aliases, abbreviations, navigation
alias vi  nvim
alias vim nvim

# ── Navigation ───────────────────────────────────────────────────────

# Inline expansions provided by puffer-fish plugin (nickeb96/puffer-fish):
#   ...  ->  ../..    (works with any command, tab-completes mid-path)
#   !!   ->  last command  (e.g. sudo !!)
#   !$   ->  last argument of previous command
#   !*   ->  all arguments of previous command

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

abbr -a rm    'rm -r'
abbr -a cp    'cp -r'
abbr -a ln    'ln -s'
abbr -a md    'mkdir -p'
abbr -a mkdir 'mkdir -p'

# ── Clipboard ────────────────────────────────────────────────────────

abbr -a y --position anywhere '| pbcopy'
abbr -a p  'pbpaste |'
abbr -a pp 'pbpaste >'
