# MASTER_PLAN.md

## Current version

- App version: `0.2.0`
- Source of truth checked in code: [trend2video/apps/api/main.py](/root/Trendas/tikTrendas/trend2video/apps/api/main.py#L18)
- Migration state in repo: `0001` -> `0002` -> `0003`

This plan is based on the current repository state on `2026-03-09`, not the older Sprint 1-only architecture.

---

## Product goal

The backend should support one production pipeline with two entry points:

1. Automatic trend discovery
2. Manual trend intake

Both should converge into:

`ContentCandidate -> Script -> RenderJob -> ReviewRequest -> PublishJob`

---

## Current architecture

### Automatic path
`TrendSearchJob -> KeywordTrend -> RelatedVideo -> ContentCandidate -> Script`

### Manual path
`ManualTrendInput -> ManualTrendReference -> ContentCandidate -> Script -> RenderJob -> ReviewRequest -> PublishJob`

### Shared downstream entities
- `ContentCandidate`
- `GeneratedScript`
- `Asset`
- `RenderJob`
- `ReviewRequest`
- `PublishJob`

---

## Status summary

### Completed
- FastAPI app and route surface for search jobs, keyword trends, related videos, candidates, scripts, manual trends, assets, renders, review requests, and publish jobs
- Repository/model/domain structure
- Alembic schema through manual trend + render/review/publish pipeline
- Automatic trend discovery flow with static and `tiktok_http` keyword sources
- Manual trend intake plus manual candidate builder
- Script generation from candidates
- Template seeding and render manifest builder
- Real FFmpeg-backed render engine
- Review request approve/reject API
- Publish job scaffold API
- Integration tests for automatic discovery flow and manual end-to-end flow

### Partially complete
- Live TikTok HTTP ingestion works, but depends on fresh browser session headers
- Rendering is real, but still template/basic-scene driven rather than a mature media pipeline
- Publish flow exists as a model/API scaffold only
- Review flow exists as API state management only

### Not complete
- Telegram review delivery
- Real TikTok publishing integration
- Media download/enrichment pipeline for related videos
- Production retries, metrics, observability, and orchestration
- Historical ranking feedback, clustering, and similarity search
- Cleanup of legacy trend flow leftovers
- README and config docs fully aligned with current architecture

---

## Evidence checked in code

### Current version
- FastAPI app declares `version="0.2.0"` in [trend2video/apps/api/main.py](/root/Trendas/tikTrendas/trend2video/apps/api/main.py#L18)

### Automatic flow exists
- Search job routes trigger keyword collection, related video collection, candidate building, and script generation in [trend2video/apps/api/routes/search_jobs.py](/root/Trendas/tikTrendas/trend2video/apps/api/routes/search_jobs.py#L1)
- End-to-end automatic flow test exists in [tests/integration/test_trend_discovery_flow.py](/root/Trendas/tikTrendas/tests/integration/test_trend_discovery_flow.py#L1)

### Manual flow exists
- Manual trend CRUD and candidate build route exists in [trend2video/apps/api/routes/manual_trends.py](/root/Trendas/tikTrendas/trend2video/apps/api/routes/manual_trends.py#L1)
- End-to-end manual flow through review/publish exists in [tests/integration/test_manual_trend_flow.py](/root/Trendas/tikTrendas/tests/integration/test_manual_trend_flow.py#L1)

### Render pipeline exists
- Render route creates a job and runs the worker in [trend2video/apps/api/routes/renders.py](/root/Trendas/tikTrendas/trend2video/apps/api/routes/renders.py#L1)
- Render worker builds a manifest and executes rendering in [trend2video/apps/worker/jobs/render_drafts.py](/root/Trendas/tikTrendas/trend2video/apps/worker/jobs/render_drafts.py#L1)
- FFmpeg-backed engine exists in [trend2video/domain/services/render_engine.py](/root/Trendas/tikTrendas/trend2video/domain/services/render_engine.py#L1) and [trend2video/integrations/media/ffmpeg_runner.py](/root/Trendas/tikTrendas/trend2video/integrations/media/ffmpeg_runner.py#L1)

### Review and publish scaffolding exists
- Review request routes exist in [trend2video/apps/api/routes/review_requests.py](/root/Trendas/tikTrendas/trend2video/apps/api/routes/review_requests.py#L1)
- Publish job routes exist in [trend2video/apps/api/routes/publish_jobs.py](/root/Trendas/tikTrendas/trend2video/apps/api/routes/publish_jobs.py#L1)

### Live TikTok HTTP source exists
- HTTP adapter exists in [trend2video/integrations/tiktok/keyword_insights_source_tiktok.py](/root/Trendas/tikTrendas/trend2video/integrations/tiktok/keyword_insights_source_tiktok.py#L1)
- Unit coverage exists in [tests/unit/test_tiktok_keyword_http_source.py](/root/Trendas/tikTrendas/tests/unit/test_tiktok_keyword_http_source.py#L1)

### Schema reflects current pipeline
- Manual trend/render/review/publish migration exists in [alembic/versions/0003_manual_trends_render_pipeline.py](/root/Trendas/tikTrendas/alembic/versions/0003_manual_trends_render_pipeline.py#L1)

---

## Current MVP definition

### MVP already implemented in code
1. Create a manual trend
2. Build a content candidate
3. Generate a script
4. Create a render job and render a draft
5. Create and approve a review request
6. Create a publish job scaffold

### Automatic discovery MVP also implemented
1. Create a search job
2. Collect keyword trends
3. Collect related videos
4. Build candidates
5. Generate scripts

---

## Main risks right now

- `tiktok_http` depends on expiring cookies and session headers
- FFmpeg rendering requires valid local media assets and `ffmpeg` in `PATH`
- No real media ingestion pipeline populates assets from discovered videos
- Review and publish stages stop at internal state transitions
- Legacy `Trend` / old route pieces still exist and can confuse the canonical model

---

## Next plan

## Phase 1: Stabilize the current backend
- Align `README.md`, config docs, and environment examples with the current `0.2.0` architecture
- Remove or clearly mark legacy `Trend` flow files/routes as deprecated
- Add one smoke test path that exercises render creation with the real worker boundary
- Add validation around missing assets, templates, and render prerequisites

## Phase 2: Make review and publish useful
- Add `needs_changes` review transition endpoint
- Add render-to-review payload formatting that is ready for Telegram or dashboard delivery
- Add publish job state transitions beyond creation
- Define a publisher interface so TikTok publishing can be implemented without route churn

## Phase 3: Strengthen media and discovery reliability
- Build media download/storage for discovered or manual references
- Enrich related videos with durable metadata beyond URL/id
- Add retry/logging/metrics around `tiktok_http`
- Add health checks or diagnostics for expired TikTok session configuration

## Phase 4: Production hardening
- Background worker orchestration instead of direct inline job execution from routes
- Better observability, structured error reporting, and idempotent job handling
- Asset storage strategy and cleanup lifecycle
- Ranking improvements using feedback/history

---

## Recommended implementation order

1. Documentation and canonical architecture cleanup
2. Legacy flow cleanup or deprecation markers
3. Render/review/publish validation and state-machine tightening
4. Telegram review integration
5. TikTok publisher interface and stub worker
6. Media ingestion/storage for assets and related videos
7. Live-source hardening and observability
8. Ranking and intelligence improvements

---

## Verification notes

- I verified the current version from code, not from the old plan text.
- I could not run the test suite directly because `pytest` is not installed in the current shell environment.
- The previous `MASTER_PLAN.md` was untracked in git and has now been replaced with a current-state plan.
