# Decision 0001: Ecosystem authority

**Status**: Accepted
**Date**: 2026-08-11

## Decision

`ml4t/ecosystem` owns shared standards, qualification evidence, documentation process, and
cross-library work coordination. Each library retains its source, user documentation, issues, Git
history, versions, and releases. `ml4t-specs` retains executable lifecycle and trading contracts.

Shared automation reads library branches but does not change them. Remediation uses the owning
library's issue and pull-request process.

## Consequences

Shared requirements have one review history and one compliance definition. Library releases can be
blocked by ecosystem failures. The ecosystem repository cannot become a runtime dependency or a
substitute for library-specific tests.
