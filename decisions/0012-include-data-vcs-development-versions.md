# Decision 0012: Include Data VCS development versions in the active exception

**Status**: Superseded by Decision 0013
**Date**: 2026-09-19
**Approver**: Stefan Jansen
**Expires**: 2026-09-30

## Context

Decision 0010 approved the `python-315-polars` exception through Data 0.1.8 with the range
`>=0.1.2,<0.1.8`. Data derives development versions from Git tags. After releasing 0.1.7, its next
commit is therefore identified as `0.1.8.devN`.

PEP 440 excludes `0.1.8.devN` from `<0.1.8`. As a result, Data pull requests fail exception
validation before reaching the Python 3.15 compatibility job, although the generated development
version belongs to the already approved 0.1.8 release line.

## Decision

Change the `python-315-polars` affected-version range to `>=0.1.2,<=0.1.8`. This includes VCS
development versions and the final 0.1.8 release while continuing to reject `0.1.9.devN` and later
versions.

The covered libraries, evidence, mitigation, stable qualification requirements, removal issues, and
2026-09-30 expiry do not change.

## Consequences

Data pull requests on the 0.1.8 development line can validate the active exception. A Data 0.1.9
development version or any release after the expiry requires new evidence and a separate decision.
