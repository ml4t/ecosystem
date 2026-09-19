# Decision 0011: Public library repository settings

**Status**: Accepted
**Date**: 2026-09-19
**Approver**: Stefan Jansen

## Context

The seven stable library repositories had the required status checks, but their surrounding GitHub
settings differed. Only Specs and Models required linear history, conversation resolution, and
administrator compliance with branch protection. Models alone required immutable action references
at the repository level. Backtest alone enabled secret scanning and push protection. Dependabot
security updates were enabled only for Diagnostic and Models.

The repositories need one baseline that keeps automated qualification mandatory without requiring a
second person to approve maintainer-owned changes. The baseline must also leave repository-specific
status checks and existing review rules intact.

## Decision

Apply these settings to each stable public library:

- allow squash and rebase merges, but not merge commits;
- delete a pull-request branch after merge;
- protect `main` with strict required status checks, linear history, conversation resolution, and
  administrator enforcement;
- deny force pushes and branch deletion on `main`;
- preserve every configured required check, branch restriction, and pull-request review rule;
- allow all GitHub Actions and reusable workflows, but require every non-local action reference to
  use a full commit SHA;
- enable Dependabot alerts and security updates; and
- enable secret scanning and push protection.

The shared baseline does not require a human approval. A repository may retain or add stricter
review rules when its risk warrants them. Release environments and their reviewers are outside this
decision and remain unchanged.

## Consequences

Agents can open and merge a qualifying pull request without waiting for another reviewer. GitHub
still blocks a merge until all repository-specific checks pass and every conversation is resolved.
Main stays linear, and GitHub removes merged branches automatically.

Repositories may use any action without an allowlist update, but the repository-level SHA rule
prevents mutable tag references. Dependabot security pull requests and secret push protection add
automated security controls without adding a standing review requirement.
