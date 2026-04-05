# Mise Environment — Cheat Sheet

Mise manages environment variables per-project (or globally), activated automatically when you `cd` into a directory. It replaces `.env`-sourcing shell plugins, `direnv`, and manual `export` blocks with a single `[env]` section in `mise.toml`.

---

## Setting env vars: the `[env]` section

**The problem:** You need project-specific env vars that activate automatically without polluting your global shell.

```toml
# mise.toml
[env]
NODE_ENV = "production"
DATABASE_URL = "postgres://localhost/myapp"
```

Unset a variable (removes it from the environment):

```toml
[env]
UNWANTED_VAR = false
```

**Verdict:** This is the bread and butter. Vars set here activate whenever mise loads this config (on `cd`, `mise exec`, `mise run`, etc.).

---

## Auto-sourcing dotenv files: `env_file`

**The problem:** You already have `.env` files everywhere and don't want to duplicate them into `mise.toml`.

Two ways to do this:

### Global setting (what you use)

```toml
# ~/.config/mise/config.toml
[settings]
env_file = '.env'
```

This tells mise to auto-load `.env` from the current directory for every project. Uses the `dotenvy` parser.

### Per-project with `_.file`

```toml
# mise.toml
[env]
_.file = '.env'
```

Supports multiple files and different formats (dotenv, JSON, YAML):

```toml
[env]
_.file = [
    '.env',
    '.env.local',
    { path = ".secrets.env", redact = true }
]
```

**Verdict:** The global `env_file` setting is convenient when every project uses `.env`. Use `_.file` in `mise.toml` when you need per-project control or multiple/non-standard files.

---

## PATH manipulation: `_.path`

**The problem:** Project has local binaries (`./bin`, `./node_modules/.bin`) that need to be on PATH.

```toml
[env]
_.path = "./bin"
```

Multiple paths:

```toml
[env]
_.path = [
    "{{config_root}}/bin",
    "{{config_root}}/node_modules/.bin",
    "~/.local/share/bin"
]
```

- Relative paths resolve from `config_root` (the directory containing `mise.toml`)
- Paths are prepended to `$PATH`
- Supports templates (see below)

**Verdict:** Replaces `export PATH="./bin:$PATH"` hacks in shell config. Clean and automatic.

---

## Sourcing shell scripts: `_.source`

**The problem:** Some env vars come from a script that computes them dynamically (credentials, build info, etc.).

```toml
[env]
_.source = "./scripts/env.sh"
```

Multiple sources with redaction:

```toml
[env]
_.source = [
    "./scripts/base-env.sh",
    { path = "./scripts/secrets.sh", redact = true }
]
```

The script is `source`d (shebang is ignored). Any `export`ed variables become available.

**Verdict:** Useful for dynamic values that can't be expressed as static strings. Keep scripts fast — they run on every activation.

---

## Templates in env values

**The problem:** Env values need to reference other vars, the project root, or system paths.

Mise uses Tera template syntax:

```toml
[env]
PROJECT_ROOT = "{{config_root}}"
LD_LIBRARY_PATH = "{{config_root}}/lib:{{env.LD_LIBRARY_PATH}}"
DATA_DIR = "{{env.HOME}}/.local/share/myapp"
```

Key template variables:
- `{{config_root}}` — directory containing the `mise.toml` file
- `{{env.HOME}}`, `{{env.USER}}`, `{{env.VAR}}` — read existing env vars
- `{{tools.node.version}}` — tool versions (requires `tools = true`, see below)

### Shell-style expansion (alternative)

```toml
[settings]
env_shell_expand = true

[env]
LD_LIBRARY_PATH = "$PROJECT_LIB:$LD_LIBRARY_PATH"
FALLBACK = "${UNDEFINED_VAR:-default_value}"
```

Supports `$VAR`, `${VAR}`, and `${VAR:-default}`.

### Referencing tool-provided env vars

