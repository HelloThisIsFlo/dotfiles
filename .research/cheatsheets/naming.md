# Chezmoi Source Directory Naming — Cheat Sheet

Chezmoi doesn't store your dotfiles with their real names. Instead, the source directory uses a naming convention — prefixes and suffixes — that tells chezmoi *how* to manage each file, not just *what* it is. This cheat sheet is the Rosetta Stone between what you see in your repo and what ends up on disk.

---

## The basic mapping

When you run `chezmoi add ~/.gitconfig`, chezmoi copies the file into your source directory with a transformed name:

```
~/.gitconfig  →  ~/.local/share/chezmoi/dot_gitconfig
```

The `dot_` prefix means "this file starts with a dot in the real filesystem." When you run `chezmoi apply`, chezmoi reverses the transformation: `dot_gitconfig` → `.gitconfig`.

Directories work the same way:

```
~/.config/fish/config.fish
→  ~/.local/share/chezmoi/dot_config/fish/config.fish
```

Only the leading dot gets the `dot_` treatment. Subdirectories and filenames without dots stay as-is.

---

## Prefixes — what they do

Prefixes stack. A file can have multiple prefixes, and chezmoi reads them left to right. The order matters: chezmoi expects them in a specific sequence (though in practice you rarely stack more than two).

### `dot_` — leading dot

The most common prefix. Converts to `.` in the target path.

```
dot_zshrc           →  .zshrc
dot_config/         →  .config/
dot_ssh/config      →  .ssh/config
```

### `executable_` — set the executable bit

Makes the target file executable (mode `0755` or `0700` depending on other prefixes). Essential for scripts you want to run directly.

```
dot_local/bin/executable_my-script  →  .local/bin/my-script  (mode 0755)
```

Without this prefix, files get `0644` by default. You don't need this for run scripts (those are executed by chezmoi itself), only for files that *you* want to call as commands.

### `private_` — restrict permissions

Sets the target to `0700` (directories) or `0600` (files). Use for anything that should only be readable by you.

```
private_dot_ssh/           →  .ssh/           (mode 0700)
private_dot_ssh/config     →  .ssh/config     (mode 0600)
```

Chezmoi also verifies permissions during `chezmoi apply` and will fix them if they've drifted.

### `readonly_` — read-only permissions

Sets the target to read-only (`0444` or combined with `private_` for `0400`). Prevents accidental edits to config files you don't want modified.

```
readonly_dot_gitattributes  →  .gitattributes  (mode 0444)
```

Rarely used in practice — most people don't bother locking down dotfiles.

### `empty_` — allow empty files

By default, chezmoi skips creating files whose rendered content is empty. This prevents templates that conditionally produce nothing from leaving empty files around. The `empty_` prefix overrides this: "create this file even if it's empty."

```
empty_dot_hushlogin  →  .hushlogin  (empty file, but still created)
```

The classic use case is `.hushlogin` — macOS checks for its *existence* to suppress the "Last login" message in Terminal. The file's content doesn't matter; it just needs to exist.

### `encrypted_` — file is encrypted in source

Marks a file as encrypted. Chezmoi decrypts it during `chezmoi apply` using your configured encryption (age or GPG). See the [Secrets cheat sheet](secrets.md) for setup.

```
encrypted_private_dot_ssh/private_encrypted_private_key  →  .ssh/private_key
```

When you run `chezmoi add --encrypt ~/.ssh/private_key`, chezmoi handles the prefix naming automatically.

### `exact_` — for directories only

Normally, chezmoi only *adds or updates* files in a directory — it never removes files it doesn't know about. The `exact_` prefix on a directory changes this: chezmoi will **remove** any file in the target directory that isn't managed in the source directory.

```
exact_dot_config/fish/     →  .config/fish/  (unmanaged files in here get deleted)
```

This is powerful but dangerous. Use it for directories where you want chezmoi to be the sole owner — like a `fish/functions/` directory where stale function files would cause confusion. Don't use it for directories where other tools write files (like `.config/` itself — that would nuke half your system).

> **Only applies one level deep.** `exact_` on a directory only cleans that directory's direct children. Subdirectories are unaffected unless they also have the `exact_` prefix.

---

## Special file types

