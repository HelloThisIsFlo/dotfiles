# Remove the legacy home-directory CLAUDE.md.
#
# Claude Code loads ~/CLAUDE.md as an ancestor instruction for projects under
# $HOME. That makes a home-only file leak into unrelated repos and personal
# admin sessions.
#
# Shared global guidance now lives in ~/.agents/AGENTS.md, with
# ~/.claude/CLAUDE.md as a symlink adapter to that shared file. Home-specific
# behavior is handled as a conditional rule inside the shared AGENTS.md:
# when cwd is exactly $HOME, treat it as a personal admin shell.
