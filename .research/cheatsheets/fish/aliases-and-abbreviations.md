# Fish Aliases and Abbreviations — Cheat Sheet

Every shell user builds muscle memory around short aliases. The problem in fish is knowing *which* mechanism to use: abbreviations, the `alias` command, or plain functions. Pick wrong and you get aliases that hide what's actually running, clutter your universal variables, or silently break in scripts.

Fish abbreviations are the answer for 80% of cases. They expand inline so you always see the real command, your history stays searchable, and they compose naturally with extra flags. Functions handle the rest.

---

## Abbreviations — the primary mechanism

An abbreviation expands inline when you press Space or Enter. You type `cm`, fish replaces it with `chezmoi` *before executing*. The expansion is visible in your terminal and recorded in history.

This is better than traditional aliases because:
- History contains the real command, not the alias name
- You see exactly what runs before it executes
- Other people reading your terminal output can follow along
- Tab completion works on the expanded command

### Defining abbreviations

```bash
abbr -a cm chezmoi
abbr -a cms 'chezmoi status'
abbr -a td 'tmux detach'
abbr -a tl 'tmux list-sessions'
abbr -a vi vim
```

After typing `cm` and pressing Space:

```
$ chezmoi _    # cursor here, ready for subcommand
```

### Abbreviations that pass arguments through

Any abbreviation naturally accepts trailing arguments. There is no `"$@"` equivalent needed — the expansion replaces the abbreviation text, then your extra arguments stay in place.

```bash
abbr -a cma 'chezmoi apply'
abbr -a cmd 'chezmoi diff'
abbr -a cme 'chezmoi edit --apply'
abbr -a cmm 'chezmoi merge'
abbr -a cmc 'chezmoi cat'
abbr -a cmra 'chezmoi re-add'
```

Type `cma ~/.gitconfig` and it expands to `chezmoi apply ~/.gitconfig`. The arguments just work.

### Cursor positioning with `--set-cursor`

For abbreviations where you need to type something in the middle, use `--set-cursor`:

```bash
abbr -a cmbrew --set-cursor 'chezmoi edit --apply ~/.Brewfile && chezmoi apply ~/brew-bundle.sh'
```

The `%` marker (default) controls where the cursor lands after expansion. In this case you probably don't need it — but it's invaluable for patterns like:

```bash
abbr -a gca --set-cursor 'git commit -m "%"'
```

Type `gca`, press Space, and the cursor is inside the quotes ready for your message.

### Removing abbreviations

```bash
abbr -e cm       # erase a single abbreviation
abbr             # list all current abbreviations
```

> **Gotcha: never define abbreviations interactively.** Running `abbr -a cm chezmoi` at a prompt saves it as a *universal variable*, which persists across sessions via `~/.config/fish/fish_variables`. This file is a mess to manage with chezmoi. Always define abbreviations in config files (see the `status is-interactive` section below).

---

## Where to put abbreviations — `conf.d` files with interactive guards

Abbreviations only make sense in interactive shells. Wrap them with `status is-interactive` so they don't run during scripts or non-interactive contexts.

Place them in `conf.d` files, organized by topic — matching the [config structure](../fish/config-structure.md):

```bash
# ~/.config/fish/conf.d/43_chezmoi.fish

status is-interactive; or return

abbr -a cm chezmoi
abbr -a cma 'chezmoi apply'
abbr -a cmd 'chezmoi diff'
abbr -a cme 'chezmoi edit --apply'
abbr -a cmm 'chezmoi merge'
abbr -a cmc 'chezmoi cat'
abbr -a cmra 'chezmoi re-add'
abbr -a cms 'chezmoi status'
```

The `or return` pattern is idiomatic fish — it exits the file early if the shell isn't interactive. Every `conf.d` file with abbreviations should start with this line.

> **Gotcha: `status is-interactive; or return` must be the guard.** Don't use `if status is-interactive` wrapping the whole file — the `or return` pattern is cleaner and avoids an indentation level for the entire file. Both work, but the community convention is `or return`.

---

## When abbreviations don't work — use functions

Abbreviations are pure text expansion. They can't:
- Accept and manipulate arguments (`$argv`)
- Run conditional logic
- Execute multiple commands in sequence
- Pipe or redirect internally
- Compute values

For these, write a [function](functions.md).

### Multi-command sequences

```bash
# ~/.config/fish/functions/dcdown.fish
function dcdown -d "Kill and remove docker compose services"
    docker compose kill
    and docker compose down
end
```

