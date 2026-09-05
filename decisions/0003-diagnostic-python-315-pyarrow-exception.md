# Decision 0003: Diagnostic Python 3.15 dependency exception

**Status**: Accepted
**Date**: 2026-09-05
**Approver**: Stefan Jansen
**Expires**: 2026-09-30

## Context

Decision 0002 allowed `ml4t-diagnostic` versions `>=0.1.0,<0.1.2` to exclude Python 3.15 because
SciPy 1.18.0 did not publish compatible wheels. That evidence no longer describes the current
release. SciPy 1.18.1 publishes CPython 3.15 wheels for Linux, macOS, and Windows, and
`ml4t-diagnostic` 0.1.2 falls outside the recorded version range.

Installing the published package on CPython 3.15.0rc1 fails before the library can be imported or
tested. PyArrow 25.0.1 has no CPython 3.15 wheels. The stable Pydantic 2.13.5 release resolves to
pydantic-core 2.46.5, which also has no CPython 3.15 wheel. Both packages attempt source builds that
fail in a clean installation. [Diagnostic issue #45](https://github.com/ml4t/diagnostic/issues/45)
records the reproduction and owns qualification of the complete dependency set.

## Decision

Extend Diagnostic's existing `python-315-scipy` exception to `ml4t-diagnostic` versions
`>=0.1.2,<0.1.4`. The identifier remains unchanged because it is an established workflow interface;
the executable exception record, not the identifier, states the current evidence. Keep the existing
2026-09-30 expiry and the requirement to pass Python 3.12 through 3.14 on Linux, macOS, and Windows.

This decision supersedes only the Diagnostic clause in Decision 0002. The Polars exception is
unchanged.

## Consequences

Diagnostic 0.1.2 and 0.1.3 remain installable only on Python 3.12 through 3.14 while the exception is
active. Diagnostic 0.1.4 is not covered. It must either pass the complete Python 3.15 matrix or
receive a separately reviewed, evidence-backed exception before publication.

The exception must be removed before its expiry, or sooner if the complete dependency set passes the
Diagnostic matrix on Python 3.15.
