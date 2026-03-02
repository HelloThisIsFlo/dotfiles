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

## v1.2 Carry-Forward — COMPLETED

Tech debt items from v1.1 audit resolved in Phase 10 (2026-03-02).

## v1.2 Key Design Decisions (Phase 11 discussion)

- **Children are independent**: own label, contact_group, destination_mailbox derived from name
- **Parent relationship = additive only**: additive contact groups + additive mailbox filing
- **Additive contact groups**: sender added to child + all ancestor groups (enables simple 1:1 sieve rules)
- **Additive mailbox filing**: emails filed to child + all ancestor destinations (mailboxes are labels in Fastmail)
- **add_to_inbox**: per-category flag, NEVER inherited through parent chain
- **add_to_inbox = Screener-only**: only adds Inbox label to emails from Screener at triage time; re-triage does NOT re-add Inbox
- **destination_mailbox: Inbox banned**: use add_to_inbox instead (CFG-02)
- **Already-grouped check deprecated**: replaced by group change feature in Phase 13
- **New defaults include**: Billboard (parent: Paper Trail), Truck (parent: Paper Trail)
- **Full workflow docs**: see `docs/WIP.md` — to be finalized at end of v1.2

## Key Patterns

- Conflict detection: same sender + different triage labels → @MailroomError (additive)
- Already-grouped detection: DEPRECATED in v1.2 (replaced by re-triage)
- Retry safety: triage label removed LAST, so failures auto-retry next poll
- Display names: extracted from JMAP From header, propagated to CardDAV contacts
