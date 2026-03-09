---
name: trend2video-sprint1
overview: "Реализация backend-модуля Sprint 1 для автогенерации TikTok-скриптов по трендам: intake из TikTok Creative Center, scoring, выбор шаблона, генерация структурированного script JSON, API и worker-ready архитектура."
todos:
  - id: setup-project-scaffold
    content: Создать скелет проекта trend2video с каталогами core, domain, integrations, persistence, apps (api/worker), tests и базовыми файлами pyproject.toml, README.md, alembic/
    status: completed
  - id: implement-domain-entities-and-normalizer
    content: Реализовать доменные сущности NormalizedTrend, TemplateDefinition, GeneratedScript, статусы трендов и сервис TrendNormalizer
    status: completed
  - id: implement-persistence-and-migrations
    content: Реализовать SQLAlchemy ORM-модели, Alembic-миграцию с созданием таблиц trends/templates/scripts и отдельный seed-скрипт для трёх шаблонов, а также репозитории
    status: completed
  - id: implement-tiktok-trend-source
    content: Реализовать TrendSource Protocol, CreativeCenterTrendSource с Playwright и StaticJsonTrendSource, использующие TrendNormalizer
    status: completed
  - id: implement-services-scorer-resolver-script
    content: Реализовать TrendScorer, TemplateResolver, LLMClient/FakeLLMClient, PromptBuilder и ScriptEngine на строгой модели BrandContext
    status: completed
  - id: implement-api-and-worker
    content: Реализовать FastAPI-приложение с маршрутами /health, /trends/ingest, /trends/process, /trends, /scripts и worker jobs ingest_trends/process_trends с выбором источника трендов через конфиг
    status: completed
  - id: implement-tests
    content: Написать unit-тесты для ключевых сервисов и integration-ish тесты для ingest и process flow, включая StaticJsonTrendSource
    status: completed
  - id: write-readme-and-commands
    content: Заполнить README описанием Sprint 1, структурой проекта, командами запуска, миграций, отдельным seed-шагом для шаблонов и примерами API-запросов
    status: completed
isProject: false
---

## План реализации Sprint 1 для `trend2video`

Статус на 2026-03-09: документ используется как design + progress artifact. Todo-статусы выше отражают текущее состояние репозитория; детальные разделы ниже описывают целевую и фактическую архитектуру Sprint 1.

### 1. Архитектура и стек

- **Подход**: модульный, domain-oriented backend с чётким разделением:
  - `domain` (сущности, чистые сервисы, scoring, resolver, script engine),
  - `persistence` (ORM-модели, репозитории),
  - `integrations` (TikTok источники, LLM),
  - `apps` (`api` и `worker`),
  - `core` (config, БД, логирование).
- **Технологии**:
  - Python 3.12, FastAPI,
  - SQLAlchemy 2.x (async engine + async session),
  - Pydantic 2.x + `pydantic-settings`,
  - PostgreSQL + Alembic (только schema migration),
  - Playwright (Creative Center) + альтернативный `StaticJsonTrendSource`,
  - httpx (на будущее, при необходимости),
  - pytest.
- **Async-политика**:
  - `async` только для I/O (API, БД, Playwright, внешние вызовы).
  - Доменные сервисы (`TrendScorer`, `TemplateResolver`, `TrendNormalizer`, `PromptBuilder`, чистая часть `ScriptEngine`) — синхронные функции (`def`), без `await`.

---

### 2. Структура директорий

- **Корень проекта**
  - `pyproject.toml` — зависимости (poetry), таргет Python 3.12.
  - `README.md` — описание Sprint 1, структура, команды, вызовы API, seed-шаблонов.
  - `alembic/` — env, `script.py`, миграции (только схема таблиц).
  - `trend2video/` — основной пакет.
  - `scripts/seed_templates.py` (или `trend2video/scripts/seed_templates.py`) — отдельный seed-скрипт для шаблонов.
