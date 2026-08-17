# Движок API: полный справочник для frontend

Документ соответствует зарегистрированным маршрутам текущего `app.main`.
Интерактивная схема доступна на `/docs`, машинная OpenAPI-схема —
`/api/v1/openapi.json`.

## Общие правила

- Базовый префикс API: `/api/v1`. Исключение — `GET /health`.
- JSON используется по умолчанию. Staff-login принимает JSON или
  `application/x-www-form-urlencoded`; импорты/загрузки используют multipart,
  а QR, XLSX и документы возвращаются как бинарные ответы.
- Даты: `YYYY-MM-DD`. Date-time: ISO 8601; frontend должен передавать часовой
  пояс, например `2026-08-01T10:00:00+03:00`.
- Денежные и decimal-поля в ответах сериализуются строками, например `"1250.00"`.
  Во входных JSON допустимы JSON number или строка с числом.
- Необъявленные поля request body запрещены. В PATCH передаются только
  изменяемые поля.
- Пагинация: `limit` (1–200, default 50), `offset` (>=0, default 0). Ответ:
  `{ "items": T[], "total": 123, "limit": 50, "offset": 0 }`.
- Все staff-ресурсы tenant-scoped: ID из другой организации обычно выглядит
  как `404`, а не раскрывается как чужой ресурс.

### Авторизация

Staff и client используют разные JWT-контуры, хотя заголовок одинаков:

```http
Authorization: Bearer <access_token>
```

- `staff:any` — `admin`, `manager` или `mechanic`;
- `staff:admin+manager` — только `admin`/`manager`;
- `staff:admin` — только `admin`;
- `staff:admin+mechanic` — только `admin`/`mechanic`;
- `client` — access token из `/client-auth/otp/verify`;
- `public` — токен не нужен.

Staff token не подходит client endpoint’ам и наоборот.

### Общие статусы и ошибки

Успех: `200`, создание: `201`, удаление без тела: `204`.

Доменные ошибки имеют форму:

```json
{ "detail": "Описание ошибки", "message": "Описание ошибки" }
```

`detail` сохранён для стандартных FastAPI-клиентов, `message` добавлен для
готовой admin-панели. У validation-ошибки `detail` остаётся массивом, а
`message` содержит короткий текст первой ошибки.

- `401` — неверные credentials/token, истёкший OTP или неподходящий JWT-контур;
- `403` — роль или отключённый для сотрудника раздел не разрешены;
- `404` — ресурс не найден или не принадлежит текущему tenant/client;
- `409` — конфликт уникальности (email, телефон, VIN, SKU и т. п.);
- `413` — тело запроса больше `MAX_REQUEST_BODY_BYTES`;
- `422` — ошибка схемы или бизнес-правила;
- `429` — rate limit регистрации, staff-логина или OTP-запроса.

Ошибка валидации FastAPI:

```json
{
  "detail": [
    { "loc": ["body", "field"], "msg": "Field required", "type": "missing" }
  ]
}
```

## Системный endpoint

| Метод и путь | Auth | Назначение | Вход | Успешный ответ |
|---|---|---|---|---|
| `GET /health` | public | Проверка процесса API | — | `200 {"status":"ok","service":"KOMIT CRM API"}` |

## Организация и staff-аутентификация

| Метод и путь | Auth | Назначение | Вход | Успешный ответ |
|---|---|---|---|---|
| `POST /api/v1/organizations/register` | public, rate limited | Создать автосервис и первого ADMIN | body `OrganizationRegister` | `201 TokenPair` |
| `GET /api/v1/organizations/me` | staff:admin | Профиль своей организации | — | `200 OrganizationRead` |
| `PATCH /api/v1/organizations/me` | staff:admin | Изменить профиль | body `OrganizationUpdate` | `200 OrganizationRead` |
| `POST /api/v1/auth/login` | public, rate limited | Вход по телефону/email/логину | form `username/password` либо JSON `{email,password,remember?}` | `200 StaffSession` |
| `POST /api/v1/auth/register` | public | Совместимая регистрация из готовой admin-панели | body `AdminFrontendRegister` | `201 StaffSession` |
| `POST /api/v1/auth/logout` | staff:any | Отозвать текущую refresh-сессию и удалить cookie | — | `200 {"success":true}` |
| `POST /api/v1/auth/refresh` | public | Ротировать refresh и обновить access | optional body `RefreshRequest`; обычно HttpOnly cookie | `200 AccessToken` |
| `DELETE /api/v1/auth/sessions/{session_id}` | staff:any | Отозвать выбранную свою сессию | path | `204` |
| `DELETE /api/v1/auth/sessions` | staff:any | Отозвать все свои сессии, кроме текущей | — | `204` |
| `GET /api/v1/auth/me` | staff:any | Текущий сотрудник | — | `200 UserRead` |
| `POST /api/v1/auth/subscription` | staff owner | Выбрать тариф организации после регистрации | body `{"plan":"standard"\|"pro"\|"premium"}` | `200 {"user":UserRead}` |
| `GET /api/v1/tariffs` | public | Каталог тарифов для admin-панели | — | `200 Tariff[]` |

Регистрация возвращает токены сразу. Duplicate INN/email/телефон даёт `409`.
`auth/login` сохраняет OAuth form-совместимость и дополнительно принимает JSON
готовой admin-панели. `StaffSession` содержит стандартные `access_token`,
`refresh_token`, `token_type` и совместимые поля `token` (тот же access token),
`user`. Refresh token также устанавливается в `HttpOnly` cookie; JSON-поле
сохранено для обратной совместимости и Swagger. В browser-интеграции запросы
делаются с credentials, access token хранится только в памяти, а refresh token
не читается JavaScript и не кладётся в local/session storage. `remember=true`
увеличивает срок refresh-сессии. Каждый refresh ротирует токен, поэтому
повторное использование старого токена даёт `401`.
`UserRead` в auth-ответах содержит совместимые поля `isOwner`,
`subscriptionPlan` и `access`; меню frontend и backend-проверка разделов
используют одну и ту же матрицу. Менять тариф может только владелец, для
обычного сотрудника endpoint возвращает `403`.

## Реферальная ссылка организации

