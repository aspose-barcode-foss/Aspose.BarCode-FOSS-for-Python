"""Code 128 encoder."""

from __future__ import annotations

from aspose_barcode_foss._internal.encoders.base import SymbologyEncoder
from aspose_barcode_foss._internal.exceptions import InvalidInputError
from aspose_barcode_foss._internal.models.options import (
    Code128EncodeMode,
    Code128Options,
    EncodeOptions,
)
from aspose_barcode_foss._internal.models.payloads import NormalizedPayload
from aspose_barcode_foss._internal.models.symbols import EncodedSymbol, ModuleMatrix, SymbolMetadata
from aspose_barcode_foss._internal.standards.code128 import (
    CODE_A,
    CODE_B,
    CODE_C,
    FNC_1,
    FNC_2,
    FNC_3,
    FNC_4_A,
    FNC_4_B,
    FNC1_SENTINEL,
    FNC2_SENTINEL,
    FNC3_SENTINEL,
    FNC4_SENTINEL,
    SHIFT,
    START_A,
    START_B,
    START_C,
    STOP,
    get_code128_code_set_a_value,
    get_code128_code_set_b_value,
    get_code128_code_set_c_value,
    get_code128_pattern,
)

_CONTROL_CHAR_NAMES: dict[int, str] = {
    0: "NUL",
    1: "SOH",
    2: "STX",
    3: "ETX",
    4: "EOT",
    5: "ENQ",
    6: "ACK",
    7: "BEL",
    8: "BS",
    9: "HT",
    10: "LF",
    11: "VT",
    12: "FF",
    13: "CR",
    14: "SO",
    15: "SI",
    16: "DLE",
    17: "DC1",
    18: "DC2",
    19: "DC3",
    20: "DC4",
    21: "NAK",
    22: "SYN",
    23: "ETB",
    24: "CAN",
    25: "EM",
    26: "SUB",
    27: "ESC",
    28: "FS",
    29: "GS",
    30: "RS",
    31: "US",
}

_FNC_SENTINELS = frozenset({FNC1_SENTINEL, FNC2_SENTINEL, FNC3_SENTINEL, FNC4_SENTINEL})


def _is_set_b_only(char: str) -> bool:
    """Return True if char is in Code Set B but not Code Set A (ord 96–126)."""
    return 96 <= ord(char) <= 126


