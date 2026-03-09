Ты senior Python backend engineer и architect.
Нужно переписать Sprint 1 проекта `trend2video` не с нуля, а как **refactor existing foundation into Trend Discovery Foundation v2**.

## Важный контекст

Текущий Sprint 1 был построен вокруг упрощённой модели:

`TrendSource -> Trend -> Score -> Template -> Script`

Но после изучения TikTok Creative Center стало понятно, что реальная доменная модель сложнее:

- тренд зависит от страны
- зависит от временного окна
- зависит от типа источника
- в `Keyword Insights` первичный сигнал — это `keyword`
- для каждого keyword есть `related videos`
- именно related videos дают референсы для будущей генерации
- script нельзя генерировать сразу после одной плоской trend row
- сначала нужен слой:
  - search job
  - keyword trends
  - related videos
  - candidate extraction
  - и только потом script generation

## Цель

Нужно перепроектировать текущий Sprint 1 в новую архитектуру:

`TrendSearchJob -> KeywordTrend -> RelatedVideo -> ContentCandidate -> Script`

## Критически важно

Не удаляй всё бездумно.
Нужно:
- сохранить полезный foundation текущего кода
- но перестроить доменную модель и pipeline под реальную задачу

---

# Что нужно сделать

## 1. Провести рефактор архитектуры, а не косметический патч

Нужно:
- оставить FastAPI, worker jobs, repository pattern, config layer, DB layer
- оставить idea of source adapters
- оставить template resolver / script engine как будущие downstream blocks
- но заменить старую модель `trends` как центральную сущность на новую модель trend discovery

---

# Новая доменная модель

Нужно ввести следующие основные сущности.

## A. TrendSearchJob

Это настраиваемое поисковое задание.

Пользователь перед запуском trend bot должен иметь возможность задать:

- country / countries
- time_window
- top_keywords_limit
- related_videos_per_keyword
- source_types
- min_popularity_change
- language
- product_tags
- mode

Пример:

```json
{
  "name": "BY_7d_top10_ecom",
  "countries": ["Belarus"],
  "time_window": "7d",
  "top_keywords_limit": 10,
  "related_videos_per_keyword": 3,
  "source_types": ["keyword_insights"],
  "min_popularity_change": 20,
  "language": "ru",
  "product_tags": ["ecommerce", "delivery", "promo"],
  "mode": "new_and_growing"
}
```

Создай для этого:
- domain entity
- DB model
- repository
- API CRUD endpoints

## B. KeywordTrend

Это результат сбора keyword-level трендов из TikTok Creative Center Keyword Insights.

Поля минимум:
- id
- job_id
- source
- country
- time_window
- keyword
- rank
- popularity
- popularity_change
- ctr
- keyword_type
- industry
- objective
- details_url
- first_seen_at
- last_seen_at
- collected_at
- raw_payload_json

Пример:

```json
{
  "job_id": "job_001",
  "source": "tiktok_keyword_insights",
  "country": "Belarus",
  "time_window": "7d",
  "keyword": "бесплатная доставка",
  "rank": 1,
  "popularity": 477,
  "popularity_change": 82.19,
  "ctr": 1.2,
  "collected_at": "..."
}
```

## C. RelatedVideo

Для каждого keyword нужно сохранять связанные видео.

Поля минимум:
- id
- keyword_trend_id
- source_platform
- source_url
- creator_name nullable
- thumbnail_url
- storage_path nullable
- overlay_text nullable
- transcript nullable
- duration_sec nullable
- visual_tags_json
- topic_tags_json
- metadata_json
- collected_at

Пример:

```json
{
  "keyword_trend_id": "kt_001",
  "source_platform": "tiktok",
  "source_url": "...",
  "thumbnail_url": "...",
  "overlay_text": "я его хочу",
  "duration_sec": 14.2,
  "visual_tags_json": ["ugc", "product_showcase", "text_overlay"]
}
```

На этом этапе можно не скачивать сами видео полностью, но архитектура должна быть готова к media storage.

## D. ContentCandidate

Это уже внутренняя сущность, которая говорит:
“эта связка keyword + related videos + product context выглядит как хороший кандидат на контент”

Поля минимум:
- id
- job_id
- keyword_trend_id
- candidate_type
- product_relevance_score
- signal_score
- scriptability_score
- recommended_angle
- status
- metadata_json
- created_at

Пример:

```json
{
  "job_id": "job_001",
  "keyword_trend_id": "kt_001",
  "candidate_type": "offer_hook",
  "product_relevance_score": 0.91,
  "signal_score": 0.84,
  "scriptability_score": 0.79,
  "recommended_angle": "promo/free-delivery",
  "status": "candidate"
}
```

## E. GeneratedScript

Эта сущность остаётся, но теперь script генерируется не напрямую от trend, а от `ContentCandidate`.

