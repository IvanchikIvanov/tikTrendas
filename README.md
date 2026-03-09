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
- `TikTokKeywordInsightsSource`: preferred live keyword ingestion path. Uses the observed TikTok Creative Center JSON endpoint at `https://ads.tiktok.com/creative_radar_api/v1/script/keyword/list` via `httpx.AsyncClient`.
- `CreativeCenterTrendSource`: older Playwright DOM source for the legacy trend feed. It still exists in the repo, but it is experimental and is not the preferred keyword insights path.

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

Use [`.env.example`](/root/Trendas/tikTrendas/.env.example) as the recommended local template:

```bash
cp .env.example .env
```

The template keeps shell-sensitive values quoted so it is safe both for dotenv loading and for `source .env` in `bash`. Keep those quotes in place when editing local values.

Main env vars from `trend2video/core/config.py`:

- `T2V_ENV`
- `T2V_DATABASE_URL`
- `T2V_TREND_SOURCE` = `static` or `creative_center`
- `T2V_STATIC_TRENDS_PATH`
- `T2V_DEFAULT_KEYWORD_SOURCE_TYPE` = `static` or `tiktok_http`
- `T2V_STATIC_KEYWORD_INSIGHTS_PATH`
- `T2V_DEFAULT_TOP_KEYWORDS_LIMIT`
- `T2V_DEFAULT_RELATED_VIDEOS_PER_KEYWORD`
- `T2V_TIKTOK_CREATIVE_CENTER_URL`
- `T2V_TIKTOK_REGION`
- `T2V_TIKTOK_COOKIE_HEADER`
- `T2V_TIKTOK_USER_AGENT`
- `T2V_TIKTOK_REFERER`
- `T2V_TIKTOK_ACCEPT_LANGUAGE`
- `T2V_TIKTOK_EXTRA_HEADERS_JSON`
- `T2V_TIKTOK_STORAGE_STATE_PATH`
- `T2V_MEDIA_STORAGE_BASE_PATH`
- `T2V_BRAND_CONTEXT` as a JSON object if you want to override the built-in default brand profile

For live keyword ingestion, `T2V_DEFAULT_KEYWORD_SOURCE_TYPE=tiktok_http` or `source_types=["tiktok_http"]` selects the HTTP adapter. If `source_types` is omitted on a job, the worker uses `T2V_DEFAULT_KEYWORD_SOURCE_TYPE` and logs that fallback explicitly. Static JSON remains the official fallback for local development and tests.

Example live config:

```bash
cp .env.example .env
# then edit .env and keep shell-sensitive values quoted:
T2V_DEFAULT_KEYWORD_SOURCE_TYPE=tiktok_http
T2V_TIKTOK_COOKIE_HEADER='sessionid_ads=example_session_cookie; msToken=example_ms_token'
T2V_TIKTOK_USER_AGENT='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
T2V_TIKTOK_REFERER='https://ads.tiktok.com/business/creativecenter/keyword-insights/pc/en'
T2V_TIKTOK_ACCEPT_LANGUAGE='en-US,en;q=0.9'
T2V_TIKTOK_EXTRA_HEADERS_JSON='{"x-csrftoken":"example_csrf_token"}'
```

Cookies and session-bound headers expire. When the live source starts returning non-zero response codes or empty data, refresh the browser session values instead of hardcoding them into the repository.

## Local setup

1. Install dependencies.

```bash
poetry install
```

2. Create a local env file from the template and adjust values as needed.

```bash
cp .env.example .env
```

3. Apply migrations or create schema in your target DB.

```bash
poetry run alembic upgrade head
```

That upgrade now includes the v2 trend-discovery schema (`trend_search_jobs`, `keyword_trends`, `related_videos`, `content_candidates`) and migrates `scripts` to `content_candidate_id`.

4. Seed templates.

```bash
poetry run python -m trend2video.scripts.seed_templates
```

5. Run the API.

```bash
poetry run uvicorn trend2video.apps.api.main:app --reload
```

## Worker commands

Collect keyword trends:

```bash
poetry run python -m trend2video.apps.worker.jobs.collect_keyword_trends
```

Run just the live source tests:

```bash
PYTHONPATH=. pytest tests/unit/test_tiktok_keyword_http_source.py -q
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

- The live keyword source depends on TikTok session headers. Cookie and CSRF-style values are not durable and must be refreshed manually.
- `video_list` currently provides the first live evidence for `RelatedVideo`, but only TikTok video IDs are available from this endpoint. The adapter maps them into deterministic video URLs and preserves the raw IDs in `metadata_json`.
- Media download/storage is not implemented yet, but the `RelatedVideo.storage_path` and `media_storage_base_path` hooks are in place.
- The legacy `trends` table and old Sprint 1 files may still exist for migration continuity, but the v2 architecture does not depend on them.

## Sprint 2 direction

- Video download and asset storage
- Vector similarity and candidate ranking improvements
- Rendering
- Review workflow
- Publishing pipeline
