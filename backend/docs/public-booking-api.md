# Публичная запись по ссылке: API для frontend

## Назначение

Автосервис размещает `booking_url` из административного referral API на картах,
в соцсетях или в QR. Посетитель открывает ссылку без аккаунта, выбирает услугу,
специалиста, свободные дату и время, вводит контактные данные и создаёт заявку.

Ссылка имеет вид:

```text
https://app.example.ru/client/book/AbCdEf0123_-XyZ9
```

Последний сегмент — постоянный публичный код, а не ID организации и не секрет.
Все API-пути ниже имеют префикс `/api/v1`; авторизация не требуется.

## Порядок вызовов

1. Извлечь `code` из `/book/:code`.
2. Получить контекст автосервиса.
3. Загрузить услуги и специалистов.
4. После выбора услуги/специалиста запросить доступность месяца.
5. Пользователь вручную выбирает один слот.
6. Отправить заявку. Свободное время не назначается автоматически.

## Контекст автосервиса

`GET /api/v1/public-booking/{code}`

```json
{
  "city": "Казань",
  "branches": [
    {
      "id": "AbCdEf0123_-XyZ9",
      "name": "Автосервис Движок",
      "address": "г. Казань, ул. Примерная, 1",
      "isOpen": true,
      "until": "20:00",
      "mapSrc": "/client/icons/record/map.png"
    }
  ]
}
```

Всегда возвращается максимум один автосервис. Поле `id` содержит тот же
публичный код и не является внутренним ID организации.

## Услуги

`GET /api/v1/public-booking/{code}/options`

```json
{
  "serviceOptions": [
    { "value": "12", "label": "Диагностика", "price": "2500.00" }
  ],
  "carOptions": [],
  "masters": [
    { "id": "any", "name": "Любой мастер", "subtitle": "Определяется автоматически" }
  ],
  "timeSlots": []
}
```

Для гостя `carOptions` пуст: сведения об автомобиле вводятся на последнем шаге.

## Специалисты

`GET /api/v1/public-booking/{code}/specialists`

```json
{
  "specialists": [
    {
      "id": "5",
      "name": "Иван Мастеров",
      "role": "Мастер",
      "avatarColor": "var(--dvijok-accent-coral)",
      "rating": "0.00",
      "reviews": 0,
      "price": "2500.00",
      "nearestDate": "среда, 12 августа",
      "slots": ["09:00", "09:30"]
    }
  ]
}
```

Frontend также может передать `specialistId=any`; backend выберет мастера только
после того, как пользователь явно выбрал время.

## Свободные слоты

`GET /api/v1/public-booking/{code}/availability`

Query-параметры:

- `year` — год, например `2026`;
- `month` — индекс месяца от `0` (январь) до `11` (декабрь);
- `serviceId` — выбранная услуга;
- `specialistId` — ID специалиста либо `any`.

Пример:

```http
GET /api/v1/public-booking/AbCdEf0123_-XyZ9/availability?year=2026&month=7&serviceId=12&specialistId=5
```

```json
{
  "days": { "11": false, "12": true, "13": true },
  "slots": [
    {
      "date": "2026-08-12",
      "time": "09:00",
      "masterId": "5",
      "startTime": "2026-08-12T09:00:00+03:00",
      "endTime": "2026-08-12T10:00:00+03:00"
    }
  ],
  "timezone": "Europe/Moscow"
}
```

## Создать гостевую заявку

`POST /api/v1/public-booking/{code}`

```json
{
  "serviceId": 12,
  "specialistId": 5,
  "date": "2026-08-12",
  "time": "09:00",
  "client": {
    "name": "Иванов Иван",
    "phone": "+7 999 111-22-33",
    "brand": "Toyota",
    "model": "Camry",
    "plateType": "ru",
    "plate": "А123ВС116",
    "consentPersonal": true,
    "consentTransfer": true
  }
}
```

Успех — `201 Created`:

```json
{
  "number": "4831",
  "status": "new",
  "startTime": "2026-08-12T09:00:00+03:00",
  "endTime": "2026-08-12T10:00:00+03:00"
}
```

Ответ не содержит ID организации, клиента, автомобиля, заказа или слота.
Backend повторно проверяет принадлежность услуги/мастера организации и
доступность слота, а затем в одной транзакции создаёт CRM-карточки, заказ в
статусе `new` с источником `referral` и резерв календаря. Аккаунт клиента и
токены не создаются. Если телефон уже принадлежит существующему аккаунту, заказ
будет доступен ему после обычного OTP-входа.

## Ошибки

- `404` — код неизвестен, автосервис неактивен, услуга или мастер не найдены;
- `422` — неверные поля/согласия, прошедшая дата, время занято или недоступно;
- `429` — превышен лимит гостевых заявок для IP и ссылки.

При `422` frontend читает человекочитаемое сообщение из поля `message`.

## Настройка frontend и deployment

- маршрут SPA: `/book/:referralCode`, без `requiresAuth`;
- backend URL: обычный `VITE_API_BASE_URL`/`QCLI_API_BASE_URL`;
- production `PUBLIC_CLIENT_BASE_URL` должен указывать на публичный HTTPS-корень
  клиентского SPA, например `https://app.example.ru/client`;
- reverse proxy должен направлять `/api/v1` в FastAPI и поддерживать history
  fallback клиентского SPA для `/client/book/*`;
- для mobile deep link используется тот же HTTPS-домен.
