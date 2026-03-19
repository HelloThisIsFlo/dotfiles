# Homebrew in Chezmoi — Three Approaches Compared

You want chezmoi to manage your Homebrew packages. There are three officially blessed ways to do it. Each has real tradeoffs — this guide helps you pick.

---

## The problem all three solve

You want:
1. A **declarative list** of what should be installed (taps, formulas, casks)
2. A **script** that installs missing packages on `chezmoi apply`
3. **Re-runs** when the list changes (but not on every apply)

The difference is where the list lives and how the script consumes it.

---

## Approach A: `dot_Brewfile` + hash trick

**This is what we use now.** Also the approach shown on chezmoi's [macOS page](https://www.chezmoi.io/user-guide/machines/macos/).

```
dot_Brewfile                              ← deployed to ~/.Brewfile
run_onchange_after_brew-bundle.sh.tmpl    ← runs brew bundle
```

The script embeds a sha256 hash of the Brewfile so chezmoi re-runs it when the Brewfile changes:

```bash
{{- if eq .chezmoi.os "darwin" -}}
#!/bin/bash

# Brewfile hash: {{ include "dot_Brewfile" | sha256sum }}

brew bundle --no-upgrade
{{ end -}}
```

### How to add a package

Edit `dot_Brewfile`, add `brew "something"` or `cask "something"`, run `chezmoi apply`.

### Pros

- **Familiar format.** The Brewfile is standard Homebrew — anyone who uses `brew bundle` already knows it.
- **Full Brewfile syntax.** Supports everything: `restart_service: true`, `args:`, `link: false`, `mas` App Store installs, tap URLs with custom clone paths, etc.
- **One file to edit.** All packages live in one place with no indirection.
- **`dot_Brewfile` deploys to `~/.Brewfile`.** So `brew bundle` outside of chezmoi also works (useful for `brew bundle cleanup --force` to uninstall packages removed from the list).
- **Simple.** The script is 6 lines.

### Cons

- **`brew bundle` uses `--adopt` internally for casks.** When an app auto-updates itself (common with GUI apps), the Caskroom version and `/Applications` version diverge. `brew bundle` tries to "adopt" the existing app, compares versions, fails, then purges the download but leaves metadata behind — creating a zombie state where `brew list` says installed but `brew upgrade` says not installed. The `--no-upgrade` flag mitigates this (skips already-installed packages entirely), but new installs can still hit it if the app was previously installed outside Homebrew.
- **No cross-platform.** The Brewfile is macOS-only. If you later want Linux packages managed the same way, this approach doesn't extend.
- **No per-machine conditionals.** The Brewfile is a plain file (not a template). Every machine gets the same list. You can't say "install Docker on work machines only."
- **Deploys `~/.Brewfile` to target.** Minor clutter in home directory.

### When to choose this

You only use macOS, don't need per-machine package variation, and value the simplicity of a standard Brewfile. The `--no-upgrade` flag is good enough for the cask version mismatch issue.

---

## Approach B: `.chezmoidata/brew.yaml` + templated script

The approach from chezmoi's [Install packages declaratively](https://www.chezmoi.io/user-guide/advanced/install-packages-declaratively/) guide.

```
.chezmoidata/brew.yaml                         ← data, not deployed
run_onchange_after_brew-install.sh.tmpl        ← generates install commands
```

Package lists live in a YAML data file:

```yaml
brew:
  taps:
    - d12frosted/emacs-plus
    - ngrok/ngrok
  formulas:
    - bat
    - git-delta
    - jq
  casks:
    - amethyst
    - discord
    - iterm2
```

The script iterates over the data:

```bash
{{- if eq .chezmoi.os "darwin" -}}
#!/bin/bash

# brew.yaml hash: {{ include ".chezmoidata/brew.yaml" | sha256sum }}

{{ range .brew.taps -}}
brew tap {{ . }} 2>/dev/null || true
{{ end }}
{{ range .brew.formulas -}}
brew install {{ . }} || echo "⚠ Failed: {{ . }}"
{{ end }}
{{ range .brew.casks -}}
brew list --cask {{ . }} &>/dev/null || brew install --cask {{ . }} || echo "⚠ Failed: {{ . }}"
{{ end }}
{{ end -}}
```

Or, following the official example exactly, you can still use `brew bundle` under the hood:

```bash
{{- if eq .chezmoi.os "darwin" -}}
#!/bin/bash

# brew.yaml hash: {{ include ".chezmoidata/brew.yaml" | sha256sum }}

brew bundle --no-upgrade --file=/dev/stdin <<EOF
{{ range .brew.taps -}}
tap {{ . | quote }}
{{ end -}}
{{ range .brew.formulas -}}
brew {{ . | quote }}
{{ end -}}
{{ range .brew.casks -}}
cask {{ . | quote }}
{{ end -}}
EOF
{{ end -}}
```

