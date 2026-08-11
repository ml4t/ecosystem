# API compatibility

Stable releases preserve documented public imports, signatures, types, configuration semantics,
serialized formats, lifecycle ordering, and observable error behavior within a minor version line.

An incompatible change requires:

- evidence that compatibility cannot be preserved without compromising correctness or security;
- an ecosystem-visible compatibility assessment when multiple libraries are affected;
- a deprecation period when the old behavior can remain safely available;
- migration documentation and tests for the supported transition; and
- an appropriate version change under the repository's versioning policy.

Shared trading and lifecycle contracts remain in `ml4t-specs`. Backtest and live implementations
must demonstrate the same contract semantics rather than maintaining undocumented parallel APIs.

Removing accidental complexity is encouraged when tests establish unchanged public behavior. A
simplification is not compatible merely because its output is usually similar; boundary cases,
failure behavior, ordering, and persisted data are part of the assessment.
