# Интеграция клиентского frontend с backend

Документ описывает API существующего Vue/Quasar клиентского кабинета без
изменения его визуального сценария. Все пути имеют префикс `/api/v1`.

## Локальная конфигурация

- backend: `http://localhost:8000`;
- client frontend: `http://localhost:9001/client/`;
- API base URL frontend: `/api/v1`;
- dev proxy frontend: `/api` → `http://127.0.0.1:8000`;
- расписание и передаваемые даты используют `SCHEDULE_TIMEZONE`
  (по умолчанию `Europe/Moscow`).

Тестовые клиентские данные создаются идемпотентно командой
`python -m scripts.seed_client_demo`. Телефон: `+79991112233`, имя:
`Иван Клиентский`. При `OTP_PROVIDER=sms_ru_call` после запроса поступает
звонок; код — последние четыре цифры входящего номера. Для бесплатной локальной
отладки можно временно выбрать `OTP_PROVIDER=local` и взять `debug_code`.

Запросы с cookie должны выполняться с `credentials: "include"`. Access token
передаётся как `Authorization: Bearer <client_access_token>`. Client JWT нельзя
использовать в административном API и наоборот.

## Авторизация по телефону

### 1. Запросить код

`POST /api/v1/client-auth/otp/request`, public.

```json
{
  "phone": "+7 999 111 22 33"
}
```

Номер нормализуется в `+79991112233`. Ответ:

```json
{
  "detail": "Звонок поступит в ближайшее время. Введите последние 4 цифры номера.",
  "debug_code": null
}
```

В режиме SMS.ru `debug_code` всегда `null`, даже при `DEBUG=true`. Frontend уже
показывает инструкцию о последних четырёх цифрах и дополнительных изменений не
требует. Подробности backend-настройки: [phone-call-auth.md](phone-call-auth.md).

### 2. Подтвердить код

`POST /api/v1/client-auth/otp/verify`, public.

```json
{
  "phone": "+7 999 111 22 33",
  "code": "4821",
  "full_name": "Иванов Иван",
  "referral_code": "AbCdEf0123_-XyZ9"
}
```

