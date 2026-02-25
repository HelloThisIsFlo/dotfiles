# Chezmoi Assistant Skill — Rationale & Spec

## Why this exists

Chezmoi has a learning curve not in the commands themselves but in knowing *which* command to run *when*. The day-to-day workflow has enough moving parts that it's easy to forget a step — especially when juggling multiple things and coming back to a messy repo days later. A Claude Code skill that understands the chezmoi model and my specific setup means I can say "what's the state of things?" or "help me clean this up" instead of remembering the exact triage sequence.

## The target-authoritative files problem

Chezmoi's model is source → target: the source directory is truth, `chezmoi apply` overwrites the target. But some directories in my repo have the opposite flow:

- **`~/.claude/` directory** — contains skills I edit directly at the destination (not through `chezmoi edit`), plus config files that the Claude terminal UI auto-updates when I change preferences. The target is the authoritative copy, not the source.

For these files, running `chezmoi apply` without first running `chezmoi re-add` silently reverts my changes. There's no confirmation prompt, no safety net. `chezmoi diff` shows the divergence but doesn't tell you *which side* changed — you have to interpret the diff yourself.

The workflow is: `chezmoi re-add ~/.claude/` to sync target → source, *then* `chezmoi apply`. `re-add` is safe here because these are plain files, not templates (re-add on `.tmpl` files destroys the template logic). But remembering to do this every time, and knowing which files need it, is exactly the kind of thing an agent should handle.

More directories like this may appear over time — any tool that writes its own config at the destination rather than being configured through chezmoi's source.

## What the skill should do

**Health check / triage:** Run `chezmoi status` and `chezmoi diff`, then classify each change:
- "apply" — source changed, target needs updating
- "re-add" — target changed (target-authoritative file modified externally)
- "conflict" — both sides changed, needs manual resolution

Present a clear summary so I can see the full picture at a glance.

**Safety enforcement:** Before any `chezmoi apply`, always re-add target-authoritative files first. Warn if apply would overwrite local changes that haven't been re-added.

**Semantic commits:** After triage, help group related changes into meaningful git commits instead of one big "update dotfiles" commit. Things like "update shell aliases", "add new Claude skill", "sync macOS defaults".

**File flow awareness:** Know which directories are source-authoritative (most config) vs target-authoritative (`~/.claude/`, and anything else added later). This could be encoded as a simple manifest file in the repo — something like `.chezmoi-workflow.yaml` — or just hardcoded in the skill initially.

## Why a skill, not an MCP server

The initial instinct was to build an MCP server so this could work from any chat agent (Claude.ai, other UIs). We decided against it:

- Claude Code already has full shell access — it can run every chezmoi and git command natively. The value isn't in wrapping shell commands behind tool schemas; it's in the *knowledge* of when and how to use them.
- An MCP server is significantly more work: tool schema definitions, process execution, state management, running as a service, maintenance.
- A skill encodes the same knowledge with a fraction of the effort.
- If the skill proves valuable and I genuinely want it outside Claude Code, the skill becomes the spec for an MCP server. But there's a 99% chance the skill is enough.

## When to build this

After the core chezmoi setup is working (Phases 1–3 in the next actions list). The skill needs a real repo with real files to be useful — building it against a half-set-up repo would just encode workarounds for incomplete config.
