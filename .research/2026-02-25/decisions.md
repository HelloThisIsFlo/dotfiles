# Chezmoi Architecture Decisions

This file documents key architectural decisions for this dotfiles setup. Future-me: read this before making changes.

---

## 1. Secrets management: rbw-only (decided 2026-02-24)

### Decision

Use `rbw` (Rust Bitwarden CLI with persistent agent) for **all** secrets — both on Mac and headless servers. No age encryption, no GPG, no official Bitwarden CLI.

### Context

- Bitwarden is the primary password manager (paid pro, ~$20/yr). Mari uses the free plan with shared vault via Free Organization.
- Need secrets in templates across Mac + headless Linux servers + other desktops/laptops.
- The official Bitwarden CLI (`bw`) has terrible UX — session tokens expire constantly, the chezmoi maintainer calls it "insecure by default."
- 1Password has the best chezmoi integration but costs $60/yr for family plan (3x current cost) and requires migrating Mari.
- `pass`/GPG has too much maintenance overhead (the "GPG tax").

### How it works

- `rbw` runs a background agent that holds the decrypted vault in memory.
- Lock timeout set to 12 hours → type master password once per morning.
- Screen lock does not kill the agent (only reboots do).
- Master password is never stored on disk — only the Bitwarden API key (for device auth).
- On Mac: `pinentry-mac` (GUI dialog). On servers: `pinentry-tty` (terminal prompt).
- Template syntax: `{{ (rbw "item-name").data.password }}` or `{{ (rbwFields "item-name").field_name.value }}`.

### Escape hatch: age encryption

If I ever need:
- Unattended `chezmoi apply` (cron, Ansible, cloud-init)
- Air-gapped servers with no internet
- CI/CD pipelines applying dotfiles

→ Migrate those specific files to `age` encryption (`chezmoi add --encrypt <file>`). This is additive, not a rewrite. age is built into the chezmoi binary, needs only a key file on disk, and works fully offline and non-interactively.

### What NOT to do

- Do not go back to the official `bw` CLI.
- Do not install `pass` or set up GPG for secrets.
- Do not use `chezmoi re-add` on template files (it destroys the template).

---

## 2. Workflow: edit → apply, not re-add (decided 2026-02-24)

### Decision

Use `chezmoi edit <target-path>` → `chezmoi apply` as the primary workflow. Stop using `chezmoi re-add` as the default.

### Why

- `re-add` overwrites template source files with rendered output, destroying template logic.
- `edit` resolves the `dot_` naming convention automatically — no need to navigate the source directory manually.
- With `edit` → `apply`, the source repo is always ahead, and git diffs work naturally.

### When re-add is still okay

- For plain (non-template) files that were edited in place by accident.
- Never for `.tmpl` files.

---

## 3. Future: Touch ID for rbw via custom Swift pinentry (backlog)

### Plan

Build a lightweight Swift pinentry program that:
- Stores the Bitwarden master password in macOS Keychain
- Gates access via Touch ID (LocalAuthentication framework)
- Speaks the Assuan protocol directly (no Go wrapper, no pinentry-mac dependency)

### Why not use existing pinentry-touchid?

- Pre-1.0, many open bugs from 2022-2024, unresponsive maintainer.
- Architecture problem: Go wrapper around pinentry-mac with shared Keychain entries → fragile.
- A native Swift implementation avoids the entire category of issues.

### Timeline

6-12 months out. Estimated 3-5 days of focused work. Not a priority — the current "type password once per morning" workflow is liveable.

---

## 4. No age encryption for v1 (decided 2026-02-24)

### Decision

Defer age encryption. The deep research report recommended age + rbw hybrid, but after discussion the added complexity isn't justified by current usage patterns.

### Revisit when

- A server needs unattended `chezmoi apply`
- A server has restricted/no internet access
- CI/CD needs to apply dotfiles
- The rbw-on-servers workflow becomes annoying in practice

### How to add age later

1. `chezmoi age-keygen --output ~/.config/chezmoi/key.txt`
2. Add `encryption = "age"` and `[age]` block to `chezmoi.toml`
3. `chezmoi add --encrypt <file>` for files that need offline/unattended access
4. Distribute the age key to servers (encrypt it with a passphrase for bootstrapping)