Some values (like tool paths) aren't available until tools are installed. Use `tools = true` to defer evaluation:

```toml
[env]
GEM_BIN = { value = "{{env.GEM_HOME}}/bin", tools = true }
NODE_VER = { value = "{{tools.node.version}}", tools = true }
_.path = { path = ["{{env.GEM_HOME}}/bin"], tools = true }
```

**Verdict:** Tera templates are the default and more explicit. Shell expansion (`env_shell_expand`) is simpler if you're used to `$VAR` syntax. Pick one per project.

---

## Automatic virtualenv: `_.python.venv`

**The problem:** You want a Python virtualenv created and activated automatically when entering a project.

Basic:

```toml
[env]
_.python.venv = ".venv"
```

With auto-creation:

```toml
[env]
_.python.venv = { path = ".venv", create = true }
```

Full options:

```toml
[env]
_.python.venv = {
    path = ".venv",
    create = true,
    python = "3.12",
    uv_create_args = ["--seed"]
}
```

| Parameter | Default | Purpose |
|---|---|---|
| `path` | — | Venv location (relative or absolute, supports templates) |
| `create` | `false` | Auto-create if missing |
| `python` | system | Python version for creation |
| `python_create_args` | `[]` | Args for `python -m venv` |
| `uv_create_args` | `[]` | Args for `uv venv` (used when `uv` is installed) |

**Verdict:** Replaces manual `python -m venv` + `source .venv/bin/activate`. If you use `uv`, add `--seed` to get pip/setuptools in the venv.

---

## Directory-specific env via project `mise.toml`

**The problem:** Different projects need different env vars, and you don't want them leaking across projects.

Just put a `mise.toml` in each project root:

```
~/src/work/api/mise.toml     → NODE_ENV=production, DATABASE_URL=...
~/src/work/frontend/mise.toml → NODE_ENV=development, API_URL=...
~/src/personal/mise.toml     → different vars entirely
```

Mise walks up the directory tree and merges configs. A nested `mise.toml` overrides vars from parent directories.

For local overrides (git-ignored):

```toml
# mise.local.toml  (add to .gitignore)
[env]
DATABASE_URL = "postgres://localhost/myapp_dev"
```

---

## Environment variable precedence

**The problem:** You have global, project, and local configs all setting env vars. Which wins?

Precedence (highest to lowest):

| Priority | Source |
|---|---|
| 1 (highest) | `mise.{ENV}.local.toml` |
| 2 | `mise.local.toml` |
| 3 | `mise.{ENV}.toml` |
| 4 | `mise.toml` |
| 5 | Parent directory configs (walking up) |
| 6 | `~/.config/mise/config.toml` (global) |
| 7 (lowest) | `/etc/mise/config.toml` (system) |

Within a single `[env]` section, vars are evaluated top-to-bottom (later entries can reference earlier ones via templates).

The `[env]` section is **additive with overrides** — global vars merge with project vars, with closer configs winning on conflicts.

**Verdict:** Local > project > global. Use `mise.local.toml` for secrets or personal overrides that shouldn't be committed.

---

## Redaction and masking of sensitive vars

**The problem:** `mise env` output includes secrets. You want to hide them in logs and output.

Per-variable:

```toml
[env]
API_KEY = { value = "sk-abc123", redact = true }
```

Per-file or per-source:

```toml
[env]
_.file = { path = ".secrets.env", redact = true }
_.source = { path = "./load-secrets.sh", redact = true }
```

Pattern-based (bulk redaction):

```toml
redactions = ["SECRET_*", "*_TOKEN", "*_KEY", "PASSWORD"]

[env]
SECRET_DB = "sensitive"
API_TOKEN = "also-sensitive"
```

Inspect redacted values:

```bash
mise env                    # redacted values hidden
mise env --redacted         # show only redacted vars
mise env --values           # show values without export syntax
mise set --no-redact        # show unmasked values in mise set output
```