| Метод и путь | Auth | Назначение | Вход | Успешный ответ |
|---|---|---|---|---|
| `GET /api/v1/referrals/me` | staff:admin+manager, grant `qr` | Получить ранее созданную ссылку | — | `200 ReferralRead`; `404`, если ещё нет |
| `POST /api/v1/referrals/me` | staff:admin+manager, grant `qr` | Создать или идемпотентно получить ссылку | без body | `201 ReferralRead` при создании, `200` повторно |
| `GET /api/v1/referrals/me/qr.svg` | staff:admin+manager, grant `qr` | Получить тот же QR отдельным SVG-файлом | — | `200 image/svg+xml`; `404`, если ещё нет |

`ReferralRead = {code, url, qr_svg}`. URL и QR не содержат внутренних ID или
секретов. Полный frontend-сценарий: [referral-api.md](referral-api.md).

## Сотрудники

Все endpoint’ы — `staff:admin`.

| Метод и путь | Назначение | Вход | Успешный ответ |
|---|---|---|---|
| `GET /api/v1/users` | Список | query `limit`, `offset` | `200 Page<UserRead>` |
| `POST /api/v1/users` | Создать сотрудника | body `UserCreate` | `201 UserRead` |
| `GET /api/v1/users/{user_id}` | Получить | path `user_id:int` | `200 UserRead` |
| `PATCH /api/v1/users/{user_id}` | Изменить | path + body `UserUpdate` | `200 UserRead` |
| `DELETE /api/v1/users/{user_id}` | Удалить | path | `204` |

Повторный email даёт `409`.

## CRM-клиенты

Все endpoint’ы — `staff:admin+manager`.

| Метод и путь | Назначение | Вход | Успешный ответ |
|---|---|---|---|
| `GET /api/v1/clients` | Список/поиск | `query?` (имя/телефон/авто), `client_type?`, pagination | `200 Page<ClientListItem>` |
| `POST /api/v1/clients` | Создать карточку | body `ClientCreate` | `201 ClientRead` |
| `GET /api/v1/clients/{client_id}` | Карточка + статистика + авто | path | `200 ClientDetail` |
| `PATCH /api/v1/clients/{client_id}` | Изменить | path + body `ClientUpdate` | `200 ClientRead` |
| `DELETE /api/v1/clients/{client_id}` | Удалить | path | `204` |

Телефон уникален внутри организации; конфликт при create/update — `409`.

## Автомобили

Все endpoint’ы — `staff:admin+manager`.

| Метод и путь | Назначение | Вход | Успешный ответ |
|---|---|---|---|
| `GET /api/v1/vehicles` | Список | `client_id?`, pagination | `200 Page<VehicleRead>` |
| `POST /api/v1/vehicles` | Добавить клиенту | body `VehicleCreate` | `201 VehicleRead` |
| `GET /api/v1/vehicles/{vehicle_id}` | Получить | path | `200 VehicleRead` |
| `PATCH /api/v1/vehicles/{vehicle_id}` | Изменить | path + body `VehicleUpdate` | `200 VehicleRead` |
| `DELETE /api/v1/vehicles/{vehicle_id}` | Удалить | path | `204` |

`client_id` должен принадлежать текущей организации. VIN уникален внутри
организации; нарушения дают `404`/`409`.

## CRM-проекция готовой admin-панели

Чтение и изменение доступны любой должности с grant `crm`. Поля ответа
используют camelCase и готовы для текущих компонентов канбана. Специальные
selector endpoint'ы не требуют дополнительных grant `services` или `tasks`.

| Метод и путь | Назначение | Вход | Успешный ответ |
|---|---|---|---|
| `GET /api/v1/crm/clients` | Компактный список клиентов | — | `200 CrmClientBrief[]` |
| `GET /api/v1/crm/columns` | Канбан с восемью колонками и карточками | — | `200 CrmColumn[]` |
| `GET /api/v1/crm/deals` | Плоский список сделок | — | `200 CrmOrderRead[]` |
| `GET /api/v1/crm/services` | Услуги для формы CRM | — | `200 AdminServiceRead[]` |
| `GET /api/v1/crm/employees` | Сотрудники для формы CRM | — | `200 TaskEmployee[]` |
| `POST /api/v1/crm/orders` | Создать заказ; клиент и авто создаются только при наличии их данных | body `CrmOrderWrite` (включая `{}`) | `201 CrmOrderRead` |
| `GET /api/v1/crm/orders/{order_id}` | Карточка заказа | path | `200 CrmOrderRead` |
| `PUT /api/v1/crm/orders/{order_id}` | Полностью сохранить форму заказа | path + body `CrmOrderWrite` | `200 CrmOrderRead` |
| `PATCH /api/v1/crm/orders/{order_id}/status` | Переместить между колонками | body `{status}` | `200 CrmOrderRead` |
| `DELETE /api/v1/crm/orders/{order_id}` | Удалить заказ | path | `204` |
| `DELETE /api/v1/crm/orders/bulk` | Удалить выбранные | body `{ids:int[]}` | `204` |

`CrmOrderWrite` соответствует форме frontend: `status`, `clientName`, `phone`,
`email?`, `description`, `date`, `time`, `source`, `plate`, `brand`, `model`,
`year?`, `color`, `vin`, `mileage?`, `lines[]`. Строка: `serviceId`, `price`,
`discount` (0..100), `masterId?` — unified staff/User ID из
`GET /services/masters`. Скидка сохраняется и участвует в `amount`.
Вычисляемые frontend-поля `id`, `number`, `amount`, `services`, `master` и
`masters` при записи безопасно игнорируются; остальные неизвестные поля дают
ошибку валидации.

Все поля формы необязательны. Пустое тело `{}` создаёт заказ в статусе `new`
без клиента, автомобиля, услуг, мастера и календарной брони. Пустые значения в
ответе представлены как `""`, `null` или `[]` в соответствии с типом поля.
Частичные сведения (например, только телефон или только марка) можно сохранить
позже через `PUT`; backend создаёт соответствующую карточку только когда в её
группе появляется хотя бы одно значение.

`date`/`time` принимаются для совместимости формы, но не создают бронь. В
ответе они заполняются только после явного `POST /orders/{id}/reservation`.
Все восемь статусов CRM-доски допускают переход в любую другую колонку, в том
числе обратный переход из `done`; ограничение workflow и требование документа
относятся только к доменному `PATCH /orders/{id}/status`. Технические статусы
`agreement` и `cancelled` не принимаются CRM endpoint'ом.

