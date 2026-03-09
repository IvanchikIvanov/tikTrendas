from __future__ import annotations

from trend2video.domain.entities.brand import BrandContext
from trend2video.domain.entities.keyword_trend import KeywordTrend


class KeywordTrendScorer:
    def score_signal_strength(self, keyword_trend: KeywordTrend) -> float:
        popularity = max(0.0, float(keyword_trend.popularity or 0.0))
        growth = max(0.0, float(keyword_trend.popularity_change or 0.0))
        ctr = max(0.0, float(keyword_trend.ctr or 0.0))
        return min(1.0, popularity / 1000.0 * 0.5 + growth / 100.0 * 0.35 + ctr / 10.0 * 0.15)

    def score_product_relevance(self, keyword_trend: KeywordTrend, brand_ctx: BrandContext) -> float:
        haystack = " ".join(
            filter(
                None,
                [
                    keyword_trend.keyword.lower(),
                    (keyword_trend.industry or "").lower(),
                    (keyword_trend.objective or "").lower(),
                ],
            )
        )
        if not haystack:
            return 0.0
        tags = {tag.lower() for tag in brand_ctx.niche_tags}
        pains = {pain.lower() for pain in brand_ctx.pain_points}
        matches = sum(1 for token in tags | pains if token and token in haystack)
        return min(1.0, matches / max(1, len(tags | pains)))

    def score_keyword_usefulness(self, keyword_trend: KeywordTrend) -> float:
        keyword = keyword_trend.keyword.lower()
        high_intent_markers = ("free", "sale", "delivery", "promo", "discount", "launch", "review")
        marker_bonus = 0.25 if any(marker in keyword for marker in high_intent_markers) else 0.0
        rank_bonus = max(0.0, (20 - float(keyword_trend.rank or 20)) / 20.0) * 0.35
        type_bonus = 0.2 if (keyword_trend.keyword_type or "").lower() in {"commercial", "product"} else 0.0
        return min(1.0, marker_bonus + rank_bonus + type_bonus + 0.2)

    def score(self, keyword_trend: KeywordTrend, brand_ctx: BrandContext) -> dict[str, float]:
        signal = self.score_signal_strength(keyword_trend)
        relevance = self.score_product_relevance(keyword_trend, brand_ctx)
        usefulness = self.score_keyword_usefulness(keyword_trend)
        return {
            "signal_score": round(signal, 4),
            "product_relevance_score": round(relevance, 4),
            "keyword_usefulness_score": round(usefulness, 4),
            "overall_score": round(min(1.0, signal * 0.45 + relevance * 0.35 + usefulness * 0.20), 4),
        }
