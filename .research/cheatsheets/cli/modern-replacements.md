# Modern CLI Replacements

Drop-in (or near-drop-in) replacements for classic Unix tools. Each entry: what it replaces, why you'd switch, real examples, and honest caveats.

Status key: **Installed** = in Brewfile, **New** = added this session, **Recommend** = worth evaluating

---

## File Management & Navigation

### eza (replaces `ls`)

**Status:** Installed | `brew "eza"`

Better defaults: colors, git status column, tree view, human-readable sizes — all without flags.

```bash
# The old way
ls -la
ls -laR src/

# The eza way
eza -la                     # long listing with git status indicators
eza -la --git               # explicit git column (added/modified markers)
eza --tree --level=3 src/   # tree view (replaces `tree` for quick looks)
eza -la --sort=modified     # most recently modified first
```

**When to use:** Daily `ls` replacement. The git integration alone is worth it.
**When not to:** Scripts that parse `ls` output — use `ls` or `stat` for machine-readable output.

### bat (replaces `cat`)

**Status:** Installed | `brew "bat"`

Syntax highlighting, line numbers, git diff markers, automatic paging. Also powers delta as a library.

```bash
# The old way
cat src/main.rs
head -50 config.toml

# The bat way
bat src/main.rs                  # syntax-highlighted with line numbers
bat -r 1:50 config.toml         # range (like head)
bat -r 100:120 large-file.log   # specific line range
bat -d src/main.rs               # show only git diff lines (like git diff but in context)
bat --plain file.txt             # no line numbers, no frills (like cat but with highlighting)
```

**Config:** `~/.config/bat/config` for theme, tabs, etc. Integrates with `fzf` preview, `man`, and `git diff`.
**When not to:** Piping binary data or when you genuinely just want bytes (`cat` is fine for `cat file | wc -l`).

### fd (replaces `find`)

**Status:** Installed | `brew "fd"`

Sane defaults: ignores `.git`/`node_modules`, regex by default, colorized output, much faster.

```bash
# The old way
find . -name "*.rs" -type f
find . -name "*.log" -mtime -1

# The fd way
fd '.rs$'                        # find all Rust files (regex, recursive, respects .gitignore)
fd -e toml                       # find by extension
fd -e log --changed-within 1d    # modified in last day
fd -H '.env'                     # include hidden files (-H)
fd -t d config                   # directories only (-t d)
fd -e tmp -x rm {}               # find and delete (like find -exec)
```

**Key difference:** `fd` respects `.gitignore` by default. Use `-u` (unrestricted) to search everything.
**When not to:** Complex `-exec` chains with multiple actions — `find` is still more flexible for elaborate pipelines.

### ripgrep / rg (replaces `grep`)

**Status:** Installed | `brew "ripgrep"`

Fast recursive search. Respects `.gitignore`, skips binary files, shows context with colors.

```bash
# The old way
grep -rn "TODO" --include="*.rs" .
grep -rn "pattern" . | head -20

# The rg way
rg "TODO"                        # recursive, .gitignore-aware, colored
rg "TODO" -t rust                # filter by file type
rg "fn\s+\w+" -t rust            # regex: find all function definitions
rg "error" -C 3                  # 3 lines context before/after
rg "pattern" -l                  # list matching files only
rg "old_name" --json             # structured output for tooling
```

**Pairs with:** `fzf` for interactive grep (`rg "pattern" | fzf`).
**When not to:** `grep -P` (PCRE) one-liners where you need lookbehind/lookahead — rg supports these with `-P` flag though.

### zoxide (replaces `cd` / autojump / z)

**Status:** New | `brew "zoxide"`

Learns your most-used directories. Type partial names, jump instantly.

```bash
# Setup: add to config.fish
zoxide init fish | source

# The old way
cd ~/projects/dotfiles/.research/cheatsheets

# The zoxide way
z cheat             # jumps to most frecent match for "cheat"
z dot research      # multiple terms narrow the match
zi                  # interactive selection with fzf
z -                 # previous directory (like cd -)
```

**How it works:** Tracks directory visits, ranks by frequency + recency ("frecency"). First few days it's learning — after that, it's magic.
**When not to:** Scripting — always use explicit paths in scripts.

