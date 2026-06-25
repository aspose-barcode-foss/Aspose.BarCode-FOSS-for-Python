"""Package-internal bootstrap for the default service registry."""

from __future__ import annotations

from aspose_barcode_foss._internal.encoders.code128 import Code128Encoder
from aspose_barcode_foss._internal.encoders.code39 import Code39Encoder
from aspose_barcode_foss._internal.encoders.ean13 import Ean13Encoder
from aspose_barcode_foss._internal.encoders.ean8 import Ean8Encoder
from aspose_barcode_foss._internal.encoders.qr import QrEncoder
from aspose_barcode_foss._internal.encoders.upca import UpcaEncoder
from aspose_barcode_foss._internal.encoders.upce import UpceEncoder
from aspose_barcode_foss._internal.models.capabilities import SymbologyCapabilities
from aspose_barcode_foss._internal.models.options import ResolvedRenderOptions
from aspose_barcode_foss._internal.parsers.code128 import Code128InputParser
from aspose_barcode_foss._internal.parsers.code39 import Code39InputParser
from aspose_barcode_foss._internal.parsers.ean13 import Ean13InputParser
from aspose_barcode_foss._internal.parsers.ean8 import Ean8InputParser
from aspose_barcode_foss._internal.parsers.qr import QrInputParser
from aspose_barcode_foss._internal.parsers.upca import UpcaInputParser
from aspose_barcode_foss._internal.parsers.upce import UpceInputParser
from aspose_barcode_foss._internal.profiles.code128 import Code128Profile
from aspose_barcode_foss._internal.profiles.code39 import Code39Profile
from aspose_barcode_foss._internal.profiles.ean13 import Ean13Profile
from aspose_barcode_foss._internal.profiles.ean8 import Ean8Profile
from aspose_barcode_foss._internal.profiles.qr import QrProfile
from aspose_barcode_foss._internal.profiles.upca import UpcaProfile
from aspose_barcode_foss._internal.profiles.upce import UpceProfile
from aspose_barcode_foss._internal.registry import SymbologyDefinition, SymbologyRegistry
from aspose_barcode_foss._internal.resolver import OptionsResolver
from aspose_barcode_foss._internal.service import BarcodeService
from aspose_barcode_foss._internal.text.code128 import Code128TextLayoutPolicy
from aspose_barcode_foss._internal.text.code39 import Code39TextLayoutPolicy
from aspose_barcode_foss._internal.text.ean13 import Ean13TextLayoutPolicy
from aspose_barcode_foss._internal.text.ean8 import Ean8TextLayoutPolicy
from aspose_barcode_foss._internal.text.qr import QrTextLayoutPolicy
from aspose_barcode_foss._internal.text.upca import UpcaTextLayoutPolicy
from aspose_barcode_foss._internal.text.upce import UpceTextLayoutPolicy


def _build_render_defaults(
    *,
    quiet_zone: float,
    module_height: float = 10.0,
    show_text: bool = True,
) -> ResolvedRenderOptions:
    """Return bootstrap render defaults for a symbology profile."""
    return ResolvedRenderOptions(
        scale=1.0,
        dpi=300,
        module_width=2.0,
        module_height=module_height,
        quiet_zone=quiet_zone,
        foreground_color="#111111",
        background_color="#fefefe",
        transparent_background=False,
        show_text=show_text,
        font_family="Fira Sans",
        font_size=8.0,
    )


def _build_capabilities() -> SymbologyCapabilities:
    """Return the conservative bootstrap capability metadata."""
    return SymbologyCapabilities(
        gs1_support="unsupported",
        eci_support="unsupported",
        structured_append_support="unsupported",
        binary_input_support="unsupported",
        rendering_outputs=("svg",),
    )


def _build_code128_spec_references() -> tuple[str, ...]:
    """Return factual Code 128 support notes."""
    return (
        "Code 128 supports non-empty printable Code Set B text on the shared SVG pipeline.",
        "Successful symbols always emit Start B, data codewords, a modulo-103 checksum, and the stop pattern.",
    )


