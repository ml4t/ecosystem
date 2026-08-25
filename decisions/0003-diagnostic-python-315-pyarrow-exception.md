# Decision 0003: Diagnostic Python 3.15 PyArrow exception

**Status**: Proposed
**Date**: 2026-08-25
**Approver**: Pending review
**Expires**: 2026-09-30

## Context

Decision 0002 allowed `ml4t-diagnostic` versions `>=0.1.0,<0.1.2` to exclude Python 3.15 because
SciPy 1.18.0 did not publish compatible wheels. That evidence no longer describes the current
release. SciPy 1.18.1 publishes CPython 3.15 wheels for Linux, macOS, and Windows, and
`ml4t-diagnostic` 0.1.2 falls outside the recorded version range.

Installing `ml4t-diagnostic` 0.1.2 on CPython 3.15.0rc1 now reaches PyArrow 25.0.1. PyArrow has no
CPython 3.15 wheels, so installation attempts a source build and fails before the library can be
imported or tested. Apache Arrow issues
[#48172](https://github.com/apache/arrow/issues/48172) and
[#50091](https://github.com/apache/arrow/issues/50091) track Python 3.15 support for Arrow 26.0.0.
[Diagnostic issue #45](https://github.com/ml4t/diagnostic/issues/45) owns library qualification
against that release.

## Proposed decision

Replace Diagnostic's `python-315-scipy` exception with `python-315-pyarrow`. Limit the replacement
to `ml4t-diagnostic` versions `>=0.1.2,<0.1.3`. Keep the existing 2026-09-30 expiry and the existing
requirement to pass Python 3.12 through 3.14 on Linux, macOS, and Windows.

This decision supersedes only the Diagnostic clause in Decision 0002. The Polars exception is
unchanged.

## Consequences

Diagnostic 0.1.2 remains installable only on Python 3.12 through 3.14 while the exception is active.
The next Diagnostic release is not covered. It must either pass the complete Python 3.15 matrix or
receive a separately reviewed, evidence-backed exception before publication.

The exception must be removed before its expiry, or sooner if compatible PyArrow wheels pass the
complete Diagnostic matrix.
