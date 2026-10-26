# Decision 0016: Current Data and Diagnostic Python 3.15 scopes

**Status**: Accepted
**Date**: 2026-10-25
**Approver**: Stefan Jansen

## Context

Decision 0015 explicitly excluded the Data 0.3 release line from the older Polars exception.
Data 0.3.0 is now published. Its post-release candidates declare versions such as
`0.3.1.dev3+g8ca0c3828`, which the existing `>=0.1.2,<0.3` exception correctly rejects.

[Data issue 37](https://github.com/ml4t/data/issues/37#issuecomment-6374129753) records the current
dependency condition. A CPython 3.15 final core installation and 66 focused tests pass, while the
complete environment cannot resolve. Released Databento 0.88.0 requires `databento-dbn~=0.70.0`,
whose released artifacts cannot satisfy that environment. The October 25 reproduction confirms the
same condition. The earlier Polars failure is not the demonstrated current Data blocker.

Diagnostic also needs an explicit scope for its proposed 0.2 release. PyArrow 26 wheels are available,
and the current core dependency set installs and imports on Python 3.15. The remaining work in
[Diagnostic issue 45](https://github.com/ml4t/diagnostic/issues/45) is actual Diagnostic source,
installed-package and full three-operating-system qualification. Missing PyArrow wheels no longer
justify this deferral.

## Decision

### Data 0.3

Add `python-315-data-databento-030` for Data only, with affected versions `>=0.3,<0.4`. Select it in
Data's inventory entry. Preserve the older `python-315-polars` record and Engineer's selection and
scope without modification. Existing immutable policy revisions retain historical Data scopes.

Recheck when a released Databento dependency set supports CPython 3.15. Keep Data issue 37 open,
the truthful `<3.15` package bound and the visible monthly canary. Its core-only passing probes do
not qualify the complete distribution. Review the complete environment on Linux, macOS and Windows
before removing the upper bound. The canary must expose the actual dependency wait as well as core
progress; a passing core probe alone cannot establish that Databento is ready.

### Diagnostic 0.2

Extend the Diagnostic-only `python-315-scipy` record to `>=0.1.2,<0.3`, retaining its historical
identifier so existing workflow callers remain compatible. Replace the obsolete wheel rationale
with the current qualification-pending state. This deferral expires on November 24, 2026, and must
be reviewed earlier if full three-OS qualification completes. It does not assert a current external
dependency failure.

Diagnostic must retain `Requires-Python: >=3.12,<3.15`, publish current evidence in issue 45 and run
a visible monthly three-OS candidate canary. Unsupported-target probes must be identified as such;
an ordinary install rejected by the package's own Python bound is not a meaningful dependency probe.
Removing the upper bound requires the complete native and installed-artifact workflows to pass on
all three systems. The exception and package bound must be removed together after qualification.
A later release line or an extension beyond November 24 needs a new evidence-backed decision.

### Enforcement and release impact

Every Python 3.12-3.14 operating-system gate remains blocking. Only the version-scoped Python 3.15
criterion is deferred. No source, numerical, rendering, security, documentation or package gate is
waived, and no package release or documentation deployment is authorized by this decision.

Validate actual built candidate metadata with the existing exception validator. Reject versions
outside each approved range, other libraries, repository mismatches and missing evidence. Pin the
reusable workflow's internal policy checkout to an immutable revision containing these records;
updating only the caller's workflow reference does not select the new policy.

This decision supersedes Decisions 0013 and 0015 only for these Data 0.3 and Diagnostic-through-0.2
scopes. It does not change another library's exception or claim that Python 3.15 tests have passed.
