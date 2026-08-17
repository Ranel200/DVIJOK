# Календарь и создание заказа: frontend-интеграция

## Главное правило

Backend не выбирает и не проставляет свободное время автоматически.
`GET /schedule/availability` только предлагает актуальные варианты. Пользователь
должен явно выбрать один из них, после чего frontend вызывает reservation
endpoint. Заказ можно создать как черновик без мастера и даты.
Legacy-поля `mechanic_id`/`scheduled_at` в staff create/PATCH нельзя
использовать для обхода календаря: backend вернёт `422` и предложит reservation
endpoint. Client booking использует отдельный совместимый flow.

Все пути имеют префикс `/api/v1`. Нужен staff access token. Просмотр и настройка
календаря доступны ролям `admin` и `manager`; резервирование заказа — также
`admin`/`manager`.

## Рекомендуемый flow нового заказа

1. Создать заказ без календарного назначения:

```http
POST /api/v1/orders
Authorization: Bearer <staff_access_token>
Content-Type: application/json
```

```json
{
  "client_id": 12,
  "vehicle_id": 34,
  "items": [
    { "item_type": "service", "service_id": 8, "quantity": 1 }
  ]
}
```

2. Запросить предложения. `service_id` определяет длительность по каталогу:

```http
GET /api/v1/schedule/availability?date_from=2026-08-03&date_to=2026-08-09&service_id=8
Authorization: Bearer <staff_access_token>
```

Можно дополнительно передать `mechanic_id`. Если `service_id` не передан,
используется `duration_minutes`; если нет и его — 60 минут. Максимальный
диапазон — 31 день.

```json
{
  "date_from": "2026-08-03",
  "date_to": "2026-08-09",
  "timezone": "Europe/Moscow",
  "duration_minutes": 60,
  "slots": [
    {
      "mechanic_id": 5,
      "start_time": "2026-08-03T10:00:00+03:00",
      "end_time": "2026-08-03T11:00:00+03:00",
      "duration_minutes": 60
    }
  ]
}
```

Этот запрос read-only: он ничего не резервирует. Между показом списка и
подтверждением другой пользователь может занять вариант.

3. После явного выбора отправить точные `mechanic_id` и `start_time`:

```http
POST /api/v1/orders/91/reservation
Authorization: Bearer <staff_access_token>
Content-Type: application/json
```

```json
{
  "mechanic_id": 5,
  "start_time": "2026-08-03T10:00:00+03:00"
}
```

Если `duration_minutes` не передан, backend суммирует длительности service
items заказа с учётом quantity; заказ без услуг получает 60 минут.

Ответ `201`:

```json
{
  "id": 44,
  "created_at": "2026-07-28T12:00:00",
  "updated_at": "2026-07-28T12:00:00",
  "mechanic_id": 5,
  "order_id": 91,
  "work_type": null,
  "title": "Заказ 91",
  "start_time": "2026-08-03T10:00:00+03:00",
  "end_time": "2026-08-03T11:00:00+03:00"
}
```

При успехе заказу также записываются `mechanic_id` и `scheduled_at`.
Повторный POST для того же заказа атомарно переносит его бронь.

Если слот уже занят, заблокирован или вышел за рабочий график, backend
возвращает `422`. Frontend должен обновить availability и попросить выбрать
другой вариант, а не повторять запрос скрыто.

4. Снять бронь и вернуть заказ в неназначенное состояние:

```http
DELETE /api/v1/orders/91/reservation
Authorization: Bearer <staff_access_token>
```

Ответ `204`; `mechanic_id` и `scheduled_at` заказа становятся `null`.

## Индивидуальный график мастера

Получить текущий график:

```http
GET /api/v1/schedule/mechanics/5/working-hours
```

```json
{
  "mechanic_id": 5,
  "timezone": "Europe/Moscow",
  "uses_default": true,
  "intervals": [
    { "weekday": 0, "start_time": "09:00:00", "end_time": "18:00:00" }
  ]
}
```

`weekday`: `0` — понедельник, …, `6` — воскресенье. Время — локальное для
`timezone`. Пока график ни разу не сохранён, availability показывает default
Пн–Пт 09:00–18:00 (`uses_default=true`). Для обратной совместимости старые
client bookings у такого мастера не блокируются графиком до первого сохранения.

Полностью заменить график:

```http
PUT /api/v1/schedule/mechanics/5/working-hours
Content-Type: application/json
```

```json
{
  "intervals": [
    { "weekday": 0, "start_time": "09:00:00", "end_time": "13:00:00" },
    { "weekday": 0, "start_time": "14:00:00", "end_time": "18:00:00" },
    { "weekday": 2, "start_time": "10:00:00", "end_time": "19:00:00" }
  ]
}
```

Интервалы одного дня не должны пересекаться. Пустой `intervals` означает
полностью нерабочую неделю. Обед задаётся разрывом между двумя интервалами.

## Выходные, отпуск и исключения

Регулярные выходные — дни без working-hours interval. Разовые исключения
создаются существующим endpoint:

```http
POST /api/v1/schedule/blocks
```

```json
{
  "mechanic_id": 5,
  "start_time": "2026-08-10T00:00:00+03:00",
  "end_time": "2026-08-15T00:00:00+03:00",
  "reason": "Отпуск"
}
```

Availability исключает пересекающиеся blocks и существующие schedule slots.
Ручной reserve проверяет те же правила повторно.

## Длительность и шаг предложений

- `service_id` в availability: `Service.duration_minutes`;
- explicit `duration_minutes`: когда услуга не выбрана;
- reservation без duration: сумма длительностей услуг заказа × quantity;
- fallback: `DEFAULT_APPOINTMENT_DURATION_MINUTES` (60);
- начало предложений идёт с шагом `SCHEDULE_SLOT_STEP_MINUTES` (30);
- запись обязана целиком помещаться в один рабочий интервал и локальный день.

## Часовые пояса и конкурентность

Локальная зона задаётся backend-переменной `SCHEDULE_TIMEZONE` (default
`Europe/Moscow`). Frontend обязан передавать offset в date-time. Naive datetime
отклоняется с `422`.

При reservation backend блокирует строку мастера в транзакции, затем повторно
проверяет slots/blocks и только после этого создаёт slot. Одновременные запросы
для одного мастера выполняются последовательно: один получит `201`, второй —
`422`, если интервалы пересекаются.

## Типовые ошибки

- `401` — отсутствует/истёк staff token;
- `403` — роль mechanic пытается настраивать/резервировать;
- `404` — заказ, мастер или услуга не найдены в организации;
- `422` — невалидный диапазон, naive date-time, время вне графика,
  пересечение slot/block или пересекающиеся working-hours intervals.

Полная модель заказов и остальные endpoint’ы:
[api-reference.md](api-reference.md).