Нужно изменить модель и связи:
- script должен ссылаться на `content_candidate_id`
- при желании может дополнительно ссылаться на `keyword_trend_id`

---

# Что нужно изменить в пайплайне

Старый пайплайн:
- ingest trends
- process trends
- generate scripts

Новый пайплайн должен быть таким:

### Job 1 — collect_keyword_trends
Берёт активные `TrendSearchJob` и собирает keywords по их параметрам.

### Job 2 — collect_related_videos
Для отобранных keyword trends собирает related videos.

### Job 3 — build_content_candidates
Для keyword + related videos + brand context создаёт `ContentCandidate`.

### Job 4 — generate_scripts
Генерирует scripts только для top candidates.

---

# Источники данных

Нужно ввести abstraction layer под разные trend sources.

## Новый основной source тип
Сейчас главный источник для реального MVP:
- `TikTok Keyword Insights`

Нужно сделать новый adapter, например:
- `TikTokKeywordInsightsSource`

Он должен быть заточен под модель:
- country
- time_window
- top_keywords_limit
- keyword rows
- optional related videos collection

### Важно
Не нужно сейчас обязательно сделать production-perfect live scraper.
Но нужно:
- заложить правильный интерфейс
- сделать mockable / testable adapter
- сделать минимум один working development source

---

# Источники на первом этапе

Обязательно реализовать:

## 1. StaticKeywordInsightsSource
Читает локальный JSON и возвращает keyword trends + optional related videos.
Это должен быть first-class источник для локальной разработки и тестов.

## 2. TikTokKeywordInsightsSource
Адаптер под реальный TikTok Creative Center Keyword Insights.
Можно оставить честные TODO там, где live scraping пока нестабилен, но интерфейс и shape данных должны быть правильными.

---

# Что делать с текущими сущностями Sprint 1

## Сохранить
- config.py
- db.py
- logging.py
- repository pattern
- worker/jobs structure
- API app structure
- template definitions
- template resolver
- fake llm
- script engine idea
- brand context model

## Переработать
- старую сущность `Trend`
- старую таблицу `trends`
- старые process jobs
- старые API endpoints `/trends/ingest` и `/trends/process`

### Что делать со старой таблицей trends
Не использовать её как core entity новой архитектуры.

Разрешено:
- либо удалить и заменить новыми таблицами
- либо оставить как legacy/deprecated table, если это проще для миграции

Но новая архитектура не должна зависеть от старой таблицы `trends`.

---

# Новая структура проекта

Перестрой проект примерно так:

```text
trend2video/
  apps/
    api/
      main.py
      deps.py
      routes/
        health.py
        search_jobs.py
        keyword_trends.py
        related_videos.py
        candidates.py
        scripts.py

    worker/
      jobs/
        collect_keyword_trends.py
        collect_related_videos.py
        build_content_candidates.py
        generate_scripts.py

  core/
    config.py
    db.py
    logging.py

  domain/
    entities/
      brand.py
      search_job.py
      keyword_trend.py
      related_video.py
      content_candidate.py
      script.py
      template.py

    services/
      keyword_trend_scorer.py
      candidate_builder.py
      template_resolver.py
      script_engine.py
      prompt_builder.py

  integrations/
    tiktok/
      keyword_insights_source_base.py
      keyword_insights_source_static.py
      keyword_insights_source_tiktok.py
      schemas.py

    llm/
      base.py
      fake_llm.py

  persistence/
    models/
      search_job.py
      keyword_trend.py
      related_video.py
      content_candidate.py
      script.py
      template.py

    repositories/
      search_job_repository.py
      keyword_trend_repository.py
      related_video_repository.py
      content_candidate_repository.py
      script_repository.py
      template_repository.py

  scripts/
    seed_templates.py

  tests/
    unit/
    integration/
```

Можно слегка улучшить структуру, но сохраняй modularity.

---

# База данных

Нужно создать новые таблицы.

## trend_search_jobs
Поля:
- id
- name
- countries_json
- time_window
- top_keywords_limit
- related_videos_per_keyword
- source_types_json
- min_popularity_change
- language
- product_tags_json
- mode
- is_active
- created_at
- updated_at

## keyword_trends
Поля:
- id
- job_id
- source
- country
- time_window
- keyword
- rank
- popularity
- popularity_change
- ctr
- keyword_type
- industry
- objective
- details_url
- raw_payload_json
- first_seen_at
- last_seen_at
- collected_at
- created_at
- updated_at

Уникальность хотя бы по:
- `(job_id, country, time_window, keyword, collected_at::date)`
или другой разумной стратегии

## related_videos
Поля:
- id
- keyword_trend_id
- source_platform
- source_url
- creator_name
- thumbnail_url
- storage_path
- overlay_text
- transcript
- duration_sec
- visual_tags_json
- topic_tags_json
- metadata_json
- collected_at
- created_at
- updated_at

