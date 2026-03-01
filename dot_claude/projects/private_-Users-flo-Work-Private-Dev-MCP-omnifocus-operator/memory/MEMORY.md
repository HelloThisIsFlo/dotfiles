# OmniFocus Operator — Project Memory

## Current State
- GSD project initialized (2026-03-01)
- Milestone 1 (Foundation) scoped: 8 phases, 35 requirements
- No implementation yet — ready for `/gsd:discuss-phase 1`

## Key Decisions
- Repo: https://github.com/HelloThisIsFlo/omnifocus-operator (public)
- Python 3.12, uv, single runtime dep: `mcp>=1.26.0`
- Use official SDK's built-in FastMCP (`mcp.server.fastmcp`), NOT standalone `fastmcp` package
- Workflow-agnostic server — workflow logic lives in the agent, not the server
- Bridge script is "proven direction, not literal copy-paste" — direction is fixed, implementation can improve

## Critical Safety Rule
- **SAFE-01/02**: No automated test or agent touches RealBridge. All automated testing uses InMemoryBridge or SimulatorBridge. RealBridge = manual UAT only.

## GSD Config
- Mode: Interactive | Depth: Comprehensive | Parallel: Yes | Git tracking: Yes
- All workflow agents enabled (research, plan check, verifier)
- Model profile: Quality (Opus for research/roadmap)

## Research Highlights
- `os.replace()` not `os.rename()` for atomic writes on macOS
- All async file I/O via `asyncio.to_thread()` or anyio to avoid blocking event loop
- URL scheme trigger is fire-and-forget — no delivery guarantee
- Use `st_mtime_ns` (nanoseconds) for cache freshness, not `st_mtime` (float)
- 3 competing OmniFocus MCP servers exist — all use sync AppleScript/JXA. Our snapshot + pluggable bridge is the differentiator.
