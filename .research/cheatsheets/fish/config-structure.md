# Fish Config Structure — Cheat Sheet

Fish's config system is the opposite of zsh's monolithic `.zshrc`: instead of one 800-line file with fold markers, you get a directory tree where each file has a single responsibility. The problem is knowing what goes where — `conf.d/` vs `functions/` vs `config.fish`, what loads when, and how to keep it organized as your setup grows.

---

## Loading order

Fish loads configuration in a strict sequence. Getting this wrong means things silently fail because a dependency wasn't loaded yet.

### The sequence

1. **`/etc/fish/config.fish`** — system-wide config (rarely touched)
2. **`conf.d/*.fish`** — snippets, loaded alphabetically by filename
3. **`~/.config/fish/config.fish`** — your personal config (loads last)

### What this means in practice

- `conf.d/` loads BEFORE `config.fish`. This is the opposite of what most people expect.
- Anything in `conf.d/` can depend on system defaults but not on `config.fish`.
- `config.fish` can depend on everything — it's the last thing to load.
- Fish also checks `$__fish_vendor_confdirs` and `$__fish_sysconf_dir` for additional conf.d directories (Homebrew uses this for tool integrations like `mise activate fish`).

### Where to put things

The right answer for almost everything is `conf.d/`. Keep `config.fish` minimal — it's for interactive-only setup that genuinely needs to run after everything else. In practice, that's almost nothing.

```bash
# config.fish — this is all you need
if status is-interactive
# Commands to run in interactive sessions can go here
end
```

> **Gotcha.** Scripts in `conf.d/` run for ALL fish sessions — interactive, login, and non-interactive. If something should only run in interactive sessions, wrap it in `if status is-interactive`. Most tool activations (direnv, zoxide, starship) already handle this internally.

---

## The conf.d numbering scheme

Without a naming convention, conf.d becomes a junk drawer. The numbering scheme creates load-order guarantees and visual grouping in a single pass.

### The ranges

| Range | Category | What goes here |
|-------|----------|----------------|
| `0x` | Shell fundamentals | Keybinds, env vars, secrets — things everything else depends on |
| `1x` | Package managers | Homebrew, mise — tool version managers and package sources |
| `2x` | Tool integrations | direnv, zoxide, language setups — tools that hook into the shell |
| `4x` | Commands and aliases | Abbreviations, functions, custom commands — the stuff you type |
| `8x` | PATH | Path construction — runs late so tools are already configured |
| `99` | Completions | Completion registration — must run after everything is defined |

### Why this ordering

- **Shell env (0x) before package managers (1x):** Homebrew needs env vars. mise needs Homebrew.
- **Package managers (1x) before tools (2x):** Tools are installed by package managers. Their activation scripts need the binaries on PATH.
- **Tools (2x) before commands (4x):** Custom commands may wrap or depend on tools (e.g., git aliases that use delta).
- **PATH (8x) near the end:** By this point all tools have registered their paths. The 8x files do final PATH assembly.
- **Completions (99) dead last:** Completions reference commands that must already be defined.

### The actual layout

```
conf.d/
  00=====SHELL-FUNDAMENTALS=====09    # section separator (not a real script)
  01__keybinds-and-vi-mode.fish
  02__shell-env.fish
  03__secrets.fish
  10======PACKAGE-MANAGERS======19
  11__homebrew.fish
  12__mise.fish
  20=====TOOL-INTEGRATIONS======39
  21__direnv.fish
  22__zoxide.fish
  23__python.fish
  24__go.fish
  25__aws.fish
  26__home-assistant.fish
  40======CUSTOM-COMMANDS=======79
  41__general.fish
  42__git.fish
  43__chezmoi.fish
  44__docker.fish
  45__claude.fish
  46__network.fish
  47__file-utilities.fish
  48__system-utilities.fish
  49__tmux.fish
  50__k8s.fish
  80============PATH============89
  81__core-paths.fish
  82__language-paths.fish
  83__app-paths.fish
  90========COMPLETIONS=========99
  99__completions.fish
```

