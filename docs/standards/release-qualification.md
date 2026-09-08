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

## Pull-request and default-branch gates

Every file named by `required_workflow_files` in `config/libraries.toml` exists. Pull requests and
pushes to `main` run, at minimum:

- locked dependency installation with `uv`;
- `ruff` lint and format checks;
- `ty` type checking;
- the repository's unit, integration, regression, and contract tests with its enforced coverage
  threshold;
- a strict documentation build;
- source distribution and wheel builds followed by artifact metadata validation; and
- the central supported and prerelease Python and operating-system qualification matrix.

Workflows cancel superseded branch runs without cancelling a release or production documentation
deployment. Required checks retain stable names so branch protection cannot silently stop enforcing
them. A green default branch is necessary but does not replace qualification of the release commit.

## Commit-bound release process

A release workflow accepts an explicit version and candidate commit, then verifies that the commit
is the intended `main` revision and that the version is absent from Git tags, GitHub releases, and
PyPI. It performs these steps in order:

1. run all release and ecosystem qualification against the candidate commit;
2. build the source distribution and wheel once;
3. install the wheel in a clean environment and verify its public import, version, README quick
   start, license, and canonical metadata;
4. record a manifest containing the version, candidate commit, artifact names, and SHA-256 digests;
5. deploy documentation built from that commit and verify its canonical route and displayed
   library, version, and revision;
6. publish the already verified artifacts to PyPI through trusted publishing;
7. create the Git tag and GitHub release for the same commit, attaching those artifacts and the
   manifest; and
8. verify the PyPI metadata, install the published wheel, check the GitHub release digests, and
   repeat the deployed-documentation identity check.

No later job rebuilds an artifact. A failure before publication creates no tag, GitHub release, or
PyPI version. A failure after an irreversible publication stops further publication and records a
recovery issue; it never reuses the version for different bytes.

Metadata qualification compares the values from the tagged source, built source distribution,
built wheel, PyPI JSON response, GitHub repository settings, and deployed documentation. A mismatch
fails qualification even when each value is individually plausible. The canonical identity,
required fields, and allowed contact domains come from `config/libraries.toml`.

Deprecated public identifiers are allowed only when the library inventory names them explicitly and
the release provides a tested replacement path, a runtime deprecation warning, and migration
documentation. No new example or primary documentation may recommend a deprecated identifier.

## Agent orientation

Every public release repository has a root `AGENTS.md` for an external agent trying to understand
the library from a source checkout. It states the library's responsibility, identifies the source
tree and major subsystems, names supported public imports or workflows, points to deeper guides when
they exist, and gives the authoritative quality commands. The workspace audit checks for substantive
sections, the configured import package, source-tree navigation, and an executable import or quality
command. A placeholder file, tool-mechanism explanation, or import of private workspace state fails.

The public root file stays below 200 lines and contains no internal work management, volatile file or
test counts, status snapshots, detailed API documentation, or tutorials. Nested `AGENTS.md` files are
justified when they provide subsystem orientation or rules that differ within their directory and do
not repeat the root. Public repositories do not track `CLAUDE.md`, `.claude/`, `.codex/`, or
`.workspace/`; those are local agent plumbing rather than library orientation.

An instruction audit reports obsolete, duplicated, missing, or misplaced content and presents the
exact proposed edits. Editing an `AGENTS.md` or `CLAUDE.md` requires the user's explicit approval of
that reported scope. Approval for a library's instruction files does not authorize user-level or
other repositories' instruction changes.

## Development sidecars

Each library may name one private, independent `ml4t-{library}-dev` Git repository next to its public
release checkout. A configured sidecar contains agent instructions, research, issue drafts, and
local work state. It must have:

- a configured `origin` whose repository visibility has been verified as private;
- a clean worktree synchronized with its upstream before handoff;
- root `AGENTS.md` and the one-line `CLAUDE.md` import;
- `issues/` for local drafts that are not yet accepted work;
- `.workspace/work/` for active specifications and plans;
- `.workspace/transitions/` for session handoffs; and
- `.workspace/memory/MEMORY_INDEX.md` as the only automatically included memory file.

Sidecar contents are never copied into the public release repository or ecosystem evidence. Existing
untracked files, unpushed commits, and branches are user work: inspect and preserve them, then commit,
push, merge, or ask about genuinely ambiguous work instead of deleting or hiding it.

Run `uv run ml4t-ecosystem audit-workspaces` from the ecosystem checkout to report local topology,
instruction imports, origin configuration, cleanliness, and synchronization. The report records
paths and results only, never private file contents. Repository visibility is verified separately
with authenticated GitHub metadata because a local remote URL does not prove visibility.

An omitted `development_workspace` means the library is managed directly from the ecosystem and
release checkouts. The audit records that no sidecar is required and does not synthesize one. Specs
uses this exception because its runtime-neutral contract work is small and already writable from the
other library development sandboxes.

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
