"""Normalization helpers for public login identifiers.

The admin UI accepts a phone number, email address, or an explicitly assigned
staff login in the same field.  Keeping the normalization in one place avoids
different registration and authentication rules.
"""

import re

_PHONE_CHARS = re.compile(r"^[+\d\s().-]+$")
_NON_DIGITS = re.compile(r"\D+")


def normalize_email(value: str) -> str:
    return value.strip().casefold()


def normalize_login(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().casefold()
    return normalized or None


def normalize_phone(value: str | None) -> str | None:
    """Return a stable E.164-like phone or ``None`` for non-phone input.

    Russian local forms are normalized to ``+7``.  International numbers are
    accepted only when the original input starts with ``+`` so an arbitrary
    numeric staff login is not accidentally classified as a phone number.
    """

    if value is None:
        return None
    raw = value.strip()
    if not raw or _PHONE_CHARS.fullmatch(raw) is None:
        return None
    digits = _NON_DIGITS.sub("", raw)
    if len(digits) == 10:
        return f"+7{digits}"
    if len(digits) == 11 and digits[0] in {"7", "8"}:
        return f"+7{digits[1:]}"
    if raw.startswith("+") and 8 <= len(digits) <= 15:
        return f"+{digits}"
    return None
