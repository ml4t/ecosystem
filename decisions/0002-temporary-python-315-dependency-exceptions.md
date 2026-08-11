# Decision 0002: Temporary Python 3.15 dependency exceptions

**Status**: Accepted
**Date**: 2026-08-11
**Approver**: Stefan Jansen
**Expires**: 2026-09-30

## Decision

`ml4t-data` and `ml4t-engineer` versions `>=0.1.2,<0.1.4` may declare
`Requires-Python >=3.12,<3.15` while required Polars operations fail on CPython 3.15.0rc1.
`ml4t-diagnostic` versions `>=0.1.0,<0.1.2` may declare the same bound while SciPy does not
publish CPython 3.15 wheels for Linux, macOS, and Windows.

The three libraries must continue to pass installation, import, tests, type checking, and builds
on Python 3.12 through 3.14 on all three operating systems. Their shared qualification workflows
must validate the applicable exception instead of omitting Python 3.15 without evidence.

The exception definitions in `config/libraries.toml` are authoritative and expire after
2026-09-30. [Ecosystem issue #2](https://github.com/ml4t/ecosystem/issues/2) owns removal.

## Consequences

Users of these versions must use Python 3.12 through 3.14. `ml4t-backtest`, `ml4t-specs`,
`ml4t-live`, and `ml4t-models` remain eligible for Python 3.15 and continue to run the blocking
prerelease matrix.

The upper bounds must be removed as soon as compatible Polars and SciPy releases pass the complete
matrix. They cannot remain in a release after the exception expires.
