# Initial seven-library qualification review

Date: 2026-08-11

Scope: `data`, `engineer`, `backtest`, `specs`, `live`, `diagnostic`, and `models`.

Policy: Python 3.12 through 3.14 must pass installation, import, test, type-check, and
package-build checks on Linux, macOS, and Windows. Python 3.15 prerelease installation and the
non-hardware-dependent suite are also blocking on all three operating systems.

## Result

The stable-release qualification is not complete. Repository-owned compatibility and quality
failures found during the review have been fixed on the integration branches. The remaining known
Python 3.15 failures originate in required third-party dependencies:

- Polars fails common expression and datetime operations on CPython 3.15.0rc1. This blocks the
  required suites in `data` and `engineer`.
- SciPy does not publish CPython 3.15 wheels. Building SciPy from source in the qualification jobs
  fails because the runners do not provide the required OpenBLAS development environment. This
  blocks `diagnostic` before its tests start.

The integration pull requests have not been merged. An attempted merge of the fully passing
`specs` pull request returned `403 Resource not accessible by integration`, so default-branch
qualification, generated status snapshots, and releases cannot yet be completed by this session.

## Pull-request evidence

| Library | Pull request | Reviewed commit | Qualification state |
|---|---:|---|---|
| data | [#42](https://github.com/ml4t/data/pull/42) | `77b0dec` | 20 checks pass, including every stable job; all three Python 3.15 jobs fail in Polars |
| engineer | [#34](https://github.com/ml4t/engineer/pull/34) | `2c8490d` | 23 checks pass, including every stable job; all three Python 3.15 jobs fail in Polars |
| backtest | [#75](https://github.com/ml4t/backtest/pull/75) | `98c12aa` | All 36 checks pass, including two independent Python 3.15 matrices |
| specs | [#9](https://github.com/ml4t/specs/pull/9) | `54c8480` | All 28 checks pass, including Python 3.15 on all three operating systems |
| live | [#56](https://github.com/ml4t/live/pull/56) | `7f6e6cc` | Both qualification workflows complete successfully, including every stable and Python 3.15 operating-system job |
| diagnostic | [#39](https://github.com/ml4t/diagnostic/pull/39) | `bcdd8fc` | 34 checks pass, including every stable job; all three Python 3.15 jobs fail during SciPy installation |
| models | [#36](https://github.com/ml4t/models/pull/36) | `3a13150` | Every required stable and Python 3.15 job passes; the optional CUDA job is skipped on pull requests |

This table records pull-request branch evidence, not default-branch or published-package status.
The generated files under `status/` remain authoritative for merged default branches.

## Repository-owned remediation completed

- Added standard issue forms, pull-request templates, security reporting, shared labels, central
  qualification callers, and release qualification dependencies across the seven repositories.
- Added or aligned strict MkDocs validation and documentation deployment contracts.
- Corrected Python metadata so prerelease qualification can install the candidate packages.
- Isolated optional scientific and hardware-dependent dependencies from core qualification where
  they are not part of the package's core functionality.
- Kept Polars in the `data` and `engineer` core suites and SciPy in the `diagnostic` core suite
  because removing them would avoid testing required behavior.
- Defined a non-hardware-dependent `models` Python 3.15 suite instead of requiring a prerelease
  PyTorch build that is not part of the core package.
- Fixed Windows path, encoding, filesystem cleanup, signal, and recovery-test behavior in `live`.
- Changed the `live` qualification target from the already published 0.1.0 artifact to the 0.1.1
  release candidate and verified its built artifacts locally.
- Updated affected lock files to NumPy 2.5.2, the first current release with the required CPython
  3.15 Windows wheel.
- Moved optional ML runtimes out of the generic `diagnostic` development environment while retaining
  their dedicated integration checks.
- Moved optional scientific dependencies out of the `engineer` core environment and retained clear
  runtime errors for features that require them.
- Isolated one explicit `data` storage benchmark from the default correctness suite so a timing
  threshold does not make ordinary macOS qualification nondeterministic.
- Required authentication for response monitoring after reproducing GitHub's incorrect anonymous
  maintainer association. Authenticated monitoring of all current open issues and pull requests
  reports no overdue classification or response findings.

## External blockers

### Polars on CPython 3.15

Affected libraries: `data`, `engineer`.

Evidence:

- [pola-rs/polars#28347](https://github.com/pola-rs/polars/issues/28347) tracks the accepted
  CPython 3.15 failure.
- [pola-rs/polars#28750](https://github.com/pola-rs/polars/pull/28750) contains the upstream fix but
  was not merged or released at the evidence cutoff.
- The failure reproduces with Polars 1.43.1 and 1.43.2 before ML4T code can process the result.

Resolution condition: select an upstream Polars release containing the fix and pass the complete
Python 3.15 suite on Linux, macOS, and Windows.

### SciPy wheels for CPython 3.15

Affected library: `diagnostic`.

Evidence:

- SciPy 1.18.0 publishes no CPython 3.15 wheels on PyPI at the evidence cutoff.
- No compatible prerelease wheel is available from the configured scientific Python prerelease
  indexes.
- Linux, macOS, and Windows qualification therefore attempt a source build and fail before the
  package test suite can start.

Resolution condition: install a SciPy release or prerelease with compatible wheels on all three
operating systems, then pass the complete non-hardware-dependent suite.

### Merge authorization

Affected repositories: all integration pull requests that remain open.

Evidence: the `specs` pull request is clean and fully passing, but the GitHub integration returned
HTTP 403 when asked to merge the reviewed head commit.

Resolution condition: an authorized maintainer merges the qualified pull requests, or grants the
integration permission to merge them. Failing required checks must not be overridden.

## Release decision

Do not publish stable patch releases yet. Release approval requires all of the following:

1. Every required pull-request matrix has completed successfully, including Python 3.15 on all
   three operating systems.
2. Qualified pull requests are merged without overriding required checks.
3. The same requirements pass on each default branch.
4. The ecosystem collector regenerates `status/current.json` and `status/current.md` from GitHub and
   PyPI evidence, and the validated result is retained under `status/snapshots/`.
5. Libraries with user-visible changes publish the next patch release through their normal trusted
   publishing workflow.
6. Installed artifacts, published metadata, documentation routes, and the release qualification
   evidence are verified after publication.

The review remains open in [ecosystem issue #1](https://github.com/ml4t/ecosystem/issues/1).
Third-party Python 3.15 failures are tracked in
[ecosystem issue #2](https://github.com/ml4t/ecosystem/issues/2).