## Каталог услуг

| Метод и путь | Auth | Назначение | Вход | Успешный ответ |
|---|---|---|---|---|
| `GET /api/v1/services` | staff:any | Список | `query?`, `category?`, `active_only=false`, pagination | `200 Page<ServiceRead>` |
| `POST /api/v1/services` | staff:admin+manager | Создать | body `ServiceCreate` | `201 ServiceRead` |
| `GET /api/v1/services/summary` | staff:any | Показатели каталога и заказов | — | `200 ServiceSummary` |
| `GET /api/v1/services/masters` | staff:any, grant `services` | Только мастера для select | — | `200 ServiceMasterBrief[]` |
| `GET /api/v1/services/admin` | staff:any | Плоский список для готового экрана | — | `200 AdminServiceRead[]` |
| `POST /api/v1/services/admin` | staff:admin+manager | Создать из UI-формы | body `AdminServiceWrite` | `201 AdminServiceRead` |
| `GET /api/v1/services/admin/{service_id}` | staff:any | UI-карточка | path | `200 AdminServiceRead` |
| `PUT /api/v1/services/admin/{service_id}` | staff:admin+manager | Полностью обновить UI-карточку | path + body | `200 AdminServiceRead` |
| `DELETE /api/v1/services/admin/{service_id}` | staff:admin+manager | Удалить | path | `204` |
| `DELETE /api/v1/services/admin/bulk` | staff:admin+manager | Массово удалить | body `{ids:int[]}` | `204` |
| `GET /api/v1/services/import/template` | staff:admin+manager | Скачать XLSX-шаблон | — | `200 XLSX` |
| `POST /api/v1/services/import/preview` | staff:admin+manager | Проверить XLSX без записи | multipart `file` | `200 ServiceImportReport` |
| `POST /api/v1/services/import` | staff:admin+manager | Атомарно импортировать XLSX | multipart `file` | `200 ServiceImportReport`; `422` при ошибках |
| `GET /api/v1/services/{service_id}` | staff:any | Получить | path | `200 ServiceRead` |
| `PATCH /api/v1/services/{service_id}` | staff:admin+manager | Изменить | path + body `ServiceUpdate` | `200 ServiceRead` |
| `DELETE /api/v1/services/{service_id}` | staff:admin+manager | Удалить | path | `204` |

## Мастера

| Метод и путь | Auth | Назначение | Вход | Успешный ответ |
|---|---|---|---|---|
| `GET /api/v1/mechanics` | staff:admin+manager | Список | pagination | `200 Page<MechanicRead>` |
| `POST /api/v1/mechanics` | staff:admin | Создать | body `MechanicCreate` | `201 MechanicRead` |
| `GET /api/v1/mechanics/{mechanic_id}` | staff:admin+manager | Получить | path | `200 MechanicRead` |
| `PATCH /api/v1/mechanics/{mechanic_id}` | staff:admin | Изменить | path + body `MechanicUpdate` | `200 MechanicRead` |
| `DELETE /api/v1/mechanics/{mechanic_id}` | staff:admin | Удалить | path | `204` |

Опциональный `user_id` связывает профиль мастера с staff-пользователем.
Несуществующий пользователь даёт `404`, уже занятая связь — `409`.

### Единая карточка сотрудника

| Метод и путь | Auth | Назначение | Вход | Успешный ответ |
|---|---|---|---|---|
| `GET /api/v1/employees` | staff:admin | Все сотрудники с объединёнными данными User/Mechanic | — | `200 EmployeeRead[]` |
| `POST /api/v1/employees` | staff:admin | Атомарно создать учётную запись и профиль мастера при роли `mechanic` | body `EmployeeCreate` | `201 EmployeeRead` |
| `GET /api/v1/employees/{user_id}` | staff:admin | Получить единую карточку | path | `200 EmployeeRead` |
| `PATCH /api/v1/employees/{user_id}` | staff:admin | Обновить учётку и профиль мастера | path + body `EmployeeUpdate` | `200 EmployeeRead` |
| `DELETE /api/v1/employees/{user_id}` | staff:admin | Безопасно деактивировать сотрудника | path | `204` |
| `GET /api/v1/employees/{user_id}/documents` | staff:admin | Метаданные настоящих кадровых файлов | path | `200 EmployeeDocumentRead[]` |
| `POST /api/v1/employees/{user_id}/documents/{kind}` | staff:admin | Загрузить/заменить `passport`, `inn` или `medicalBook` | multipart `file`, PDF/JPEG/PNG до 2 MiB | `200 EmployeeDocumentRead` |
| `GET /api/v1/employees/{user_id}/documents/{document_id}/content` | staff:admin | Скачать закрытый кадровый файл | paths | `200 binary` |
| `DELETE /api/v1/employees/{user_id}/documents/{document_id}` | staff:admin | Удалить файл | paths | `204` |

`EmployeeRead` содержит `mechanic_id?`, учётные данные без пароля, роль,
`calendar_color`, `duties?`, `ui_permissions`, `documents`, специализации, год найма,
ставку, комиссию, рейтинг и признак настроенного графика. Удаление является
деактивацией; собственную учётную запись администратор отключить не может.

## Задачи сотрудников

Чтение — `staff:any`, механик видит назначенные ему и общие задачи. Создание,
полное редактирование и удаление — `staff:admin+manager`; сменить статус может
доступный задаче сотрудник.

| Метод и путь | Назначение | Вход | Успешный ответ |
|---|---|---|---|
| `GET /api/v1/tasks` | Список для таблицы | — | `200 TaskRead[]` |
| `GET /api/v1/tasks/summary` | Карточки «сегодня/просрочено/неделя» | — | `200 TaskSummary` |
| `GET /api/v1/tasks/employees` | Сотрудники для select и CRM-линий | — | `200 TaskEmployee[]` |
| `POST /api/v1/tasks` | Создать задачу | body `TaskCreate` | `201 TaskRead` |
| `PUT /api/v1/tasks/{task_id}` | Обновить | path + body `TaskUpdate` | `200 TaskRead` |
| `PATCH /api/v1/tasks/{task_id}/status` | Сменить статус | body `{status}` | `200 TaskRead` |
| `DELETE /api/v1/tasks/{task_id}` | Удалить | path | `204` |
| `DELETE /api/v1/tasks/bulk` | Удалить выбранные | body `{ids:int[]}` | `204` |

