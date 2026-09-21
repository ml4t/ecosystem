# Compatibility

ML4T libraries support every stable CPython release from Python 3.12 through the latest stable
version on Linux, macOS, and Windows.

Each supported Python and operating-system combination must pass:

1. dependency resolution and installation from the built wheel;
2. public-package import;
3. the non-hardware-dependent test suite;
4. `ruff` lint and format checks;
5. `ty` type checking; and
6. source distribution and wheel builds with metadata validation.

The next CPython prerelease enters CI after beta 1. Libraries whose complete dependency sets install
on the prerelease run blocking core installation and non-hardware-dependent tests on Linux, macOS,
and Windows. Prerelease support is tested but not advertised as stable.

A dependency-blocked library keeps a truthful `Requires-Python` upper bound and runs a visible
non-blocking canary at least monthly. Its configured prerelease wait records the affected release
line, evidence, user impact, mitigation, owner issue, and objective review triggers. A trigger starts
a new review; it does not claim compatibility or block an otherwise qualified stable release.

When that CPython release becomes final, it joins the supported matrix for libraries without an
approved wait. A waiting library reviews fresh qualification evidence when final ships and records
whether the wait can end. Dropping an older Python version requires an ecosystem decision and a
documented deprecation period.

For releases before Python 3.15 is qualified across a library's complete dependency set, the stable
matrix is Python 3.12 through 3.14. Python 3.15 remains a blocking target for libraries without a
configured prerelease wait.

A library may temporarily retain an upper bound only through a machine-readable exception in
`config/libraries.toml`. The `prerelease_exception` name remains in the configuration and reusable
workflow for compatibility. For a trigger-based wait, the validation fails when the record is
missing, applied to another repository, outside its release-line scope, or lacks review triggers.
The wait never removes the stable operating-system matrix.

Hardware-specific capabilities such as CUDA require a separate matrix. Passing the general matrix
does not establish hardware support.

The shared matrix is a minimum, not a replacement for capability-specific tests. A library keeps
its applicable provider, broker, licensed-framework, paper-trading, recovery, performance, and
hardware checks. Secrets or unavailable hardware may move those checks to protected environments,
but must not be replaced with mocks that only restate the implementation.
