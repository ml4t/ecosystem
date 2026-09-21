# Live qualification review

Date: 2026-09-20

Scope: Live source, public and private agent guides, local sidecar issues, public issues and pull
requests, provider evidence, supported-version qualification, documentation, and release 0.1.3.

## Completed work

Live is clean on `main` at `43da4ca`. Pull request
[#101](https://github.com/ml4t/live/pull/101) completed the public agent-guide review, and the
private sidecar is clean on `main` at `3185527`. Its local issue index records current dispositions.

Ruff, ty, actionlint, strict MkDocs, package builds, pre-commit, and the full local suite pass. The
suite has 1,051 passing tests and 29 documented skips. Pull request #101 also passed the complete
repository CI and ecosystem qualification before merge.

Current retained provider evidence passes for Alpaca in run
[35473026566](https://github.com/ml4t/live/actions/runs/35473026566) and OKX in run
[35473028351](https://github.com/ml4t/live/actions/runs/35473028351). Their provider contracts are
unchanged at the current candidate.

## Remaining release gate

Release run [35553318363](https://github.com/ml4t/live/actions/runs/35553318363) passed preflight,
the complete stable matrix, and exact installed-artifact qualification, then stopped at the
provider-evidence gate.

No retained IB artifact satisfies the current complete contract. The September IB runs predate the
required six-hour soak artifact. The older complete bundle targets a revision before changes to the
IB adapter, paper qualification, persistence, safety, and supported-runtime contract. Reusing it
would claim coverage it did not establish.

The remaining sequence is exact and provider-specific:

1. Start an authenticated IB Gateway or TWS paper session with API access.
2. Dispatch `paper.yml` for candidate `43da4caf90a12240c34143b3ea336b4d96013772`, qualification
   run `35553318363`, and `extended-provider=ib`.
3. After the exercise, restart, and six-hour soak succeed, rerun `release.yml` for version 0.1.3 and
   the same candidate commit.
4. Require the release workflow to verify PyPI, the GitHub release, and the deployed documentation
   before closing Live issue #92 and ecosystem issues #36 and #40.

The release gate remains fail closed. No other provider needs a fresh extended session unless its
recorded contract changes before publication.
