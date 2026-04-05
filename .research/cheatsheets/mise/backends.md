# Mise Backends -- Cheat Sheet

Backends are how mise actually installs tools. Each backend is a different package ecosystem (aqua, cargo, npm, etc.) with different trade-offs around speed, platform support, and what's available. When you `mise use delta`, the registry decides which backend handles it.

---

## The Registry -- How `mise use delta` knows what to do

**The problem:** There are 18+ backends. You don't want to type `aqua:dandavison/delta` every time.

The registry is a built-in mapping from short names to fully qualified backend references. When you run `mise use delta`, mise looks up `delta` in the registry and resolves it to a specific backend (in this case, `aqua:dandavison/delta`).

```bash
# Check what backend a tool resolves to
$ mise registry | grep delta
delta                          aqua:dandavison/delta

$ mise registry | grep eza
eza                            aqua:eza-community/eza

$ mise registry | grep black
black                          pipx:black
```

**Key point:** The registry determines the *default* backend. You can always override it with a fully qualified name.

---

## Fully Qualified Names -- Forcing a specific backend

**The problem:** The registry default isn't always what you want. Maybe you want to compile delta from source with custom features, or the registry picks a backend you don't prefer.

Syntax: `backend:identifier`

```toml
# In mise.toml or ~/.config/mise/config.toml
[tools]
"aqua:dandavison/delta" = "latest"       # aqua — download pre-built binary
"cargo:git-delta" = "latest"             # cargo — compile from source (crate name differs!)
"npm:prettier" = "latest"                # npm — install from npmjs.org
"npm:@scope/pkg" = "latest"              # npm — scoped packages work too
"pipx:black" = "latest"                  # pipx — Python tool in isolated venv
"go:github.com/golangci/golangci-lint/cmd/golangci-lint" = "latest"  # go — full module path
"github:cli/cli" = "latest"              # github — download from GitHub Releases
```

Each backend has its own identifier format:
- **aqua** — `aqua:owner/repo` (matches aqua registry naming)
- **cargo** — `cargo:crate-name` (crate name, not repo name)
- **npm** — `npm:package-name` or `npm:@scope/package`
- **pipx** — `pipx:package` or `pipx:owner/repo`
- **go** — `go:full/module/path`
- **github** — `github:owner/repo`
- **asdf** — `asdf:plugin-name`
- **spm** — `spm:owner/repo`

---

## Backend Priority -- Which one wins

**The problem:** Multiple backends can install the same tool. Which one does the registry prefer?

The registry defines a single preferred backend per tool. The general priority pattern:

1. **core** — language runtimes (node, python, ruby, go, java, etc.)
2. **aqua** — preferred for most CLI tools (pre-built binaries)
3. **github** — fallback for tools not in aqua registry
4. **pipx/npm/cargo/go** — language-specific tools that only exist in those ecosystems

In practice, for CLI tools like `delta`, `eza`, `cheat`, `ripgrep`, `fd`, `bat` -- aqua is the default. For language runtimes like `node`, `python`, `ruby` -- core handles them natively.

You can override defaults:
- **Per-tool:** use fully qualified names in config
- **Environment variable:** `MISE_BACKENDS_<TOOL>=backend:identifier` (SHOUTY_SNAKE_CASE)
- **Disable a backend entirely:** `mise settings disable_backends=asdf`

---

## All Backends

### core -- Language runtimes

Mise's built-in runtime manager. Handles major languages natively without any external backend.

- **Covers:** node, python, ruby, go, java, erlang, elixir, rust, bun, deno, and more
- **How it works:** Downloads pre-built binaries from official sources (node-build, python-build, etc.)
- **When to use:** Automatically used for language runtimes. You don't choose this -- it's the default for supported languages.

**Verdict:** You're already using it. `node = "22"` and `ruby = "3.3"` go through core.

### aqua -- Pre-built binaries from GitHub Releases

The registry that mise compiles directly into its binary. Downloads pre-built platform-specific binaries from GitHub releases.

- **How it works:** Aqua registry YAML files are baked into the mise binary at release. No aqua CLI needed. Mise reads the registry to find the right binary for your OS/arch and downloads it.
- **Syntax:** `aqua:owner/repo` (e.g., `aqua:dandavison/delta`, `aqua:XAMPPRocky/tokei`)
- **Security:** Native verification -- checksums, cosign signatures, SLSA provenance, GitHub Artifact Attestations. All built into mise, no external tools.
- **Limitation:** Only handles binary downloads. Can't set environment variables or run post-install scripts.

