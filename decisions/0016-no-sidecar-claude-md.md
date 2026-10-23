# Decision 0016: Development sidecars drop CLAUDE.md

**Status**: Accepted
**Date**: 2026-10-23
**Approver**: Stefan Jansen

## Context

Decision 0014 kept a one-line `CLAUDE.md` containing `@AGENTS.md` in each private development
sidecar so Claude Code would load the canonical instructions. Claude Code now reads `AGENTS.md`
natively when no `CLAUDE.md` is present. The include file only duplicates that behavior, and any
`CLAUDE.md`, including a stray local one, takes precedence over the native reading.

## Decision

No sidecar tracks `CLAUDE.md`. The workspace audit replaces `sidecar.file.CLAUDE.md`, which
required the exact include, with `sidecar.no-claude-md`, which fails when a sidecar contains a
`CLAUDE.md`. Public repositories continue not to track one. This supersedes the sidecar sentence
of decision 0014; the rest of 0014 stands.

## Consequences

Each sidecar has one instruction file that both Claude Code and Codex read. The sidecar include
files were removed on 2026-10-23, so the audit passes without further changes to the sidecars.