`TaskCreate`: `title`, `description`, `deadline:date?`,
`status:new|hot|burned|done`, `employee:{id,name,role}`. `employee.id="all"`
создаёт общую задачу. `TaskSummary = {today:{count,overdue}, planned,
donePerWeek}`.

## Настройки admin-панели

Все endpoint’ы — только владелец организации (`isOwner=true`).

| Метод и путь | Назначение | Вход | Успешный ответ |
|---|---|---|---|
| `GET /api/v1/settings` | Профиль сервиса, подписка и безопасная security-проекция | — | `200 SettingsRead` |
| `PUT /api/v1/settings` | Изменить ровно один раздел | body `SettingsUpdate` | `200 SettingsRead` |

Профиль отправляется как `{service:{name,headName,legalType,taxSystem,inn,
ogrn,phone,email,address,logo,description}}`. Для смены пароля текущий frontend
отправляет `{security:{currentPassword:<новый>,oldPassword,code?}}`; backend
проверяет старый пароль, никогда не возвращает пароль или хэш, а
`security.currentPassword` в GET всегда пуст. Действие
`{action:"sendPasswordCode",email}` пока только совместимо по контракту:
почтовый провайдер не подключён, поэтому фактором остаётся старый пароль.
`security.sessions` и `security.loginHistory` заполняются реальными серверными
refresh-сессиями и событиями входа. Для кнопок отзыва используйте
`DELETE /auth/sessions/{session_id}` и `DELETE /auth/sessions`.

## Заказ-наряды

| Метод и путь | Auth | Назначение | Вход | Успешный ответ |
|---|---|---|---|---|
| `GET /api/v1/orders` | staff:any | Список/поиск | `status?`, `source?`, `mechanic_id?`, `query?` (номер/клиент/авто), pagination | `200 Page<OrderRead>` |
| `POST /api/v1/orders` | staff:admin+manager | Создать | body `OrderCreate` | `201 OrderRead` |
| `POST /api/v1/orders/intake` | staff:admin+manager | Атомарно создать CRM-заказ с новым/существующим клиентом и автомобилем, без назначения времени | body `OrderIntakeCreate` | `201 OrderRead` |
| `GET /api/v1/orders/{order_id}` | staff:any | Получить с позициями | path | `200 OrderRead` |
| `PATCH /api/v1/orders/{order_id}` | staff:admin+manager | Изменить основные поля | path + body `OrderUpdate` | `200 OrderRead` |
| `DELETE /api/v1/orders/{order_id}` | staff:admin+manager | Удалить | path | `204` |
| `PATCH /api/v1/orders/{order_id}/status` | staff:any | Сменить статус | body `OrderStatusUpdate` | `200 OrderRead` |
| `GET /api/v1/orders/{order_id}/document` | staff:any | Метаданные оформленного заказ-наряда | path | `200 OrderDocumentRead` |
| `GET /api/v1/orders/{order_id}/document/content` | staff:any | Скачать PDF/HTML как attachment | path | `200 binary` |
| `POST /api/v1/orders/{order_id}/document/generate` | staff:admin+manager | Сгенерировать печатный HTML | path, без body | `201 OrderDocumentRead` |
| `POST /api/v1/orders/{order_id}/document/upload` | staff:admin+manager | Загрузить готовый PDF/HTML | multipart `file` (до 2 MiB) | `201 OrderDocumentRead` |
| `GET /api/v1/orders/{order_id}/documents` | staff:any | Все документы заказа | path | `200 OrderDocumentRead[]` |
| `GET /api/v1/orders/{order_id}/documents/{document_id}/content` | staff:any | Скачать выбранный документ | paths | `200 binary` |
| `GET /api/v1/orders/{order_id}/documents/archive` | staff:any | Скачать все документы ZIP-пакетом | path | `200 application/zip` |
| `POST /api/v1/orders/{order_id}/documents/generate` | staff:admin+manager | Добавить сгенерированный документ | path | `201 OrderDocumentRead[]` |
| `POST /api/v1/orders/{order_id}/documents/upload` | staff:admin+manager | Атомарно загрузить до 10 документов | multipart `files[]` | `201 OrderDocumentRead[]` |
| `DELETE /api/v1/orders/{order_id}/documents/{document_id}` | staff:admin+manager | Удалить выбранный документ открытого заказа | paths | `204` |
| `POST /api/v1/orders/{order_id}/items` | staff:any | Добавить услугу/запчасть | body `OrderItemCreate` | `201 OrderRead` |
| `DELETE /api/v1/orders/{order_id}/items/{item_id}` | staff:any | Удалить позицию | paths | `200 OrderRead` |
| `POST /api/v1/orders/{order_id}/reservation` | staff:admin+manager | Явно зарезервировать выбранное время | body `OrderReservationCreate` | `201 SlotRead` |
| `DELETE /api/v1/orders/{order_id}/reservation` | staff:admin+manager | Снять календарную бронь и назначение | path | `204` |

Для роли `mechanic` список принудительно фильтруется по связанному профилю
мастера; переданный `mechanic_id` игнорируется. Получение конкретного заказа
и его документа разрешено механику только для назначенного ему заказа.

При создании `vehicle_id` должен принадлежать `client_id`. Для позиции
`item_type=service` обязателен `service_id`, для `part` —
`inventory_item_id`. Состав нельзя менять у `done`/`cancelled`.
Staff create/PATCH не принимают календарное назначение через legacy-поля
`mechanic_id`/`scheduled_at`: создайте черновик, затем вызовите explicit
`/reservation`.

`POST /orders/intake` принимает ровно одно из `client_id`/`client` и ровно одно
из `vehicle_id`/`vehicle`. При передаче нового клиента существующая карточка с
тем же телефоном переиспользуется; автомобиль с тем же VIN также переиспользуется
только если принадлежит этому клиенту. Вся операция выполняется в одной
транзакции. Endpoint не выбирает время автоматически и не назначает мастера.

