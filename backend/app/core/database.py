"""Async-движок SQLAlchemy и фабрика сессий.

Транзакция привязана к запросу (Unit of Work): get_db() коммитит при успехе и
откатывает при исключении. Репозитории внутри используют flush() — единый
commit выполняется на границе HTTP-запроса.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Пул соединений не применяется к SQLite (используется в тестах).
_engine_kwargs: dict = {"echo": settings.DB_ECHO, "pool_pre_ping": True}
if not settings.DATABASE_URL.startswith("sqlite"):
    _engine_kwargs.update(
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
    )

engine = create_async_engine(settings.DATABASE_URL, **_engine_kwargs)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI-зависимость: сессия БД с авто-commit/rollback на границе запроса."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
