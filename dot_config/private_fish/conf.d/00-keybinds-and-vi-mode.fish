# List active bindings: `bind`
# See also: Ghostty keybinds (~/.config/ghostty/features/keybinds)

if status is-interactive
    fish_vi_key_bindings

    # Word-deletion bindings
    #
    #              soft                                soft/hard                            hard
    #   ┌──────────────────────────────┬──────────────────────────────────────┬──────────────────────────────┐
    #   │  backward-kill-word          │  backward-kill-path-component       │  backward-kill-token         │
    #   │  stops at punctuation        │  stops at / = :                     │  stops at whitespace only    │
    #   └──────────────────────────────┴──────────────────────────────────────┴──────────────────────────────┘
    #
    # macOS: alt = soft, ctrl = hard (matches system-wide Option+Backspace behavior)
    # Linux: alt = hard, ctrl = soft (no platform convention, so more aggressive default)
    set -l soft backward-kill-word
    set -l hard backward-kill-token
    set -l soft_fwd kill-word
    set -l hard_fwd kill-token

    if fish_in_macos_terminal
        bind alt-backspace $soft
        bind ctrl-alt-h $soft
        bind ctrl-backspace $hard
        bind alt-delete $soft_fwd
        bind ctrl-delete $hard_fwd

        bind -M insert alt-backspace $soft
        bind -M insert ctrl-alt-h $soft
        bind -M insert ctrl-backspace $hard
        bind -M insert alt-delete $soft_fwd
        bind -M insert ctrl-delete $hard_fwd
    else
        bind alt-backspace $hard
        bind ctrl-alt-h $hard
        bind ctrl-backspace $soft
        bind alt-delete $hard_fwd
        bind ctrl-delete $soft_fwd

        bind -M insert alt-backspace $hard
        bind -M insert ctrl-alt-h $hard
        bind -M insert ctrl-backspace $soft
        bind -M insert alt-delete $hard_fwd
        bind -M insert ctrl-delete $soft_fwd
    end
end
