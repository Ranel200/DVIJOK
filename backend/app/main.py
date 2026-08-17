"""Точка входа FastAPI: фабрика приложения, регистрация роутеров и middleware."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import app.models  # noqa: F401
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.modules.auth.router import router as auth_router
from app.modules.client_auth.router import router as client_auth_router
from app.modules.client_portal.public_router import router as public_booking_router
from app.modules.client_portal.router import frontend_router as client_frontend_router
from app.modules.client_portal.router import router as client_portal_router
from app.modules.client_vehicles.router import router as client_vehicles_router
from app.modules.clients.router import router as clients_router
from app.modules.crm.router import router as crm_router
from app.modules.employees.router import router as employees_router
from app.modules.inventory.router import router as inventory_router
from app.modules.mechanics.router import router as mechanics_router
from app.modules.notifications.router import router as notifications_router
from app.modules.notifications.service import NotificationDispatcher
from app.modules.orders.router import router as orders_router
from app.modules.organizations.router import router as organizations_router
from app.modules.referrals.router import router as referrals_router
from app.modules.schedule.router import router as schedule_router
from app.modules.services.router import router as services_router
from app.modules.settings.router import router as settings_router
from app.modules.tariffs.router import router as tariffs_router
from app.modules.tasks.router import router as tasks_router
from app.modules.users.router import router as users_router
from app.modules.vehicles.router import router as vehicles_router

ROUTERS = [
    organizations_router,
    tariffs_router,
    referrals_router,
    auth_router,
    users_router,
    employees_router,
    crm_router,
    clients_router,
    vehicles_router,
    services_router,
    settings_router,
    tasks_router,
    mechanics_router,
    orders_router,
    schedule_router,
    inventory_router,
    client_auth_router,
    public_booking_router,
    client_frontend_router,
    client_vehicles_router,
    client_portal_router,
    notifications_router,
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    from app.core.database import async_session_factory, engine

    dispatcher = NotificationDispatcher(async_session_factory)
    worker: asyncio.Task[None] | None = None
    if settings.NOTIFICATIONS_ENABLED:
        worker = asyncio.create_task(
            dispatcher.run_forever(), name="notification-outbox-worker"
        )
    try:
        yield
    finally:
        if worker is not None:
            dispatcher.stop()
            await worker
        await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        docs_url="/docs",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    @app.middleware("http")
    async def security_and_limits(request: Request, call_next):
        # Защита от слишком больших тел запросов (по Content-Length).
        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit():
            if int(content_length) > settings.MAX_REQUEST_BODY_BYTES:
                return JSONResponse(
                    status_code=413,
                    content={
                        "detail": "Слишком большое тело запроса",
                        "message": "Слишком большое тело запроса",
                    },
                )
        response = await call_next(request)
        # Security-заголовки (CSP не задаём, чтобы не ломать Swagger UI — см. README).
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Permissions-Policy", "geolocation=(), microphone=(), camera=()"
        )
        if settings.is_production:
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=63072000; includeSubDomains"
            )
        return response

    for router in ROUTERS:
        app.include_router(router, prefix=settings.API_V1_PREFIX)

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.APP_NAME}

    return app


app = create_app()
