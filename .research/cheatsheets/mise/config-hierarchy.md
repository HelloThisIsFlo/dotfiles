# Mise Config Hierarchy — Cheat Sheet

Mise resolves configuration by walking up from the current directory to `~/` and beyond, merging every config file it finds along the way. Understanding this hierarchy is key to knowing why a tool is a particular version and where that decision came from.

---

## Search order — project to global to system

Mise walks the directory tree upward from `$PWD`, collecting every config file it finds. Closer files win over distant ones.

```
~/src/myproj/backend/mise.toml     # 1st — most specific
~/src/myproj/mise.toml             # 2nd
~/mise.toml                        # 3rd (if it existed)
~/.config/mise/config.toml         # 4th — global user config
~/.config/mise/conf.d/*.toml       # loaded alongside global, alphabetically
/etc/mise/config.toml              # 5th — system-wide
/etc/mise/conf.d/*.toml            # loaded alongside system, alphabetically
```

- Walking stops at filesystem root (or at `MISE_CEILING_PATHS` if set)
- All files found are merged together — it's additive, not first-match
- Use `mise config ls` to see exactly which files are active and in what order

---

## Recognized config file names

Within any single directory, mise looks for these files (highest to lowest precedence):

| File | Notes |
|------|-------|
| `mise.{env}.local.toml` | Environment-specific local override (gitignored) |
| `mise.local.toml` | Local override, not committed |
| `mise.{env}.toml` | Environment-specific (e.g. `mise.production.toml`) |
| `mise.toml` | Primary project config |
| `.mise.toml` | Dotfile variant (same as `mise.toml`) |
| `mise/config.toml` | Subdirectory variant |
| `.mise/config.toml` | Hidden subdirectory variant |
| `.config/mise.toml` | XDG-style variant |
| `.config/mise/config.toml` | XDG-style subdirectory variant |
| `.tool-versions` | asdf-compatible legacy format |

In practice, most projects use `mise.toml` (project) and `~/.config/mise/config.toml` (global). The others exist for edge cases and preferences.

---

## `settings.toml` vs `config.toml` — there is no separate settings file

Mise does **not** have a separate `settings.toml`. Settings live inside any `mise.toml` under the `[settings]` section:

```toml
# ~/.config/mise/config.toml (global config)

[tools]
node = 'lts'
python = '3.13'

[settings]
idiomatic_version_file_enable_tools = ['python', 'node', 'ruby', 'java']
env_file = '.env'
ruby.compile = false
```

- **`[tools]`** = which tool versions to install
- **`[env]`** = environment variables to set
- **`[tasks]`** = task runner definitions
- **`[settings]`** = mise's own behavior (how it operates, not what it manages)

Settings can also be set via:
- `mise settings key=value` CLI command
- Environment variables with `MISE_` prefix (e.g. `MISE_ENV_FILE=.env`)

Settings in project-level configs override global settings via the same merge rules as everything else.

---

## `conf.d/` — splitting config into fragments

Instead of one monolithic `config.toml`, you can split configuration into multiple files under `conf.d/`:

```
~/.config/mise/conf.d/
  01-languages.toml       # node, python, ruby, etc.
  02-infrastructure.toml  # terraform, kubectl, etc.
  03-cli-tools.toml       # delta, cheat, usage, etc.
```

- Files load in **alphabetical order** (hence the numeric prefixes)
- Each file is a standard `mise.toml` — can contain `[tools]`, `[settings]`, `[env]`, etc.
- Same pattern exists at system level: `/etc/mise/conf.d/*.toml`

**When to use it:** When your global config grows large enough that a single file feels unwieldy, or when you want to manage different tool categories independently.

Your current global config has this note at the top:

