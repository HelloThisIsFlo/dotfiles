# Fish Sourcing, Secrets, and Tool Integration — Cheat Sheet

Your zshrc has `source ~/.secrets.env`, `eval "$(direnv hook zsh)"`, and a dozen tool initializations. None of them work in fish. The `source` command only reads fish syntax, `eval` behaves differently, and bash-format `export KEY=value` files are gibberish to the parser. This sheet covers how to translate every sourcing and tool-init pattern from your zshrc into idiomatic fish.

---

## The sourcing problem

Fish's `source` command reads fish syntax only. It cannot parse bash/zsh files — no `export`, no `$()` subshells, no `&&` chains (well, fish has `&&` but the rest of the syntax differs). A `source ~/.secrets.env` that works in zsh will blow up in fish.

### Three approaches

| Approach | When to use | Speed | Reliability |
|----------|-------------|-------|-------------|
| Rewrite as fish | Static config, env vars, anything you control | Fastest | Best |
| `bass` plugin | One-off bash scripts you can't rewrite (vendor scripts like `travis.sh`) | Slow (spawns bash) | Good |
| `bash -c 'source ...; env'` | When you only need env vars from a bash file and don't want bass | Medium | Fragile |

### Approach 1: Rewrite as fish (the right way for most things)

This is the right answer 90% of the time. If the bash file is just setting environment variables, rewrite it in fish syntax and put it in `conf.d/`.

```bash
# bash: ~/.secrets.env
export GITHUB_TOKEN=ghp_abc123
export AWS_ACCESS_KEY_ID=AKIA...
```

```bash
# fish: conf.d/03__secrets.fish
set -gx GITHUB_TOKEN ghp_abc123
set -gx AWS_ACCESS_KEY_ID AKIA...
```

No quoting gymnastics, no subshell overhead. It loads at shell startup with everything else.

### Approach 2: `bass` plugin (for unmodifiable bash scripts)

