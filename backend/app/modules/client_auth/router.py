"""HTTP-роутер client_auth: OTP-вход клиента по телефону (Система B).

Публичный вход (без staff-авторизации на уровне роутера) — /otp/* и /refresh.
/me и /link-token — за get_current_client.
"""

from typing import Literal, cast

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_client
from app.core.exceptions import UnauthorizedError
from app.modules.auth.schemas import AccessToken, RefreshRequest, TokenPair
from app.modules.client_auth.models import ClientAccount
from app.modules.client_auth.repository import ClientAuthRepository
from app.modules.client_auth.schemas import (
    ClientAccountRead,
    ClientAccountUpdate,
    LinkTokenRead,
    OtpRequest,
    OtpRequestResponse,
    OtpVerify,
)
from app.modules.client_auth.service import ClientAuthService
from app.modules.referrals.repository import ReferralRepository

router = APIRouter(prefix="/client-auth", tags=["client-auth"])


def _same_site() -> Literal["lax", "strict", "none"]:
    return cast(
        Literal["lax", "strict", "none"],
        settings.REFRESH_COOKIE_SAMESITE,
    )


def _request_meta(request: Request) -> tuple[str, str]:
    ip = request.client.host if request.client else ""
    return ip, request.headers.get("user-agent", "")


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.CLIENT_REFRESH_COOKIE_NAME,
        value=token,
        max_age=settings.CLIENT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite=_same_site(),
        domain=settings.REFRESH_COOKIE_DOMAIN or None,
        path="/",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.CLIENT_REFRESH_COOKIE_NAME,
        domain=settings.REFRESH_COOKIE_DOMAIN or None,
        path="/",
        secure=settings.REFRESH_COOKIE_SECURE,
        httponly=True,
        samesite=_same_site(),
    )


def get_client_auth_service(
    db: AsyncSession = Depends(get_db, scope="function"),
) -> ClientAuthService:
    return ClientAuthService(ClientAuthRepository(db), ReferralRepository(db))


@router.post("/otp/request", response_model=OtpRequestResponse)
async def request_otp(
    payload: OtpRequest,
    request: Request,
    service: ClientAuthService = Depends(get_client_auth_service),
) -> OtpRequestResponse:
    ip, _ = _request_meta(request)
    code = await service.request_otp(payload.phone, ip)
    is_call = settings.OTP_PROVIDER in {"sms_ru_call", "zvonok_flashcall"}
    return OtpRequestResponse(
        detail=(
            "Звонок поступит в ближайшее время. Введите последние 4 цифры номера."
            if is_call
            else "Код отправлен"
        ),
        # Реальный код звонка не возвращаем даже при DEBUG=true.
        debug_code=code if settings.DEBUG and not is_call else None,
    )


@router.post("/otp/verify", response_model=TokenPair)
async def verify_otp(
    payload: OtpVerify,
    request: Request,
    response: Response,
    service: ClientAuthService = Depends(get_client_auth_service),
) -> TokenPair:
    account = await service.verify_otp(
        payload.phone,
        payload.code,
        payload.referral_code,
        payload.full_name,
    )
    ip, user_agent = _request_meta(request)
    access, refresh = await service.create_session(
        account,
        ip=ip,
        user_agent=user_agent,
    )
    _set_refresh_cookie(response, refresh)
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=AccessToken)
async def refresh_token(
    request: Request,
    response: Response,
    body: RefreshRequest | None = None,
    service: ClientAuthService = Depends(get_client_auth_service),
) -> AccessToken:
    token = (body.refresh_token if body else None) or request.cookies.get(
        settings.CLIENT_REFRESH_COOKIE_NAME
    )
    if not token:
        raise UnauthorizedError("Refresh-токен не передан")
    access, rotated = await service.refresh(token)
    if rotated is not None:
        _set_refresh_cookie(response, rotated)
    return AccessToken(access_token=access, refresh_token=rotated, token=access)


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    _: ClientAccount = Depends(get_current_client),
    service: ClientAuthService = Depends(get_client_auth_service),
) -> dict[str, bool]:
    await service.revoke(request.cookies.get(settings.CLIENT_REFRESH_COOKIE_NAME))
    _clear_refresh_cookie(response)
    return {"success": True}


@router.get("/me", response_model=ClientAccountRead)
async def me(current_client: ClientAccount = Depends(get_current_client)) -> ClientAccountRead:
    return ClientAccountRead.model_validate(current_client)


@router.patch("/me", response_model=ClientAccountRead)
async def update_me(
    payload: ClientAccountUpdate,
    current_client: ClientAccount = Depends(get_current_client),
    service: ClientAuthService = Depends(get_client_auth_service),
) -> ClientAccountRead:
    account = await service.update_profile(current_client, payload.full_name)
    return ClientAccountRead.model_validate(account)


@router.post("/link-token", response_model=LinkTokenRead)
async def link_token(
    current_client: ClientAccount = Depends(get_current_client),
    service: ClientAuthService = Depends(get_client_auth_service),
) -> LinkTokenRead:
    return LinkTokenRead(link_token=service.issue_link_token(current_client.id))
