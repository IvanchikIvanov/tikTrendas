from __future__ import annotations

from pydantic import BaseModel, Field


class BrandContext(BaseModel):
    """Строгий контракт brand context, используемый scorer-ом и ScriptEngine."""

    product_name: str
    product_type: str
    audience: list[str]
    pain_points: list[str]
    tone: str
    forbidden_topics: list[str] = Field(default_factory=list)
    cta_style: str
    niche_tags: list[str] = Field(default_factory=list)

