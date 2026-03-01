# OmniFocus MCP Server - Memory

## Project Overview
MCP server for AI assistants to interact with OmniFocus on macOS via AppleScript/JXA. Published as `omnifocus-mcp` on npm. v1.5.0.

## Build & Run
- `npm run build` — tsc + copy OmniJS scripts + chmod
- `npm start` — node dist/server.js
- `npm run dev` — tsc watch mode
- TypeScript is installed globally on this machine
- No test framework set up yet (Vitest planned — see Next-Steps.md)

## Architecture
- **Two-layer tool pattern**: `tools/definitions/` (Zod schemas, MCP response formatting) → `tools/primitives/` (business logic, AppleScript generation)
- **11 tools**: query_omnifocus, dump_database, add_omnifocus_task, add_project, edit_item, remove_item, batch_add_items, batch_remove_items, list_perspectives, get_perspective_view, list_tags
- Each primitive has a `generateAppleScript()` function that builds the script as a string
- Scripts executed via temp files (`osascript ${tempFile}`) — except removeItem and addProject which still use `osascript -e` (known bug)

## Key Files
- `src/server.ts` — MCP server init, tool registration
- `src/types.ts` — OmniJS enum mappings
- `src/omnifocustypes.ts` — TypeScript interfaces for OF objects
- `src/utils/scriptExecution.ts` — executeJXA() and executeOmniFocusScript()
- `src/utils/dateFormatting.ts` — AppleScript date workarounds (dates must be constructed outside tell blocks)
- `src/utils/cacheManager.ts` — Singleton LRU cache (5min TTL, 50MB max)
- `src/utils/omnifocusScripts/*.js` — OmniJS scripts (plain JS, NOT TypeScript, run inside OmniFocus)
- `cli.cjs` — npm binary entry point

## Known Bug: Quote Escaping (documented in Next-Steps.md)
AppleScript return values build JSON via string concatenation without escaping special chars. Task names with `"` break JSON.parse(). Affects editItem, removeItem, addOmniFocusTask, addProject. Also queryOmnifocus interpolates filter values into JXA without escaping. Full details and fix plan in `/Users/flo/Work/Private/Dev/MCP/OmniFocus-MCP/Next-Steps.md`.

## Conventions
- ESM modules throughout (`"type": "module"`)
- Strict TypeScript, ES2022 target
- Zod for parameter validation
- Minimal deps: only @modelcontextprotocol/sdk and zod in production
- Error pattern: primitives return `{success, error?, ...}`, definitions wrap in MCP format
- AppleScript string escaping: `.replace(/["\\]/g, '\\$&')` for input side (search/create)
- `my handlerName()` to call script-level handlers from within `tell` blocks

## Fork Workflow
- This is a fork of `themotionmachine/omnifocus-mcp-server`
- Remote `upstream` = original repo, `origin` = user's fork
- User's fork `main` will include a test harness the upstream doesn't have
- For upstream PRs: branch off `upstream/main`, cherry-pick only source commits (not test commits)
- Keep test commits and source commits separate for clean cherry-picking
- Full workflow documented in `CONTRIBUTING-WORKFLOW.md`

## Planned Work (see Next-Steps.md)
- **Phase 1**: Add Vitest + comprehensive tests covering the whole project (separate session)
- **Phase 2**: Fix quote escaping bug (separate session, after tests are in place)
- Changes were prototyped in this session then reset — Next-Steps.md has the full fix plan

## User Preferences
- Python developer, not familiar with TypeScript ecosystem
- Prefers understanding before running global installs
- Wants tests before bug fixes (test-first approach)
- Values community best practices (Vitest over Jest for modern TS)
- Prefers clear explanations of tooling before executing (e.g., what npm install does)
- Wants reference docs in the project for workflows they might forget
