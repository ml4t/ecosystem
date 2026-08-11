# Issues and pull requests

GitHub is the authoritative work record after an internal request is accepted. A local Markdown file
may be a draft but cannot be the only record for accepted work.

## Intake

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

## Implementation

Every non-automated user-visible change and defect fix has an associated issue. Its pull request uses
a closing reference. Automated dependency updates and administrative metadata changes are exempt.
External pull requests may use their own complete description as the issue record when the repository
accepts and links it explicitly.

Automation may report, classify, and update work records with approved credentials. It never writes
to library branches. Code and documentation changes use the owning repository's pull-request process.
