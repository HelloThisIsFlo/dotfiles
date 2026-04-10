---
name: Pre-release — no backward compatibility
description: Project is unreleased with one user; "breaking changes" are just cleanups, no migration concern
type: project
---

OmniFocus Operator is pre-release. Flo is the only user in the world. No agents have ever used any version of the API.

**Why:** There are zero backward compatibility concerns. The milestone spec frames some changes as "breaking changes" (BREAK-01 through BREAK-08) but this framing is misleading — these are just cleanups and new features.

**How to apply:** Never spend time on migration paths, backward compat shims, educational errors for "old" input forms, or interception of deprecated fields. Just make the change directly. If an enum member is being removed, remove it — don't add a migration error. If a field type changed, it changed — agents will see the current schema.
