# Decision 0010: Current Python 3.15 dependency exceptions

**Status**: Accepted
**Date**: 2026-09-19
**Approver**: Stefan Jansen
**Expires**: 2026-09-30

## Context

The executable exception ranges no longer cover the latest published Data and Diagnostic releases.
Data 0.1.6 is outside `>=0.1.2,<0.1.6`, and Diagnostic 0.1.5 is outside
`>=0.1.2,<0.1.5`. The planned metadata remediation releases would also fall outside those ranges.

A fresh Data run on CPython 3.15.0rc1 with Polars 1.44.2 still fails in Polars series construction
with `AttributeError: 'NoneType' object has no attribute '_s'`. Data issue
[#37](https://github.com/ml4t/data/issues/37) records the result and the upstream Polars fix.

PyArrow 25.0.1 still publishes no CPython 3.15 wheels. Stable Pydantic 2.13.5 still pins
pydantic-core 2.46.5, which also has no CPython 3.15 wheels. Diagnostic issue
[#45](https://github.com/ml4t/diagnostic/issues/45) records both blockers and the releases that
trigger another review.

## Decision

Extend the `python-315-polars` range to `>=0.1.2,<0.1.8` and the `python-315-scipy` range to
`>=0.1.2,<0.1.7`. These bounds cover the currently published packages and the next patch releases
needed to correct their public metadata. Keep the 2026-09-30 expiry and all existing evidence,
mitigation, supported-version, and three-platform qualification requirements.

This decision does not add another library, change the supported Python range, or permit a release
after the exception expires. Data issue #37 and Diagnostic issue #45 remain the owning removal
issues.

## Consequences

Data and Engineer releases covered by the Polars range, and Diagnostic releases covered by the
PyArrow and Pydantic range, remain installable only on Python 3.12 through 3.14 while the exceptions
are active. Their required stable matrices remain blocking.

The ranges must be removed by 2026-09-30 or sooner if the complete dependency sets pass the Python
3.15 matrix on Linux, macOS, and Windows. Any later affected release requires new evidence and a
separate decision.