Перевод в `done` разрешён после оформления хотя бы одного документа. Plural
endpoint’ы добавляют документы; legacy `/document...` endpoint’ы сохранены и
работают с последним документом. После `done` или `cancelled` добавление,
замена и удаление запрещены. Загружаются PDF (`application/pdf`, сигнатура
`%PDF-`) либо UTF-8 HTML без `<script>`. Подробный UI-flow:
`docs/order-document-frontend-contract.md`.

Переходы статусов (CRM-этапы добавлены без удаления legacy `agreement`):

- `new` → `primary`, `diagnostics`, `approval`, `secondary`, `waiting`,
  `in_progress`, `cancelled`;
- `primary` → `diagnostics`, `approval`, `waiting`, `in_progress`, `cancelled`;
- `diagnostics` → `approval`, `secondary`, `waiting`, `in_progress`, `cancelled`;
- `approval` → `secondary`, `waiting`, `in_progress`, `done`, `cancelled`;
- `secondary` → `waiting`, `in_progress`, `cancelled`;
- `waiting` → `in_progress`, `cancelled`;
- `in_progress` → `waiting`, `agreement`, `done`, `cancelled`;
- `agreement` → `done`, `cancelled`;
- `done` и `cancelled` — конечные.

Нарушение правила — `422`.

## Расписание

Чтение календаря, предложений и месячной таблицы — `staff:any` с grant
`schedule`. Изменение графика/слотов/блоков, подробные карточки и управление
сотрудниками доступны только владельцу и должности `senior_admin`.

| Метод и путь | Назначение | Вход | Успешный ответ |
|---|---|---|---|
| `GET /api/v1/schedule/week` | Неделя Пн–Вс | required query `day:date`, `mechanic_id?` | `200 WeekView` |
| `GET /api/v1/schedule/calendar` | Готовая недельная проекция для таблицы админки | required query `weekStart:date` | `200 CalendarView` |
| `GET /api/v1/schedule/employees` | Месячная таблица сотрудников | `year`, `month` (0=январь) | `200 StaffMonthRow[]` |
| `GET /api/v1/schedule/employees/{user_id}` | UI-карточка сотрудника без пароля | path | `200 StaffDetail` |
| `POST /api/v1/schedule/employees` | Создать из UI-формы | body `StaffWrite` | `201 StaffDetail` |
| `PUT /api/v1/schedule/employees/{user_id}` | Обновить UI-карточку | path + body `StaffWrite` | `200 StaffDetail` |
| `DELETE /api/v1/schedule/employees/{user_id}` | Деактивировать | path | `204` |
| `PUT /api/v1/schedule/settings` | Задать рабочие дни/время/перерывы сотруднику или всем сотрудникам | body `StaffScheduleSettings` | `204` |
| `GET /api/v1/schedule/availability` | Предложить свободные интервалы без резервирования | `date_from`, `date_to`, optional `mechanic_id`, `service_id`, `duration_minutes` | `200 AvailabilitySuggestions` |
| `GET /api/v1/schedule/mechanics/{mechanic_id}/working-hours` | Рабочий график мастера | path | `200 WorkingHoursRead` |
| `PUT /api/v1/schedule/mechanics/{mechanic_id}/working-hours` | Полностью заменить график | path + body `WorkingHoursReplace` | `200 WorkingHoursRead` |
| `POST /api/v1/schedule/slots` | Создать запись | body `SlotCreate` | `201 SlotRead` |
| `PATCH /api/v1/schedule/slots/{slot_id}` | Изменить запись | path + body `SlotUpdate` | `200 SlotRead` |
| `DELETE /api/v1/schedule/slots/{slot_id}` | Удалить запись | path | `204` |
| `POST /api/v1/schedule/blocks` | Заблокировать время мастера | body `BlockCreate` | `201 BlockRead` |
| `DELETE /api/v1/schedule/blocks/{block_id}` | Удалить блок | path | `204` |

`end_time` должен быть позже `start_time`. Пересечение записей или блокировка
мастера дают `422`.

`StaffScheduleSettings` принимает текущие frontend-поля: `type="workdays"`,
`start`, `end`, `breaks:[{start,end}]`, `workDays` в JS-формате
(`0`=Вс, `1`=Пн … `6`=Сб), `employeeId:int|"all"`. Повторяющиеся перерывы
сохраняются у мастера, исключаются из availability и запрещены при
резервировании. Датированные отпуска/болезни по-прежнему задаются через blocks.

## Склад

| Метод и путь | Auth | Назначение | Вход | Успешный ответ |
|---|---|---|---|---|
| `GET /api/v1/inventory` | staff:any | Список | `query?`, `category?`, `low_stock=false`, pagination | `200 Page<InventoryItemRead>` |
| `POST /api/v1/inventory` | staff:admin | Создать позицию | body `InventoryItemCreate` | `201 InventoryItemRead` |
| `GET /api/v1/inventory/{item_id}` | staff:any | Получить | path | `200 InventoryItemRead` |
| `PATCH /api/v1/inventory/{item_id}` | staff:admin | Изменить | path + body `InventoryItemUpdate` | `200 InventoryItemRead` |
| `DELETE /api/v1/inventory/{item_id}` | staff:admin | Удалить | path | `204` |
| `POST /api/v1/inventory/{item_id}/movements` | staff:admin | Приход/расход/возврат/списание | body `MovementCreate` | `200 InventoryItemRead` |
| `GET /api/v1/inventory/{item_id}/movements` | staff:any | История | pagination | `200 Page<MovementRead>` |
| `POST /api/v1/inventory/{item_id}/write-off` | staff:admin+mechanic | Списать под заказ | body `WriteOffRequest` | `200 InventoryItemRead` |

SKU уникален внутри организации. `order_id`, если передан, должен принадлежать
tenant. Уход остатка ниже нуля отклоняется с `422`.

## Клиентская авторизация

