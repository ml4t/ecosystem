# Decision 0015: Continue the Polars wait through 0.2 releases

**Status**: Accepted
**Date**: 2026-09-24
**Approver**: Stefan Jansen

## Context

Decision 0013 replaced the expiration date for the Data and Engineer Python 3.15 wait with two
review triggers: Python 3.15 final and a Polars release after 1.44.2. Neither trigger has occurred.
Data 0.2.0 retains the truthful `Requires-Python: >=3.12,<3.15` bound and passed the blocking Python
3.12 through 3.14 release matrix, but the configured affected-version range ended before 0.2.0.
The ecosystem audit therefore rejected the published release even though its dependency blocker,
supported Python versions, evidence, user impact, and mitigation are unchanged.

## Decision

Extend the `python-315-polars` affected-version range from `>=0.1.2,<0.2` to `>=0.1.2,<0.3`.
The existing libraries, evidence, mitigation, owning issue, and objective review triggers remain
unchanged. This covers the Data and Engineer 0.2 release lines while the recorded dependency wait
is active. It does not claim Python 3.15 support or weaken the three-platform stable matrix.

A 0.3 development or final release is outside this decision. It requires either completed Python
3.15 qualification or another reviewed decision supported by current dependency evidence.

## Consequences

Data 0.2.0 can satisfy ecosystem qualification when its source commit, release tag, PyPI metadata,
and deployed documentation agree. Data and Engineer continue to run the visible Python 3.15 canary
and must requalify when either existing review trigger occurs.
