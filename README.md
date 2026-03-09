## trend2video Sprint 1

Backend-модуль для автогенерации TikTok-скриптов по трендам (Sprint 1): intake трендов, scoring, выбор шаблона, генерация структурированного скрипта и сохранение в БД.

### Что делает Sprint 1

- **Trend intake**: получение трендов из TikTok Creative Center (Playwright) и/или из локального JSON (`StaticJsonTrendSource`).
- **Scoring**: расчёт score тренда с учётом brand context и доступных шаблонов.
- **Template resolver**: выбор лучшего шаблона под конкретный тренд.
- **Script engine**: генерация строго типизированного `GeneratedScript` через абстракцию LLM (в Sprint 1 — `FakeLLMClient`).
- **Persistence**: сохранение трендов, шаблонов и скриптов в PostgreSQL.
- **API + worker**: FastAPI-приложение и воркеры для ingest/process.

### Структура проекта (основное)

- `trend2video/core/` — конфиг (`AppSettings` + `BrandContext`), подключение к БД, логирование.
- `trend2video/domain/entities/` — `NormalizedTrend`, `TemplateDefinition`, `GeneratedScript`, `BrandContext`, статусы тренда.
- `trend2video/domain/services/` — `TrendNormalizer`, `TrendScorer`, `TemplateResolver`, `ScriptEngine`.
- `trend2video/integrations/tiktok/` — `TrendSource` Protocol, `CreativeCenterTrendSource`, `StaticJsonTrendSource`.
- `trend2video/integrations/llm/` — `LLMClient`, `FakeLLMClient`, `prompt_builder`.
- `trend2video/persistence/models/` — ORM-модели `TrendORM`, `TemplateORM`, `ScriptORM`.
- `trend2video/persistence/repositories/` — репозитории трендов, шаблонов и скриптов.
- `trend2video/apps/api/` — FastAPI-приложение (`main.py`, deps, роуты `/health`, `/trends`, `/scripts`).
- `trend2video/apps/worker/` — jobs `ingest_trends.py`, `process_trends.py`.
- `trend2video/scripts/seed_templates.py` — сидирование трёх базовых шаблонов.
- `alembic/` — конфигурация и миграции (инициальная схема `trends/templates/scripts`).
- `tests/` — unit и integration-ish тесты.

### Как поднять проект локально

1. **Установить зависимости**

```bash
poetry install
```
# Explanation: Устанавливает все зависимости проекта через poetry.

2. **Настроить переменные окружения**

Минимум:

- `T2V_DATABASE_URL` (если отличается от значения по умолчанию в `core/config.py`),
- `T2V_TREND_SOURCE` (`static` или `creative_center`),
- `T2V_STATIC_TRENDS_PATH` (путь к JSON с трендами для статического источника).

3. **Накатить миграции**

```bash
poetry run alembic upgrade head
```
# Explanation: Применяет Alembic-миграции и создаёт таблицы в БД.

4. **Сидировать шаблоны**

```bash
poetry run python -m trend2video.scripts.seed_templates
```
# Explanation: Создаёт/обновляет 3 базовых шаблона в таблице templates.

5. **Запустить API**

```bash
poetry run uvicorn trend2video.apps.api.main:app --reload
```
# Explanation: Поднимает FastAPI-приложение с маршрутами /health, /trends и /scripts.

6. **Запустить worker jobs вручную (опционально)**

```bash
poetry run python -m trend2video.apps.worker.jobs.ingest_trends
poetry run python -m trend2video.apps.worker.jobs.process_trends
```
# Explanation: Первый джоб делает ingest трендов, второй — обрабатывает тренды до скриптов.

### Примеры API-запросов

1. **Health-check**

```bash
curl http://localhost:8000/health
```
# Explanation: Проверка, что API живо и отвечает.

2. **Ingest трендов**

```bash
curl -X POST http://localhost:8000/trends/ingest
```
# Explanation: Запускает intake трендов из выбранного источника и сохраняет их в БД.

3. **Process трендов**

```bash
curl -X POST "http://localhost:8000/trends/process?limit=20&force_regenerate=false"
```
# Explanation: Берёт необработанные тренды, считает score, выбирает шаблон, генерирует скрипты.

4. **Список трендов**

```bash
curl "http://localhost:8000/trends?limit=50"
```
# Explanation: Возвращает список трендов с их score и статусом.

5. **Список скриптов**

```bash
curl "http://localhost:8000/scripts?limit=50"
```
# Explanation: Возвращает список сгенерированных скриптов и базовую информацию по ним.

### Что будет во Sprint 2

- Добавление renderer-а для реального видео.
- Workflow ревью через Telegram/другие каналы.
- Паблишеры для TikTok / Instagram / YouTube.
- Расширение pipeline, метрики перформанса шаблонов и перегенерация.

