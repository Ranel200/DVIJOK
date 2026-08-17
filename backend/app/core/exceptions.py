"""Доменные исключения приложения и регистрация обработчиков FastAPI.

Сервисы бросают подклассы AppException — роутеры не содержат try/except и не
знают о HTTP-кодах бизнес-ошибок: маппинг централизован здесь.
"""

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppException(Exception):
    status_code: int = 400
    detail: str = "Ошибка приложения"

    def __init__(self, detail: str | None = None) -> None:
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class NotFoundError(AppException):
    status_code = 404
    detail = "Ресурс не найден"


class ConflictError(AppException):
    status_code = 409
    detail = "Конфликт данных"


class UnauthorizedError(AppException):
    status_code = 401
    detail = "Не авторизован"


class ForbiddenError(AppException):
    status_code = 403
    detail = "Недостаточно прав"


class BusinessRuleError(AppException):
    status_code = 422
    detail = "Нарушение бизнес-правила"


class ServiceUnavailableError(AppException):
    status_code = 503
    detail = "Внешний сервис временно недоступен"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def _handle_app_exception(_: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "message": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def _handle_validation_error(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        first = errors[0] if errors else None
        message = str(first.get("msg")) if first else "Ошибка проверки данных"
        return JSONResponse(
            status_code=422,
            content=jsonable_encoder({"detail": errors, "message": message}),
        )
