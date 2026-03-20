---
name: UNSET sentinel stays at service layer
description: UNSET filtering is agent-intent logic — belongs in service, never pushed to repos
type: feedback
---

UNSET sentinel resolution must happen at the service layer, not the repo layer.

**Why:** UNSET represents agent intent ("caller didn't mention this field"). Repos should receive clean, already-filtered payloads — they shouldn't need to understand agent intent. Pushing UNSET down would duplicate filtering across 3 repo implementations and violate the "repo as pass-through" principle.

**How to apply:** When building new use cases or refactoring the write pipeline, keep all UNSET → payload filtering in the service. RepoPayload models should never contain _Unset types. Repos use Pydantic's `exclude_unset=True` which relies on the service having already done the translation via `model_validate(only_changed_kwargs)`.
