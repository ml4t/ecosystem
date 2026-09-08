# Decision 0005: Public agent orientation

**Status**: Accepted
**Date**: 2026-09-08

## Decision

Public release repositories must carry a substantive root `AGENTS.md` that helps an external agent
understand the library's responsibility, structure, public entry points, deeper guidance, and quality
commands. They must not track a `CLAUDE.md` include whose only purpose is internal tool setup.

The ecosystem audits `AGENTS.md` content through `release.agent-orientation` and
`repository.agent-orientation`. It no longer requests or checks public `CLAUDE.md` files.

## Consequences

The audit now tests the public information need instead of one agent tool's include mechanism.
Claude-specific setup remains available in private sidecars and local ignored files. A missing,
placeholder, or private-workspace-dependent public guide blocks workspace and release qualification.
