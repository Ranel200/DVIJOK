"""HTTP-роутер аутентификации: login, register facade, refresh, me."""

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import BusinessRuleError, ForbiddenError, UnauthorizedError
from app.core.rate_limit import login_rate_limit
from app.modules.auth.schemas import (
    AccessToken,
    AdminFrontendRegister,
    RefreshRequest,
    StaffSession,
    StaffUser,
    SubscriptionSelection,
)
from app.modules.auth.service import AuthService
from app.modules.organizations.models import Organization
from app.modules.organizations.repository import OrganizationRepository
from app.modules.organizations.schemas import OrganizationRegister
from app.modules.organizations.service import OrganizationService
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserRead
from app.shared.enums import LegalForm, TaxSystem

router = APIRouter(prefix="/auth", tags=["auth"])


def _request_meta(request: Request) -> tuple[str, str]:
    ip = request.client.host if request.client else ""
    return ip, request.headers.get("user-agent", "")


def _set_refresh_cookie(response: Response, token: str, remember: bool) -> None:
    max_age = None
    if remember:
        max_age = settings.REMEMBER_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=token,
        max_age=max_age,
        httponly=True,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
        domain=settings.REFRESH_COOKIE_DOMAIN or None,
        path="/",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        domain=settings.REFRESH_COOKIE_DOMAIN or None,
        path="/",
        secure=settings.REFRESH_COOKIE_SECURE,
        httponly=True,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
    )


def get_auth_service(
    db: AsyncSession = Depends(get_db, scope="function"),
) -> AuthService:
    return AuthService(UserRepository(db))


def _user_read(user: User, subscription_plan: str | None) -> UserRead:
    return UserRead.model_validate(user).model_copy(
        update={"subscription_plan": (subscription_plan or "none").lower()}
    )


def _session(
    access: str,
    refresh: str,
    user: User,
    subscription_plan: str | None,
) -> StaffSession:
    return StaffSession(
        access_token=access,
        refresh_token=refresh,
        token=access,
        user=_user_read(user, subscription_plan),
    )


