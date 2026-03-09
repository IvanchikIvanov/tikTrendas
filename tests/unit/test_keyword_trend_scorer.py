from __future__ import annotations

from trend2video.core.config import get_settings
from trend2video.domain.entities.keyword_trend import KeywordTrend
from trend2video.domain.services.keyword_trend_scorer import KeywordTrendScorer


def test_keyword_trend_scorer_returns_useful_scores() -> None:
    trend = KeywordTrend(
        job_id=1,
        source="static",
        country="Belarus",
        time_window="7d",
        keyword="free delivery promo",
        rank=1,
        popularity=477,
        popularity_change=82.19,
        ctr=1.2,
        keyword_type="commercial",
        industry="ecommerce",
        objective="conversions",
    )
    scores = KeywordTrendScorer().score(trend, get_settings().brand_context)
    assert scores["signal_score"] > 0.4
    assert scores["keyword_usefulness_score"] > 0.4
