#!/usr/bin/env fish

# -- GENERATED CONFIG ----
# To regenerate: run `tide configure`, and press `p` at the very end (instead of `y`)
tide configure --auto --style=Lean --prompt_colors='True color' --show_time=No --lean_prompt_height='Two lines' --prompt_connection=Dotted --prompt_connection_andor_frame_color=Dark --prompt_spacing=Sparse --icons='Many icons' --transient=No
# -- GENERATED CONFIG ----



# -- Right prompt items ---------
# Declared explicitly (not appended) so re-runs are idempotent.
# `clock` is added separately by 0024-FISH-configure-tide-clock.fish.
#
# To compare against tide defaults after a `tide configure`:
#   set -S tide_right_prompt_items
# Then diff against this list.
# Reset then append — each line is independently editable (reorder, comment out, etc.)
set -U tide_right_prompt_items

# Shell
set -a tide_right_prompt_items status
set -a tide_right_prompt_items cmd_duration
set -a tide_right_prompt_items context
set -a tide_right_prompt_items jobs
set -a tide_right_prompt_items direnv

# Languages & runtimes
set -a tide_right_prompt_items node
set -a tide_right_prompt_items bun
set -a tide_right_prompt_items python
set -a tide_right_prompt_items elixir
set -a tide_right_prompt_items ruby
set -a tide_right_prompt_items go
set -a tide_right_prompt_items rustc
set -a tide_right_prompt_items java
set -a tide_right_prompt_items php
set -a tide_right_prompt_items crystal
set -a tide_right_prompt_items zig

# Cloud & infra
set -a tide_right_prompt_items aws
set -a tide_right_prompt_items gcloud
set -a tide_right_prompt_items kubectl
set -a tide_right_prompt_items terraform
set -a tide_right_prompt_items pulumi
set -a tide_right_prompt_items nix_shell
set -a tide_right_prompt_items distrobox
set -a tide_right_prompt_items toolbox

# Status indicators
set -a tide_right_prompt_items private_mode
set -a tide_right_prompt_items shlvl