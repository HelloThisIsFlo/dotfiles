# Mise Language Features — Cheat Sheet

Mise has built-in, language-aware support for several runtimes — auto-env-vars, precompiled binaries, idiomatic version files, and default packages. This covers the settings and gotchas for each.

---

## Idiomatic Version Files (cross-language)

Mise can read `.python-version`, `.node-version`, `.ruby-version`, `.java-version`, `.nvmrc`, `.sdkmanrc`, etc. Disabled by default since 2025.10.0 to prevent mise from auto-managing tools based on unrelated files (e.g. `go.mod`, `Gemfile`).

Opt in per tool:

```toml
# ~/.config/mise/config.toml
[settings]
idiomatic_version_file_enable_tools = ['python', 'node', 'ruby', 'java']
```

- Only enable for tools with a dedicated `.{tool}-version` convention
- `.python-version` — used by uv, pyenv, most CI platforms
- `.node-version` — used by nvm, fnm, Vercel, Netlify
- `.ruby-version` — used by rbenv, chruby
- `.java-version` — used by jenv, sdkman

---

## Python

### Version pinning

```toml
[tools]
python = '3.13'
uv = 'latest'
```

- Multiple versions: `python = ['3.13', '3.12']` — first is default, both available via `python3.12`, `python3.13`
- `.python-version` / `.python-versions` files supported (needs opt-in above)

### Compile setting

```toml
[settings]
python.compile = true   # always compile from source via python-build
python.compile = false  # always use precompiled binaries
# unset = precompiled when available, compile otherwise (default)
```

- Precompiled binaries are much faster to install and need no build deps
- Analogous to `ruby.compile`

### Auto-virtualenv (`_.python.venv`)

Per-project venv creation and activation:

```toml
# project mise.toml
[env]
_.python.venv = { path = ".venv", create = true }

# with specific python version
_.python.venv = { path = ".venv", create = true, python = "3.12" }
```

- Activates the venv automatically when entering the directory
- `create = true` — creates the venv if it doesn't exist
- Uses `uv venv` instead of `python -m venv` when uv is installed

### uv integration

- When uv is installed via mise, it replaces `python -m venv` for venv creation
- `python.uv_venv_auto` — auto-manage `.venv` when `uv.lock` exists:
  - `false` (default) — disabled
  - `"source"` — activate existing `.venv` only
  - `"create|source"` — create if missing, then activate

**Gotcha:** uv-created venvs don't include pip by default. If you need pip inside the venv, add `uv_create_args = ['--seed']` to the venv config.

---

## Node

### Version pinning

```toml
[tools]
node = 'lts'     # tracks latest LTS
node = '22'      # latest 22.x
```

- `.node-version` and `.nvmrc` files supported (needs opt-in)
- Drop-in replacement for nvm

### Default packages

Create `~/.default-npm-packages` (one package per line):

```
typescript@latest
@types/node@^20
pnpm
```

- Installed automatically after every new Node version install
- Configurable path via `node.default_packages_file` setting

### Corepack

```toml
[settings]
node.corepack = true   # default: false
```

- Automatically installs corepack shims after each Node install
- Enables `pnpm` and `yarn` version management via `package.json` `packageManager` field

---

## Ruby

### Version pinning

```toml
[tools]
ruby = '3'
```

- `.ruby-version` supported (needs opt-in)
- `Gemfile` ruby version detection also possible

### Compile setting

```toml
[settings]
ruby.compile = false   # use precompiled binaries (faster, no build deps)
ruby.compile = true    # always compile from source via ruby-build
# unset = compile from source (default changes to precompiled in 2026.8.0)
```

- Precompiled binaries available for: macOS arm64, Linux arm64, Linux x86_64
- Significantly faster installs — seconds instead of minutes

### Default gems

Create `~/.default-gems` (one gem per line):

```
bundler
pry
rubocop --pre    # supports flags
bcat ~> 0.6.0   # supports version constraints
```

- Installed after every new Ruby version install
- Configurable path via `ruby.default_packages_file`

---

## Java

### Distribution selection

```toml
[tools]
java = 'temurin-21'     # Eclipse Adoptium (recommended for LTS)
# java = 'corretto-21'  # Amazon
# java = 'zulu-21'      # Azul
# java = '21'           # OpenJDK (stops getting updates after ~6 months)
```

