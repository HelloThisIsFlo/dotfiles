---
name: Contracts layer is pure data
description: No transformation logic (serializers, builders) in contracts/ — only field definitions and validators
type: feedback
---

Contracts are pure data carriers with optional validation. Never put `model_serializer` or domain translation logic in contracts.

**Why:** Contracts define *what* the data looks like at a boundary, not *how* to transform it. Putting RRULE serialization in a contract model mixes concerns — the layer that owns the transformation (repository for bridge-format, service for spec-to-core) should contain the logic, not the data definition layer.

**How to apply:** When you need custom serialization at a boundary, put the serialization function in the layer that consumes it (e.g., `repository/` for bridge serialization), not on the Pydantic model in `contracts/`. Model validators are fine in contracts (they guard data shape). Model serializers are not (they encode transformation knowledge).