```toml
[tools]
"aqua:dandavison/delta" = "latest"
"aqua:BurntSushi/ripgrep" = "latest"
```

**Settings:**

| Setting | Default | Purpose |
|---------|---------|---------|
| `aqua.baked_registry` | `true` | Use registry compiled into mise binary |
| `aqua.cosign` | `true` | Verify cosign signatures |
| `aqua.github_attestations` | `true` | Verify GitHub Artifact Attestations |
| `aqua.slsa` | `true` | Verify SLSA provenance |

**Verdict:** Your go-to for CLI tools. Fast (download, not compile), secure (multiple verification methods), huge catalog. Already your preferred backend.

### github -- GitHub Releases (no aqua registry needed)

Downloads release assets directly from GitHub repositories. Intelligently scores assets to pick the right one for your platform.

- **How it works:** Hits GitHub Releases API, scores assets by OS/arch/format match, downloads the best one.
- **Syntax:** `github:owner/repo`
- **vs aqua:** github backend does its own asset detection heuristics. Aqua uses curated registry data (more reliable). Use github for tools not in the aqua registry.
- **Replaces:** the deprecated `ubi` backend (same idea, newer implementation).

```toml
[tools]
"github:cli/cli" = "latest"
```

**Verdict:** Fallback for tools not in aqua. Also useful for private repos or GitHub Enterprise (supports custom `api_url`).

### cargo -- Rust ecosystem

Installs from crates.io. Compiles from source by default, but uses `cargo-binstall` when available for pre-built binaries.

- **Syntax:** `cargo:crate-name` (the crate name, which may differ from the repo name -- `git-delta` not `delta`)
- **Performance:** With `cargo-binstall`: fast (downloads pre-built). Without: slow (compiles from source, can take minutes).
- **Requires:** `cargo` on PATH (install via mise or rustup).

```toml
[tools]
"cargo:eza" = "latest"
# With options:
"cargo:some-tool" = { version = "latest", features = "postgres,s3", locked = true }
```

| Setting | Default | Purpose |
|---------|---------|---------|
| `cargo.binstall` | `true` | Use cargo-binstall for pre-built binaries |

**Verdict:** Only when aqua doesn't have the tool AND you need crate-specific features/flags. For most Rust CLI tools, aqua is faster and simpler.

### go -- Go ecosystem

Installs via `go install`. Always compiles from source.

- **Syntax:** `go:full/module/path` (e.g., `go:github.com/golangci/golangci-lint/cmd/golangci-lint`)
- **Performance:** Compiles from source every time. Slower than aqua.
- **Requires:** `go` on PATH.

```toml
[tools]
"go:github.com/golang-migrate/migrate/v4/cmd/migrate" = { version = "latest", tags = "postgres" }
```

**Verdict:** Only when aqua doesn't have the tool, or you need build tags. Most Go CLI tools are in aqua.

### npm -- Node.js packages

Installs from npmjs.org.

- **Syntax:** `npm:package` or `npm:@scope/package`
- **Requires:** npm, bun, or pnpm on PATH.

```toml
[tools]
"npm:prettier" = "latest"
"npm:@biomejs/biome" = "latest"
```

| Setting | Default | Purpose |
|---------|---------|---------|
| `npm.package_manager` | `npm` | Which package manager to use (npm/bun/pnpm) |

**Verdict:** For Node.js tools that are npm-only. Many popular ones (prettier, eslint) are also in aqua -- check `mise registry | grep <tool>` first.

### pipx -- Python tools in isolated venvs

Uses `uvx` (preferred) or `pipx` to install Python CLI tools with isolated dependencies.

- **Syntax:** `pipx:package` or `pipx:owner/repo` (GitHub) or `pipx:git+https://...`
- **Requires:** `uv` or `pipx` on PATH.

```toml
[tools]
"pipx:black" = "latest"
"pipx:psf/black" = "latest"     # from GitHub
# With extras:
"pipx:some-tool" = { version = "latest", extras = "postgres,s3" }
```

| Setting | Default | Purpose |
|---------|---------|---------|
| `pipx.uvx` | `true` | Use uvx when uv is installed |

**Verdict:** For Python-only CLI tools (black, ruff, mypy, etc.). Some are also in aqua.

