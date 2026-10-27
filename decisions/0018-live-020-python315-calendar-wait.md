# Decision 0018: Live 0.2 calendar dependency wait on Python 3.15

**Status**: Accepted through maintainer-directed compatibility review
**Date**: 2026-10-26
**Reviewer**: ML4T development coordinator under delegated maintenance authority

## Reproduced condition

Live's current-cohort integration uses released Backtest 0.2.0 and Specs 0.2.0. Its strict public
calendar workflow calls `get_schedule("HKEX", ..., include_breaks=True)`. With NumPy 2.5.2 or
2.5.4, pandas 3.0.5, pandas-market-calendars 5.5.0 and exchange-calendars 4.13.2, that call fails
under `-W error::DeprecationWarning`. Independent isolated installations reproduced it on Python
3.12 and Python 3.15 final. NumPy and pandas imports succeed in the latter environment.

The exception originates in the upstream XHKG calendar's `adhoc_holidays`: adding a bare integer
to a NumPy year value uses a deprecated generic timedelta unit. This is a strict-warning
compatibility failure; it does not establish incorrect schedule values. NumPy 2.5.4 provides
Python 3.15 support, so this is not a missing NumPy wheel claim.

NumPy 2.4.6 avoids that warning, but upstream advertises Python 3.11-3.14 support only. Live's
actual Windows 3.15 job fails importing NumPy 2.4.6 before test collection. The compatible bounds
therefore cannot establish Python 3.15 support. Pandas 3.1 also produces upstream deprecations in
the strict calendar workflow; Live retains its qualified pandas <3.1 bound.

Evidence and exact commands are tracked in [ecosystem issue 2](https://github.com/ml4t/ecosystem/issues/2).
The actual [failed Windows job](https://github.com/ml4t/live/actions/runs/40421184735/job/121915993276)
retains its original failure. Upstream [NumPy 2.4.6](https://github.com/numpy/numpy/releases/tag/v2.4.6)
and [2.5.4](https://github.com/numpy/numpy/releases/tag/v2.5.4) document the different Python support.
The upstream [XHKG implementation](https://github.com/gerrymanoim/exchange_calendars/blob/4.13.2/exchange_calendars/exchange_calendar_xhkg.py)
contains the deprecated year arithmetic.

## Alternatives reviewed

Do not suppress the warning, monkeypatch NumPy or vendor holiday logic. Substituting the native
pandas-market-calendars HKEX provider avoids this particular operation but changes the historical
calendar. A direct 2010-2030 comparison found seven session dates present in only one provider,
292 different opens, and 44 different break ends and closes on common sessions. This does not
establish which provider is correct for every discrepancy. It does establish that substitution is
not a behavior-preserving compatibility fix.

## Bounded decision

Add `python-315-live-calendar-020` for Live alone, covering `>=0.2.0.dev0,<0.3`, including development
versions of that line. It expires on November 26, 2026. Review earlier after a new released
exchange-calendars, pandas-market-calendars or NumPy version, or completed three-OS qualification.
Published Live 0.1.3, its dependency cohort and other libraries' records remain unchanged.

Live must declare `Requires-Python >=3.12,<3.15`. Keep the qualified NumPy <2.5 and pandas <3.1
bounds and all Python 3.12-3.14 operating-system, artifact, provider and strict-warning gates.
No current failed check is relabeled as passing. A final changed candidate requires fresh complete
qualification before its ordinary merge. This decision authorizes no release or deployment.

Run a visible monthly and manually callable Python 3.15 canary on Linux, macOS and Windows. Resolve
the complete declared dependency set separately from the package's unsupported Python metadata,
report dependency/import outcomes, and exercise the public Hong Kong calendar and explicitly
unsupported source workflows. An ordinary install rejected solely by the package's own Python
upper bound is not dependency evidence. A passing source probe does not qualify an installed wheel.

Remove the bound and exception only after normal installed-artifact, complete source and applicable
provider/calendar workflows pass on all three systems using a new supported candidate. An extension
beyond the deadline or another release line needs a fresh evidence-backed decision. Reuse issue 2
for the upstream wait; the runtime integration remains owned by Live issue 145 and PR 146.

The existing built-candidate validator enforces the library, repository, version and expiry scope.
No shared validator, supported matrix or release criterion is weakened.