`full_name` нужен при регистрации и может отсутствовать при обычном входе.
`referral_code` опционален. Успешный ответ сохраняет client refresh token в
отдельной HttpOnly cookie и для обратной совместимости также возвращает его в
JSON:

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer"
}
```

Frontend хранит access token только в памяти. Refresh token читать из
JavaScript или класть в localStorage не требуется.

### 3. Восстановить сессию

`POST /api/v1/client-auth/refresh`, public, HttpOnly cookie.

Тело не требуется. Legacy-клиенты могут отправить
`{"refresh_token":"<jwt>"}`. Backend вращает refresh token и отвечает:

```json
{
  "access_token": "<new-jwt>",
  "refresh_token": "<rotated-jwt>",
  "token": "<new-jwt>",
  "token_type": "bearer"
}
```

После refresh нужно записать новый access token в Pinia и вызвать
`GET /api/v1/client-auth/me`.

### 4. Текущий клиент и выход

- `GET /api/v1/client-auth/me`, client auth — профиль клиента;
- `PATCH /api/v1/client-auth/me`, client auth — сохранить ФИО:
  `{ "full_name": "Иван Петров" }`; обновлённое имя будет использоваться и
  в CRM-карточках автосервисов, с которыми связан клиент;
- `POST /api/v1/client-auth/logout`, client auth — отзывает refresh-сессию и
  удаляет cookie.

Типичные ошибки: `401` — неверный/истёкший OTP или токен; `422` — некорректный
телефон либо недействительный referral code; `429` — слишком много OTP-запросов;
`503` — SMS.ru временно недоступен или отклонил звонок.

## Экран «Записаться»

### Каталог автосервисов

`GET /api/v1/client-portal/ui/services?query=масло`, client auth.

```json
{
  "city": "г. Москва",
  "yours": [],
  "all": [
    {
      "id": "1",
      "name": "КОМИТ Тест",
      "address": "г. Москва, тестовая",
      "hours": "Открыто до 18:00",
      "description": "Автосервис полного цикла",
      "rating": "0",
      "reviews": 0,
      "lastVisit": "",
      "logo": ""
    }
  ]
}
```

`yours` содержит сервисы с историей клиента, `all` — остальные. Поиск учитывает
название, адрес, описание и названия услуг. До появления модуля отзывов backend
возвращает `rating=0`, `reviews=0`.

### Варианты услуги, автомобиля и мастера

`GET /api/v1/client-portal/ui/booking/options?shopId=1`, client auth.

```json
{
  "serviceOptions": [{"value": "3", "label": "Замена масла"}],
  "carOptions": [{"value": "8", "label": "Toyota Camry · А123ВС116"}],
  "masters": [
    {"id": "any", "name": "Любой мастер", "subtitle": "Определяется автоматически"},
    {"id": "5", "name": "Иван Мастеров", "subtitle": "Услуги"}
  ],
  "timeSlots": []
}
```

`timeSlots` намеренно пуст: время нельзя загружать до выбора услуги, мастера и
месяца.

### Свободные слоты месяца

`GET /api/v1/client-portal/ui/booking/availability`

Query:

- `shopId:int` — автосервис;
- `year:int`;
- `month:int` — месяц frontend, от `0` (январь) до `11`;
- `serviceId:int`;
- `masterId:int|"any"`.

```json
{
  "days": {"1": false, "2": true},
  "slots": [
    {
      "date": "2026-08-02",
      "time": "10:00",
      "masterId": "5",
      "startTime": "2026-08-02T10:00:00+03:00",
      "endTime": "2026-08-02T10:40:00+03:00"
    }
  ],
  "timezone": "Europe/Moscow"
}
```

Frontend отмечает даты через `days`, а после выбора даты показывает уникальные
`time` из `slots` этой даты. Endpoint только предлагает варианты и ничего не
резервирует.

### Подтвердить запись

`POST /api/v1/client-portal/ui/booking`, client auth.

```json
{
  "shopId": 1,
  "shopName": "КОМИТ Тест",
  "serviceId": 3,
  "carId": 8,
  "masterId": "any",
  "date": "2026-08-02",
  "time": "10:00"
}
```

При `masterId="any"` backend выбирает подходящего свободного мастера и
резервирует его. Проверка доступности и создание записи выполняются в одной
транзакции с блокировкой мастера. Ответ `201`:

```json
{
  "order_id": 17,
  "number": "000017",
  "organization_id": 1,
  "status": "new",
  "mechanic_id": 5,
  "slot_id": 29,
  "start_time": "2026-08-02T10:00:00+03:00",
  "end_time": "2026-08-02T10:40:00+03:00"
}
```

`404` означает отсутствующий сервис/автомобиль. `422` означает прошедшее,
занятое или недоступное время. После успеха frontend обновляет «Моё авто» и
историю.

## Экран «Моё авто»

`GET /api/v1/client-portal/ui/cars`, client auth.

Ответ имеет готовый формат существующих компонентов:

```json
{
  "cars": [
    {
      "id": "8",
      "brand": "Toyota Camry",
      "year": 2020,
      "color": "Белый",
      "plate": "А123ВС116",
      "vin": "TESTCLIENTVIN0001",
      "nextAppointment": {
        "serviceName": "КОМИТ Тест",
        "datetime": "02.08.2026 10:00",
        "service": "Замена масла",
        "master": "Иван Мастеров",
        "car": "Toyota Camry"
      },
      "maintenance": [{"label": "Крайний пробег", "value": "50 000 км"}],
      "repair": {
        "orderNumber": "000017",
        "carLabel": "Toyota Camry",
        "statuses": [
          {
            "id": "booked",
            "title": "Записан",
            "subtitle": "02.08.2026 10:00",
            "color": "#093095",
            "state": "current",
            "action": null
          }
        ]
      }
    }
  ],
  "bots": []
}
```

Ссылки ботов появляются только при настройке `TELEGRAM_BOT_PUBLIC_URL`,
`VK_BOT_PUBLIC_URL` или `MAX_BOT_PUBLIC_URL`. Каждый `href` содержит отдельный
одноразовый код текущего клиента; frontend открывает ссылку как есть. Полный
flow, статусы и backend-настройка описаны в [messenger-bots.md](messenger-bots.md).

## История и документ

`GET /api/v1/client-portal/ui/history`, client auth.

Возвращает `{ "items": [...] }` с полями текущего `HistoryCard`:
`id`, `title`, `status`, `carBrand`, `carPlate`, `serviceName`,
`serviceAddress`, `master`, `datetime`, `amount`, `orderNumber`, `orderReady`,
`monthLabel`.

Backend сводит доменные статусы к поддерживаемым UI-группам:

- `new`, `primary`, `secondary`, `waiting` → `new`;
- `diagnostics`, `in_progress` → `in_progress`;
- `approval`, `agreement` → `approval`;
- `done`, `cancelled` → `completed`.

`GET /api/v1/client-portal/ui/history/{orderId}/document`, client auth — отдаёт
последний готовый документ с `Content-Disposition: inline`. Чужой заказ даёт
`404`; заказ без документа — `404 Заказ-наряд ещё не готов`.

## Реферальный deep link

Публичная ссылка имеет вид `${PUBLIC_CLIENT_BASE_URL}/r/<code>`. Frontend
сохраняет код до успешного OTP и передаёт его в `referral_code`. После первой
атрибуции повторное сканирование не меняет организацию-источник.

## Порядок интеграции frontend

1. Включить real mode и dev proxy.
2. Подключить OTP request/verify/refresh/me/logout.
3. После восстановления сессии загружать `/ui/cars`.
4. Подключить каталог и booking options.
5. При смене месяца, услуги или мастера обновлять availability.
6. После выбора даты формировать кнопки времени из `slots` выбранного дня.
7. После успешной записи перечитать cars/history.
8. Открывать документ в новой вкладке с client Bearer token либо скачивать как
   Blob.