### How to add a package

Edit `.chezmoidata/brew.yaml`, add an entry to the list, run `chezmoi apply`.

### Pros

- **Clean separation of data and logic.** What to install (YAML) is separate from how to install (script). Easy to read, easy to diff.
- **Cross-platform ready.** One YAML file can have `darwin:` and `linux:` sections. Multiple scripts read from the same data.
- **Sets the pattern for Phase 6.5.** Add `.chezmoidata/pip.yaml`, `.chezmoidata/npm.yaml`, etc. — each with its own `run_onchange_after_` script. Consistent across all package ecosystems.
- **No file deployed to `~/`.** `.chezmoidata/` is source-only — chezmoi never places it in the target directory.
- **Changes take effect on `chezmoi apply`** (no `chezmoi init` required). `.chezmoidata` files are read as part of the source state.
- **Can bypass `brew bundle` entirely.** Using direct `brew install` commands in the script avoids the `--adopt` bug. Casks need a `brew list --cask` guard since `brew install --cask` errors on already-installed apps.

### Cons

- **`.chezmoidata` files cannot be templated.** This is a hard limitation ([GitHub issue #1663](https://github.com/twpayne/chezmoi/issues/1663)). You cannot use `{{ if }}` in the YAML. Per-machine variation must happen in the *script* template (filtering the data), not in the data file.
- **Loses Brewfile-specific syntax.** No `restart_service: true`, `args:`, `link: false`, `mas` entries. You'd handle these as special cases in the script (e.g., a separate `services:` list with `brew services start`).
- **Two files to manage per ecosystem** (data + script) instead of one. More indirection.
- **No `chezmoi edit` shorthand.** `chezmoi edit ~/.Brewfile` doesn't work for `.chezmoidata/` files — you edit them directly in the source directory.
- **YAML list merge gotcha.** If two `.chezmoidata/*.yaml` files define the same key, lists are *replaced* not merged. Only dictionaries are deep-merged.

### When to choose this

You want structured data driving your installs, plan to manage multiple package ecosystems (brew + pip + npm + cargo), or want cross-platform support. You're comfortable with the indirection of data + script.

---

## Approach C: Inline template lists in the script

What [Tom Payne (chezmoi author) uses](https://github.com/twpayne/dotfiles) in his own dotfiles. No external data file at all.

```
run_onchange_before_install-packages.sh.tmpl   ← everything in one file
```

Package lists are Go template variables defined inside the script:

```bash
{{- if eq .chezmoi.os "darwin" -}}
#!/bin/bash

{{ $taps := list
     "d12frosted/emacs-plus"
     "ngrok/ngrok"
-}}

{{ $brews := list
     "bat"
     "git-delta"
     "jq"
-}}

{{ $casks := list
     "amethyst"
     "discord"
     "iterm2"
-}}

{{/* Conditional packages */}}
{{ if eq .trust_level "personal" -}}
{{   $casks = concat $casks (list "spotify" "telegram" "plex") -}}
{{ end -}}

brew bundle --no-upgrade --file=/dev/stdin <<EOF
{{ range ($taps | sortAlpha | uniq) -}}
tap "{{ . }}"
{{ end -}}
{{ range ($brews | sortAlpha | uniq) -}}
brew "{{ . }}"
{{ end -}}
{{ range ($casks | sortAlpha | uniq) -}}
cask "{{ . }}"
{{ end -}}
EOF
{{ end -}}
```

### How to add a package

Edit the `$brews` or `$casks` list in the script template. Run `chezmoi apply`.

### Pros

- **Self-contained.** One file, no indirection. Data and logic together. Open the script, see everything.
- **Full Go template power.** `{{ if }}`, `{{ else }}`, `concat`, `sortAlpha`, `uniq` — any conditional logic you want. Per-machine, per-trust-level, per-OS package variation is trivial.
- **`run_onchange` just works.** The rendered output changes when the lists change — no explicit hash trick needed. (The hash is implicit in the rendered content.)
- **Can still use `brew bundle` syntax.** The template *generates* a Brewfile and pipes it to `brew bundle --file=/dev/stdin`, so you keep `restart_service:`, `mas`, etc. — just expressed as template logic.
- **Easiest to migrate to.** Take your current Brewfile, wrap it in a `cat <<EOF ... EOF`, and you're done. Add template variables incrementally.
- **Proven in the wild.** This is literally how the chezmoi author manages his packages.

### Cons

- **Big script files.** 123 formulas + 46 casks + taps + template logic = a 200+ line script. Harder to scan than a clean YAML list.
- **Mixing data with logic.** If you want to share the package list with another script (e.g., a cleanup script that removes unlisted packages), you'd have to duplicate the lists or extract them.
- **No standard data format.** The lists are Go template syntax (`list "a" "b" "c"`), not YAML/TOML/JSON. Not as easy to parse with external tools or read at a glance.
- **Doesn't set a reusable pattern.** Each ecosystem (brew, pip, npm) would be its own self-contained script with its own inline list. No shared data layer. Fine for brew alone, but if you have 5 ecosystems it gets repetitive.

### When to choose this

You want per-machine conditional packages (personal vs work, macOS vs Linux), prefer everything in one file, and don't mind longer scripts. You're comfortable with Go template syntax and don't need other scripts to read the package data.

---

## Side-by-side comparison

| | A: `dot_Brewfile` | B: `.chezmoidata/` | C: Inline template |
|---|---|---|---|
| **Where data lives** | `dot_Brewfile` (deployed to `~/`) | `.chezmoidata/brew.yaml` (source only) | Inside the script template |
| **Brewfile syntax** | Full native | Lost (use direct `brew install` or generate on-the-fly) | Generate on-the-fly via heredoc |
| **Per-machine conditionals** | Not possible | In the script (not in the YAML) | Directly in the data (Go template) |
| **Cross-platform** | macOS only | YAML can have darwin/linux sections | Template can have OS conditionals |
| **Change detection** | Hash trick (`include` + `sha256sum`) | Hash trick or implicit (rendered output changes) | Implicit (rendered output changes) |
| **Files per ecosystem** | 2 (Brewfile + script) | 2 (YAML + script) | 1 (script only) |
| **Phase 6.5 pattern** | Doesn't extend well | Clean: one `.chezmoidata/*.yaml` per ecosystem | Separate script per ecosystem, no shared data |
| **Readability for 100+ packages** | Great (standard Brewfile) | Great (YAML list) | Verbose (Go template `list` syntax) |
| **Official docs** | [macOS page](https://www.chezmoi.io/user-guide/machines/macos/) | [Declarative packages guide](https://www.chezmoi.io/user-guide/advanced/install-packages-declaratively/) | Author's [own dotfiles](https://github.com/twpayne/dotfiles) |

---

## What about `brew bundle`'s adopt bug?

This is separate from the data storage question:

- **Approach A** uses `brew bundle` directly — `--no-upgrade` mitigates the issue (skips installed packages), but new cask installs can still hit it.
- **Approach B** can either generate a Brewfile for `brew bundle --file=/dev/stdin` (same issue) or bypass `brew bundle` entirely with direct `brew install` commands (avoids the bug completely).
- **Approach C** typically generates a Brewfile for `brew bundle --file=/dev/stdin` (same issue), but could also use direct `brew install` commands.

If avoiding `brew bundle` is a goal, approaches B and C both support it. Approach A cannot — `dot_Brewfile` is inherently tied to `brew bundle`.

---

## Decision framework

**Start here:**

1. **Do you need per-machine package variation?** (personal vs work, macOS vs Linux)
   - No → Approach A is simplest
   - Yes → Approach B or C

2. **Do you want a reusable pattern for pip/npm/cargo/go?**
   - Yes → Approach B (`.chezmoidata/` directory scales cleanly)
   - No / don't care yet → Approach A or C

3. **Do you want to avoid `brew bundle` entirely?**
   - Yes → Approach B with direct `brew install`, or Approach C with direct `brew install`
   - No → Any approach works (`--no-upgrade` is good enough)

4. **How much Go template are you comfortable with?**
   - Minimal → Approach A (no templates) or B (templates only in script)
   - Comfortable → Approach C (templates everywhere)

---

## Sources

- [chezmoi — macOS (Brewfile approach)](https://www.chezmoi.io/user-guide/machines/macos/)
- [chezmoi — Install packages declaratively (.chezmoidata approach)](https://www.chezmoi.io/user-guide/advanced/install-packages-declaratively/)
- [twpayne/dotfiles (inline approach)](https://github.com/twpayne/dotfiles)
- [Issue #2868 — "Best practice: where to store a list of packages?"](https://github.com/twpayne/chezmoi/issues/2868) — Tom Payne's direct response
- [Issue #468 — "Running a script based on changes to another file"](https://github.com/twpayne/chezmoi/issues/468) — origin of the hash trick
- [Issue #1663 — ".chezmoidata cannot be templated"](https://github.com/twpayne/chezmoi/issues/1663) — the limitation
