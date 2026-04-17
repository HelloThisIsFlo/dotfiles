---
name: DadHome is a separate HA instance
description: The `dadhome-*` entities in Flo's HA are just Tailscale device trackers — DadHome is a separate, larger HA instance, not a unification target.
type: project
originSessionId: cf35004c-c30e-4cd5-a1c9-4bf203cdccab
---
DadHome (Flo's parents' house) is a **fully separate Home Assistant instance**:
- 3-floor house with heavy sensor coverage
- Running 5-6 years
- Significantly bigger than Flo's "TheHome" HA
- Its own project, separately maintained

The `dadhome-haos`, `dadhome-ubuntuvm`, `dadhome-plex` etc. sensors that appear in Flo's HA are **incidental**: they're just Tailscale-tracked devices showing up because the two sites share a Tailscale network.

**Why:** avoid suggesting "cross-site one home" unification or merging DadHome into TheHome's HA. That framing misreads the setup and undervalues DadHome as a separate, mature project.

**How to apply:** when touching presence, backups, or cross-site scenarios, treat the two HA instances as peer systems, not candidates for unification. If federation ever comes up, it should preserve DadHome's independence (e.g., remote-HA integration, not absorption).
