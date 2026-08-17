# Уведомления клиентов в Telegram, VK и MAX

## Назначение и пользовательский сценарий

Кнопки Telegram, VK и MAX в разделе клиента «Моё авто» подключают выбранный
мессенджер к текущей клиентской учётной записи. Визуальная часть frontend не
меняется: `GET /api/v1/client-portal/ui/cars` возвращает готовые `href` для уже
существующих кнопок.

Сценарий:

1. Авторизованный клиент открывает «Моё авто».
2. Backend создаёт отдельную одноразовую ссылку для каждого настроенного канала.
3. Клиент нажимает кнопку, открывает бота и нажимает Start/Начать.
4. Webhook получает одноразовый код и ID диалога, после чего навсегда связывает
   мессенджер с глобальным `ClientAccount`.
5. Создание заказа и дальнейшие смены стадии в канбане записывают сообщения в
   outbox. Фоновый обработчик доставляет их независимо от CRM-транзакции.

В публичной записи без регистрации уведомление о создании приходит только если
номер телефона уже принадлежит клиентской учётке с подключённым ботом. Если
клиент сначала оставил гостевую заявку, а затем подтвердил тот же телефон по
OTP, существующая CRM-карточка связывается с его учёткой; последующие изменения
статуса будут приходить в подключённые каналы.

## API для frontend

### `GET /api/v1/client-portal/ui/cars`

Авторизация: клиентский `Authorization: Bearer <access_token>`.

Поле `bots` ответа:

```json
{
  "cars": [],
  "bots": [
    {
      "id": "tg",
      "label": "@dvijok_bot",
      "icon": "/client/icons/my-car/tg.png",
      "href": "https://t.me/dvijok_bot?start=V_1Wr1JxkY8n1zJVi6GtzX6p5nPpPjdi"
    },
    {
      "id": "vk",
      "label": "@dvijok",
      "icon": "/client/icons/my-car/vk.png",
      "href": "https://vk.me/dvijok?ref=...&ref_source=dvijok"
    },
    {
      "id": "max",
      "label": "@dvijok_bot",
      "icon": "/client/icons/my-car/max.png",
      "href": "https://max.ru/dvijok_bot?start=..."
    }
  ]
}
```

Frontend должен использовать `href` как есть и не извлекать/не хранить код.
Ссылка действует `CLIENT_LINK_TOKEN_TTL_SECONDS` (по умолчанию 10 минут),
одноразовая и относится только к одному каналу. Если она истекла, достаточно
повторно запросить `/ui/cars`. В БД хранится SHA-256 кода, а не сам код. Ни
внутренний ID клиента, ни токен Bot API в ссылку не попадают.

Канал отсутствует в `bots`, пока для него не настроен `*_BOT_PUBLIC_URL`.

### Webhook endpoint'ы

Эти маршруты вызывают только платформы ботов; клиентский frontend их не вызывает.

| Канал | Метод и путь | Проверка подлинности | Успех |
|---|---|---|---|
| Telegram | `POST /api/v1/bot-gateway/telegram/webhook` | `X-Telegram-Bot-Api-Secret-Token` | `200 {"ok": true}` |
| VK | `POST /api/v1/bot-gateway/vk/webhook` | поле `secret` в JSON | `200 ok`; для `confirmation` — код подтверждения |
| MAX | `POST /api/v1/bot-gateway/max/webhook` | `X-Max-Bot-Api-Secret` | `200 {"ok": true}` |

Ошибочная, истёкшая или уже использованная другим аккаунтом ссылка не меняет
существующую привязку. Повтор того же webhook после успешной привязки
идемпотентен.

## Логика статусов и текстов

Одинаковый клиентский этап отправляется не более одного раза на заказ и канал,
даже если администратор последовательно прошёл через несколько внутренних
статусов с тем же смыслом.

| Внутренний статус заказа | Клиентский этап | Уведомление |
|---|---|---|
| `new` | Записан | «Вы записаны. Статус: „Записан“» |
| `diagnostics`, `in_progress` | В работе | «Ваш автомобиль в работе» |
| `approval`, `agreement`, `waiting` | Согласование | «Статус заказа: „Согласование“» |
| `done` | Готово | «Работа завершена. Автомобиль готов» |
| `cancelled` | Отменён | «Запись отменена» |
| `primary`, `secondary` | без отдельного сообщения | — |

Это покрывает оба согласованных сценария:

- «Диагностика»: `new` → `diagnostics` → `approval/agreement` → `done`;
- «Работа»: `new` → `in_progress` → `waiting` → `done`.

Недоступность внешнего Bot API не откатывает заказ и не мешает перетаскиванию
карточки. Ошибка сохраняется в outbox и повторяется до
`NOTIFICATION_MAX_ATTEMPTS` раз.

## Backend-конфигурация

```dotenv
CLIENT_LINK_TOKEN_TTL_SECONDS=600
NOTIFICATIONS_ENABLED=true
NOTIFICATION_POLL_INTERVAL_SECONDS=2
NOTIFICATION_MAX_ATTEMPTS=5

TELEGRAM_BOT_TOKEN=
TELEGRAM_BOT_PUBLIC_URL=https://t.me/dvijok_bot
TELEGRAM_WEBHOOK_SECRET=

VK_BOT_TOKEN=
VK_BOT_PUBLIC_URL=https://vk.me/dvijok
VK_BOT_SECRET=
VK_CONFIRMATION_CODE=
VK_API_VERSION=5.199

MAX_BOT_TOKEN=
MAX_BOT_PUBLIC_URL=https://max.ru/dvijok_bot
MAX_WEBHOOK_SECRET=
```

Токены и webhook-секреты хранятся только в переменных окружения backend. Их
нельзя добавлять во frontend, Git или QR/публичные ссылки. В production
`NOTIFICATIONS_ENABLED=true` требует URL, Bot API token и webhook secret для
каждого включённого канала.

## Подключение провайдеров

Перед настройкой webhook backend должен быть опубликован по HTTPS, а миграции
должны быть применены командой `alembic upgrade head`.

Telegram: зарегистрировать
`https://<api-domain>/api/v1/bot-gateway/telegram/webhook` через `setWebhook`,
передав то же значение в `secret_token`, что указано в
`TELEGRAM_WEBHOOK_SECRET`. Deep link имеет официальный формат
`https://t.me/<bot>?start=<payload>`.

VK: в Callback API сообщества указать
`https://<api-domain>/api/v1/bot-gateway/vk/webhook`, сохранить выданный код в
`VK_CONFIRMATION_CODE`, а секрет — в `VK_BOT_SECRET`. Для сообщений сообщества
должно быть разрешено событие `message_new`.

MAX: создать подписку `POST https://platform-api2.max.ru/subscriptions` с URL
`https://<api-domain>/api/v1/bot-gateway/max/webhook`, типом события
`bot_started` и секретом `MAX_WEBHOOK_SECRET`. Ссылка использует официальный
формат `https://max.ru/<bot>?start=<payload>`; отправка выполняется через
`POST https://platform-api2.max.ru/messages`.

Без реальных токенов локально можно полностью проверить генерацию ссылок,
webhook-привязку, создание outbox и дедупликацию. Фактическая доставка во
внешний мессенджер проверяется после передачи токенов и публикации HTTPS URL.