- `**trend2video/core/`**
  - `config.py` — `AppSettings` (Pydantic Settings) + строго типизированный `BrandContext`.
  - `logging.py` — настройка `logging`/uvicorn-loggers.
  - `db.py` — async engine, `async_sessionmaker`, helpers/dep для получения сессии.
- `**trend2video/domain/entities/**`
  - `trend.py` — `NormalizedTrend`, enum `TrendStatus`.
  - `template.py` — `TemplateScene`, `TemplateDefinition` с полями `template_key`, `version`, и derived `id` при необходимости.
  - `script.py` — `GeneratedScript`.
  - (опционально) `brand.py` — модель `BrandContext` (может быть и в `core/config.py`).
- `**trend2video/domain/services/**`
  - `trend_normalizer.py` — `TrendNormalizer.normalize(raw: dict) -> NormalizedTrend`.
  - `trend_scorer.py` — `TrendScorer` (формула scoring c разложением на подметоды).
  - `template_resolver.py` — `TemplateResolver` (отдельный scoring шаблонов и `pick_best`).
  - `script_engine.py` — `ScriptEngine` (использует `LLMClient`, `PromptBuilder`, возвращает `GeneratedScript`).
- `**trend2video/integrations/tiktok/**`
  - `schemas.py` — при необходимости Pydantic-схемы для raw-структур.
  - `trend_source_base.py` — `TrendSource` (Protocol) + базовые типы/исключения.
  - `trend_source_creative_center.py` — `CreativeCenterTrendSource` (Playwright).
  - `trend_source_static.py` — `StaticJsonTrendSource` (fallback/детерминированный источник).
- `**trend2video/integrations/llm/**`
  - `base.py` — Protocol `LLMClient`.
  - `fake_llm.py` — `FakeLLMClient` (детерминированный, без внешних вызовов).
  - `prompt_builder.py` — сборка промпта для скрипта из тренда, шаблона и `BrandContext`.
- `**trend2video/persistence/models/**`
  - `trend.py` — `TrendORM` (таблица `trends`).
  - `template.py` — `TemplateORM` (таблица `templates`).
  - `script.py` — `ScriptORM` (таблица `scripts`).
- `**trend2video/persistence/repositories/**`
  - `trend_repository.py`.
  - `template_repository.py`.
  - `script_repository.py`.
- `**trend2video/apps/api/**`
  - `main.py` — создание FastAPI-приложения, подключение роутов.
  - `deps.py` — DI-фабрики: настройки, БД, репозитории, сервисы, `TrendSource`, `BrandContext`.
  - `routes/health.py` — `/health`.
  - `routes/trends.py` — `/trends/ingest`, `/trends/process`, `/trends` (GET).
  - `routes/scripts.py` — `/scripts` (либо роут в `trends.py`).
  - **Без** `routes/pipeline.py` в Sprint 1.
- `**trend2video/apps/worker/`**
  - `jobs/ingest_trends.py` — ingestion job.
  - `jobs/process_trends.py` — scoring + template + script job.
  - (опционально) `jobs/seed_templates.py` — если seed реализуется как job, а не отдельный скрипт в `scripts/`.
- `**trend2video/tests/**`
  - `unit/` — unit-тесты для доменных сервисов и нормализатора.
  - `integration/` — тесты ingest/process flow и, при желании, API.

---

### 3. Доменные сущности и BrandContext

- `**NormalizedTrend` (`domain/entities/trend.py`)**:
  - Pydantic v2-модель по спецификации:
    - `source`, `external_id`, `trend_type`, `title`, `region`, `industry | None`, `rank | None`, `heat | None`, `velocity | None`, `tags: list[str]`, `raw_payload: dict`, `discovered_at: datetime`.
  - Enum `TrendStatus`:
    - `discovered`, `scored`, `template_selected`, `script_generated`, `skipped`, `failed`.
