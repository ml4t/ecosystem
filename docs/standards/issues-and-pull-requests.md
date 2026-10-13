# Issues and pull requests

GitHub is the authoritative work record after an internal request is accepted. A local Markdown file
may be a draft but cannot be the only record for accepted work.

Each private development sidecar keeps unaccepted drafts under `issues/`. Once work is accepted,
create or update the issue in the owning public library repository and link subsequent pull requests
there. The ecosystem repository holds only cross-library standards, qualification, or coordination
issues. It does not duplicate an owning library's implementation issue.

## Intake

The [contribution policy](https://github.com/ml4t/ecosystem/blob/main/CONTRIBUTING.md) applies to
the current ML4T and maintained Reloaded libraries. Each issue describes one problem or coherent
change; unrelated problems require separate issues. Each PR addresses its owning issue. A bundle
of unrelated fixes is not made focused by collecting them in one issue.

All libraries provide compatible forms for bugs, features, and documentation problems. Intake
records the affected version, environment, observed and expected behavior, reproduction evidence
where applicable, compatibility impact, and acceptance criteria.

Suspected vulnerabilities use private vulnerability reporting and never require public exploit
details.

## Classification and response

Every new issue and pull request receives the shared type, priority, status, affected-version, and
compatibility-impact classification within one hour. Within two business days, a maintainer provides
a substantive response or applies `status: pending-review` and states the next review point.

Library-specific labels may extend the vocabulary but may not redefine shared labels.

`uv run ml4t-ecosystem monitor --output status/monitor.json` collects the full open queues in
`config/maintained-repositories.toml`, using each repository's explicit GitHub owner and name.
This maintenance inventory includes the seven current libraries and four Reloaded libraries;
`config/libraries.toml` continues to define only the seven-library qualification scope.
The existing audit workflow runs nominally hourly. Each report records when evidence was actually
collected, complete paginated queues, and current PR head/base revisions. Collection is metadata
inspection, not a code review or executed verification.

The command exits zero when collection is complete with no response-target findings, one when
findings need attention, and two when API evidence is incomplete. An incomplete repository must not
be interpreted as an empty queue or used to infer that an item closed. The report retains evidence
errors alongside successfully collected repositories. Downstream advisory tools must key items by
full repository identity and number, and re-evaluate a changed PR revision before reusing a review.

## Implementation

Every non-automated user-visible change and defect fix has an associated issue. Its pull request uses
a closing reference. Automated dependency updates and administrative metadata changes are exempt.
External pull requests may use their own complete description as the issue record when the repository
explicitly accepts it during triage of an existing submission. This is an intake exception, not the
default process for new submissions, and does not waive focused scope or verification.

Bug fixes include executed evidence that the same regression fails on the relevant base and passes
with the correction through a real public API or user workflow. Contributors disclose AI assistance
and remain accountable for code and prose. Verified numerical defects are corrected; changes to
intended conventions require agreement on expected behavior and compatibility impact in the owning
issue. Preserving an existing output is not a reason to retain a verified defect.

Shared maintenance automation prepares triage and review recommendations for maintainer approval.
It records the revision inspected and distinguishes metadata inspection, diff inspection, and
executed verification. Missing API or runner evidence is reported as missing evidence. Automated
recommendations do not post comments or reviews, apply labels, approve runs, close items, merge,
publish, or write to library branches. Code and documentation changes use the owning repository's
pull-request process.