| Метод и путь | Auth | Назначение | Вход | Успешный ответ |
|---|---|---|---|---|
| `POST /api/v1/client-auth/otp/request` | public, rate limited | Запросить OTP | body `OtpRequest` | `200 OtpRequestResponse` |
| `POST /api/v1/client-auth/otp/verify` | public | Проверить OTP/первичный вход | body `OtpVerify` | `200 TokenPair` |
| `POST /api/v1/client-auth/refresh` | public | Обновить client access token | HttpOnly cookie или body `RefreshRequest` | `200 AccessToken` |
| `POST /api/v1/client-auth/logout` | client | Завершить refresh-сессию | — | `200 {success:true}` |
| `GET /api/v1/client-auth/me` | client | Текущий глобальный аккаунт | — | `200 ClientAccountRead` |
| `PATCH /api/v1/client-auth/me` | client | Сохранить ФИО клиента и синхронизировать связанные CRM-карточки | body `{ "full_name": "Иван Петров" }` | `200 ClientAccountRead` |
| `POST /api/v1/client-auth/link-token` | client | Legacy-токен привязки (старые клиенты) | без body | `200 LinkTokenRead` |

Сценарий: `otp/request` → получить звонок и запомнить последние четыре цифры
входящего номера →
`otp/verify` → хранить access token в памяти; refresh token устанавливается в
отдельную HttpOnly cookie. Для legacy-клиентов он также остаётся в JSON. В debug-окружении
`OtpRequestResponse.debug_code` содержит код только при `OTP_PROVIDER=local`.
При `OTP_PROVIDER=sms_ru_call` поле всегда `null`, включая debug-окружение.
Настройка описана в [`docs/phone-call-auth.md`](phone-call-auth.md).

`referral_code` в `OtpVerify` необязателен. Он применяется только если у
аккаунта ещё нет источника; повторный код источник не меняет. Неизвестный код
для неатрибутированного клиента — `422`.

## Шлюз Telegram, VK и MAX

Публичные webhook'и предназначены только для соответствующих платформ и
проверяют отдельный webhook secret. Обычный frontend вызывает их не напрямую,
а открывает одноразовые `bots[].href` из `/client-portal/ui/cars`.

| Метод и путь | Auth | Назначение | Вход | Успешный ответ |
|---|---|---|---|---|
| `POST /api/v1/bot-gateway/telegram/webhook` | Telegram secret header | Принять `/start <token>` и привязать диалог | Telegram Update JSON | `200 {"ok":true}` |
| `POST /api/v1/bot-gateway/vk/webhook` | VK secret в JSON | Confirmation/`message_new`, привязать диалог | VK Callback JSON | `200 confirmation-code` или `ok` |
| `POST /api/v1/bot-gateway/max/webhook` | MAX secret header | Принять `bot_started` с payload | MAX Update JSON | `200 {"ok":true}` |

Полный flow, таблица клиентских статусов и production-настройка приведены в
[`docs/messenger-bots.md`](messenger-bots.md).

## Клиентский портал

Все endpoint’ы требуют client access token.

| Метод и путь | Назначение | Вход | Успешный ответ |
|---|---|---|---|
| `GET /api/v1/client-portal/organizations` | Активные автосервисы | — | `200 OrganizationPublic[]` |
| `GET /api/v1/client-portal/organizations/{organization_id}/services` | Активные услуги | path | `200 ServicePublic[]` |
| `GET /api/v1/client-portal/organizations/{organization_id}/mechanics` | Активные мастера | path | `200 MechanicPublic[]` |
| `GET /api/v1/client-portal/organizations/{organization_id}/availability` | Свободные/занятые интервалы на дату | required `date`, optional `mechanic_id` | `200 AvailabilityRead` |
| `POST /api/v1/client-portal/bookings` | Создать заказ/запись | body `BookingCreate` | `201 BookingRead` |
| `GET /api/v1/client-portal/me/vehicles` | Мои авто во всех сервисах | — | `200 MyVehicleRead[]` |
| `GET /api/v1/client-portal/me/orders` | Мои заказы | pagination | `200 Page<MyOrderRead>` |
| `GET /api/v1/client-portal/me/orders/{order_id}/invoice` | Мой счёт | path | `200 InvoiceRead` |
| `GET /api/v1/client-portal/ui/services` | Карточки существующего client UI | `query?` | `200 ServiceDirectoryRead` |
| `GET /api/v1/client-portal/ui/booking/options` | Услуги/авто/мастера | `shopId` | `200 BookingOptionsRead` |
| `GET /api/v1/client-portal/ui/booking/availability` | Свободные слоты месяца | `shopId,year,month,serviceId,masterId` | `200 BookingAvailabilityUiRead` |
| `POST /api/v1/client-portal/ui/booking` | Подтвердить и атомарно зарезервировать | body `FrontendBookingCreate` | `201 BookingRead` |
| `GET /api/v1/client-portal/ui/cars` | «Моё авто» + одноразовые ссылки Telegram/VK/MAX | — | `200 ClientCarsRead` |
| `GET /api/v1/client-portal/ui/history` | Готовая проекция истории | — | `200 ClientHistoryRead` |
| `GET /api/v1/client-portal/ui/history/{order_id}/document` | Собственный заказ-наряд | path | raw document / `404` |

Рекомендуемый booking flow:

1. Получить организации.
2. Параллельно загрузить услуги и мастеров выбранной организации.
3. Запросить availability с датой/мастером.
4. Отправить `BookingCreate`. Клиентская CRM-карточка и авто создаются или
   связываются автоматически. Если указан `service_id`, длительность берётся
   из услуги; иначе используется 60 минут. При указанном мастере создаётся slot.
5. Обновить мои заказы/авто.

VIN, уже привязанный к другому клиенту того же сервиса, пересечение расписания
или блокировка мастера дают `422`.

## Схемы request/response

`*` означает обязательное поле. `?` означает nullable. Все read-модели с
`id, created_at, updated_at` используют `id:int` и ISO date-time.

### Авторизация и организация

- `TokenPair`: `access_token*:string`, `refresh_token*:string`,
  `token_type:string="bearer"`.
- `StaffSession`: TokenPair + `token` (копия access token) + `user:UserRead`.
- `AdminFrontendRegister`: UI-поля `name`, `headName`, `legalType`, `inn`,
  `taxSystem`, `phone`, `email`, `contactName`, `address`, `password`,
  `passwordConfirm`, `consent=true`.
- `AccessToken`: `access_token*:string`, `refresh_token?:string`,
  `token?:string` (копия access token), `token_type:string="bearer"`.
