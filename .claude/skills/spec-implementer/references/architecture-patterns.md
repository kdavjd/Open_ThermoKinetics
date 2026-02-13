# Architecture Patterns Reference

Детальные паттерны реализации для web_portal проекта.

## Слои приложения

```
Web Layer        → api/, web/, templates/
Business Layer   → services/, auth/, modules/
Infrastructure   → infrastructure/ (Message Bus, email)
Data Layer       → database/, models/
```

## Правила создания файлов

| Тип файла    | Расположение                         | Паттерн                   |
| ------------ | ------------------------------------ | ------------------------- |
| API endpoint | `src/web_portal/api/`                | REST, Pydantic schemas    |
| Web route    | `src/web_portal/web/routes.py`       | Jinja2 templates          |
| Service      | `src/web_portal/modules/{name}/`     | BaseService interface     |
| Model        | `src/web_portal/models/`             | SQLAlchemy ORM            |
| Template     | `src/web_portal/templates/`          | Jinja2, extends base.html |
| Command      | `src/web_portal/infrastructure/bus/` | dataclass, MessageBus     |
| Tests        | `tests/`                             | pytest, async             |

## Message Bus паттерны

```python
# Command — императивный запрос (1 handler)
@dataclass
class SendEmailCommand(Command):
    to: str
    subject: str
    body: str

# Event — уведомление (N subscribers)
@dataclass
class BookingCreatedEvent(Event):
    booking_id: int
    guest_email: str

# Query — запрос данных (1 handler, returns result)
@dataclass
class GetUserQuery(Query):
    user_id: int
```

## UI паттерны

```
templates/
├── base.html              # Наследование: {% extends "base.html" %}
├── components/            # Включение: {% include "components/header.html" %}
├── pages/                 # {% block content %}
└── services/              # Страницы сервисов
```

## Лимиты

**Максимум строк на этап:** 250

**Исключения (не считаются):**
- `*.lock` — lock-файлы
- `alembic/versions/*.py` — миграции
- `*.generated.*` — автогенерируемые
- `.ai/*.md` — документация фреймворка
