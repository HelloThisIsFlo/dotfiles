# Chezmoi abbreviations — expand in-place so you see the full command
abbr cm    chezmoi
abbr cma   chezmoi apply
abbr cmd   chezmoi diff
abbr cme   'chezmoi edit --apply'
abbr cmm   chezmoi merge
abbr cmc   chezmoi cat
abbr cmra  'chezmoi re-add'
abbr cms   chezmoi status

abbr cmbrew 'chezmoi edit --apply ~/.Brewfile && chezmoi apply ~/.chezmoiscripts/Z--AFTER/0010-MACOS-brew-bundle.sh'
abbr cmfish 'chezmoi apply ~/.config/fish && exec fish'