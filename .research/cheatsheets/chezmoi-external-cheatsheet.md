# Chezmoi External Dependencies — Cheat Sheet

Some dotfiles depend on things you didn't write — shell plugins, font files, vim colour schemes, zsh frameworks, tmux plugin managers. You need these on every machine, but committing someone else's repository into yours is messy: your git history fills with their changes, updates are manual, and your repo balloons in size.

`.chezmoiexternal` solves this. You declare "I need this repo/archive at this path," and chezmoi fetches it during `chezmoi apply`. Your repo only stores the *declaration*, not the actual files.

---

## How it works

Create a file called `.chezmoiexternal.toml` in the root of your source directory. Each entry maps a target path to an external source:

```toml
[".oh-my-zsh"]
  type = "archive"
  url = "https://github.com/ohmyzsh/ohmyzsh/archive/master.tar.gz"
  exact = true
  stripComponents = 1
  refreshPeriod = "168h"
```

When you run `chezmoi apply`, chezmoi downloads the archive, extracts it to `~/.oh-my-zsh`, and strips the top-level directory from the tarball (that's what `stripComponents` does — GitHub archives always have a `reponame-branch/` wrapper).

Your source directory never contains the oh-my-zsh files. Your git repo stays clean.

---

## The two types

### `archive` — download and extract a tarball or zip

Use for anything distributed as a release archive or GitHub's auto-generated tarballs.

```toml
[".config/tmux/plugins/tpm"]
  type = "archive"
  url = "https://github.com/tmux-plugins/tpm/archive/master.tar.gz"
  exact = true
  stripComponents = 1
```

`exact = true` means chezmoi treats the directory like an `exact_` prefix — files not in the archive get deleted. This keeps the directory clean if the upstream project removes files between versions.

### `git-repo` — clone a git repository

Use when you need a full git clone (e.g., the tool does `git pull` internally, or you want `.git/` metadata).

```toml
[".tmux/plugins/tpm"]
  type = "git-repo"
  url = "https://github.com/tmux-plugins/tpm.git"
  refreshPeriod = "168h"
```

The difference: `archive` gives you a snapshot of files. `git-repo` gives you a proper clone with history, branches, and the ability to `git pull`. Some plugin managers (like tpm itself) expect a git repo because they run `git` commands internally.

---

## `refreshPeriod` — how often to re-fetch

Chezmoi doesn't re-download on every `chezmoi apply`. It caches the result and only re-fetches when the refresh period expires.

```toml
refreshPeriod = "168h"   # 168 hours = 7 days
```

Common values:

| Period | Meaning |
|---|---|
| `"0"` | Every single apply (slow, usually wrong) |
| `"24h"` | Daily |
| `"168h"` | Weekly |
| `"720h"` | Monthly (30 days) |
| omitted | Only fetches once, never refreshes |

For most plugins and tools, weekly (`"168h"`) is a good balance. You get updates regularly without slowing down every apply. If you want something truly pinned, omit `refreshPeriod` and it fetches once — then only again if you run `chezmoi apply --refresh-externals`.

---

## Pinning versions

Pointing at `master.tar.gz` means you get whatever's on main. That's fine for things you trust to be stable, but risky for anything where a breaking change would ruin your shell.

### Pin to a tag

```toml
[".config/tmux/plugins/tpm"]
  type = "archive"
  url = "https://github.com/tmux-plugins/tpm/archive/refs/tags/v3.1.0.tar.gz"
  exact = true
  stripComponents = 1
```

No `refreshPeriod` needed — this URL always returns the same content. You update by changing the tag in the URL.

### Pin to a commit (git-repo)

```toml
[".tmux/plugins/tpm"]
  type = "git-repo"
  url = "https://github.com/tmux-plugins/tpm.git"
  clone.args = ["--branch", "v3.1.0", "--depth", "1"]
```

`--depth 1` gives you a shallow clone — just the files, no full history. Saves disk space and clone time.

### The tradeoff

Pinning means stability but manual updates. Following `master` means automatic updates but potential breakage. For your shell environment, where a broken plugin means a broken terminal on a fresh machine, pinning is usually the safer choice.

---

## Practical examples

### Zsh plugins (without a framework)

If you manage zsh plugins yourself instead of using oh-my-zsh or similar:

```toml
[".zsh/plugins/zsh-autosuggestions"]
  type = "archive"
  url = "https://github.com/zsh-users/zsh-autosuggestions/archive/master.tar.gz"
  exact = true
  stripComponents = 1
  refreshPeriod = "168h"

[".zsh/plugins/zsh-syntax-highlighting"]
  type = "archive"
  url = "https://github.com/zsh-users/zsh-syntax-highlighting/archive/master.tar.gz"
  exact = true
  stripComponents = 1
  refreshPeriod = "168h"

[".zsh/plugins/zsh-completions"]
  type = "archive"
  url = "https://github.com/zsh-users/zsh-completions/archive/master.tar.gz"
  exact = true
  stripComponents = 1
  refreshPeriod = "168h"
```

Then in your `.zshrc`:

```bash
source ~/.zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh
source ~/.zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
fpath=(~/.zsh/plugins/zsh-completions/src $fpath)
```

No plugin manager needed. Chezmoi *is* your plugin manager.

### Nerd Fonts (single font file)

```toml
[".local/share/fonts/JetBrainsMonoNerdFont-Regular.ttf"]
  type = "file"
  url = "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.1.1/JetBrainsMono.zip"
```

Wait — that's a zip containing multiple files and you want just one. For that, use `archive` with an `include` filter:

```toml
[".local/share/fonts"]
  type = "archive"
  url = "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.1.1/JetBrainsMono.zip"
  include = ["JetBrainsMonoNerdFont-Regular.ttf", "JetBrainsMonoNerdFont-Bold.ttf", "JetBrainsMonoNerdFont-Italic.ttf"]
```

Pinned to a specific release. Only the font files you actually use are extracted.

### Neovim plugin manager (needs git repo)

Some tools expect to manage their own updates via git. Lazy.nvim (Neovim's plugin manager) bootstraps itself from a git clone:

```toml
[".local/share/nvim/lazy/lazy.nvim"]
  type = "git-repo"
  url = "https://github.com/folke/lazy.nvim.git"
  clone.args = ["--branch", "stable", "--depth", "1"]
  refreshPeriod = "168h"
```

Lazy.nvim then handles all other Neovim plugins internally. You only need chezmoi to bootstrap the plugin manager itself.

---

## Template support

`.chezmoiexternal.toml` can also be a template by adding `.tmpl`:

```
.chezmoiexternal.toml.tmpl
```

This lets you conditionally include externals per machine:

```toml
{{ if eq .chezmoi.os "darwin" -}}
[".local/share/fonts"]
  type = "archive"
  url = "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.1.1/JetBrainsMono.zip"
  include = ["JetBrainsMonoNerdFont-Regular.ttf"]
{{ end -}}

{{ if not .is_headless -}}
[".zsh/plugins/zsh-autosuggestions"]
  type = "archive"
  url = "https://github.com/zsh-users/zsh-autosuggestions/archive/master.tar.gz"
  exact = true
  stripComponents = 1
  refreshPeriod = "168h"
{{ end -}}
```

A headless server doesn't need fonts or zsh plugins — skip them entirely.

---

## Commands

```bash
chezmoi apply                          # fetches externals if cache expired
chezmoi apply --refresh-externals      # force re-fetch everything, ignoring cache
chezmoi managed --include=externals    # list all externally managed paths
chezmoi diff                           # shows changes from externals too
```

`--refresh-externals` is your "update everything now" command. Useful after changing a pinned version or when you want to pull latest regardless of the refresh period.

---

## When to use externals vs other approaches

| Approach | When to use |
|---|---|
| `.chezmoiexternal` | Third-party repos/archives you need at a specific path |
| Run script with `git clone` | If you need complex clone logic or post-clone setup |
| Homebrew | If the tool is available as a brew package (simpler, better) |
| Just commit it | Tiny files (a single script, a colour scheme file) — not worth the machinery |

The rule of thumb: if it's a **directory of files from someone else's repo** that needs to live at a specific path in your home directory, use externals. If it's a **binary or package**, use your system package manager. If it's a **single small file**, just commit it.

---

## Quick reference

```toml
# Archive (snapshot of files)
["target/path"]
  type = "archive"
  url = "https://github.com/owner/repo/archive/refs/tags/v1.0.tar.gz"
  exact = true            # delete files not in archive
  stripComponents = 1     # strip top-level directory from tarball
  refreshPeriod = "168h"  # re-fetch weekly
  include = ["*.ttf"]     # only extract matching files

# Git repo (full clone)
["target/path"]
  type = "git-repo"
  url = "https://github.com/owner/repo.git"
  refreshPeriod = "168h"
  clone.args = ["--depth", "1"]     # shallow clone
  pull.args = ["--ff-only"]         # safe pulls only

# Single file download
["target/path/filename"]
  type = "file"
  url = "https://example.com/some-script.sh"
  executable = true       # make it executable
  refreshPeriod = "720h"  # monthly
```
