"""Canonical phone handling for the client OTP contour."""

import re


def normalize_client_phone(value: str) -> str:
    """Return a stable E.164-like value used as the account identity.

    The current client UI is Russian and sends masked ``+7`` numbers.  We also
    accept the common local forms ``8XXXXXXXXXX`` and ``XXXXXXXXXX`` so the
    same person cannot accidentally receive several accounts because of
    spaces, brackets or a leading eight.
    """

    digits = re.sub(r"\D", "", value)
    if len(digits) == 10:
        digits = f"7{digits}"
    elif len(digits) == 11 and digits.startswith("8"):
        digits = f"7{digits[1:]}"
    if not 10 <= len(digits) <= 15:
        raise ValueError("Некорректный номер телефона")
    return f"+{digits}"
