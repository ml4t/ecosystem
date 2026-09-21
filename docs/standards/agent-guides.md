# Agent guides

This page is the reference standard for public `AGENTS.md` files in the seven stable library
repositories. Public guides help an external contributor understand a source checkout. Private
sidecars hold agent configuration, work management, and persistent local state.

## Root guide

Every public library tracks one root `AGENTS.md`, no longer than 200 lines. It must identify:

- the library's responsibility and public import package;
- the source tree, tests, documentation, examples, scripts, and major subsystems that exist;
- supported public imports or user workflows;
- compatibility and safety rules that affect changes;
- narrower nested guides, when they exist; and
- the repository's current `ruff`, format, `ty`, `pytest`, documentation, build, and pre-commit
  commands as applicable.

The guide points to authoritative code or documentation instead of copying API reference or
tutorial content. It does not include current work, issue queues, test or file counts, release
status, machine paths, credentials, or private sidecar content.

## Nested guides

A nested `AGENTS.md` is optional. Add one only when its directory has a distinct responsibility,
public surface, safety rule, compatibility constraint, or verification lane that the root guide
cannot state concisely. A nested guide:

- names its directory or subsystem in the title;
- states the directory's responsibility and the rules that differ there;
- inherits repository-wide commands and rules instead of repeating them;
- stays below 120 lines and contains no volatile counts or status snapshots; and
- is removed when the directory no longer needs narrower guidance.

No repository creates empty or placeholder guides for discovery. The conformance audit discovers
tracked files, so an absent nested guide means the root guide applies.

## Claude interoperability

Public repositories do not track `CLAUDE.md`. A one-line `@AGENTS.md` include configures one tool but
does not help a contributor understand the library. Public repositories also ignore `.claude/`,
`.codex/`, and `.workspace/` so local configuration cannot be published by a broad Git add.

Each configured private development sidecar tracks `AGENTS.md` as its canonical instructions and a
`CLAUDE.md` containing exactly `@AGENTS.md`. Sidecar instructions may describe local work, issue
drafts, transitions, memory, and cross-repository coordination because the sidecar is private.

## Maintenance triggers

Review the root guide when a change alters the package responsibility, supported public import,
repository layout, quality commands, release process, compatibility policy, or safety boundary.
Review an affected nested guide when a subsystem moves, gains or loses a public surface, changes a
local constraint, or changes its focused verification lane. Deleting a subsystem also deletes its
guide.

An ordinary implementation change does not require prose churn when these facts stay the same.
Reviewers compare the guide with the changed source and commands rather than updating dates or
counts.

## Conformance

`uv run ml4t-ecosystem audit-workspaces` discovers tracked guides in each local release checkout. It
checks root structure, public import and source-tree references, required quality commands, line
limits, private-state references, tool-mechanism prose, volatile counts, nested titles, and exact
duplicate nested content. The GitHub and PyPI collector applies the root checks to each default
branch.

Automated checks cannot establish that a guide names the correct public surface. Each library audit
therefore compares the guide with its installed package, documentation, workflow commands, and
tracked nested files. A deviation uses an issue and pull request in the owning library.
