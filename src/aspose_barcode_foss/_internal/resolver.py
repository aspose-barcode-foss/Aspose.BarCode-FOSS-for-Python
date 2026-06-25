"""Option resolution for rendering."""

from __future__ import annotations

from dataclasses import fields
from math import isfinite
from numbers import Integral, Real

from aspose_barcode_foss._internal.exceptions import InvalidInputError
from aspose_barcode_foss._internal.models.options import RenderOptions, ResolvedRenderOptions
from aspose_barcode_foss._internal.profiles.base import SymbologyProfile

_RENDER_OPTION_FIELDS = tuple(field.name for field in fields(RenderOptions))
_STRING_RENDER_OPTION_FIELDS = frozenset({"foreground_color", "background_color", "font_family"})


class OptionsResolver:
    """Merge user-supplied render options with symbology defaults."""

    def coerce_options(
        self,
        options: RenderOptions | None,
    ) -> RenderOptions | None:
        """Normalize supported option input into a RenderOptions instance."""
        if options is None:
            return None

        if isinstance(options, RenderOptions):
            normalized_options = {
                field_name: self._normalize_option_value(
                    field_name,
                    getattr(options, field_name),
                )
                for field_name in _RENDER_OPTION_FIELDS
            }
            return self._build_render_options(normalized_options)

        msg = "render options must be RenderOptions or None"
        raise InvalidInputError(msg)

    def merge_options(
        self,
        earlier: RenderOptions | None,
        later: RenderOptions | None,
    ) -> RenderOptions | None:
        """Merge two unresolved option layers with later values taking priority."""
        earlier_options = self.coerce_options(earlier)
        later_options = self.coerce_options(later)

        merged_options = {
            field_name: self._merge_value(earlier_options, later_options, field_name)
            for field_name in _RENDER_OPTION_FIELDS
        }
        return self._build_render_options(merged_options)

    def resolve(
        self,
        profile: SymbologyProfile,
        *,
        options: RenderOptions | None = None,
    ) -> ResolvedRenderOptions:
        """Resolve the final render configuration."""
        overrides = self.coerce_options(options)
        defaults = profile.defaults

        scale = self._require_positive_number(
            "scale",
            self._select_value(defaults.scale, overrides, "scale"),
        )
        dpi = self._require_positive_integer(
            "dpi",
            self._select_value(defaults.dpi, overrides, "dpi"),
        )
        module_width = self._require_positive_number(
            "module_width",
            self._select_value(defaults.module_width, overrides, "module_width"),
        )
        module_height = self._require_positive_number(
            "module_height",
            self._select_value(defaults.module_height, overrides, "module_height"),
        )
        quiet_zone = self._require_non_negative_number(
            "quiet_zone",
            self._select_value(defaults.quiet_zone, overrides, "quiet_zone"),
        )
        foreground_color = self._require_non_empty_string(
            "foreground_color",
            self._select_value(defaults.foreground_color, overrides, "foreground_color"),
        )
        background_color = self._require_optional_non_empty_string(
            "background_color",
            self._select_value(defaults.background_color, overrides, "background_color"),
        )
        transparent_background = self._require_boolean(
            "transparent_background",
            self._select_value(
                defaults.transparent_background,
                overrides,
                "transparent_background",
            ),
        )
        show_text = self._require_boolean(
            "show_text",
            self._select_value(defaults.show_text, overrides, "show_text"),
        )
        font_family = self._require_non_empty_string(
            "font_family",
            self._select_value(defaults.font_family, overrides, "font_family"),
        )
        font_size = self._require_positive_number(
            "font_size",
            self._select_value(defaults.font_size, overrides, "font_size"),
        )

        if transparent_background:
            background_color = None

        return ResolvedRenderOptions(
            scale=scale,
            dpi=dpi,
            module_width=module_width,
            module_height=module_height,
            quiet_zone=quiet_zone,
            foreground_color=foreground_color,
            background_color=background_color,
            transparent_background=transparent_background,
            show_text=show_text,
            font_family=font_family,
            font_size=font_size,
        )

    def _build_render_options(
        self,
        values: dict[str, object | None],
    ) -> RenderOptions | None:
        """Return a RenderOptions instance when any override is provided."""
        if not any(value is not None for value in values.values()):
            return None
        return RenderOptions(**values)

    def _select_value(
        self,
        default: object,
        overrides: RenderOptions | None,
        field_name: str,
    ) -> object:
        """Return the override when present, otherwise the profile default."""
        value = self._get_option_value(overrides, field_name)
        if value is not None:
            return value
        return default

    def _merge_value(
        self,
        earlier: RenderOptions | None,
        later: RenderOptions | None,
        field_name: str,
    ) -> object | None:
        """Return the later override when present, otherwise the earlier one."""
        later_value = self._get_option_value(later, field_name)
        if later_value is not None:
            return later_value
        return self._get_option_value(earlier, field_name)

    def _get_option_value(
        self,
        options: RenderOptions | None,
        field_name: str,
    ) -> object | None:
        """Return the field value for an unresolved option layer."""
        if options is None:
            return None
        return getattr(options, field_name)

    def _normalize_option_value(
        self,
        field_name: str,
        value: object,
    ) -> object | None:
        """Trim supported string values while preserving later validation."""
        if value is None:
            return None
        if field_name not in _STRING_RENDER_OPTION_FIELDS or not isinstance(value, str):
            return value

        normalized_value = value.strip()
        if not normalized_value:
            msg = f"{field_name} must be a non-empty string"
            raise InvalidInputError(msg)
        return normalized_value

    def _require_boolean(self, field_name: str, value: object) -> bool:
        """Validate a strict boolean option."""
        if type(value) is not bool:
            msg = f"{field_name} must be a boolean"
            raise InvalidInputError(msg)
        return value

    def _require_positive_number(self, field_name: str, value: object) -> float:
        """Validate a strictly positive numeric option."""
        numeric_value = self._require_real_number(field_name, value)
        if numeric_value <= 0:
            msg = f"{field_name} must be greater than zero"
            raise InvalidInputError(msg)
        return numeric_value

    def _require_non_negative_number(self, field_name: str, value: object) -> float:
        """Validate a non-negative numeric option."""
        numeric_value = self._require_real_number(field_name, value)
        if numeric_value < 0:
            msg = f"{field_name} must be greater than or equal to zero"
            raise InvalidInputError(msg)
        return numeric_value

    def _require_real_number(self, field_name: str, value: object) -> float:
        """Validate a real numeric value while rejecting booleans."""
        if not isinstance(value, Real) or isinstance(value, bool):
            msg = f"{field_name} must be a real number"
            raise InvalidInputError(msg)

        numeric_value = float(value)
        if not isfinite(numeric_value):
            msg = f"{field_name} must be a finite real number"
            raise InvalidInputError(msg)
        return numeric_value

    def _require_positive_integer(
        self,
        field_name: str,
        value: object,
    ) -> int | None:
        """Validate an optional positive integer option."""
        if value is None:
            return None
        if not isinstance(value, Integral) or isinstance(value, bool):
            msg = f"{field_name} must be a positive integer"
            raise InvalidInputError(msg)

        integer_value = int(value)
        if integer_value <= 0:
            msg = f"{field_name} must be a positive integer"
            raise InvalidInputError(msg)
        return integer_value

    def _require_non_empty_string(self, field_name: str, value: object) -> str:
        """Validate a non-empty string after trimming whitespace."""
        if not isinstance(value, str):
            msg = f"{field_name} must be a non-empty string"
            raise InvalidInputError(msg)

        normalized_value = value.strip()
        if not normalized_value:
            msg = f"{field_name} must be a non-empty string"
            raise InvalidInputError(msg)
        return normalized_value

    def _require_optional_non_empty_string(
        self,
        field_name: str,
        value: object,
    ) -> str | None:
        """Validate an optional string option after trimming whitespace."""
        if value is None:
            return None
        return self._require_non_empty_string(field_name, value)
