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
function cmfish -d "Apply fish config + FISH scripts, then reload shell"
    chezmoi apply ~/.config/fish
    or return

    for script in (chezmoi managed --include=scripts | grep FISH)
        chezmoi apply ~/"$script"
    end

    exec fish
end

function cmghostty -d "Apply Ghostty config, then reload Ghostty config"
    # Apply Ghostty config
    chezmoi apply "~/Library/Application Support/com.mitchellh.ghostty"

    # Reload Ghostty config by simulating keypresses
    osascript -e 'tell application "System Events" to tell process "ghostty" to keystroke "," using {command down, shift down}'
end