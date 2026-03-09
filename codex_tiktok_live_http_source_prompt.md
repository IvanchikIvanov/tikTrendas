You are working in the existing `trend2video` repository, which has already been refactored to the v2 architecture:

TrendSearchJob -> KeywordTrend -> RelatedVideo -> ContentCandidate -> Script

Now implement the next step: a real live TikTok Keyword Insights HTTP source based on an observed Creative Center network endpoint, instead of relying on DOM scraping.

## Goal

Implement a live source adapter that pulls keyword trend data from TikTok Creative Center using the observed JSON endpoint:

GET https://ads.tiktok.com/creative_radar_api/v1/script/keyword/list

Make this the preferred live ingestion path for keyword trends.

## Observed endpoint details

Base URL:
https://ads.tiktok.com/creative_radar_api/v1/script/keyword/list

Observed query params:
- page
- limit
- period
- country_code
- order_by
- order_type

Observed example request:
GET https://ads.tiktok.com/creative_radar_api/v1/script/keyword/list?page=1&limit=20&period=7&country_code=BY&order_by=post&order_type=desc

## Observed request session data

Cookie header:
_tea_utm_cache_1988='{"utm_source":"chatgpt.com"}'; _tea_utm_cache_3874='{"utm_source":"chatgpt.com"}'; cookie-consent='{"optional":true,"ga":true,"af":true,"fbp":true,"lip":true,"bing":true,"ttads":true,"reddit":true,"hubspot":true,"version":"v10"}'; csrftoken=""; g_state='{"i_l":1,"i_ll":1773069675651,"i_b":"QEh58TDE+JOIW/rNlJMxhT8cOFTIpMwNeiZol0xCTdo","i_e":{"enable_itp_optimization":15}}'; lang_type="en"; msToken="rfWKb100hcxExDxFlmtdASTGibJPFx1qXu07YvGWHe-mrQMXP89eCMfgPzAyddGKnu-8nD0xsgE8C-X2YcpvWCpVfYQovysWY2Foj2Yy-ZRGfHhnqY_I6CVWzfRz"; odin_tt="56cbe03dd69b64b8ddbc0845dad522232c3870fc4319442917acd0a828616a80a3c3a9f404c454adaa0070621066d5b85ca4a7a877292d060368a8d2ef173e57"; part="stable"; passport_auth_status_ads="d8ceb9ad381b3a07bed93a47420fb356,"; passport_auth_status_ss_ads="d8ceb9ad381b3a07bed93a47420fb356,"; passport_csrf_token="701e4296538ff3546ae3d3bce59bb6d8"; passport_csrf_token_default="701e4296538ff3546ae3d3bce59bb6d8"; pre_country="US"; s_v_web_id="verify_mmjbwmfz_NmYbdFqX_lZSA_4dtv_9D7M_NVn2q1kXovPp"; sessionid_ads="93681ebf88b5a8d7d63c86c6104ac4be"; sessionid_ss_ads="93681ebf88b5a8d7d63c86c6104ac4be"; sid_guard_ads="93681ebf88b5a8d7d63c86c6104ac4be|1773069689|259200|Thu,+12-Mar-2026+15:21:29+GMT"; sid_tt_ads="93681ebf88b5a8d7d63c86c6104ac4be"; sid_ucp_sso_v1_ads="1.0.1-KGY5Y2UxZjIxOWExN2YzMWU4MTQ0YjY0ZDMzYzdmOWU4NzUwZGE4NzQKFwiSiJq2mKy512kQ-cq7zQYYzCQ4CEASEAMaAm15IiBiMmQ3NjFhMTljN2ZmNWZkNzJiOTBlMjI4YzQ1MzM0ODJOCiBh4GHOjiP--If8CynoNsOxPrp2ujs2LdxfRzvjkEDR8BIgXEsHVBY5wPxOx2uKt8fDT-AEj2ru3LrXtG23ENZQJa0YBCIGdGlrdG9r"; sid_ucp_v1_ads="1.0.1-KDZmNTViMDYyMTZlNjIyN2U2NDQwNGQzYmY0MDA5YWM5MDQ0Yjg1ZTEKFwiSiJq2mKy512kQ-cq7zQYYzCQ4CEASEAMaAm15IiA5MzY4MWViZjg4YjVhOGQ3ZDYzYzg2YzYxMDRhYzRiZTJOCiAUEyZiQBSyTR0Pq-RVjJ_E3hBSVVjy3d9abJbStjhZ9RIgY_KkSwBIPyfF8o_Q9Go1qI61YCKujNaPhrHAsh47JQQYBCIGdGlrdG9r"; ssid_ucp_sso_v1_ads="1.0.1-KGY5Y2UxZjIxOWExN2YzMWU4MTQ0YjY0ZDMzYzdmOWU4NzUwZGE4NzQKFwiSiJq2mKy512kQ-cq7zQYYzCQ4CEASEAMaAm15IiBiMmQ3NjFhMTljN2ZmNWZkNzJiOTBlMjI4YzQ1MzM0ODJOCiBh4GHOjiP--If8CynoNsOxPrp2ujs2LdxfRzvjkEDR8BIgXEsHVBY5wPxOx2uKt8fDT-AEj2ru3LrXtG23ENZQJa0YBCIGdGlrdG9r"; ssid_ucp_v1_ads="1.0.1-KDZmNTViMDYyMTZlNjIyN2U2NDQwNGQzYmY0MDA5YWM5MDQ0Yjg1ZTEKFwiSiJq2mKy512kQ-cq7zQYYzCQ4CEASEAMaAm15IiA5MzY4MWViZjg4YjVhOGQ3ZDYzYzg2YzYxMDRhYzRiZTJOCiAUEyZiQBSyTR0Pq-RVjJ_E3hBSVVjy3d9abJbStjhZ9RIgY_KkSwBIPyfF8o_Q9Go1qI61YCKujNaPhrHAsh47JQQYBCIGdGlrdG9r"; sso_uid_tt_ads="0f6b3e8b044dfde8ea5eb098009ef6e24689e3e5eb1c0053b04c3417c6dc5e9f"; sso_uid_tt_ss_ads="0f6b3e8b044dfde8ea5eb098009ef6e24689e3e5eb1c0053b04c3417c6dc5e9f"; sso_user_ads="b2d761a19c7ff5fd72b90e228c453348"; sso_user_ss_ads="b2d761a19c7ff5fd72b90e228c453348"; tt_session_tlb_tag_ads="sttt|1|k2gev4i1qNfWPIbGEErEvv_________DbbRROyJfXAPDatoS9ILtMXMk7sKYMMgyp8co7oprsHk="; ttwid="1|bj6y-acgqAu-xlMxD4t3NzqCYUf6G3PlcVqFmIwYpkU|1773069965|505814ca417411f2e972630ec2407d479488a52e626ce17ad8851e36cd668df8"; uid_tt_ads="b7c248d09e1059cb66c2e627c7659f94d800d2c867f915e750c6ed42dd01f3ba"; uid_tt_ss_ads="b7c248d09e1059cb66c2e627c7659f94d800d2c867f915e750c6ed42dd01f3ba" 

