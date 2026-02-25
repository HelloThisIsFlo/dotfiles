# Chezmoi Secrets Management — Cheat Sheet

Dotfiles often contain secrets — API tokens, SSH keys, service credentials, database URLs. The problem: you want your dotfiles in a git repo (ideally public), but you can't commit secrets. Chezmoi solves this by pulling secrets from external sources at `chezmoi apply` time, so your repo only ever contains *references* to secrets, never the actual values.

There are two complementary approaches:

- **`rbw`** (Rust Bitwarden CLI) — field-level secrets in templates, pulled from your existing Bitwarden vault
- **`age` encryption** — whole-file encryption built into chezmoi, for files that should be encrypted at rest

This cheat sheet covers both. `rbw` is the primary day-to-day tool; `age` is an escape hatch for specific scenarios.

---

## rbw — field-level secrets from Bitwarden

### What is rbw?

`rbw` is an unofficial Bitwarden CLI written in Rust. Unlike the official `bw` CLI (which requires managing session tokens and is famously painful), `rbw` runs a background agent that holds your vault unlocked — similar to `ssh-agent`. You type your master password once, then work freely for hours.

The chezmoi maintainer explicitly recommends `rbw` over the official `bw` CLI.

### Installation

**macOS:**
```bash
brew install rbw
```

**Linux (Debian/Ubuntu):**
```bash
# Check https://github.com/doy/rbw for latest install options
cargo install rbw  # or use your distro's package manager
```

### Initial setup

```bash
# Set your Bitwarden email
rbw config set email flo@kempenich.ai

# Set lock timeout to 12 hours (43200 seconds)
# This means you type your master password once per morning
rbw config set lock_timeout 43200

# Register this device with Bitwarden
# You'll need your API key from Bitwarden web vault:
# Settings → Security → Keys → API Key
rbw register

# Unlock the vault (enter master password)
rbw unlock

# Verify it works
rbw list
rbw get some-item-name
```

### Pinentry configuration

`rbw` uses `pinentry` to prompt for your master password — the same system GPG uses. Which pinentry you use depends on the machine:

**macOS (GUI dialog):**
```bash
brew install pinentry-mac
rbw config set pinentry pinentry-mac
```

This gives you a native macOS dialog box. It appears over whatever you're doing, so you never have to switch to a terminal to unlock.

**Headless Linux servers (terminal prompt):**
```bash
rbw config set pinentry pinentry-tty
```

Also add this to your shell config (`.zshrc`, `.bashrc`):
```bash
export GPG_TTY=$(tty)
```

Without `GPG_TTY`, `pinentry-tty` won't know which terminal to prompt on and you'll get cryptic `ioctl` errors.

### How the auth model works

Understanding this helps when things go wrong:

- **API key** — stored in `rbw`'s config on disk. This identifies your device to Bitwarden's servers. You set it up once with `rbw register`.
- **Master password** — held in memory by the `rbw-agent` daemon. Never written to disk. This is what you enter via pinentry.
- **Lock timeout** — how long the agent holds your master password in memory. After this, the next `rbw` call triggers a pinentry prompt. With 43200 seconds (12 hours), you unlock once per morning.
- **Screen lock doesn't kill the agent.** Only a reboot (or explicit `rbw lock`) clears it. So locking your Mac mid-day doesn't mean re-entering your password.
- **`rbw-agent` starts automatically** when you run any `rbw` command. You don't need to manage it.

### Using rbw in chezmoi templates

Any file with a `.tmpl` suffix can reference secrets. The secret is fetched at `chezmoi apply` time and rendered into the target file.

**Basic password retrieval:**
```
{{ (rbw "github-api-token").data.password }}
```

This fetches the item named "github-api-token" from your Bitwarden vault and returns its password field.

**Custom fields:**
```
{{ (rbwFields "cloudflare").api_key.value }}
```

This fetches the custom field called "api_key" from the Bitwarden item "cloudflare". Use this when you store multiple values on a single vault item (e.g., both an API key and an account ID).

**Username:**
```
{{ (rbw "some-service").data.user }}
```

### Practical template examples

