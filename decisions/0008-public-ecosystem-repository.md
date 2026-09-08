# Decision 0008: Public ecosystem repository

**Status**: Accepted
**Date**: 2026-09-08

## Decision

`ml4t/ecosystem` remains public. Its contributor-facing surface is `README.md`, `CONTRIBUTING.md`,
`SECURITY.md`, `docs/standards/`, and `decisions/`. Its inventory, audit implementation, generated
status, and dated reviews remain public evidence for those policies, not internal work management.

Private plans, transitions, memory, credentials, and security reports remain in ignored
`.workspace/` state or private development sidecars.

## Consequences

Contributors can inspect the same standards and qualification logic that govern the seven public
libraries, and existing documentation links remain valid. Public pushes continue to require the
publication discipline stated in `AGENTS.md`; private operational detail has an explicit exclusion.
