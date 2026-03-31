# Base shell environment — locale, editor, TERM

set -gx LC_ALL en_US.UTF-8
set -gx LANG en_US.UTF-8

set -gx EDITOR nvim

# Let Ghostty set TERM=xterm-ghostty for full feature support (undercurl, etc.)
# Only fall back to xterm-256color for other terminals
if test "$TERM_PROGRAM" != ghostty
    set -gx TERM xterm-256color
    set -gx COLORTERM truecolor
end

# Colored man pages via bat
if command -q bat
    set -gx MANPAGER "sh -c 'col -bx | bat -l man -p'"
end
