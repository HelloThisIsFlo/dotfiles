# NeoVim — LazyVim Configuration

You installed LazyVim and now you have a dozen files you didn't write. This explains what each one does, which ones matter, and how the layering system works — so you can customise with confidence instead of cargo-culting from the starter template.

---

## Quick reference

```
~/.config/nvim/
  init.lua                     # Don't touch — just loads lazy.lua
  lua/
    config/
      lazy.lua                 # Plugin manager settings, colorscheme, perf
      keymaps.lua              # Your keymaps (loaded on VeryLazy)
      options.lua              # Your vim.opt settings (loaded first)
      autocmds.lua             # Your autocommands (loaded on VeryLazy)
    plugins/
      *.lua                    # Drop any file — auto-loaded as plugin specs
  lazyvim.json                 # Extras toggle state (auto-managed)
  .neoconf.json                # LSP config (Lua server + NeoVim API)
  stylua.toml                  # Lua formatter: 2-space, 120 col
  .gitignore                   # Ignores temp files

LazyVim defaults:  ~/.local/share/nvim/lazy/LazyVim/
Plugin installs:   ~/.local/share/nvim/lazy/
```

---

## How the layering works

LazyVim follows the same pattern as fish's preset vs user bindings. There are two layers:

- **LazyVim defaults** — live inside the plugin itself (`~/.local/share/nvim/lazy/LazyVim/`). You never edit these.
- **Your overrides** — live in `~/.config/nvim/lua/config/` and `lua/plugins/`. These take priority.

When both layers define the same thing (a keymap, an option, a plugin config), yours wins. When you don't override something, you get LazyVim's sensible default. This means your config only contains the delta — what you've changed or added.

---

## File overview

| File | Purpose | Edit frequency |
|---|---|---|
| `init.lua` | Entry point — loads LazyVim | Never |
| `lua/config/lazy.lua` | Plugin manager bootstrap + settings | Rarely |
| `lua/config/keymaps.lua` | Your key mappings | Often |
| `lua/config/options.lua` | Your vim options (`set` equivalents) | Sometimes |
| `lua/config/autocmds.lua` | Your auto-triggered commands | Sometimes |
| `lua/plugins/*.lua` | Your plugin additions/overrides | Often |
| `lazyvim.json` | Tracks enabled LazyVim extras | Auto-managed |
| `.neoconf.json` | LSP server configuration | Rarely |
| `stylua.toml` | Lua formatter settings | Rarely |
| `.gitignore` | Ignores temp/debug files | Never |

---

## Entry point: `init.lua`

One line: `require("config.lazy")`. This bootstraps everything. Don't touch it.

---

## `lua/config/` — your personal settings

These files are loaded automatically by LazyVim at specific times. You don't need to `require` them anywhere.

### `lazy.lua` — plugin manager bootstrap

This is the only config file with real content out of the box. It:

- Downloads `lazy.nvim` (the plugin manager) if missing
- Loads LazyVim's default plugins + your `lua/plugins/` specs
- Sets the fallback colorscheme for first install
- Configures plugin update checking
- Disables some built-in vim plugins for performance (`gzip`, `tar`, `zip`, `tutor`)

Things you'd change here:

```lua
-- Change the fallback colorscheme (used on first install before plugins load)
install = { colorscheme = { "catppuccin", "habamax" } },

-- Disable background update checks if they annoy you
checker = {
  enabled = false,
},
```

### `keymaps.lua` — your key mappings

Loaded on the `VeryLazy` event (after UI is ready). This is where custom keybindings go. LazyVim's defaults are at [lazyvim/config/keymaps.lua](https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua).

```lua
-- macOS-native Option+Backspace in insert mode
vim.keymap.set("i", "<M-BS>", "<C-w>", { desc = "Delete word backward" })

-- macOS-native Option+Arrow word movement in insert mode
vim.keymap.set("i", "<M-b>", "<C-o>b", { desc = "Move word backward" })
vim.keymap.set("i", "<M-f>", "<C-o>w", { desc = "Move word forward" })
```

