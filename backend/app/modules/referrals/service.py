"""Создание ссылок, печатных QR и разрешение реферальных кодов."""

import secrets
from io import BytesIO

import qrcode
import qrcode.image.svg
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.modules.referrals.models import OrganizationReferral
from app.modules.referrals.repository import ReferralRepository
from app.modules.referrals.schemas import ReferralRead


class ReferralService:
    def __init__(self, repo: ReferralRepository) -> None:
        self.repo = repo

    @staticmethod
    def public_url(code: str) -> str:
        """Стабильная ссылка регистрации с неизменяемой атрибуцией."""
        base = settings.PUBLIC_CLIENT_BASE_URL.rstrip("/")
        return f"{base}/r/{code}"

    @classmethod
    def booking_url(cls, code: str) -> str:
        """Стабильная ссылка гостевой записи в конкретный автосервис."""
        base = settings.PUBLIC_CLIENT_BASE_URL.rstrip("/")
        return f"{base}/book/{code}"

    @staticmethod
    def _qr_svg(url: str) -> str:
        """Возвращает векторный QR с quiet zone, пригодный для печати."""
        image = qrcode.make(
            url,
            image_factory=qrcode.image.svg.SvgPathImage,
            box_size=10,
            border=4,
        )
        output = BytesIO()
        image.save(output)
        return output.getvalue().decode("utf-8")

    @classmethod
    def qr_svg(cls, code: str) -> str:
        return cls._qr_svg(cls.public_url(code))

    @classmethod
    def booking_qr_svg(cls, code: str) -> str:
        return cls._qr_svg(cls.booking_url(code))

    @classmethod
    def present(cls, referral: OrganizationReferral) -> ReferralRead:
        return ReferralRead(
            code=referral.code,
            url=cls.public_url(referral.code),
            qr_svg=cls.qr_svg(referral.code),
            booking_url=cls.booking_url(referral.code),
            booking_qr_svg=cls.booking_qr_svg(referral.code),
        )

    async def get(self, organization_id: int) -> ReferralRead:
        referral = await self.repo.get_by_organization(organization_id)
        if referral is None:
            raise NotFoundError("Реферальная ссылка ещё не создана")
        return self.present(referral)

    async def get_or_create(self, organization_id: int) -> ReferralRead:
        referral = await self.repo.get_by_organization(organization_id)
        if referral is not None:
            return self.present(referral)

        # Savepoint позволяет безопасно пережить одновременное создание для
        # одной организации или практически невероятную коллизию кода.
        for _ in range(3):
            try:
                async with self.repo.session.begin_nested():
                    referral = await self.repo.add(
                        OrganizationReferral(
                            organization_id=organization_id,
                            # Ровно 16 URL-safe символов / 96 бит энтропии.
                            code=secrets.token_urlsafe(12),
                        )
                    )
                return self.present(referral)
            except IntegrityError:
                referral = await self.repo.get_by_organization(organization_id)
                if referral is not None:
                    return self.present(referral)
        raise BusinessRuleError(
            "Не удалось создать реферальную ссылку, повторите запрос"
        )

    async def resolve_organization(self, code: str) -> int:
        referral = await self.repo.get_by_code(code)
        if referral is None:
            raise BusinessRuleError("Недействительный реферальный код")
        return referral.organization_id

    async def resolve_public_booking_organization(self, code: str) -> int:
        referral = await self.repo.get_by_code(code)
        if referral is None:
            raise NotFoundError("Ссылка записи недействительна")
        return referral.organization_id
