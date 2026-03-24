# Ghostty — Shell Integration

Ghostty does things other terminals can't — clicking to reposition your cursor, scrolling between prompts, inheriting your working directory in new tabs. None of this is magic; it's shell integration. Understanding what it does (and when it breaks) saves confusion later.

---

## How it works

When Ghostty launches your shell, it automatically injects a small script that hooks into your prompt. This script communicates back to Ghostty via escape sequences, telling it where prompts are, what directory you're in, and when commands start and finish.

Supported shells: **bash**, **zsh**, **fish**, **elvish**. Auto-detection is the default — you don't need to configure anything.

```
# Default — auto-detect and inject
shell-integration = detect

# Force a specific shell (rarely needed)
shell-integration = zsh

# Disable entirely
shell-integration = none
```

---

## What it enables

Shell integration isn't one feature — it's a foundation that unlocks several:

### Prompt-aware cursor

Your cursor automatically switches to a **bar** at the shell prompt and reverts to **block** inside programs (vim, less, etc.). This gives you an instant visual cue for "am I at a prompt or inside something?"

### Click to reposition cursor

`Cmd+click` (macOS) / `Alt+click` (Linux) at the prompt moves your cursor to that position. Only works at an idle prompt — it's repositioning within your current command line, not arbitrary terminal clicking.

### Prompt-to-prompt scrolling

The `jump_to_prompt` keybind action lets you scroll between prompts in your scrollback. Instead of hunting through output, you jump directly from one command to the next. Default binds: `Cmd+Up/Down` (macOS).

### Working directory tracking

Your shell reports its current directory to Ghostty after every command. This is what makes `tab-inherit-working-directory`, `split-inherit-working-directory`, and `window-inherit-working-directory` work. Without shell integration, new tabs always open in your home directory.

### Smart close confirmation

When you close a terminal that's sitting at an idle prompt, Ghostty skips the "are you sure?" dialog. It only confirms if a program is actually running. This is why `confirm-close-surface = true` isn't annoying with shell integration enabled.

### Output selection

`Ctrl+Cmd+click` (macOS) / `Ctrl+click` (Linux) selects the entire output of a command — from one prompt to the next. Useful for copying a full command result without manually selecting.

### Sudo wrapper

Ghostty wraps `sudo` so that the Ghostty terminfo is preserved through privilege escalation. Without this, `sudo` commands might get garbled rendering because the root user's `TERM` doesn't know about Ghostty's capabilities.

### SSH features (1.2.0+)

Two features that make SSH from Ghostty much smoother:

- **`ssh-env`** — Automatically converts `TERM` to `xterm-256color` when SSHing (since remote hosts rarely have `ghostty` terminfo). Also propagates `COLORTERM=truecolor` so remote tools know truecolor is available.
- **`ssh-terminfo`** — Auto-installs the `ghostty` terminfo entry on remote hosts (via `infocmp` + `tic`). After the first connection, future SSH sessions can use `TERM=ghostty` natively.

---

## Configuring features

All features are on by default. You only need this config if you want to disable something:

```
# Disable specific features (prefix with no-)
shell-integration-features = no-cursor,no-sudo

# Disable everything
shell-integration-features = false

# Explicitly enable everything (same as default)
shell-integration-features = true
```

| Feature | What it controls |
|---------|-----------------|
| `cursor` | Bar cursor at prompt |
| `sudo` | Sudo terminfo wrapper |
| `title` | Shell sets window title |
| `ssh-env` | TERM conversion over SSH |
| `ssh-terminfo` | Auto-install terminfo on remote hosts |

---

## Gotchas

> **macOS system bash doesn't work.** `/bin/bash` on macOS is ancient (3.2) and doesn't support the injection mechanism. If you use bash, install it via Homebrew — `brew install bash`.

> **Sub-shells need manual sourcing.** Auto-injection only works for the shell Ghostty launches directly. If you run `bash`, `nix-shell`, or any nested shell inside Ghostty, you need to source the integration manually:
> ```bash
> source "${GHOSTTY_RESOURCES_DIR}/shell-integration/zsh/ghostty-integration"
> ```

> **Fish 4.0+ overlap.** Fish 4.0 added native prompt marking. Some shell integration features are redundant if you're on Fish 4.0+, but they coexist fine.

> **Verifying it works.** Check the Ghostty log for `shell integration automatically injected`. If you don't see it, the injection failed — usually because the shell version is too old or a shell plugin is interfering.