### yazi (replaces ranger / file managers)

**Status:** Installed | `brew "yazi"`

Blazing-fast terminal file manager. Async I/O, image preview, bulk rename, plugin system.

```bash
yazi                  # open in current directory
yazi ~/Downloads      # open in specific directory
# Inside yazi:
#   h/l or arrows    — navigate
#   space            — select files
#   d                — delete selected
#   r                — rename
#   p                — paste (after yank with y)
#   S                — shell command on selected
#   q                — quit (cwd changes if configured)
```

**Key feature:** Integrates with `bat` for previews, `fd` for search, `ripgrep` for content search — the whole modern toolkit.
**When not to:** Quick one-off operations. `mv`, `cp`, `fd` are faster for single commands.

### Recommend: broot (replaces `tree` + navigation)

Interactive tree explorer with fuzzy search. Navigate, preview, and act on files without leaving the tree.

```bash
brew install broot
br                    # launch (first run creates shell function)
# Type to fuzzy-filter the tree in real time
# Enter to cd, alt+enter to open
```

### Recommend: dust (replaces `du`)

Intuitive disk usage with visual bars. One-shot — shows biggest directories immediately.

```bash
brew install dust
dust                  # current directory, sorted by size, with visual bars
dust -d 2 ~/          # depth limit
dust -r               # reverse sort (smallest first)
```

### Recommend: duf (replaces `df`)

Modern disk free with color-coded output grouped by device type.

```bash
brew install duf
duf                   # all filesystems, grouped and colored
duf /                 # specific mount point
```

### Recommend: choose (replaces `cut` / `awk` column selection)

Human-friendly field selection. No more counting delimiters.

```bash
brew install choose
# The old way
echo "one two three" | awk '{print $2}'
# The choose way
echo "one two three" | choose 1          # 0-indexed: "two"
echo "a:b:c" | choose -f ':' 1           # custom delimiter
docker ps | choose 0 1 -1                # first, second, last columns
```

---

## Text & Data Processing

### sd (replaces `sed`)

**Status:** New | `brew "sd"`

Intuitive find-and-replace. No backslash hell, no remembering `sed` delimiter rules.

```bash
# The old way
sed -i '' 's/old_name/new_name/g' file.txt
echo "hello world" | sed 's/world/rust/'

# The sd way
sd 'old_name' 'new_name' file.txt        # in-place by default
echo "hello world" | sd 'world' 'rust'   # piped
sd 'fn (\w+)' 'fn new_$1' src/*.rs       # regex with capture groups
sd -F 'exact.string' 'replacement' f.txt  # fixed string (no regex)
```

**Key win:** Regex syntax is just normal regex — no doubled backslashes, no `\(\)` vs `()` confusion.
**When not to:** Complex multi-line transformations with hold space — `sed` (or `awk`) is still more powerful for those edge cases.

### jq (JSON processing)

**Status:** Installed | `brew "jq"`

The standard for JSON on the command line. Filter, transform, query.

```bash
curl -s api.example.com/data | jq '.results[0].name'    # extract field
cat data.json | jq '.[] | select(.age > 30)'            # filter array
cat data.json | jq '[.[] | {name, email}]'              # reshape
echo '{"a":1}' | jq '. + {"b": 2}'                      # merge
jq -r '.name' data.json                                  # raw output (no quotes)
```

**Pairs with:** `curl`/`xh` for API exploration, `bat` for viewing large JSON.

### difftastic (replaces line-based diff)

**Status:** New | `brew "difftastic"`

Structural, syntax-aware diffing. Understands that moving a function isn't "delete 50 lines + add 50 lines" — it's a move.

```bash
# Standalone
difft old.rs new.rs              # side-by-side structural diff
difft --display inline old new   # inline display

# As git diff tool
git config --global diff.external difft
git diff                          # now uses difftastic automatically
git log -p --ext-diff             # log with structural diffs

# Per-invocation (without changing config)
GIT_EXTERNAL_DIFF=difft git diff
```

