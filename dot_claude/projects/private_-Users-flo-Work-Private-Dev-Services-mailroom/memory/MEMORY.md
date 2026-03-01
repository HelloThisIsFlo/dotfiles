# Mailroom Project Memory

## Human Integration Tests (IMPORTANT)

The user considers `human-tests/` first-class citizens alongside unit tests. When doing UAT, planning, or verification:
- Always reference applicable human tests
- When adding workflow features, remind about adding/updating human tests
- Human tests run against real Fastmail — they are standalone scripts, not pytest
- See `CLAUDE.md` for the full test table

## Project Structure

- Fastmail email triage: JMAP (email) + CardDAV (contacts)
- ScreenerWorkflow.poll() is the main entry point
- Config via MAILROOM_ env vars (pydantic-settings)
- TDD with atomic commits (RED/GREEN/REFACTOR)
- Phases tracked in `.planning/phases/`

## Key Patterns

- Conflict detection: same sender + different triage labels → @MailroomError (additive)
- Already-grouped detection: contact in wrong group → @MailroomError
- Retry safety: triage label removed LAST, so failures auto-retry next poll
- Display names: extracted from JMAP From header, propagated to CardDAV contacts
