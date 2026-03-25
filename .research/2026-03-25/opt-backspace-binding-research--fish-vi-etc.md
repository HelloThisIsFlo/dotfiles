
# Word Deletion: What to Bind Option+Backspace To?

## Decision

Use `backward-kill-word` (small word) everywhere, with minimal config:

- **Ghostty:** `macos-option-as-alt = true`
  - Sends `\x1b\x7f` for Option+Backspace
  - No app-specific keybind hacks — remapping happens in each app
- **Fish:** `backward-kill-word` (default for Option+BS on macOS)
- **Vim/Neovim:** `<C-w>` in insert mode (stock behaviour)
- **Zsh:** `WORDCHARS=''` (if I ever switch back)

## Why this

- **Consistency over optimality.** Small word isn't the sweet spot
  (that's path-component at 8 presses), but it works everywhere
  without custom functions
- **Matches Chrome/Electron.** Most GUI apps I use daily (browsers,
  Claude Desktop, VS Code) already behave this way
- **Transparent.** `\x1b\x7f` is sent from the terminal emulator,
  each app interprets it natively — no per-app keybind overrides
- **Minimal config.** One Ghostty setting. Minimal Fish config. Minimal
  Vim config. I understand every line involved
- **Close enough.** Fish and Vim disagree on underscores (20 vs 18
  presses), but muscle memory still transfers

## The problem

Option+Backspace behaves differently everywhere — even within macOS:

- **Native Cocoa** (TextEdit, Notes)
  - Groups punctuation with words
  - `foo-bar.test.ts` = 2 units (`bar.test.ts` → `foo-`, then `foo-` → empty)
- **Chrome/Electron** (browsers, Claude Desktop)
  - Stops at every punctuation character
  - `foo-bar.test.ts` = 7 units
- **Vim `<C-w>`**
  - Similar to Chrome, but `_` is part of a word
  - `foo-bar.test.ts` = 7 units, `my_variable` = 1 unit
- **Fish `backward-kill-word`**
  - Stops at all punctuation including `_`
  - `foo-bar.test.ts` = 7 units, `my_variable` = 3 units
- **Fish `backward-kill-path-component`** (Ctrl+W default)
  - Treats `-` `.` `_` as part of a word, stops at `/` and shell chars
  - `foo-bar.test.ts` = 1 unit

### Test string

`git log --oneline /usr/local/bin/my_variable-name.test.ts`

```
Fish kill-word               ████████████████████  20
Vim <C-w>                    ██████████████████    18
Fish path-component          ████████               8
macOS native (TextEdit)      ████████               8
Vim dB (WORD)                █████                  5*
```

*Vim `dB` leaves the last char; need `x` to finish = 5 total.

The 2-press gap (20 vs 18) is the underscore: Fish treats `_` as a
boundary (`my` + `_` + `variable` = 3), Vim doesn't (`my_variable` = 1).

## Why I didn't chase the sweet spot

Fish path-component and macOS native both land at 8 presses — the
ideal middle ground. But I chose small word (18-20) because:

1. **I want to understand every line in my config** — no black-box
   custom widgets
2. **I want well-known, tested behaviour** — not bespoke ZLE functions
3. **Trailing punctuation is annoying but not worth a hack** — needing
   2 presses to delete `.ts` instead of 1 is liveable
4. **Fish kill-word ≈ Vim `<C-w>`** — close enough (20 vs 18) despite
   the `_` disagreement
5. **Small word matches Chrome/Electron** — covers most GUI apps

## Key things I learned

- **Zsh `WORDCHARS`** controls what's a "word"
  - Default includes almost everything (slashes, dots, hyphens)
  - Oh My Zsh sets it to `_-`
  - Empty string = every non-alphanumeric char is a boundary
  - `_` alone would match Vim `<C-w>`, not Fish kill-word
- **Fish kill-word vs Vim `<C-w>`** — Fish is slightly more granular
  (stops at `_`, Vim doesn't)
- **Two-tier model** is the community consensus
  - Small word: `<C-w>` / kill-word
  - Big WORD: `<C-o>dB` in Vim / `backward-kill-bigword` in Fish
- **Terminal emulator config** — must send `\x1b\x7f` for Option+BS.
  I chose to set this in Ghostty and let each app handle it, rather
  than binding Ctrl+W directly in Ghostty — more transparent
- **TUI apps** (Claude Code, lazygit) each implement their own input
  handling. Ctrl+W is the most reliable universal fallback
- **Full consistency is near-impossible** — each layer defines "word"
  differently (Unicode properties in Cocoa, `WORDCHARS` in Zsh,
  `iskeyword` in Vim, hardcoded char classes in Fish). Could spend
  months building perfect parity, but the pragmatic path is: make
  terminal tools consistent with each other, accept GUI apps are
  their own world

## References

- Fish 4.1 OS-specific defaults: github.com/fish-shell/fish-shell/issues/12122
- Cody Hiar's two-tier Zsh approach: codyhiar.com/blog/custom-backward-word-deletion-in-zsh/
- Oh My Zsh WORDCHARS saga: github.com/ohmyzsh/ohmyzsh/wiki/FAQ
- "Sensible WORDCHARS": lgug2z.com/articles/sensible-wordchars-for-most-developers/

_Researched March 2026. All press counts verified by hand._