```toml
# Note: This can be migrated to a `.config/mise/conf.d/*.toml` format,
#       if need more flexibility in the future.
```

---

## Merge semantics — how config files combine

Different sections have different merge behavior:

| Section | Merge strategy | Example |
|---------|---------------|---------|
| `[tools]` | Additive + override | Project says `node = '20'`, global says `node = 'lts'` and `python = '3.13'` — result: `node = '20'`, `python = '3.13'` |
| `[env]` | Additive + override | Same as tools — child values override, parent values preserved |
| `[settings]` | Additive + override | Project settings override global settings |
| `[tasks]` | Full replacement per task | If project defines task `test`, it completely replaces any parent `test` task |

**Key insight:** "Additive + override" means closer configs add new keys and replace conflicting ones, but don't remove keys from parent configs. A project `mise.toml` with only `node` defined won't remove `python` from your global config — you'll get both.

---

## Profiles and `MISE_ENV` — environment-specific config

**The problem:** You need different tool versions or env vars for development vs CI vs production, but don't want to maintain separate config files manually.

Set `MISE_ENV` and mise automatically loads environment-specific files:

```bash
MISE_ENV=production mise install
# or
mise -E production install
```

This activates `mise.production.toml` files at every level of the hierarchy. The full precedence becomes:

```
mise.production.local.toml    # highest — env-specific local
mise.local.toml               # local override
mise.production.toml          # env-specific
mise.toml                     # base config
```

**Multiple environments:** `MISE_ENV=ci,staging` — later values take precedence.

**Important:** `MISE_ENV` cannot be set inside `mise.toml` — it determines which files to load in the first place.

---

## Local overrides — `mise.local.toml`

**The problem:** You need machine-specific overrides (a different Python version, extra env vars) that shouldn't be committed to the project repo.

```toml
# mise.local.toml (in project root, gitignored)
[tools]
python = '3.11'  # override the project's 3.13 for this machine

[env]
DATABASE_URL = 'postgres://localhost/mydb_dev'
```

Add to `.gitignore`:

```gitignore
mise.local.toml
mise.*.local.toml
```

The `.local.toml` variants always take precedence over their non-local counterparts at the same directory level.

---

## Legacy/idiomatic version files

**The problem:** Many tools have their own version file convention (`.python-version`, `.node-version`, `.nvmrc`). You want mise to respect these so the same version files work for team members using different version managers.

**Disabled by default** since mise 2025.10.0 to avoid accidental tool management from unrelated files like `go.mod` or `Gemfile`.

Opt in per tool:

```toml
# In ~/.config/mise/config.toml
[settings]
idiomatic_version_file_enable_tools = ['python', 'node', 'ruby', 'java']
```

This enables:

| Setting value | Files recognized |
|--------------|-----------------|
| `python` | `.python-version` |
| `node` | `.node-version`, `.nvmrc` |
| `ruby` | `.ruby-version` |
| `java` | `.java-version` |

These files contain a bare version string (e.g. `3.13`) and are recognized anywhere in the directory walk-up, just like `mise.toml`.

---

## Template support in config files

Mise uses [Tera](https://keats.github.io/tera/) templates (Jinja2-like syntax) in config files:

```toml
[env]
PROJECT_NAME = "{{ cwd | basename }}"

[tools]
terraform = "{{ env.TERRAFORM_VERSION }}"
```

**Available variables:**

- `env` — current environment variables (key-value map)
- `cwd` — current working directory
- `config_root` — directory containing the config file
- `mise_bin`, `mise_pid` — mise executable path and process ID
- `xdg_cache_home`, `xdg_config_home`, `xdg_data_home`, `xdg_state_home`
- `tools` — installed tools with version and path info

**Available features:** filters (`lower`, `upper`, `trim`, `basename`), functions (`exec()`, `read_file()`, `arch()`, `os()`), conditionals, loops.

---

## `mise config` — inspect resolved configuration

```bash
mise config ls              # list all active config files and their tools
mise config ls --json       # same, as JSON
mise config ls --no-header  # without table header
mise config get             # get specific config values
mise config set             # modify config values
mise config --tracked-configs  # show all monitored config files
```

**Use `mise config ls` as your debugging tool.** When you're confused about which file is providing a particular tool version, this tells you exactly which configs are loaded and what each one contributes.

---

## Decision guide — where to put what

| What you want | Where to put it |
|--------------|----------------|
| Global default tool versions | `~/.config/mise/config.toml` `[tools]` |
| Project-specific tool versions | `./mise.toml` `[tools]` |
| Machine-specific overrides (not committed) | `./mise.local.toml` |
| Mise behavior settings (idiomatic files, env_file, etc.) | `~/.config/mise/config.toml` `[settings]` (or project-level to override) |
| Environment-specific config (CI, prod) | `./mise.production.toml`, activated via `MISE_ENV=production` |
| Modular global config (split by category) | `~/.config/mise/conf.d/01-languages.toml`, `02-infra.toml`, etc. |
| Team members using nvm/pyenv | Enable idiomatic files + commit `.python-version` / `.node-version` |
| System-wide defaults (multi-user) | `/etc/mise/config.toml` or `/etc/mise/conf.d/*.toml` |

---

## Key environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `MISE_ENV` | (unset) | Activate environment-specific config files |
| `MISE_GLOBAL_CONFIG_FILE` | `~/.config/mise/config.toml` | Override global config path |
| `MISE_SYSTEM_CONFIG_DIR` | `/etc/mise` | Override system config directory |
| `MISE_CEILING_PATHS` | (unset) | Stop directory walk-up at these paths |

---

## Related

- [Settings](settings.md) — all settings that can go in `[settings]`
- [Environment](environment.md) — `[env]` section, dotenv, PATH manipulation
- [Tool Management](tool-management.md) — version specifiers and install commands
