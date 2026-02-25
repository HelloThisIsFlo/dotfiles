# Chezmoi Tips & Useful Commands — Cheat Sheet

The previous cheat sheets cover chezmoi's core systems in depth. This one collects the smaller things — commands, workflows, and tricks that don't warrant their own sheet but are good to know.

---

## `chezmoi doctor` — is everything working?

Runs a series of diagnostic checks and tells you what's healthy and what's not.

```bash
chezmoi doctor
```

Output looks like:

```
ok    version          v2.46.0
ok    os/arch          darwin/arm64
ok    config-file      /Users/flo/.config/chezmoi/chezmoi.toml
ok    source-dir       /Users/flo/.local/share/chezmoi
ok    working-tree     /Users/flo/.local/share/chezmoi
ok    git-cli          git version 2.44.0
ok    age-cli          v1.1.1
ok    rbw-cli          rbw 1.9.0
warn  gpg-cli          gpg not found in $PATH
```

What it checks: chezmoi version, OS, config file validity, source directory existence, encryption tools, password manager CLIs, git setup, and more. The `warn` for GPG above is fine if you're using age — it only matters if your config says `encryption = "gpg"`.

Run it when something isn't working and you're not sure why. It's the first thing to check before digging deeper.

---

## `chezmoi merge` — resolving conflicts

When the source state, the target state, and the last-applied state all differ, chezmoi can't automatically decide what to do. This happens when you edit a target file directly (outside of `chezmoi edit`) while the source has also changed.

```bash
chezmoi merge ~/.gitconfig
```

This opens your configured merge tool (see [Configuration cheat sheet](config.md)) with a three-way diff: what chezmoi last applied, what's currently on disk, and what the source wants to apply.

In practice, this is rare if you follow the workflow of always using `chezmoi edit` instead of editing target files directly. If you do hit it, resolve the merge, and chezmoi records the result.

> **Avoiding merges entirely:** Stick to `chezmoi edit ~/.gitconfig` instead of editing `~/.gitconfig` directly. The edit command opens the *source* file, so the source and target never diverge. Merges only happen when you bypass chezmoi and edit the target.

---

## `chezmoi cd` — jump into the source directory

```bash
chezmoi cd
```

Opens a new shell in your source directory (`~/.local/share/chezmoi`). Useful for git operations — committing, pushing, checking status, viewing history.

```bash
chezmoi cd
git log --oneline -10
git push
exit   # back to your normal shell
```

If you have `[git] autoCommit = true` in your config, you still need to push manually (unless you also set `autoPush = true`). `chezmoi cd` is the quick way to do that.

---

## `chezmoi edit` — the right way to make changes

```bash
chezmoi edit ~/.gitconfig        # opens the source file for .gitconfig
chezmoi edit --apply ~/.gitconfig # opens it, then applies on save
```

This opens the *source* file (the template or plain file in your chezmoi directory) in your editor. The `--apply` flag automatically runs `chezmoi apply` after you close the editor, so you see the change immediately.

Why this matters: if you edit `~/.gitconfig` directly, chezmoi doesn't know about the change. Next time you run `chezmoi apply`, it overwrites your edit with whatever's in the source. Always edit through chezmoi.

---

## `chezmoi diff` and `chezmoi status` — what would change?

```bash
chezmoi diff       # show a full diff of what apply would change
chezmoi status     # one-line-per-file summary
```

`chezmoi status` output uses single-letter codes:

```
 M .gitconfig           # Modified — source and target differ
 A .config/new-tool     # Added — exists in source, not on disk
 D .old-config          # Deleted — marked for removal
```

Always run `chezmoi diff` before `chezmoi apply` if you're unsure what will change. It's a dry run that shows the exact diff without modifying anything.

---

## `chezmoi data` — what does chezmoi know?

```bash
chezmoi data          # dump all template data as JSON
chezmoi data | jq .   # pretty-printed
```

Shows everything available in templates: built-in variables (`.chezmoi.os`, `.chezmoi.hostname`, etc.) and all your custom `[data]` values. Essential for debugging templates — if a value isn't showing up here, it won't work in a template.

