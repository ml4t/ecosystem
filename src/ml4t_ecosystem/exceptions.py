"""Qualification exception validation."""

from __future__ import annotations

from datetime import date

from ml4t_ecosystem.models import EcosystemConfig, QualificationException


def validate_exception(
    config: EcosystemConfig,
    *,
    exception_id: str,
    library_key: str,
    repository: str,
    on_date: date,
) -> QualificationException:
    """Validate an exception against its library, repository, and expiration."""
    library = config.library(library_key)
    exception = config.exception(exception_id)
    if library.prerelease_exception != exception.id or library.key not in exception.libraries:
        raise ValueError(f"exception {exception.id} does not cover library {library.key}")
    expected_repository = f"{config.owner}/{library.repository}"
    if repository != expected_repository:
        raise ValueError(
            f"repository {repository} does not match repository {expected_repository} "
            f"for {library.key}"
        )
    if not exception.is_active(on_date):
        raise ValueError(f"exception {exception.id} expired on {exception.expires_on.isoformat()}")
    return exception
