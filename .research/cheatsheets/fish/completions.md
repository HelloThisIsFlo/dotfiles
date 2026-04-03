# Fish Completions — Cheat Sheet

In zsh, completions are a multi-layered mess: `compinit`, `compdef`, `fpath`, `bashcompinit`, `_wanted`, `_multi_parts` — all loaded eagerly every shell startup. If you forget one incantation, completions silently stop working and you don't notice for weeks. Fish solves this by making completions a first-class, declarative system: drop a file in the right directory, or use the `complete` builtin, and it just works. No initialization ritual.

---

## How fish finds completions

Fish loads completions **lazily** — it doesn't parse completion files until you actually press Tab after a command. It searches three locations, in order:

1. **User completions:** `~/.config/fish/completions/COMMAND.fish`
2. **System-wide vendor:** `/usr/share/fish/vendor_completions.d/COMMAND.fish`
3. **Fish built-ins:** `/usr/share/fish/completions/COMMAND.fish`

The file name must match the command name. `git.fish` provides completions for `git`. `chezmoi.fish` provides completions for `chezmoi`. That's the entire discovery mechanism.

### What fish does automatically

Fish ships with completions for ~900 commands out of the box (git, ssh, systemctl, docker, etc.). It also **parses man pages** to generate basic completions for commands it doesn't know about. This happens in the background via `fish_update_completions`, which runs periodically.

```bash
# Force a man page completion rebuild
fish_update_completions
```

> **Gotcha:** Man-page-generated completions are basic — they only get flags and short descriptions. For tools with complex subcommand trees (like chezmoi or kubectl), you want CLI-generated completions instead.

### The zsh contrast

The entire zsh `fpath` / `compinit` dance is gone:

```bash
# zsh — all of this is unnecessary in fish
autoload -Uz compinit && compinit
autoload -U +X bashcompinit && bashcompinit
fpath=(~/.docker/completions $fpath)
fpath+=~/.zfunc
```

In fish: put a file in `~/.config/fish/completions/`. Done. No `fpath`, no `compinit`, no `autoload`.

---

## CLI-generated completions

Most modern CLIs can generate their own completion scripts. The pattern is always the same:

```bash
TOOL completion fish | source
```

### The problem with naive sourcing

Running `chezmoi completion fish | source` on every shell startup works but is slow — it spawns a subprocess, generates the full completion script, and parses it. For one tool, fine. For ten tools, noticeable lag.

### The right way: version-aware caching

This is what the `cache_completions` function does — it generates completions once per tool version and writes them to `~/.config/fish/completions/TOOL.fish`, which fish then loads lazily:

```bash
# In conf.d/99__completions.fish
if status is-interactive
    cache_completions chezmoi "chezmoi completion fish"
    cache_completions mise "mise completion fish"
end
```

```bash
# functions/cache_completions.fish
function cache_completions --argument-names tool cmd
    command -q $tool; or return
    set -l cache ~/.config/fish/completions/$tool.fish
    set -l current_version (command $tool --version 2>/dev/null; or echo unknown)
    set -l version_file ~/.config/fish/.$tool-completions-version
    if not test -f $cache; or not test -f $version_file; or test "$current_version" != (cat $version_file)
        eval $cmd > $cache
        echo $current_version > $version_file
    end
end
```

This regenerates completions only when the tool is upgraded. The cache file lands in `~/.config/fish/completions/`, so fish finds it automatically — no sourcing needed after the first run.

### Adding a new tool

```bash
# Just add one line to conf.d/99__completions.fish:
cache_completions poetry "poetry completions fish"
cache_completions talosctl "talosctl completion fish"
cache_completions kubectl "kubectl completion fish"
```

> **Gotcha:** Some tools use different subcommand names. It's `poetry completions fish` (plural) but `chezmoi completion fish` (singular). Always check `TOOL --help` or `TOOL help completion` first.

> **Gotcha:** The `eval` in `cache_completions` is safe here because you control the command string. Don't pass user input to it.

---

## The `complete` builtin

When a CLI doesn't have a `completion` subcommand, or you need custom completions for your own functions and abbreviations, you write them directly with the `complete` builtin.

### Basic syntax

```bash
complete -c COMMAND -s SHORT -l LONG -a 'VALUES' -d 'Description'
```