The separator files (e.g., `00=====SHELL-FUNDAMENTALS=====09`) are not scripts — they're zero-byte marker files that visually group sections in `ls` output. Fish ignores them because they don't end in `.fish`.

### Naming convention

`NN__description.fish` — two-digit prefix, double underscore, descriptive name. The double underscore visually separates the number from the name and makes it easy to sort.

### Adding a new file

1. Pick the category range
2. Choose the next available number in that range
3. Create: `chezmoi add` a new file or `chezmoi edit` to create from source

```bash
# Example: adding a Rust integration
chezmoi edit ~/.config/fish/conf.d/27__rust.fish
```

> **Gotcha.** Gaps in numbering are fine and expected. Don't renumber existing files to fill gaps — it creates unnecessary churn in version control and breaks muscle memory.

---

## The functions/ directory

Fish has autoloading functions: put a file named `foo.fish` in `~/.config/fish/functions/` and the function `foo` is available everywhere — but only loaded into memory when first called.

### How autoloading works

- File must be named exactly `functionname.fish`
- File must contain a function with the same name: `function functionname`
- One function per file (the primary one — helper functions inside are fine)
- Lazy-loaded: the file is read only when the function is first invoked
- Overrides: a function in `~/.config/fish/functions/` shadows any same-named function from the system or plugins

### When to use functions/ vs conf.d/

| Use `functions/` when... | Use `conf.d/` when... |
|---|---|
| Defining a standalone command | Setting env variables |
| The function is called infrequently (lazy loading saves startup time) | Activating tool integrations (direnv, zoxide) |
| You want tab completion on the function name | Defining abbreviations |
| Overriding a builtin or plugin function | Running setup code that must execute at shell start |

### Current functions

```
functions/
  cache_completions.fish    # completion caching utility
```

Most command definitions live in `conf.d/4x` files as abbreviations rather than in `functions/`. This is deliberate — abbreviations expand inline (you see the real command in history) and are simpler to maintain. See [aliases-and-abbreviations.md](aliases-and-abbreviations.md) for the full rationale.

> **Gotcha.** `funcsave` writes to `functions/` — if you define a function interactively and save it, it lands there outside chezmoi's control. Either `chezmoi add` it or delete it and put the definition in the appropriate `conf.d/` file instead.

---

## Fisher — plugin management

Fisher is fish's plugin manager. It's minimal: no plugin framework, no shell hooks, just git clone and symlink.

### How it works

- `fish_plugins` is the manifest file (like a lockfile)
- `fisher install` reads `fish_plugins` and installs everything listed
- `fisher update` updates all plugins to latest
- Plugins install files into `conf.d/`, `functions/`, and `completions/` — they use the same structure as your own config

### Current plugins

```
# fish_plugins
lengyijun/fisher          # Fisher manages itself
ilancosman/tide@v6        # Prompt theme (async, git-aware)
meaningful-ooo/sponge     # Removes failed commands from history
```

### Common operations

```bash
# Install a new plugin
fisher install author/plugin
# This updates fish_plugins automatically

# Update all plugins
fisher update

# Remove a plugin
fisher remove author/plugin

# Reinstall everything from fish_plugins (e.g., on a new machine)
fisher install
```

### Adding a plugin (chezmoi workflow)

1. Run `fisher install author/plugin` in a live shell
2. Fisher updates `~/.config/fish/fish_plugins`
3. Run `chezmoi re-add ~/.config/fish/fish_plugins` to sync the change back to source
4. Commit the updated `fish_plugins` in the chezmoi repo

On a new machine, `chezmoi apply` deploys `fish_plugins`, then a run_onchange script triggers `fisher install`.

