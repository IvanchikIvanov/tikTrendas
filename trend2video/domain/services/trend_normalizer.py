from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from trend2video.domain.entities.trend import NormalizedTrend


class TrendNormalizer:
    """Преобразует сырой тренд из источника во внутренний NormalizedTrend."""

    def normalize(self, raw: dict[str, Any]) -> NormalizedTrend:
        """
        Нормализует словарь сырых данных в NormalizedTrend.

        Ожидается, что адаптер источника приведёт raw к минимально
        согласованной схеме; здесь только безопасные преобразования и дефолты.
        """

        source = str(raw.get("source") or "unknown")
        external_id = str(raw.get("external_id") or raw.get("id") or "")

        trend_type = str(raw.get("trend_type") or raw.get("type") or "generic")
        title = str(raw.get("title") or raw.get("name") or "").strip()
        region = str(raw.get("region") or raw.get("country") or "unknown")
        industry = raw.get("industry")
        if industry is not None:
            industry = str(industry)

        rank = self._to_int_or_none(raw.get("rank"))
        heat = self._to_float_or_none(raw.get("heat"))
        velocity = self._to_float_or_none(raw.get("velocity"))

        tags_raw = raw.get("tags") or raw.get("hashtags") or []
        if isinstance(tags_raw, str):
            tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        elif isinstance(tags_raw, list):
            tags = [str(t).strip() for t in tags_raw if str(t).strip()]
        else:
            tags = []

        discovered_at_raw = raw.get("discovered_at") or raw.get("timestamp")
        discovered_at = self._parse_datetime(discovered_at_raw)

        return NormalizedTrend(
            source=source,
            external_id=external_id,
            trend_type=trend_type,
            title=title,
            region=region,
            industry=industry,
            rank=rank,
            heat=heat,
            velocity=velocity,
            tags=tags,
            raw_payload=raw,
            discovered_at=discovered_at,
        )

    @staticmethod
    def _to_int_or_none(value: Any) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_float_or_none(value: Any) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_datetime(value: Any) -> datetime:
        if isinstance(value, datetime):
            return value.astimezone(timezone.utc)
        if isinstance(value, (int, float)):
            # Unix timestamp
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        if isinstance(value, str):
            for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                try:
                    dt = datetime.strptime(value, fmt)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    return dt.astimezone(timezone.utc)
                except ValueError:
                    continue
        # fallback: сейчас
        return datetime.now(tz=timezone.utc)

