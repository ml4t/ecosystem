# Release qualification

A stable library release requires evidence for all applicable criteria:

- compatibility matrix;
- public imports and typed interfaces;
- unit, integration, regression, and contract tests appropriate to the library;
- package build and installation from artifacts;
- dependency and vulnerability review;
- strict documentation build and deployed identity;
- consistent source, wheel, PyPI, documentation, and release metadata;
- backward-compatibility assessment and release notes; and
- no unresolved critical or high-priority correctness finding affecting the release.

The library's default branch must pass the current ecosystem qualification before a tag can publish.
A local library check cannot substitute for a failed shared check.

An exception is valid only when it records:

- the exact criterion and affected library versions;
- evidence explaining why the exception is necessary;
- user impact and mitigation;
- the approving maintainer;
- an expiration date; and
- the issue that removes the exception.

Expired or incomplete exceptions fail qualification. Validation occurs before publication, so a
rejected release does not create a tag, artifact, GitHub release, or PyPI upload.
