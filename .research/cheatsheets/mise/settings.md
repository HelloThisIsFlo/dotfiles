# Mise Settings — Cheat Sheet

Mise settings control tool installation behavior, environment handling, network timeouts, language-specific compilation, and status display. They can be set in multiple places with a clear precedence order, or overridden per-invocation via environment variables.

---

## Where settings live

**Three places, highest priority wins:**

1. **Environment variables** — `MISE_<SETTING>` (underscores, uppercase). Highest priority.
   - Nested settings use `_` separator: `MISE_PYTHON_COMPILE=1`, `MISE_STATUS_MESSAGE_MISSING_TOOLS=always`
2. **Project config** — `[settings]` section in `mise.toml` (or `mise.local.toml` for untracked overrides)
3. **Global config** — `~/.config/mise/config.toml` under `[settings]`. Lowest priority.

There is no separate `settings.toml` file — settings always go in `[settings]` inside `config.toml` or `mise.toml`.

**Flo's current global settings** (in `~/.config/mise/config.toml`):

```toml
[settings]
idiomatic_version_file_enable_tools = ['python', 'node', 'ruby', 'java']
ruby.compile = false
env_file = '.env'
```

---

## `mise settings` CLI

```bash
mise settings                              # show all active settings
mise settings --all                        # show all settings including defaults
mise settings jobs                         # get a single setting's value
mise settings jobs=16                      # set a value (global config)
mise settings set jobs 16                  # same thing, alternate syntax
mise settings unset jobs                   # remove from config (reverts to default)
mise settings add trusted_config_paths ~/work  # append to a list setting
mise settings -l jobs=16                   # set in local (project) config
mise settings --json                       # output as JSON
mise settings --toml                       # output as TOML
mise settings --json-extended              # JSON with source info per setting
```

---

## Core behavior

| Setting | Default | Env var | What it does |
|---------|---------|---------|-------------|
| `experimental` | `false` | `MISE_EXPERIMENTAL` | Enable experimental features (hooks, some backends). Required for bleeding-edge stuff. |
| `auto_install` | `true` | `MISE_AUTO_INSTALL` | Install missing tools automatically during `mise x`, `mise run`, and shell activation. Turn off if you want explicit `mise install` only. |
| `not_found_auto_install` | `true` | `MISE_NOT_FOUND_AUTO_INSTALL` | Install tools via the "command not found" shell handler. Handy for first-time use in a project. |
| `auto_install_disable_tools` | `[]` | `MISE_AUTO_INSTALL_DISABLE_TOOLS` | Skip auto-install for specific tools (e.g., large compilers you want to install manually). |
| `jobs` | `8` | `MISE_JOBS` | Parallel installation jobs. Increase on beefy machines, decrease if hitting rate limits. |
| `raw` | `false` | `MISE_RAW` | Pass stdin/stdout/stderr through to child processes. Required for interactive installs (e.g., Ruby with prompts). |
| `yes` | `false` | `MISE_YES` | Auto-confirm all prompts. Useful in CI/scripts. |
| `pin` | `false` | `MISE_PIN` | Default to `--pin` behavior in `mise use` (write exact versions, not ranges). |

---

## Environment

| Setting | Default | Env var | What it does |
|---------|---------|---------|-------------|
| `env_file` | none | `MISE_ENV_FILE` | Auto-source a dotenv file when entering a directory. **Flo: `.env`** |
| `trusted_config_paths` | `[]` | `MISE_TRUSTED_CONFIG_PATHS` | Directories to auto-trust (skip the `mise trust` prompt). Useful for `~/work/` or `~/projects/`. Colon-separated in env var. |
| `ignored_config_paths` | `[]` | `MISE_IGNORED_CONFIG_PATHS` | Config files mise should completely ignore. |
| `ceiling_paths` | `[]` | `MISE_CEILING_PATHS` | Stop walking up the directory tree at these paths. Prevents picking up stray configs from parent dirs. |
| `env_shell_expand` | none | `MISE_ENV_SHELL_EXPAND` | Enable shell-style variable expansion (`$HOME`, `${VAR}`) in `[env]` values. |
| `no_env` | none | `MISE_NO_ENV` | Skip loading environment variables from config files entirely. |
| `no_hooks` | none | `MISE_NO_HOOKS` | Disable hook execution from config files. |

