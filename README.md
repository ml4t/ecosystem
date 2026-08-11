# ML4T Ecosystem

Shared standards, qualification evidence, documentation rules, and coordinated work management for
the stable ML4T Python libraries.

| Library | Package | Responsibility |
|---|---|---|
| [Data](https://github.com/ml4t/data) | `ml4t-data` | Market data acquisition, validation, storage, and access |
| [Engineer](https://github.com/ml4t/engineer) | `ml4t-engineer` | Feature engineering, labeling, and dataset construction |
| [Backtest](https://github.com/ml4t/backtest) | `ml4t-backtest` | Event-driven simulation, execution, risk, and accounting |
| [Specs](https://github.com/ml4t/specs) | `ml4t-specs` | Shared runtime-neutral lifecycle and trading contracts |
| [Live](https://github.com/ml4t/live) | `ml4t-live` | Paper and live execution using the shared contracts |
| [Diagnostic](https://github.com/ml4t/diagnostic) | `ml4t-diagnostic` | Statistical validation, splitters, evaluation, and diagnostics |
| [Models](https://github.com/ml4t/models) | `ml4t-models` | Model training, selection, persistence, and inference support |

This repository does not contain library source code and is not a runtime dependency. Start with the
[ecosystem documentation](https://ml4t.github.io/ecosystem/) or the tracked documents under
`standards/`, `status/`, `reviews/`, and `decisions/`.

## Stable-release policy

ML4T supports every stable CPython release from Python 3.12 through the latest stable version on
Linux, macOS, and Windows. Each supported combination must pass installation, import, tests, type
checking, and package build checks before release. The next CPython prerelease becomes a blocking
compatibility target after beta 1 without being advertised as stable.

See [Compatibility](standards/compatibility.md) and
[Release qualification](standards/release-qualification.md) for the normative criteria.
