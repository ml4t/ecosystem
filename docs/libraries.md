# Libraries

| Library | Responsibility | Documentation |
|---|---|---|
| Data | Acquire, validate, store, and query observations | [Data docs](https://www.ml4trading.io/docs/data/) |
| Engineer | Produce features, labels, and research datasets | [Engineer docs](https://www.ml4trading.io/docs/engineer/) |
| Models | Train, select, persist, and run predictive models | [Models docs](https://www.ml4trading.io/docs/models/) |
| Diagnostic | Validate data, signals, splits, models, and results | [Diagnostic docs](https://www.ml4trading.io/docs/diagnostic/) |
| Specs | Define runtime-neutral lifecycle and trading contracts | [Specs docs](https://www.ml4trading.io/docs/specs/) |
| Backtest | Simulate lifecycle, execution, risk, and accounting | [Backtest docs](https://www.ml4trading.io/docs/backtest/) |
| Live | Run shared contracts against paper and live adapters | [Live docs](https://www.ml4trading.io/docs/live/) |

This order describes a common user workflow. It does not assert a direct package dependency between
every adjacent library. `ml4t-specs` owns shared contracts used by simulation and live execution.
