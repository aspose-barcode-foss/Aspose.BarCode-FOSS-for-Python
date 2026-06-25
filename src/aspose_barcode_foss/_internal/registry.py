"""Registry for concrete symbology definitions."""

from __future__ import annotations

from dataclasses import dataclass

from aspose_barcode_foss._internal.encoders.base import SymbologyEncoder
from aspose_barcode_foss._internal.exceptions import SymbologyNotFoundError
from aspose_barcode_foss._internal.parsers.base import InputParser
from aspose_barcode_foss._internal.profiles.base import SymbologyProfile
from aspose_barcode_foss._internal.text.base import TextLayoutPolicy


def _normalize_registered_name(name: str) -> str:
    """Normalize a canonical name or alias for registry storage."""
    if not isinstance(name, str):
        msg = "symbology names must be strings"
        raise ValueError(msg)

    normalized_name = name.strip().lower()
    if not normalized_name:
        msg = "symbology names must not be blank"
        raise ValueError(msg)
    return normalized_name


@dataclass(slots=True, frozen=True)
class SymbologyDefinition:
    """Bundle the components required to support one symbology."""

    name: str
    parser: InputParser
    encoder: SymbologyEncoder
    profile: SymbologyProfile
    aliases: tuple[str, ...] = ()


class SymbologyRegistry:
    """Store complete symbology definitions keyed by canonical ids and aliases."""

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._definitions: dict[str, SymbologyDefinition] = {}
        self._lookup_names: dict[str, str] = {}

    def get_definition(self, name: str) -> SymbologyDefinition:
        """Return the definition registered for a symbology name."""
        if not isinstance(name, str):
            msg = f"unknown symbology: {name!r}"
            raise SymbologyNotFoundError(msg)

        normalized_name = name.strip().lower()
        canonical_name = self._lookup_names.get(normalized_name)
        if canonical_name is None:
            msg = f"unknown symbology: {name!r}"
            raise SymbologyNotFoundError(msg)
        return self._definitions[canonical_name]

    def get_parser(self, name: str) -> InputParser:
        """Return the input parser registered for a symbology name."""
        return self.get_definition(name).parser

    def get_encoder(self, name: str) -> SymbologyEncoder:
        """Return the encoder registered for a symbology name."""
        return self.get_definition(name).encoder

    def get_profile(self, name: str) -> SymbologyProfile:
        """Return the profile registered for a symbology name."""
        return self.get_definition(name).profile

    def get_text_policy(self, name: str) -> TextLayoutPolicy:
        """Return the text layout policy registered for a symbology name."""
        return self.get_definition(name).profile.text_policy

    def register(self, definition: SymbologyDefinition) -> None:
        """Register a complete symbology definition."""
        canonical_name = _normalize_registered_name(definition.name)
        normalized_aliases = tuple(_normalize_registered_name(alias) for alias in definition.aliases)

        new_lookup_names = {canonical_name}
        for alias in normalized_aliases:
            if alias in new_lookup_names:
                msg = f"duplicate symbology name or alias in definition: {alias!r}"
                raise ValueError(msg)
            new_lookup_names.add(alias)

        conflicting_name = next(
            (lookup_name for lookup_name in new_lookup_names if lookup_name in self._lookup_names),
            None,
        )
        if conflicting_name is not None:
            msg = f"duplicate symbology name or alias: {conflicting_name!r}"
            raise ValueError(msg)

        stored_definition = SymbologyDefinition(
            name=canonical_name,
            aliases=normalized_aliases,
            parser=definition.parser,
            encoder=definition.encoder,
            profile=definition.profile,
        )
        self._definitions[canonical_name] = stored_definition
        self._lookup_names[canonical_name] = canonical_name
        for alias in normalized_aliases:
            self._lookup_names[alias] = canonical_name


class EncoderRegistry(SymbologyRegistry):
    """Backward-compatible alias for the earlier registry name."""
