# Decision 0007: Public workspace files

**Status**: Accepted
**Date**: 2026-09-08

## Decision

Public repositories do not track `.workspace/` content. Backtest, Specs, and Live fold the useful
package, architecture, safety, and quality-command material from `.workspace/shared-context.md` into
their root `AGENTS.md`, then delete the shared-context file and its include.

Public repositories ignore `CLAUDE.md`, `.claude/`, `.codex/`, and `.workspace/` so local agent state
cannot be published by a broad Git add.

## Consequences

Public orientation is self-contained and clone-safe. The shared Claude/Codex workspace convention
retains one meaning: private local state. Future public guides cannot depend on an ignored include.
