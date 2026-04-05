# Mise Tasks — Cheat Sheet

Mise has a built-in task runner that can replace Make, Just, or npm scripts. Tasks are defined either inline in `mise.toml` (TOML tasks) or as standalone executable scripts (file tasks). Dependencies run in parallel by default, and source/output tracking skips tasks that are already up-to-date.

---

## TOML tasks — inline in `mise.toml`

**The problem:** You want simple project tasks without creating separate script files.

```toml
[tasks.build]
description = "Build the project"
run = "cargo build --release"

[tasks.test]
description = "Run test suite"
depends = ["build"]
run = "cargo test"

[tasks.lint]
description = "Lint and format"
run = ["cargo clippy", "cargo fmt --check"]  # array = run in series
env = { RUST_BACKTRACE = "1" }
```

Run with `mise run build` or the alias `mise r build`.

**Key config fields:**

| Field | Purpose |
|---|---|
| `run` | Command string or array of commands (series) |
| `description` | Shows in `mise tasks ls` and help |
| `alias` | Shorthand name (e.g., `alias = "b"` -> `mise run b`) |
| `depends` | Tasks that must complete first (parallel by default) |
| `depends_post` | Tasks that run after this task completes |
| `wait_for` | Like `depends` but doesn't trigger the dependency — just waits if it's already running |
| `sources` | Glob patterns for input files |
| `outputs` | Expected output files — skip task if newer than sources |
| `env` | Task-scoped environment variables |
| `dir` | Working directory (default: directory containing `mise.toml`) |
| `shell` | Override interpreter (e.g., `"bash -c"`, `"node -e"`) |
| `hide` | Exclude from `mise tasks ls` |
| `raw` | Pass stdin/stdout/stderr directly (for interactive tasks) |
| `file` | Run an external script or remote URL instead of `run` |
| `confirm` | Prompt for confirmation before running |

---

## File tasks — standalone scripts

**The problem:** Complex tasks need real scripts with syntax highlighting, linting, and proper structure.

Place executable scripts in any of these directories:
- `.mise/tasks/`
- `mise/tasks/`
- `mise-tasks/`
- `.mise-tasks/`
- `.config/mise/tasks/`

Configure via special comments at the top:

```bash
#!/usr/bin/env bash
#MISE description="Deploy to staging"
#MISE alias="d"
#MISE depends=["build", "test"]
#MISE sources=["src/**/*.rs", "Cargo.toml"]
#MISE outputs=["target/release/myapp"]
#MISE env={DATABASE_URL = "postgres://localhost/staging"}
#MISE dir="{{cwd}}"

cargo build --release
scp target/release/myapp staging:/opt/myapp/
```

**Subdirectories create namespaced tasks:**

```
.mise/tasks/
  build           -> mise run build
  test/
    _default      -> mise run test
    integration   -> mise run test:integration
    unit          -> mise run test:unit
```

**Any language works** — the shebang determines the interpreter:

```python
#!/usr/bin/env python
#MISE description="Generate API docs"
#MISE sources=["src/**/*.py"]

import subprocess
subprocess.run(["pdoc", "--html", "src/"])
```

```javascript
#!/usr/bin/env node
//MISE description="Seed the database"

const { seedDB } = require('./scripts/seed');
seedDB().then(() => console.log('Done'));
```

**Verdict:** File tasks are better for anything over ~3 lines. Use TOML for simple one-liners.

---

## Task arguments — the `usage` spec

**The problem:** Tasks need flags and positional args with validation and shell completion.

### TOML tasks

```toml
[tasks.deploy]
description = "Deploy to environment"
usage = '''
arg "<env>" help="Target environment (staging|prod)"
flag "-f --force" help="Skip confirmation"
flag "-t --tag <tag>" help="Docker tag to deploy" default="latest"
'''
run = '''
#!/usr/bin/env bash
if [ "$usage_force" != "true" ]; then
  read -p "Deploy $usage_tag to $usage_env? [y/N] " -n 1 -r
  echo
  [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
fi
echo "Deploying $usage_tag to $usage_env..."
'''
```

### File tasks

```bash
#!/usr/bin/env bash
#MISE description="Run migrations"
#USAGE arg "<direction>" help="up or down"
#USAGE flag "-n --count <count>" help="Number of migrations" default="1"
#USAGE flag "-v --verbose" help="Show SQL"

if [ "${usage_verbose:-false}" = "true" ]; then
  set -x
fi
migrate "$usage_direction" --count "$usage_count"
```

