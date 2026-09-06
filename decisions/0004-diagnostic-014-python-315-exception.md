# Decision 0004: Diagnostic 0.1.4 Python 3.15 dependency exception

**Status**: Accepted
**Date**: 2026-09-05
**Approver**: Stefan Jansen
**Expires**: 2026-09-30

## Context

Decision 0003 covers `ml4t-diagnostic` versions `>=0.1.2,<0.1.4`. Version 0.1.4 was subsequently
published with `Requires-Python: >=3.12,<3.15` before the executable exception range was updated.
The published version is therefore outside the recorded exception even though the dependency
blockers remain.

A fresh dependency check on 2026-09-05 found that PyArrow 25.0.1 still has no CPython 3.15 wheels.
Pydantic 2.13.5 still resolves to pydantic-core 2.46.5, which also has no CPython 3.15 wheel. The
complete Diagnostic dependency set cannot install on CPython 3.15 on the required platforms.
[Diagnostic issue #45](https://github.com/ml4t/diagnostic/issues/45) retains the reproduction and
upstream evidence.

## Decision

Extend the `python-315-scipy` exception to `ml4t-diagnostic` versions `>=0.1.2,<0.1.5`. Do not change
the 2026-09-30 expiry. Diagnostic 0.1.4 must continue to pass Python 3.12 through 3.14 on Linux,
macOS, and Windows.

This decision changes only the Diagnostic version range in Decision 0003. It does not change the
Polars exception or exempt any additional library.

## Consequences

Diagnostic 0.1.4 remains installable only on Python 3.12 through 3.14 while the exception is active.
Diagnostic 0.1.5 is not covered. It must either pass the complete Python 3.15 matrix or receive a
separately reviewed, evidence-backed exception before publication.

The exception must be removed before its expiry, or sooner if the complete dependency set passes the
Diagnostic matrix on Python 3.15.