**Shell config with API tokens** (e.g., `dot_zshrc.tmpl`):
```
# Non-secret config — always present
export EDITOR="nvim"
export PATH="$HOME/.local/bin:$PATH"

{{- if eq .machine_type "personal" }}

# Personal machine secrets
export ANTHROPIC_API_KEY={{ (rbw "anthropic-api-key").data.password }}
export GITHUB_TOKEN={{ (rbw "github-pat").data.password }}
{{- end }}

{{- if eq .machine_type "work" }}

# Work machine secrets
export ARTIFACTORY_TOKEN={{ (rbw "troweprice-artifactory").data.password }}
{{- end }}
```

**Git config with conditional email** (e.g., `dot_gitconfig.tmpl`):
```
[user]
    name = Flo Kempenich
{{- if eq .machine_type "work" }}
    email = flo@troweprice.com
    signingkey = {{ (rbw "work-gpg-key-id").data.password }}
{{- else }}
    email = flo@kempenich.ai
    signingkey = {{ (rbw "personal-gpg-key-id").data.password }}
{{- end }}
```

**App config with multiple fields** (e.g., `private_dot_config/some-app/config.tmpl`):
```
[database]
host = {{ (rbwFields "prod-db").hostname.value }}
port = {{ (rbwFields "prod-db").port.value }}
user = {{ (rbw "prod-db").data.user }}
password = {{ (rbw "prod-db").data.password }}
```

### Conditional guards — why they matter

Every `{{ rbw ... }}` call requires the vault to be unlocked. If the vault is locked, `chezmoi apply` fails on that template.

More importantly: **don't call rbw for secrets a machine doesn't need.** If your work machine doesn't need your personal API tokens, wrap them in a conditional:

```
{{- if eq .machine_type "personal" }}
export ANTHROPIC_API_KEY={{ (rbw "anthropic-api-key").data.password }}
{{- end }}
```

Without the guard, `chezmoi apply` on your work machine would try to fetch a secret it doesn't need — and fail if the item doesn't exist in your vault, or succeed but expose a secret where it shouldn't be.

### Organising secrets in Bitwarden

Create a dedicated folder (e.g., "chezmoi" or "dotfiles") in your Bitwarden vault for secrets referenced by templates. Use consistent, descriptive names:

```
chezmoi/
  anthropic-api-key
  github-pat
  cloudflare            (with custom fields: api_key, account_id)
  prod-db               (with custom fields: hostname, port)
  troweprice-artifactory
  personal-gpg-key-id
  work-gpg-key-id
```

By default, `rbw` matches items by name across your entire vault. If your names are unique, the folder is just for your own sanity when browsing the Bitwarden UI.

If you do have naming conflicts (e.g., two items both called "api-key" in different folders), you can filter by folder in templates:

```
{{ (rbw "api-key" "--folder" "chezmoi").data.password }}
{{ (rbwFields "api-key" "--folder" "chezmoi").field_name.value }}
```

Extra arguments after the item name are passed straight through to `rbw get --raw`, so any `rbw` CLI flag works here.

### rbw limitations to know about

- **No attachment support.** Unlike the official `bw` CLI, `rbw` can't retrieve Bitwarden attachments. If you store SSH keys or certificates as attachments, use `age` encryption for those files instead.
- **2FA support is limited.** `rbw` supports TOTP and email 2FA but **not WebAuthn/passkeys or Duo**. If your Bitwarden account uses only an unsupported 2FA method, add a TOTP authenticator as a secondary option.
- **Every template evaluation triggers rbw calls.** Running `chezmoi diff` or `chezmoi status` on templates with `rbw` references requires the vault to be unlocked. This is fine with a 12-hour lock timeout, but good to know.
- **Requires internet** for initial unlock (it talks to Bitwarden servers). Once unlocked, cached data works offline for the duration of the session.

### Troubleshooting rbw