**How it works:**
- Arguments become environment variables prefixed with `usage_`
- Flags: `usage_force` = `"true"` or `"false"`
- Options: `usage_tag` = the value passed
- Positional: `usage_env` = the argument value
- Shell completion works automatically from usage specs

```bash
mise run deploy staging --tag v2.1.0 --force
```

---

## Dependencies and execution order

**The problem:** Tasks have prerequisites that should run (in parallel when possible) before the main task.

```toml
[tasks.ci]
depends = ["lint", "test", "typecheck"]  # all 3 run in parallel
run = "echo 'CI passed'"

[tasks.release]
depends = ["ci"]                          # ci (and its deps) must pass first
depends_post = ["notify-slack"]           # runs after release completes
run = "goreleaser release"

[tasks.notify-slack]
run = "curl -X POST $SLACK_WEBHOOK ..."
```

- `depends` — must complete successfully before this task starts. Failed dependency = task doesn't run.
- `depends_post` — runs after the task finishes. Like cleanup or notifications.
- `wait_for` — doesn't trigger the other task, but if it's already running (e.g., from another dependency chain), wait for it to finish before proceeding. Avoids duplicate runs.

**Parallel by default.** Multiple dependencies run concurrently. Control with `--jobs`:

```bash
mise run ci --jobs 2    # limit to 2 parallel tasks
```

---

## Sources and outputs — skip if unchanged

**The problem:** Rebuilding every time is slow. Only re-run when inputs actually changed.

```toml
[tasks.build]
sources = ["Cargo.toml", "src/**/*.rs"]
outputs = ["target/release/myapp"]
run = "cargo build --release"

[tasks.bundle-css]
sources = ["styles/**/*.scss"]
outputs = ["dist/bundle.css"]
run = "sass styles/main.scss dist/bundle.css"
```

**Behavior:**
- If all `outputs` exist and are newer than all `sources`, the task is skipped
- `mise run --force build` overrides the check
- `sources` alone (without `outputs`) still works — used by `mise watch` to know which files to monitor

---

## `mise run` — the executor

**Alias:** `mise r`

```bash
mise run build                         # single task
mise run lint ::: test ::: typecheck   # parallel tasks (separated by :::)
mise run test -- --verbose             # pass args to task
mise run deploy staging --force        # args defined by usage spec

mise run --dry-run ci                  # show execution order without running
mise run --force build                 # ignore source/output freshness
mise run --raw test                    # passthrough stdin/stdout (interactive)
mise run --jobs 1 ci                   # serial execution

mise run --output prefix ci            # prefix output lines with task name
mise run --output interleave ci        # raw interleaved output
mise run --output keep-order ci        # preserve output order per task
```

**Key flags:**

| Flag | Purpose |
|---|---|
| `-f, --force` | Run even if outputs are fresh |
| `-n, --dry-run` | Print execution plan, don't run |
| `-j, --jobs <N>` | Max parallel tasks (default: 4) |
| `-r, --raw` | Direct stdin/stdout passthrough |
| `-o, --output <MODE>` | `prefix`, `interleave`, `keep-order`, `quiet`, `silent` |
| `--skip-deps` | Run only the named task, skip dependencies |
| `--timeout <DURATION>` | Kill task after duration |
| `-q, --quiet` | Suppress extra output |
| `-S, --silent` | Suppress all output except errors |

---

## `mise watch` — rebuild on file changes

**The problem:** You want a dev loop that re-runs tasks when source files change.

Requires `watchexec` installed (`mise use -g watchexec` or `brew install watchexec`).

```bash
mise watch build                         # re-run build when sources change
mise watch test --watch src --exts rs    # override watch paths
mise watch serve --restart               # kill and restart on changes
mise watch lint ::: test                 # watch multiple tasks
```

**Sources from the task definition are used automatically** — if the task has `sources = ["src/**/*.rs"]`, that's what gets watched.

**Useful flags:**

