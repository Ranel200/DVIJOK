"""Настройки организации и безопасная смена пароля текущего администратора."""

import base64
import datetime as dt
from pathlib import Path

from sqlalchemy import select

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError, UnauthorizedError
from app.core.security import hash_password, verify_password
from app.modules.auth.models import StaffLoginEvent, StaffRefreshSession
from app.modules.organizations.models import Organization
from app.modules.settings.schemas import (
    SecuritySession,
    SecuritySettings,
    ServiceSettings,
    SettingsRead,
    SettingsUpdate,
    SubscriptionFeature,
    SubscriptionSettings,
)
from app.modules.users.models import User
from app.shared.enums import LegalForm, OrganizationStatus, TaxSystem

_LEGAL_FROM_UI = {
    "ИП": LegalForm.IP,
    "ООО": LegalForm.OOO,
    "ОАО": LegalForm.OAO,
    "ЗАО": LegalForm.ZAO,
    "ПАО": LegalForm.PAO,
}
_LEGAL_TO_UI = {value: key for key, value in _LEGAL_FROM_UI.items()}
_TAX_FROM_UI = {"УСН": TaxSystem.USN, "НДС": TaxSystem.NDS}
_TAX_TO_UI = {value: key for key, value in _TAX_FROM_UI.items()}
_FEATURES = [
    SubscriptionFeature(icon="plane", label="Неограниченные заказы"),
    SubscriptionFeature(icon="analytic", label="Аналитика и отчеты"),
    SubscriptionFeature(icon="group", label="До 10 мастеров"),
    SubscriptionFeature(icon="support", label="Поддержка"),
]
MAX_ORGANIZATION_LOGO_BYTES = 1_800_000
_LOGO_TYPES = {
    "image/jpeg": {".jpg", ".jpeg"},
    "image/png": {".png"},
    "image/webp": {".webp"},
    "image/gif": {".gif"},
}