| Symptom | Fix |
|---|---|
| `rbw` hangs or shows no prompt | Check pinentry config: `rbw config show`. On Mac, ensure `pinentry-mac` is installed. On servers, ensure `GPG_TTY` is set. |
| "not logged in" error | Run `rbw register` again. Your API key may need refreshing. |
| "vault locked" during `chezmoi apply` | Run `rbw unlock`. Consider increasing lock timeout. |
| Wrong secret returned | Check Bitwarden for duplicate item names. `rbw` matches by name — duplicates cause ambiguity. Use `rbw get --folder chezmoi item-name` if needed. |
| Agent died after reboot | Normal — `rbw-agent` doesn't persist across reboots. First `rbw` command after boot restarts it and prompts for master password. |

### Utility wrapper: `cmbitwarden`

A small convenience wrapper so you don't have to remember the folder name every time. Add this to your `.zshrc` (or keep it as a standalone script):

```bash
CHEZMOI_BW_FOLDER="chezmoi"

cmbitwarden() {
  case "$1" in
    new)
      rbw add --folder "$CHEZMOI_BW_FOLDER" "${@:2}"
      ;;
    edit)
      rbw edit --folder "$CHEZMOI_BW_FOLDER" "${@:2}"
      ;;
    show)
      rbw get --folder "$CHEZMOI_BW_FOLDER" "${@:2}"
      ;;
    list)
      rbw list --fields name,user,folder | grep "$CHEZMOI_BW_FOLDER"
      ;;
    *)
      echo "Usage: cmbitwarden {new|edit|show|list} [name]"
      ;;
  esac
}
```

```bash
cmbitwarden new anthropic-api-key    # create, prompts for password
cmbitwarden show anthropic-api-key   # print password to stdout
cmbitwarden edit anthropic-api-key   # opens editor to modify
cmbitwarden list                     # all secrets in the chezmoi folder
```

---

## age — whole-file encryption

### When to use age

`age` is built directly into the chezmoi binary — no external tool needed. It encrypts entire files, which are stored as `.age` blobs in your repo. Use it for:

- **SSH private keys** — the classic use case. The encrypted file sits in your repo; chezmoi decrypts it on `apply`.
- **Certificates and private key files** — anything that's a complete file, not a value to interpolate into a config.
- **Headless servers with no internet** — age decryption is fully offline. No daemon, no agent, no authentication service. Just the key file and the encrypted data.
- **Unattended automation** — cron jobs, Ansible, cloud-init. The age key sits on disk, so `chezmoi apply` needs no interaction.
- **CI/CD pipelines** — pre-place the key or set it as an env var.

The rule of thumb: **rbw for values you embed in config files, age for whole files you need encrypted at rest.**

### Setup

**Generate an age keypair:**
```bash
chezmoi age-keygen --output ~/.config/chezmoi/key.txt
```

This creates a key file containing both your private key and your public key (starts with `age1...`). Note the public key — you'll need it for config.

**Add to chezmoi config** (`chezmoi.toml`):
```toml
encryption = "age"
[age]
  identity = "~/.config/chezmoi/key.txt"
  recipient = "age1your-public-key-here"
```

If you're using `.chezmoi.toml.tmpl` (which you should be), add it there instead:
```
encryption = "age"
[age]
  identity = "~/.config/chezmoi/key.txt"
  recipient = "age1your-public-key-here"
```

### Adding encrypted files

```bash
chezmoi add --encrypt ~/.ssh/id_ed25519
```

This encrypts the file and stores it in the source directory as `encrypted_private_dot_ssh/private_id_ed25519.age`. Your repo contains only the encrypted blob — safe to push publicly.

On `chezmoi apply`, the file is decrypted using your age key and written to the target path with the correct permissions.

### Using age-encrypted content in templates

You can also decrypt age-encrypted files *inside* templates using the `decrypt` function:

```
{{ include "encrypted_secret_file.age" | decrypt }}
```

This lets you include the decrypted content of an encrypted file within a larger template. For example, if you have a config file that's mostly non-secret but includes one block of sensitive data, you could keep the sensitive part in a separate encrypted file and include it.

### Key management — the bootstrap problem

The chicken-and-egg: you need the age key to decrypt your dotfiles, but how do you get the key onto a new machine?

**Option 1: Passphrase-encrypted key in repo**
```bash
# Encrypt your key with a passphrase
age -p -o key.txt.age ~/.config/chezmoi/key.txt
```