These prefixes change what kind of thing chezmoi creates, rather than just setting attributes.

### `create_` — write once, then hands off

A `create_` file is only written if the target **doesn't already exist**. After first creation, chezmoi ignores it completely — even if the source changes.

```
create_dot_config/some-cli/state.db  →  .config/some-cli/state.db
```

This is a niche feature. The main use case: an application that expects a file to exist with valid structure and crashes or misbehaves if it's missing. The file's contents are purely runtime data — there's nothing to sync, nothing to template. You just need valid scaffolding on a fresh machine so the app works on first launch.

For example, a CLI tool that stores state in a SQLite database and refuses to start if the file is missing. You seed an empty but valid database; after that, the tool owns the file entirely.

`chezmoi diff` and `chezmoi status` will also skip `create_` files that already exist at the target. It's a genuine "set and forget."

> **If you're thinking "I want to sync part of a file but not another part" — that's not what `create_` is for.** Use a template with secrets for files where you control the content, or `modify_` for genuine shared ownership. `create_` means you don't care about the file's content after initial creation.

### `modify_` — surgical editing

A `modify_` file is a script, not a regular file. During `chezmoi apply`, chezmoi pipes the **current target file's contents** into the script on stdin. The script's stdout becomes the new target file.

```
modify_dot_config/some-app/config.json
```