def _build_code128_known_limitations() -> tuple[str, ...]:
    """Return the documented Code 128 limitations."""
    return (
        "GS1, ECI, bytes / binary input, FNC handling, Code Set A/C, Shift, and code-set switching are unsupported.",
        "Only the SVG backend is implemented for Code 128 .",
        "Explicit quiet_zone overrides can shrink below the Code 128 10X minimum; enforcement is not implemented yet.",
    )


def _build_code39_spec_references() -> tuple[str, ...]:
    """Return factual Code 39 profile references."""
    return (
        "ISO/IEC 16388:2017 §4.1–§4.4: Code 39 character set, 9-element (5 bars + 4 spaces, exactly three wide) "
        "structure, dimensions, and quiet zone.",
        "ISO/IEC 16388:2017 Annex A: optional modulo-43 check character and Full-ASCII (Extended) two-character "
        "shift encoding of all 128 ASCII values.",
        "Symbols are framed by a start/stop '*'; the optional check character and the start/stop '*' are excluded "
        "from the human-readable text.",
    )


def _build_code39_known_limitations() -> tuple[str, ...]:
    """Return the documented Code 39 limitations."""
    return (
        "GS1, ECI, bytes / binary input, and structured append are unsupported.",
        "Only the SVG backend is implemented for Code 39.",
        "A fixed 3:1 wide:narrow ratio is used; the spec's configurable 2.0:1–3.0:1 range is not implemented.",
        "The nominal 1X inter-character gap is used; the spec's gap-widening allowances are not implemented.",
        "Explicit quiet_zone overrides can shrink below the Code 39 10X minimum; enforcement is not implemented.",
        "Non-ASCII (code point > 127) input is rejected in both modes.",
    )


def _build_qr_capabilities() -> SymbologyCapabilities:
    """Return the QR Code capability metadata."""
    return SymbologyCapabilities(
        gs1_support="unsupported",
        eci_support="supported",
        structured_append_support="unsupported",
        binary_input_support="unsupported",
        rendering_outputs=("svg", "png"),
    )


def _build_qr_spec_references() -> tuple[str, ...]:
    """Return factual ISO/IEC 18004:2015 QR Code references."""
    return (
        "ISO/IEC 18004:2015: QR Code (Model 2) numeric, alphanumeric, 8-bit byte (Latin-1), and Kanji "
        "modes with automatic optimal mode segmentation, versions 1-40, error correction levels L/M/Q/H.",
        "ISO/IEC 18004:2015 §7.4.1: Table 2 mode indicators and Table 3 character-count-indicator bit "
        "widths per version group (1-9 / 10-26 / 27-40).",
        "ISO/IEC 18004:2015 §7.4.3 numeric mode (groups of 3/2/1 digits -> 10/7/4 bits), §7.4.4 Table 5 "
        "alphanumeric mode (45-character set, 11 bits per pair / 6 bits for a trailing single).",
        "ISO/IEC 18004:2015 §7.4.6 Kanji mode (Shift-JIS double-byte 13-bit packing) and §7.4.2 / "
        "§7.4.2.2 ECI (mode indicator 0111 with a 1/2/3-codeword assignment number; default byte "
        "interpretation is Latin-1).",
        "Reed-Solomon error correction over GF(256) (primitive polynomial 0x11D); all eight data "
        "masks are evaluated with ISO penalty scoring and the lowest-penalty mask is selected.",
        "Symbols carry format and version information, finder/separator/timing/alignment patterns, "
        "the dark module, and a 4-module quiet zone.",
    )


def _build_qr_known_limitations() -> tuple[str, ...]:
    """Return the documented QR Code deferrals and exclusions."""
    return (
        "Numeric, alphanumeric, and Kanji modes, ECI, and automatic optimal mode segmentation "
        "(mixed-mode) are implemented.",
        "ECI combined with a forced non-byte mode (numeric / alphanumeric / Kanji) is rejected; the "
        "default byte interpretation is Latin-1 (no ECI->codec table).",
        "Micro QR and Structured Append are excluded.",
        "bytes / binary input is unsupported (a clean future extension); GS1 is unsupported.",
        "Only the SVG and PNG backends are implemented for QR Code.",
        "Overriding only one of module_width / module_height can distort the square module grid.",
    )


