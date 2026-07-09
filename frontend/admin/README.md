# DVIJOK Admin (dvijok-admin)

Админ-панель платформы автосервисов DVIJOK. Разделы: Вход, Расписание, CRM, Услуги, Настройки.

Стек: Quasar v2 (Vite) + Vue 3 + Pinia. Данные пока на моках (`src/api`), готово к подключению реального бэкенда.

## Установка зависимостей

```bash
pnpm install
```

## Запуск в режиме разработки (HMR)

```bash
quasar dev
```

## Сборка продакшн-версии

```bash
quasar build
```

## Линтинг и форматирование

```bash
pnpm lint
```

## Структура `src`

```text
api/          # слой работы с API (fetch-обёртка + моки)
stores/       # Pinia-сторы (app, auth)
constants/    # константы (навигация)
router/       # маршруты + guard
layouts/      # AuthLayout, AdminLayout
components/    # переиспользуемые компоненты (шапка, сайдбар)
pages/        # страницы разделов (пока пустые скелеты)
css/          # глобальные стили и Sass-переменные
```

## Конфигурация

См. [Configuring quasar.config.js](https://v2.quasar.dev/quasar-cli-vite/quasar-config-file).
