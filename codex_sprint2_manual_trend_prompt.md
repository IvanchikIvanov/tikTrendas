Ты senior Python backend engineer и solution architect.
Работаешь в существующем репозитории `trend2video`.

## Контекст проекта

Сейчас в проекте уже есть v2 foundation:

`TrendSearchJob -> KeywordTrend -> RelatedVideo -> ContentCandidate -> Script`

Но live automatic trend discovery через TikTok пока нестабилен, поэтому на Sprint 2 мы переходим к рабочему промежуточному режиму:

## Новый продуктовый режим

Я нахожу тренды вручную, вношу их в систему, а система дальше делает всё остальное:

`ManualTrendInput -> ContentCandidate -> Script -> RenderDraft -> ReviewRequest -> PublishJob`

### Важно
Не нужно ломать v2 архитектуру.
Нужно добавить новый входной контур для ручного ввода тренда, чтобы downstream pipeline переиспользовал уже существующие сущности и сервисы там, где это разумно.

---

# Цель Sprint 2

Сделать систему, в которой пользователь может:

1. вручную добавить найденный тренд
2. прикрепить related video references / notes / hook ideas
3. превратить это в `ContentCandidate`
4. сгенерировать `GeneratedScript`
5. собрать draft video из шаблонов и заранее заготовленных ассетов
6. создать `ReviewRequest`
7. подготовить систему к будущему publish flow

### Что должно получиться после Sprint 2
Реально работающий flow:

manual trend input -> candidate -> script -> render draft

Review и publish можно сделать как минимальную архитектуру/заготовку, но render draft должен быть реальным и usable.

---

# Стратегия Sprint 2

Разбить работу на 3 логических слоя внутри одного спринта:

## Sprint 2A
Manual trend intake + candidate + script

## Sprint 2B
Template-based render draft from prepared assets

## Sprint 2C
Review queue + publish job scaffolding

---

# Важные архитектурные требования

1. Не ломай текущую v2 доменную модель.
2. Добавь новый входной контур для ручных трендов.
3. Не дублируй pipeline, если можно переиспользовать `ContentCandidate`, `GeneratedScript`, `TemplateDefinition`.
4. Не делай no-code.
5. Не делай фейковый renderer — нужен реальный draft render pipeline на FFmpeg.
6. Не обещай production-grade TikTok publishing в этом спринте, но подготовь data model и job structure.
7. Код должен быть расширяемым под:
   - automatic trend ingestion
   - Telegram review
   - TikTok publish
   - Instagram / Shorts later

---

# Что нужно реализовать

## 1. Manual Trend Input domain

Добавь новую сущность:

## `ManualTrendInput`

Она представляет тренд, который пользователь нашёл руками.

Минимальные поля:
- id
- title
- trend_type
- country
- time_window
- notes
- reference_hook_texts
- related_video_urls
- manual_tags
- priority
- status
- created_at
- updated_at

Пример:

```json
{
  "title": "for free",
  "trend_type": "keyword",
  "country": "Belarus",
  "time_window": "7d",
  "notes": "можно адаптировать под бесплатную доставку или бесплатный аудит",
  "reference_hook_texts": [
    "try it for free",
    "get it for free"
  ],
  "related_video_urls": [
    "https://www.tiktok.com/@demo/video/123",
    "https://www.tiktok.com/@demo/video/456"
  ],
  "manual_tags": ["offer", "promo", "ecommerce"],
  "priority": 1,
  "status": "new"
}
```

### Нужно создать
- domain entity
- ORM model
- repository
- CRUD API endpoints

---

## 2. Manual Trend Reference data

Если related videos передаются не просто как URL-строки, а как отдельные reference objects, добавь отдельную сущность:

## `ManualTrendReference`

Поля:
- id
- manual_trend_input_id
- source_platform
- source_url
- hook_text nullable
- notes nullable
- metadata_json
- created_at

Это допустимо как отдельная таблица, если так чище.

Если решишь, что это удобнее хранить в JSON в самой manual trend сущности — обоснуй, но prefer explicit table if it helps future extension.

---

## 3. Candidate building from manual trends

Нужно сделать сервис:

## `ManualTrendCandidateBuilder`

Он принимает:
- `ManualTrendInput`
- optional related references
- `BrandContext`

И строит `ContentCandidate`.

Логика на первом этапе может быть эвристической:
- manual tags
- notes
- reference hooks
- product tags
- trend_type
- keyword phrases

Нужно посчитать хотя бы:
- product_relevance_score
- signal_score
- scriptability_score
- recommended_angle
- candidate_type

