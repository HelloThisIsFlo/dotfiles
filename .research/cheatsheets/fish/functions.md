# Fish Functions — Cheat Sheet

Your zshrc has dozens of functions: argument validation helpers, tmux wrappers, file-upload utilities, OS-switching updaters. Fish supports all of this, but functions work fundamentally differently — they're autoloaded from individual files, scoped more tightly, and have a built-in event system that zsh lacks entirely. Misunderstanding any of these differences means functions that silently break, variables that leak, or config that loads twice.

---

## Basics

### Defining a function

```bash
function greet
    echo "hello, $argv"
end
```

The body goes between `function ... end`. No `{ }`, no `()` after the name.

### Arguments: `$argv` replaces `$1`, `$2`, `$@`

Fish has no `$1`, `$2`, etc. Everything comes through `$argv` — a list.

```bash
function greet
    echo "hello, $argv[1]"      # first argument
    echo "all args: $argv"      # all arguments (like $@ in zsh)
    echo "arg count: "(count $argv)  # like $# in zsh
end
```

### Named arguments with `--argument-names`

For readability, name your positional args. This creates local variables from `$argv`.

```bash
function mkcd --argument-names dir_name
    mkdir -p $dir_name && cd $dir_name
end
```

Multiple names map to consecutive `$argv` positions:

```bash
function transfer_file --argument-names file_path target_host
    scp $file_path $target_host:~/incoming/
end
```

> **Gotcha:** `--argument-names` only creates named aliases for `$argv[1]`, `$argv[2]`, etc. It does not enforce that arguments were passed. If you call `mkcd` with no args, `$dir_name` is empty — no error, just an empty string. Always validate.

### Return values

`return` sets `$status` (like `$?` in zsh). Return 0 for success, non-zero for failure.

```bash
function require_file --argument-names path
    if not test -e $path
        echo "File not found: $path" >&2
        return 1
    end
end
```

> **Gotcha:** `return` without a value returns the status of the last command. This is usually what you want, but can surprise you if the last command was an `echo` (which almost always succeeds).

---

## Argument validation

### Translating the `_ensure_argument_present` pattern

Your zshrc uses this helper everywhere:

```bash
function _ensure_argument_present {
  argument=$1; cli=$2; arg_name=$3
  if [ -z "$argument" ]; then
    echo "Please supply a $arg_name when using this cli:"
    echo "    \`$cli $arg_name\`"
    throw "IllegalArgument"
  fi
}
```

The fish equivalent:

```bash
function _ensure_argument_present --argument-names argument cli arg_name
    if test -z "$argument"
        echo "Please supply a $arg_name when using this cli:"
        echo "    `$cli $arg_name`"
        return 1
    end
end
```

Usage stays almost identical:

```bash
function tk --argument-names session_name
    _ensure_argument_present "$session_name" tk SESSION_NAME; or return
    tmux kill-session -t $session_name
end
```

> **Gotcha:** The `; or return` after the validation call is critical. Fish has no exceptions (`throw`). If the helper returns non-zero, you must explicitly bail out. Without `; or return`, execution continues to the next line regardless. This is the single most common mistake when porting from zsh.

### Alternative: inline validation

For simple cases, skip the helper entirely:

```bash
function serve-current-dir --argument-names port
    if test -z "$port"
        echo "Usage: serve-current-dir PORT"
        return 1
    end
    echo "Serving current dir on port '$port'"
    docker run --rm -it -p "$port:80" -v (pwd):/usr/share/nginx/html:ro jorgeandrada/nginx-autoindex
end
```

### `argparse` — the right way for complex arguments

When a function takes flags or optional arguments, `argparse` is the fish-native solution:

```bash
function custom-tree --description "tree with sane defaults"
    argparse 'l/level=!_validate_int --min 1' -- $argv; or return

    set -l level $_flag_level
    set -l to_ignore 'node_modules|lib'
    tree -L $level -I $to_ignore --noreport $argv
end
```

For your simpler functions, `--argument-names` + a `-z` check is fine. Reach for `argparse` when you have flags (`--flag`), optional arguments, or need `--help` generation.

---

## Autoloaded functions

### The `~/.config/fish/functions/` directory

This is the defining feature of fish functions. Place one function per file, named `function_name.fish`. Fish loads it lazily — the file is read only when the function is first called.

```
~/.config/fish/functions/
  mkcd.fish
  transfer.fish
  updateall.fish
  tk.fish
  custom-tree.fish
  _ensure_argument_present.fish
```

Each file contains exactly one public function definition:

```bash
# ~/.config/fish/functions/mkcd.fish
function mkcd --argument-names dir_name
    mkdir -p $dir_name && cd $dir_name
end
```

### When to use `functions/` vs `conf.d/`

| Location | Loaded when | Use for |
|---|---|---|
| `functions/name.fish` | Lazily, on first call | Standalone functions (the default) |
| `conf.d/something.fish` | Eagerly, at shell startup | Variables, abbreviations, event handlers, startup logic |

The rule: **if it's a function someone calls by name, put it in `functions/`.** If it's config that must run at startup (setting variables, registering event handlers, defining abbreviations), put it in `conf.d/`.