- `**TemplateDefinition` и `TemplateScene` (`domain/entities/template.py`)**:
  - Из ТЗ, плюс поля для версионирования:
    - `template_key: str` — логический ключ (`"problem_solution_fastcut"`),
    - `version: str` — версия (`"v1"`),
    - (опционально) `id: str` — производное (`"problem_solution_fastcut_v1"`).
- `**GeneratedScript` (`domain/entities/script.py`)**:
  - Структура из ТЗ, без свободного текста, только строго типизированные поля.
- `**BrandContext` (строгая модель)**:
  - Вводится Pydantic-модель:
    - `product_name: str`
    - `product_type: str`
    - `audience: list[str]`
    - `pain_points: list[str]`
    - `tone: str`
    - `forbidden_topics: list[str] = Field(default_factory=list)`
    - `cta_style: str`
    - `niche_tags: list[str] = Field(default_factory=list)`
  - `AppSettings` содержит поле `brand_context: BrandContext`.
  - `TrendScorer`, `TemplateResolver` (где нужно), `PromptBuilder` и `ScriptEngine` принимают именно `BrandContext`, не `dict`.
- `**TrendNormalizer` (`domain/services/trend_normalizer.py`)**:
  - `def normalize(self, raw: dict) -> NormalizedTrend`.
  - Явное сопоставление полей из raw-структуры источника к полям `NormalizedTrend`.
  - Обработка `None`, парсинг чисел/дат, нормализация строк (регион, тип тренда), дефолты для отсутствующих полей.
  - Любая логика, завязанная на формат Creative Center/JSON, изолирована в интеграционном слое + нормализаторе.

---

### 4. Persistence: ORM-модели, миграции и репозитории

#### 4.1. ORM-модели

- `**TrendORM` (`persistence/models/trend.py`)**:
  - Таблица `trends`:
    - `id` (PK, UUID/serial),
    - `source`, `external_id`, `trend_type`, `title`, `region`, `industry`,
    - `rank`, `heat`, `velocity`,
    - `tags_json` (JSONB),
    - `raw_payload_json` (JSONB),
    - `score` (Float, nullable),
    - `status` (String, enum constraint по `TrendStatus`),
    - `discovered_at`,
    - `created_at`, `updated_at`.
  - Уникальный constraint на `(source, external_id)` (upsert-ключ).
- `**TemplateORM` (`persistence/models/template.py`)**:
  - Таблица `templates`:
    - `id` (PK),
    - `template_key: String`,
    - `version: String`,
    - `config_json: JSONB` (сериализованный `TemplateDefinition`),
    - `is_active: Boolean`,
    - `created_at`, `updated_at`.
  - Уникальный constraint на `(template_key, version)`.
- `**ScriptORM` (`persistence/models/script.py`)**:
  - Таблица `scripts`:
    - `id` (PK),
    - `trend_id` (FK → `trends.id`),
    - `template_id` (FK → `templates.id`),
    - `script_json: JSONB` (содержит `GeneratedScript`),
    - `status: String` (например, `created`, `failed`),
    - `created_at`, `updated_at`.
  - Уникальный constraint на `trend_id` для Sprint 1 (один script на тренд).

#### 4.2. Alembic-миграции

- Первая миграция:
  - создаёт таблицы `trends`, `templates`, `scripts` со всеми полями и constraint’ами;
  - **не сидирует** шаблоны.

#### 4.3. Seed шаблонов

- Скрипт `scripts/seed_templates.py` (или job под `apps/worker/jobs`):
  - Подключается к БД,
  - в транзакции делает upsert трёх базовых шаблонов:
    - `template_key="problem_solution_fastcut"`, `version="v1"`,
    - `template_key="myth_busting"`, `version="v1"`,
    - `template_key="before_after_demo"`, `version="v1"`,
  - идемпотентен (повторный запуск не создаёт дубликаты).
- README: после `alembic upgrade head` нужно запустить seed-скрипт.

#### 4.4. Репозитории

