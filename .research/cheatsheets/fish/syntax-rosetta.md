# Fish Syntax Rosetta Stone — Cheat Sheet

You have an 800-line zshrc. You know exactly what you want to express. You just don't know the fish syntax for it. This sheet is the translation table you keep open in a split while converting config — every zsh/bash pattern mapped to its fish equivalent, with the gotchas that will otherwise cost you 20 minutes each.

---

## Conditionals

### `if test` replaces `[ ]` and `[[ ]]`

Fish has one conditional syntax: `if test`. No `[ ]`, no `[[ ]]`, no `(( ))`. The `test` command is the same POSIX `test` you already know — it just looks different without the brackets.

```bash
# zsh: if [ "$(uname)" '==' Linux ]; then ... fi
if test (uname) = Linux
    echo "on Linux"
end

# zsh: if [ -z "$argument" ]; then ... fi
if test -z "$argument"
    echo "argument is empty"
end

# zsh: if [ ! -e $file ]; then ... fi
if test ! -e $file
    echo "file does not exist"
end

# zsh: if [ -d $file ]; then ... fi
if test -d $file
    echo "it's a directory"
end
```

> **Gotcha:** Use `=` for string comparison, not `==`. The `test` command is POSIX — `==` is a bash/zshism that happens to work in some shells but is not portable and fish does not support it.

### `command -q` replaces `command -v ... &>/dev/null`

```bash
# zsh: if command -v bat &>/dev/null; then ... fi
if command -q bat
    set -gx BAT_THEME "Catppuccin Mocha"
end
```

`command -q` is the idiomatic way to check if a binary exists. It's silent by design — no output redirection needed.

### `and`/`or` and `&&`/`||`

Fish supports both styles. Use `&&`/`||` for inline one-liners, `and`/`or` for multi-line flow.

```bash
# One-liner (zsh: [ -f ~/.config/op/plugins.sh ] && source ~/.config/op/plugins.sh)
test -f ~/.config/op/plugins.sh; and source ~/.config/op/plugins.sh

# Also valid (fish 3.0+):
test -f ~/.config/op/plugins.sh && source ~/.config/op/plugins.sh
```

> **Gotcha:** `and`/`or` connect to the **previous command's exit status**, not as boolean operators inside an expression. `if test -f foo; and test -d bar` works, but `if test -f foo -a -d bar` is the `test` builtin's own `-a` flag — different mechanism, same result.

### `status is-interactive` — the conf.d guard

```bash
if status is-interactive
    fish_vi_key_bindings
end
```

Standard guard at the top of `conf.d/` files. See [aliases-and-abbreviations.md](aliases-and-abbreviations.md) for what goes inside it.

---

## Loops

### `for ... in`

Same concept as bash/zsh, different terminator:

```bash
# zsh: for version in $(asdf list java); do ... done
for version in (asdf list java)
    echo $version
end
```

### No brace expansion — use `seq`

Fish does not have `{1..10}` syntax. Use `seq` instead:

```bash
# zsh: for i in {1..5}; do echo $i; done
for i in (seq 1 5)
    echo $i
end
```

### `while` loops

```bash
while test -f /tmp/lockfile
    sleep 1
end
```

### Iterating over lines of output

```bash
# Process each line of a command's output
for line in (cat /etc/hosts)
    echo "entry: $line"
end
```

> **Gotcha:** Fish splits command substitution output on newlines by default, not whitespace. This is usually what you want. If a filename contains spaces, `for f in (ls)` handles it correctly — each line is one element. This is the opposite of bash, where you'd need `IFS=$'\n'`.

---

## Command substitution

### `(command)` replaces `$(command)` and backticks

```bash
# zsh: basefile=$(basename "$file" | sed -e 's/[^a-zA-Z0-9._-]/-/g')
set basefile (basename "$file" | sed -e 's/[^a-zA-Z0-9._-]/-/g')

# zsh: tmpfile=$( mktemp -t transferXXX )
set tmpfile (mktemp -t transferXXX)

# zsh: ip=$(local-ip)
set ip (local-ip)
```

Nesting works naturally:

```bash
set result (string trim (cat /tmp/output.txt))
```

> **Gotcha:** No `$()` syntax at all. If you type `$(command)`, fish will error. Muscle memory will fight you on this for about a week.

---

## String manipulation

### The `string` builtin replaces `${var...}` parameter expansion

Fish has no parameter expansion syntax (`${var%%pattern}`, `${var:offset}`, etc.). The `string` builtin does everything. This is the biggest mental shift coming from zsh.

### Strip suffix/prefix — `string replace`

