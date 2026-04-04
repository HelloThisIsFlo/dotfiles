# Chezmoi Features Worth Exploring — Cheat Sheet

Features beyond the core chezmoi workflow that solve specific problems — managing files you don't fully own, cleaning up unwanted files, reusable template partials, and more. Each includes a real-world example from this repo and a verdict.

---

## `modify_` — Patch files you don't fully own

**The problem:** Some config files are shared between you and a tool. You want to set certain keys, but the tool also writes to the file (adding contexts, tokens, runtime state). Managing the whole file with chezmoi means `chezmoi apply` clobbers the tool's changes.

**`modify_` files** receive the current target content on stdin and output the merged result. Chezmoi writes whatever your script/template returns.

**Example — `~/.kube/config`:**

Tools like `gcloud`, `aws eks`, `doctl` all add clusters/contexts to your kubeconfig. You can't own the whole file — but you can ensure your personal clusters are always present:

```
# Source file: modify_dot_kube/modify_config
{{- /* chezmoi:modify-template */ -}}
{{- $config := .chezmoi.stdin | fromYaml -}}
{{- /* Ensure my homelab cluster is always in the kubeconfig */ -}}
{{- $homelab := dict "cluster" (dict "server" "https://k8s.home.lan:6443") "name" "homelab" -}}
{{- $config = set $config "clusters" (append $config.clusters $homelab | uniq) -}}
{{- $config | toYaml -}}
```

On `chezmoi apply`: reads the current kubeconfig, injects your cluster, preserves everything `gcloud`/`doctl` added.

**Example — `~/.docker/config.json`:**

Docker writes `auths` (login tokens) alongside your settings like `credsStore`:

```
{{- /* chezmoi:modify-template */ -}}
{{- $config := .chezmoi.stdin | fromJson -}}
{{- $_ := set $config "credsStore" "osxkeychain" -}}
{{- $_ := set $config "detachKeys" "ctrl-z,z" -}}
{{- $config | toPrettyJson -}}
```

Your keys are guaranteed. Docker's auth tokens survive.