| Flag | Purpose | Example |
|------|---------|---------|
| `-c` | Command to complete for | `-c git` |
| `-s` | Short flag (single char) | `-s v` (completes `-v`) |
| `-l` | Long flag | `-l verbose` (completes `--verbose`) |
| `-a` | Arguments/values to offer | `-a 'start stop restart'` |
| `-d` | Human-readable description | `-d 'Enable verbose output'` |
| `-f` | Don't suggest files (force only your completions) | |
| `-F` | Force file completions (even if other completions exist) | |
| `-r` | Flag requires an argument | |
| `-n` | Only complete when condition is true | `-n '__fish_seen_subcommand_from push'` |

### A simple command with flags

```bash
# completions/mybackup.fish
complete -c mybackup -s v -l verbose -d 'Show verbose output'
complete -c mybackup -s d -l dry-run -d 'Show what would be done'
complete -c mybackup -l target -r -a '(__fish_complete_directories)' -d 'Backup target directory'
```

### Subcommand completions with `-n`

The `-n` (condition) flag is how you build subcommand trees. Fish provides helper functions that make this readable:

```bash
# completions/deploy.fish

# Top-level subcommands — only when no subcommand has been typed yet
complete -c deploy -f -n '__fish_use_subcommand' -a staging -d 'Deploy to staging'
complete -c deploy -f -n '__fish_use_subcommand' -a production -d 'Deploy to production'
complete -c deploy -f -n '__fish_use_subcommand' -a rollback -d 'Rollback last deployment'

# Flags specific to "staging" subcommand
complete -c deploy -n '__fish_seen_subcommand_from staging' -l branch -r -d 'Branch to deploy'
complete -c deploy -n '__fish_seen_subcommand_from staging' -l skip-tests -d 'Skip test suite'

# Flags specific to "production" subcommand
complete -c deploy -n '__fish_seen_subcommand_from production' -l tag -r -d 'Release tag to deploy'
complete -c deploy -n '__fish_seen_subcommand_from production' -l approve -d 'Skip approval prompt'
```

### Key condition helpers

| Helper function | True when... |
|----------------|--------------|
| `__fish_use_subcommand` | No subcommand has been typed yet |
| `__fish_seen_subcommand_from sub1 sub2` | One of the listed subcommands appears on the line |
| `__fish_complete_directories` | Returns directory paths for completion |
| `__fish_complete_users` | Returns system usernames |
| `__fish_complete_groups` | Returns system groups |

> **Gotcha:** `-f` (no file completions) should usually go on subcommand completions. Without it, fish mixes your subcommand names with filenames, which is almost never what you want.

---

## Custom completions — real examples

### Completing chezmoi managed files

The zsh version required `_wanted`, `_multi_parts`, `compdef`, and a bespoke function:

```bash
# zsh — 6 lines of ceremony
function _chezmoi_managed_files() {
  local -a managed_files
  managed_files=(${(f)"$(chezmoi managed 2>/dev/null)"})
  _wanted files expl 'managed file' _multi_parts / managed_files
}
compdef _chezmoi_managed_files cma cmd cme cmm cmc cmra
```

In fish, you provide a function that outputs one completion per line. Fish calls it on demand:

```bash
# completions/cma.fish (and symlink or copy for cme, cmm, etc.)
function __chezmoi_managed_files
    chezmoi managed 2>/dev/null
end

complete -c cma -f -a '(__chezmoi_managed_files)' -d 'Managed file'
complete -c cme -f -a '(__chezmoi_managed_files)' -d 'Managed file'
complete -c cmm -f -a '(__chezmoi_managed_files)' -d 'Managed file'
complete -c cmc -f -a '(__chezmoi_managed_files)' -d 'Managed file'
complete -c cmra -f -a '(__chezmoi_managed_files)' -d 'Managed file'
```

The `-a` flag accepts a command substitution. Fish runs `__chezmoi_managed_files` every time you press Tab, and each output line becomes a completion candidate. Path separators work naturally — fish handles partial path completion out of the box.

> **Gotcha:** If `chezmoi managed` is slow, completions will feel sluggish. Consider caching the output or using `chezmoi managed --path-style absolute` if you need full paths.

### Completing tmux sessions

The zsh version:

