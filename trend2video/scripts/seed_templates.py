from __future__ import annotations

import asyncio

from trend2video.core.db import get_session_factory
from trend2video.domain.entities.template import TemplateDefinition, TemplateScene
from trend2video.persistence.models.template import TemplateORM


TEMPLATES: list[TemplateDefinition] = [
    TemplateDefinition(
        template_key="problem_solution_fastcut",
        version="v1",
        name="Problem Solution Fast Cut",
        duration_sec=18,
        aspect_ratio="9:16",
        hooks=[
            "Ты тоже делаешь это неправильно?",
            "Вот почему это не работает",
            "Самая частая ошибка в этой задаче",
        ],
        scene_plan=[
            TemplateScene(
                scene_id="hook",
                asset_type="broll",
                asset_tag="product_closeup",
                duration_sec=2.5,
                text_slot="hook_text",
            ),
            TemplateScene(
                scene_id="pain",
                asset_type="ugc",
                asset_tag="frustration",
                duration_sec=3.0,
                text_slot="pain_text",
            ),
            TemplateScene(
                scene_id="solution",
                asset_type="screenrec",
                asset_tag="demo_main",
                duration_sec=6.0,
                text_slot="solution_text",
            ),
            TemplateScene(
                scene_id="cta",
                asset_type="broll",
                asset_tag="logo_endcard",
                duration_sec=2.5,
                text_slot="cta_text",
            ),
        ],
        caption_policy={
            "style": "short_lines",
            "max_chars_per_line": 28,
        },
        tags=["direct_response", "demo", "pain_solution"],
        active=True,
    ),
    TemplateDefinition(
        template_key="myth_busting",
        version="v1",
        name="Myth Busting",
        duration_sec=20,
        aspect_ratio="9:16",
        hooks=[
            "Тебе врали всё это время",
            "3 мифа, которые мешают результатам",
        ],
        scene_plan=[
            TemplateScene(
                scene_id="hook",
                asset_type="ugc",
                asset_tag="face_cam",
                duration_sec=3.0,
                text_slot="hook_text",
            ),
            TemplateScene(
                scene_id="myth",
                asset_type="broll",
                asset_tag="myth_visual",
                duration_sec=5.0,
                text_slot="pain_text",
            ),
            TemplateScene(
                scene_id="reality",
                asset_type="screenrec",
                asset_tag="proof",
                duration_sec=7.0,
                text_slot="solution_text",
            ),
            TemplateScene(
                scene_id="cta",
                asset_type="ugc",
                asset_tag="face_cam",
                duration_sec=3.0,
                text_slot="cta_text",
            ),
        ],
        caption_policy={},
        tags=["myth_busting", "education"],
        active=True,
    ),
    TemplateDefinition(
        template_key="before_after_demo",
        version="v1",
        name="Before After Demo",
        duration_sec=22,
        aspect_ratio="9:16",
        hooks=[
            "До и после: что меняется за 7 дней",
        ],
        scene_plan=[
            TemplateScene(
                scene_id="before",
                asset_type="ugc",
                asset_tag="frustration",
                duration_sec=4.0,
                text_slot="pain_text",
            ),
            TemplateScene(
                scene_id="after",
                asset_type="ugc",
                asset_tag="relief",
                duration_sec=4.0,
                text_slot="outcome_text",
            ),
            TemplateScene(
                scene_id="demo",
                asset_type="screenrec",
                asset_tag="product_demo",
                duration_sec=8.0,
                text_slot="solution_text",
            ),
            TemplateScene(
                scene_id="cta",
                asset_type="broll",
                asset_tag="logo_endcard",
                duration_sec=3.0,
                text_slot="cta_text",
            ),
        ],
        caption_policy={},
        tags=["before_after", "demo"],
        active=True,
    ),
]


async def seed() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        for t in TEMPLATES:
            tmpl_id = t.id
            existing = await session.get(TemplateORM, tmpl_id)
            data = t.model_dump(mode="json")
            if existing is None:
                obj = TemplateORM(
                    id=tmpl_id,
                    template_key=t.template_key,
                    version=t.version,
                    config_json=data,
                    is_active=t.active,
                )
                session.add(obj)
            else:
                existing.template_key = t.template_key
                existing.version = t.version
                existing.config_json = data
                existing.is_active = t.active
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())