### asdf -- Plugin ecosystem

The original plugin system. Thousands of community plugins.

- **Syntax:** `asdf:plugin-name`
- **Note:** Disabled by default on Windows. Being gradually replaced by aqua for most tools.

**Verdict:** Legacy fallback. Use aqua/core first. Only needed for obscure tools with an asdf plugin but no aqua entry.

### vfox -- Cross-platform plugin system

Similar to asdf but designed for Windows compatibility.

- **Syntax:** `vfox:plugin-name`

**Verdict:** Mainly relevant if you need Windows support for a tool that only has a vfox plugin.

### spm -- Swift Package Manager (experimental)

Installs Swift executables from GitHub/GitLab.

- **Syntax:** `spm:owner/repo`
- **Requires:** `swift` on PATH.

**Verdict:** Niche. Only for Swift CLI tools distributed as Swift packages.

### ubi -- Universal Binary Installer (deprecated)

Downloads from GitHub/GitLab releases. **Deprecated in favor of the github backend.**

- **Syntax:** `ubi:owner/repo`
- **Migration:** Replace `ubi:` with `github:` in your config.

**Verdict:** Don't use. Migrate existing entries to `github:owner/repo`.

### Other backends

- **forgejo** -- like github but for Forgejo/Gitea instances
- **gitlab** -- like github but for GitLab
- **conda** (experimental) -- Conda packages
- **dotnet** (experimental) -- .NET tools
- **gem** -- Ruby gems
- **http** -- download from arbitrary URLs
- **s3** (experimental) -- download from S3 buckets

---

## Decision Guide

| Situation | Backend | Why |
|-----------|---------|-----|
| Language runtime (node, python, ruby, etc.) | core | Built-in, optimized, automatic |
| CLI tool (delta, eza, ripgrep, fd, bat, cheat) | aqua | Pre-built binary, fast, secure, huge catalog |
| CLI tool not in aqua | github | Same idea (GitHub releases), auto-detects assets |
| Python CLI tool (black, ruff, mypy) | pipx | Isolated venv, manages Python deps |
| Node.js CLI tool (prettier, eslint) | npm | Native npm install; check aqua first |
| Rust tool needing custom features | cargo | Build flags only available via cargo |
| Go tool needing build tags | go | Build tags only available via `go install` |
| Legacy/obscure tool | asdf | Huge plugin ecosystem, but check aqua first |
| Swift tool | spm | Only option for Swift packages |

### Performance at a glance

| Backend | Install speed | Mechanism |
|---------|--------------|-----------|
| core | Fast | Downloads pre-built runtime |
| aqua | Fast | Downloads pre-built binary |
| github | Fast | Downloads pre-built binary |
| cargo (with binstall) | Fast | Downloads pre-built binary |
| cargo (without binstall) | Slow (minutes) | Compiles from source |
| go | Slow | Compiles from source |
| npm | Medium | Downloads + installs deps |
| pipx | Medium | Creates venv + installs deps |

---

## Your Config Explained

```toml
# By default, for most tools, mise prioritizes aqua over cargo/go/npm/[...]. 
# This is great because aqua downloads are pre-built binaries from GitHub releases
# To find out which backend will be used by default: mise registry | grep <tool>
# To force a specific backend: 'cargo:git-delta', 'npm:@ls-lint/ls-lint', 'aqua:XAMPPRocky/tokei'
usage = 'latest'     # mise registry | grep usage -> aqua backend
delta = 'latest'     # mise registry | grep delta -> aqua:dandavison/delta
cheat = 'latest'     # mise registry | grep cheat -> aqua:cheat/cheat
```

All three resolve to aqua via the registry. No compilation, just binary downloads. Exactly right.

---

## Quick Reference Commands

```bash
mise registry                       # list all known tools + their backends
mise registry | grep <tool>         # check which backend a tool resolves to
mise use <tool>                     # install using registry default backend
mise use aqua:owner/repo            # force aqua backend
mise use cargo:crate-name           # force cargo backend
mise settings disable_backends=asdf # disable a backend globally
```

---

## Related

- [Tool Management](tool-management.md) — `mise use`, version specifiers, fully qualified names in config
- [Language Features](language-features.md) — language-specific backend behaviors
- [Security & Trust](security-trust.md) — lockfile checksums and supply chain verification
- [CI & Bootstrap](ci-bootstrap.md) — backend considerations for CI environments
