# Chezmoi Data Sources — Cheat Sheet

Every chezmoi template pulls its values from somewhere. This cheat sheet covers all the places data can come from, how they fit together, and how to set up your data so that one repo works across all your machines.

---

## The data model

Templates access variables using `{{ .something }}`. Those variables come from three sources, merged in this order (later wins):

1. **Built-in variables** — chezmoi provides these automatically based on the current machine
2. **Data files** — `.chezmoidata.*` files in your source directory
3. **Config file** — `chezmoi.toml` (specifically its `[data]` section)

If the same key exists in multiple sources, config file wins over data files, which win over built-ins.

You can see everything that's available on the current machine with:

```bash
chezmoi data
```

---

## Built-in variables

Chezmoi populates these automatically. No configuration needed.

| Variable | Example value | What it is |
|---|---|---|
| `.chezmoi.os` | `"darwin"`, `"linux"` | Operating system |
| `.chezmoi.arch` | `"amd64"`, `"arm64"` | CPU architecture |
| `.chezmoi.hostname` | `"Flos-MacBook-Pro"` | Machine hostname |
| `.chezmoi.homeDir` | `"/Users/flo"` | Home directory path |
| `.chezmoi.sourceDir` | `"/Users/flo/.local/share/chezmoi"` | Source directory path |
| `.chezmoi.username` | `"flo"` | Current username |
| `.chezmoi.fqdnHostname` | `"Flos-MacBook-Pro.local"` | Fully qualified hostname |
| `.chezmoi.osRelease.*` | *(Linux only)* | Distro info from `/etc/os-release` |

Use these for OS and architecture conditionals in templates:

```
{{ if eq .chezmoi.os "darwin" }}macOS stuff{{ end }}
{{ if eq .chezmoi.arch "arm64" }}Apple Silicon{{ end }}
```

---

## Config file: `chezmoi.toml`

Lives at `~/.config/chezmoi/chezmoi.toml`. This is chezmoi's own configuration — it controls both chezmoi's behaviour and your custom template data.

### Structure

```toml
# Chezmoi behaviour settings
encryption = "age"

[age]
  identity = "~/.config/chezmoi/key.txt"
  recipient = "age1..."

[git]
  autoCommit = true
  autoPush = false

# Your custom template variables
[data]
  machine_type = "personal"
  is_headless = false
  email = "flo@kempenich.ai"
```

Everything under `[data]` becomes a template variable. The rest configures chezmoi itself — for a full guide on those settings (encryption, git, diff, merge, etc.), see the [Configuration cheat sheet](chezmoi-config-cheatsheet.md).

### Generating it with `.chezmoi.toml.tmpl`

You should not maintain `chezmoi.toml` by hand on each machine. Instead, create `.chezmoi.toml.tmpl` in the root of your source directory. This is a template that chezmoi renders during `chezmoi init` to produce the config file.

Because it renders at init time (not during every apply), it has access to special interactive prompt functions:

| Function | What it does |
|---|---|
| `promptStringOnce . "key" "Question?"` | Asks for text, stores the answer |
| `promptBoolOnce . "key" "Question?"` | Asks yes/no, stores the answer |
| `promptChoiceOnce . "key" "Question?" (list "a" "b" "c")` | Asks to pick from a list, stores the answer |

The "Once" means chezmoi stores your answer in its state database and silently reuses it on future `chezmoi init` runs — so it only asks when setting up a new machine.

Full example:

```
{{- $machine_type := promptChoiceOnce . "machine_type" "Machine type" (list "personal" "work" "server") -}}
{{- $is_headless := promptBoolOnce . "is_headless" "Is this headless" -}}
{{- $email := promptStringOnce . "email" "Email address" -}}

encryption = "age"

[age]
  identity = "~/.config/chezmoi/key.txt"
  recipient = "age1your-public-key-here"

[data]
  machine_type = {{ $machine_type | quote }}
  is_headless = {{ $is_headless }}
  email = {{ $email | quote }}
```

When you run `chezmoi init` on a new machine:

```
Machine type? [personal/work/server]: server
Is this headless? [yes/no]: yes
Email address: flo@kempenich.ai
```

It stores the answers, generates `chezmoi.toml`, and every template in your repo can then access `{{ .machine_type }}`, `{{ .is_headless }}`, `{{ .email }}`.

> **About prompt functions in other templates:** All prompt functions (both `promptString` and `promptStringOnce` variants) are available in any `.tmpl` file — chezmoi doesn't restrict them. But in practice they only belong in `.chezmoi.toml.tmpl`. The non-Once variants would ask on every `chezmoi apply`, which breaks automation. The Once variants would technically work, but the stored values end up buried in chezmoi's opaque state database instead of centralised in `chezmoi.toml` where every other template can access them via `.data`. Keep prompts here, let everything else consume the data.

### Changing configuration after init

Edit `.chezmoi.toml.tmpl` in the source directory (your repo), then run `chezmoi init` to re-render the config. This ensures the change is captured and will apply to any future machine of the same type.

`chezmoi init` won't re-ask questions it already has stored answers for. To force re-asking, use `chezmoi init --prompt`.

> For a quick temporary test, you can also edit `~/.config/chezmoi/chezmoi.toml` directly. But this change lives only on that machine and won't be captured in your repo.