- `**TrendRepository`**:
  - `async def upsert_trends(self, trends: list[NormalizedTrend]) -> tuple[list[TrendORM], dict]`:
    - upsert по `(source, external_id)`,
    - обновляет `rank`, `heat`, `velocity`, `tags_json`, `raw_payload_json`, `updated_at`,
    - `discovered_at` не трогает, если запись уже есть,
    - не сбрасывает статусы pipeline (например, `script_generated`), если тренд уже прошёл дальше, без спец-флага,
    - возвращает список ORM-объектов и summary:
      - `{"inserted_count": int, "updated_count": int, "skipped_count": int}`.
  - `async def get_unprocessed_trends(self, limit: int = 20) -> list[TrendORM]`:
    - выбирает тренды по политике: статусы, для которых ещё нет скрипта (например, `discovered`, `scored` без script).
  - `async def update_score(self, trend_id: str, score: float) -> None`:
    - обновляет `score`, статус на `scored`.
  - `async def mark_status(self, trend_id: str, status: str) -> None`.
  - `async def list_trends(self, status: str | None = None, limit: int = 50, offset: int = 0) -> list[TrendORM]`.
  - `async def get_by_source_external_id(self, source: str, external_id: str) -> TrendORM | None`.
- `**TemplateRepository**`:
  - `async def get_active_templates(self) -> list[TemplateORM]`.
  - `async def get_active_template_definitions(self) -> list[TemplateDefinition]`:
    - десериализует `config_json` в доменные `TemplateDefinition`.
  - `async def get_latest_by_key(self, template_key: str) -> TemplateDefinition | None`.
  - `async def get_by_id(self, template_id: str) -> TemplateORM | None`.
- `**ScriptRepository**`:
  - `async def create_script(self, trend: TrendORM, template: TemplateORM, script: GeneratedScript) -> ScriptORM`:
    - сохраняет `script_json`, выставляет статус (`created`), учитывает уникальность `trend_id`.
  - `async def get_by_trend_id(self, trend_id: str) -> ScriptORM | None`.
  - `async def exists_for_trend(self, trend_id: str) -> bool`.
  - `async def list_scripts(self, limit: int = 50, offset: int = 0) -> list[ScriptORM]`.

---

### 5. TikTok integrations: TrendSource, CreativeCenter и StaticJson

#### 5.1. Абстракция `TrendSource`

- В `integrations/tiktok/trend_source_base.py` вводится Protocol:
  - `async def fetch_new_trends(self) -> list[NormalizedTrend]`.
- Остальной код оперирует только `TrendSource`, не зная деталей реализации.

#### 5.2. `CreativeCenterTrendSource`

- В `trend_source_creative_center.py`:
  - Конструктор принимает:
    - настройки из `AppSettings` (URL, регион, пагинация и пр.),
    - `TrendNormalizer`.
  - Методы:
    - `_open_page` — инициализация Playwright, открытие целевой страницы, ожидание нужных селекторов.
    - `_extract_raw_trends` — сбор сырых трендов (`list[dict]`) через селекторы/`eval_on_selector_all`.
    - `_normalize_trend` — обёртка над `TrendNormalizer`.
    - `fetch_new_trends` — orchestration: открыть → собрать raw → нормализовать → вернуть `list[NormalizedTrend]`.
  - Обработка ошибок:
    - логирование,
    - graceful fallback (например, поднять понятное исключение или вернуть пустой список).
  - В коде помечены TODO о хрупкости HTML и возможной замене на API.

#### 5.3. `StaticJsonTrendSource`

- В `trend_source_static.py`:
  - Читает локальный JSON-файл с сырыми трендами:
    - путь берётся из `AppSettings.static_trends_path`.
  - Для каждого объекта вызывает `TrendNormalizer.normalize(raw)` → `NormalizedTrend`.
  - Используется:
    - в локальной разработке,
    - в CI,
    - как fallback, если Creative Center ломается,
    - для детерминированной отладки scoring/template/script flow.

