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

The next CPython prerelease enters CI after beta 1. Before final release, core installation and the
non-hardware-dependent tests must pass on Linux, macOS, and Windows. Prerelease support is tested but
not advertised as stable.

When that CPython release becomes final, it joins the supported matrix and failures block releases.
Dropping an older Python version requires an ecosystem decision and a documented deprecation period.

For releases before 2026-10-01, the stable matrix is Python 3.12 through 3.14 and the blocking
prerelease target is Python 3.15. A package metadata upper bound that prevents installation on the
prerelease target fails this standard.

A library may temporarily retain an upper bound only through a machine-readable exception in
`config/libraries.toml`. The exception replaces the prerelease jobs with an explicit validation job;
it does not remove the stable operating-system matrix. The validation fails when the exception is
missing, applied to another repository, outside its version scope, or expired.

Hardware-specific capabilities such as CUDA require a separate matrix. Passing the general matrix
does not establish hardware support.

The shared matrix is a minimum, not a replacement for capability-specific tests. A library keeps
its applicable provider, broker, licensed-framework, paper-trading, recovery, performance, and
hardware checks. Secrets or unavailable hardware may move those checks to protected environments,
but must not be replaced with mocks that only restate the implementation.