> **Gotcha:** If you define a function inside a `conf.d/` file, it works but defeats lazy loading — it's parsed on every shell startup even if never called. The exception is event handler functions that must be registered at startup (see [Event handlers](#event-handlers) below).

### Helper functions

Functions starting with `_` (like `_ensure_argument_present`) are a convention for "private" helpers. Fish doesn't enforce this — it's just naming. Put them in `functions/_helper_name.fish` like any other function.

### How chezmoi manages function files

In chezmoi source state, `functions/` lives at:

```
dot_config/private_fish/functions/
```

Each function file maps to `~/.config/fish/functions/`. Add a new function with:

```bash
chezmoi add ~/.config/fish/functions/mkcd.fish
```

See [config-structure.md](config-structure.md) for the full directory layout.

---

## Translating specific functions

### `transfer` — file checks, tty detection, curl piping

The most complex function in your zshrc. Key translations: `tty -s` becomes `isatty stdin`, `$()` becomes `()`, `${@:2}` becomes `$argv[2..]`.

```bash
# ~/.config/fish/functions/transfer.fish
function transfer --description "Upload to transfer.sh"
    set -l url "https://transfersh.floriankempenich.com/"

    if test (count $argv) -eq 0
        echo "No arguments specified. Usage:"
        echo "  transfer /tmp/test.md"
        echo "  cat /tmp/test.md | transfer test.md"
        return 1
    end

    set -l tmpfile (mktemp -t transferXXX)
    set -l file $argv[1]

    if isatty stdin
        set -l basefile (basename "$file" | sed -e 's/[^a-zA-Z0-9._-]/-/g')
        if not test -e $file
            echo "File $file doesn't exist."
            return 1
        end
        if test -d $file
            set -l zipfile (mktemp -t transferXXX.zip)
            cd (dirname $file) && zip -r -q - (basename $file) >> $zipfile
            curl --progress-bar --upload-file "$zipfile" "$url$basefile.zip" >> $tmpfile
            rm -f $zipfile
        else
            curl --progress-bar --upload-file "$file" "$url$basefile" >> $tmpfile
        end
    else
        curl --progress-bar --upload-file "-" "$url$file" >> $tmpfile
    end

    cat $tmpfile
    echo
    rm -f $tmpfile
end
```

Key differences from the zsh version:
- `isatty stdin` instead of `tty -s` — fish builtin, reads cleaner
- `(mktemp ...)` instead of `$( mktemp ... )` — fish command substitution syntax
- `(basename $file)` instead of `$(basename "$file")` — same pattern
- `set -l` for all local variables — see [Scope](#scope) below
- No `\n` in echo — fish's `echo` doesn't interpret escape sequences by default (use `printf` or `echo -e` if needed)

### `updateall` — OS switching

```bash
# ~/.config/fish/functions/updateall.fish
function updateall --description "Update all packages"
    if test (uname) = Linux
        sudo apt update && sudo apt upgrade -y && sudo apt autoremove -y
    else
        brew update && brew upgrade && brew cleanup
    end
end
```

See [syntax-rosetta.md](syntax-rosetta.md) for the full `if test` pattern.

### `ta` / `ts` / `tk` — tmux wrappers with optional args

```bash
# ~/.config/fish/functions/ta.fish
function ta --argument-names session_name --description "tmux attach"
    if test -z "$session_name"
        tmux -CC attach
    else
        tmux -CC attach -t $session_name
    end
end
```

```bash
# ~/.config/fish/functions/ts.fish
function ts --argument-names session_name --description "tmux new session"
    if test -z "$session_name"
        tmux -CC new-session
    else
        tmux -CC new-session -s $session_name
    end
end
```

```bash
# ~/.config/fish/functions/tk.fish
function tk --argument-names session_name --description "tmux kill session"
    _ensure_argument_present "$session_name" tk SESSION_NAME; or return
    tmux kill-session -t $session_name
end
```

> **Consider:** These are great candidates for [abbreviations](aliases-and-abbreviations.md) if you don't need the optional-argument logic. `abbr -a ta 'tmux -CC attach'` is simpler and shows the expanded command in your history.

### `scratch` — paths with spaces

```bash
# ~/.config/fish/functions/scratch.fish
function scratch --argument-names scratch_file --description "Open scratch note"
    set -l folder "$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Main/Scratch"
    mvim "$folder/$scratch_file.md"
end
```

> **Gotcha:** Fish handles spaces in variables better than zsh — `$folder` doesn't need quoting to prevent word splitting (fish doesn't split on spaces). But quoting it is still good practice for clarity and when passing to external commands.

### `custom-tree` — slicing args with `$argv[2..]`

```bash
# ~/.config/fish/functions/custom-tree.fish
function custom-tree --argument-names level --description "tree with defaults"
    _ensure_argument_present "$level" custom-tree LEVEL; or return
    set -l to_ignore 'node_modules|lib'
    tree -L $level -I $to_ignore --noreport $argv[2..]
end
```

The zsh `${@:2}` becomes `$argv[2..]` — fish's slice syntax. See [syntax-rosetta.md](syntax-rosetta.md) for more on list slicing.