```bash
# ~/.config/fish/functions/dcreload.fish
function dcreload -d "Rebuild and restart docker compose services"
    docker compose up --build --timeout 0 -d
end
```

### Argument manipulation

```bash
# ~/.config/fish/functions/mkcd.fish
function mkcd -d "Create directory and cd into it"
    if test (count $argv) -ne 1
        echo "Usage: mkcd <directory>" >&2
        return 1
    end
    mkdir -p $argv[1]; and cd $argv[1]
end
```

### Pipelines and complex logic

```bash
# ~/.config/fish/functions/git-copy-push-remote.fish
function git-copy-push-remote -d "Copy git push remote URL to clipboard"
    git remote -v | tail -n1 | awk '{print $2}' | pbcopy
end
```

```bash
# ~/.config/fish/functions/greignore.fish
function greignore -d "Re-apply .gitignore rules"
    git rm -r --cached .
    and git add .
    and git commit -m "Re-apply .gitignore rules"
end
```

See [syntax-rosetta.md](syntax-rosetta.md) for translating zsh syntax in function bodies.

---

## The `alias` command — mostly avoid it

Fish's `alias` command exists but is just syntactic sugar for creating a wrapper function. Running:

```bash
alias vi vim
```

is equivalent to:

```bash
function vi --wraps vim
    command vim $argv
end
```

The `--wraps` flag gives you completions from the wrapped command, which is nice. But the result is a function that hides the real command — your history shows `vi`, not `vim`.

### One legitimate use: default flags

When you always want certain flags on a command but still want the original name:

```bash
alias ls 'ls --color=auto'
```

This creates a function named `ls` that calls `command ls --color=auto $argv`. The `command` keyword bypasses the function to call the real `ls`.

For most cases, abbreviations are better. They expand so you see the real command, and you can easily override by deleting the expansion and typing something different.

> **Gotcha: `alias` in `config.fish` runs every shell startup.** Each call creates a function in memory. For a handful of aliases this is fine. For dozens, define them as proper function files in `~/.config/fish/functions/` instead — fish autoloads those on demand.

---

## Translating Flo's zshrc aliases

Here's every alias from the zsh config, organized by `conf.d` file, with the right fish mechanism for each.

### General (`conf.d/41_general.fish`)

```bash
status is-interactive; or return

# Simple expansions → abbr
abbr -a vi vim
abbr -a t t2
abbr -a t1 'custom-tree 1'
abbr -a t2 'custom-tree 2'
abbr -a t3 'custom-tree 3'
abbr -a t4 'custom-tree 4'
```

`mkcd` needs argument handling, so it becomes a function (shown above).

`x` (chmod last file) needs command substitution — function:

```bash
# ~/.config/fish/functions/x.fish
function x -d "Make the most recently modified file executable"
    chmod u+x (ls -tr | tail -1)
end
```

### Git (`conf.d/42_git.fish`)

```bash
status is-interactive; or return

# No abbreviations needed — all git aliases are functions
# (greignore and git-copy-push-remote are multi-command)
```

Both `greignore` and `git-copy-push-remote` are functions (shown above).

### Chezmoi (`conf.d/43_chezmoi.fish`)

```bash
status is-interactive; or return

abbr -a cm chezmoi
abbr -a cma 'chezmoi apply'
abbr -a cmd 'chezmoi diff'
abbr -a cme 'chezmoi edit --apply'
abbr -a cmm 'chezmoi merge'
abbr -a cmc 'chezmoi cat'
abbr -a cmra 'chezmoi re-add'
abbr -a cms 'chezmoi status'
abbr -a cmbrew 'chezmoi edit --apply ~/.Brewfile && chezmoi apply ~/brew-bundle.sh'
```

### Docker (`conf.d/44_docker.fish`)

```bash
status is-interactive; or return

# Both need multiple commands → functions (shown above)
```

### Claude (`conf.d/45_claude.fish`)

```bash
status is-interactive; or return

abbr -a claude 'claude --allow-dangerously-skip-permissions'
```

> **Gotcha: shadowing the command name.** This abbreviation replaces `claude` with `claude --allow-dangerously-skip-permissions`. Fish handles this correctly — the expanded text uses the actual `claude` binary, not the abbreviation again. No recursion issues.

### Network (`conf.d/46_network.fish`)

```bash
status is-interactive; or return

abbr -a show-all-ports-in-use 'sudo lsof -PiTCP -sTCP:LISTEN'
```

### Tmux (`conf.d/49_tmux.fish`)

```bash
status is-interactive; or return

abbr -a td 'tmux detach'
abbr -a tl 'tmux list-sessions'
```

