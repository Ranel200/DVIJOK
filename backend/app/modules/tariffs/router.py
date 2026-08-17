"""Публичный неизменяемый каталог тарифов для экрана после регистрации."""

from fastapi import APIRouter

router = APIRouter(prefix="/tariffs", tags=["tariffs"])

_TARIFFS = [
    {
        "id": "standard",
        "name": "СТАНДАРТ",
        "logo": "/admin/icons/tariffs/standard.png",
        "logoNoStar": "/admin/icons/tariffs/standard-no-star.png",
        "logoAlt": "Тариф Стандарт",
        "summary": "Для небольших автомастерских с одним сотрудником.",
        "description": (
            "Идеально подходит частным мастерам и небольшим гаражным сервисам, "
            "которые хотят вести клиентов, записи и ремонты в одной системе."
        ),
        "price": "5 990 ₽",
        "features": [
            {
                "icon": "/admin/icons/tariffs/crm.svg",
                "title": "CRM для клиентов и авто",
                "text": "Удобная аналитика",
            },
            {
                "icon": "/admin/icons/auth/calendar.svg",
                "title": "Календарь записей",
                "text": "Все записи на одном экране",
            },
            {
                "icon": "/admin/icons/auth/docs.svg",
                "title": "Канбан заказов",
                "text": "Все заказы в одном месте",
            },
            {
                "icon": "/admin/icons/tariffs/history.svg",
                "title": "История ремонтов",
                "text": "Общая для автосервиса и для каждого клиента",
            },
            {
                "icon": "/admin/icons/tariffs/manage.svg",
                "title": "Управление услугами",
                "text": "Создание и изменение услуг",
            },
            {
                "icon": "/admin/icons/tariffs/tg.svg",
                "title": "Telegram-бот уведомлений",
                "text": "Удобство коммуникации",
            },
            {
                "icon": "/admin/icons/tariffs/book.svg",
                "title": "Электронная сервисная книжка",
                "text": "Сервисная книжка клиентов",
            },
        ],
    },
    {
        "id": "pro",
        "name": "ПРО",
        "logo": "/admin/icons/tariffs/pro.png",
        "logoNoStar": "/admin/icons/tariffs/pro-no-star.png",
        "logoAlt": "Тариф Про",
        "summary": "Для автомастерских с двумя и больше сотрудниками.",
        "description": (
            "Подходит сервисам, где важно контролировать работу команды, "
            "загруженность мастеров и поток заказов. Включает все из тарифа "
            "«Стандарт», а также ПРО-функции."
        ),
        "price": "6 990 ₽",
        "includedFrom": {
            "icon": "/admin/icons/tariffs/star.svg",
            "title": "Все из тарифа СТАНДАРТ",
        },
        "features": [
            {
                "icon": "/admin/icons/tariffs/groups.svg",
                "title": "Неограниченное число сотрудников",
                "text": "Управление сотрудниками в одном месте",
            },
            {
                "icon": "/admin/icons/auth/calendar.svg",
                "title": "График работы мастеров",
                "text": "Интерактивный календарь с графиком",
            },
            {
                "icon": "/admin/icons/tariffs/control.svg",
                "title": "Контроль загруженности",
                "text": "Управление рабочими часами сотрудников",
            },
            {
                "icon": "/admin/icons/auth/canban.svg",
                "title": "Распределение заказов",
                "text": "Распределение заказов между сотрудниками внутри системы",
            },
            {
                "icon": "/admin/icons/auth/crm.svg",
                "title": "Базовая аналитика",
                "text": "Доступ к базовым аналитическим инструментам",
            },
        ],
    },
    {
        "id": "premium",
        "name": "ПРЕМИУМ",
        "logo": "/admin/icons/tariffs/premium.png",
        "logoNoStar": "/admin/icons/tariffs/premium-no-star.png",
        "logoAlt": "Тариф Премиум",
        "summary": "Для компаний с двумя и более автомастерскими.",
        "description": (
            "Все филиалы работают в единой системе, а руководство контролирует "
            "бизнес из одного кабинета. Включает все из тарифа «ПРО», а также "
            "ПРЕМИУМ-функции."
        ),
        "price": "7 990 ₽",
        "includedFrom": {
            "icon": "/admin/icons/tariffs/star.svg",
            "title": "Все из тарифа ПРО",
        },
        "features": [
            {
                "icon": "/admin/icons/tariffs/manage-2.svg",
                "title": "Управление несколькими автомастерскими",
                "text": "Все филиалы в одном месте",
            },
            {
                "icon": "/admin/icons/tariffs/book.svg",
                "title": "Общая база",
                "text": "Сводная база клиентов и автомобилей",
            },
            {
                "icon": "/admin/icons/tariffs/doc-2.svg",
                "title": "Общая отчетность по сети",
                "text": "Сборные отчеты по работе всего бизнеса",
            },
            {
                "icon": "/admin/icons/tariffs/manage-3.svg",
                "title": "Централизованное управление",
                "text": "Централизованное управление сотрудниками всех филиалов",
            },
            {
                "icon": "/admin/icons/tariffs/analytic.svg",
                "title": "Аналитика по каждому филиалу",
                "text": "Доступ к аналитике работы каждого филиала",
            },
            {
                "icon": "/admin/icons/tariffs/manager.svg",
                "title": "Персональный менеджер",
                "text": "Ваш личный специалист по работе в системе",
            },
        ],
    },
]


@router.get("")
async def list_tariffs() -> list[dict]:
    return _TARIFFS
