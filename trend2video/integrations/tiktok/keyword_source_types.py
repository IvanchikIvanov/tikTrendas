from __future__ import annotations

from collections.abc import Sequence


STATIC_SOURCE_TYPE = "static"
TIKTOK_HTTP_SOURCE_TYPE = "tiktok_http"
SUPPORTED_KEYWORD_SOURCE_TYPES = frozenset({STATIC_SOURCE_TYPE, TIKTOK_HTTP_SOURCE_TYPE})


def normalize_source_types(source_types: Sequence[str] | None) -> list[str]:
    normalized: list[str] = []
    for source_type in source_types or []:
        value = source_type.strip()
        if not value:
            continue
        if value not in SUPPORTED_KEYWORD_SOURCE_TYPES:
            allowed = ", ".join(sorted(SUPPORTED_KEYWORD_SOURCE_TYPES))
            raise ValueError(f"source_types contains unsupported value '{source_type}'. Allowed values: {allowed}")
        if value not in normalized:
            normalized.append(value)
    return normalized
