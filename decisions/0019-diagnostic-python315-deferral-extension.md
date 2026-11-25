# Decision 0019: Extend the Diagnostic Python 3.15 qualification deferral

**Status**: Accepted
**Date**: 2026-11-25
**Approver**: Stefan Jansen

## Context

Decision 0016 scoped the Diagnostic-only `python-315-scipy` record to `>=0.1.2,<0.3` with an expiry
of November 24, 2026, and required a new evidence-backed decision for any extension. The record
expired with [Diagnostic issue 45](https://github.com/ml4t/diagnostic/issues/45) still open: full
Diagnostic source, installed-artifact and three-operating-system qualification on Python 3.15 has
not run. Every Diagnostic pull request now fails its required `Validate Python 3.15 exception` check
on the expiry date alone, independent of its change.

PyPI metadata on November 25, 2026 shows CPython 3.15 wheels for Linux, macOS and Windows for the
current releases of Diagnostic's compiled core dependencies: SciPy 1.18.1, PyArrow 26.0.1,
pydantic-core 2.50.5 and NumPy 2.5.5. The deferral is therefore a pending qualification run, not
an external dependency wait. Decision 0016 already records this distinction.

## Decision

Extend `python-315-scipy` to expire on December 31, 2026. Its identifier, library, affected
versions `>=0.1.2,<0.3`, rationale, mitigation and review trigger are unchanged.

Diagnostic retains `Requires-Python: >=3.12,<3.15` and every Python 3.12-3.14 operating-system gate.
The exception and the package bound are removed together once the complete native and
installed-artifact workflows pass on Linux, macOS and Windows; review earlier if that happens
before December 31. A further extension needs a new decision that states why qualification did
not complete.

No other library's exception changes, and no release or documentation deployment is authorized by
this decision.