- **Don't use the shorthand `java = '21'`** — defaults to OpenJDK which has short support windows
- Temurin (Eclipse Adoptium) provides long-term updates — see [whichjdk.com](https://whichjdk.com)
- Supported vendors: Temurin, Zulu, Corretto, OpenJDK

### JAVA_HOME

- Mise sets `JAVA_HOME` automatically
- macOS apps that use `/usr/libexec/java_home` need manual symlink setup:
  ```bash
  sudo mkdir -p /Library/Java/JavaVirtualMachines/temurin-21.jdk
  sudo ln -s ~/.local/share/mise/installs/java/temurin-21/Contents \
    /Library/Java/JavaVirtualMachines/temurin-21.jdk/Contents
  ```

### `.java-version` / `.sdkmanrc`

- Supported (needs opt-in)
- Vendor identifiers are auto-mapped (e.g. `20.0.2-tem` becomes `temurin-20.0.2`)

**Gotcha:** Gradle cannot auto-detect mise JDK installations for toolchains. Workarounds:
1. Create an asdf-compatible symlink: `mkdir -p ~/.asdf/installs/ && ln -s ~/.local/share/mise/installs/java ~/.asdf/installs/`
2. Use the `foojay-resolver-convention` Gradle plugin for automatic JDK download

---

## Go

### Version pinning

```toml
[tools]
golang = '1'     # latest 1.x
```

### GOROOT / GOPATH / GOBIN

- `go.set_goroot = true` (default) — sets `GOROOT` to the mise install path
- `go.set_gopath` — deprecated, don't use
- `go.set_gobin` — controls where `go install` puts binaries:
  - unset (default) — uses mise install path
  - `false` — leaves GOBIN unset (uses `${GOPATH:-$HOME/go}/bin`)
  - `true` — overrides any previously set GOBIN

### Default packages

Create `~/.default-go-packages`:

```
github.com/jesseduffield/lazygit
golang.org/x/tools/gopls
```

- Installed after each new Go version install

---

## Rust

### Channel-based versions

```toml
[tools]
rust = 'stable'    # latest stable
# rust = 'beta'
# rust = 'nightly'
# rust = '1.82'    # specific version
```

- Mise uses rustup under the hood — sets `RUSTUP_TOOLCHAIN` to trigger auto-install
- Installs rustup automatically if not present

### Tool options

```toml
[tools]
rust = { version = "stable", profile = "minimal", components = "rust-src,llvm-tools" }
```

- `profile` — `minimal`, `default`, or `complete`
- `components` — additional components (e.g. `rust-src`, `clippy`, `llvm-tools`)
- `targets` — cross-compilation targets (e.g. `wasm32-unknown-unknown`)

### Cargo backend (for installing CLI tools)

Install any crate as a mise-managed tool:

```toml
[tools]
"cargo:eza" = "latest"
"cargo:git-delta" = "latest"
"cargo:cargo-edit" = { version = "latest", features = "add" }
```

```bash
mise use -g cargo:eza        # add from command line
```

- Uses `cargo binstall` by default when available (pre-built binary download, much faster)
- Falls back to `cargo install` (compiles from source)
- Git installs: `cargo:https://github.com/user/repo@tag:v1.0.0`
- Settings: `cargo.binstall = true` (default), `cargo.binstall_only = false`

**Gotcha:** The cargo backend requires Rust/Cargo to be installed (either via rustup or `mise use -g rust`).

---

## Erlang / Elixir

### Erlang

```toml
[tools]
erlang = '28'      # OTP major version
```

- Built via kerl under the hood
- `erlang.compile = false` — use precompiled binaries (default when available)
- `erlang.compile = true` — compile from source (slow, needs build deps)

### Elixir

```toml
[tools]
erlang = '28'
elixir = '1.19.5-otp-28'   # must match erlang OTP version
```

- Erlang must be installed before Elixir
- The `-otp-28` suffix pins the Elixir build to a specific OTP major version
- **The OTP suffix must match your installed Erlang version** — mismatched versions will fail at runtime

**Gotcha:** When upgrading Erlang (e.g. OTP 27 to 28), you must also update the Elixir version string to match the new OTP version.

---

## Related

- [Tool Management](tool-management.md) — version specifiers and install commands
- [Settings](settings.md) — `python.compile`, `ruby.compile`, and other language settings
- [Backends](backends.md) — cargo, go, npm backends for language tooling
- [Environment](environment.md) — `_.python.venv` and language-specific env setup
