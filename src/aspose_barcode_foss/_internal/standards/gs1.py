"""GS1 helper models and interfaces."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Gs1ApplicationIdentifier:
    """One GS1 application identifier."""

    value: str


@dataclass(slots=True, frozen=True)
class Gs1ElementString:
    """One GS1 element string."""

    application_identifier: Gs1ApplicationIdentifier
    data: str


@dataclass(slots=True, frozen=True)
class Gs1Message:
    """Structured GS1 payload produced by the parser layer."""

    elements: tuple[Gs1ElementString, ...]


class Gs1Helper:
    """Parse and validate GS1 payloads."""

    def parse(self, value: str) -> Gs1Message:
        """Parse a public GS1 string into a structured payload."""
        raise NotImplementedError

    def validate(self, message: Gs1Message) -> None:
        """Validate a structured GS1 payload."""
        raise NotImplementedError