---

## Version files

| Setting | Default | Env var | What it does |
|---------|---------|---------|-------------|
| `idiomatic_version_file_enable_tools` | `[]` | `MISE_IDIOMATIC_VERSION_FILE_ENABLE_TOOLS` | Which tools should read legacy version files (`.python-version`, `.node-version`, `.ruby-version`, `.java-version`). **Flo: `['python', 'node', 'ruby', 'java']`** |
| `disable_tools` | `[]` | `MISE_DISABLE_TOOLS` | Globally ignore these tools even if they appear in configs. |
| `enable_tools` | `[]` | `MISE_ENABLE_TOOLS` | Allowlist mode: only use these tools, ignore everything else. |
| `disable_backends` | `[]` | `MISE_DISABLE_BACKENDS` | Disable specific backends (e.g., `asdf`, `pipx`, `vfox`). |
| `default_config_filename` | `mise.toml` | `MISE_DEFAULT_CONFIG_FILENAME` | Override the default config filename mise looks for. |

---

## Network and performance

| Setting | Default | Env var | What it does |
|---------|---------|---------|-------------|
| `http_timeout` | `30s` | `MISE_HTTP_TIMEOUT` | Timeout for HTTP requests. Increase on slow connections. |
| `http_retries` | `0` | `MISE_HTTP_RETRIES` | Number of retries with exponential backoff. Set to `3` for flaky networks. |
| `fetch_remote_versions_timeout` | `20s` | `MISE_FETCH_REMOTE_VERSIONS_TIMEOUT` | Timeout specifically for version resolution API calls. |
| `fetch_remote_versions_cache` | `1h` | `MISE_FETCH_REMOTE_VERSIONS_CACHE` | How long to cache remote version lists. |
| `cache_prune_age` | `30d` | `MISE_CACHE_PRUNE_AGE` | Age before cache files are pruned. |
| `offline` | `false` | `MISE_OFFLINE` | Never make HTTP requests. Only use cached/installed data. |
| `prefer_offline` | `false` | `MISE_PREFER_OFFLINE` | Use cache first, fall back to network. Good for airplane mode. |
| `use_versions_host` | `true` | `MISE_USE_VERSIONS_HOST` | Use mise's version resolution service instead of hitting upstream APIs directly. Faster, but can lag behind releases. |

---

## Language-specific

### Python

| Setting | Default | Env var | What it does |
|---------|---------|---------|-------------|
| `python.compile` | none | `MISE_PYTHON_COMPILE` | `true` = compile from source (slow, custom flags). `false` = use precompiled binaries (fast). Default auto-detects. |
| `python.uv_venv_auto` | `false` | `MISE_PYTHON_UV_VENV_AUTO` | Auto-create/source uv venvs. Values: `false`, `source` (source existing only), `create\|source` (create if missing), `true` (legacy). |
| `python.venv_stdlib` | `false` | `MISE_VENV_STDLIB` | Prefer stdlib `venv` module over `virtualenv`. |
| `python.default_packages_file` | none | `MISE_PYTHON_DEFAULT_PACKAGES_FILE` | File listing packages to install with every new Python version. |

### Ruby

| Setting | Default | Env var | What it does |
|---------|---------|---------|-------------|
| `ruby.compile` | none | `MISE_RUBY_COMPILE` | `true` = compile from source. `false` = use precompiled binaries. **Flo: `false`** (precompiled is faster, no build deps needed). |
| `ruby.default_packages_file` | `~/.default-gems` | `MISE_RUBY_DEFAULT_PACKAGES_FILE` | File listing gems to install with every new Ruby version. |