This lets you make targeted edits to files that other tools also manage. Instead of replacing the whole file (which would overwrite the other tool's changes), you read what's there, tweak it, and write it back.

A simple example — ensure a JSON config has a specific key:

```bash
#!/bin/bash
# Read current file from stdin, add our key if missing
python3 -c "
import json, sys
config = json.load(sys.stdin)
config.setdefault('theme', 'dark')
json.dump(config, sys.stdout, indent=2)
"
```

A more realistic example — a CLI tool that stores both your config preferences and a rotating auth token in the same YAML file. You want to sync the config across machines without clobbering the token:

```bash
#!/bin/bash
# modify_dot_config/some-cli/config.yml
python3 -c "
import yaml, sys

# Read current file (may include a fresh auth token)
current = yaml.safe_load(sys.stdin) or {}

# Set the config values we care about
current['git_protocol'] = 'ssh'
current['editor'] = 'nvim'
current['pager'] = 'delta'

# The auth token (if present) passes through untouched

yaml.dump(current, sys.stdout, default_flow_style=False)
"
```

This preserves any keys the tool wrote (like a refreshed auth token) while ensuring your config preferences are always set.

> **Gotcha: often, a template with secrets is the better answer.** If the "dynamic" part of the file is actually a long-lived secret (API key, OAuth token, personal access token), you're better off storing it in your password manager and templating the entire file — chezmoi owns 100% of it, no script needed. For example, `~/.config/gh/hosts.yml` looks like shared ownership (GitHub CLI writes an auth token), but the token is stable and belongs in Bitwarden anyway. A template with `{{ (rbw "github-cli-token").data.password }}` is simpler and more robust. Reserve `modify_` for genuinely rotating values that you can't predict or store — and accept that the script is inherently brittle (you're parsing and rewriting structured files in bash, handling edge cases like an empty file on a fresh machine, and hoping the tool's format doesn't change).

This is an advanced feature. For most files, a regular template is simpler and clearer. Reach for `modify_` only when you genuinely share a file with another tool and can't control the whole thing.

### `symlink_` — create a symlink

The source file's *content* is the symlink target path. Chezmoi creates a symbolic link at the target location.

```
symlink_dot_zshenv  →  .zshenv  (symlink pointing to wherever the file content says)
```

The content of `symlink_dot_zshenv` might be:

```
{{ .chezmoi.homeDir }}/.config/zsh/.zshenv
```

Note it's a template (`.tmpl` suffix) if you need dynamic paths. This is useful when an app expects a file at one location but you want to keep the real file elsewhere.

### `remove_` — delete a target file

Declares that chezmoi should actively **delete** this path from the target. The source file itself is empty — it's just a marker.

```
remove_dot_old_config  →  deletes ~/.old_config
```

Use this for cleanup: you used to manage a file, you've stopped, and you want `chezmoi apply` to clean it up on all your machines. Without `remove_`, the old file would just linger forever.

There's also `.chezmoiremove` — a file in the source root that lists paths to remove, one per line. It supports patterns:

```
.old_config
.config/obsolete-app
.local/bin/deprecated-*
```

`.chezmoiremove` is better when you're cleaning up multiple files. `remove_` prefixed files are better for a single targeted deletion.

---

## The `.tmpl` suffix

Any file (including all the special types above) can also be a template by adding `.tmpl`:

```
dot_gitconfig.tmpl                    →  .gitconfig  (rendered as template)
private_dot_ssh/config.tmpl           →  .ssh/config  (rendered as template, mode 0600)
create_dot_npmrc.tmpl                 →  .npmrc  (created once, rendered as template)
modify_dot_config/app/config.json.tmpl →  modify script is itself templated
```

The `.tmpl` suffix is stripped from the target name and tells chezmoi to render `{{ }}` expressions before writing. See the [Templates cheat sheet](templates.md).

---

## How `chezmoi add` handles naming

You don't usually construct these names by hand. When you run `chezmoi add`, chezmoi examines the file and picks the right prefixes automatically:

```bash
chezmoi add ~/.gitconfig
# → dot_gitconfig (detects the leading dot)

chezmoi add ~/.local/bin/my-script
# → dot_local/bin/executable_my-script (detects executable bit)

chezmoi add ~/.ssh/config
# → private_dot_ssh/private_config (detects restrictive permissions)

chezmoi add --encrypt ~/.ssh/id_ed25519
# → private_dot_ssh/encrypted_private_id_ed25519

chezmoi add --template ~/.gitconfig
# → dot_gitconfig.tmpl (adds .tmpl suffix)
```

If chezmoi gets the prefixes wrong (rare), you can rename the file in the source directory manually. Chezmoi reads the name, not any metadata — so renaming is all it takes.

---

## Prefix stacking order

When multiple prefixes apply, chezmoi expects this order:

```
[remove_|create_|modify_] [encrypted_] [private_] [readonly_] [exact_] [executable_] [dot_] [empty_] name [.tmpl]
```

In practice, the most common combinations you'll see:

```
private_dot_ssh/                          → .ssh/  (0700)
private_dot_ssh/encrypted_private_key     → .ssh/private_key  (encrypted, 0600)
executable_dot_local/bin/executable_foo   → .local/bin/foo  (0755)
create_dot_npmrc.tmpl                     → .npmrc  (write-once template)
exact_dot_config/fish/functions/          → .config/fish/functions/  (exact directory)
```

You'll almost never need more than two prefixes on a single file.

---

## `.chezmoiignore` vs `remove_` vs `exact_`

Three different ways to control what exists at the target. They solve different problems:

| Mechanism | What it does | Use when |
|---|---|---|
| `.chezmoiignore` | Chezmoi pretends the source file doesn't exist on this machine | You have a file in your repo but don't want it on certain machines |
| `remove_` / `.chezmoiremove` | Chezmoi actively deletes the target | You want to clean up a file that shouldn't exist anymore |
| `exact_` directory | Chezmoi deletes unmanaged files in that directory | You want chezmoi to own the entire directory |

`.chezmoiignore` is covered in the [Templates cheat sheet](templates.md) (it's a template itself, so it can conditionally ignore files per machine type).

---

## Quick reference

| Source name | Target | Effect |
|---|---|---|
| `dot_zshrc` | `.zshrc` | Basic dotfile |
| `dot_zshrc.tmpl` | `.zshrc` | Dotfile with template rendering |
| `executable_my-script` | `my-script` | Executable file |
| `private_dot_ssh/` | `.ssh/` | Directory with 0700 |
| `encrypted_secret.txt` | `secret.txt` | Decrypted on apply |
| `create_dot_npmrc` | `.npmrc` | Only written if absent |
| `modify_dot_config/app.json` | `.config/app.json` | Surgical edit via script |
| `symlink_dot_zshenv` | `.zshenv` | Symbolic link |
| `remove_dot_old` | (deleted) | Removes `~/.old` |
| `exact_dot_config/fish/` | `.config/fish/` | Removes unmanaged files |
| `empty_dot_hushlogin` | `.hushlogin` | Created even if empty |
| `readonly_dot_gitattributes` | `.gitattributes` | Read-only permissions |
