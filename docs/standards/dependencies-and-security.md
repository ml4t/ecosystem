# Dependencies and security

Dependencies must have a current, documented purpose and a supported release compatible with the
Python and operating-system matrix. Remove unused dependencies and avoid duplicating capabilities
already provided by a required dependency without a measured reason.

Release qualification checks:

- dependency resolution on every supported Python version;
- direct URL, prerelease, yanked, and unbounded dependency declarations;
- known vulnerabilities in runtime and build dependencies;
- license compatibility;
- optional dependency isolation; and
- reproducible source and wheel metadata.

Each library enables GitHub private vulnerability reporting and documents it in `SECURITY.md`.
Security fixes use coordinated disclosure. Public issues must not contain unpublished exploit details
or credentials.
