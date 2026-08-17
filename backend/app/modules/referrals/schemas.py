"""Внешние контракты реферального API без внутренних идентификаторов."""

from app.shared.base_schema import StrictModel


class ReferralRead(StrictModel):
    code: str
    url: str
    qr_svg: str
    booking_url: str
    booking_qr_svg: str
