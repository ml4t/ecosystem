# Decision 0013: Python 3.15 waiting policy

**Status**: Accepted
**Date**: 2026-09-20
**Approver**: Stefan Jansen

## Context

[Python 3.15.0 final is scheduled for 2026-10-01](https://peps.python.org/pep-0790/). Data and
Engineer depend on [Polars 1.44.2](https://pypi.org/project/polars/1.44.2/), which still fails
required Data operations on CPython 3.15.0rc1. Diagnostic depends on
[PyArrow 25.0.1](https://pypi.org/project/pyarrow/25.0.1/#files), which publishes no CPython 3.15
wheels. [Pydantic-core 2.49.0](https://pypi.org/project/pydantic-core/2.49.0/#files) now publishes
CPython 3.15 wheels and is no longer a current Diagnostic blocker.

The existing exceptions expire on 2026-09-30. That date does not measure whether the libraries can
install and pass their full suites. Requiring a new exception for each patch release would block
Python 3.12 through 3.14 users without improving Python 3.15 compatibility.

## Decision

Python 3.12 through 3.14 remain the blocking stable matrix. A library whose complete dependency set
cannot pass Python 3.15 may retain a truthful `<3.15` upper bound for its 0.1 release line. The
library must run a visible non-blocking Python 3.15 canary at least monthly and keep an owning issue
with current evidence.

Replace the 2026-09-30 expirations with these review triggers:

- Data and Engineer: Python 3.15 final or a Polars release after 1.44.2.
- Diagnostic: Python 3.15 final or PyArrow 26.

A trigger requires the owner to rerun installation, import, and the non-hardware-dependent suite on
Linux, macOS, and Windows. The result updates the owning issue and either removes the upper bound or
records why the wait continues. A trigger does not make Python 3.15 compatibility a condition for a
release that otherwise passes the stable matrix.

The existing `prerelease_exception` configuration and workflow input names remain to avoid breaking
the seven library workflows. Their trigger-based records now represent prerelease waits. Date-bounded
exceptions remain supported for other qualification criteria.

This decision supersedes the September 30 expiry and affected-version ranges in Decisions 0010 and
0012. Those decisions remain as the history of the evidence and earlier release scopes.

## Consequences

Data, Engineer, and Diagnostic can publish qualified 0.1 patch releases for Python 3.12 through
3.14 while their Python 3.15 dependencies remain unavailable. Their package metadata continues to
reject Python 3.15 rather than claiming support that has not passed qualification.

Ecosystem issue [#2](https://github.com/ml4t/ecosystem/issues/2), Data issue
[#37](https://github.com/ml4t/data/issues/37), and Diagnostic issue
[#45](https://github.com/ml4t/diagnostic/issues/45) remain open until the affected libraries pass the
complete Python 3.15 matrix.
