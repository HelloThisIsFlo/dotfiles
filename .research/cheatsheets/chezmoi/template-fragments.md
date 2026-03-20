# Chezmoi Template Fragments — Cheat Sheet

You have one config file that needs to live at different paths depending on the OS — `~/Library/Application Support/Code/User/settings.json` on macOS, `~/.config/Code/User/settings.json` on Linux. You don't want to maintain two identical copies and manually keep them in sync. Template fragments solve this: define the content once, deploy it to multiple paths.

---

## What `.chezmoitemplates/` is

A special directory in your chezmoi source state. Files in it are **never deployed anywhere** — they exist purely as reusable building blocks that other `.tmpl` files can pull in.

```
~/.local/share/chezmoi/
├── .chezmoitemplates/
│   └── vscode-settings.json       ← content defined ONCE here
├── dot_config/Code/User/
│   └── settings.json.tmpl         ← thin wrapper (Linux path)
└── private_Library/Application Support/Code/User/
    └── settings.json.tmpl         ← thin wrapper (macOS path)
```

Each wrapper is a one-liner:

```
{{ template "vscode-settings.json" . }}
```

The `.` at the end is critical — it passes your full template data context (`.os`, `.email`, `.trust_level`, etc.) into the fragment. Without it, the fragment renders with an empty context and all your variables are undefined.

---

## `{{ template }}` vs `{{ include }}`

These look similar but do different things.

| | `{{ template "name" . }}` | `{{ include "path" }}` |
|---|---|---|
| **Source** | `.chezmoitemplates/` directory | Any file in source state |
| **Rendering** | Full template rendering with data context | Raw content, no rendering |
| **Use case** | Shared config with variables | Static content insertion, hash tricks |
| **Path argument** | Just the filename (no directory prefix) | Source-state path (e.g., `dot_Brewfile`) |

Use `{{ template }}` when the shared content needs template variables (conditionals, secrets, machine-specific values). Use `{{ include }}` when you want raw content — the classic example is `{{ include "dot_Brewfile" | sha256sum }}` for change detection in run scripts.

> **About `include` rendering:** `{{ include }}` does *not* evaluate template expressions inside the included file. If the file contains `{{ .email }}`, that literal string appears in the output. This is why `include` works for hash tricks — it hashes the source content, not the rendered output.

See the [Templates cheat sheet](templates.md) for full `{{ include }}` usage and the hash trick pattern.

---

## The cross-platform pattern

This is the primary use case. Walk-through with VS Code settings:

### Step 1: Create the shared fragment

```
# .chezmoitemplates/vscode-settings.json
{
    "editor.fontSize": 14,
    "editor.fontFamily": "JetBrains Mono",
{{- if eq .os "macos" }}
    "terminal.integrated.fontFamily": "MesloLGS NF",
{{- else }}
    "terminal.integrated.fontFamily": "MesloLGS Nerd Font",
{{- end }}
    "editor.formatOnSave": true
}
```

The fragment is a full template — conditionals, variables, everything works.

### Step 2: Create thin wrappers at each OS path

macOS wrapper at `private_Library/Application Support/Code/User/settings.json.tmpl`:

```
{{ template "vscode-settings.json" . }}
```

Linux wrapper at `dot_config/Code/User/settings.json.tmpl`:

```
{{ template "vscode-settings.json" . }}
```

Both files are identical — one line. The only difference is their location in the source state, which determines the target path.

### Step 3: Ignore the wrong path per OS

In `.chezmoiignore`:

```
{{ if ne .os "macos" }}
Library/Application Support/Code/User/settings.json
{{ end }}

{{ if ne .os "linux" }}
.config/Code/User/settings.json
{{ end }}
```

On macOS, only the `Library/` path gets applied. On Linux, only the `.config/` path. The other wrapper exists in source but chezmoi pretends it doesn't.

### Step 4: Verify

```bash
chezmoi cat ~/Library/Application\ Support/Code/User/settings.json  # macOS
chezmoi cat ~/.config/Code/User/settings.json                        # Linux
```

Both render the same content (with OS-appropriate conditionals applied). Edit the fragment once, both paths update on next `chezmoi apply`.

---

## Other uses

Template fragments aren't just for cross-platform paths. Any time you're repeating config content across multiple files, a fragment can DRY it up.

### Shared shell aliases

If you maintain both `.bashrc` and `.zshrc` with overlapping aliases and exports:

```
# .chezmoitemplates/shell-aliases
alias ll="ls -la"
alias g="git"
alias k="kubectl"

{{- if eq .os "macos" }}
alias flush-dns="sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder"
{{- end }}

export EDITOR="nvim"
export LANG="en_US.UTF-8"
```

Then in both `private_dot_zshrc.tmpl` and `dot_bashrc.tmpl`:

```
# ... shell-specific setup above ...

# Shared aliases and exports
{{ template "shell-aliases" . }}

# ... shell-specific stuff below ...
```

### Common SSH host config

If multiple SSH hosts share the same options:

```
# .chezmoitemplates/ssh-defaults
    ServerAliveInterval 60
    ServerAliveCountMax 3
    AddKeysToAgent yes
{{- if eq .os "macos" }}
    UseKeychain yes
{{- end }}
```

Then in `private_dot_ssh/private_config.tmpl`:

```
Host personal-server
    HostName 192.168.1.100
    User flo
{{ template "ssh-defaults" . }}

Host work-server
    HostName 10.0.0.50
    User fkempenich
{{ template "ssh-defaults" . }}
```

---

## Gotchas

> **Don't forget the dot.** `{{ template "name" . }}` passes data context. `{{ template "name" }}` passes nothing — every variable in the fragment becomes undefined. This is the most common mistake and produces confusing `<no value>` output.

> **Fragment names are just filenames.** No path prefix, no directory. A file at `.chezmoitemplates/ssh-defaults` is referenced as `{{ template "ssh-defaults" . }}`. If you nest into subdirectories (`.chezmoitemplates/ssh/defaults`), the name becomes `ssh/defaults`.

> **Fragments can nest.** A fragment can call `{{ template "other-fragment" . }}` — useful for composing complex configs from smaller pieces. Don't go overboard; one level of nesting is usually enough.

> **Fragments are templates, not files.** They're rendered by Go's template engine, so all template syntax works inside them — conditionals, loops, functions, even `{{ include }}`. But they only exist inside the template engine; `chezmoi cat` won't show a fragment directly, only the final rendered output of files that use it.

---

## Quick reference

| I want to... | Use |
|---|---|
| Share config content across multiple target files | `.chezmoitemplates/` + `{{ template "name" . }}` |
| Deploy one config to different paths per OS | Fragment + thin wrappers + `.chezmoiignore` |
| Insert raw file content without rendering | `{{ include "source-path" }}` ([Templates cheat sheet](templates.md)) |
| Check what a fragment renders to | `chezmoi cat <target-that-uses-it>` |
| Pass variables into a fragment | The `.` in `{{ template "name" . }}` — always include it |
| Organise many fragments | Subdirectories work: `.chezmoitemplates/ssh/defaults` → `{{ template "ssh/defaults" . }}` |
