# Stage Templates

Common implementation stage patterns for Web Portal specifications.

## Database Stage Template

### Этап: Database Models & Migration (~150-200 строк)
**Статус:** ⬜ Не начат

**Цель:** Создать схему базы данных для {feature name}

**Задачи:**
- [ ] Создать `src/web_portal/models/{domain}.py` с моделями
- [ ] Создать Alembic миграцию `alembic/versions/{timestamp}_{description}.py`
- [ ] Добавить индексы для производительности
- [ ] Обновить `src/web_portal/models/__init__.py` (экспорт моделей)

**Файлы:**
- `src/web_portal/models/{domain}.py` (создать)
- `alembic/versions/{timestamp}_{description}.py` (создать)
- `src/web_portal/models/__init__.py` (изменить)

**Критерий приёмки:**
- Миграция выполняется успешно через `alembic upgrade head`
- Таблицы созданы с корректной схемой
- Foreign keys и indexes работают корректно
- Модели импортируются из `models` пакета

---

## Service Layer Stage Template

### Этап: Service Layer (~200-300 строк)
**Статус:** ⬜ Не начат

**Цель:** Реализовать бизнес-логику для {feature name}

**Задачи:**
- [ ] Создать `src/web_portal/services/{service}_service.py`
- [ ] Реализовать {method_1} с {validation/logic}
- [ ] Реализовать {method_2} с {validation/logic}
- [ ] Реализовать {method_3} с {validation/logic}
- [ ] Добавить обработку ошибок

**Файлы:**
- `src/web_portal/services/{service}_service.py` (создать)

**Критерий приёмки:**
- Сервис обрабатывает edge cases ({example})
- Все операции транзакционно-безопасны (если БД)
- Ошибки логируются и обрабатываются корректно

---

## API Endpoints Stage Template

### Этап: API Endpoints (~200-300 строк)
**Статус:** ⬜ Не начат

**Цель:** Создать REST API для {feature name}

**Задачи:**
- [ ] Создать Pydantic схемы в `src/web_portal/api/schemas/{feature}_schemas.py`
- [ ] Создать `src/web_portal/api/{feature}.py` роутер
- [ ] Реализовать `POST /api/{resource}` endpoint
- [ ] Реализовать `GET /api/{resource}/{{id}}` endpoint
- [ ] Реализовать `PUT /api/{resource}/{{id}}` endpoint (если нужно)
- [ ] Зарегистрировать роутер в `src/web_portal/api/__init__.py`

**Файлы:**
- `src/web_portal/api/schemas/{feature}_schemas.py` (создать)
- `src/web_portal/api/{feature}.py` (создать)
- `src/web_portal/api/__init__.py` (изменить)

**Endpoints:**
- `POST /api/{resource}` — создание ресурса
- `GET /api/{resource}/{{id}}` — получение ресурса
- `PUT /api/{resource}/{{id}}` — обновление ресурса

**Критерий приёмки:**
- API возвращает корректные JSON ответы
- Валидация Pydantic работает корректно
- Пагинация работает (если применимо)
- Права доступа проверяются (если нужно)

---

## Frontend Page Stage Template

### Этап: Frontend Template (~300-500 строк)
**Статус:** ⬜ Не начат

**Цель:** Создать UI для {feature name}

**Задачи:**
- [ ] Создать `src/web_portal/templates/{pages|services}/{feature}.html`
- [ ] Добавить web route в `src/web_portal/web/routes.py`
- [ ] Реализовать {component 1} (table/form/etc)
- [ ] Реализовать {component 2}
- [ ] Добавить JavaScript для {interaction}
- [ ] Добавить стили если нужно

**Файлы:**
- `src/web_portal/templates/{pages|services}/{feature}.html` (создать)
- `src/web_portal/web/routes.py` (изменить)
- `src/web_portal/static/css/{feature}.css` (создать, если нужно)
- `src/web_portal/static/js/{feature}.js` (создать, если нужно)

**Критерий приёмки:**
- Страница загружается и отображает данные корректно
- Responsive дизайн сохранён
- JavaScript взаимодействие работает без перезагрузки (если применимо)
- Ошибки отображаются пользователю понятно

---

## Message Bus Stage Template

### Этап: Message Bus Integration (~250-350 строк)
**Статус:** ⬜ Не начат

**Цель:** Интегрировать {feature} в Message Bus для асинхронной обработки

**Задачи:**
- [ ] Создать `src/web_portal/modules/{module}/commands.py`
- [ ] Определить команды: {Command1}, {Command2}
- [ ] Определить события: {Event1}, {Event2}
- [ ] Создать `src/web_portal/modules/{module}/handlers.py`
- [ ] Реализовать `handle_{command}()` command handler
- [ ] Создать `src/web_portal/modules/{module}/event_handlers.py`
- [ ] Зарегистрировать handlers в `src/web_portal/main.py`

**Файлы:**
- `src/web_portal/modules/{module}/commands.py` (создать)
- `src/web_portal/modules/{module}/handlers.py` (создать)
- `src/web_portal/modules/{module}/event_handlers.py` (создать)
- `src/web_portal/main.py` (изменить)

**Критерий приёмки:**
- Commands выполняются асинхронно через MessageBus
- Events публикуются и обрабатываются подписчиками
- Handlers обновляют статус в базе данных
- Ошибки изолируются и логируются

---

## Testing Stage Template

### Этап: Testing & Documentation (~150-250 строк)
**Статус:** ⬜ Не начат

**Цель:** Добавить тесты и обновить документацию

**Задачи:**
- [ ] Создать `tests/test_{feature}_service.py`
- [ ] Создать `tests/test_{feature}_api.py`
- [ ] Протестировать edge cases
- [ ] Обновить `.ai/ARCHITECTURE.md` с {описанием изменений}
- [ ] Добавить docstrings в код

**Файлы:**
- `tests/test_{feature}_service.py` (создать)
- `tests/test_{feature}_api.py` (создать)
- `.ai/ARCHITECTURE.md` (изменить)

**Критерий приёмки:**
- Тесты покрывают основные use cases
- Edge cases обработаны
- Архитектура документирована
- Code имеет docstrings

---

## Configuration Stage Template

### Этап: Configuration (~50-100 строк)
**Статус:** ⬜ Не начат

**Цель:** Добавить настройки для {feature name}

**Задачи:**
- [ ] Добавить настройки в `src/web_portal/config.py`
- [ ] Обновить `.env.example` с новыми переменными
- [ ] Добавить валидацию настроек (если нужно)

**Файлы:**
- `src/web_portal/config.py` (изменить)
- `.env.example` (изменить)

**Переменные окружения (.env):**
```bash
{SETTING_1}=
{SETTING_2}=
{SETTING_3}=
```

**Критерий приёмки:**
- Настройки загружаются из переменных окружения
- Валидация работает корректно
- Default значения разумны