**Key win:** Understands syntax trees — renames, moved blocks, and formatting changes show as what they are, not as big red/green blocks.
**Tradeoff:** Slower than `delta` on very large diffs. Best for code review, not for scanning 10,000-line generated diffs. Can coexist with `delta` — use difftastic for focused review, delta as daily pager.

### Recommend: grex (generates regex from examples)

Feed it strings, get back a regex that matches them. Great for one-off patterns.

```bash
brew install grex
grex "2023-01-15" "2024-12-31" "2025-06-01"
# Output: ^\d{4}-\d{2}-\d{2}$
grex -r "foo_bar" "foo_baz" "foo_qux"     # with repetition
```

### Recommend: xh (replaces `curl` for API work)

`curl` with better UX: syntax highlighting, sensible defaults, JSON shortcuts.

```bash
brew install xh
xh httpbin.org/get                        # GET with colored output
xh POST api.example.com name=test         # JSON body from key=value
xh :8080/api/health                       # shorthand for localhost
xh -d https://example.com/file.zip        # download mode
```

**When not to:** `curl` is still better for scripting, auth flows, and anything where exact header control matters.

---

## System Monitoring

### btop (replaces `top` / `htop`)

**Status:** Installed | `brew "btop"`

Beautiful system monitor. CPU, memory, network, disk, process tree — all in one TUI.

```bash
btop                  # launch
# Inside btop:
#   f — filter processes
#   t — tree view
#   s — sort menu
#   k — kill process
#   m — toggle memory display
```

**When not to:** Quick "what's eating CPU?" checks — `top -o cpu` is faster to launch and quit.

### viddy (replaces `watch`)

**Status:** Installed | `brew "viddy"`

Modern `watch` with diff highlighting, history, and time-travel through past outputs.

```bash
# The old way
watch -n 2 'kubectl get pods'

# The viddy way
viddy 'kubectl get pods'              # default 2s interval, with diff highlighting
viddy -d -n 5 'curl -s localhost/health'  # 5s interval, highlight changes
# Inside viddy:
#   / — search
#   shift+up/down — scroll through history
```

### hyperfine (replaces `time`)

**Status:** New | `brew "hyperfine"`

Statistical benchmarking. Warmup runs, multiple iterations, comparison, export.

```bash
# The old way
time my-command       # single run, wall clock only

# The hyperfine way
hyperfine 'fd -e rs'                               # 10 runs, mean/stddev/min/max
hyperfine 'rg TODO' 'grep -r TODO'                 # compare two commands
hyperfine --warmup 3 'cargo build'                  # 3 warmup runs first
hyperfine -L tool rg,grep '{tool} pattern src/'     # parameterized comparison
hyperfine --export-markdown bench.md 'my-command'   # export results
```

**Key win:** Statistical rigor. Instead of "it felt faster," you get "262ms +/- 12ms vs 1.4s +/- 80ms."
**When not to:** Quick "how long does this take?" checks — `time` is still fine for that.

### Recommend: procs (replaces `ps`)

Colorized process list with keyword search, tree view, pager support.

```bash
brew install procs
procs                     # all processes, colored, with ports
procs node                # filter by keyword
procs --tree              # process tree
```

### Recommend: bandwhich (network monitor)

Per-process/connection bandwidth usage. See exactly what's using your network.

```bash
brew install bandwhich
sudo bandwhich            # needs root for packet capture
```

### Recommend: gping (replaces `ping`)

`ping` with a real-time graph. Ping multiple hosts simultaneously.

```bash
brew install gping
gping google.com                          # single host with graph
gping google.com cloudflare.com 1.1.1.1   # compare latency
```

---

## Git & Dev Tools

### git-delta (replaces git diff pager)

**Status:** Installed | `brew "git-delta"`

Syntax-highlighted diffs with line numbers, side-by-side mode, and merge conflict display. Already configured as the git pager in this repo.

```bash
# Already configured in .gitconfig:
# [core]
#     pager = delta
# [delta]
#     navigate = true
#     side-by-side = true

git diff                  # automatic — delta renders it
git log -p                # delta renders commit diffs too
delta file1 file2         # standalone diff
```