#### 5.4. Выбор источника через конфиг

- В `AppSettings`:
  - `trend_source: Literal["creative_center", "static"] = "static"`,
  - `static_trends_path: str`.
- В `apps/api/deps.py` и worker jobs:
  - фабрика `get_trend_source(settings, normalizer)`:
    - если `settings.trend_source == "creative_center"` → `CreativeCenterTrendSource`,
    - иначе → `StaticJsonTrendSource`.
- `/trends/ingest` и `run_ingest_job()` работают только через `TrendSource`, режим задаётся конфигом.

---

### 6. LLM, PromptBuilder и ScriptEngine

- `**LLMClient` (`integrations/llm/base.py`)**:
  - Protocol:
    - `async def generate_structured(self, prompt: str, schema: type[BaseModel]) -> dict`.
- `**FakeLLMClient` (`fake_llm.py`)**:
  - Реализация `LLMClient`:
    - по промпту/контексту детерминированно собирает dict, валиден относительно `GeneratedScript`;
    - использует данные тренда, шаблона, `BrandContext` для генерации текстов;
    - не делает внешних HTTP-вызовов — полностью локальный/тестируемый.
- `**PromptBuilder` (`prompt_builder.py`)**:
  - `def build_script_prompt(trend: NormalizedTrend, template: TemplateDefinition, brand_ctx: BrandContext) -> str`.
  - В промпте:
    - описываются тренд, бренд, аудитория, pain points;
    - описывается структура шаблона (scene_plan, text slots);
    - жёстко задаётся формат ответа — JSON, совместимый с `GeneratedScript`;
    - указываются ограничения: forbidden_topics, tone, CTA стиль.
- `**ScriptEngine` (`domain/services/script_engine.py`)**:
  - Инициализируется `LLMClient`.
  - `async def generate(self, trend, template, brand_ctx) -> GeneratedScript`:
    - собирает промпт через `PromptBuilder`,
    - вызывает `llm_client.generate_structured(prompt, GeneratedScript)`,
    - валидирует результат через `GeneratedScript.model_validate`,
    - возвращает экземпляр `GeneratedScript`.

---

### 7. TrendScorer и TemplateResolver

- `**TrendScorer` (`trend_scorer.py`)**:
  - `def score(self, trend: NormalizedTrend, brand_ctx: BrandContext, templates: list[TemplateDefinition]) -> float`.
  - Приватные методы:
    - `_calc_velocity(trend) -> float` — нормализация `velocity` в диапазон [0, 1].
    - `_calc_niche_relevance(trend, brand_ctx) -> float` — соответствие `trend.tags` / `industry` целевой нише и `niche_tags` бренда.
    - `_calc_brand_fit(trend, brand_ctx) -> float` — forbidden topics, тон, соответствие продукту/аудитории.
    - `_calc_template_fit(trend, templates) -> float` — наличие подходящих шаблонов по структуре, тегам, hooks.
    - `_calc_production_feasibility(trend) -> float` — эвристики по реализуемости.
  - Формула:
    - `score = 0.35 * velocity + 0.25 * niche_relevance + 0.15 * brand_fit + 0.15 * template_fit + 0.10 * production_feasibility`.
    - Компоненты защищены от `None` и `NaN`.
    - Итоговый `score` clamped в [0.0, 1.0].
- `**TemplateResolver` (`template_resolver.py`)**:
  - `def score_template(self, trend: NormalizedTrend, template: TemplateDefinition, brand_ctx: BrandContext) -> float`:
    - учитывает:
      - `trend_type` vs `template.tags`/scene_plan,
      - индустрию/таги и `niche_tags` бренда,
      - наличие подходящих hooks под тон/аудиторию.
  - `def pick_best(self, trend: NormalizedTrend, templates: list[TemplateDefinition], brand_ctx: BrandContext) -> TemplateDefinition | None`:
    - считает score для каждого шаблона,
    - выбирает лучший, если score > порога (например, 0.3),
    - иначе возвращает `None`.

