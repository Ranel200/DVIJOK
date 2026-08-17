# Интеграция готовой admin-панели с backend

## Что уже готово

Backend предоставляет маршруты для всех разделов admin-панели: вход и
регистрация, расписание и сотрудники, CRM, услуги, задачи, QR и настройки.
Базовый URL локально: `http://localhost:8000/api/v1`.

В frontend нужны runtime-переменные:

```dotenv
VITE_USE_MOCK=false
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Frontend работает на порту `9000`, который уже добавлен в backend CORS.

## Маршруты по экранам

| Экран | Основные вызовы |
|---|---|
| Вход/регистрация | `POST /auth/login`, `POST /auth/register`, `GET /auth/me`, `POST /auth/logout` |
| Тариф после регистрации | `GET /tariffs`, `POST /auth/subscription` |
| Календарь | `GET /schedule/calendar?weekStart=...`, `GET /schedule/availability`, `POST /orders/{id}/reservation` |
| Сотрудники | `GET/POST /schedule/employees`, `GET/PUT/DELETE /schedule/employees/{id}`, `PUT /schedule/settings` |
| CRM | `GET /crm/columns`, `GET /crm/deals`, `GET /crm/services`, `GET /crm/employees`, `POST/GET/PUT/DELETE /crm/orders...` |
| Услуги | `GET/POST /services/admin`, `GET/PUT/DELETE /services/admin/{id}`, `GET /services/summary`, `GET /services/masters` |
| Импорт услуг | `GET /services/import/template`, `POST /services/import/preview`, `POST /services/import` |
| Задачи | `GET/POST /tasks`, `GET /tasks/summary`, `GET /tasks/employees`, status/CRUD/bulk routes |
| QR | `POST /referrals/me`, `GET /referrals/me`, `GET /referrals/me/qr.svg` |
| Настройки | `GET /settings`, `PUT /settings` |
| Документы заказа | список/content/archive/generate/upload/delete под `/orders/{id}/documents...`; legacy singular URL сохранены |
| Кадровые документы | list/upload/download/delete под `/employees/{id}/documents...` |

Подробные тела и ответы: [api-reference.md](api-reference.md).

## Права сотрудников

Auth-ответы содержат `isOwner`, `subscriptionPlan` и объект `access` с ключами
`schedule`, `crm`, `services`, `tasks`, `qr`, `settings`. Frontend скрывает
недоступные разделы и открывает первый разрешённый; backend независимо
возвращает `403` на запрещённый endpoint. Владелец имеет полный доступ.

Матрица действий внутри доступного раздела:

| Раздел | Просмотр | Изменение |
|---|---|---|
| Расписание | Любая должность с grant `schedule` | Только владелец и `senior_admin`, включая сотрудников и графики |
| CRM | Любая должность с grant `crm` | Та же должность: grant открывает полный CRM-контур |
| Услуги | Любая должность с grant `services` | Владелец, `senior_admin`, `junior_admin` |
| Задачи | Любая должность с grant `tasks`; мастер меняет статус | Создание, полное изменение и удаление — владелец и администраторы |
| QR | Владелец или администратор с grant `qr` | Владелец или администратор с grant `qr` |
| Настройки | Только владелец | Только владелец |

Форма сотрудника не выдаёт `settings`; `qr` доступен для назначения только
административным должностям. Backend повторно проверяет эту матрицу, поэтому
прямой вызов скрытого endpoint также вернёт `403`.

Для локальной демонстрации после `python -m scripts.seed_demo_staff` доступны
профили `smirnov`, `sidorov`, `petrov`, `morozova`, `sokolova`; пароль каждого
совпадает с логином. Seed идемпотентен и не запускается автоматически.

## Минимальные изменения frontend, которые ещё нужны

Эти изменения намеренно не внесены без разрешения владельца frontend.

1. В `servicesApi.list()` заменить `/services` на `/services/admin`. Добавить
   create/update/delete/bulk методы и вызывать их из `ServicesPage.vue` вместо
   изменения только локального массива.
2. В `CrmPage.vue` вызывать `PUT /crm/orders/{id}`, status endpoint и delete
   endpoints. Сейчас создание сохраняется, а edit/delete/drag меняют только
   локальное состояние.
3. В `TasksPage.vue` подключить bulk delete; сейчас удаление только локальное.
4. В `QrPage.vue` загрузить `POST /referrals/me`, отобразить `qr_svg`/`url`, а
   печать направить на `/referrals/me/qr.svg`. Сейчас показана статическая
   картинка и обработчик печати — TODO.
5. Подключить кнопки generate/upload/download документа в `OrderModal.vue`.
   Backend уже реализован.
6. Выполнять API-запросы с `credentials: "include"`, держать access token только
   в памяти и при старте приложения вызывать `POST /auth/refresh`: серверная
   HttpOnly cookie восстановит сессию и вернёт новый access token. Refresh token
   нельзя переносить в `localStorage`.
7. В форме смены пароля убрать сравнение старого пароля с
   `security.currentPassword`: backend специально возвращает пустую строку и
   проверяет пароль сервером. Email-код нельзя считать реально отправленным до
   подключения почтового провайдера.
8. Для нового заказа добавить UI выбора из `GET /schedule/availability`, затем
   явный вызов reservation. Нельзя автоматически ставить первый свободный слот.

## Совместимость полей

- Auth login принимает текущий JSON `{email,password}` и старый OAuth form.
  Ответ содержит и стандартный `access_token`, и ожидаемые frontend поля
  `token`, `user`.
- Регистрация `/auth/register` принимает текущие `headName`, `legalType`,
  `taxSystem`, `contactName`, `passwordConfirm`, `consent`.
- Calendar/CRM/tasks/settings ответы используют camelCase там, где его уже
  ожидают компоненты.
- `masterId` в CRM и `masters[]` в admin services — User ID из
  `/services/masters`; backend сам переводит его во внутренний Mechanic ID.
- `employeeId` в `/schedule/settings` — User ID или `"all"`.
- График из `/schedule/settings` хранится для любой должности, а не только для
  мастера; календарная availability использует график связанных мастеров.

## Ограничения текущего UI

- Backend поддерживает `priceTo` для услуги с типом `range`, но текущий UI имеет
  только одно поле цены. Для реального диапазона frontend потребуется второе
  поле; при его отсутствии `priceTo` можно отправлять равным `price`.
- Backend хранит кадровые PDF/JPEG/PNG как закрытые tenant-scoped файлы. Текущий
  UI пока передаёт лишь имена: для реальной загрузки нужно подключить
  `/employees/{id}/documents/{kind}`.
- Refresh-сессии и история входов хранятся сервером; logout отзывает текущую
  сессию. Доступны отзыв выбранной сессии и «выйти на других устройствах».
- Отправка email-кода и 2FA остаются UI-совместимыми заглушками, пока не выбран
  почтовый/SMS-провайдер. Смена пароля защищена проверкой старого пароля.
