# Документы заказ-наряда: frontend-контракт

## Назначение

У одного заказа может быть несколько документов: сгенерированный заказ-наряд
и загруженные PDF/HTML-файлы. Перевести заказ в `done` можно, когда существует
хотя бы один документ. Документы добавляются только явным действием пользователя
и сами по себе не меняют статус заказа.

Все URL ниже имеют префикс `/api/v1`. Авторизация — staff Bearer JWT. Чтение
доступно сотруднику, которому доступен заказ; добавление и удаление — ролям
`admin` и `manager`. После `done` или `cancelled` состав документов неизменяем.

## JSON-модель

```json
{
  "id": 42,
  "order_id": 123,
  "source": "generated",
  "filename": "order-4953.html",
  "content_type": "text/html",
  "size_bytes": 8142,
  "sha256": "64 lowercase hex characters",
  "created_by_id": 7,
  "created_at": "2026-08-06T15:20:00Z",
  "updated_at": "2026-08-06T15:20:00Z"
}
```

Бинарное содержимое не входит в JSON. Для обратной совместимости
`OrderRead.document` содержит последний документ или `null`; полный список
нужно получать отдельным endpoint'ом.

## Основные endpoint'ы

### Получить список

`GET /orders/{order_id}/documents`

Ответ `200`: `OrderDocumentRead[]`. Пустой массив означает, что документов нет.

### Сгенерировать новый документ

`POST /orders/{order_id}/documents/generate`

- тело отсутствует;
- ответ `201`: массив с одним созданным `OrderDocumentRead`;
- создаётся печатный UTF-8 HTML и добавляется к существующим документам.

### Загрузить один или несколько файлов

`POST /orders/{order_id}/documents/upload`

- `Content-Type: multipart/form-data`;
- поле `files` можно повторить от 1 до 10 раз;
- ответ `201`: созданные `OrderDocumentRead[]`;
- каждый файл — не более 2 MiB;
- PDF: `.pdf`, `application/pdf`, сигнатура `%PDF-`;
- HTML: `.html`/`.htm`, `text/html`, UTF-8-разметка без `<script>`;
- пакет атомарный: ошибка любого файла не добавляет ни одного.

```js
const form = new FormData();
for (const file of selectedFiles) form.append("files", file);
const response = await api.post(`/orders/${orderId}/documents/upload`, form);
```

Не задавайте `Content-Type` вручную: браузер добавит multipart boundary.

### Скачать выбранный документ

`GET /orders/{order_id}/documents/{document_id}/content`

Ответ `200` содержит исходные байты и `Content-Type`,
`Content-Disposition: attachment`, а также checksum в `X-Content-SHA256`.

### Скачать всё ZIP-архивом

`GET /orders/{order_id}/documents/archive`

Ответ `200 application/zip`. Если список пуст, backend вернёт `422`.

### Удалить выбранный документ

`DELETE /orders/{order_id}/documents/{document_id}`

Ответ `204`. Удаление запрещено после `done`/`cancelled`.

## Legacy endpoint'ы

Существующие singular URL сохранены: `GET /document`,
`GET /document/content`, `POST /document/generate` и
`POST /document/upload`. Они работают с последним документом и нужны только
для старых клиентов. Новый UI должен использовать plural API, чтобы не скрывать
остальные файлы.

## Завершение заказа

`PATCH /orders/{order_id}/status` с телом:

```json
{"status": "done"}
```

Успешный `200 OrderRead` содержит `status: "done"`, `completed_at` и
ненулевой совместимый `document`. Для отображения всех файлов после ответа
перечитайте `GET /orders/{order_id}/documents`.

## Рекомендуемый UI-flow

1. При открытии карточки загрузить список документов.
2. Generate/upload выполнять только после явного нажатия пользователя.
3. После `201` перечитать список либо добавить возвращённые элементы.
4. При выборе «Готово» убедиться, что список не пуст, затем отдельно отправить
   status PATCH.
5. Для механика без документов показать просьбу обратиться к
   администратору/менеджеру. Для закрытого заказа скрыть изменение файлов.

## Ошибки

Доменные ошибки имеют поля `detail` и `message` с одним текстом.

| HTTP | Когда |
|---|---|
| `401` | нет или истёк staff access token |
| `403` | роль не может добавлять/удалять документ |
| `404` | заказ или выбранный документ отсутствует/недоступен |
| `413` | всё HTTP-тело превысило глобальный лимит |
| `422` | `done` без документа, недопустимый переход, формат/размер файла, пустой архив или изменение закрытого заказа |

При конкурентном изменении перечитайте заказ и список документов, затем
покажите фактическое серверное состояние.
