# Backtest closure review

Date: 2026-09-20

Scope: Backtest source, public and private agent guides, local sidecar issues, public issues and
pull requests, supported-version qualification, documentation, and packaging.

## Result

Backtest is clean on `main` at `a32a206`. Pull request
[#101](https://github.com/ml4t/backtest/pull/101) replaced stale package and file counts in nine
public agent guides with stable ownership boundaries, local constraints, and verification commands.
The public issue and pull-request queues are empty.

The private sidecar is clean on `main` at `21dbaad`. Its local issue index now records every draft's
current disposition. Private issues #14 and #16 were closed after verifying the associated book
change and the published release history through 0.1.7.

The timezone-alignment fix in current source changed installed behavior after 0.1.7. Release
[v0.1.8](https://github.com/ml4t/backtest/releases/tag/v0.1.8) therefore publishes exact `main`
commit `a32a20620b1a34cc5c8a657f358b4b145b1efa69` rather than leaving that fix unreleased.

## Verification

- Ruff lint and formatting, ty, actionlint, strict MkDocs, package builds, and every pre-commit hook
  pass locally.
- The full local suite passes with 2,162 tests and 14 documented skips.
- Pull request #101 passed supported Python 3.12 through 3.14 qualification on Linux, macOS, and
  Windows, plus its repository CI, before merge.
- The ecosystem agent-guide audit passes for the root guide and all nested guides.
- The built wheel installs and imports successfully in an isolated environment.
- Release run
  [35553684066](https://github.com/ml4t/backtest/actions/runs/35553684066) passed the complete
  candidate, licensed-comparison, documentation, publication, and post-publication gates. PyPI,
  the GitHub release, and the deployed documentation all report version 0.1.8 and the exact source
  commit.
