# Data recovery reconciliation

Date: 2026-09-20

Scope: dormant Data standardization worktree, local standardization branches, merged Data pull
request [#55](https://github.com/ml4t/data/pull/55), and the private recovery set captured on
2026-09-19.

## Result

The dormant state contains no requirement that should replace current Data `main`. Pull request #55
implements the accepted issue #50 scope and adds release, security, documentation, and agent-guide
changes that the local branches lack. The remaining worktree differences are either byte-identical
to `main` or older content that current `main` intentionally replaced.

## Recovery verification

The recovery bundle passes `git bundle verify` and contains the complete
`codex/ecosystem-standardization` history at `a907fbf`. All four recorded SHA-256 checksums match the
live worktree:

- branch bundle: `bf91f6c6154f2d355aef2350ffd222f51e6a997e4e6ae147601be0077e1412c3`;
- staged patch: `2784a3356395816492dc01fc8841af417b0ffdac679c6935acb71cc79a9e8504`;
- unstaged patch: `b9ef69c080f23c07359044984a7d37824fd8c6ece96473eeb34989c8c2dd10a8`;
- untracked migration file: `1223a375b348dd915744936823f118f4bc106972b531ccf3573bef2e89c4b44e`.

A clean temporary clone reconstructed from the bundle, staged patch, unstaged patch, and untracked
file produced the same staged diff, unstaged diff, untracked-file digest, and short status as the
live worktree.

## Requirement disposition

| Recovered work | Disposition |
|---|---|
| Canonical package identity, `QLDM_DATA_ROOT`, and `QldmError` compatibility | Present on current `main` through pull request #55, with stronger discovery and precedence tests. |
| `ML4T_DATA_DIR` and `QLDM_LOG_LEVEL` compatibility proposed by `a907fbf` | Not accepted. Data issue #50 explicitly limited compatibility to `QLDM_DATA_ROOT` and `QldmError`; pull request #55 removed the other names from the public contract. |
| Five `codex/issue-50-standardization` commits | Superseded by pull request #55. Its reviewed head contains the same standardization tree plus newer workflow, security, documentation, agent-guide, and provider fixes. |
| Twenty-six staged documentation and example deletions | All twenty-six paths are absent from current `main`. |
| Sixty-six unstaged modifications | Fifty-six are byte-identical to current `main`. |
| Ten non-identical unstaged paths | Rejected as older content: a weaker alias-removal promise, stale getting-started material, unsupported production wording, incomplete metadata punctuation, weaker empty-environment handling, provider typos, removal of the Yahoo rate-limit fix, and removal of compatibility tests. |
| Untracked migration guide | Superseded by the current guide, which adds the 0.x compatibility guarantee and otherwise contains the same migration. |

The two local branch tips and the worktree registration are obsolete. The verified recovery set
remains the recoverable source for the discarded dirty state.
