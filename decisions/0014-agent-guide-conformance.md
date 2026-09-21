# Decision 0014: Agent guide conformance

**Status**: Accepted
**Date**: 2026-09-20

## Context

Decisions 0005 through 0009 established public root orientation, private sidecar plumbing, the ban
on public workspace state, the public ecosystem boundary, and optional development sidecars. The
release standard still contained one contradictory sidecar requirement, and the executable audit
checked only a root guide's word count and a few substrings. It could not discover stale nested
guides or volatile inventories.

## Decision

Adopt `docs/standards/agent-guides.md` as the public reference. Root guides describe the library,
source layout, public surface, change constraints, and current quality commands in no more than 200
lines. Nested guides are optional, directory-specific, and no more than 120 lines. Public guides do
not contain private state, agent-tool setup, volatile counts, or current work.

The workspace audit discovers tracked root and nested guides. It does not require empty discovery
files. Structural checks supplement, but do not replace, a library-level semantic review against
the package, documentation, and workflows.

Public repositories do not track `CLAUDE.md`. Private sidecars keep `AGENTS.md` as the source of
truth and a one-line `CLAUDE.md` import for interoperability.

## Consequences

Changes to package boundaries, public imports, repository layout, quality commands, release rules,
or subsystem constraints trigger a guide review. Ordinary implementation changes do not. Each
library owns remediation for its public files through its issue and pull-request workflow.
