# Миграции базы данных

## Обычное применение

Перед обновлением production-базы сделайте резервную копию, затем выполните:

```bash
alembic upgrade head
```

Актуальная цепочка:

```text
ca9578f833fe (legacy initial)
  -> 41b7e2a9d6c0 (schema reconciliation)
  -> 7d3a1f0c2b4e (referrals)
  -> 8f3c2d91a6b4 (order documents)
  -> 9c4f2a8e1d70 (mechanic working hours)
  -> b6e1c4a2d9f0 (order acquisition source)
  -> c8f4a2d7e1b3 (staff profile fields)
  -> d1a7f3c9e5b2 (expanded service catalog)
  -> d2c8a4f1b6e9 (CRM line discounts and masters)
  -> d3e9b5a2c7f1 (staff tasks)
  -> d4f1c6b8a3e2 (organization/admin settings)
  -> d5a2e7c9b4f3 (staff document metadata and recurring breaks)
  -> e2f6a1c8d4b0 (staff phone/login identity and exact UI roles)
  -> e3a7b2d9c5f1 (work schedules for every staff member)
  -> e4b8c3d0a6f2 (exact admin service categories)
  -> e5c9d4a1b7f3 (multiple order documents)
  -> e6d0a5b2c8f4 (rotating staff refresh sessions and login audit)
  -> e7a1b6c3d9f5 (private employee document storage)
  -> e8b2c7d4f0a6 (free movement between CRM board statuses)
  -> f1c3d5e7a9b2 (rotating client refresh sessions)
  -> f2d4e6a8b0c1 (empty CRM order drafts)
  -> f3e5a7c9b1d2 (global client vehicles)
  -> f4a6b8c0d2e4 (organization owner flag)
  -> f5b7c9d1e3a5 (messenger bindings and notification outbox)
  -> f6c8d0e2a4b6 (stable client booking services)
  -> f7d9e1a3b5c7 (client booking without placeholder prices)
  -> f8e2a4c6b0d1 (staff accounts without email)
  -> f9a3b5c7d1e2 (per-organization order numbering)
```

Ревизия `41b7e2a9d6c0` оставляет исходную initial-миграцию неизменной и безопасно
добавляет отсутствовавшие в ней организации, tenant scoping, client accounts и
связь CRM-клиента с глобальным аккаунтом. Операции проверяют фактическую схему,
поэтому миграцию можно применять и к базе, где client backend ранее был создан
вне Alembic.

Если в старой pre-tenant схеме уже есть данные, они не удаляются. Миграция
создаёт служебную организацию `Legacy data (migration)` и относит старые записи
к ней. После обновления администратор БД должен проверить эти записи и при
необходимости перенести их в реальные организации.

Reconciliation-ревизия является forward-only: её `downgrade` намеренно не
удаляет tenant/client колонки, поскольку они могли существовать до регистрации
ревизии в Alembic. Referral-ревизия имеет обычный обратимый downgrade.

## Проверка чистой установки

Команды нужно запускать только против отдельной пустой PostgreSQL-базы:

```bash
export DATABASE_URL=postgresql+asyncpg://user@localhost:5432/komit_migration_test
alembic upgrade head
alembic check
```

`alembic check` должен завершиться сообщением:

```text
No new upgrade operations detected.
```

Это означает, что созданная миграциями схема соответствует текущей SQLAlchemy
metadata. Не используйте production-базу для тестового downgrade или stamp.
