# Chezmoi Templates — Cheat Sheet

Templates let chezmoi **generate** files dynamically instead of copying them verbatim. A single source file can produce different output on different machines — different OS, different role, different secrets. Any file in the source directory with a `.tmpl` suffix is rendered through Go's `text/template` engine before being written to the target.

---

## The basics

### Making a file a template

Add `.tmpl` to the filename in the source directory:

```
dot_gitconfig.tmpl        → renders to ~/.gitconfig
dot_zshrc.tmpl            → renders to ~/.zshrc
private_dot_ssh/config.tmpl → renders to ~/.ssh/config
```

Everything inside `{{ }}` is a template expression. Everything outside is literal text passed through unchanged.

### Where template data comes from

Templates pull values from built-in variables (like `.chezmoi.os`, `.chezmoi.hostname`) and your custom variables (like `.machine_type`, `.email`). For a full breakdown of all data sources, how they merge, and how to set up machine-specific configuration with interactive prompts, see the [Data Sources cheat sheet](data-sources.md).

---

## Conditionals

### Simple if

```
{{ if eq .chezmoi.os "darwin" }}
# macOS-only config here
export BROWSER="open"
{{ end }}
```

### If / else

```
{{ if eq .chezmoi.os "darwin" }}
export BROWSER="open"
{{ else }}
export BROWSER="xdg-open"
{{ end }}
```

### If / else if / else

```
{{ if eq .machine_type "personal" }}
export GIT_EMAIL="flo@kempenich.ai"
{{ else if eq .machine_type "work" }}
export GIT_EMAIL="flo@troweprice.com"
{{ else }}
export GIT_EMAIL="flo@kempenich.ai"
{{ end }}
```

### Boolean variables

```
{{ if .is_headless }}
# No GUI tools
{{ end }}

{{ if not .is_headless }}
# GUI tools here
{{ end }}
```

### Combining conditions

```
# AND — both must be true
{{ if and (eq .chezmoi.os "darwin") (not .is_headless) }}
# macOS desktop only
{{ end }}

# OR — either is true
{{ if or (eq .machine_type "personal") (eq .machine_type "work") }}
# any non-server machine
{{ end }}

# Nested logic
{{ if and (eq .chezmoi.os "linux") (or (eq .machine_type "server") (.is_headless)) }}
# Linux server or headless Linux
{{ end }}
```

---

## Whitespace control

This is the fiddly bit. By default, template tags produce blank lines in the output where the `{{ }}` blocks were. Use hyphens to trim whitespace:

```
# WITHOUT whitespace control — leaves blank lines
{{ if eq .chezmoi.os "darwin" }}
export PATH="/opt/homebrew/bin:$PATH"
{{ end }}
```

Output:
```

export PATH="/opt/homebrew/bin:$PATH"

```

```
# WITH whitespace control — clean output
{{- if eq .chezmoi.os "darwin" }}
export PATH="/opt/homebrew/bin:$PATH"
{{- end }}
```

Output:
```
export PATH="/opt/homebrew/bin:$PATH"
```

The rules:
- `{{-` trims all whitespace (including newlines) **before** the tag
- `-}}` trims all whitespace (including newlines) **after** the tag
- You can use both: `{{- something -}}`

> **Tip:** When you're getting unexpected blank lines in your rendered output, whitespace control is almost always the fix. Use `chezmoi cat <target>` to see the rendered output without applying it, and tweak the hyphens until it looks right.

---

## Secrets with rbw

This section covers the template syntax for pulling secrets. For full setup — installing rbw, vault organisation, age encryption, and best practices — see the [Secrets cheat sheet](secrets.md).

### Basic password retrieval

```
export API_KEY={{ (rbw "anthropic-api-key").data.password }}
```

### Custom fields

If you store extra fields on a Bitwarden item (e.g., a custom field called "api_key"):

```
export API_KEY={{ (rbwFields "my-service").api_key.value }}
```

### Conditional secrets (only on certain machines)

```
{{- if eq .machine_type "personal" }}
export PERSONAL_TOKEN={{ (rbw "github-personal-token").data.password }}
{{- end }}
```

