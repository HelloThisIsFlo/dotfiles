# Mise Shims vs Activation — Cheat Sheet

Mise has two models for making tools available on your PATH: **activation** (a shell hook that rewrites PATH on every prompt) and **shims** (tiny wrapper scripts that resolve the right version at call time). You pick one as your primary, but they can coexist.

---

## The two models

### PATH activation (shell hook)

**The problem:** Your shell doesn't know about mise-managed tools unless something injects them into PATH. Activation solves this by running a hook on every prompt that scans your directory's config files and prepends the correct tool paths.

How it works:

1. You add `mise activate fish | source` to `~/.config/fish/config.fish`
2. This registers a prompt hook (`mise hook-env`) that fires before every prompt
3. `hook-env` reads `mise.toml` / `.tool-versions` for the current directory
4. It updates `$PATH` and sets any `[env]` variables defined in config
5. When you `cd` to a project with different versions, the next prompt picks them up automatically

```fish
# ~/.config/fish/config.fish (or conf.d/43__chezmoi.fish)
mise activate fish | source
```

What you get:
- Full `[env]` support — arbitrary environment variables work everywhere, not just in mise-managed tools
- All hooks work (`cd`, `enter`, `exit`, `watch_files`)
- `which node` shows the real path (e.g., `~/.local/share/mise/installs/node/20.11.0/bin/node`)
- Status messages when entering directories with tool configs (if `status.show_tools` is enabled)

### Shims (wrapper scripts)

**The problem:** Activation only works in interactive shells with a prompt. IDEs, cron jobs, scripts launched outside your shell — none of these trigger the prompt hook, so tools are invisible.

How it works:

1. Mise creates small executable scripts in `~/.local/share/mise/shims/` — one per binary
2. Each shim is a wrapper that calls mise, which resolves the correct tool version based on the directory's config, then executes it
3. You add the shims directory to PATH (either via `mise activate --shims` or manually)

```fish
# Option A: via activate (recommended — lets mise manage it)
mise activate fish --shims | source

# Option B: manual PATH entry
fish_add_path --prepend ~/.local/share/mise/shims
```

What you get:
- Works everywhere — IDEs, scripts, cron, `ssh` commands, inline `cd proj && node -v`
- No prompt hook overhead
- Simple mental model: shim intercepts command, loads context, runs real binary

What you lose:
- `[env]` variables only apply to mise-managed tool invocations, not your whole shell
- Most hooks don't fire (`cd`, `enter`, `exit`, `watch_files`)
- `which node` shows `~/.local/share/mise/shims/node` — use `mise which node` for the real path

---

## Comparison table

