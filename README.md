# Tarot Cards Bot

A Telegram bot that works with the Rider–Waite–Smith tarot deck, paired with a web admin panel where all
user-facing content is written and edited. The bot only reads from the database; every card description,
daily reading and history chapter is authored through the admin.

## Features

- **Telegram bot** on aiogram 3 with long polling
- **Admin panel** built on SQLAdmin — Russian labels, session auth, length validation against Telegram's
  4096-character message limit, and a custom django-unfold–style theme with light and dark modes
- **Content in the database**: 78 cards, per-card daily readings, history of tarot
- **Two independent entry points** — the bot and the admin run as separate processes and share only the
  database layer
- **Alembic migrations** for the schema

## Stack

| Layer | Choice |
|---|---|
| Bot framework | aiogram 3 |
| Admin | SQLAdmin on Starlette, served by uvicorn |
| ORM | SQLAlchemy 2 (async) |
| Migrations | Alembic |
| Database | SQLite in debug, PostgreSQL via asyncpg otherwise |
| Cache | Redis |
| Settings | pydantic-settings |

Requires Python 3.14+.

## Project layout

```
bot/
  admin/          admin panel: auth, base view, filters, wiring
  core/           settings, database, Redis cache, logging
  tarot/          models, admin views, repository, router
  run_bot.py      entry point — Telegram bot
  run_admin.py    entry point — admin panel
migrations/       Alembic
static/           admin assets: logo, css/admin.css theme
templates/        SQLAdmin template overrides
```

## Setup

Install dependencies:

```bash
uv sync
```

Create a `.env` file in the project root:

```dotenv
IS_DEBUG=true
BOT_TOKEN=123456:your-telegram-bot-token

ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-me
ADMIN_SECRET_KEY=generate-a-long-random-string
```

`ADMIN_PASSWORD` and `ADMIN_SECRET_KEY` have no defaults on purpose — the app refuses to start without
them. Generate a secret key with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Apply migrations:

```bash
uv run alembic upgrade head
```

## Running

The bot:

```bash
uv run python -m bot.run_bot
```

The admin panel:

```bash
uv run python -m bot.run_admin
```

The admin is then available at `http://localhost:8080/admin`.

## Configuration

All settings are read from `.env`. Anything with a default can be omitted.

| Variable | Default | Purpose |
|---|---|---|
| `IS_DEBUG` | `true` | Switches database and Redis targets, and the log format |
| `BOT_TOKEN` | — | Telegram bot token |
| `ADMIN_USERNAME` | `admin` | Admin login |
| `ADMIN_PASSWORD` | — | Admin password |
| `ADMIN_SECRET_KEY` | — | Signing key for admin session cookies |
| `ADMIN_HOST` | `0.0.0.0` | Admin bind address |
| `ADMIN_PORT` | `8080` | Admin port |
| `SQLITE_URL` | `sqlite+aiosqlite:///db.sqlite3` | Used when `IS_DEBUG=true` |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | — | Used when `IS_DEBUG=false` |
| `POSTGRES_HOST` | `localhost` | |
| `POSTGRES_PORT` | `5432` | |
| `REDIS_HOST` | `localhost` in debug, `redis` otherwise | |
| `REDIS_PORT` | `6379` | |
| `REDIS_DB` | `0` | |
| `LOG_LEVEL` | `INFO` | Level for the `bot` and `aiogram` loggers |

`IS_DEBUG` does more than toggle verbosity: it selects SQLite over PostgreSQL, `localhost` over the `redis`
service host, human-readable logs over JSON, and disables the `Secure` flag on the admin session cookie.
Set it to `false` in production.

## Content model

- **Card** — name, short description shown in spreads, image path, and a cached Telegram `file_id`
- **DailyCard** — one-to-one with a card, holds the full card-of-the-day post
- **History** — the history of tarot as readable text

Text fields are capped at 4096 characters in the admin forms, matching the longest message Telegram will
accept. Note that Telegram counts UTF-16 code units, so text heavy in emoji is longer than `len()` suggests,
and captions attached to a photo are limited to 1024 rather than 4096.

## Admin theme

The admin keeps SQLAdmin's views and routes but replaces its look with a theme in the spirit of
[django-unfold](https://github.com/unfoldadmin/django-unfold): a light sidebar with sectioned navigation,
breadcrumbs, a dashboard, a redesigned login page, and a light/dark switch. It is built on top of the Tabler
CSS that SQLAdmin already ships, so no extra frontend dependencies are needed.

Templates in `templates/sqladmin/` take precedence over SQLAdmin's own. An override that only tweaks a page
extends the original through the `sqladmin_original/` prefix, e.g. `{% extends "sqladmin_original/edit.html" %}`.

| File | Role |
|---|---|
| `static/css/admin.css` | The theme: design tokens, layout, restyled Tabler components |
| `templates/sqladmin/base.html` | Loads the Inter font and `admin.css`, applies the saved theme before first paint |
| `templates/sqladmin/layout.html` | Page shell: sidebar, topbar with breadcrumbs and language switcher, theme toggle |
| `templates/sqladmin/_menu.html` | Sidebar macros — categories render as headed sections instead of dropdowns |
| `templates/sqladmin/index.html` | Dashboard with a card per admin view |
| `templates/sqladmin/login.html` | Login page |
| `templates/sqladmin/create.html`, `edit.html` | Form submit buttons |
| `templates/sqladmin/filters/operation_filter.html` | Russian operation filter |

Colors are CSS variables at the top of `admin.css`: `:root` holds the light theme, `[data-bs-theme="dark"]`
the dark one. Change the accent with `--ta-primary` / `--ta-primary-rgb`. The chosen theme is stored in the
browser's `localStorage` under `ta-theme`; on first visit it follows the system preference.

The Inter font is loaded from Google Fonts; without internet access the admin falls back to the system font.

List columns with long text use the `_preview()` formatter from `bot/tarot/admin.py`, which shortens the
value on a word boundary and lets it wrap instead of stretching the table. It applies to list pages only —
the detail page shows the full text.

## Logging

Logging is configured in `bot/core/logging.py`: readable single-line output in debug, JSON in production.
Structured fields are passed through `extra`, and the JSON formatter promotes them to top-level keys.

```python
logger.info("redis_set", extra={"redis_key": key})
```

## Development

Migrations are autogenerated from the models:

```bash
uv run alembic revision --autogenerate -m "description"
```

Formatting uses black, which also runs as an Alembic post-write hook on generated migrations.