This means `chezmoi apply` on a work machine won't even try to fetch the personal token from Bitwarden — the entire block is skipped before any rbw call happens.

### Username and password together

```
export DB_USER={{ (rbw "prod-database").data.username }}
export DB_PASS={{ (rbw "prod-database").data.password }}
```

> **Important:** Every `{{ rbw ... }}` call requires the rbw vault to be unlocked. If the vault is locked and chezmoi hits an rbw expression during rendering, it will fail. This is why conditional guards (`if .machine_type`) are valuable — they prevent rbw calls on machines that don't need those secrets.

---

## `.chezmoiignore` — skip entire files per machine

`.chezmoiignore` is a special template file in the source directory root. It lists files that chezmoi should **completely ignore** on this machine — not render, not apply, not even think about.

> **⚠️ The logic reads backwards at first glance.** This is an *ignore* file, so the conditional means "when this condition is true, **skip** these files." So `{{ if .is_headless }}` followed by GUI config paths means "if headless, **ignore** (skip) the GUI configs" — not "if headless, include them." It's the same logic as `.gitignore` listing files you *don't* want, but with template conditionals on top. Read each block as: "when [condition], **don't manage** these files."

> **Note:** Paths in `.chezmoiignore` are **target paths** (like `~/.ssh/...`), not source directory paths (not `dot_ssh/...`). And the file itself is a template, so the `{{ }}` conditionals work.

```
# .chezmoiignore

# Always ignore these
README.md
LICENSE

# When on a work machine, skip personal SSH keys
{{ if eq .machine_type "work" }}
.ssh/personal_id_ed25519
.ssh/personal_id_ed25519.pub
{{ end }}

# When on a personal machine, skip work configs
{{ if eq .machine_type "personal" }}
.config/work-vpn/**
{{ end }}

# When headless, skip GUI configs (we don't need them)
{{ if .is_headless }}
.config/alacritty/**
.config/rectangle/**
Library/**
{{ end }}

# When NOT on macOS, skip macOS-specific files
{{ if ne .chezmoi.os "darwin" }}
.Brewfile
Library/**
{{ end }}
```

This is the cleanest way to handle "I don't want my personal SSH key on my work machine" — the file simply doesn't exist in chezmoi's view on that machine.

---

## Machine-specific configuration

This is how you make one repo work across personal machines, work laptops, and headless servers. The full setup — including `.chezmoi.toml.tmpl`, interactive prompt functions (`promptChoiceOnce`, `promptBoolOnce`, `promptStringOnce`), `chezmoi init`, and data file organisation — is covered in the [Data Sources cheat sheet](data-sources.md).

The short version: you create a `.chezmoi.toml.tmpl` that asks questions on first run and generates your config. Every other template then uses those values:

```
{{ if eq .machine_type "work" -}}
# Work-specific config here
{{ end -}}
```

---

## Template functions you'll actually use

### String manipulation

```
{{ .chezmoi.hostname | lower }}              → "flos-macbook-pro"
{{ .chezmoi.hostname | upper }}              → "FLOS-MACBOOK-PRO"
{{ "hello world" | title }}                  → "Hello World"
{{ "  spaced  " | trim }}                    → "spaced"
{{ "hello" | contains "ell" }}               → true
{{ "hello" | hasPrefix "hel" }}              → true
{{ "hello" | replace "l" "r" }}              → "herro"
```

### Quoting (for TOML/YAML/JSON config files)

```
email = {{ .email | quote }}                 → email = "flo@kempenich.ai"
```

### Including other files

```
{{ include "dot_Brewfile" }}                  → inserts the raw content of dot_Brewfile
{{ include "dot_Brewfile" | sha256sum }}      → inserts the SHA256 hash (the hash trick)
```

### Checking if a command exists

```
{{ if lookPath "bat" }}
# bat is installed — use it as cat replacement
alias cat="bat --style=plain"
{{ end }}

{{ if lookPath "delta" }}
# delta is installed — use it as git pager
export GIT_PAGER="delta"
{{ end }}
```