```bash
# zsh: class_c_network=${ip%.*}.0/24
# Strip last octet: 192.168.1.42 → 192.168.1
set class_c_network (string replace -r '\.[^.]*$' '' $ip).0/24
```

```bash
# zsh: ${filename%.txt}
set name (string replace -r '\.txt$' '' $filename)

# zsh: ${filename#*/}
set rest (string replace -r '^[^/]*/' '' $filename)
```

`-r` enables regex. Without it, the match is literal.

### Substring — `string sub`

```bash
# zsh: ${var:0:5}  — first 5 characters
string sub -l 5 $var

# zsh: ${var:3}  — everything from index 3
string sub -s 4 $var  # fish is 1-indexed
```

> **Gotcha:** Fish string indexing is 1-based, not 0-based. `string sub -s 4` starts at the 4th character (equivalent to zsh's `${var:3}`).

### Split — `string split`

```bash
# Split PATH-like variable on colons
set parts (string split : $MANPATH)

# Split once (zsh: ${var%%:*} and ${var#*:})
set first (string split -m 1 : $var)[1]
set rest (string split -m 1 : $var)[2]
```

### Match and capture — `string match`

```bash
# Glob-style match
string match '*.md' $filename

# Regex capture groups
if string match -rq '^(\d+)\.(\d+)' $version
    echo "major: $match[1], minor: $match[2]"
end
```

`-q` suppresses output (for use in `if`). Capture groups populate `$match`.

### Other `string` subcommands

`string trim`, `string upper`, `string lower`, `string length`, `string repeat -n 3`, `string join ", "`, `string collect` — all do what you'd expect. Run `string --help` for the full list.

For the `set` variable system (scopes, `$PATH` list handling, exports), see [variables-and-path.md](variables-and-path.md).

---

## Quoting

### No word splitting in double quotes

This is the single biggest difference between fish and bash/zsh. In fish, variables are **never** word-split, even unquoted. Quoting is only needed for literal special characters.

```bash
set greeting "hello world"

# In bash, this would be TWO arguments without quotes:
echo $greeting   # fish: one argument, "hello world" — always

# So this just works:
set file "my document.txt"
test -f $file    # no quotes needed, but they don't hurt
```

> **Gotcha:** Because variables don't word-split, `set args "-l -a"` creates ONE argument containing a literal space. If you want multiple arguments, use a list: `set args -l -a`. This trips up people translating from bash where `OPTS="-l -a"` and then `ls $OPTS` works via word splitting.

### Single quotes are fully literal

Same as bash/zsh — no variable expansion, no escaping (except `\'`).

```bash
echo 'the variable is $HOME'  # prints literally: the variable is $HOME
```

---

## Piping and redirection

### `$status` replaces `$?`

```bash
# Checking explicitly:
some_command
if test $status -eq 0
    echo "success"
end

# Idiomatic — just use the command directly:
if some_command
    echo "success"
end
```

### Stderr redirection

```bash
# zsh: command 2>/dev/null
command 2>/dev/null

# zsh: command &>/dev/null  (both stdout and stderr)
command &>/dev/null         # fish 3.0+ supports this

# zsh: command 2>&1
command 2>&1
```

### No herestrings (`<<<`) and no heredocs (`<<EOF`)

Fish has neither. Use `echo` and pipe, or `printf`:

```bash
# zsh: grep foo <<< "$variable"
echo $variable | grep foo

# zsh: cat <<EOF
# multi
# line
# EOF
printf '%s\n' "multi" "line"

# Or for longer blocks:
echo "line one
line two
line three" | some_command
```

### Process substitution workaround

Fish has no `<(command)` syntax. Use `psub` or a temp file:

```bash
# zsh: diff <(sort file1) <(sort file2)
diff (sort file1 | psub) (sort file2 | psub)
```

> **Gotcha:** `psub` creates a temporary file behind the scenes. It works well for most cases, but the file is cleaned up after the command finishes — don't try to save the path for later use.

---

## Functions

### Declaring functions

```bash
# zsh: function mkcd { dir_name=$1; mkdir $dir_name && cd $dir_name }
function mkcd
    mkdir $argv[1] && cd $argv[1]
end
```

No `$1`, `$2`, etc. Fish uses `$argv` as a list. `$argv[1]` is the first argument.

### Argument handling

```bash
# zsh: ${@:2}  — all args except first
$argv[2..]

# zsh: ${@:1:-1}  — all args except last
$argv[1..-2]

# zsh: $#  — argument count
count $argv
```

### Functions auto-save

In fish, functions defined in `~/.config/fish/functions/funcname.fish` are autoloaded. You don't source a file of function definitions — you save each function as its own file. See [functions.md](functions.md) for the full pattern.

### Return values

```bash
function is_git_repo
    git rev-parse --is-inside-work-tree &>/dev/null
    # implicitly returns $status of last command
end

function explicit_return
    if test -z "$argv[1]"
        return 1
    end
    echo "got: $argv[1]"
    return 0
end
```

---

## Sourcing and config structure

### Config structure

Fish uses `conf.d/*.fish` (alphabetical order) + `config.fish` — not one giant rc file.

```bash
# zsh: [ -f $HOME/.travis/travis.sh ] && source $HOME/.travis/travis.sh
test -f $HOME/.travis/travis.sh; and source $HOME/.travis/travis.sh
```

### Aliases are abbreviations

The right way is `abbr -a ll 'eza -la'` — it expands in-place so you see the real command. For the full decision tree, see [aliases-and-abbreviations.md](aliases-and-abbreviations.md).

---

## Quick reference

The "I know what I want, just give me the fish syntax" table.

| zsh / bash | fish | Notes |
|---|---|---|
| `$1`, `$2`, `$@` | `$argv[1]`, `$argv[2]`, `$argv` | 1-indexed list |
| `$#` | `(count $argv)` | |
| `$?` | `$status` | |
| `$!` | `$last_pid` | |
| `$$` | `$fish_pid` | |
| `$(command)` | `(command)` | No dollar sign |
| `` `command` `` | `(command)` | Backticks not supported |
| `${var:-default}` | `if set -q var; echo $var; else; echo default; end` | Or use `set -q var; or set var default` |
| `${var:=default}` | `set -q var; or set var default` | Set-if-unset pattern |
| `${var%%pattern}` | `string replace -r 'pattern$' '' $var` | Regex suffix strip |
| `${var##pattern}` | `string replace -r '^pattern' '' $var` | Regex prefix strip |
| `${var%suffix}` | `string replace -r 'suffix$' '' $var` | Non-greedy via regex |
| `${var:offset:len}` | `string sub -s (math $offset+1) -l $len $var` | 1-indexed |
| `${#var}` | `string length $var` | |
| `export VAR=val` | `set -gx VAR val` | `-g` global, `-x` export |
| `local var=val` | `set -l var val` | Function-scoped |
| `unset VAR` | `set -e VAR` | |
| `VAR=val command` | `env VAR=val command` | No inline assignment |
| `[[ -f file ]]` | `test -f file` | Same flags: `-d`, `-e`, `-z`, `-n`, etc. |
| `[[ $a == $b ]]` | `test "$a" = "$b"` | Single `=` |
| `[[ $a =~ regex ]]` | `string match -rq 'regex' $a` | |
| `command -v cmd &>/dev/null` | `command -q cmd` | Silent existence check |
| `if cmd; then; fi` | `if cmd; ...; end` | `end` not `fi` |
| `for x in list; do; done` | `for x in list; ...; end` | `end` not `done` |
| `while cmd; do; done` | `while cmd; ...; end` | |
| `case $var in pat) ;; esac` | `switch $var; case pat; ...; end` | |
| `{1..10}` | `(seq 1 10)` | No brace expansion |
| `cmd1 && cmd2` | `cmd1 && cmd2` or `cmd1; and cmd2` | Both work |
| `cmd1 \|\| cmd2` | `cmd1 \|\| cmd2` or `cmd1; or cmd2` | Both work |
| `<<< "string"` | `echo "string" \| cmd` | No herestrings |
| `<(command)` | `(command \| psub)` | Process substitution |
| `source file` | `source file` | Same |
| `alias x='cmd'` | `abbr -a x cmd` | Abbreviations are the right way |
| `function f { }` | `function f; ...; end` | |
| `return` | `return` | Same |
| `\n` in `echo` | `echo` handles it, or `printf` | `echo` in fish interprets `\n` by default |
| `array=(a b c)` | `set array a b c` | All variables are lists |
| `${array[0]}` | `$array[1]` | 1-indexed |
| `${array[@]}` | `$array` | Already the whole list |
| `${#array[@]}` | `(count $array)` | |
| `array+=(val)` | `set -a array val` | `-a` appends |
| `read -p "prompt: " var` | `read -P "prompt: " var` | Capital `-P` |
| `trap cmd EXIT` | `function --on-event fish_exit; cmd; end` | Event handlers |

---

## What to read next

- [variables-and-path.md](variables-and-path.md) — `set` scopes, `$PATH` as a list, universal variables
- [functions.md](functions.md) — autoloading, `$argv`, event handlers, `funcsave`
- [aliases-and-abbreviations.md](aliases-and-abbreviations.md) — when to use `abbr` vs `alias` vs a function file