---

## `chezmoi execute-template` — test template rendering

```bash
echo '{{ .chezmoi.os }}' | chezmoi execute-template
# → darwin

echo '{{ if eq .machine_type "work" }}work{{ else }}personal{{ end }}' | chezmoi execute-template
# → personal

chezmoi execute-template < ~/.local/share/chezmoi/dot_gitconfig.tmpl
# renders the full template with your current data
```

Test template expressions without applying anything. Invaluable when writing a new template and you're not sure if the syntax is right.

---

## `chezmoi forget` — stop managing a file

```bash
chezmoi forget ~/.config/some-app/config.toml
```

Removes the file from chezmoi's source directory (deletes the source entry) but **leaves the target file untouched**. The file stays on disk exactly as-is; chezmoi just stops tracking it.

This is the opposite of `chezmoi add`. Use it when you decide a file doesn't belong in your dotfiles anymore. The file continues to exist on your machine — it just becomes unmanaged.

Compare with `remove_` (from the [Naming cheat sheet](naming.md)): `forget` stops managing and leaves the file. `remove_` actively deletes the target file on all machines.

---

## `chezmoi unmanaged` — what's not tracked?

```bash
chezmoi unmanaged             # list unmanaged files in your home directory
chezmoi unmanaged ~/.config   # scope to a specific directory
```

Shows files in your home directory (or a subdirectory) that chezmoi isn't managing. Useful for auditing — "is there anything in `~/.config` I should be tracking but haven't added yet?"

The output can be noisy (lots of application cache and state files). It's most useful scoped to a specific directory you care about.

---

## `chezmoi add` vs `chezmoi re-add` — updating source from target

Both commands copy a target file's current state back into the source directory. The difference is scope and intent.

```bash
chezmoi add ~/.gitconfig       # adds a new file OR updates an existing one
chezmoi re-add ~/.gitconfig    # updates an existing managed file only
chezmoi re-add                 # updates ALL managed files at once (no arguments)
```

`add` handles both new and existing files. If `~/.gitconfig` isn't managed yet, it starts managing it. If it's already managed, it updates the source from the current target — identical to `re-add`.

`re-add` only works on files chezmoi already manages. Its real purpose is the no-argument form: sweep through every managed file and update the source from whatever's currently on disk. Useful if you've edited a bunch of target files directly and want to capture all those changes in one go.

In practice, if you follow the `chezmoi edit` workflow, you'll rarely need either — they're recovery tools for when you've bypassed chezmoi. But `add` is also the command you use when bringing a new file under chezmoi's management for the first time:

```bash
chezmoi add ~/.config/starship.toml              # manage a new file
chezmoi add --template ~/.config/starship.toml   # manage it as a template
chezmoi add --encrypt ~/.ssh/id_ed25519          # manage it encrypted
```

---

## Workflow summary

The day-to-day loop:

```bash
chezmoi edit ~/.some-config       # edit the source file
chezmoi diff                      # review what would change
chezmoi apply                     # apply changes to target
chezmoi cd && git push && exit    # push to your repo
```

Or more compactly with auto-commit:

```bash
chezmoi edit --apply ~/.some-config   # edit + apply in one step
chezmoi cd && git push && exit        # push (auto-committed already)
```

Setting up a new machine:

```bash
chezmoi init --apply https://github.com/you/dotfiles.git
```

That single command clones, prompts for machine config, and applies everything — including fetching externals, running scripts, and decrypting secrets.

---

## Related cheat sheets

- [Templates](templates.md) — template syntax, conditionals, functions
- [Run Scripts](run-scripts.md) — scripts that run during apply
- [Hooks](hooks.md) — commands before/after lifecycle events
- [Secrets](secrets.md) — rbw and age encryption
- [macOS Preferences](macos-preferences.md) — managing plist settings
- [Configuration](config.md) — chezmoi.toml settings
- [Data Sources](data-sources.md) — where template data comes from
- [Source Directory Naming](naming.md) — prefixes, suffixes, file types
- [External Dependencies](externals.md) — third-party repos and archives
