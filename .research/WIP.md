# Active Work In Progress

Last updated: 2026-07-13

These dirty paths are intentional WIP. Do not treat them as ready to commit unless Flo explicitly says so.

- `private_dot_tmux.conf` / `private_dot_tmux.conf.bak`
  - `private_dot_tmux.conf` is currently clean.
  - `private_dot_tmux.conf.bak` exists as a small TPM/resurrect reference.
  - Tmux remains WIP until the BAK file is reconciled, deleted, or intentionally onboarded.

- `.chezmoi.toml.tmpl`
  - Part of the declarative Time Machine policy package.
- `.chezmoidata/time-machine.yaml`
  - Time Machine inclusion and exclusion policy.
- `.chezmoiscripts/Z--AFTER/run_onchange_after_0012-MACOS-time-machine-policy.sh.tmpl`
  - Time Machine policy reconciliation script.
- `.research/MIGRATION.md`
  - Time Machine policy documentation and migration tracking.
  - The package looks structurally complete but has not been tested on the real machine.
  - Keep all four paths as WIP until the `plan`, `apply`, and `verify` flows have been exercised and Flo explicitly approves the result.

- `dot_config/nvim/lua/config/keymaps.lua`
  - Arrow-key remap experiment.
  - Needs formatting cleanup, final newline, and maybe `desc` fields before commit.

- `.research/cheatsheets/mise/tool-management.md`
  - Mise tool-management cheatsheet rewrite.
  - Treat as draft/reference material until Flo approves commit.

- `.research/cheatsheets/agents/codex-claude-instructions-cheatsheet.md`
  - Draft agents/Codex/Claude instruction-system cheatsheet.
  - Includes diagrams and public-facing explanation work; review before commit.

- `.research/cheatsheets/index.html`
  - Docsify Mermaid rendering support for cheatsheets.
  - Treat with the agents cheatsheet work; verify rendering before commit.

Agent handling:

- If these files are dirty, assume that is expected.
- Do not commit or clean them up while doing unrelated work.
- At the end of a repo session, briefly ask Flo whether to keep, update, or clear this list if it looks stale.