### `deactivate-droplet` — environment cleanup

```bash
# ~/.config/fish/functions/deactivate-droplet.fish
function deactivate-droplet --description "Deactivate Docker droplet"
    set -e DOCKER_TLS_VERIFY
    set -e DOCKER_HOST
    set -e DOCKER_CERT_PATH
    echo "Docker droplet deactivated"
end
```

`unset VAR` becomes `set -e VAR` (erase). See [syntax-rosetta.md](syntax-rosetta.md).

---

## Event handlers

Fish has a built-in event system with no zsh equivalent. Functions can fire on shell events, variable changes, or signals.

### `--on-event` — shell lifecycle events

```bash
# Run code when fish starts
function my_greeting --on-event fish_prompt
    echo "Ready."
end
```

The most useful events:

| Event | When it fires |
|---|---|
| `fish_prompt` | Before every prompt |
| `fish_exit` | When shell exits |
| `fish_postexec` | After every command |
| `fish_preexec` | Before every command |

### `--on-variable` — react to variable changes

```bash
function _update_window_title --on-variable PWD
    printf '\033]0;%s\007' (basename $PWD)
end
```

This fires every time `$PWD` changes (i.e., every `cd`). Useful for terminal title, prompt updates, or syncing state.

### `--on-signal` — trap replacement

```bash
function _cleanup --on-signal INT
    echo "Caught Ctrl-C, cleaning up..."
    rm -f /tmp/my_lockfile
end
```

Replaces zsh's `trap 'cleanup' INT`.

### Where to put event handlers

Event handlers must be registered at startup — they cannot be lazy-loaded from `functions/`. Place them in `conf.d/`:

```bash
# ~/.config/fish/conf.d/window-title.fish
function _update_window_title --on-variable PWD
    printf '\033]0;%s\007' (basename $PWD)
end
```

> **Gotcha:** If you put an `--on-event` function in `functions/`, it will never fire because fish never loads the file (no one calls it by name, and the event binding isn't registered until the file is loaded). This is a common source of "why isn't my handler running?" confusion.

---

## Scope

### Variables are local by default (unlike zsh)

In zsh, variables inside functions leak to the caller by default. In fish, `set` inside a function creates a **function-scoped** variable by default.

```bash
function example
    set name "local to this function"
    set -l also_local "explicit local"
    set -g visible_everywhere "global"
end
```

| Scope flag | Meaning |
|---|---|
| *(none)* | Function-local (if inside a function) |
| `-l` | Explicitly local — same as no flag inside a function, but clearer |
| `-g` | Global — visible in all functions and the interactive session |
| `-U` | Universal — persists across all fish sessions (stored on disk) |

> **Gotcha:** The no-flag default depends on context. Inside a function, `set x value` is local. At the top level (interactive prompt or `conf.d/`), `set x value` is global. Use `-l` or `-g` explicitly to avoid ambiguity. The `-l` flag is essentially free documentation.

### Implications for your ported functions

In zsh, `_activate_droplet` uses `eval` to set environment variables in the caller's shell. In fish, you'd need to explicitly scope those as global:

```bash
function _activate_droplet --argument-names secret_repo_path
    _ensure_argument_present "$secret_repo_path" _activate_droplet SECRET_REPO_PATH; or return
    eval ($secret_repo_path/activate.sh)
    echo "Docker droplet activated: "(basename $secret_repo_path)
end
```

> **Gotcha:** `eval` in fish works similarly to zsh, but the output of `activate.sh` must produce valid fish syntax (`set -gx VAR value`), not bash syntax (`export VAR=value`). If the script outputs bash, you'll need a wrapper that translates. This is a common trap when porting scripts that `eval` output from external tools.

---

## Quick reference

| Task | Fish syntax |
|---|---|
| Define a function | `function name ... end` |
| Named arguments | `function name --argument-names a b` |
| All arguments | `$argv` |
| Nth argument | `$argv[N]` |
| Argument count | `(count $argv)` |
| Remaining args from N | `$argv[N..]` |
| Return with status | `return 1` |
| Check empty arg | `if test -z "$arg"` |
| Call helper + bail on fail | `helper $arg; or return` |
| Erase a variable | `set -e VAR` |
| Local variable | `set -l name value` |
| Global variable | `set -g name value` |
| Universal variable | `set -U name value` |
| Autoloaded function | `~/.config/fish/functions/name.fish` |
| Event handler | `function name --on-event fish_exit` |
| Variable watcher | `function name --on-variable PWD` |
| Signal handler | `function name --on-signal INT` |
| Parse flags | `argparse 'v/verbose' -- $argv; or return` |
| Function description | `function name --description "text"` |
| List all functions | `functions` |
| View function source | `functions name` |
| Delete a function | `functions -e name` |

---

## See also

- [Syntax Rosetta Stone](syntax-rosetta.md) — the full zsh-to-fish translation table
- [Aliases and Abbreviations](aliases-and-abbreviations.md) — when to use `abbr` instead of a function
- [Completions](completions.md) — adding tab completions for your custom functions
- [Config Structure](config-structure.md) — where `functions/`, `conf.d/`, and `completions/` live
