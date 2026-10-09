# ML4T Ecosystem Agent Guide

This repository owns shared standards, qualification evidence, documentation rules, and coordinated
work management for the stable ML4T libraries. It does not own their source code or Git histories.

## Managed Libraries

| Library | Public repository | Import package | Local release checkout | Development workspace |
|---|---|---|---|---|
| Data | `ml4t/data` | `ml4t.data` | `ml4t-data/` | `ml4t-data-dev/` |
| Engineer | `ml4t/engineer` | `ml4t.engineer` | `ml4t-engineer/` | `ml4t-engineer-dev/` |
| Backtest | `ml4t/backtest` | `ml4t.backtest` | `ml4t-backtest/` | `ml4t-backtest-dev/` |
| Specs | `ml4t/specs` | `ml4t.specs` | `ml4t-specs/` | none, managed from here |
| Live | `ml4t/live` | `ml4t.live` | `ml4t-live/` | `ml4t-live-dev/` |
| Diagnostic | `ml4t/diagnostic` | `ml4t.diagnostic` | `ml4t-diagnostic/` | `ml4t-diagnostic-dev/` |
| Models | `ml4t/models` | `ml4t.models` | `ml4t-models/` | `ml4t-models-dev/` |

Repositories outside this table are not covered by stable-library qualification.

**Specs has no development workspace and is not getting one.** It is small enough
that its work is managed directly from this repository and from its own
`ml4t-specs/` checkout, which carries public agent orientation in `AGENTS.md`.
Every other library's sandbox config grants write access to
`ml4t-specs/`, so agents reach it from wherever they are working. Do not create
`ml4t-specs-dev/`; if the volume of specs work ever justifies one, change this
paragraph first.

## Reloaded Maintenance

The shared contributor policy also covers these independent repositories. Their own maintenance
agents own queues, reproductions, reviews, fixes, CI and documentation. Support covers bug,
security and compatibility fixes and preserves existing docs. Direct new features to current ML4T
libraries. They retain native qualification and documentation workflows; the current-library matrix
below does not automatically apply.

| Public repository | Sibling release checkout | Private workspace | Migration partner |
|---|---|---|---|
| `stefan-jansen/zipline-reloaded` | `zipline-reloaded/` | `zipline-reloaded-dev/` | Backtest |
| `stefan-jansen/pyfolio-reloaded` | `pyfolio-reloaded/` | `pyfolio-reloaded-dev/` | Diagnostic |
| `stefan-jansen/alphalens-reloaded` | `alphalens-reloaded/` | `alphalens-reloaded-dev/` | Diagnostic |
| `stefan-jansen/empyrical-reloaded` | `empyrical-reloaded/` | `empyrical-reloaded-dev/` | Diagnostic |

## Local Repository Model

The parent directory is a plain container, not a Git repository. Its children are independent
checkouts:

- `ml4t-ecosystem/` is this public standards and qualification repository.
- `ml4t-dev/` is the private coordinator workspace for shared setup, routing and cross-library work.
- `ml4t-{library}/` is the local checkout of the public release repository. Its default branch,
  tags, workflows, package metadata, and release history belong to that library.
- `ml4t-{library}-dev/` is a private development workspace for agent instructions, work units,
  research, issue drafts, and transitions. It may direct changes into the sibling release checkout.
- Additional directories with suffixes such as a feature name are temporary worktrees or historical
  workspaces. Inspect their Git metadata before using them.
- Reloaded release checkouts and their private sidecars follow the table above.
- Never add a sibling repository or private workspace to this repository.

The coordinator owns shared policy and infrastructure. Individual library agents own their source
work and maintenance queues. Specs remains managed without a dedicated sidecar. Migration partners
provide expertise and measured evidence; they do not take ownership of the Reloaded queues.

Before changing a library, read both this file and the target library or development workspace
`AGENTS.md`. The more specific instructions apply within that repository.

Each current library's release checkout also carries `docs/book-guide/index.md`: the authoritative
chapter-to-API cross-reference (book notebook -> concept -> library API -> docs page). An agent
mapping a book chapter to a library's surface should read that file first, not grep the seven repos.

## Sources of Truth

Use these authorities in order:

1. PyPI metadata for the currently published package.
2. The library's GitHub default branch for current source and workflows.
3. The library's root `AGENTS.md` for repository-specific commands and constraints.
4. `docs/standards/` in this repository for requirements shared by all libraries.
5. `status/` and `reviews/` for current and dated cross-library evidence.
6. The private development sidecar for agent state. It is not public policy.

Do not treat a stale local tag, feature branch, development-workspace issue draft, or copied status
table as current release evidence.

## Local agent state

Shared coordinator memory, active work, transitions and agent-specific configuration belong in
the sibling private `ml4t-dev/` checkout. Library state belongs in its own sidecar. Curated memory
is read on demand; each sidecar includes only its memory index. This public guide does not include
private memory or depend on a private checkout being present for contributors.