## content_candidates
Поля:
- id
- job_id
- keyword_trend_id
- candidate_type
- signal_score
- product_relevance_score
- scriptability_score
- recommended_angle
- status
- metadata_json
- created_at
- updated_at

## scripts
Обновить:
- script должен ссылаться на `content_candidate_id`

---

# Конфиг

Нужно расширить `AppSettings`.

Добавь:
- default trend source type for keyword jobs
- optional cookie header
- optional user-agent
- optional storage state path
- media storage base path
- default related_videos_per_keyword
- default top_keywords_limit

Но не переусложняй.

---

# API

Нужно сделать нормальные endpoint’ы.

## Search Jobs
- `POST /search-jobs`
- `GET /search-jobs`
- `GET /search-jobs/{id}`
- `PATCH /search-jobs/{id}`
- `POST /search-jobs/{id}/run-keywords`
- `POST /search-jobs/{id}/run-related-videos`
- `POST /search-jobs/{id}/build-candidates`
- `POST /search-jobs/{id}/generate-scripts`

## Keyword Trends
- `GET /keyword-trends`
- фильтры по:
  - job_id
  - country
  - time_window
  - min_popularity_change

## Related Videos
- `GET /related-videos`
- фильтры по:
  - keyword_trend_id
  - job_id

## Candidates
- `GET /candidates`
- `POST /candidates/{id}/generate-script`

## Scripts
- `GET /scripts`

---

# Repositories

Нужны новые репозитории с минимально нормальными методами.

## SearchJobRepository
- create
- list
- get_by_id
- update
- list_active

## KeywordTrendRepository
- bulk_upsert
- list_for_job
- list_top_for_job
- get_without_related_videos
- list_candidate_ready

## RelatedVideoRepository
- bulk_insert
- list_for_keyword_trend
- exists_for_keyword_trend

## ContentCandidateRepository
- create_many
- list_for_job
- get_top_candidates
- mark_status

## ScriptRepository
- create_for_candidate
- get_by_candidate_id
- list_all

---

# Services

## KeywordTrendScorer
Нужно оценивать:
- signal strength
- growth
- product relevance
- keyword usefulness

## CandidateBuilder
Из:
- keyword trend
- related videos
- brand context

строит content candidates.

Можно использовать эвристики на первом этапе:
- keywords containing “free”, “delivery”, “sale”, etc.
- video overlays
- product tags matching

Но код должен быть расширяемым.

## ScriptEngine
Теперь принимает:
- `ContentCandidate`
- optional related videos context
- template
- brand context

И возвращает `GeneratedScript`.

---

# Тесты

Нужно переписать тесты под новую модель.

Минимум нужны:

## Unit
- search job validation
- keyword trend scorer
- candidate builder
- script engine
- static source parsing

## Integration
- create search job
- collect keyword trends from static source
- collect related videos from static source
- build candidates
- generate scripts
- full flow end-to-end

---

# Seed data

Оставить seed templates.
При желании можно добавить sample static keyword insights dataset для тестов/локальной разработки.

---

# README

Переписать README под новую архитектуру.

Нужно описать:
- что теперь такое search job
- как запустить collection keywords
- как собрать related videos
- как построить candidates
- как сгенерировать scripts
- что live TikTok source пока может быть нестабилен
- что Static source является официальным dev fallback

---

# Важные требования

1. Не делай superficial patch. Это должен быть реальный refactor.
2. Не ломай модульность.
3. Не прячь технический долг — помечай TODO честно.
4. Не выдумывай рабочий live scraper, если его нельзя честно гарантировать.
5. Делай код так, чтобы следующим спринтом можно было добавить:
   - video download
   - asset storage
   - vector similarity
   - rendering
   - review workflow
   - publishing
6. Не используй no-code.
7. Не удаляй без причины то, что можно переиспользовать.
8. Не пиши псевдокод там, где можно дать реальный код.

---

# Формат результата

Выдай результат в таком порядке:

1. Refactor plan
2. Updated directory structure
3. Migration strategy
4. Code files one by one
5. Commands to run locally
6. Example API flows
7. What remains for Sprint 2

Если код длинный, показывай по файлам, например:

```python
# file: trend2video/domain/entities/search_job.py
...
```

---

# Финальный критерий готовности

Считай задачу выполненной, если:

- можно создать `TrendSearchJob`
- можно собрать keyword trends из static source
- можно собрать related videos
- можно построить content candidates
- можно сгенерировать script из candidate
- тесты под новый flow проходят
- README отражает новую модель
- проект архитектурно готов к Sprint 2

---

# Короткая версия задачи для Codex в одну фразу

Refactor the current Sprint 1 from a flat `Trend -> Script` pipeline into a configurable `TrendSearchJob -> KeywordTrend -> RelatedVideo -> ContentCandidate -> Script` backend architecture, preserving reusable foundations but replacing the domain model, persistence layer, jobs, APIs, and tests accordingly.
