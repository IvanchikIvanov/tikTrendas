# trend2video Trend Discovery Foundation v2

Backend for trend discovery and script generation built around the pipeline:

`TrendSearchJob -> KeywordTrend -> RelatedVideo -> ContentCandidate -> Script`

The old flat `Trend -> Script` Sprint 1 flow is no longer the core architecture. FastAPI, worker jobs, repositories, config, DB wiring, template resolver, and fake LLM remain, but the domain model now reflects the real TikTok Creative Center discovery workflow.

## Core concepts

- `TrendSearchJob`: configurable search specification with countries, time window, limits, source types, language, product tags, and mode.
- `KeywordTrend`: keyword-level signal collected from Keyword Insights.
- `RelatedVideo`: reference videos linked to a keyword trend.
- `ContentCandidate`: internal content opportunity built from keyword + video evidence + brand context.
- `GeneratedScript`: downstream script generated from a content candidate, not directly from a flat trend row.

## Sources

- `StaticKeywordInsightsSource`: official dev/test fallback. Reads local JSON and supports keyword trends plus related videos.
- `TikTokKeywordInsightsSource`: live adapter skeleton for TikTok Keyword Insights. Interface is production-shaped, but the live implementation is intentionally conservative and still marked with TODOs where scraping is unstable.

## Project structure

```text
trend2video/
  apps/
    api/
      deps.py
      main.py
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
    services/
  integrations/
    llm/
    tiktok/
  persistence/
    models/
    repositories/
  data/
    static_keyword_insights.json
  tests/
    unit/
    integration/
```

## Key configuration

Main env vars:

- `T2V_DATABASE_URL`
- `T2V_DEFAULT_KEYWORD_SOURCE_TYPE` = `static` or `tiktok_keyword_insights`
- `T2V_STATIC_KEYWORD_INSIGHTS_PATH`
- `T2V_DEFAULT_TOP_KEYWORDS_LIMIT`
- `T2V_DEFAULT_RELATED_VIDEOS_PER_KEYWORD`
- `T2V_TIKTOK_COOKIE_HEADER`
- `T2V_TIKTOK_USER_AGENT`
- `T2V_TIKTOK_STORAGE_STATE_PATH`
- `T2V_MEDIA_STORAGE_BASE_PATH`

## Local setup

1. Install dependencies.

```bash
poetry install
```

2. Apply migrations or create schema in your target DB.

```bash
poetry run alembic upgrade head
```

3. Seed templates.

```bash
poetry run python -m trend2video.scripts.seed_templates
```

4. Run the API.

```bash
poetry run uvicorn trend2video.apps.api.main:app --reload
```

## Worker commands

Collect keyword trends:

```bash
poetry run python -m trend2video.apps.worker.jobs.collect_keyword_trends
```

Collect related videos:

```bash
poetry run python -m trend2video.apps.worker.jobs.collect_related_videos
```

Build content candidates:

```bash
poetry run python -m trend2video.apps.worker.jobs.build_content_candidates
```

Generate scripts:

```bash
poetry run python -m trend2video.apps.worker.jobs.generate_scripts
```

## API flow

Create a search job:

```bash
curl -X POST http://localhost:8000/search-jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "BY_7d_top10_ecom",
    "countries": ["Belarus"],
    "time_window": "7d",
    "top_keywords_limit": 10,
    "related_videos_per_keyword": 3,
    "source_types": ["static"],
    "min_popularity_change": 20,
    "language": "ru",
    "product_tags": ["ecommerce", "delivery", "promo"],
    "mode": "new_and_growing",
    "is_active": true
  }'
```

Run the discovery stages:

```bash
curl -X POST http://localhost:8000/search-jobs/1/run-keywords
curl -X POST http://localhost:8000/search-jobs/1/run-related-videos
curl -X POST http://localhost:8000/search-jobs/1/build-candidates
curl -X POST http://localhost:8000/search-jobs/1/generate-scripts
```

Inspect outputs:

```bash
curl "http://localhost:8000/keyword-trends?job_id=1"
curl "http://localhost:8000/related-videos?job_id=1"
curl "http://localhost:8000/candidates?job_id=1"
curl "http://localhost:8000/scripts"
```

Generate a script for one candidate explicitly:

```bash
curl -X POST http://localhost:8000/candidates/1/generate-script
```

## Testing

The repository ships with a static keyword insights dataset and SQLite-backed unit/integration tests for the v2 flow.

```bash
PYTHONPATH=. pytest tests/unit tests/integration -q
```

## Current limitations

- Live TikTok Keyword Insights scraping is still unstable and intentionally not presented as production-ready.
- Media download/storage is not implemented yet, but the `RelatedVideo.storage_path` and `media_storage_base_path` hooks are in place.
- The legacy `trends` table and old Sprint 1 files may still exist for migration continuity, but the v2 architecture does not depend on them.

## Sprint 2 direction

- Video download and asset storage
- Vector similarity and candidate ranking improvements
- Rendering
- Review workflow
- Publishing pipeline
