---
name: Hooks dispatcher architecture
description: Chezmoi hooks use a folder-based dispatcher pattern — one dispatcher script routes to numbered scripts per event directory. Decided 2026-03-20.
type: project
---

Chezmoi only supports one hook per event. To allow multiple hooks per event, we use a dispatcher pattern.

**Structure:**
```
.hooks/
├── run-hooks.sh                    ← dispatcher (~5 lines, runs all *.sh in a subdirectory)
├── read-source-state.pre/
│   └── 01-ensure-password-manager.sh
├── apply.pre/
│   └── 01-watch-dirs.sh
└── status.pre/
    └── 01-watch-dirs.sh
```

**Config pattern:**
```toml
[hooks.<event>.<phase>]
command = ".local/share/chezmoi/.hooks/run-hooks.sh"
args = ["<event>.<phase>"]
```

**Why:** Chezmoi allows only one `command` per hook event. A dispatcher script that runs all scripts in a named subdirectory gives us unlimited hooks per event. Numbered prefixes (01-, 02-) control execution order. Adding a new hook = drop a script in the right folder.

**How to apply:** When adding any new chezmoi hook, create a numbered script in the appropriate `.hooks/<event>/` subdirectory. Never put hook logic directly in the config — always go through the dispatcher.
