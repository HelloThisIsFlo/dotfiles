---
name: HA config is already under version control (don't propose migration)
description: Flo's HA config is fully mirrored to github.com/HelloThisIsFlo/TheHome-HA by the HA Version Control add-on (~15 min cadence). Don't propose YAML migration, packages split, or CI — it's already solved.
type: feedback
originSessionId: cf35004c-c30e-4cd5-a1c9-4bf203cdccab
---
Flo's Home Assistant config is **already under version control** via the "Home Assistant Version Control" add-on running inside HA. It mirrors the full HA config directory to a GitHub repo on a ~15-minute cadence, one commit per changed file.

- **Repo:** https://github.com/HelloThisIsFlo/TheHome-HA
- **Tracked:** `.storage/`, `automations.yaml`, `scripts.yaml`, `scenes.yaml`, `configuration.yaml`, `blueprints/`, `custom_components/`, `esphome/`, `zigbee2mqtt/`, `addons_config/`, `sandbox.yaml`
- **Commit pattern:** auto-commits per file, commit message = filename (e.g., `"automations.yaml"`, `".storage/core.device_registry"`), plus occasional `"Re-apply .gitignore rules"` maintenance commits.
- **All 35 current automations** are serialized to `automations.yaml` as YAML (default HA behavior for UI-created automations — "UI-created" does not mean "not YAML").
- Changes made via the UI OR via MCP (e.g., `ha_config_set_automation`, `ha_config_remove_automation`) both land in `automations.yaml` and get mirrored to git automatically.

**Why (don't propose these things):**
- Wholesale migration from UI to YAML → already serialized as YAML.
- Splitting `automations.yaml` into `packages/` → Flo explicitly doesn't care, and UI editing still works with the single-file layout.
- Pre-commit / CI validation → Flo explicitly doesn't care. The add-on commits *after* HA has already accepted the change, so CI isn't catching pre-production breakage anyway.

**How to apply:**
- When Flo (or I) change an automation/script/scene via the UI or MCP, the change ends up in the HA VC repo on the next cycle. No manual push step needed.
- Recovery from a bad change = look up the commit in the HA VC repo and either manually revert in HA UI or (rarely) restore from an HA backup.
- Don't confuse the two git repos: `TheHome` is Flo's home lab infra-as-code repo (where we store research docs and todos); `TheHome-HA` is the HA VC add-on's mirror of his HA config. Different purposes, different source-of-truth relationships.
- Flo still prefers the UI as his primary authoring surface for iteration speed. Don't push him toward IDE-based YAML editing — the VC add-on gives him the audit trail without changing his workflow.