def _build_ean_upc_spec_references(symbology: str) -> tuple[str, ...]:
    """Return ISO 15420 profile references for one EAN/UPC symbology."""
    if symbology == "ean13":
        return (
            "ISO/IEC 15420:2009: EAN-13 character encoding, symbol structure, check digit, and guard bar dimensions.",
            "EAN-13 encodes 13 digits; the first digit is implied by the left-half A/B parity mix.",
            "Guard and centre guard bars extend 5X below data bars.",
        )
    if symbology == "upca":
        return (
            "ISO/IEC 15420:2009: UPC-A character encoding, symbol structure, check digit, and guard bar dimensions.",
            "UPC-A encodes 12 GTIN digits using six left set-A digits and six right set-C digits.",
            "Guard bars and first and last data character bars extend 5X below data bars.",
        )
    if symbology == "upce":
        return (
            "ISO/IEC 15420:2009: UPC-E zero-suppression, parity, special guard pattern, and guard bar dimensions.",
            "UPC-E is encoded from a number-system-0 GTIN-12 value after ISO zero-suppression.",
            "Guard and special guard bars extend 5X below data bars.",
        )
    if symbology == "ean8":
        return (
            "ISO/IEC 15420:2009: EAN-8 character encoding, symbol structure, check digit, and guard bar dimensions.",
            "EAN-8 encodes 7 data digits plus 1 check digit, four left set-A digits and four right set-C digits.",
            "Guard and centre guard bars extend 5X below data bars.",
        )

    msg = f"unknown EAN/UPC symbology {symbology!r}"
    raise ValueError(msg)


def _build_ean_upc_known_limitations() -> tuple[str, ...]:
    """Return EAN/UPC limitations that are not implemented."""
    return (
        "Bar/space compensation (ISO/IEC 15420:2009 4.3.6, Table 8) is not implemented.",
        "Symmetric quiet zone is used; ISO/IEC 15420:2009 minimums are asymmetric for EAN-13 and UPC-E.",
        "GS1, ECI, and binary input are not supported.",
        "EAN-2 and EAN-5 add-on symbols are not supported.",
    )