**Verdict:** Always redact secrets. Pattern-based redaction (`redactions = [...]`) is the cleanest approach for projects with many secrets.

---

## Required variables

**The problem:** A project needs certain env vars to be set, and you want a clear error if they're missing.

```toml
[env]
DATABASE_URL = { required = true }
API_KEY = { required = "Set API_KEY — see .env.example for format" }
```

The variable must be satisfied by a pre-existing env var, a parent config, or a `mise.local.toml`. Mise errors with the help text if it's unset.

**Verdict:** Use for vars that come from outside the config (secrets, local-only settings). The help text string form is much better than bare `true`.

---

## Inspecting resolved environment: `mise env`

**The problem:** You need to see what mise would actually set, after all configs are merged.

```bash
mise env                    # shell export statements
mise env -s fish            # fish-compatible output
mise env --json             # JSON format
mise env --json-extended    # JSON with source file metadata
mise env --dotenv           # .env format
mise env -s bash | source   # one-shot activation in bash
mise env -s fish | source   # one-shot activation in fish
```

Useful flags:
- `-s, --shell <SHELL>` — target shell (bash, fish, zsh, nu, etc.)
- `-J, --json` — machine-readable output
- `--json-extended` — includes which config file each var came from
- `--dotenv` / `-D` — dotenv format
- `--redacted` — show only redacted vars
- `--values` — values only (no `export` prefix)

**Verdict:** `mise env --json-extended` is the debugging power tool — shows exactly which file set each variable.

---

## Quick env var setting: `mise set`

**The problem:** You want to add an env var without hand-editing `mise.toml`.

```bash
mise set NODE_ENV=production            # writes to ./mise.toml
mise set -g DATABASE_URL=postgres://... # writes to global config
mise set -E staging NODE_ENV=staging    # writes to mise.staging.toml
mise set                                # list all env vars with sources
```

Interactive and stdin modes:

```bash
mise set --prompt PASSWORD              # hidden input (no echo)
cat key.pem | mise set --stdin MY_KEY   # multiline value from stdin
```

Experimental encryption:

```bash
mise set --age-encrypt API_KEY=secret   # encrypt with age
```

**Verdict:** Handy for quick one-offs. For anything involving multiple vars or templates, edit `mise.toml` directly.

---

## Duplicate directive keys: `[[env]]` syntax

**The problem:** TOML doesn't allow duplicate keys, but you need multiple `_.source` or `_.file` entries.

```toml
[[env]]
_.source = "./scripts/base.sh"

[[env]]
_.source = "./scripts/secrets.sh"
```

Use `[[env]]` (array-of-tables) instead of `[env]` when you need multiple entries for the same directive.

---

## Decision guide

| I want to... | Use |
|---|---|
| Set static env vars | `[env]` section in `mise.toml` |
| Load `.env` files automatically | `env_file = '.env'` in settings (global) or `_.file` (per-project) |
| Add dirs to PATH | `_.path = ["./bin"]` |
| Source a shell script | `_.source = "./script.sh"` |
| Auto-create Python venvs | `_.python.venv = { path = ".venv", create = true }` |
| Reference project root in values | `{{config_root}}` template |
| Reference existing env vars | `{{env.HOME}}` template or `$HOME` with `env_shell_expand` |
| Hide secrets in output | `redact = true` per-var or `redactions = [...]` patterns |
| Require a var without setting it | `DATABASE_URL = { required = "help text" }` |
| Inspect resolved env | `mise env --json-extended` |
| Quick-set a var from CLI | `mise set KEY=value` |
| Override per-machine (not committed) | `mise.local.toml` |

---

## Related

- [Config Hierarchy](config-hierarchy.md) — file search order and merge semantics
- [Settings](settings.md) — `env_file` and other environment-related settings
- [Security & Trust](security-trust.md) — trust implications of `[env]` sections
- [Fish sourcing, secrets & tools](../fish/sourcing-secrets-and-tools.md)