### Architecture — macOS only (`conf.d/50_arch.fish`)

These need to launch zsh (not fish) under a specific architecture. Functions are cleaner here since the commands are long:

```bash
# ~/.config/fish/functions/arm.fish
function arm -d "Launch ARM64 zsh login shell"
    env /usr/bin/arch -arm64 /bin/zsh --login
end

# ~/.config/fish/functions/intel.fish
function intel -d "Launch x86_64 zsh login shell"
    env /usr/bin/arch -x86_64 /bin/zsh --login
end
```

### Misc (`conf.d/90_misc.fish`)

```bash
status is-interactive; or return

abbr -a mfp 'myfitnesspal remainings Shock_N745'
abbr -a tb 'nc termbin.com 9999'
```

`rmstream` points to a script path — abbreviation works fine:

```bash
abbr -a rmstream "$HOME/Work/Private/Dev/Misc/RemarkableStreaming/start.sh"
```

---

## Decision framework

When translating a zsh alias, ask these questions in order:

1. **Is it pure text substitution?** (no args processing, no pipes, no conditionals)
   - Yes -- **abbreviation**
   - `alias cm=chezmoi` becomes `abbr -a cm chezmoi`

2. **Does it just pass all arguments through?** (`"$@"` or implicit)
   - Yes -- **abbreviation** (arguments naturally trail the expansion)
   - `function cma() { chezmoi apply "$@" }` becomes `abbr -a cma 'chezmoi apply'`

3. **Does it need argument validation, multiple commands, pipes, or logic?**
   - Yes -- **function** in `~/.config/fish/functions/name.fish`
   - `function mkcd { mkdir $1 && cd $1 }` becomes a proper function file

4. **Does it add default flags to an existing command name?**
   - Consider **`alias`** for the `--wraps` completion inheritance
   - Or just use an abbreviation with the same name

> **Gotcha: don't mix mechanisms.** If you have both an abbreviation and a function with the same name, the abbreviation takes priority in interactive shells (it expands before fish looks up functions). Pick one.

---

## Quick reference

| zsh alias | fish mechanism | definition |
|---|---|---|
| `cm=chezmoi` | abbr | `abbr -a cm chezmoi` |
| `cma() { chezmoi apply "$@" }` | abbr | `abbr -a cma 'chezmoi apply'` |
| `cmd() { chezmoi diff "$@" }` | abbr | `abbr -a cmd 'chezmoi diff'` |
| `cme() { chezmoi edit --apply "$@" }` | abbr | `abbr -a cme 'chezmoi edit --apply'` |
| `cmm() { chezmoi merge "$@" }` | abbr | `abbr -a cmm 'chezmoi merge'` |
| `cmc() { chezmoi cat "$@" }` | abbr | `abbr -a cmc 'chezmoi cat'` |
| `cmra() { chezmoi re-add "$@" }` | abbr | `abbr -a cmra 'chezmoi re-add'` |
| `cms="chezmoi status"` | abbr | `abbr -a cms 'chezmoi status'` |
| `cmbrew=...` | abbr | `abbr -a cmbrew 'chezmoi edit ...'` |
| `greignore=...` | function | multi-command git sequence |
| `git-copy-push-remote` | function | pipeline with awk + pbcopy |
| `dcreload` | function | docker compose rebuild |
| `dcdown` | function | docker compose kill + down |
| `vi=vim` | abbr | `abbr -a vi vim` |
| `x='chmod ...'` | function | command substitution needed |
| `t=t2` | abbr | `abbr -a t t2` |
| `t1`..`t4` | abbr | `abbr -a t1 'custom-tree 1'` |
| `mkcd` | function | argument handling + cd |
| `claude=...` | abbr | `abbr -a claude 'claude --allow...'` |
| `show-all-ports-in-use` | abbr | `abbr -a show-all-ports-in-use 'sudo lsof ...'` |
| `td`, `tl` | abbr | `abbr -a td 'tmux detach'` |
| `arm`, `intel` | function | launch different arch shell |
| `mfp`, `tb`, `rmstream` | abbr | simple text expansion |

### Decision cheat sheet

| Pattern | Mechanism | Why |
|---|---|---|
| Simple text swap | `abbr` | Visible expansion, searchable history |
| Pass-through args (`$@`) | `abbr` | Args trail the expansion naturally |
| Multi-command sequence | function | `and` chaining, error handling |
| Pipeline / redirect | function | Can't pipe inside an abbreviation |
| Argument manipulation | function | Need `$argv` access |
| Default flags, same name | `alias` or `abbr` | `alias` gives `--wraps` completions |