Observed referer:
https://ads.tiktok.com/business/creativecenter/keyword-insights/pc/en

Observed accept-language:
en-US,en;q=0.9

Observed note:
- the cookie/user-agent/referer/accept-language must be configurable via AppSettings
- do not hardcode secrets in source code
- use the values above only to shape the adapter and sample config support

## Observed response sample

```json
{
  "code": 0,
  "msg": "OK",
  "request_id": "20260310001030D47244E85D621396E41C",
  "data": {
    "keyword_list": [
      {
        "comment": 436,
        "cost": 40700,
        "cpa": 0.03,
        "ctr": 4.15,
        "cvr": 100,
        "impression": 28300000,
        "keyword": "this game",
        "like": 30544,
        "play_six_rate": 18.79,
        "post": 23800,
        "post_change": 77.24,
        "share": 187,
        "video_list": [
          "7571778224779267345",
          "7589796090572967175",
          "7613618054219468039",
          "7564841806261751048",
          "7567397649754770704"
        ]
      },
      {
        "comment": 399,
        "cost": 73200,
        "cpa": 0.01,
        "ctr": 11.1,
        "cvr": 100,
        "impression": 40200000,
        "keyword": "play now",
        "like": 53251,
        "play_six_rate": 24.42,
        "post": 20800,
        "post_change": 59.23,
        "share": 252,
        "video_list": [
          "7611094939748896016",
          "7589796090572967175",
          "7611115866368871681",
          "7611119963956464903",
          "7584805700031810817"
        ]
      },
      {
        "comment": 574,
        "cost": 25700,
        "cpa": 0.01,
        "ctr": 7.18,
        "cvr": 100,
        "impression": 16400000,
        "keyword": "harder than you think",
        "like": 25423,
        "play_six_rate": 35.96,
        "post": 17400,
        "post_change": 75.84,
        "share": 147,
        "video_list": [
          "7574580108401364225",
          "7613642779062799647",
          "7594552469032684801",
          "7602028967863864583",
          "7591673336921378066"
        ]
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 500,
      "has_more": true
    }
  }
}
```