---

### 8. API слой (FastAPI)

- `**apps/api/main.py`**:
  - Создаёт FastAPI app, подключает роуты `health`, `trends`, `scripts`.
  - Настраивает CORS (минимально), при желании — версию/теги.
- `**apps/api/deps.py**`:
  - `get_settings()` — singleton `AppSettings`.
  - `get_db_session()` — async generator сессии.
  - `get_brand_context()` — возвращает `BrandContext` из настроек.
  - Репозитории: `get_trend_repo`, `get_template_repo`, `get_script_repo`.
  - Сервисы: `get_trend_scorer`, `get_template_resolver`, `get_llm_client` (возвращает `FakeLLMClient`), `get_script_engine`.
  - `get_trend_source(settings, normalizer)` — выбор между `CreativeCenterTrendSource` и `StaticJsonTrendSource`.
- **Маршруты**:
  - `/health` (GET):
    - Возвращает `{"status": "ok"}`.
  - `/trends/ingest` (POST):
    - Берёт `TrendSource` через DI (режим — из конфига),
    - вызывает `fetch_new_trends`,
    - передаёт в `TrendRepository.upsert_trends`,
    - возвращает summary:
      - `inserted_count`, `updated_count`, `skipped_count`, возможно ids.
  - `/trends/process` (POST):
    - Берёт unprocessed тренды через `TrendRepository.get_unprocessed_trends(limit=...)`,
    - загружает активные шаблоны (`TemplateRepository.get_active_template_definitions()`),
    - для каждого тренда:
      - проверяет `ScriptRepository.exists_for_trend(trend.id)`;
      - если уже есть скрипт и не передан `force_regenerate=True` → пропускает (учитывает в `skipped_existing`);
      - считает score (`TrendScorer`), обновляет в БД;
      - выбирает шаблон (`TemplateResolver`);
      - если шаблон найден:
        - генерирует скрипт (`ScriptEngine`),
        - сохраняет через `ScriptRepository.create_script`,
        - обновляет статус тренда на `script_generated`;
      - при ошибках — статус `failed`.
    - Возвращает summary: сколько обработано, сколько получили скрипт, сколько пропущено/failed/уже были сгенерированы.
  - `/trends` (GET):
    - Использует `TrendRepository.list_trends(...)`,
    - возвращает список трендов с score и статусом (с пагинацией).
  - `/scripts` (GET):
    - Использует `ScriptRepository.list_scripts(...)`,
    - может возвращать базовую информацию о скриптах (trend_id, template, timestamps).

---

### 9. Worker / jobs и seed

- `**apps/worker/jobs/ingest_trends.py`**:
  - `async def run_ingest_job()`:
    - читает настройки (`AppSettings`),
    - создаёт engine/session,
    - инициализирует `TrendNormalizer` и `TrendSource` (через такую же фабрику, как в API),
    - вызывает `fetch_new_trends`,
    - вызывает `TrendRepository.upsert_trends`,
    - логирует summary (inserted/updated/skipped).
- `**apps/worker/jobs/process_trends.py**`:
  - `async def run_process_job(limit: int = 20, force_regenerate: bool = False)`:
    - читает настройки, БД,
    - берёт unprocessed тренды,
    - берёт активные шаблоны (`TemplateRepository.get_active_template_definitions()`),
    - создаёт `TrendScorer`, `TemplateResolver`, `ScriptEngine` (с `FakeLLMClient`),
    - повторяет ту же логику, что `/trends/process`.
- **Seed templates**:
  - Отдельный модуль `scripts/seed_templates.py` или worker job `seed_templates`,
  - README указывает команду запуска seed после миграций.

---

### 10. Тесты

