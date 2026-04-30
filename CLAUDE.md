# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

MUSILAB — a music school learning platform in Django 6.0.2. Language: Portuguese (pt-br). Timezone: America/Sao_Paulo.

## Commands

```bash
# Run dev server
python manage.py runserver

# Migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files (production only — not needed in dev)
python manage.py collectstatic
```

## Static Files — Critical Rule

**Always edit `setup/static/` — never `static/`.**

- `STATICFILES_DIRS = [setup/static/]` — this is what Django serves in development
- `STATIC_ROOT = static/` — this is the output of `collectstatic` and gets overwritten

Key files:
- CSS: `setup/static/style/styles.css`
- JS: `setup/static/assets/` (auth.js, dashboard.js, lesson.js, notifications.js)
- Logo: `setup/static/assets/logo-musilab.png`

## App Architecture

```
core/          Admin Studio — CRUD for all content (superuser only)
accounts/      Auth, Profile, NotificationSettings, Notification, PlaybackSettings
courses/       Module → Lesson → Material/Exercise/Question/Answer
progress/      LessonProgress, ModuleProgress, StudyStreak, ActivityLog
achievements/  Achievement, UserAchievement
```

URL namespaces: `core:`, `accounts:`, `courses:`, `progress:`, `achievements:`

## Key Patterns

**Superuser guard** — all Studio views use `@superuser_required` (defined in `core/views.py`):
```python
from core.views import superuser_required  # or copy the decorator
```

**Sending notifications** — always use `send_notification()` from `accounts/views.py`, never `send_mail()` directly. It saves to the DB (bell icon) AND sends email:
```python
from accounts.views import send_notification
send_notification(user=user, subject='...', message='...')
```

**Video serving** — uploaded videos are served via `courses:video_serve` (not direct media URL) to support HTTP Range Requests for seeking.

**Progress tracking** — `progress/views.py::update_progress` is called via AJAX every 5s from `lesson.js`. Auto-completes at ≥90% of video watched.

## Templates

All templates are standalone (no base template inheritance). Each inner page (dashboard, modules, progress, achievements, profile, settings) includes:
- The full sidebar nav
- A `🔔` notification bell button (`id="notif-btn"`, `onclick="toggleNotifPanel()"`)
- The notification panel HTML at end of body
- `<script src="{% static 'assets/notifications.js' %}"></script>`

## Models — Unique Constraints

- `Module.order` — globally unique (`unique=True`)
- `Lesson.order` — unique per module (`unique_together = ('module', 'order')`)
- `Exercise.number` — unique per lesson (`unique_together = ('lesson', 'number')`)

Studio save views wrap these in `except IntegrityError` and show a user-facing error message.

## Environment Variables (`.env`)

```
SECRET_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
EMAIL_HOST_USER=        # Gmail address used as sender
EMAIL_HOST_PASSWORD=    # Gmail App Password (16-char, spaces allowed)
```

## Database

SQLite (`db.sqlite3`). Media files in `media/` (gitignored in production).
