# Chezmoi Configuration — Cheat Sheet

Chezmoi's configuration lives at `~/.config/chezmoi/chezmoi.toml`. This file controls both chezmoi's behaviour and your custom template data.

One of the most important sections is `[data]`, where you define variables that templates consume. For a full guide on data sources — including `[data]`, `.chezmoidata` files, built-in variables, and `.chezmoi.toml.tmpl` with interactive prompts — see the [Data Sources cheat sheet](chezmoi-data-sources-cheatsheet.md).

This cheat sheet covers everything *else* in the config file: the settings that control how chezmoi itself behaves.

---

## Config file location

```
~/.config/chezmoi/chezmoi.toml
```

You should generate this from `.chezmoi.toml.tmpl` in your source directory (see the Data Sources sheet), but the settings below work the same regardless of how the file is created.

---

## Encryption

Configures how `chezmoi add --encrypt` and encrypted file decryption work. See the [Secrets cheat sheet](chezmoi-secrets-cheatsheet.md) for full setup details.

```toml
encryption = "age"

[age]
  identity = "~/.config/chezmoi/key.txt"
  recipient = "age1your-public-key-here"
```

For GPG instead of age:

```toml
encryption = "gpg"

[gpg]
  recipient = "your-gpg-key-id"
```

---

## Git integration

Chezmoi can automatically commit and push when you make changes. Useful if you want your dotfiles repo always up to date without remembering to commit.

```toml
[git]
  autoCommit = true   # commit after chezmoi add, edit, etc.
  autoPush = false     # push after each auto-commit (can be noisy)
  autoAdd = true       # git add new files automatically
```

A common setup is `autoCommit = true` with `autoPush = false` — changes are tracked locally, and you push manually when you're ready.

---

## Diff tool

What `chezmoi diff` uses to show differences between source and target. By default it uses chezmoi's built-in diff, which is fine for most cases.

```toml
[diff]
  command = "delta"     # use delta for coloured diffs
  pager = "less"        # pipe output through a pager
```

Or with VS Code:

```toml
[diff]
  command = "code"
  args = ["--diff", "--wait"]
```

---

## Merge tool

What `chezmoi merge` uses for three-way conflict resolution. Only matters when the source, target, and last-applied version all differ.

```toml
[merge]
  command = "nvim"
  args = ["-d"]
```

Or with VS Code:

```toml
[merge]
  command = "code"
  args = ["--merge", "--wait"]
```

If you never manually edit target files (you shouldn't need to with `chezmoi edit`), you'll rarely encounter merges.

---

## Edit settings

Configure which editor `chezmoi edit` opens.

```toml
[edit]
  command = "nvim"
  args = []
```

Chezmoi also respects the `$VISUAL` and `$EDITOR` environment variables. The config setting overrides both. If none are set, it falls back to `vi`.

---

## Interpreters

Map file extensions to specific runtimes for run scripts. Useful if the default interpreter isn't what you want.

```toml
[interpreters.py]
  command = "/usr/bin/python3"

[interpreters.rb]
  command = "/usr/local/bin/ruby"
```

You usually don't need this — chezmoi picks up interpreters from `$PATH` and shebang lines. Only configure it if you need a specific version or non-standard path.

---

## CD command

What shell `chezmoi cd` drops you into.

```toml
[cd]
  command = "/bin/zsh"
```

Defaults to your `$SHELL`. Rarely needs changing.

---

## A typical config file

Putting it together, a realistic `chezmoi.toml` might look like:

```toml
encryption = "age"

[age]
  identity = "~/.config/chezmoi/key.txt"
  recipient = "age1your-public-key-here"

[git]
  autoCommit = true
  autoPush = false

[diff]
  command = "delta"

[data]
  machine_type = "personal"
  is_headless = false
  email = "flo@kempenich.ai"
```

Most sections are optional. The only ones you'll likely use are `[age]` (if encrypting), `[git]` (if auto-committing), and `[data]` (always).

---

## Quick reference

| Section | What it controls | Likely to use? |
|---|---|---|
| `encryption` | Encryption method (`age` or `gpg`) | Yes, if using age |
| `[age]` / `[gpg]` | Encryption keys and recipients | Yes, if using age |
| `[git]` | Auto-commit, auto-push, auto-add | Nice to have |
| `[diff]` | External diff tool | Optional |
| `[merge]` | Three-way merge tool | Rarely |
| `[edit]` | Editor for `chezmoi edit` | Only if `$EDITOR` isn't set |
| `[hooks]` | Commands before/after lifecycle events | Rarely — see [Hooks sheet](chezmoi-hooks-cheatsheet.md) |
| `[interpreters]` | Script runtime overrides | Rarely |
| `[cd]` | Shell for `chezmoi cd` | Almost never |
| `[data]` | Template variables | **Always** — see [Data Sources sheet](chezmoi-data-sources-cheatsheet.md) |
