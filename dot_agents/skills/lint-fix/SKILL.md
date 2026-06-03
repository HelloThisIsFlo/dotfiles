---
name: lint-fix
description: "Run project linting, formatting, and type checking, then auto-fix all mechanical issues and present structural ones for user decision. Never suppresses warnings — always fixes root causes. Use this skill whenever the user mentions linting, formatting, type errors, code cleanup, preparing for commit, or finishing implementation work. Trigger on: 'lint', 'fix lint', 'lint-fix', 'clean up the code', 'run checks', 'fix errors', 'make it pass lint', or after implementing features/phases. Even if the user just says 'check the code' or 'is this clean?', use this skill."
---

# Lint Fix

Auto-fix mechanical lint/format/type issues. Escalate structural ones. Never suppress.

## Core Principle

**Fix root causes, never suppress.** No `# noqa`, `# type: ignore`, `# pragma: no cover`, or per-file-ignores without explicit user approval. If the only remaining option is suppression, explain why and ask.

## Workflow

### 1. Detect Tooling

Check for project tooling in this order:

1. **Makefile / justfile** — look for `lint`, `typecheck`, `format`, `check`, `test` targets
2. **pyproject.toml** — detect configured tools (ruff, mypy, black, isort, flake8, pyright)
3. **package.json** — for JS/TS projects (eslint, prettier, tsc)
4. **Direct availability** — fall back to installed tools

Build four commands:
- **Lint**: `make lint` / `ruff check` / `eslint`
- **Format**: `ruff format` / `black` / `prettier` (often bundled into lint target)
- **Typecheck**: `make typecheck` / `mypy` / `pyright` / `tsc`
- **Test**: `make test` / `pytest` / `jest`

Use project runner where available (`uv run`, `npx`, `poetry run`, etc.).

### 2. Run Diagnostics

Run lint + typecheck, capture full output. If everything passes → report success, stop.

### 3. Auto-Fix Pass

Run the project's auto-fixers directly (not via make targets, which typically run in check-only mode):

```bash
# Python (ruff)
ruff check --fix <source-dirs>
ruff format <source-dirs>

# Python (black + isort, if no ruff)
isort <source-dirs>
black <source-dirs>

# JS/TS
eslint --fix <source-dirs>
prettier --write <source-dirs>
```

Re-run diagnostics. If clean → skip to Step 6.

### 4. Fix Remaining Mechanical Issues

For violations surviving auto-fix, apply manual fixes when they are **deterministic and behavior-preserving**:

- **Import organization** (TC001-TC004): Move imports in/out of `if TYPE_CHECKING` as the linter directs
- **Mutable class defaults** (RUF012): `field: list[X] = []` → `Field(default_factory=list)`
- **Line length** (E501): Wrap long lines sensibly
- **Unused code** (F401, F841): Remove unused imports and variables
- **Type annotations**: Add missing return types, fix annotation syntax
- **Syntax modernization**: f-strings, `X | Y` union syntax, etc.
- **Deferred imports** (PLC0415): Hoist to top-level when safe

**Re-run diagnostics after each batch.** This catches cascading issues (e.g., moving an import reveals a new unused import).

#### When a fix backfires

If hoisting a deferred import to top-level causes:
- **ImportError** (circular dependency) → revert, escalate in Step 5
- **Test failure** (e.g., monkeypatch needs to intercept before binding) → revert, escalate in Step 5

Don't guess at structural fixes. Revert cleanly and ask.

### 5. Escalate Structural Issues

Group all remaining issues and present them together. For each:

1. **What**: Rule code + plain English explanation
2. **Why**: Root cause in this specific code
3. **Options**: Possible fixes with trade-offs
4. **Recommendation**: Your suggested approach

**Always escalate — never auto-fix:**
- Circular dependency resolution (moving code between modules)
- Any suppression (`# noqa`, `# type: ignore`, per-file-ignores)
- Linter config changes (e.g., `runtime-evaluated-base-classes`, new rule selections)
- Changes to module public API or re-exports
- Anything that changes runtime behavior

Wait for user decisions before proceeding. The user may want to discuss, defer, or take a different approach entirely.

### 6. Final Verification

Run full checks in order:
1. **Lint** — must pass
2. **Typecheck** — must pass
3. **Tests** — run full suite, report pass/fail count and any failures

Report summary: what was fixed, what was escalated (and user's decisions), final status. Do not commit — leave that to the user.

## Guardrails

- **Only touch files with violations.** No drive-by cleanups, no formatting changes to untouched files, no "while I'm here" improvements.
- **Explain unfamiliar rules.** When reporting issues to the user, always say what the rule means in plain English. Not everyone has the rule catalog memorized. E.g., "TC001 means this import is only used in type annotations and can move behind `if TYPE_CHECKING` to avoid loading the module at runtime."
- **Don't loop forever.** If a fix introduces new violations that need more fixes: stop after 3 rounds and escalate what remains.
- **Preserve existing suppressions.** Don't remove or question existing `# noqa` / per-file-ignores unless the user specifically asks for a suppression review.

## Common Patterns

### Pydantic + TYPE_CHECKING (Python)

When TC001/TC003 flags an import used in a Pydantic model's field annotations: the import **must stay at runtime** because Pydantic evaluates annotations for validation/serialization. The correct fix is adding the model's base class to `runtime-evaluated-base-classes` in ruff config — not moving the import behind `if TYPE_CHECKING` (which would cause runtime NameError). This is a config change → escalate.

### Legitimate Deferred Imports (Python)

PLC0415 (non-top-level import) has valid uses that should be preserved, not "fixed":
- **Monkeypatch patterns**: Tests using `monkeypatch.setattr` on a module attribute need the target to NOT have the name bound at import time
- **Import-is-the-test**: Smoke tests where the `import` statement itself is what's being verified
- **Intentional lazy loading**: Performance-critical paths that defer heavy imports

If a PLC0415 suppression already exists with a comment explaining why, leave it alone.
