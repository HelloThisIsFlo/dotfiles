---
name: Contracts are pure data, model_serializer is the real risk
description: Contracts/ has zero serializers. @field_serializer is allowed in models/ as a documented workaround. @model_serializer is the actual risk — it erases JSON Schema under nested serialization.
type: feedback
originSessionId: 9b91e88b-09ed-44da-b760-d2105ab6088b
---
Two rules, often conflated:

**Rule 1 — Contracts are pure data.** The `contracts/` package holds zero serializers. Only field definitions, types, defaults, and `@field_validator` (which guards shape, not transforms it). Transformation logic belongs in the layer that **consumes** the contract — `server/projection/` for agent-facing stripping, `repository/` for bridge payloads, `service/` for spec→core conversion.

**Rule 2 — `@model_serializer` is the real danger, `@field_serializer` is not universally banned.**

- `@model_serializer` on a model replaces Pydantic's entire serialization pipeline. When that model is nested inside another model, Pydantic v2's Rust serializer invokes the internal path directly and **the JSON Schema erases**: `TypeAdapter(X).json_schema(mode="serialization")` goes from structured properties to `{"type": "object", "additionalProperties": true}`. FastMCP advertises that schema to MCP clients → every discriminated union breaks for every client. This is intrinsic to `@model_serializer` returning `dict[str, Any]`, not a Pydantic bug — there's nothing for Pydantic to build a schema from.
- `@field_serializer` on a parent's field is different — it post-processes the child's already-serialized output without touching the child's schema. Safe.

**Live state of the codebase (verify before citing):**

- `@model_serializer`: zero call sites anywhere. None in contracts, none in models.
- `@field_serializer`: two legitimate uses, both in `models/`:
  - `models/repetition_rule.py` → `@field_serializer("frequency")` to suppress `interval=1` default
  - `models/task.py` → `@field_serializer("parent")` to normalize the `ParentRef` union via `model_dump(exclude_none=True, by_alias=True)`
- `docs/model-taxonomy.md` documents `@field_serializer` as an allowed workaround when `pydantic_core.to_jsonable_python` can't be passed `exclude_defaults`. The principled alternative is a separate `<noun>Read` model.

**Guard in place:** `TestUnionRegressionGuard.test_no_erased_union_in_tool_schemas` in `tests/test_output_schema.py` — fires if any `$defs` entry degrades to the erased form. That's what protects us when someone re-introduces a problematic serializer.

**How to apply:**
- Writing a contract model? No serializers, only validators.
- Writing a model in `models/`? `@field_serializer` is fine if you have a real reason (default suppression, union normalization). Prefer a `<noun>Read` variant when possible (see `docs/model-taxonomy.md`).
- Tempted to add `@model_serializer`? Don't, unless you've verified `TestUnionRegressionGuard` still passes AND you understand the nested-serialization failure mode. Consider handler-level stripping (`server/projection.py`) instead.
