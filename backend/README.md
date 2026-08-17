# Движок backend

FastAPI backend автосервиса: staff/admin CRM, календарь мастеров, услуги,
заказы и документы, задачи, настройки, referral QR и клиентский кабинет.

## Быстрый локальный запуск через Docker

Требуются Docker Desktop и свободные порты `5432`, `6379`, `8000`.

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec api python -m scripts.seed
```

После запуска:

- health: <http://localhost:8000/health>;
- Swagger UI: <http://localhost:8000/docs>;
- OpenAPI: <http://localhost:8000/api/v1/openapi.json>.

Dev-администратор из `.env.example`: `admin@komit.ru` / `admin12345`.
`scripts.seed` идемпотентен и не меняет пароль существующего пользователя.

Остановка без удаления данных:

```bash
docker compose down
```

Команда `docker compose down -v` удаляет локальную БД и потому намеренно не
рекомендуется как обычный шаг.

## Запуск backend без контейнера API

PostgreSQL и Redis можно оставить в Docker:

```bash
docker compose up -d db redis
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
cp .env.example .env
.venv/bin/alembic upgrade head
.venv/bin/python -m scripts.seed
.venv/bin/uvicorn app.main:app --reload --port 8000
```

## Проверки

```bash
.venv/bin/pytest -q
.venv/bin/ruff check app tests
.venv/bin/alembic check
```

Для `alembic check` нужна актуальная PostgreSQL-база из `DATABASE_URL`.
Подробности миграций: [docs/migrations.md](docs/migrations.md). Полный API:
[docs/api-reference.md](docs/api-reference.md).

## Подключение admin frontend

Frontend запускается на `http://localhost:9000`. Его runtime-переменные:

```dotenv
VITE_USE_MOCK=false
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Backend уже разрешает этот origin через CORS. Точный статус интеграции и
небольшие изменения, которые ещё требуется согласовать для frontend:
[docs/admin-frontend-integration.md](docs/admin-frontend-integration.md).