### What does `chezmoi init` actually do?

Three things:

1. **Clones your dotfiles repo** into the source directory (`~/.local/share/chezmoi`) if it's not already there.
2. **Renders `.chezmoi.toml.tmpl`** to generate your config file (this is when prompts run).
3. **Optionally applies everything** if you pass `--apply` (e.g., `chezmoi init --apply`).

It's the "bootstrap a new machine from scratch" command. After initial setup, you rarely run it again — you just use `chezmoi edit` → `chezmoi apply`. But it's safe to re-run (thanks to `promptOnce` not re-asking).

### Fallback: manual `chezmoi.toml`

For a throwaway machine or quick testing, you can skip the template and create `~/.config/chezmoi/chezmoi.toml` directly. This works but the values are **not captured in your repo**. Only use for temporary or disposable setups.

---

## Data files: `.chezmoidata`

For simple setups, `[data]` in `chezmoi.toml` is enough. But when you have a lot of structured data — lists of packages, per-machine tool configs, complex nested structures — it gets unwieldy in TOML. That's where `.chezmoidata` comes in.

### How it works

Put files in your source directory root with the name `.chezmoidata.<format>`:

```
.chezmoidata.yaml
.chezmoidata.json
.chezmoidata.toml
```

Or put multiple files in a `.chezmoidata/` directory:

```
.chezmoidata/
  packages.yaml
  apps.json
  work.toml
```

Their contents are merged into the template data automatically. No configuration needed — chezmoi picks them up on every `apply`.

### Example: package lists

`.chezmoidata/packages.yaml`:

```yaml
brew_packages:
  - bat
  - delta
  - fd
  - fzf
  - ripgrep
  - jq

brew_casks:
  personal:
    - 1password
    - discord
    - spotify
    - vlc
  work:
    - slack
    - zoom
    - docker
```

Then in a run script template (`run_onchange_after_brew-install.sh.tmpl`):

```bash
#!/bin/bash

{{ range .brew_packages -}}
brew install {{ . }}
{{ end -}}

{{ if eq .machine_type "personal" -}}
{{ range .brew_casks.personal -}}
brew install --cask {{ . }}
{{ end -}}
{{ end -}}

{{ if eq .machine_type "work" -}}
{{ range .brew_casks.work -}}
brew install --cask {{ . }}
{{ end -}}
{{ end -}}
```

The benefit over putting this in `chezmoi.toml`: it's YAML, so lists and nesting are natural. And it's a separate file, so changes to your package list don't clutter your config diff.

### Example: per-machine overrides

`.chezmoidata/defaults.yaml`:

```yaml
editor: nvim
terminal_font: "JetBrains Mono"
terminal_font_size: 14
```

These become `{{ .editor }}`, `{{ .terminal_font }}`, `{{ .terminal_font_size }}` in templates. If you also set `editor` in your `chezmoi.toml` `[data]` section, the toml value wins (config file takes priority over data files).

### When to use data files vs config

| Situation | Use |
|---|---|
| Machine-specific values (type, email, headless) | `chezmoi.toml` via `.chezmoi.toml.tmpl` with prompts |
| Lists of packages, tools, plugins | `.chezmoidata/*.yaml` |
| Shared defaults across all machines | `.chezmoidata/*.yaml` |
| Values that vary per machine and need prompting | `chezmoi.toml` via prompts |
| Complex nested structures | `.chezmoidata/*.yaml` or `.chezmoidata/*.json` |
| Simple key-value pairs | Either — `chezmoi.toml` is fine |

The rule of thumb: if it's a machine-specific question ("what type is this machine?"), it belongs in `chezmoi.toml` via prompts. If it's shared data that templates consume ("what packages do I want?"), `.chezmoidata` keeps things cleaner.

---

## How sources merge

When chezmoi evaluates a template, all data is merged into a single namespace:

```
Built-in variables (.chezmoi.*)
    ↓ merged with
.chezmoidata files (alphabetical order, later files override earlier)
    ↓ merged with
chezmoi.toml [data] section (highest priority)
    ↓
Available as {{ .variable_name }} in templates
```

Built-in variables live under `.chezmoi.*` so they never conflict with your custom data. Between `.chezmoidata` and `chezmoi.toml`, the config file always wins.

Within `.chezmoidata/`, files are read in alphabetical order. If `apps.yaml` and `packages.yaml` both define the same key, `packages.yaml` wins (it comes later alphabetically).

---

## Debugging data

```bash
# Show all available template data (built-in + data files + config)
chezmoi data

# Test a specific variable
chezmoi execute-template '{{ .machine_type }}'

# Test a nested value from a data file
chezmoi execute-template '{{ .brew_packages }}'

# Test a built-in
chezmoi execute-template '{{ .chezmoi.os }}'
```

---

## Quick reference

| Source | Location | Priority | Use for |
|---|---|---|---|
| Built-in | Automatic | Lowest | OS, arch, hostname |
| Data files | `.chezmoidata.*` or `.chezmoidata/` in source dir | Middle | Package lists, shared defaults, structured data |
| Config file | `~/.config/chezmoi/chezmoi.toml` `[data]` | Highest | Machine-specific values (type, email, headless) |
| Config template | `.chezmoi.toml.tmpl` in source dir | Generates config | Interactive prompts for machine setup |
