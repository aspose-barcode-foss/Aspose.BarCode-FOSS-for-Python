"""ECI helper models and interfaces."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class EciDesignator:
    """Normalized ECI designator."""

    assignment_number: int
    name: str | None = None


class EciHelper:
    """Validate and normalize ECI metadata."""

    def normalize(self, value: int | str) -> EciDesignator:
        """Normalize a public ECI value into an internal designator."""
        raise NotImplementedError

    def validate(self, designator: EciDesignator) -> None:
        """Validate an internal ECI designator."""
        raise NotImplementedError