**When to use which:**
- Plists -> `defaults write` scripts (plists are binary, `modify_` can't parse them)
- Configs you fully own (fish, git, etc.) -> regular template
- Configs shared with a tool (kubeconfig, docker config, app JSON) -> `modify_`

**Verdict: Use it** — when you have a config file that a tool also writes to.

---

## `[scriptEnv]` — Environment variables for scripts

**What we have now** in `.chezmoi.toml.tmpl`:

```toml
[data]
    mise_bin = "{{ joinPath .chezmoi.homeDir ".local/bin/mise" }}"
```

Then in scripts:

```bash
# Every script that needs mise must be a .tmpl file
{{ .mise_bin }} install
```

**With `[scriptEnv]`:**

```toml
# .chezmoi.toml.tmpl
[scriptEnv]
    MISE_BIN = "{{ joinPath .chezmoi.homeDir ".local/bin/mise" }}"
```

Then in scripts:

```bash
# No .tmpl needed — $MISE_BIN is injected as a real env var
$MISE_BIN install
```

**The tradeoff:**
- `[data]` + templates: explicit — you see `{{ .mise_bin }}` in the source and know it's templated
- `[scriptEnv]`: implicit — `$MISE_BIN` looks like a normal env var, you'd have to remember it comes from chezmoi config

**For this repo:** The mise scripts already need `.tmpl` for other reasons (like the `{{ include ... | sha256sum }}` hash trigger). So `scriptEnv` wouldn't save the `.tmpl` extension anyway.

**Verdict: Skip** — `[data]` approach is the right call. Templates are explicit, and scripts need `.tmpl` anyway for `sha256sum` triggers. `scriptEnv` would only shine with many non-template scripts that all need the same env vars.

---

## `output` — Run commands inside templates

Captures command stdout at template-render time. The escape hatch for system data chezmoi doesn't expose natively.

**Example — hostname on a machine you don't control:**

```
# dot_config/private_fish/conf.d/02__shell-env.fish.tmpl
{{ $hostname := output "hostname" "-s" | trim }}
set -gx MACHINE_NAME {{ $hostname | quote }}
```

Or use it to set a machine-specific label in git config:

```
# dot_gitconfig.tmpl
[user]
    name = Flo Kempenich
{{ if eq .trust_level "work" }}
    # On work machines, use the hostname to identify which machine signed
    signingkey = "{{ output "hostname" "-s" | trim }}-signing-key"
{{ end }}
```

**The key insight:** This is for values that are **specific to the current machine but not under your control**. Chezmoi gives you `.chezmoi.hostname`, but `output` lets you read *anything* — the system serial number, the active network interface, a value from `defaults read`, etc.

> **Danger:** If the command fails during bootstrap (tool not installed yet), the whole template fails. Guard with `lookPath` if needed.

**Verdict: Maybe later** — keep in your back pocket for machines where you don't control the system identity. `.chezmoi.hostname` covers the basic case, but the pattern extends to any system command.

---

## `remove_` — Ensure a file does NOT exist

```
# Source file: remove_dot_mackup.cfg
# (empty file — just the name matters)
```

On `chezmoi apply`, this **deletes** `~/.mackup.cfg` from the target. Every time, on every machine.

**Cleanup script vs `remove_`:**

For one-time migration cleanup, a `run_once` script works fine:

```bash
# run_once_after_0500-CLEANUP-remove-legacy.sh
rm -f ~/.asdfrc ~/.tool-versions ~/.mackup.cfg
rm -rf ~/.mackup ~/.antigen
```

The difference is about **time horizon and new machines:**
- **Cleanup script:** runs once, done. If you set up a new machine 6 months later where some tool created `~/.asdfrc` as a default, the script already ran — it won't clean it up.
- **`remove_`:** declarative, runs every `chezmoi apply`, on every machine, forever. "This file should never exist in my home directory, period."

**Where `remove_` shines:** Files that keep coming back. Some tools recreate their defaults on launch. If you don't want `~/.lesshst` or `~/.wget-hsts` cluttering your home dir, `remove_` deletes them on every apply.

```
remove_dot_lesshst             # less keeps recreating this
remove_dot_wget-hsts           # wget keeps recreating this
```

**Verdict: Maybe later** — for migration cleanup, a `run_once` script is simpler. Use `remove_` for files that keep coming back or that you want permanently banned from `~`.

---

## `.chezmoitemplates/` — Reusable template partials

Create a `.chezmoitemplates/` directory at the repo root. Files inside are available via `{{ template "name.tmpl" . }}`.

**You can pass variables.** The `.` passes the full template data context. You can also pass a custom dict:

```
{{ template "name.tmpl" (dict "file" "dot_config/mise/config.toml" "bin" .mise_bin) }}
```

**Power example — onchange script generator:**

A partial that handles the "hash a config file and re-run a command when it changes" pattern:

```
# .chezmoitemplates/onchange-header.tmpl
#!/bin/bash
# {{ .file }} hash: {{ include .file | sha256sum }}
```

Then the mise install script becomes:

```
{{ template "onchange-header.tmpl" (dict "file" "dot_config/mise/config.toml") }}
{{ .mise_bin }} cache clear
{{ .mise_bin }} install
```

And any future onchange script follows the same pattern:

```
{{ template "onchange-header.tmpl" (dict "file" "dot_Brewfile") }}
brew bundle --global
```

One line to get the hash trigger + shebang, then just the command.

**Honest take:** With 7 scripts, this is overkill. The maintenance cost of indirection outweighs the DRY benefit at current scale.

**Verdict: Maybe later** — revisit when you have 10+ scripts. The `dict` passing trick makes it genuinely powerful though.

---

## `create_` — Write once, never overwrite

```
# Source file: create_dot_gitconfig.local
[user]
    # Override email per-machine if needed:
    # email = work@company.com
```

On first `chezmoi apply`: creates `~/.gitconfig.local`.
On every subsequent apply: **completely ignored**, even if you or a tool modified it.

**When this makes sense:** Files that need a **seed** (starting content) but then become **locally owned**. The classic pattern is a "local overrides" file that a main config includes:

```gitconfig
# Your managed .gitconfig:
[include]
    path = ~/.gitconfig.local    # <- this file is create_ managed
```

The `.gitconfig.local` gets seeded with a template on first apply, then you customize it per-machine (different signing keys, work vs personal email, etc.) without chezmoi ever overwriting your local changes.

**Why not a script?** A `run_once` script that creates the file works too, but `create_` is cleaner — the seed content lives in your source tree as a real file, so you can see and edit the template.

**Verdict: Maybe later** — you'll want this when you set up the `trust_level` distinction between personal/work machines and need machine-specific override files.

---

## `.chezmoiversion` — Minimum version guard

```
# .chezmoiversion (at repo root)
2.70.0
```

If someone (or future-you on an old machine) runs `chezmoi apply` with an older version, it fails immediately with a clear error instead of silently breaking on unsupported template functions.

**Verdict: Use it** — already implemented in this repo (pinned to 2.70.0). One file, zero maintenance, prevents confusing failures.

---

## Related cheat sheets

- [Templates](templates.md) — template syntax, conditionals, functions
- [Naming Conventions](naming.md) — prefixes like `modify_`, `remove_`, `create_`
- [Run Scripts](run-scripts.md) — scripts that run during apply
- [Configuration](config.md) — `[data]`, `[scriptEnv]`, and chezmoi.toml settings
- [Data Sources](data-sources.md) — where template data comes from
- [Tips & Escape Hatches](tips.md) — doctor, merge, forget, debug templates