- **Unit-тесты (`tests/unit/`)**:
  - `test_trend_normalizer.py`:
    - корректный маппинг raw → `NormalizedTrend`,
    - обработка отсутствующих/неправильных полей.
  - `test_trend_scorer.py`:
    - разные комбинации `velocity`, `tags`, `BrandContext`,
    - проверка clamp [0, 1].
  - `test_template_resolver.py`:
    - выбор правильного шаблона,
    - поведение при отсутствии подходящих (возвращает `None`).
  - `test_script_engine.py`:
    - с `FakeLLMClient` проверяет, что:
      - результат — валидный `GeneratedScript`,
      - учитываются brand context (tone, CTA style, forbidden topics).
- **Integration-ish (`tests/integration/`)**:
  - `test_ingest_flow.py`:
    - использует `StaticJsonTrendSource` (или мок `TrendSource`),
    - проверяет, что ingest:
      - создаёт новые тренды,
      - обновляет существующие,
      - возвращает корректное summary.
  - `test_process_flow.py`:
    - поднимает тестовую БД (in-memory SQLite или тестовый PostgreSQL),
    - прогоняет весь flow:
      - есть несколько трендов в статусе `discovered`,
      - есть шаблоны (через seed/helper),
      - `run_process_job` создаёт `scripts`, обновляет статусы.
  - (Опционально) API-тесты с `httpx.AsyncClient`:
    - `/health`, `/trends/ingest` (через StaticJson), `/trends/process`, `/trends`, `/scripts`.

---

### 11. README и команды

- **README разделы**:
  - Что делает Sprint 1:
    - intake трендов (Creative Center + Static JSON),
    - scoring,
    - выбор шаблона,
    - генерация `GeneratedScript`,
    - сохранение в БД,
    - API + worker-ready архитектура.
  - Структура проекта (краткое описание директорий и их ролей).
  - Как поднять проект локально:
    - `poetry install`,
    - настройка переменных окружения (URL БД, `TREND_SOURCE`, `STATIC_TRENDS_PATH`, brand context),
    - `alembic upgrade head`,
    - запуск seed-шаблонов (`python -m trend2video.scripts.seed_templates` или аналог),
    - запуск API: `poetry run uvicorn trend2video.apps.api.main:app --reload`,
    - запуск worker jobs: `poetry run python -m trend2video.apps.worker.jobs.ingest_trends` / `process_trends`.
  - Как вызвать endpoints:
    - `GET /health`,
    - `POST /trends/ingest`,
    - `POST /trends/process`,
    - `GET /trends`,
    - `GET /scripts` (с примерами `curl`/`httpie`).
  - Что будет во Sprint 2:
    - renderer,
    - Telegram review workflow,
    - TikTok / IG / YouTube publishers,
    - расширение pipeline, метрики перформанса шаблонов.

---

### 12. Критерии готовности Sprint 1

Sprint 1 считается завершённым, если:

- проект запускается локально;
- `GET /health` возвращает `{ "status": "ok" }`;
- ingest работает **минимум с одним стабильным source** (`StaticJsonTrendSource`) и может быть переключён на `CreativeCenterTrendSource` через конфиг;
- `POST /trends/ingest` сохраняет тренды, корректно считает `inserted/updated/skipped`;
- `POST /trends/process`:
  - считает `score`,
  - выбирает шаблон,
  - генерирует `GeneratedScript` через `ScriptEngine`+`FakeLLMClient`,
  - сохраняет `scripts` и обновляет статусы трендов,
  - не плодит дубли скриптов при повторном запуске без `force_regenerate`;
- минимум 3 шаблона (`problem_solution_fastcut_v1`, `myth_busting_v1`, `before_after_demo_v1`) загружены в БД через seed-скрипт;
- unit- и integration-ish тесты для критичных частей (normalizer, scorer, resolver, script engine, ingest/process flow) проходят;
- структура кода позволяет без боли перейти к Sprint 2 (renderer, Telegram review, TikTok/IG/YT publishers, новые источники трендов).
