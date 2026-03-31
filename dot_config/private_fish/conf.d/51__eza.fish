# eza — modern ls replacement
set -gx EZA_ICONS_AUTO 1

alias ls  'eza --group-directories-first --hyperlink --no-quotes'
alias ll  'ls -l --git --header --color-scale=all --time-style=relative --mounts'
alias la  'll -a'
alias lao 'la --octal-permissions'

alias lt    'eza --tree --level=2 --group-directories-first --hyperlink --git-ignore'
alias lt1   'lt --level=1'
alias lt2   'lt --level=2'
alias lt3   'lt --level=3'
alias lt4   'lt --level=4'
alias ltinf 'lt --level=999'