| Aspect | Activation | Shims |
|---|---|---|
| **Setup** | `mise activate fish \| source` in shell config | `mise activate fish --shims \| source` or manual PATH |
| **When PATH updates** | Every prompt (via `hook-env`) | At call time (shim resolves lazily) |
| **`[env]` variables** | Available to entire shell | Only available to mise-managed tool invocations |
| **Hooks (cd/enter/exit)** | Full support | Most don't fire |
| **`which <tool>`** | Shows real install path | Shows shim path |
| **IDE / non-interactive** | Doesn't work (no prompt = no hook) | Works out of the box |
| **Performance** | ~ms on each prompt | ~ms on each tool invocation |
| **`cd proj && node -v`** | May not work (hook hasn't fired yet) | Works (shim resolves at call time) |

---

## The hybrid: `mise activate --shims`

**The problem:** You want activation for your interactive shell but also need IDEs to find tools. You can use both.

```fish
# Interactive shell: full activation
mise activate fish | source

# Non-interactive / IDE contexts: shims
# (Add to ~/.config/fish/config.fish for login shells, or to your IDE's shell profile)
mise activate fish --shims | source
```

Mise automatically removes the shims directory from PATH when full `mise activate` runs, so having both lines doesn't cause conflicts. The activation takes precedence in interactive shells; shims serve as the fallback for everything else.

---

## IDE integration

**The problem:** IDEs launch tools from their own process, not from your interactive shell. The prompt hook never fires, so activation alone leaves IDEs blind to mise-managed tools.

**Approaches, in order of preference:**

1. **IDE plugin** (best) — VS Code: [mise-vscode](https://marketplace.visualstudio.com/items?itemName=hverlin.mise-vscode). JetBrains: [intellij-mise](https://github.com/134130/intellij-mise). These read `mise.toml` directly.
2. **Shims in PATH** — add `mise activate fish --shims | source` to your login shell profile. IDEs that inherit login environment will see the shims.
3. **`mise x`** — run tools through `mise x -- node script.js`. Works anywhere but requires wrapping every command.
4. **Manual path** — use `mise which node` to get the install path, paste it into IDE settings. Breaks on version changes.

For VS Code on macOS, also add to settings:
```json
{
  "terminal.integrated.automationProfile.osx": {
    "path": "/opt/homebrew/bin/fish",
    "args": ["--login"]
  }
}
```

---

## `mise hook-env` — under the hood

**The problem:** You're debugging activation and need to understand what the shell hook actually does.

`hook-env` is the function that `mise activate` registers as a prompt hook. On every prompt:

1. Checks current directory (and parents) for `mise.toml` / `.tool-versions`
2. Compares against the last-known state (skips work if nothing changed)
3. Modifies `$PATH` — prepends bin directories for active tools, removes stale ones
4. Sets/unsets `[env]` variables from config
5. Runs any configured hooks (`enter`, `cd`, etc.)

You can run it manually for debugging:

```fish
# See exactly what hook-env would change
mise hook-env --trace 2>&1 | less
```

The `--no-hook-env` flag on `mise activate` disables automatic execution — useful for isolating issues.

### Performance tuning

| Setting | Effect | Default |
|---|---|---|
| `hook_env.chpwd_only` | Only re-scan on directory change, not every prompt | `false` |
| `hook_env.cache_ttl` | Cache directory traversal (e.g., `5s` for NFS) | `0s` |
| `activate_aggressive` | Push mise paths to front of PATH on every prompt | `false` |

```toml
# ~/.config/mise/config.toml
[settings]
hook_env.chpwd_only = true   # skip re-scan if you haven't cd'd
activate_aggressive = true    # ensure mise versions always win PATH conflicts
```

---

## `mise reshim` — when and why

**The problem:** You installed a global npm package (`npm i -g tsx`) but the `tsx` command isn't found.

Mise auto-reshims when you install/update/remove tools via `mise install` or `mise use`. But if you install binaries through the tool's own package manager (npm, pip, cargo, etc.), mise may not notice.

```fish
# Force regeneration of all shims
mise reshim

# Nuclear option: delete all shims and regenerate
mise reshim --force
```

When you need it:
- After `npm i -g`, `pip install`, `cargo install` (especially via yarn/pnpm which bypass mise's detection)
- After manually modifying tool installations
- When a binary "should exist" but isn't found

You can automate it with a wrapper:
```fish
function npm
    command npm $argv
    mise reshim
end
```

Reshim is fast — the overhead is negligible.

---

## Shim configuration

| Setting | Description | Default |
|---|---|---|
| `MISE_SHIMS_DIR` | Override shims directory location | `~/.local/share/mise/shims` |
| `MISE_FISH_AUTO_ACTIVATE` | Auto-activate via fish's `vendor_conf.d` | `1` (enabled) |

Do not manually add files to the shims directory — `mise reshim` will delete them.

---

## Diagnosing PATH issues

**The problem:** A tool shows the wrong version, isn't found, or behaves unexpectedly.

```fish
# What does mise think is active?
mise ls

# Where does mise think a tool lives?
mise which node

# What does your shell think?
which node
type node

# Is the shims dir in PATH? Where?
echo $PATH | tr ' ' '\n' | grep -n mise

# What would hook-env change right now?
mise hook-env --trace 2>&1

# Full diagnostic
mise doctor
```

Common issues:
- **Wrong version**: Another PATH entry (homebrew, system) is shadowing mise. Fix: `activate_aggressive = true` or reorder PATH.
- **Tool not found in IDE**: Activation-only setup, no shims. Fix: add `mise activate fish --shims | source` to login profile.
- **Shim shows wrong version**: Stale shims. Fix: `mise reshim --force`.
- **`[env]` vars missing in IDE**: Using shims — `[env]` only applies during shim execution. Fix: use an IDE plugin instead.
- **Slow prompt**: `hook-env` rescanning on every prompt with a slow filesystem. Fix: `hook_env.chpwd_only = true` or set `hook_env.cache_ttl`.

---

## Verdict

- **Interactive shell (fish/bash/zsh):** Use activation. Full feature set, `[env]` works everywhere, hooks work.
- **IDEs:** Install the mise plugin for your editor. Fall back to shims if no plugin exists.
- **Scripts / cron / non-interactive:** Use shims or `mise x --`.
- **Hybrid (Flo's setup):** Activation in fish config for daily use. Add shims to login profile or IDE config only if an IDE can't find tools.

You almost never need to choose exclusively. Activation for interactive, shims as fallback for everything else.

---

## Related

- [Settings](settings.md) — `activate_aggressive`, `shims_dir`, and other activation settings
- [CI & Bootstrap](ci-bootstrap.md) — shims vs activation in CI contexts
- [Fish sourcing, secrets & tools](../fish/sourcing-secrets-and-tools.md)
- [Fish config structure](../fish/config-structure.md)