```bash
# zsh — custom completion function + compdef wiring
function __tmux-sessions () {
  local -a sessions
  sessions=(${${(f)"$(command tmux 2> /dev/null list-sessions)"}/:[ $'\t']##/:})
  _describe -t sessions 'sessions' sessions "$@"
}
compdef __tmux-sessions ta
compdef __tmux-sessions tk
```

The fish version:

```bash
# completions/ta.fish
function __tmux_sessions
    tmux list-sessions -F '#{session_name}' 2>/dev/null
end

complete -c ta -f -a '(__tmux_sessions)' -d 'Tmux session'
complete -c tk -f -a '(__tmux_sessions)' -d 'Tmux session'
```

The `-F` format flag extracts just the session name — cleaner than the zsh string manipulation gymnastics.

### Completing abbreviations and wrapper functions

Fish abbreviations expand inline and then complete as whatever they expand to. If you have `abbr -a g git`, typing `g <space>` expands to `git ` and you get full git completions for free.

For wrapper functions (like `ta` for tmux attach), you need explicit `complete` definitions since fish doesn't know what the function wraps. That's what the examples above do.

> **Gotcha:** If you define both an abbreviation and a completion for the same command, the abbreviation expands first and the custom completion never fires. Use one or the other — abbreviations for simple expansions, functions + completions for anything that needs custom Tab behavior. See [aliases-and-abbreviations.md](aliases-and-abbreviations.md) for when to use which.

---

## Completing for functions in the functions directory

When you have a function like `functions/ta.fish`, completions go in `completions/ta.fish`. Fish finds both by name. You can put all completions for related commands in a single file if you prefer — the file name just needs to match at least one of them:

```bash
# completions/ta.fish — covers both ta and tk
complete -c ta -f -a '(__tmux_sessions)' -d 'Tmux session'
complete -c tk -f -a '(__tmux_sessions)' -d 'Tmux session'
```

---

## Debugging completions

### Test what fish would complete

```bash
# Show completions for "chezmoi a" as if you pressed Tab
complete -C 'chezmoi a'
```

This is the single most useful debugging command. It runs the completion engine and shows exactly what Tab would produce.

### List all completions registered for a command

```bash
complete -c chezmoi
```

This dumps every `complete` definition for `chezmoi` — all flags, subcommands, and dynamic completions. Useful to check whether CLI-generated completions loaded correctly.

### Find which file provides completions

```bash
# Check if a completion file exists
ls ~/.config/fish/completions/chezmoi.fish
ls /usr/share/fish/vendor_completions.d/chezmoi.fish
ls /usr/share/fish/completions/chezmoi.fish
```

Remember the priority order: user > vendor > built-in. If the same command has completions in multiple locations, user wins.

### Clear and reload completions

```bash
# Remove all completions for a command
complete -e -c mycommand

# Then source the file again
source ~/.config/fish/completions/mycommand.fish
```

> **Gotcha:** `complete -C` only works for the first argument position by default. To test subcommand completions, include the subcommand: `complete -C 'chezmoi edit '` (note the trailing space).

---

## Quick reference

| Task | Command |
|------|---------|
| Add CLI-generated completions | `cache_completions tool "tool completion fish"` in `conf.d/99__completions.fish` |
| Complete a simple command's flags | `complete -c cmd -s f -l flag -d 'desc'` |
| Complete subcommands | `complete -c cmd -f -n '__fish_use_subcommand' -a 'sub1 sub2'` |
| Complete subcommand-specific flags | `complete -c cmd -n '__fish_seen_subcommand_from sub1' -l flag` |
| Dynamic completions from a command | `complete -c cmd -f -a '(some_command)'` |
| Suppress file completions | Add `-f` to the `complete` call |
| Force file completions | Add `-F` to the `complete` call |
| Flag requires an argument | Add `-r` to the `complete` call |
| Test completions | `complete -C 'cmd partial'` |
| List registered completions | `complete -c cmd` |
| Clear completions for a command | `complete -e -c cmd` |
| Rebuild man page completions | `fish_update_completions` |
| Where user completions live | `~/.config/fish/completions/COMMAND.fish` |

---

## See also

- [syntax-rosetta.md](syntax-rosetta.md) — zsh-to-fish translation table
- [config-structure.md](config-structure.md) — where completion files fit in the config directory layout
- [functions.md](functions.md) — writing the functions that completions complete for
- [aliases-and-abbreviations.md](aliases-and-abbreviations.md) — when abbreviations auto-complete vs when you need explicit completions
