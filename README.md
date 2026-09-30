# Tarot Cards Bot

A Telegram bot that works with the Rider–Waite–Smith tarot deck, paired with a web admin panel where all
user-facing content is written and edited. The bot only reads from the database; every card description,
daily reading and history chapter is authored through the admin.

## Features

- **Telegram bot** on aiogram 3 with long polling and inline-keyboard navigation through the deck
- **Admin panel** built on SQLAdmin — Russian labels, session auth, length validation against Telegram's
  4096-character message limit, and a custom django-unfold–style theme with light and dark modes
- **Content in the database**: 78 cards, per-card daily readings, history of tarot
- **Two independent entry points** — the bot and the admin run as separate processes and share only the
  database layer
- **CSV export and import** for every admin view
- **Alembic migrations** for the schema
- **Docker Compose** for the whole stack: admin, bot and PostgreSQL

## Stack

| Layer | Choice |
|---|---|
| Bot framework | aiogram 3 |
| Admin | SQLAdmin on Starlette, served by uvicorn |
| ORM | SQLAlchemy 2 (async) |
| Migrations | Alembic |
| Database | SQLite in debug, PostgreSQL via asyncpg otherwise |
| Settings | pydantic-settings |

Requires Python 3.14+.

## Project layout

```
bot/
  admin/          admin panel: auth, base view, filters, wiring
  core/           settings, database, logging
  tarot/          models, admin views, repository, router, keyboards, message formatting
  run_bot.py      entry point — Telegram bot
  run_admin.py    entry point — admin panel
migrations/       Alembic
static/           admin assets: logo, css/admin.css theme
templates/        SQLAdmin template overrides
Dockerfile        image for both entry points
docker-compose.yml  admin, bot and PostgreSQL
.env.template     every setting the app reads
```

## Setup

Install dependencies:

```bash
uv sync
```

Create `.env` from the template and fill it in:

```bash
cp .env.template .env
```

At the very least `BOT_TOKEN`, `ADMIN_PASSWORD` and `ADMIN_SECRET_KEY` have to be set. The `POSTGRES_*`
values are only needed when running through Docker Compose, where they also configure the database
container itself.

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

### Locally

With `IS_DEBUG=true` both processes use the SQLite file, so nothing else has to be running.

The bot:

```bash
uv run python -m bot.run_bot
```

The admin panel:

```bash
uv run python -m bot.run_admin
```

The admin is then available at `http://localhost:8080/admin`.

### Docker Compose

```bash
docker compose up -d --build
```

This starts three containers: `pg` (PostgreSQL 16), `admin` and `bot`. Both application containers get
`IS_DEBUG=false` and `POSTGRES_HOST=pg`, so they talk to PostgreSQL instead of SQLite. The admin applies
`alembic upgrade head` before it starts, and the bot waits for it. Only the admin port is published; the
database stays on the internal network.

## Bot commands

| Command | What it does |
|---|---|
| `/start` | Greeting |
| `/help` | The command list |
| `/cards` | The deck behind inline buttons: arcana → cards → one card |
| `/card <name>` | One card with its description. The name has to match exactly, including case |
| `/history` | The history of tarot |

### Browsing the deck

`/cards` sends a single message and then rewrites it in place, so the chat stays clean:

```
/cards ──► buttons: major arcana and the four suits
             │  tap a suit
             ▼
          the same message → its 14 cards, two per row, plus "back"
             │  tap a card
             ▼
          the same message → the description in a quote, plus "back"
```

All of the state lives in the button itself. `DeckCallback` from `bot/tarot/keyboards.py` packs it into
`deck:<action>:<value>` — `action` picks the screen, `value` is the arcana index or the card id. Nothing is
kept in memory, so a message from last week still works after a restart.

Arcana are addressed by index rather than by title (`group_index()` in `bot/tarot/service.py`): emoji and
Cyrillic would eat into the 64 bytes Telegram allows for callback data, and renaming a heading would break
old buttons.

Message texts are built in `bot/tarot/service.py` and keyboards in `bot/tarot/keyboards.py`, so the handlers
stay thin. Tapping the same button twice makes Telegram answer "message is not modified" — the router
swallows exactly that error and re-raises everything else.

## Configuration

All settings are read from `.env`. Anything with a default can be omitted.

| Variable | Default | Purpose |
|---|---|---|
| `IS_DEBUG` | `true` | Switches the database target and the log format |
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
| `LOG_LEVEL` | `INFO` | Level for the `bot` and `aiogram` loggers |

`IS_DEBUG` does more than toggle verbosity: it selects SQLite over PostgreSQL, human-readable logs over
JSON, and disables the `Secure` flag on the admin session cookie. Set it to `false` in production.

## Content model

- **Card** — name, short description shown in spreads, and an image path
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

## Export and import

Every view inherits `BaseAdmin` from `bot/admin/base.py`, which turns CSV import on (`can_import = True`)
and keeps export raw (`use_pretty_export = False`). Exported file names carry the model and a timestamp,
e.g. `card_2026-09-29_18-40.csv`.

Both buttons sit in the list page header. Import opens a dialog with a file picker, a "continue on error"
checkbox and a progress bar; the report lists the line number and the reason for every row that did not
make it.

Things worth knowing before importing:

- **Headers are field names** (`name`, `description`, `image`), not the Russian column labels.
- **Rows go through the create form**, so the `Length` validators apply — an over-long description is
  rejected instead of being truncated.
- **Import only inserts.** There is no upsert: re-importing the same file fails on `Card.name`, which is
  unique. To change existing rows, edit them in the admin.
- **Each row is written in its own savepoint.** Without "continue on error" the whole import rolls back;
  with it, bad rows are skipped and reported.
- **Keep `use_pretty_export` off.** Pretty export writes the *formatted* value, so the `<span>` wrapper and
  the ellipsis from `_preview()` would end up in the CSV — and back in the database on the next import.
  Telegram then refuses to send such text, because it only accepts `<span class="tg-spoiler">`.

## Logging

Logging is configured in `bot/core/logging.py`: readable single-line output in debug, JSON in production.
Structured fields are passed through `extra`, and the JSON formatter promotes them to top-level keys.

```python
logger.info("admin_login_success", extra={"username": username})
```

## Development

Migrations are autogenerated from the models:

```bash
uv run alembic revision --autogenerate -m "description"
```

Formatting uses black, which also runs as an Alembic post-write hook on generated migrations.