def build_default_registry() -> SymbologyRegistry:
    """Build a fresh registry populated with the default definitions."""
    code128_defaults = _build_render_defaults(quiet_zone=20.0)
    code39_defaults = _build_render_defaults(quiet_zone=20.0)
    ean13_defaults = _build_render_defaults(quiet_zone=22.0, module_height=138.5)
    upca_defaults = _build_render_defaults(quiet_zone=18.0, module_height=138.5)
    upce_defaults = _build_render_defaults(quiet_zone=18.0, module_height=138.5)
    ean8_defaults = _build_render_defaults(quiet_zone=14.0, module_height=138.5)
    capabilities = _build_capabilities()
    ean_upc_known_limitations = _build_ean_upc_known_limitations()
    registry = SymbologyRegistry()

    code128_text_policy = Code128TextLayoutPolicy()
    registry.register(
        SymbologyDefinition(
            name="code128",
            aliases=("code-128",),
            parser=Code128InputParser(),
            encoder=Code128Encoder(),
            profile=Code128Profile(
                name="code128",
                status="beta",
                defaults=code128_defaults,
                capabilities=capabilities,
                text_policy=code128_text_policy,
                spec_references=_build_code128_spec_references(),
                known_limitations=_build_code128_known_limitations(),
            ),
        )
    )

    ean13_text_policy = Ean13TextLayoutPolicy()
    registry.register(
        SymbologyDefinition(
            name="ean13",
            aliases=("ean-13",),
            parser=Ean13InputParser(),
            encoder=Ean13Encoder(),
            profile=Ean13Profile(
                name="ean13",
                status="beta",
                defaults=ean13_defaults,
                capabilities=capabilities,
                text_policy=ean13_text_policy,
                spec_references=_build_ean_upc_spec_references("ean13"),
                known_limitations=ean_upc_known_limitations,
            ),
        )
    )

    upca_text_policy = UpcaTextLayoutPolicy()
    registry.register(
        SymbologyDefinition(
            name="upca",
            aliases=("upc-a",),
            parser=UpcaInputParser(),
            encoder=UpcaEncoder(),
            profile=UpcaProfile(
                name="upca",
                status="beta",
                defaults=upca_defaults,
                capabilities=capabilities,
                text_policy=upca_text_policy,
                spec_references=_build_ean_upc_spec_references("upca"),
                known_limitations=ean_upc_known_limitations,
            ),
        )
    )

    upce_text_policy = UpceTextLayoutPolicy()
    registry.register(
        SymbologyDefinition(
            name="upce",
            aliases=("upc-e",),
            parser=UpceInputParser(),
            encoder=UpceEncoder(),
            profile=UpceProfile(
                name="upce",
                status="beta",
                defaults=upce_defaults,
                capabilities=capabilities,
                text_policy=upce_text_policy,
                spec_references=_build_ean_upc_spec_references("upce"),
                known_limitations=ean_upc_known_limitations,
            ),
        )
    )

    ean8_text_policy = Ean8TextLayoutPolicy()
    registry.register(
        SymbologyDefinition(
            name="ean8",
            aliases=("ean-8",),
            parser=Ean8InputParser(),
            encoder=Ean8Encoder(),
            profile=Ean8Profile(
                name="ean8",
                status="beta",
                defaults=ean8_defaults,
                capabilities=capabilities,
                text_policy=ean8_text_policy,
                spec_references=_build_ean_upc_spec_references("ean8"),
                known_limitations=ean_upc_known_limitations,
            ),
        )
    )

    code39_text_policy = Code39TextLayoutPolicy()
    code39_spec_references = _build_code39_spec_references()
    code39_known_limitations = _build_code39_known_limitations()

    registry.register(
        SymbologyDefinition(
            name="code39",
            aliases=("code-39", "3of9", "code 39"),
            parser=Code39InputParser(default_full_ascii=False, symbology_name="code39"),
            encoder=Code39Encoder(),
            profile=Code39Profile(
                name="code39",
                status="beta",
                defaults=code39_defaults,
                capabilities=capabilities,
                text_policy=code39_text_policy,
                spec_references=code39_spec_references,
                known_limitations=code39_known_limitations,
            ),
        )
    )

    registry.register(
        SymbologyDefinition(
            name="code39ext",
            aliases=("code-39-extended", "code39extended", "code39full", "code-39-full", "extended-code-39"),
            parser=Code39InputParser(default_full_ascii=True, symbology_name="code39ext"),
            encoder=Code39Encoder(),
            profile=Code39Profile(
                name="code39ext",
                status="beta",
                defaults=code39_defaults,
                capabilities=capabilities,
                text_policy=code39_text_policy,
                spec_references=code39_spec_references,
                known_limitations=code39_known_limitations,
            ),
        )
    )

    qr_defaults = _build_render_defaults(quiet_zone=8.0, module_height=2.0, show_text=False)
    qr_text_policy = QrTextLayoutPolicy()
    registry.register(
        SymbologyDefinition(
            name="qr",
            aliases=("qrcode", "qr-code"),
            parser=QrInputParser(),
            encoder=QrEncoder(),
            profile=QrProfile(
                name="qr",
                status="beta",
                defaults=qr_defaults,
                capabilities=_build_qr_capabilities(),
                text_policy=qr_text_policy,
                spec_references=_build_qr_spec_references(),
                known_limitations=_build_qr_known_limitations(),
            ),
        )
    )

    return registry


def build_default_service() -> BarcodeService:
    """Build a fresh default service with a fresh registry."""
    return BarcodeService(
        registry=build_default_registry(),
        options_resolver=OptionsResolver(),
    )
