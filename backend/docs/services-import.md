# Импорт услуг из Excel: frontend-интеграция

Все endpoint’ы имеют префикс `/api/v1/services/import` и требуют staff access
token с ролью `admin` или `manager`.

## Формат файла

Поддерживается только `.xlsx`, активный лист книги. Первая строка должна
содержать ровно два столбца:

| Услуга | Стоимость |
|---|---:|
| Замена масла | 2500 |

- порядок столбцов не важен;
- регистр и пробелы вокруг заголовков не важны;
- неизвестные и повторяющиеся заголовки запрещены;
- полностью пустые строки игнорируются;
- название обязательно, до 255 символов;
- стоимость обязательна, строго больше нуля, максимум `99999999.99`, не более
  двух знаков после запятой;
- допустимы Excel number и текст вида `1 500,50`;
- формулы не принимаются: нужно вставить вычисленное значение;
- названия сравниваются без учёта регистра и повторных пробелов;
- дубликаты внутри файла и существующие услуги текущей организации запрещены.

Лимиты по умолчанию: файл до 2 MiB, до 2000 непустых строк.

Импортированные услуги получают безопасные defaults текущей модели:

```json
{
  "category": "other",
  "description": null,
  "labor_hours": 0,
  "duration_minutes": 60,
  "is_active": true
}
```

## 1. Скачать шаблон

```http
GET /api/v1/services/import/template
Authorization: Bearer <staff_access_token>
```

Ответ `200`:

- Content-Type:
  `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`;
- Content-Disposition:
  `attachment; filename="services-import-template.xlsx"`;
- body — XLSX-файл.

Frontend может сохранить ответ как `Blob`. Шаблон содержит правильные
заголовки, числовой денежный формат и одну примерную строку. Перед загрузкой
пользователь должен удалить пример либо заменить его своей услугой.

## 2. Предпросмотр

```http
POST /api/v1/services/import/preview
Authorization: Bearer <staff_access_token>
Content-Type: multipart/form-data
```

Form field: `file` — выбранный XLSX.

Preview всегда read-only и при успешно разобранном HTTP-запросе возвращает
`200`, даже если в книге есть ошибки:

```json
{
  "valid": true,
  "total_rows": 2,
  "valid_rows": 2,
  "imported_rows": 0,
  "errors": [],
  "rows": [
    {
      "row_number": 2,
      "name": "Замена масла",
      "base_price": "2500.00"
    },
    {
      "row_number": 3,
      "name": "Диагностика",
      "base_price": "1500.50"
    }
  ]
}
```

`row_number` — настоящий номер строки Excel, включая строку заголовков.

Пример ошибок:

```json
{
  "valid": false,
  "total_rows": 3,
  "valid_rows": 1,
  "imported_rows": 0,
  "errors": [
    {
      "row_number": 3,
      "field": "Услуга",
      "message": "Дубликат строки 2"
    },
    {
      "row_number": 4,
      "field": "Стоимость",
      "message": "Стоимость должна быть положительным числом"
    }
  ],
  "rows": [
    {
      "row_number": 2,
      "name": "Шиномонтаж",
      "base_price": "3000.00"
    }
  ]
}
```

`rows` в невалидном preview нужны только для интерфейса; импортировать отдельно
эти строки нельзя.

## 3. Атомарно применить

```http
POST /api/v1/services/import
Authorization: Bearer <staff_access_token>
Content-Type: multipart/form-data
```

Frontend повторно отправляет тот же form field `file`. Backend заново проверяет
файл и текущий каталог — результат preview не является разрешением на запись.

При успехе возвращается `200` и тот же отчёт с
`imported_rows == valid_rows`.

Если найдена хотя бы одна ошибка, ответ `422`, `valid=false`,
`imported_rows=0`. Ни одна услуга не создаётся. Частичного режима намеренно нет:
пользователь исправляет весь файл, снова делает preview и повторяет import.

## Tenant isolation и конкурентность

Файл не содержит `organization_id`; backend всегда назначает организацию из
staff JWT. Услуга с тем же названием в другом автосервисе не мешает импорту.

На apply строка текущей организации блокируется в транзакции, поэтому два
параллельных массовых импорта одного tenant последовательно перепроверят
дубликаты. Обычные API-права и tenant scoping остаются в силе.

## Типовые HTTP-ошибки

- `401` — staff token отсутствует или истёк;
- `403` — роль `mechanic`;
- `422` — невалидная книга при apply или отсутствует multipart field `file`;
- `413` middleware — общий лимит HTTP body; oversized XLSX в пределах body
  возвращается как `valid=false` в отчёте preview/apply.

Полный backend-справочник: [api-reference.md](api-reference.md).