### Важно
Не генерируй script сразу в API route.
Сначала всегда создавай `ContentCandidate`.

---

## 4. Script generation from manual candidates

Текущий `ScriptEngine` нужно адаптировать так, чтобы он умел работать с candidate, пришедшим из:
- keyword trend pipeline
- manual trend pipeline

Нужно:
- не ломать существующий контракт, если он уже есть
- расширить prompt building
- использовать `reference_hook_texts`, `notes`, `manual_tags`, `related_video_urls` как дополнительный контекст

Результат:
- `GeneratedScript`
- с привязкой к `content_candidate_id`

---

## 5. Template-based render draft

Это главный новый модуль спринта.

Нужно реализовать реальный renderer, который собирает черновое вертикальное видео из заранее подготовленных ассетов и script/template данных.

### Компоненты

#### A. Asset Registry
Добавь сущность/слой для описания доступных ассетов.

Минимум:
- id
- asset_type
- asset_tag
- path
- duration_sec
- metadata_json
- active

Типы ассетов:
- broll
- ugc
- screenrec
- outro
- music
- sfx
- image

Можно хранить в БД или в конфиге + registry loader.
Но prefer structured persistent model, если это не слишком тяжело.

#### B. RenderJob
Сущность:
- id
- content_candidate_id
- script_id
- template_id
- status
- render_manifest_json
- output_path
- preview_path nullable
- error nullable
- created_at
- updated_at

#### C. RenderOutput
Если удобно отделить output от job — можно, но не обязательно.
Если не нужно, достаточно `RenderJob`.

### Render pipeline
Нужно:
1. взять template
2. подобрать ассеты по `scene_plan`
3. построить render manifest
4. собрать draft через FFmpeg
5. сохранить output path
6. вернуть сущность render job

### Допустимый MVP render
Можно сделать:
- 1080x1920
- 30 fps
- нарезка сцен
- overlay text
- simple subtitles or text overlays
- optional background music
- end card

### Важно
Это не должен быть псевдо-renderer.
Нужен рабочий FFmpeg-based pipeline.

---

## 6. Review layer scaffold

Нужно подготовить архитектуру review, даже если Telegram не делаем полностью сейчас.

Добавь сущность:

## `ReviewRequest`
Поля:
- id
- render_job_id
- channel_type
- status
- reviewer
- review_comment
- created_at
- reviewed_at

Статусы:
- pending
- approved
- rejected
- needs_changes

### Для Sprint 2
Достаточно:
- API endpoint создать review request
- API endpoint approve/reject
- downstream data model
- без реальной Telegram интеграции, если не успеваешь

Но если хочешь сделать минимальный Telegram scaffold — можно, без полного publish.

---

## 7. Publish scaffold

Подготовь сущность:

## `PublishJob`
Поля:
- id
- render_job_id
- target_platform
- status
- payload_json
- result_json
- scheduled_at nullable
- created_at
- updated_at

Статусы:
- pending
- ready
- published
- failed

Для Sprint 2 publishing реально можно не делать, но data model и API scaffold нужны.

---

# Новые API endpoints

## Manual Trends
- `POST /manual-trends`
- `GET /manual-trends`
- `GET /manual-trends/{id}`
- `PATCH /manual-trends/{id}`

## Candidate building
- `POST /manual-trends/{id}/build-candidate`

Можно разрешить:
- либо один candidate на manual trend
- либо несколько вариантов

## Script generation
- `POST /candidates/{id}/generate-script`

Если уже есть — адаптируй под новый flow.

## Render
- `POST /renders`
- `GET /renders`
- `GET /renders/{id}`

Или:
- `POST /scripts/{id}/render`

Но лучше иметь явную сущность `RenderJob`.

## Review
- `POST /renders/{id}/review-request`
- `POST /review-requests/{id}/approve`
- `POST /review-requests/{id}/reject`

## Publish scaffold
- `POST /renders/{id}/publish-jobs`
- `GET /publish-jobs`

---

# Новая структура проекта

Перестрой/расширь проект примерно так:

```text
trend2video/
  apps/
    api/
      routes/
        manual_trends.py
        renders.py
        review_requests.py
        publish_jobs.py

    worker/
      jobs/
        build_manual_candidates.py
        generate_scripts.py
        render_drafts.py
        create_review_requests.py

  domain/
    entities/
      manual_trend.py
      manual_trend_reference.py
      render_job.py
      review_request.py
      publish_job.py
      asset.py

    services/
      manual_trend_candidate_builder.py
      render_manifest_builder.py
      render_engine.py
      asset_selector.py

  integrations/
    media/
      ffmpeg_runner.py
      subtitle_builder.py
      manifest_builder.py

  persistence/
    models/
      manual_trend.py
      manual_trend_reference.py
      render_job.py
      review_request.py
      publish_job.py
      asset.py

    repositories/
      manual_trend_repository.py
      render_job_repository.py
      review_request_repository.py
      publish_job_repository.py
      asset_repository.py
```