class SettingsService:
    def __init__(
        self,
        session,
        current_user: User,
        current_session_id: int | None = None,
    ) -> None:
        self.session = session
        self.current_user = current_user
        self.current_session_id = current_session_id

    @staticmethod
    def _user_agent(value: str) -> tuple[str, str, str]:
        lowered = value.casefold()
        mobile_markers = ("mobile", "iphone", "android")
        device_type = "phone" if any(item in lowered for item in mobile_markers) else "pc"
        if "edg/" in lowered:
            browser = "Edge"
        elif "firefox/" in lowered:
            browser = "Firefox"
        elif "chrome/" in lowered:
            browser = "Chrome"
        elif "safari/" in lowered:
            browser = "Safari"
        else:
            browser = ""
        device = "Мобильное устройство" if device_type == "phone" else "Компьютер"
        return device_type, device, browser

    async def _sessions(self) -> list[SecuritySession]:
        now = dt.datetime.now(dt.UTC)
        sessions = list(
            (
                await self.session.execute(
                    select(StaffRefreshSession)
                    .where(
                        StaffRefreshSession.user_id == self.current_user.id,
                        StaffRefreshSession.revoked_at.is_(None),
                        StaffRefreshSession.expires_at > now,
                    )
                    .order_by(StaffRefreshSession.created_at.desc())
                )
            )
            .scalars()
            .all()
        )
        result: list[SecuritySession] = []
        for session in sessions:
            device_type, device_name, browser = self._user_agent(session.user_agent)
            result.append(
                SecuritySession(
                    id=str(session.id),
                    current=session.id == self.current_session_id,
                    type=device_type,
                    device_name=device_name,
                    browser=browser,
                    city="",
                    country="",
                    ip=session.ip,
                    last_active_at=session.last_used_at or session.created_at,
                )
            )
        return result

    async def _login_history(self) -> list[dict]:
        events = list(
            (
                await self.session.execute(
                    select(StaffLoginEvent)
                    .where(StaffLoginEvent.user_id == self.current_user.id)
                    .order_by(StaffLoginEvent.created_at.desc())
                    .limit(100)
                )
            )
            .scalars()
            .all()
        )
        result = []
        for event in events:
            _, device_name, browser = self._user_agent(event.user_agent)
            result.append(
                {
                    "id": str(event.id),
                    "success": event.success,
                    "deviceName": device_name,
                    "browser": browser,
                    "city": "",
                    "country": "",
                    "ip": event.ip,
                    "loggedAt": event.created_at.isoformat(),
                }
            )
        return result

    async def _organization(self) -> Organization:
        organization = await self.session.get(Organization, self.current_user.organization_id)
        if organization is None:
            raise NotFoundError("Организация не найдена")
        return organization

    @staticmethod
    def _validate_logo(
        filename: str | None,
        content_type: str | None,
        content: bytes,
    ) -> str:
        safe_name = Path(filename or "").name
        media_type = (content_type or "").split(";", 1)[0].strip().lower()
        suffix = Path(safe_name).suffix.lower()
        if not content:
            raise BusinessRuleError("Файл логотипа пуст")
        if len(content) > MAX_ORGANIZATION_LOGO_BYTES:
            raise BusinessRuleError("Размер логотипа превышает 1,8 МБ")
        if (
            not safe_name
            or media_type not in _LOGO_TYPES
            or suffix not in _LOGO_TYPES[media_type]
        ):
            raise BusinessRuleError("Поддерживаются JPEG, PNG, WebP и GIF")
        signatures = {
            "image/jpeg": content.startswith(b"\xff\xd8\xff"),
            "image/png": content.startswith(b"\x89PNG\r\n\x1a\n"),
            "image/webp": content.startswith(b"RIFF") and content[8:12] == b"WEBP",
            "image/gif": content.startswith((b"GIF87a", b"GIF89a")),
        }
        if not signatures[media_type]:
            raise BusinessRuleError("Содержимое файла не соответствует формату")
        return media_type

    async def upload_logo(
        self,
        *,
        filename: str | None,
        content_type: str | None,
        content: bytes,
    ) -> SettingsRead:
        media_type = self._validate_logo(filename, content_type, content)
        organization = await self._organization()
        encoded = base64.b64encode(content).decode("ascii")
        organization.logo = f"data:{media_type};base64,{encoded}"
        await self.session.flush()
        return await self.read()

    @staticmethod
    def _subscription(organization: Organization) -> SubscriptionSettings:
        today = dt.date.today()
        until = organization.subscription_until
        days_left = max(0, (until - today).days) if until else 0
        if organization.status == OrganizationStatus.SUSPENDED or (
            until is not None and until < today
        ):
            status = "expired"
        elif days_left and days_left <= 14:
            status = "expiring"
        else:
            status = "active"
        started = organization.subscription_started_at
        used_months = (
            max(0, (today.year - started.year) * 12 + today.month - started.month) if started else 0
        )
        return SubscriptionSettings(
            status=status,
            plan=organization.subscription_plan,
            active_until=until,
            days_left=days_left,
            used_months=used_months,
            total_months=12,
            features=_FEATURES,
        )

    async def read(self) -> SettingsRead:
        organization = await self._organization()
        user = self.current_user
        return SettingsRead(
            service=ServiceSettings(
                name=organization.name,
                head_name=organization.head_name or user.full_name,
                legal_type=_LEGAL_TO_UI[organization.legal_form],
                tax_system=_TAX_TO_UI[organization.tax_system],
                inn=organization.inn,
                ogrn=organization.ogrn or "",
                bank_account=organization.bank_account or "",
                phone=organization.phone,
                email=organization.email or user.email,
                address=organization.legal_address,
                logo=organization.logo or "",
                description=organization.description or "",
            ),
            subscription=self._subscription(organization),
            security=SecuritySettings(
                # Хэш и исходный пароль никогда не возвращаются клиенту.
                current_password="",
                password_changed_at=user.password_changed_at.date(),
                security_level="medium",
                email_confirm_enabled=user.email_confirm_enabled,
                email=organization.email or user.email,
                phone_confirm_enabled=user.phone_confirm_enabled,
                phone=organization.phone,
                sessions=await self._sessions(),
                login_history=await self._login_history(),
            ),
        )

    async def update(self, data: SettingsUpdate) -> SettingsRead:
        if data.action is not None:
            # Почтовый провайдер ещё не подключён. Старый пароль остаётся
            # обязательным фактором при фактической смене пароля.
            return await self.read()
        if data.service is not None:
            organization = await self._organization()
            payload = data.service.model_dump(exclude_unset=True)
            if "inn" in payload:
                duplicate = (
                    await self.session.execute(
                        select(Organization.id).where(
                            Organization.inn == payload["inn"],
                            Organization.id != organization.id,
                        )
                    )
                ).scalar_one_or_none()
                if duplicate is not None:
                    raise ConflictError("Организация с таким ИНН уже существует")
            mapping = {
                "head_name": "head_name",
                "address": "legal_address",
                "legal_type": "legal_form",
            }
            for field, value in payload.items():
                target = mapping.get(field, field)
                if field == "legal_type":
                    if value not in _LEGAL_FROM_UI:
                        raise ConflictError("Неподдерживаемая организационная форма")
                    value = _LEGAL_FROM_UI[value]
                elif field == "tax_system":
                    if value not in _TAX_FROM_UI:
                        raise ConflictError("Неподдерживаемая система налогообложения")
                    value = _TAX_FROM_UI[value]
                elif field == "email" and value is not None:
                    value = str(value)
                setattr(organization, target, value)
            await self.session.flush()
        elif data.security is not None:
            if not verify_password(data.security.old_password, self.current_user.hashed_password):
                raise UnauthorizedError("Неверный текущий пароль")
            if data.security.current_password == data.security.old_password:
                raise ConflictError("Новый пароль должен отличаться от текущего")
            self.current_user.hashed_password = hash_password(data.security.current_password)
            self.current_user.password_changed_at = dt.datetime.now(dt.UTC)
            await self.session.flush()
        return await self.read()
