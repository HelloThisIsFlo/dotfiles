-- macOS-native Option+Backspace in picker input
-- Mirrors the keymaps.lua binding but for the Snacks picker,
-- which has its own keymap layer (global insert-mode maps don't reach it).
-- Uses the same <c-s-w> trick Snacks uses for <C-w> (avoids the <c-w> prefix conflict).
return {
  "folke/snacks.nvim",
  opts = {
    picker = {
      win = {
        input = {
          keys = {
            ["<M-BS>"] = { "<c-s-w>", mode = { "i" }, expr = true, desc = "Delete word backward" },
          },
        },
      },
    },
  },
}