- `RefreshRequest`: `refresh_token?:string`; при cookie-flow тело можно не
  отправлять.
- `OrganizationRegister`: `name*:string(1..255)`, `inn*:string(10..12)`,
  `tax_system*:TaxSystem`, `legal_form*:LegalForm`, `legal_address*:string`,
  `phone*:string(1..20)`, `admin_full_name*:string(1..255)`,
  `admin_email*:email`, `admin_password*:string(6..72)`.
- `OrganizationUpdate`: optional `name`, `legal_address`, `phone`, `tax_system`.
- `OrganizationRead`: timestamps + `name`, `inn`, `tax_system`, `legal_form`,
  `legal_address`, `phone`, `status`, `subscription_until:date?`, `is_active`.
- `ReferralRead`: `code*:string`, `url*:string`, `qr_svg*:string`.

### Пользователи, клиенты, автомобили

- `UserCreate`: `email*:email`, `full_name*:string`, `phone?:string`,
  `login?:string`, `staff_role_key?:string`, `rate?:decimal`,
  `role:UserRole="manager"`, `password*:string(6..72)`.
- `UserUpdate`: optional `full_name`, `phone`, `login`, `staff_role_key`,
  `rate`, `role`, `is_active`, `password`.
- `UserRead`: timestamps + `email`, `full_name`, `phone?`, `login?`, `role`,
  `staff_role_key`, `roleLabel`, `rate?`, `isOwner:boolean`,
  `subscriptionPlan:"none"|"standard"|"pro"|"premium"`, `is_active`.
- `UserRead` также содержит `calendar_color`, `duties?` и
  `ui_permissions:object` и совместимый alias `access`. Владелец имеет доступ
  ко всем разделам. Пустой legacy-объект обычного сотрудника разрешает доступ согласно роли;
  после явной настройки backend также проверяет флаг соответствующего раздела,
  поэтому скрытия кнопки на frontend недостаточно.
- `ClientCreate`: `full_name*`, `phone*`, optional `email`, `birth_date`,
  `notes`; `client_type="new"`, `marketing_consent=false`,
  `notifications_enabled=true`.
- `ClientUpdate`: optional поля ClientCreate + `is_active`.
- `ClientRead`: timestamps + поля клиента, `balance:decimal`,
  `bonus_points:decimal`, `is_active`.
- `ClientStats`: `visits_count:int`, `total_spent:decimal`,
  `last_visit:date-time?`.
- `ClientListItem`: `ClientRead + stats`.
- `ClientDetail`: `ClientRead + stats + vehicles:VehicleRead[]`.
- `VehicleCreate`: `client_id*:int`, `make*:string`, `model*:string`, optional
  `year`, `license_plate`, `vin`, `color`, `mileage`,
  `next_service_mileage`, `last_service_at`.
- `VehicleUpdate`: все поля VehicleCreate, кроме `client_id`, optional.
- `VehicleRead`: timestamps + все сохранённые поля VehicleCreate.

### Услуги и мастера

- `ServiceCreate`: `name*`, `category*`, optional `description`,
  `internal_notes`, `mechanic_ids:int[]`; `base_price=0`,
  `price_type="fixed"`, `price_to?`, `labor_hours=0`,
  `duration_minutes=60 (>0)`, `is_active=true`. `price_type` принимает
  `fixed`, `range` или `negotiable`; для `range` обязательно
  `price_to >= base_price`. Все мастера из `mechanic_ids` должны принадлежать
  текущей организации.
- `ServiceUpdate`: все поля ServiceCreate optional.
- `ServiceRead`: timestamps + поля услуги и сохранённые `mechanic_ids`.
- `ServiceSummary`: `totalServices:int`, `averageCheck:decimal`,
  `popularService:{name,ordersPerMonth}?`, `revenuePerMonth:decimal`,
  `activeMasters:int`. Популярность и выручка считаются за последние 30 дней;
  отменённые заказы не учитываются.
- `AdminServiceWrite`: `title`, `description`,
  `category:maintenance|diagnostics|repair|body|other`,
  `priceType:fixed|range|negotiable`, `price`, `duration`,
  `durationUnit:minutes|hours`, `status:active|hidden`,
  `masters:(user_id|"all")[]`, `notes`. Текущая UI-форма не имеет отдельной
  верхней границы диапазона, поэтому для `range` доменная `price_to` временно
  равна `price`; точный диапазон доступен через основной Service API.
- `AdminServiceRead`: `id`, UI-поля + `priceNote`, `durationHours`,
  `ordersCount`, `master?`, `masters[]`.
- `ServiceImportReport`: `valid`, `total_rows`, `valid_rows`,
  `imported_rows`, `errors:ServiceImportError[]`, `rows:ServiceImportRow[]`.
  Ошибка содержит `row_number?`, `field`, `message`; строка preview —
  `row_number`, `name`, `base_price`.
- `MechanicCreate`: `full_name*`; optional `phone`,
  `specializations:ServiceCategory[]=[]`, `hired_year`, `user_id`;
  `hourly_rate=0`, `commission_percent=0`.
- `MechanicUpdate`: поля MechanicCreate optional + `is_active`.
- `MechanicRead`: timestamps + поля мастера, `rating:decimal`, `is_active`.

### Заказы и расписание

- `OrderCreate`: `client_id*:int`, `vehicle_id*:int`; optional `mechanic_id`,
  `source` (`call|website|avito|referral|walk_in|other`, default `other`),
  `comment`, `mileage`, `scheduled_at`; `items:OrderItemCreate[]=[]`.
- `OrderIntakeCreate`: ровно одно из `client_id:int` или
  `client:{full_name,phone,email?}`; ровно одно из `vehicle_id:int` или
  `vehicle:{make,model,year?,license_plate?,vin?,color?,mileage?}`; optional
  `source`, `comment`, `mileage`; `items:OrderItemCreate[]=[]`.
- `OrderUpdate`: optional `mechanic_id`, `source`, `comment`, `mileage`, `scheduled_at`,
  `payment_status`.
- `OrderStatusUpdate`: `status*:OrderStatus`.
- `OrderItemCreate`: `item_type:OrderItemType="service"`, optional
  `service_id`, `inventory_item_id`, `mechanic_id`, `description`, `unit_price`,
  `discount_percent` (0..100), `labor_hours`; `quantity=1`.