> **Gotcha.** Fisher installs plugin files directly into your `conf.d/`, `functions/`, and `completions/` directories. These plugin-managed files should NOT be added to chezmoi — Fisher owns them. Only `fish_plugins` itself is chezmoi-managed.

---

## Managing with chezmoi

Fish config lives under `~/.config/fish/`. In chezmoi's source state, this maps to `dot_config/private_fish/`.

### Source tree

```
dot_config/private_fish/
  config.fish                           # minimal — just the is-interactive guard
  fish_plugins                          # Fisher manifest (plain file, not template)
  conf.d/
    01__keybinds-and-vi-mode.fish       # all the numbered conf.d files
    02__shell-env.fish
    ...
  functions/
    cache_completions.fish              # autoloaded functions
```

### Why `private_fish`?

The `private_` prefix tells chezmoi to set `0700` permissions on the directory. Fish stores sensitive data (like `fish_variables` which may contain secrets from `set -Ux`) in this directory, so restricting access is good practice.

### Key rules

- `fish_plugins` is a plain file, not a template — use `chezmoi re-add` after Fisher changes it
- `conf.d/` files are plain files unless they need templating (e.g., `03__secrets.fish` might become `.tmpl` when rbw integration lands)
- Don't add Fisher-managed files (plugin conf.d snippets, plugin functions, plugin completions) — they're regenerated by `fisher install`
- The section separator files (e.g., `00=====SHELL-FUNDAMENTALS=====09`) are managed by chezmoi so they appear on every machine

### Editing workflow

```bash
# Edit an existing conf.d file
chezmoi edit ~/.config/fish/conf.d/42__git.fish

# Add a new conf.d file
# First create it at the target, then add to chezmoi
vim ~/.config/fish/conf.d/27__rust.fish
chezmoi add ~/.config/fish/conf.d/27__rust.fish

# Preview what chezmoi would deploy
chezmoi diff

# Apply changes
chezmoi apply ~/.config/fish/
```

> **Gotcha.** `chezmoi status` may show Fisher-managed files as unmanaged. This is expected — don't add them. If `chezmoi apply` is removing Fisher files, check `.chezmoiignore` to make sure the relevant paths are excluded.

---

## Quick reference — zsh to fish mapping

| zsh concept | fish equivalent | Location |
|---|---|---|
| `.zshrc` (monolithic) | `conf.d/*.fish` (split by concern) | `~/.config/fish/conf.d/` |
| `.zshenv` | `conf.d/0x` files (shell-env, secrets) | Loads for all sessions, same as zshenv |
| `antigen bundle` / `zinit` | `fisher install` | Declared in `fish_plugins` |
| `~/.antigen/` | `~/.config/fish/` | Fisher installs directly into config tree |
| `export FOO=bar` | `set -gx FOO bar` | See [variables-and-path.md](variables-and-path.md) |
| `alias ll='ls -la'` | `abbr -a ll 'ls -la'` | See [aliases-and-abbreviations.md](aliases-and-abbreviations.md) |
| `compdef` / `compinit` / `fpath` | `complete` builtin + `completions/` dir | See [completions.md](completions.md) |
| `bindkey` | `bind` | In `conf.d/01__keybinds-and-vi-mode.fish` |
| `precmd` / `preexec` hooks | `--on-event fish_prompt` / `fish_preexec` | Event system, not direct hooks |
| Fold markers in one file | Numbered files with section separators | Self-documenting in `ls` output |
| `source ~/.zshrc` (reload) | `exec fish` (restart) | Fish caches aggressively — restart is cleaner |

---

## Cross-references

- [completions.md](completions.md) — completion system, `complete` builtin, caching strategy
- [variables-and-path.md](variables-and-path.md) — universal vs global vs local, PATH fish_add_path
- [aliases-and-abbreviations.md](aliases-and-abbreviations.md) — why abbreviations over aliases, migration from zsh
- [functions.md](functions.md) — autoloading deep dive, funcsave, event handlers
