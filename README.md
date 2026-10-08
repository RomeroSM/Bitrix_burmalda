# Bitrix Bridge

Webhook-сервис переносит данные чеклиста задачи Bitrix24 в элемент процесса
«Инженерный HelpDesk». `Code.gs` оставлен как пример старой реализации,
рабочая версия находится в `python/`.

## Подготовка сервера

Нужны Docker с Compose, публичный домен и открытые входящие порты `80` и `443`.
A/AAAA-запись домена должна указывать на сервер до получения сертификата.

Создайте настройки:

```bash
cp python/.env.example python/.env
cp .env.example .env
```

В `python/.env` укажите вебхуки Bitrix24. В корневом `.env` укажите домен и
email для Let's Encrypt:

```dotenv
DOMAIN=bitrix.example.com
CERTBOT_EMAIL=admin@example.com
CERTBOT_STAGING=0
CERTBOT_FORCE_RENEWAL=0
```

Оба файла `.env` исключены из Git.

## Первый запуск и HTTPS

```bash
python3 scripts/init_letsencrypt.py
```

Скрипт запускает приложение и Nginx, получает сертификат через HTTP-01 и
включает HTTPS. Проверка:

```bash
curl https://bitrix.example.com/health
docker compose ps
docker compose logs --tail 100
```

В Bitrix24 укажите URL вебхука:

```text
https://bitrix.example.com/
```

Certbot проверяет продление каждые 12 часов. Nginx перечитывает сертификаты
каждые 6 часов. Сертификаты и CSV-лог хранятся в Docker volumes и переживают
пересборку контейнеров; приватные ключи не входят в образ и не попадают в Git.

Для предварительной проверки Let's Encrypt можно выставить
`CERTBOT_STAGING=1`. Чтобы затем заменить тестовый сертификат настоящим,
верните `CERTBOT_STAGING=0`, один раз выставьте `CERTBOT_FORCE_RENEWAL=1` и
повторно запустите установщик. После успешной выдачи верните
`CERTBOT_FORCE_RENEWAL=0`.

## Обновление

```bash
git pull
docker compose up -d --build
```

## Управление

```bash
docker compose logs -f
docker compose restart
docker compose down
```

Команда `docker compose down` сохраняет сертификаты и лог. Не используйте
`docker compose down -v`, если не хотите удалить volumes с этими данными.