## Standard Work Lifecycle

Accepted internal requests and public user reports use the same accountable flow:

1. Confirm the owning library and search its open and closed GitHub issues.
2. Reproduce bugs through the public API or user workflow before diagnosing them.
3. Create or update the owning GitHub issue using the standard intake fields. Local Markdown is
   draft material only.
4. Work on a library feature branch or isolated worktree. Preserve unrelated local changes.
5. Run the library's full documented quality gates plus applicable ecosystem qualification.
6. Commit coherent checkpoints with plain `git commit`; never bypass hooks.
7. Push the feature branch and open a pull request that closes the issue.
8. Address review and CI failures, merge according to repository policy, and verify the default
   branch.
9. Publish a patch release when users need the fix in an installable artifact.
10. Refresh ecosystem evidence and close the cross-library tracking issue only after verification.

Automated dependency updates and administrative metadata changes do not require a separate issue.
User-visible changes and defect fixes do.

## Issue and Pull-Request Monitoring

The ecosystem qualification monitor covers the seven current repositories. Dedicated maintenance
agents monitor the four Reloaded queues using their own repository identities and native checks.
Both follow the shared contributor policy and prepare advisory recommendations for approval.

- Classify each new item within one hour using the shared type, priority, status, affected-version,
  and compatibility-impact vocabulary.
- Provide a substantive maintainer response or explicit pending-review status within two business
  days.
- Route suspected vulnerabilities to GitHub private vulnerability reporting. Do not request or
  publish exploit details in a public issue.
- Keep automation read-only against library branches. Changes use library pull requests.
- Update a shared standard or decision when a lesson affects multiple libraries or changes a shared
  release criterion.

See `docs/standards/issues-and-pull-requests.md` for the normative requirements.

## Documentation Process

Each library owns its tutorials, how-to guides, reference pages, explanations, examples, and API
documentation. The ecosystem repository owns the common process and index.

The requirements below apply to current libraries. Reloaded libraries preserve their existing
Sphinx documentation and deployment routes; changes to those are owned by their maintenance agent.

- Use MkDocs with the shared ML4T theme and navigation conventions.
- Run `uv run mkdocs build --strict` for every documentation change and release.
- Publish each library under its assigned `https://ml4trading.io/docs/{library}/` route.
- Validate internal links, navigation entries, code examples, package identity, and deployed route.
- Keep user documentation in the release repository. Do not move API content into this repository.
- Update the ecosystem index when a library, route, or adoption path changes.

See `docs/standards/documentation.md` for the deployment contract and required content categories.

## Compatibility and Release Qualification

Each current library must pass installation, import, tests, type checking, and package builds on Python 3.12
through 3.14 on Linux, macOS, and Windows. Python 3.15 prereleases must pass core installation and
non-hardware-dependent tests on all three systems unless a dependency-blocked library has a
configured prerelease wait. A waiting library keeps a truthful upper bound and runs a visible
non-blocking canary at least monthly.

An ecosystem failure blocks the affected release unless an approved exception records its scope,
rationale, approver, and an expiration date or objective review triggers. Hardware-specific features
use separate matrices.

See `docs/standards/compatibility.md` and `docs/standards/release-qualification.md`.

## Ecosystem Repository Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest -q
uv run mkdocs build --strict
pre-commit run --all-files
```

Install hooks once with `pre-commit install`. Commit at coherent passing checkpoints, without waiting
to be asked.

`ml4t/ecosystem` and the separate library repos are **public**, so a push here is a publication to
outside contributors and downstream users, not a backup. Confirm before pushing unless the active
task already authorizes publication. This is the narrow exception to the standing "push private repos
freely" rule in `~/.claude/CLAUDE.md`; it applies because these repos are public, not because pushing
is risky in general.

## Public Repository Boundary

This repository remains public because contributors to the seven public libraries need one visible
source for shared standards, security reporting, compatibility decisions, and independently
executable qualification checks. `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `docs/standards/`,
and `decisions/` are the contributor-facing policy surface. `config/`, `src/`, `tests/`, `status/`,
and `reviews/` provide the inventory, implementation, and public evidence behind that policy.

Internal planning, transitions, memory, credentials, and private security material stay in ignored
`.workspace/` state or the private development sidecars. Do not add internal operational detail to
tracked files merely because the repository is public.

## Safety

- Never commit `.env`, credentials, private security reports, `.claude/`, `.workspace/`, `.codex/`,
  nested repositories, or development workspaces.
- Never edit generated current-status files by hand. Regenerate them through the status command.
- Never weaken a shared check inside a library to make CI pass. Change the shared standard through a
  reviewed ecosystem decision when the requirement itself is wrong.
- Never modify auto-generated changelogs manually.