### Node

| Setting | Default | Env var | What it does |
|---------|---------|---------|-------------|
| `node.compile` | none | `MISE_NODE_COMPILE` | `true` = compile from source (rarely needed). `false` = precompiled. |
| `node.corepack` | `false` | `MISE_NODE_COREPACK` | Install corepack shims (for pnpm/yarn version management) after Node install. |
| `node.default_packages_file` | `~/.default-npm-packages` | `MISE_NODE_DEFAULT_PACKAGES_FILE` | File listing npm packages to install with every new Node version. |

### Go

| Setting | Default | Env var | What it does |
|---------|---------|---------|-------------|
| `go.default_packages_file` | `~/.default-go-packages` | `MISE_GO_DEFAULT_PACKAGES_FILE` | File listing Go packages to install with every new Go version. |

### All languages

| Setting | Default | Env var | What it does |
|---------|---------|---------|-------------|
| `all_compile` | `false` | `MISE_ALL_COMPILE` | Force compile-from-source for every language. Nuclear option. |

---

## Display and status

| Setting | Default | Env var | What it does |
|---------|---------|---------|-------------|
| `status.missing_tools` | `if_other_versions_installed` | `MISE_STATUS_MESSAGE_MISSING_TOOLS` | When to warn about missing tools. Values: `if_other_versions_installed` (only if you have other versions), `always`, `never`. |
| `status.show_env` | `false` | `MISE_STATUS_MESSAGE_SHOW_ENV` | Show which env vars changed when entering a directory. Useful for debugging `[env]` and `env_file`. |
| `status.show_tools` | `false` | `MISE_STATUS_MESSAGE_SHOW_TOOLS` | Show which tools activated when entering a directory. |
| `quiet` | `false` | `MISE_QUIET` | Suppress all output except errors. |
| `silent` | `false` | `MISE_SILENT` | Suppress `mise run`/`mise watch` output except errors. |
| `verbose` | `false` | `MISE_VERBOSE` | Show verbose output including installation logs. |
| `color` | `true` | `MISE_COLOR` | Enable colored terminal output. |
| `color_theme` | `default` | `MISE_COLOR_THEME` | Theme for output. Options: `default`, `charm`, `base16`, `catppuccin`, `dracula`. |

---

## Security

| Setting | Default | Env var | What it does |
|---------|---------|---------|-------------|
| `paranoid` | `false` | `MISE_PARANOID` | Extra-secure mode. Disables implicit trust, requires explicit verification. |
| `github_attestations` | `true` | `MISE_GITHUB_ATTESTATIONS` | Verify GitHub artifact authenticity via attestations. |
| `gpg_verify` | none | `MISE_GPG_VERIFY` | Use GPG to verify tool signatures. |
| `lockfile` | none | `MISE_LOCKFILE` | Read/update lockfiles (`mise.lock`) for reproducible installs. |
| `locked` | `false` | `MISE_LOCKED` | Strict mode: fail if tools lack pre-resolved URLs in lockfile. Good for CI. |

---

## Lockfiles and installation

| Setting | Default | Env var | What it does |
|---------|---------|---------|-------------|
| `always_keep_download` | `false` | `MISE_ALWAYS_KEEP_DOWNLOAD` | Keep downloaded archives after installation. Useful for debugging. |
| `always_keep_install` | `false` | `MISE_ALWAYS_KEEP_INSTALL` | Keep install artifacts even on failure. Useful for debugging failed builds. |
| `install_before` | none | `MISE_INSTALL_BEFORE` | Only install versions released before this date. Values: `7d`, `90d`, `2024-06-01`. Safety net against brand-new buggy releases. |

---

## Related

- [Config Hierarchy](config-hierarchy.md) — where settings files live and how they merge
- [Language Features](language-features.md) — language-specific settings in depth
- [Security & Trust](security-trust.md) — trust and paranoid mode settings
- [Mise documentation — settings reference](https://mise.jdx.dev/configuration/settings.html)
