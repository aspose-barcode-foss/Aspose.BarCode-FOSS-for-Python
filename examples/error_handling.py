"""Handle the typed exceptions raised by the public API."""

from __future__ import annotations

from aspose_barcode_foss import InvalidInputError, SymbologyNotFoundError, code128, ean13, generate


def main() -> None:
    """Trigger and report the most common public error paths."""
    try:
        code128("")  # empty input
    except InvalidInputError as error:
        print(f"InvalidInputError: {error}")

    try:
        ean13("123")  # wrong number of digits
    except InvalidInputError as error:
        print(f"InvalidInputError: {error}")

    try:
        generate("datamatrix", "data")  # unknown symbology
    except SymbologyNotFoundError as error:
        print(f"SymbologyNotFoundError: {error}")


if __name__ == "__main__":
    main()
