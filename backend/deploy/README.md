# Production-развёртывание DVIJOK

Серверная раскладка:

- `/opt/dvizhok/backend` — исходники API;
- `/opt/dvizhok/deploy` — Compose, закрытый `.env.production` и служебные файлы;
- `/var/www/dvizhok/index.html` и `/var/www/dvizhok/assets` — публичный лендинг;
- `/var/www/dvizhok/admin` — production-сборка админки;
- `/var/www/dvizhok/client` — production-сборка клиентского SPA;
- `/opt/dvizhok/backups/postgres` — резервные копии PostgreSQL.

Запуск выполняется из `/opt/dvizhok/deploy`:

```bash
docker compose --env-file .env.production -f compose.prod.yml up -d --build
```

PostgreSQL и Redis доступны только внутренней Docker-сети. API опубликован только на
`127.0.0.1:8000`; внешний трафик принимает системный Nginx.

Содержимое frontend-каталога `landing` копируется непосредственно в
`/var/www/dvizhok`. Корень сайта `/` показывает лендинг, а его кнопки ведут в
`/client/` и `/admin/`.

Перед HTTPS домен `dvizhok.tech` должен иметь A-запись на IPv4 сервера. После этого:

```bash
certbot --nginx -d dvizhok.tech --redirect --agree-tos -m <email> --no-eff-email
```

Резервная копия создаётся командой `./backup.sh`. Для ежедневного запуска можно
установить `dvizhok-backup.cron` в `/etc/cron.d/dvizhok-backup` с правами `0644`.
Файл `.env.production`, пароли, ключи SMS.ru и ботов не должны попадать в Git.
