# Decision 0009: Optional development sidecars

**Status**: Accepted
**Date**: 2026-09-08

## Decision

`development_workspace` is optional in the ecosystem inventory. When omitted, workspace
qualification checks the public release checkout and records that no sidecar is required. It does
not create or infer a development repository.

Specs remains one of the seven qualified libraries with no development sidecar. Its work is managed
from `ml4t/ecosystem` and `ml4t-specs`, and the reusable library prompt identifies that exception.

## Consequences

Stable-library qualification no longer equates membership with a mandatory private repository.
Specs keeps full package, documentation, workflow, and public-orientation checks without twelve
false sidecar failures or an empty repository created only to satisfy configuration.
