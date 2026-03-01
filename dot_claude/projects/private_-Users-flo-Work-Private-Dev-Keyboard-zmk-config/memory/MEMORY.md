# ZMK Config Project Memory

## Project Quick Reference
- Corne (Chocofi) split keyboard, Nice Nano v2 controllers
- Custom ZMK fork: `https://github.com/HelloThisIsFlo/zmk`
- GitHub user: HelloThisIsFlo
- Active layout: **Naquadah** (46 Adaptive Keys, 0.082% SFB)
- Other layouts: Promethium, Rhodium (all three `#define`d in CONFIG.h; Naquadah wins via `#if defined` priority)

## Build
- Local: `../zmk/build_and_flash.sh left|right` (requires ZMK checkout at sibling dir)
- CI: GitHub Actions on push to `config/**`; download artifacts with `./flash.sh left|right`
- No tests — only validation is successful compilation
- `cp: directory /Volumes/NICENANO does not exist` is expected when keyboard not plugged in

## Key Architecture Decisions
- **No auto-formatting** — explicit decision, manual alignment in `.dtsi` files
- **Inclusion order matters** in `corne.keymap`: aliases → macros → behaviors → combos → layers
- **AKs are non-optional** — layouts designed around them
- Each AK gets its own layer (l_akA–l_akY), 23 total AK layers
- Layers 0–31 (uint32_t bitmask limit)

## File Navigation
- `config/CONFIG.h` — all timing constants + layout selection defines
- `config/corne.keymap` — orchestrator, strict include order
- `config/features/__BASE__/preprocessor_macros.c` — metaprogramming helpers (COMBO_*, LK, REPLACE_CHAR_WITH_BIGRAM, TYPING_MACRO)
- `config/features/__BASE__/aliases_key_positions.dtsi` — position naming: `{L|R}{T|M|B|H}{0-4}`
- `config/features/hands_down/adaptive_keys/` — core AK system
- `config/corne.conf` — ZMK hardware config (combo limits, BT power, sleep)
- `Analysis/Scripts/sfb.py` — SFB rate calculator

## Design Documents
- `Design/PHILOSOPHY.md` — living keyboard philosophy (read at session start, refine over time)
- `Design/PHILOSOPHY_LOG.md` — chronological philosophy/ergonomic decision log (append newest first)
- `Design/MECHANICS.md` — technical reference for how systems work under the hood (living, by topic)
- `Design/MECHANICS_LOG.md` — chronological technical/architectural decision log (append newest first)
- The `/layout` skill includes instructions for when/how to update these docs
- Documents are version-controlled in the repo, not ephemeral

## Build Environment
- Dev container: `devcontainer up --workspace-folder ../zmk` (or container may already be running)
- Flash pattern: `sleep 10 && ../zmk/build_and_flash.sh left` — gives user time to enter bootloader mode
- Bootloader: BIOS/cfg layer -> bottom-left pinky key; macOS may show USB permission popup first time

## Cursor Rules
- Extensive `.cursor/rules/` with 6 MDC files covering project overview, feature organization, AKs, build/test, ZMK syntax, layout-specific rules
- CLAUDE.md was created to capture the same knowledge

## User Preferences
- Commit style: short descriptive messages (see git log)
- Comfortable with direct pushes to main
- Prefers separate commits for unrelated changes
- Main work is iterating on bindings, not infrastructure — offer `/layout` skill at session start
- Likes collaborative brainstorming approach ("think together") rather than just executing changes
- Created `/layout` skill at `.claude/skills/layout-advisor/SKILL.md`