@router.post(
    "/login",
    response_model=StaffSession,
    dependencies=[Depends(login_rate_limit)],
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["email", "password"],
                        "properties": {
                            "email": {
                                "type": "string",
                                "description": "Телефон, email или логин сотрудника",
                            },
                            "password": {"type": "string", "format": "password"},
                        },
                    }
                },
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "required": ["username", "password"],
                        "properties": {
                            "username": {"type": "string"},
                            "password": {"type": "string", "format": "password"},
                        },
                    }
                },
            },
        }
    },
)
async def login(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> StaffSession:
    """Принимает старый OAuth form и JSON готовой admin-панели."""
    content_type = request.headers.get("content-type", "").lower()
    if "application/json" in content_type:
        data = await request.json()
        identifier = (
            data.get("email")
            or data.get("phone")
            or data.get("login")
            or data.get("username")
        )
        password = data.get("password")
        remember = bool(data.get("remember", False))
    else:
        data = await request.form()
        identifier = data.get("username") or data.get("email")
        password = data.get("password")
        remember = str(data.get("remember", "")).lower() in {"1", "true", "on", "yes"}
    if not isinstance(identifier, str) or not isinstance(password, str):
        raise UnauthorizedError("Неверный телефон, почта, логин или пароль")
    ip, user_agent = _request_meta(request)
    try:
        user = await service.authenticate(identifier, password)
    except UnauthorizedError:
        candidate = await service.repo.get_by_identifier(identifier)
        await service.record_login(
            identifier,
            success=False,
            user=candidate,
            ip=ip,
            user_agent=user_agent,
        )
        # Failed login audit must survive the request rollback.
        await service.repo.session.commit()
        raise
    access, refresh, _ = await service.create_session(
        user,
        remember=remember,
        ip=ip,
        user_agent=user_agent,
    )
    await service.record_login(
        identifier,
        success=True,
        user=user,
        ip=ip,
        user_agent=user_agent,
    )
    _set_refresh_cookie(response, refresh, remember)
    organization = await service.repo.session.get(Organization, user.organization_id)
    return _session(
        access,
        refresh,
        user,
        organization.subscription_plan if organization else None,
    )


@router.post(
    "/register",
    response_model=StaffSession,
    status_code=status.HTTP_201_CREATED,
)
async def register_from_admin_frontend(
    payload: AdminFrontendRegister,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db, scope="function"),
) -> StaffSession:
    legal_forms = {
        "ИП": LegalForm.IP,
        "ООО": LegalForm.OOO,
        "ОАО": LegalForm.OAO,
        "ЗАО": LegalForm.ZAO,
        "ПАО": LegalForm.PAO,
    }
    tax_systems = {"УСН": TaxSystem.USN, "НДС": TaxSystem.NDS}
    if payload.legal_type not in legal_forms or payload.tax_system not in tax_systems:
        raise BusinessRuleError("Неподдерживаемая юридическая форма или налоговая система")
    await OrganizationService(OrganizationRepository(db)).register(
        OrganizationRegister(
            name=payload.name,
            inn=payload.inn,
            tax_system=tax_systems[payload.tax_system],
            legal_form=legal_forms[payload.legal_type],
            legal_address=payload.address,
            phone=payload.phone,
            admin_full_name=payload.contact_name,
            admin_email=payload.email,
            admin_password=payload.password,
        )
    )
    user = await UserRepository(db).get_by_email(str(payload.email).lower())
    assert user is not None
    organization = await db.get(Organization, user.organization_id)
    assert organization is not None
    organization.head_name = payload.head_name
    organization.email = str(payload.email)
    await db.flush()
    auth = AuthService(UserRepository(db))
    ip, user_agent = _request_meta(request)
    access, refresh, _ = await auth.create_session(
        user,
        remember=False,
        ip=ip,
        user_agent=user_agent,
    )
    await auth.record_login(
        str(payload.email),
        success=True,
        user=user,
        ip=ip,
        user_agent=user_agent,
    )
    _set_refresh_cookie(response, refresh, False)
    return _session(access, refresh, user, organization.subscription_plan)


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    _: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> dict[str, bool]:
    await service.revoke_token(request.cookies.get(settings.REFRESH_COOKIE_NAME))
    _clear_refresh_cookie(response)
    return {"success": True}


@router.post("/refresh", response_model=AccessToken)
async def refresh_token(
    request: Request,
    response: Response,
    body: RefreshRequest | None = None,
    service: AuthService = Depends(get_auth_service),
) -> AccessToken:
    token = (body.refresh_token if body else None) or request.cookies.get(
        settings.REFRESH_COOKIE_NAME
    )
    if not token:
        raise UnauthorizedError("Refresh-токен не передан")
    access, rotated, remember = await service.refresh(token)
    if rotated is not None:
        _set_refresh_cookie(response, rotated, remember)
    return AccessToken(access_token=access, refresh_token=rotated, token=access)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> None:
    await service.revoke_session(current_user, session_id)


@router.delete("/sessions", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_other_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> None:
    await service.revoke_other_sessions(
        current_user,
        getattr(request.state, "staff_session_id", None),
    )


@router.get("/me", response_model=UserRead)
async def me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db, scope="function"),
) -> UserRead:
    organization = await db.get(Organization, current_user.organization_id)
    return _user_read(
        current_user,
        organization.subscription_plan if organization else None,
    )


@router.post("/subscription", response_model=StaffUser)
async def select_subscription(
    payload: SubscriptionSelection,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db, scope="function"),
) -> StaffUser:
    """Сохраняет выбранный владельцем тариф после регистрации."""

    if not current_user.is_owner:
        raise ForbiddenError("Только владелец может менять тариф")
    organization = await db.get(Organization, current_user.organization_id)
    if organization is None:
        raise BusinessRuleError("Организация пользователя не найдена")
    organization.subscription_plan = payload.plan.upper()
    await db.flush()
    return StaffUser(user=_user_read(current_user, organization.subscription_plan))
