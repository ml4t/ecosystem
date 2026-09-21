# Data closure review

Date: 2026-09-20

Scope: Data source, public and private agent guides, local sidecar issues, public issues and pull
requests, supported-version qualification, documentation, packaging, and the Python 3.15 wait.

## Result

Data is clean on `main` at `9b28c5c`. Pull request
[#59](https://github.com/ml4t/data/pull/59) added the monthly Python 3.15 dependency canary and
closed the public agent-guide review. No agent-guide source edit was necessary: all five tracked
guides describe current package boundaries and commands, pass the executable ecosystem checks, and
contain no public private-state or tool-specific files.

The private sidecar is clean on `main` at `9965979`. Its two records marked open were stale:

| Record | Current evidence | Disposition |
|---|---|---|
| Strict documentation build failures | `uv run mkdocs build --strict` passes on current `main`. | Resolved |
| Hard-coded storage roots | Shared resolvers, provider layout tests, and the package-source guard pass. | Resolved |

The dated website presentation review is superseded. Current website source uses responsive
workflow layout, renders library feature metadata, avoids the earlier production-maturity claim,
and lists Data provider counts consistently. The other sidecar defect records were already marked
resolved, fixed, or shipped.

## Verification

- Ruff lint and formatting, ty, actionlint, strict MkDocs, package builds, and every pre-commit hook
  pass locally.
- Both full local test lanes pass: 3,649 tests on the standard lane and 3,649 tests with
  `ResourceWarning` treated as an error.
- Pull request #59 passed supported Python 3.12 through 3.14 on Linux, macOS, and Windows, plus
  security, dependency, documentation, and exception-validation checks.
- The built wheel and source distribution completed successfully.
- Data has no open pull request. Its only open issue is
  [#37](https://github.com/ml4t/data/issues/37), the accepted external-dependency wait for Python
  3.15. It is not actionable library work until a recorded review trigger fires.

The Python 3.15 canary runs automatically each month on Ubuntu and is not a pull-request or release
gate. A fresh CPython 3.15.0rc1 probe reproduces the current dependency limits. Python 3.12 through
3.14 remain the supported release range until Python 3.15 final or a stable Polars release after
1.44.2 triggers full three-platform qualification.
