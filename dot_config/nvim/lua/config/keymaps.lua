-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua


-- macOS-native Option+Backspace in insert mode
-- See deep dive: .research/2026-03-25/opt-backspace-binding-research--fish-vi-etc.md
vim.keymap.set("i", "<M-BS>", "<C-w>", { desc = "Delete word backward" })

-- macOS-native Option+Arrow word movement in insert mode
vim.keymap.set("i", "<M-b>", "<C-o>b", { desc = "Move word backward" })
vim.keymap.set("i", "<M-f>", "<C-o>w", { desc = "Move word forward" })

-- Emacs-style line navigation in insert mode (overrides niche defaults: Ctrl+A = re-insert previous, Ctrl+E = copy char from below)
vim.keymap.set("i", "<C-a>", "<Home>", { desc = "Beginning of line" })
vim.keymap.set("i", "<C-e>", "<End>", { desc = "End of line" })
