from datetime import datetime, timezone

from trend2video.domain.services.trend_normalizer import TrendNormalizer


def test_trend_normalizer_basic():
    raw = {
        "source": "static",
        "external_id": "abc123",
        "trend_type": "hashtag",
        "title": "Test Trend",
        "region": "US",
        "rank": "1",
        "heat": "10.5",
        "velocity": "20",
        "tags": ["foo", "bar"],
        "discovered_at": datetime(2024, 1, 1, tzinfo=timezone.utc).isoformat(),
    }

    norm = TrendNormalizer().normalize(raw)

    assert norm.source == "static"
    assert norm.external_id == "abc123"
    assert norm.rank == 1
    assert norm.heat == 10.5
    assert norm.velocity == 20.0
    assert norm.tags == ["foo", "bar"]