Store `key.txt.age` in your source directory. Create a run script that decrypts it during `chezmoi init`. You enter the passphrase once per new machine.

**Option 2: Store the key in Bitwarden**
Keep a copy of your age private key as a secure note in Bitwarden. On a new machine, retrieve it with `rbw` before running `chezmoi apply`. This creates a deliberate circular dependency — your Bitwarden vault can recover your age key, and age is your independent backup channel.

**Option 3: Just SCP it**
For a small number of machines, `scp` the key file from an existing machine. Simple and pragmatic.

**Critical: back up your age key.** If you lose it without a backup, all encrypted files are **permanently unrecoverable**. Store it in at least two places (e.g., Bitwarden secure note + a physical backup).

### age quick reference

| Task | Command |
|---|---|
| Generate keypair | `chezmoi age-keygen --output ~/.config/chezmoi/key.txt` |
| Add encrypted file | `chezmoi add --encrypt ~/.ssh/id_ed25519` |
| View encrypted file (rendered) | `chezmoi cat ~/.ssh/id_ed25519` |
| Decrypt content in template | `{{ include "file.age" \| decrypt }}` |
| Re-encrypt after editing | `chezmoi edit ~/.ssh/id_ed25519` (handles re-encryption automatically) |

---

## How rbw and age work together

Here's how they complement each other in a typical setup:

| Secret type | Approach | Example |
|---|---|---|
| API tokens, passwords | `rbw` in templates | `{{ (rbw "github-pat").data.password }}` |
| Database URLs, endpoints | `rbw` custom fields | `{{ (rbwFields "prod-db").hostname.value }}` |
| SSH private keys | `age` encryption | `chezmoi add --encrypt ~/.ssh/id_ed25519` |
| SSL certificates | `age` encryption | `chezmoi add --encrypt ~/.config/certs/client.pem` |
| Entire credential files | `age` encryption | `chezmoi add --encrypt ~/.config/app/credentials.json` |
| Config files mixing secrets and non-secrets | `rbw` in templates | Template with `{{ (rbw ...) }}` inline |

### Machine-type considerations

| Machine type | rbw | age |
|---|---|---|
| Personal Mac | ✅ `pinentry-mac`, 12-hour timeout | ✅ Key on disk |
| Work Mac | ✅ Same setup, different vault items via conditionals | ✅ Same key or separate key |
| Headless server | ✅ `pinentry-tty`, works fine over SSH | ✅ Key on disk, fully offline |
| CI/automation | ❌ Requires interactive unlock | ✅ Pre-place key, fully non-interactive |
| Air-gapped server | ❌ Needs internet for unlock | ✅ Fully offline |

This is why `age` is an important escape hatch even if `rbw` handles most of your day-to-day secrets.

---

## Quick reference

### rbw commands
```bash
rbw unlock              # Enter master password, unlock vault
rbw lock                # Lock vault immediately
rbw list                # List all items
rbw get item-name       # Get password for an item
rbw get --field api_key item-name  # Get a custom field
rbw config show         # Show current config
rbw config set lock_timeout 43200  # Set 12-hour timeout
```

### rbw in chezmoi templates
```
{{ (rbw "item").data.password }}           # Password field
{{ (rbw "item").data.user }}               # Username field
{{ (rbwFields "item").field_name.value }}   # Custom field
```

### age in chezmoi
```bash
chezmoi age-keygen --output key.txt   # Generate keypair
chezmoi add --encrypt <file>          # Add as encrypted
chezmoi edit <encrypted-target>       # Edit (auto re-encrypts)
chezmoi cat <encrypted-target>        # View decrypted output
```

### Decision guide
```
Is it a whole file (SSH key, cert, credentials file)?
  → age encryption: chezmoi add --encrypt

Is it a value embedded in a config file (token, password, URL)?
  → rbw in a template: {{ (rbw "item").data.password }}

Does it need to work without internet or interactively?
  → age encryption (key on disk, fully offline)

Is it needed on all machines?
  → No conditional guard needed

Is it specific to personal/work/server?
  → Wrap in {{ if eq .machine_type "..." }} guard
```