Можно улучшить, но структура должна остаться модульной.

---

# База данных

Добавь новые таблицы:

## manual_trend_inputs
- id
- title
- trend_type
- country
- time_window
- notes
- reference_hook_texts_json
- related_video_urls_json
- manual_tags_json
- priority
- status
- created_at
- updated_at

## manual_trend_references
(если делаешь отдельной таблицей)
- id
- manual_trend_input_id
- source_platform
- source_url
- hook_text
- notes
- metadata_json
- created_at

## assets
- id
- asset_type
- asset_tag
- path
- duration_sec
- metadata_json
- is_active
- created_at
- updated_at

## render_jobs
- id
- content_candidate_id
- script_id
- template_id
- status
- render_manifest_json
- output_path
- preview_path
- error
- created_at
- updated_at

## review_requests
- id
- render_job_id
- channel_type
- status
- reviewer
- review_comment
- created_at
- reviewed_at

## publish_jobs
- id
- render_job_id
- target_platform
- status
- payload_json
- result_json
- scheduled_at
- created_at
- updated_at

Также создай Alembic migration для этих таблиц.

---

# Render details

Нужно заложить реальную механику сборки видео.

## Required render behavior
- 9:16 vertical output
- use template scene_plan
- select assets by asset_type + asset_tag
- overlay generated text from script
- output mp4
- save path in `render_jobs.output_path`

## Minimal FFmpeg support
- concat clips
- scale/crop to 1080x1920
- drawtext overlays
- optional music bed
- optional fade in/out
- end card

## Configuration
Добавь в config:
- render_output_base_path
- asset_library_base_path
- ffmpeg_binary
- default_video_width
- default_video_height
- default_video_fps

---

# Asset strategy

Добавь seed or sample assets manifest for development.

Нужно хотя бы:
- sample asset registry data
- sample template-compatible asset tags
- development-safe paths

Если реальных media файлов нет, можно использовать placeholders/sample mp4 or image assets, но renderer должен быть рабочим.

---

# Tests

Нужны новые тесты.

## Unit
- manual trend validation
- manual trend candidate builder
- asset selection
- render manifest builder
- script engine with manual trend context

## Integration
- create manual trend
- build candidate from manual trend
- generate script
- create render job
- render job produces output path
- create review request
- approve/reject review request

Если полноценный FFmpeg integration test слишком тяжёлый, сделай:
- один lightweight real render test
- остальные тесты через mocked ffmpeg runner

---

# README

Перепиши README под Sprint 2 flow.

Нужно описать:
- manual trend workflow
- how to create a manual trend
- how to build candidate
- how to generate script
- how to render draft
- where outputs are saved
- what review/publish scaffolding already does
- what still belongs to future sprint

---

# Что не нужно делать сейчас

- не делать полноценный production TikTok publisher
- не делать Instagram integration
- не делать perfect automatic trend crawler
- не делать overengineered UI
- не делать full vector search yet, but architecture may anticipate it

---

# Что должно получиться в конце

После Sprint 2 должно быть возможно:

1. вручную создать trend input
2. из него получить candidate
3. из candidate получить script
4. из script + template + assets получить draft video file
5. создать review request
6. отметить approve/reject через API
7. видеть publish job scaffold

---

# Формат ответа

Выдай результат в таком порядке:

1. Sprint 2 implementation plan
2. Updated architecture
3. Migration strategy
4. Code files one by one
5. Test plan and tests
6. How to run locally
7. Example API flow from manual trend to render
8. Remaining technical debt / Sprint 3 direction

---

# Acceptance criteria

Считай задачу выполненной, если:

- можно создать manual trend
- можно построить candidate из manual trend
- можно сгенерировать script
- можно создать render job
- render job реально производит draft output file
- можно создать review request и менять его статус
- есть publish job scaffold
- есть Alembic migration
- есть тесты
- README отражает Sprint 2 flow

---

# Короткая версия задачи

Implement Sprint 2 around a manual trend input workflow:
`ManualTrendInput -> ContentCandidate -> Script -> RenderDraft -> ReviewRequest -> PublishJob`,
with a real FFmpeg-based draft renderer and reusable architecture for later Telegram review and TikTok publishing.