- `OrderItemRead`: `id`, те же ссылки/описание +
  `quantity`, `unit_price`, `discount_percent`, `labor_hours?`, `total_price`.
- `OrderRead`: timestamps + `number`, `client_id`, `vehicle_id`,
  `mechanic_id?`, `created_by_id?`, `status`, `payment_status`,
  `total_amount`, `mileage?`, `comment?`, `scheduled_at?`, `started_at?`,
  `completed_at?`, `source`, `items:OrderItemRead[]`,
  `document:OrderDocumentRead|null`, а также CRM-проекции `client`, `vehicle`,
  `mechanic|null` с краткими готовыми данными для карточки заказа.
- `OrderDocumentRead`: `id`, `order_id`, `source:"generated"|"uploaded"`,
  `filename`, `content_type`, `size_bytes`, `sha256`, `created_by_id?`,
  `created_at`, `updated_at`. Бинарное содержимое в JSON не возвращается.
- `SlotCreate`: `mechanic_id*`, `start_time*`, `end_time*`; optional
  `order_id`, `work_type`, `title`.
- `SlotUpdate`: все SlotCreate поля optional.
- `SlotRead`: timestamps + поля slot.
- `BlockCreate`: `mechanic_id*`, `start_time*`, `end_time*`, `reason?`.
- `BlockRead`: timestamps + поля block.
- `WeekView`: `week_start`, `week_end`, `slots:SlotRead[]`,
  `blocks:BlockRead[]`.
- `WorkingHoursInterval`: `weekday*:int` (`0`=Пн … `6`=Вс),
  `start_time*:time`, `end_time*:time`.
- `WorkingHoursReplace`: `intervals:WorkingHoursInterval[]` (полная замена;
  пустой список означает отсутствие рабочих дней).
- `WorkingHoursRead`: `mechanic_id`, `timezone`, `uses_default`,
  `intervals:WorkingHoursInterval[]`.
- `AvailabilitySuggestions`: `date_from`, `date_to`, `timezone`,
  `duration_minutes`, `slots:AvailableSlot[]`; slot содержит `mechanic_id`,
  `start_time`, `end_time`, `duration_minutes`.
- `OrderReservationCreate`: `mechanic_id*`, `start_time*:date-time`,
  optional `duration_minutes` (1..1440).

### Склад

- `InventoryItemCreate`: `sku*`, `name*`, `category*`; `unit="шт"`,
  `quantity=0`, `min_quantity=0`, `purchase_price=0`, `sale_price=0`,
  `location?`.
- `InventoryItemUpdate`: optional `name`, `category`, `unit`, `min_quantity`,
  `purchase_price`, `sale_price`, `location`, `is_active`. SKU/quantity
  меняются не этим PATCH.
- `InventoryItemRead`: timestamps + поля позиции, `is_active`,
  `stock_status`.
- `MovementCreate`: `movement_type*`, `quantity*`; optional `order_id`,
  `comment`.
- `MovementRead`: `id`, `inventory_item_id`, `order_id?`, `movement_type`,
  `quantity`, `comment?`, `created_by_id?`, `created_at`.
- `WriteOffRequest`: `quantity*`, optional `order_id`, `comment`.

### Client auth и портал

- `OtpRequest`: `phone*:string`.
- `OtpRequestResponse`: `detail*:string`, `debug_code?:string`.
- `OtpVerify`: `phone*:string`, `code*:string`, `referral_code?:string(8..64)`.
- `ClientAccountRead`: timestamps + `phone`, `full_name?`, `telegram_id?`,
  `vk_id?`, `is_active`.
- `LinkTokenRead`: `link_token*:string`.
- `OrganizationPublic`: `id`, `name`, `phone`, `legal_address`.
- `ServicePublic`: `id`, `name`, `category`, `description?`, `base_price`,
  `duration_minutes`.
- `MechanicPublic`: `id`, `full_name`, `specializations:string[]`, `rating`.
- `AvailabilityRead`: `date`, `slots:SlotPublic[]`, `blocks:BlockPublic[]`;
  public slot/block содержат `id`, `mechanic_id`, `start_time`, `end_time`.
- `VehicleInput`: `make*`, `model*`; optional `year`, `vin`,
  `license_plate`, `mileage`.
- `BookingCreate`: `organization_id*`, `full_name*`, `vehicle:VehicleInput*`,
  `start_time*`; optional `service_id`, `mechanic_id`.
- `BookingRead`: `order_id`, `number`, `organization_id`, `status`,
  `mechanic_id?`, `slot_id?`, `start_time`, `end_time`.
- `MyVehicleRead`: `id`, `organization_id`, `client_id`, данные автомобиля.
- `MyOrderRead`: `id`, `organization_id`, `number`, `status`, `status_label`,
  `payment_status`, `total_amount`, даты исполнения и `created_at`.
- `InvoiceRead`: `order_number`, реквизиты организации и клиента,
  строка `vehicle`, `items:InvoiceItemRead[]`, `total_amount`, `created_at`,
  `completed_at?`. `InvoiceItemRead`: `description`, `quantity`,
  `unit_price`, `total_price`.

## Enum-значения

- `UserRole`: `admin`, `manager`, `mechanic`.
- `TaxSystem`: `usn`, `nds`.
- `LegalForm`: `ip`, `ooo`, `oao`.
- `OrganizationStatus`: `trial`, `active`, `suspended`.
- `ClientType`: `new`, `active`, `vip`.
- `ServiceCategory`: `to`, `chassis`, `diagnostics`, `oil`, `tires`, `ac`,
  `body`, `electrical`, `other`.
- `OrderStatus`: `new`, `primary`, `diagnostics`, `approval`, `secondary`,
  `waiting`, `in_progress`, `agreement` (legacy), `done`, `cancelled`.
- `TaskStatus`: `new`, `hot`, `burned`, `done`.
- `PaymentStatus`: `unpaid`, `partial`, `paid`.
- `OrderItemType`: `service`, `part`.
- `InventoryCategory`: `oils`, `brakes`, `filters`, `ignition`, `fluids`,
  `other`.
- `MovementType`: `in`, `out`, `return`, `write_off`.
- `StockStatus` (только response): `critical`, `low`, `normal`.
