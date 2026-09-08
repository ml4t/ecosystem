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

Pull requests run dependency review and static security analysis with the repository's supported
languages. The default branch and release candidate run a vulnerability scan of the resolved runtime
and build dependencies. A release fails for an unapproved high or critical finding. Any temporary
exception identifies the advisory, affected versions, mitigation, approver, and expiration date.

Workflow permissions default to `contents: read` and are widened only on the job that needs them.
Every third-party action and reusable workflow is pinned to a full commit SHA, with the release
version recorded in a comment for review. Publication uses GitHub environments and PyPI trusted
publishing rather than a long-lived upload token. Secrets are available only to the protected job
that consumes them and never to pull-request code from an untrusted fork.

Each library enables GitHub private vulnerability reporting and documents it in `SECURITY.md`.
Security fixes use coordinated disclosure. Public issues must not contain unpublished exploit details
or credentials.