## What to implement

1. Create or complete a live async HTTP adapter, e.g.:
   - `trend2video/integrations/tiktok/keyword_insights_source_tiktok.py`

2. Use `httpx.AsyncClient`.

3. Add or complete config support in `AppSettings` for:
   - `tiktok_cookie_header: str | None`
   - `tiktok_user_agent: str | None`
   - `tiktok_referer: str | None`
   - `tiktok_accept_language: str | None`
   - `tiktok_extra_headers_json: str | None`
   - keep any existing source-type setting aligned with the new live HTTP source

4. Build requests from `TrendSearchJob` fields:
   - page should default to 1
   - limit should come from `top_keywords_limit`
   - period should map from the job’s `time_window`
   - country_code should come from the selected country
   - order_by default to `post`
   - order_type default to `desc`

5. Parse the JSON response into the project’s `KeywordTrend` domain objects.
   Use the observed mapping instead of guessing:
   - `keyword` <- `keyword`
   - `rank` <- derived from position in returned list when explicit rank is absent
   - `popularity` <- `post`
   - `popularity_change` <- `post_change`
   - `ctr` <- `ctr`
   - store the full raw item in `raw_payload_json`
   - keep `source = "tiktok_keyword_insights_http"`

6. For `RelatedVideo`, use the returned `video_list` as the first live evidence source.
   If the repo currently expects URLs rather than IDs, map them into metadata and preserve the raw IDs in `metadata_json`.
   Do not invent unavailable fields.

7. Keep the current static source as the official dev/test fallback.
   Keep the old Playwright/DOM live source, if present, only as experimental fallback.

8. Add robust temporary debug logging for the live HTTP source:
   - final request URL
   - response status code
   - first 500 chars of body if JSON parsing fails
   - whether `code != 0` in response
   - keyword count extracted

9. Add tests:
   - request param building from a TrendSearchJob
   - response parsing from the observed sample JSON
   - config/header loading
   - integration-ish test using a mocked HTTP response

10. Update README:
   - document the new live HTTP keyword ingestion path
   - document required config values
   - explain that cookies/session headers may expire and need refresh
   - keep static source documented as fallback

## Important constraints

- Do not do a superficial patch.
- Reuse the existing v2 architecture and fit this source cleanly into it.
- Do not hardcode the provided cookie/header values into the codebase.
- Use these observed values only to shape the adapter and tests.
- Be honest about technical debt and TODOs.
- Preserve modularity and testability.

## Deliverables

Return:
1. short implementation plan
2. changed files
3. code updates
4. tests
5. README/config updates
6. commands to run locally
7. any remaining limitations

## Acceptance criteria

Task is complete when:
- the repo has a working live HTTP keyword source adapter
- it can build requests from job config
- it can parse the observed response shape into KeywordTrend objects
- tests for the new source pass
- README explains how to configure and use the live source