### `options.lua` — vim options

Loaded before `lazy.nvim` startup (earliest of all config files). This is the `set` equivalent in Lua.

```lua
-- Use the Lua API for vim options
vim.opt.scrolloff = 10          -- Keep 10 lines visible above/below cursor
vim.opt.ttimeoutlen = 50        -- Fast ESC sequence recognition (needed for Meta keys)
vim.opt.relativenumber = false  -- Override LazyVim's default relative line numbers
```

> **About load order.** Options load first, then lazy.lua bootstraps plugins, then keymaps and autocmds load on `VeryLazy`. This matters when an option needs to be set before a plugin reads it.

### `autocmds.lua` — auto-triggered commands

Loaded on `VeryLazy`. For things that should happen automatically in response to events.

```lua
-- Format fish files with fish_indent on save
vim.api.nvim_create_autocmd("BufWritePre", {
  pattern = "*.fish",
  callback = function()
    vim.lsp.buf.format()
  end,
})

-- Remove a LazyVim default you don't want (they're prefixed with lazyvim_)
vim.api.nvim_del_augroup_by_name("lazyvim_wrap_spell")
```

---

## `lua/plugins/` — your plugin specs

Every `.lua` file in this directory is automatically loaded by `lazy.nvim`. No imports needed — just drop a file and it's picked up.

### Adding a plugin

Create a new file (e.g., `lua/plugins/catppuccin.lua`):

```lua
return {
  -- Add the plugin
  { "catppuccin/nvim", name = "catppuccin" },

  -- Tell LazyVim to use it as the colorscheme
  {
    "LazyVim/LazyVim",
    opts = { colorscheme = "catppuccin" },
  },
}
```

### Overriding a LazyVim plugin's config

Reference the same plugin name and use `opts` to merge:

```lua
return {
  {
    "folke/trouble.nvim",
    opts = { use_diagnostic_signs = true },
  },
}
```

### Disabling a LazyVim plugin

```lua
return {
  { "folke/trouble.nvim", enabled = false },
}
```

### The `example.lua` file

This ships with the starter template. Line 3 is `if true then return {} end` — everything below is dead code. It's a reference showing patterns for adding plugins, overriding config, setting up LSP servers. Read it once for the patterns, then delete or replace it.

---

## Other root files

### `lazyvim.json`

Tracks which LazyVim extras you've enabled. Managed automatically by `:LazyExtras` — don't hand-edit it. Extras are curated plugin bundles for specific use cases (e.g., `lang.python`, `editor.leap`, `formatting.prettier`).

### `.neoconf.json`

Config for the [neoconf.nvim](https://github.com/folke/neoconf.nvim) plugin. The default enables the Lua language server with NeoVim API awareness — so you get autocomplete when editing your own NeoVim config files. Worth keeping even if you don't touch it.

### `stylua.toml`

Formatter config for [StyLua](https://github.com/JohnnyMorganz/StyLua): 2-space indentation, 120 char line width. Used by the formatter that Mason auto-installs. Change if you have different Lua style preferences.

### `.gitignore`

Ignores temp/debug files (`tt.*`, `foo.*`, `*.log`, `.tests`, `.repro`). Standard LazyVim starter content.

---

## What to track in version control

Track everything in `~/.config/nvim/` **except:**

| File | Why skip it |
|---|---|
| `lazy-lock.json` | Plugin version lockfile — regenerated on first sync |
| `LICENSE` | Leftover from the starter template, not your config |
| `README.md` | Same — starter template artifact |

---

## Key commands

| Command | What it does |
|---|---|
| `:Lazy` | Open the plugin manager UI — install, update, clean, profile |
| `:LazyExtras` | Browse and toggle LazyVim extras (updates `lazyvim.json`) |
| `:Mason` | Manage LSP servers, formatters, linters — install/update/remove |
| `:LazyHealth` | Diagnostic check for LazyVim |
| `:checkhealth` | NeoVim's built-in health checker (covers all plugins) |