[bass](https://github.com/edc/bass) runs a bash command and imports the resulting environment changes into fish. Install via Fisher:

```bash
fisher install edc/bass
```

Use it for vendor scripts you can't rewrite:

```bash
# zsh: [ -f $HOME/.travis/travis.sh ] && source $HOME/.travis/travis.sh
# fish:
if test -f $HOME/.travis/travis.sh
    bass source $HOME/.travis/travis.sh
end
```

`bass` spawns a bash subprocess, sources the script, diffs the environment, and applies changes to your fish session.

> **Gotcha:** `bass` adds ~50ms per invocation. Don't use it in `conf.d/` for things that run on every shell startup unless you genuinely need it. Rewriting as fish is always faster.

> **Gotcha:** `bass` only captures environment variable changes. If the bash script defines functions, aliases, or modifies the prompt, those are lost. It's strictly for env var side effects.

### Approach 3: Manual bash-to-env extraction (no plugin needed)

If you only need environment variables from a bash file and don't want the `bass` dependency:

```bash
# Parse KEY=VALUE lines from a bash env file (no `export`, no expressions)
for line in (grep -E '^[A-Z_]+=.' ~/.secrets.env | sed 's/^export //')
    set -l key (string split -m 1 '=' $line)[1]
    set -l val (string split -m 1 '=' $line)[2]
    set -gx $key $val
end
```

> **Gotcha:** This is fragile. It breaks on multiline values, variable interpolation (`$HOME/path`), or any bash-specific syntax. Only use it for dead-simple `KEY=value` files. Rewriting as fish is safer.

---

## Secrets

The biggest sourcing headache from zsh is usually `source ~/.secrets.env` — a file full of API tokens and credentials loaded at shell startup.

### The zsh pattern (what you're replacing)

```bash
# .zshrc
source ~/.secrets.env

# ~/.secrets.env
export GITHUB_TOKEN=ghp_abc123
export OPENAI_API_KEY=sk-...
export AWS_ACCESS_KEY_ID=AKIA...
```

Problems: secrets in a plaintext file, easy to accidentally commit, no encryption at rest.

### The chezmoi + rbw approach (the right way)

Secrets live in Bitwarden. Chezmoi templates pull them at `chezmoi apply` time and render a fish file. The rendered file is a plain `conf.d/` snippet — no runtime secret fetching, no password prompts during shell startup.

```bash
# Source: dot_config/private_fish/conf.d/03__secrets.fish.tmpl
# (this is a chezmoi template, not a raw fish file)

set -gx GITHUB_TOKEN {{ (rbw "github-token").data.password | quote }}
set -gx OPENAI_API_KEY {{ (rbw "openai-api-key").data.password | quote }}
set -gx AWS_ACCESS_KEY_ID {{ (rbwFields "aws-credentials").access_key_id.value | quote }}
set -gx AWS_SECRET_ACCESS_KEY {{ (rbwFields "aws-credentials").secret_access_key.value | quote }}
```

After `chezmoi apply`, the rendered file at `~/.config/fish/conf.d/03__secrets.fish` contains actual values:

```bash
set -gx GITHUB_TOKEN 'ghp_abc123'
set -gx OPENAI_API_KEY 'sk-...'
```

This file should have `private_` prefix in chezmoi source (enforces `0600` permissions).

### How rbw template functions work

| Syntax | What it returns |
|--------|----------------|
| `(rbw "item-name").data.password` | The password field of a Bitwarden item |
| `(rbwFields "item-name").field_name.value` | A custom field on a Bitwarden item |

Chezmoi calls `rbw` at apply time. The `rbw` agent must be running (`rbw unlock` first). If it's not, chezmoi errors out — it won't render partial secrets.

> **Gotcha:** Secrets are baked into the rendered file at apply time. If you rotate a secret in Bitwarden, you must run `chezmoi apply` again to update the file on disk. The shell won't magically pick up the new value.

> **Gotcha:** The rendered secrets file lives on disk in plaintext (with `0600` permissions). This is the same security posture as the old `~/.secrets.env` — the improvement is that the source of truth is Bitwarden, not a file you might commit to git.

---

## Tool init patterns

Most CLI tools need a shell hook — a snippet that runs at startup to set up completions, path entries, or shell integration. In zsh this is usually `eval "$(tool init zsh)"`. Fish has a cleaner equivalent.

### The pattern: `command | source`

```bash
# zsh: eval "$(tool init zsh)"
# fish:
tool init fish | source
```

This pipes the tool's init script directly into `source`. No `eval` needed — `source` reads from stdin when given no file argument. This is the idiomatic fish pattern for all tool activations.

### Homebrew

```bash
# conf.d/11__homebrew.fish
eval (/opt/homebrew/bin/brew shellenv)
```

This is the one case where `eval` is correct. `brew shellenv` outputs fish syntax (it detects the calling shell), and the parentheses are fish's command substitution. The result sets `HOMEBREW_PREFIX`, `HOMEBREW_CELLAR`, `HOMEBREW_REPOSITORY`, and prepends Homebrew paths to `PATH` and `MANPATH`.

> **Gotcha:** `brew shellenv` uses `fish_add_path --move --path` internally, which forces Homebrew directories to the front of PATH. Any PATH entries prepended before this line get pushed down. This is why tool activations that need to win over Homebrew (like asdf) must load after it. See the [conf.d numbering scheme](config-structure.md).

### direnv

```bash
# conf.d/21__direnv.fish
direnv hook fish | source
```

Translates directly from `eval "$(direnv hook zsh)"`. The `direnv hook fish` command outputs a fish function definition that hooks into the prompt to auto-load `.envrc` files.

### zoxide

```bash
# conf.d/22__zoxide.fish
zoxide init fish | source
```

Replaces `eval "$(zoxide init zsh)"`. Sets up the `z` and `zi` commands for fast directory jumping.

> **Gotcha:** If you use `--cmd cd` to alias zoxide as `cd`, put it in the init: `zoxide init fish --cmd cd | source`. This replaces the builtin `cd` with a zoxide-wrapped version.

### mise

```bash
# conf.d/12__mise.fish
mise activate fish | source
```

Replaces the asdf antigen bundle. mise is the successor to asdf (same plugin ecosystem, faster, better UX). Its activation hook manages shims and version switching automatically.

### iTerm2 shell integration

```bash
# zsh: test -e "${HOME}/.iterm2_shell_integration.zsh" && source ...
# fish:
if test -e $HOME/.iterm2_shell_integration.fish
    source $HOME/.iterm2_shell_integration.fish
end
```

iTerm2 provides a native fish integration script — no bass or translation needed. Download it with:

```bash
curl -L https://iterm2.com/shell_integration/fish -o ~/.iterm2_shell_integration.fish
```

### Summary of tool init translations

| Tool | zsh | fish |
|------|-----|------|
| Homebrew | `eval "$(brew shellenv)"` | `eval (/opt/homebrew/bin/brew shellenv)` |
| direnv | `eval "$(direnv hook zsh)"` | `direnv hook fish \| source` |
| zoxide | `eval "$(zoxide init zsh)"` | `zoxide init fish \| source` |
| mise | (via asdf plugin) | `mise activate fish \| source` |
| starship | `eval "$(starship init zsh)"` | `starship init fish \| source` |
| iTerm2 | `source ~/.iterm2_shell_integration.zsh` | `source ~/.iterm2_shell_integration.fish` |

---

## asdf vs mise

Your zshrc uses asdf via an antigen plugin. Fish needs explicit setup for either tool, and this is a good time to consider the migration to mise.

### Current asdf setup

```bash
# conf.d/13__asdf.fish
set -gx ASDF_DATA_DIR "$HOME/.asdf"
fish_add_path --global --move --path $ASDF_DATA_DIR/shims
```

This is a simplified version of the official asdf fish integration. The key insight is `--move`: it fights Homebrew's `--move` trick by re-hoisting asdf shims to the front of PATH after Homebrew has had its turn.

### The PATH ordering fight

The loading order matters because both Homebrew and asdf try to own the front of PATH:

1. `11__homebrew.fish` runs `brew shellenv` which uses `fish_add_path --move` — Homebrew wins PATH
2. `13__asdf.fish` runs `fish_add_path --move` — asdf shims overtake Homebrew

If asdf loaded first, Homebrew would push it down and you'd get Homebrew's Python instead of asdf's. The `--move` on both sides and the numbering scheme (`11` before `13`) guarantee the right order. See [variables-and-path.md](variables-and-path.md) for full details on `fish_add_path` flags.

### mise migration path

mise is a drop-in replacement for asdf. Same `.tool-versions` files, same plugin ecosystem, better performance, native fish support.

```bash
# Replace 13__asdf.fish with 12__mise.fish:
mise activate fish | source
```

Why mise is better for fish:
- No shim PATH fights — mise modifies PATH dynamically per directory, like direnv
- No `--move` hacks needed
- `mise activate` does everything: PATH management, version switching, completions
- Reads existing `.tool-versions` files (backward compatible)
- Also reads `mise.toml` for richer config (env vars, tasks, etc.)

### Migration steps

1. Install mise: `brew install mise`
2. Activate in fish: replace `13__asdf.fish` content with `mise activate fish | source`
3. Test: `mise ls` should show all your installed runtimes (reads `.tool-versions`)
4. Gradual cleanup: keep `~/.asdf` around until you verify everything works, then `rm -rf ~/.asdf`

> **Gotcha:** mise uses its own shim directory (`~/.local/share/mise/shims`). If you have scripts that hardcode `~/.asdf/shims`, update them. But if you use `mise activate` (not shim mode), there are no shims at all — mise manages PATH directly.

---

## eval in fish

In bash/zsh, `eval` is the Swiss army knife for dynamic code execution. In fish, you rarely need it.

### When to use what

| Pattern | Fish equivalent | Example |
|---------|----------------|---------|
| `eval "$(cmd)"` | `cmd \| source` | `direnv hook fish \| source` |
| `eval "$variable"` | `eval $variable` | Rare — usually a code smell |
| `eval "export FOO=bar"` | `set -gx FOO bar` | Always prefer direct `set` |
| `source <(cmd)` | `cmd \| source` | Same pattern, fish has no process substitution |

### `command | source` is the default

```bash
# This is the idiomatic way. Use it for everything.
tool init fish | source
```

`source` with no filename reads from stdin. The pipe feeds the tool's output directly in. No intermediate variable, no `eval`, no temp file.

### When eval is actually correct

The main legitimate use of `eval` in fish is when a command outputs fish code as a string (not to stdout) or when you need command substitution to expand before sourcing:

```bash
# brew shellenv — eval with command substitution is the documented pattern
eval (/opt/homebrew/bin/brew shellenv)

# Dynamic variable names (rare, usually a sign you need a different approach)
set -l varname MY_VAR
eval set -gx $varname "some-value"
```

> **Gotcha:** `eval` in fish concatenates its arguments with spaces and executes the result. This means `eval echo "hello world"` works, but complex quoting gets messy fast. If you're fighting `eval` quoting, you're doing it wrong — find the `| source` pattern instead.

---

## Quick reference

| zsh pattern | fish equivalent | Where to put it |
|-------------|----------------|-----------------|
| `source ~/.secrets.env` | chezmoi template with rbw, renders to `set -gx` | `conf.d/03__secrets.fish.tmpl` |
| `eval "$(brew shellenv)"` | `eval (/opt/homebrew/bin/brew shellenv)` | `conf.d/11__homebrew.fish` |
| `eval "$(direnv hook zsh)"` | `direnv hook fish \| source` | `conf.d/21__direnv.fish` |
| `eval "$(zoxide init zsh)"` | `zoxide init fish \| source` | `conf.d/22__zoxide.fish` |
| `source ~/.travis/travis.sh` | `bass source ~/.travis/travis.sh` | `conf.d/` (if still needed) |
| `antigen bundle asdf` | `mise activate fish \| source` | `conf.d/12__mise.fish` |
| `export PATH="$ASDF/.../shims:$PATH"` | `fish_add_path --global --move --path $ASDF_DATA_DIR/shims` | `conf.d/13__asdf.fish` |
| `export KEY=value` | `set -gx KEY value` | Relevant `conf.d/` file |
| `eval "$dynamic_code"` | `eval $dynamic_code` or refactor to `\| source` | Avoid if possible |

### See also

- [Variables and PATH](variables-and-path.md) — `set -gx` scopes, `fish_add_path` flags, the universal variable trap
- [Config structure](config-structure.md) — `conf.d/` loading order, numbering scheme, what goes where
- [Syntax Rosetta Stone](syntax-rosetta.md) — full bash-to-fish translation table for conditionals, loops, quoting
