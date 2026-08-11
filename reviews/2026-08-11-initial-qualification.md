# Initial seven-library qualification review

Date: 2026-08-11

Scope: `data`, `engineer`, `backtest`, `specs`, `live`, `diagnostic`, and `models`.

Policy: Python 3.12 through 3.14 must pass installation, import, tests, type checking, and
package builds on Linux, macOS, and Windows. Python 3.15 prerelease installation and the
non-hardware-dependent suite are blocking on all three operating systems unless a reviewed,
version-bounded, and expiring exception applies.

## Result

The repository-owned compatibility work is complete on seven integration branches. Three
libraries require temporary Python 3.15 exclusions because required upstream dependencies do not
yet support CPython 3.15. The other four libraries retain Python 3.15 prerelease qualification.

The integration pull requests remain open. The execution environment rejects `gh pr merge` because
the command requires an approval mechanism that is disabled for this session. Earlier connector
merge attempts also returned HTTP 403. No required check will be bypassed.

## Compatibility decisions

| Library | Source `Requires-Python` | Python 3.15 treatment |
|---|---|---|
| data | `>=3.12,<3.15` | `python-315-polars` exception |
| engineer | `>=3.12,<3.15` | `python-315-polars` exception |
| backtest | `>=3.12` | Blocking prerelease matrix |
| specs | `>=3.12` | Blocking prerelease matrix |
| live | `>=3.12` | Blocking prerelease matrix |
| diagnostic | `>=3.12,<3.15` | `python-315-scipy` exception |
| models | `>=3.12` | Blocking non-hardware-dependent prerelease matrix |

The exceptions are declared in `config/libraries.toml`, validated by the shared workflow, limited
to named libraries and package-version ranges, approved by Stefan Jansen, and expire on
2026-09-30. The exceptions do not skip or weaken any Python 3.12 through 3.14 operating-system job.

Polars 1.43.2 fails required expression and datetime behavior on CPython 3.15.0rc1. The accepted
upstream defect is [pola-rs/polars#28347](https://github.com/pola-rs/polars/issues/28347), with an
upstream fix under review in
[pola-rs/polars#28750](https://github.com/pola-rs/polars/pull/28750).

SciPy 1.18.0 has no CPython 3.15 wheels for the required operating systems. Qualification attempts
therefore fail during dependency installation before `diagnostic` tests can start. Both exceptions
are tracked in [ecosystem issue #2](https://github.com/ml4t/ecosystem/issues/2).

## Pull-request evidence

| Library | Pull request | Reviewed commit | Latest hosted state |
|---|---:|---|---|
| data | [#42](https://github.com/ml4t/data/pull/42) | `ba537bf` | Complete, no failures |
| engineer | [#34](https://github.com/ml4t/engineer/pull/34) | `7a6969c` | Running, no failures observed |
| backtest | [#75](https://github.com/ml4t/backtest/pull/75) | `2ddcd29` | Complete, no failures |
| specs | [#9](https://github.com/ml4t/specs/pull/9) | `c3bff2c` | Running, no failures observed |
| live | [#56](https://github.com/ml4t/live/pull/56) | `c6674a5` | Complete, no failures |
| diagnostic | [#39](https://github.com/ml4t/diagnostic/pull/39) | `beae2ab` | Running, no failures observed |
| models | [#36](https://github.com/ml4t/models/pull/36) | `2bc84bb` | Running, no failures observed |

This table records pull-request branch evidence, not default-branch or published-package status.
Generated files under `status/` remain authoritative for merged default branches and must be
regenerated after the pull requests merge.

## Local verification

- Ecosystem management: Ruff, format, ty, 80 tests, strict MkDocs, package build, and all
  pre-commit hooks pass. A new GitHub Actions audit passed after the monitor was changed to recognize
  explicitly configured maintainer accounts when GitHub reports an incorrect author association.
- Data: 3,609 tests pass with 280 explicitly deselected; Ruff, format, ty, package build, and
  pre-commit pass. Built metadata contains `Requires-Python: <3.15,>=3.12`.
- Engineer: the complete suite ran without an observed failure; release-policy tests, package build,
  and pre-commit pass. Built metadata contains `Requires-Python: <3.15,>=3.12`.
- Diagnostic: 5,309 tests pass with 75 skips; Ruff, format, ty, package build, and pre-commit pass.
  Built metadata contains `Requires-Python: <3.15,>=3.12`.
- Backtest, specs, live, and models pass their repository pre-commit gates on the reviewed commits.

## Repository cleanup

- Each canonical release checkout is now a clean `main` synchronized with `origin/main`.
- Completed temporary worktrees and branches without unique patch content were removed.
- Merged or superseded remote branches were deleted after their pull-request or patch-equivalence
  evidence was checked.
- The backtest checkout had `core.bare=true`, an unborn `HEAD`, and an empty branch reference despite
  containing a normal working tree. Its index tree exactly matched commit `4c29c8a`, a known ancestor
  of `origin/main`, with no working-tree or untracked changes. The checkout was repaired to clean,
  synchronized `main`.
- Four diagnostic worktrees remain because they belong to open pull requests.
- Branches with unique, unresolved commits remain. Removing them without reviewing their content
  would discard work rather than clean up dead references:
  - data: `chore/ci-python-312-314`, `feat/docs-plate-header`, `pr-20`,
    `slice/provider-close-noise`, and `work/local-main-unpublished-20260811`. The last branch
    preserves 133 unpublished commits.
  - engineer: `feat/docs-plate-header`.
  - backtest: `diag/engine-memory-profiling`, `feat/docs-plate-header`,
    `feature/validation-trade-audit`, `feature/validation-trade-audit-main`, and `fix/ch16-parity`.
  - live: `chore/pr-release-policy` and `feat/docs-plate-header`.
  - diagnostic: `feat/daily-ic-uncertainty`, `feat/docs-plate-header`, and
    `fix/vendor-docs-theme-ci`.

## Release decision

Do not publish patch releases from the integration branches. Release approval requires:

1. Every current hosted check completes successfully, with an approved exception recorded where
   Python 3.15 is temporarily excluded.
2. An authorized maintainer merges the reviewed heads without overriding checks.
3. The same qualification requirements pass on each default branch.
4. The ecosystem collector regenerates `status/current.json` and `status/current.md`, and the
   validated result is retained under `status/snapshots/`.
5. Libraries with metadata or user-visible changes publish patch releases through trusted
   publishing.
6. Installed artifact metadata, imports, documentation routes, and release workflow evidence are
   verified after publication.
7. The Polars and SciPy exceptions are removed as soon as compatible upstream releases qualify, and
   no later than their expiration unless a new reviewed decision explicitly changes the policy.

The qualification review remains tracked in
[ecosystem issue #1](https://github.com/ml4t/ecosystem/issues/1).