class Code128Encoder(SymbologyEncoder):
    """Encode data into a Code 128 symbol."""

    def encode(
        self,
        payload: NormalizedPayload,
        *,
        options: Code128Options | EncodeOptions | None = None,
    ) -> EncodedSymbol:
        """Encode a Code 128 payload."""
        del options

        text, mode = self._validate_payload(payload)
        plan: list[int] = self._plan_codewords(text, mode)
        checksum: int = self._calculate_checksum(plan)
        codewords: tuple[int, ...] = (*plan, checksum, STOP)
        module_row = self._build_module_row(codewords)
        display_text = self._build_display_text(text)

        return EncodedSymbol(
            matrix=ModuleMatrix(
                width=len(module_row),
                height=1,
                modules=(module_row,),
            ),
            metadata=SymbolMetadata(
                symbology="code128",
                normalized_data=text,
                display_text=display_text,
                input_kind="text",
                gs1_enabled=False,
                eci_assignment_number=None,
            ),
        )

    def _validate_payload(
        self,
        payload: NormalizedPayload,
    ) -> tuple[str, Code128EncodeMode]:
        """Validate the normalized payload contract before encoding."""
        if payload.symbology != "code128":
            msg = "Code 128 encoder requires symbology='code128'"
            raise InvalidInputError(msg)
        if payload.input_kind != "text":
            msg = "Code 128 encoder requires input_kind='text'"
            raise InvalidInputError(msg)
        if not isinstance(payload.data, str):
            msg = "Code 128 encoder requires payload.data to be a text string"
            raise InvalidInputError(msg)
        if not payload.data:
            msg = "Code 128 text must not be empty"
            raise InvalidInputError(msg)

        mode = self._require_code128_encode_mode(payload)
        assert isinstance(payload.data, str)
        text: str = payload.data
        return text, mode

    def _require_code128_encode_mode(
        self,
        payload: NormalizedPayload,
    ) -> Code128EncodeMode:
        """Require the typed Code 128 encode-mode handoff from the parser."""
        mode = payload.code128_encode_mode
        if mode is None:
            msg = "Code 128 encoder requires payload.code128_encode_mode"
            raise InvalidInputError(msg)
        if not isinstance(mode, Code128EncodeMode):
            msg = "Code 128 payload.code128_encode_mode must be a Code128EncodeMode"
            raise InvalidInputError(msg)
        return mode

    def _calculate_checksum(self, plan: list[int]) -> int:
        """Compute the modulo-103 checksum for a codeword plan.

        plan must be [START, *data_and_switching_codewords], without the
        checksum codeword or STOP. START is treated as the weight-1 term
        per Appendix A of ISO/IEC 15417.
        """
        total = plan[0]  # START value x implicit weight 1
        for position, codeword in enumerate(plan[1:], start=1):
            total += position * codeword
        return total % 103

    def _build_display_text(self, text: str) -> str:
        """Produce a printable representation of text for display.

        Control characters (ASCII 0-31) are rendered as <MNEMONIC>.
        FNC sentinel characters are rendered as <FNC1>-<FNC4>.
        All other characters are passed through unchanged.
        """
        parts: list[str] = []
        for char in text:
            o = ord(char)
            if 0 <= o <= 31:
                parts.append(f"<{_CONTROL_CHAR_NAMES[o]}>")
            elif char == FNC1_SENTINEL:
                parts.append("<FNC1>")
            elif char == FNC2_SENTINEL:
                parts.append("<FNC2>")
            elif char == FNC3_SENTINEL:
                parts.append("<FNC3>")
            elif char == FNC4_SENTINEL:
                parts.append("<FNC4>")
            else:
                parts.append(char)
        return "".join(parts)

    def _plan_codewords(self, text: str, mode: Code128EncodeMode) -> list[int]:
        """Dispatch to the mode-specific codeword plan builder.

        Returns a list [START, *data_and_switching_codewords]. The
        checksum and STOP are not included.
        """
        match mode:
            case Code128EncodeMode.CODE_A:
                return self._plan_code_a(text)
            case Code128EncodeMode.CODE_B:
                return self._plan_code_b(text)
            case Code128EncodeMode.CODE_C:
                return self._plan_code_c(text)
            case Code128EncodeMode.CODE_AB:
                return self._plan_code_ab(text)
            case Code128EncodeMode.CODE_AC:
                return self._plan_code_ac(text)
            case Code128EncodeMode.CODE_BC:
                return self._plan_code_bc(text)
            case Code128EncodeMode.AUTO:
                return self._plan_auto(text)
            case _:
                msg = f"unsupported Code 128 encode_mode: {mode!r}"
                raise InvalidInputError(msg)

    def _plan_code_b(self, text: str) -> list[int]:
        """Build a Code Set B codeword plan: [START_B, *codewords]."""
        plan: list[int] = [START_B]
        for char in text:
            if char in _FNC_SENTINELS:
                plan.append(self._fnc_codeword_b(char))
            else:
                try:
                    plan.append(get_code128_code_set_b_value(char))
                except ValueError as exc:
                    msg = f"unsupported Code 128 character in payload: {char!r}"
                    raise InvalidInputError(msg) from exc
        return plan

    def _plan_code_a(self, text: str) -> list[int]:
        """Build a Code Set A codeword plan: [START_A, *codewords]."""
        plan: list[int] = [START_A]
        for char in text:
            if char in _FNC_SENTINELS:
                plan.append(self._fnc_codeword_a(char))
            else:
                try:
                    plan.append(get_code128_code_set_a_value(char))
                except ValueError as exc:
                    msg = f"unsupported Code 128 character in payload: {char!r}"
                    raise InvalidInputError(msg) from exc
        return plan

    def _plan_code_c(self, text: str) -> list[int]:
        """Build a Code Set C codeword plan: [START_C, *codewords].

        Relies on the parser to guarantee even-length all-digit input, but
        also converts ValueError from the helper into InvalidInputError for
        payloads constructed without the parser.
        """
        plan: list[int] = [START_C]
        for i in range(0, len(text), 2):
            pair = text[i : i + 2]
            try:
                plan.append(get_code128_code_set_c_value(pair))
            except ValueError as exc:
                msg = f"unsupported Code 128 character in payload: {pair!r}"
                raise InvalidInputError(msg) from exc
        return plan

    def _plan_code_ab(self, text: str) -> list[int]:
        """Build a Code Set A/B inter-set switching codeword plan.

        Implements Appendix E rules 1, 4, and 5. Uses SHIFT for single-character
        exceptions, CODE_A/CODE_B for longer runs.
        """
        # Start selection: control char -> START_A, otherwise START_B
        if text and ord(text[0]) <= 31:
            active_set = "A"
            plan: list[int] = [START_A]
        else:
            active_set = "B"
            plan = [START_B]

        i = 0
        while i < len(text):
            char = text[i]

            if char in _FNC_SENTINELS:
                if active_set == "A":
                    plan.append(self._fnc_codeword_a(char))
                else:
                    plan.append(self._fnc_codeword_b(char))
                i += 1
                continue

            if active_set == "B" and ord(char) <= 31:
                # Control character; need Code Set A
                next1 = text[i + 1] if i + 1 < len(text) else None
                next2 = text[i + 2] if i + 2 < len(text) else None
                if next1 is not None and _is_set_b_only(next1) and next2 is not None and ord(next2) <= 31:
                    # Rule 4a: SHIFT is cheaper (control + set-B-only + control)
                    plan.extend([SHIFT, get_code128_code_set_a_value(char)])
                else:
                    # Rule 4b: switch to A
                    plan.extend([CODE_A, get_code128_code_set_a_value(char)])
                    active_set = "A"
                i += 1
            elif active_set == "A" and _is_set_b_only(char):
                # Lowercase/braces; need Code Set B
                next1 = text[i + 1] if i + 1 < len(text) else None
                next2 = text[i + 2] if i + 2 < len(text) else None
                if next1 is not None and ord(next1) <= 31 and next2 is not None and _is_set_b_only(next2):
                    # Rule 5a: SHIFT is cheaper (set-B-only + control + set-B-only)
                    plan.extend([SHIFT, get_code128_code_set_b_value(char)])
                else:
                    # Rule 5b: switch to B
                    plan.extend([CODE_B, get_code128_code_set_b_value(char)])
                    active_set = "B"
                i += 1
            else:
                if active_set == "A":
                    plan.append(get_code128_code_set_a_value(char))
                else:
                    plan.append(get_code128_code_set_b_value(char))
                i += 1

        return plan

    def _plan_code_ac(self, text: str) -> list[int]:
        """Build a Code Set A/C inter-set switching codeword plan.

        Start selection: START_C if >= 4 leading digit characters; START_A otherwise.
        No SHIFT (Code Set B is excluded).
        """
        leading_digits = 0
        for ch in text:
            if ch.isdigit():
                leading_digits += 1
            else:
                break

        if leading_digits >= 4:
            active_set = "C"
            plan: list[int] = [START_C]
        else:
            active_set = "A"
            plan = [START_A]

        i = 0
        while i < len(text):
            char = text[i]

            if active_set == "A":
                # Count consecutive digits from position i
                j = i
                while j < len(text) and text[j].isdigit():
                    j += 1
                digit_run = j - i
                if digit_run >= 4:
                    plan.append(CODE_C)
                    active_set = "C"
                    # Do NOT advance i; fall through to C handler on next iteration
                elif char in _FNC_SENTINELS:
                    plan.append(self._fnc_codeword_a(char))
                    i += 1
                else:
                    try:
                        plan.append(get_code128_code_set_a_value(char))
                    except ValueError as exc:
                        msg = f"unsupported Code 128 character in payload: {char!r}"
                        raise InvalidInputError(msg) from exc
                    i += 1
            else:  # active_set == "C"
                if i + 1 < len(text) and text[i].isdigit() and text[i + 1].isdigit():
                    plan.append(get_code128_code_set_c_value(text[i : i + 2]))
                    i += 2
                elif char == FNC1_SENTINEL:
                    plan.append(FNC_1)
                    i += 1
                else:
                    plan.append(CODE_A)
                    active_set = "A"
                    # Do NOT advance i; handle char on next iteration in A mode

        return plan

    def _plan_code_bc(self, text: str) -> list[int]:
        """Build a Code Set B/C inter-set switching codeword plan.

        Start selection: START_C if >= 4 leading digit characters; START_B otherwise.
        No SHIFT (Code Set A is excluded).
        """
        leading_digits = 0
        for ch in text:
            if ch.isdigit():
                leading_digits += 1
            else:
                break

        if leading_digits >= 4:
            active_set = "C"
            plan: list[int] = [START_C]
        else:
            active_set = "B"
            plan = [START_B]

        i = 0
        while i < len(text):
            char = text[i]

            if active_set == "B":
                # Count consecutive digits from position i
                j = i
                while j < len(text) and text[j].isdigit():
                    j += 1
                digit_run = j - i
                if digit_run >= 4:
                    plan.append(CODE_C)
                    active_set = "C"
                    # Do NOT advance i; fall through to C handler on next iteration
                elif char in _FNC_SENTINELS:
                    plan.append(self._fnc_codeword_b(char))
                    i += 1
                else:
                    try:
                        plan.append(get_code128_code_set_b_value(char))
                    except ValueError as exc:
                        msg = f"unsupported Code 128 character in payload: {char!r}"
                        raise InvalidInputError(msg) from exc
                    i += 1
            else:  # active_set == "C"
                if i + 1 < len(text) and text[i].isdigit() and text[i + 1].isdigit():
                    plan.append(get_code128_code_set_c_value(text[i : i + 2]))
                    i += 2
                else:
                    plan.append(CODE_B)
                    active_set = "B"
                    # Do NOT advance i; handle char on next iteration in B mode

        return plan

    def _plan_auto(self, text: str) -> list[int]:
        """Build a fully optimized codeword plan using the Appendix E algorithm.

        Combines A<->B switching (with SHIFT) and Code Set C transitions for
        maximum compression.
        """
        # Count leading digits
        leading_digits = 0
        for ch in text:
            if ch.isdigit():
                leading_digits += 1
            else:
                break

        # Start selection per Appendix E rule 1
        if len(text) == 2 and text.isdigit():
            active_set = "C"
            plan: list[int] = [START_C]
        elif leading_digits >= 4:
            active_set = "C"
            plan = [START_C]
        elif text and ord(text[0]) <= 31:
            active_set = "A"
            plan = [START_A]
        else:
            active_set = "B"
            plan = [START_B]

        i = 0
        while i < len(text):
            char = text[i]

            if active_set == "C":
                if i + 1 < len(text) and text[i].isdigit() and text[i + 1].isdigit():
                    plan.append(get_code128_code_set_c_value(text[i : i + 2]))
                    i += 2
                elif char == FNC1_SENTINEL:
                    plan.append(FNC_1)
                    i += 1
                else:
                    # Switch to A or B depending on next character
                    if ord(char) <= 31:
                        plan.append(CODE_A)
                        active_set = "A"
                    else:
                        plan.append(CODE_B)
                        active_set = "B"
                    # Do NOT advance i; handle char on next iteration
            elif active_set in ("A", "B"):
                # Check for a digit run that warrants switching to Code Set C
                if char.isdigit():
                    j = i
                    while j < len(text) and text[j].isdigit():
                        j += 1
                    digit_run = j - i
                    if digit_run >= 4:
                        # Switch to C
                        if digit_run % 2 == 1:
                            # Odd run: encode first digit in current set, then switch
                            if active_set == "A":
                                plan.append(get_code128_code_set_a_value(char))
                            else:
                                plan.append(get_code128_code_set_b_value(char))
                            i += 1
                        plan.append(CODE_C)
                        active_set = "C"
                        # Do NOT advance i; fall through to C handler next iteration
                        continue

                # No digit-run transition; handle A<->B switching (Appendix E rules 4 & 5)
                if char in _FNC_SENTINELS:
                    if active_set == "A":
                        plan.append(self._fnc_codeword_a(char))
                    else:
                        plan.append(self._fnc_codeword_b(char))
                    i += 1
                elif active_set == "B" and ord(char) <= 31:
                    # Control character; need Code Set A
                    next1 = text[i + 1] if i + 1 < len(text) else None
                    next2 = text[i + 2] if i + 2 < len(text) else None
                    if next1 is not None and _is_set_b_only(next1) and next2 is not None and ord(next2) <= 31:
                        plan.extend([SHIFT, get_code128_code_set_a_value(char)])
                    else:
                        plan.extend([CODE_A, get_code128_code_set_a_value(char)])
                        active_set = "A"
                    i += 1
                elif active_set == "A" and _is_set_b_only(char):
                    # Lowercase/braces; need Code Set B
                    next1 = text[i + 1] if i + 1 < len(text) else None
                    next2 = text[i + 2] if i + 2 < len(text) else None
                    if next1 is not None and ord(next1) <= 31 and next2 is not None and _is_set_b_only(next2):
                        plan.extend([SHIFT, get_code128_code_set_b_value(char)])
                    else:
                        plan.extend([CODE_B, get_code128_code_set_b_value(char)])
                        active_set = "B"
                    i += 1
                else:
                    try:
                        if active_set == "A":
                            plan.append(get_code128_code_set_a_value(char))
                        else:
                            plan.append(get_code128_code_set_b_value(char))
                    except ValueError as exc:
                        msg = f"unsupported Code 128 character in payload: {char!r}"
                        raise InvalidInputError(msg) from exc
                    i += 1

        return plan

    @staticmethod
    def _fnc_codeword_b(sentinel: str) -> int:
        """Return the Code Set B codeword for an FNC sentinel character."""
        if sentinel == FNC1_SENTINEL:
            return FNC_1  # 102
        if sentinel == FNC2_SENTINEL:
            return FNC_2  # 97
        if sentinel == FNC3_SENTINEL:
            return FNC_3  # 96
        if sentinel == FNC4_SENTINEL:
            return FNC_4_B  # 100
        raise ValueError(f"not an FNC sentinel: {sentinel!r}")

    @staticmethod
    def _fnc_codeword_a(sentinel: str) -> int:
        """Return the Code Set A codeword for an FNC sentinel character."""
        if sentinel == FNC1_SENTINEL:
            return FNC_1  # 102
        if sentinel == FNC2_SENTINEL:
            return FNC_2  # 97
        if sentinel == FNC3_SENTINEL:
            return FNC_3  # 96
        if sentinel == FNC4_SENTINEL:
            return FNC_4_A  # 101
        raise ValueError(f"not an FNC sentinel: {sentinel!r}")

    def _build_module_row(self, codewords: tuple[int, ...]) -> tuple[int, ...]:
        """Flatten Code 128 patterns into one renderer-ready module row."""
        modules: list[int] = []
        for codeword in codewords:
            modules.extend(1 if module == "1" else 0 for module in get_code128_pattern(codeword))
        return tuple(modules)
