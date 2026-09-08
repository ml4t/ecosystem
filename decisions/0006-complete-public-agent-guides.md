# Decision 0006: Complete public agent guides

**Status**: Accepted
**Date**: 2026-09-08

## Decision

Data, Engineer, Backtest, and Diagnostic retain their public root `AGENTS.md` guides. Specs and Live
must replace their mechanism-only files with library orientation. Models must add a root guide now;
its published package, documentation, examples, and release history show that initialization is
already complete.

## Consequences

All seven stable libraries have a useful public entry point for agents. Models is fixed directly
rather than left behind an issue whose premise is no longer true. Each guide remains concise and
delegates detailed API material to source, documentation, and justified nested guides.