> **`lookPath` is great for progressive enhancement.** Your templates gracefully adapt to what's installed on each machine. If you install a tool later, the next `chezmoi apply` re-renders the template and picks it up automatically. Combine with `machine_type` checks for maximum flexibility.

### Environment variables

```
{{ env "HOME" }}                             → /Users/flo
{{ env "SHELL" }}                            → /bin/zsh
```

### Comparison operators

```
{{ eq .machine_type "personal" }}            → true/false (equal)
{{ ne .chezmoi.os "windows" }}               → true/false (not equal)
{{ gt .chezmoi.arch "amd64" }}               → string comparison (greater than)
```

---

## Real-world example: `.gitconfig.tmpl`

Putting it all together — a single gitconfig that works everywhere:

```
[user]
    name = Flo Kempenich
{{- if eq .machine_type "work" }}
    email = flo@troweprice.com
{{- else }}
    email = flo@kempenich.ai
{{- end }}

[core]
    editor = nvim
{{- if eq .chezmoi.os "darwin" }}
    autocrlf = input
{{- end }}

{{- if lookPath "delta" }}
[pager]
    diff = delta
    log = delta
    reflog = delta
    show = delta
[delta]
    navigate = true
    side-by-side = true
{{- end }}

{{- if eq .machine_type "personal" }}
[url "git@github.com:"]
    insteadOf = https://github.com/
{{- end }}
```

One file. Works on personal Mac, work laptop, and headless server. Each gets the right email, the right tools config, and only the personal machine rewrites GitHub URLs to SSH.

---

## Real-world example: `.ssh/config.tmpl`

```
{{- if ne .machine_type "work" }}
# Personal servers — not on work machines
Host myserver
    HostName 192.168.1.100
    User flo
    IdentityFile ~/.ssh/personal_id_ed25519
{{- end }}

{{- if or (eq .machine_type "work") (eq .machine_type "personal") }}
# GitHub — on any non-server machine
Host github.com
    IdentityFile ~/.ssh/github_id_ed25519
    AddKeysToAgent yes
{{-   if eq .chezmoi.os "darwin" }}
    UseKeychain yes
{{-   end }}
{{- end }}
```

Combined with `.chezmoiignore` to skip the actual key files on wrong machines, this gives you a clean SSH setup per machine role.

---

## Debugging templates

### See rendered output without applying

```bash
chezmoi cat ~/.gitconfig          # shows what the rendered file looks like
chezmoi diff                       # shows what would change on apply
chezmoi data                       # shows all available template variables
chezmoi execute-template '{{ .chezmoi.os }}'  # test a template expression
```

### Common mistakes

1. **Forgetting `.tmpl` suffix** — `{{ }}` expressions appear as literal text in the output.
2. **Whitespace mess** — blank lines everywhere. Fix with `{{-` and `-}}`.
3. **Quoting strings in TOML** — `{{ .email }}` produces `flo@kempenich.ai` (no quotes). Use `{{ .email | quote }}` to get `"flo@kempenich.ai"`.
4. **rbw call on a machine that shouldn't have it** — wrap in `{{ if eq .machine_type "personal" }}` to skip on other machines.
5. **Testing with `chezmoi apply` directly** — always use `chezmoi cat` or `chezmoi diff` first to verify the rendered output looks right before applying.

---

## Quick decision guide

| I want to... | Use |
|---|---|
| Different values per OS | `{{ if eq .chezmoi.os "darwin" }}` |
| Different values per machine role | Custom `[data]` variable + `{{ if eq .machine_type "..." }}` |
| Skip entire files on certain machines | `.chezmoiignore` with conditionals |
| Inject a secret from Bitwarden | `{{ (rbw "item").data.password }}` |
| Only fetch a secret on machines that need it | Wrap `rbw` call in `{{ if }}` conditional |
| Conditional config based on installed tools | `{{ if lookPath "tool-name" }}` |
| Set up machine variables on first init | `.chezmoi.toml.tmpl` with `promptOnce` functions |
| Check rendered output before applying | `chezmoi cat <target>` or `chezmoi diff` |