**Pairs with:** `bat` (uses bat's syntax themes). See `delta --list-themes` for options.

### lazygit (TUI for git)

**Status:** New | `brew "lazygit"`

Full git TUI: staging hunks, interactive rebase, cherry-pick, stash management — all without remembering flags.

```bash
lazygit               # launch in repo
# Inside lazygit:
#   1-5 — switch panels (status, files, branches, commits, stash)
#   space — stage/unstage file
#   tab — stage individual hunks
#   c — commit
#   p — push
#   P — pull
#   r — rebase menu
#   ? — full keybind list
```

**Key win:** Interactive rebase is visual — drag commits, squash, edit messages, all with immediate preview.
**When not to:** Simple commits and pushes. `git add -p && git commit` is still faster for straightforward work.

### Recommend: tokei (replaces `cloc` / `sloccount`)

Fast, accurate code statistics. Recognizes 200+ languages.

```bash
brew install tokei
tokei                     # current repo stats
tokei src/                # specific directory
tokei --sort lines        # sort by line count
```

---

## Shells & Multiplexers

### fish (interactive shell)

**Status:** Installed | `brew "fish"`

Best out-of-the-box interactive experience: autosuggestions, syntax highlighting, web-based config. Not POSIX — that's the point.

**Use for:** Interactive terminal sessions.
**Not for:** Scripts (use bash/zsh for portability).

### nushell (data-oriented shell)

**Status:** Installed | `brew "nushell"`

Structured data pipelines. Every command returns a table, not text. Great for data exploration.

```bash
nu                                    # enter nushell
ls | where size > 1mb | sort-by size  # structured file listing
open data.csv | where age > 30        # CSV as a table
sys | get host                        # system info as structured data
```

**Use for:** Data exploration, CSV/JSON/YAML wrangling, one-off analysis.
**Not for:** Daily shell (yet) — ecosystem is young, not all tools integrate smoothly.

### just (replaces `make` for task running)

**Status:** Installed | `brew "just"`

Command runner without Make's baggage. No tabs-vs-spaces, no implicit rules, just recipes.

```bash
# justfile
build:
    cargo build --release

test *args:
    cargo test {{args}}

deploy env="staging":
    ./deploy.sh {{env}}
```

```bash
just              # list recipes
just build        # run recipe
just test -- -q   # pass args through
```

**Use for:** Project task orchestration, replacing Makefiles.
**Already used:** This dotfiles repo uses Just for scripting orchestration (per CLAUDE.md preference).

---

## Combo Patterns

Real-world pipelines combining multiple modern tools:

```bash
# Find large Rust files, sorted by size
fd -e rs | xargs eza -la --sort=size

# Interactive grep: search, fuzzy-filter results, open in editor
rg "TODO" -l | fzf --preview 'bat --color=always {}' | xargs cursor

# Benchmark two approaches to finding files
hyperfine 'fd -e json' 'find . -name "*.json"'

# Quick project overview
tokei && echo "---" && dust -d 1

# Find and replace across codebase
fd -e rs -x sd 'old_api' 'new_api' {}

# Watch a command with diff highlighting
viddy 'kubectl get pods -o wide'
```

---

## Quick Reference

| Want to... | Classic | Modern | Notes |
|---|---|---|---|
| List files | `ls -la` | `eza -la` | Git status, tree view |
| View file | `cat` | `bat` | Syntax highlighting |
| Find files | `find` | `fd` | Respects .gitignore |
| Search text | `grep -r` | `rg` | Fast, smart defaults |
| Jump dirs | `cd` | `z` (zoxide) | Learns your habits |
| Find & replace | `sed` | `sd` | Sane regex syntax |
| Diff code | `diff` | `difft` / `delta` | Syntax-aware |
| Benchmark | `time` | `hyperfine` | Statistical |
| Watch | `watch` | `viddy` | Diff + history |
| Disk usage | `du` | `dust` | Visual bars |
| Free space | `df` | `duf` | Grouped, colored |
| Processes | `top` | `btop` | Full system TUI |
| Git TUI | `git` CLI | `lazygit` | Interactive rebase |
| JSON | `python -m json.tool` | `jq` | Filter + transform |