| Flag | Purpose |
|---|---|
| `-w, --watch <PATH>` | Override watched paths |
| `-e, --exts <EXT>` | Filter by extension |
| `-r, --restart` | Kill running process and restart (for servers) |
| `-c, --clear` | Clear screen before each run |
| `-d, --debounce <MS>` | Wait before triggering (default: 50ms) |
| `-p, --postpone` | Don't run initially, wait for first change |
| `-N, --notify` | Desktop notification on completion |

---

## Task environment variables

**The problem:** Tasks need project-specific env vars, plus access to mise context.

### Setting env vars on tasks

```toml
[tasks.test]
env = { NODE_ENV = "test", LOG_LEVEL = "debug" }
run = "jest"
```

### Built-in variables available to all tasks

| Variable | Value |
|---|---|
| `MISE_ORIGINAL_CWD` | Directory where `mise run` was invoked |
| `MISE_CONFIG_ROOT` | Directory containing the `mise.toml` |
| `MISE_PROJECT_ROOT` | Project root directory |
| `MISE_TASK_NAME` | Name of the current task |
| `MISE_TASK_DIR` | Directory of the task script (file tasks) |
| `MISE_TASK_FILE` | Full path to the task script (file tasks) |

---

## Working directory (`dir`)

**The problem:** Tasks should run from a consistent directory regardless of where you invoke `mise run`.

- **Default:** The directory containing `mise.toml`
- **Override per task:** `dir = "frontend"` (relative to config) or `dir = "/absolute/path"`
- **Run from caller's directory:** `dir = "{{cwd}}"`

```toml
[tasks."frontend:build"]
dir = "frontend"
run = "npm run build"

[tasks."infra:deploy"]
dir = "{{cwd}}"  # respect where the user is standing
run = "terraform apply"
```

---

## Remote task files

**The problem:** Share task scripts across repos without copying them.

```toml
[tasks.shared-lint]
file = "https://example.com/scripts/lint.sh"

[tasks.shared-build]
file = "git::ssh://git@github.com/org/shared-tasks.git//build.sh?ref=v1.0.0"
```

Files are cached in `MISE_CACHE_DIR`. Set `MISE_TASK_REMOTE_NO_CACHE=1` to re-fetch every time.

---

## Generating task documentation

```bash
mise generate task-docs                            # print to stdout
mise generate task-docs --output TASKS.md          # write to file
mise generate task-docs --style detailed           # verbose format
mise generate task-docs --inject                   # inject between <!-- mise-tasks --> markers
mise generate task-docs --multi --output docs/     # one file per task
```

Useful for repos with many tasks — auto-generates a reference from descriptions and usage specs.

---

## Mise tasks vs Just vs Make

**The problem:** You already use Just. When does mise tasks make sense?

| I want to... | Use |
|---|---|
| Simple project commands (`build`, `test`, `lint`) | Either works. Just if already set up. |
| Tasks that skip when unchanged (source/output tracking) | **Mise tasks** — Just doesn't have this |
| File watcher dev loop | **Mise tasks** — `mise watch` built in |
| Complex argument parsing with completion | **Mise tasks** — usage spec with auto-completion |
| Polyglot task scripts (bash, python, node, etc.) | **Mise file tasks** — shebang-based, any language |
| Dependency graph with parallel execution | **Mise tasks** — parallel by default, dependency chains |
| Tasks that need specific tool versions | **Mise tasks** — `tools = {node = "20"}` in file tasks |
| Portable Makefile replacement everyone knows | **Just** — simpler syntax, widely known |
| Recipes with interactive prompts | **Just** — `choose`, `confirm` built-ins |
| Quick ad-hoc command aliases | **Just** — less ceremony for simple recipes |
| Bootstrap/setup scripts for your dotfiles | **Just** — no dependency on mise being installed yet |

**Verdict:** They complement each other. Just is great for simple command orchestration where everyone on the team already knows it. Mise tasks shine when you need source tracking, file watching, parallel dependency graphs, or polyglot scripts with typed arguments. If you already have mise for tool management, tasks are zero extra tooling. For dotfiles bootstrap (where mise may not be installed yet), stick with Just.

---

## Related

- [Environment](environment.md) — `[env]` section for task environment variables
- [CI & Bootstrap](ci-bootstrap.md) — `mise run` in CI pipelines
- [Security & Trust](security-trust.md) — trust implications of tasks
- [Mise documentation — tasks](https://mise.jdx.dev/tasks/) — official docs
