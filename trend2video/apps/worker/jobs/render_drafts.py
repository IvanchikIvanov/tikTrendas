from __future__ import annotations

import asyncio
from pathlib import Path

from trend2video.core.config import get_settings
from trend2video.core.db import get_session_factory
from trend2video.domain.entities.script import GeneratedScript
from trend2video.domain.entities.template import TemplateDefinition
from trend2video.domain.entities.render_job import RenderJobStatus
from trend2video.domain.services.render_engine import RenderEngine
from trend2video.domain.services.render_manifest_builder import RenderManifestBuilder
from trend2video.persistence.repositories.asset_repository import AssetRepository
from trend2video.persistence.repositories.render_job_repository import RenderJobRepository
from trend2video.persistence.repositories.script_repository import ScriptRepository
from trend2video.persistence.repositories.template_repository import TemplateRepository


async def run_render_draft(render_job_id: int) -> dict[str, str | int]:
    session_factory = get_session_factory()
    manifest_builder = RenderManifestBuilder()
    render_engine = RenderEngine()
    settings = get_settings()
    async with session_factory() as session:
        render_repo = RenderJobRepository(session)
        script_repo = ScriptRepository(session)
        template_repo = TemplateRepository(session)
        asset_repo = AssetRepository(session)
        render_job = await render_repo.get_by_id(render_job_id)
        if render_job is None:
            return {"render_job_id": render_job_id, "status": "missing"}
        script_orm = await script_repo.get_by_id(render_job.script_id)
        if script_orm is None:
            await render_repo.update_result(render_job_id, status=RenderJobStatus.FAILED, error="script not found")
            return {"render_job_id": render_job_id, "status": "failed"}
        template = await template_repo.get_by_id(render_job.template_id)
        if template is None:
            await render_repo.update_result(render_job_id, status=RenderJobStatus.FAILED, error="template not found")
            return {"render_job_id": render_job_id, "status": "failed"}
        assets = list(await asset_repo.list_active())
        manifest = manifest_builder.build(
            GeneratedScript.model_validate(script_orm.script_json),
            TemplateDefinition.model_validate(template.config_json),
            assets,
        )
        output_path = str(Path(settings.media_storage_base_path) / "renders" / f"render_{render_job_id}.mp4")
        try:
            await render_repo.update_result(render_job_id, status=RenderJobStatus.RENDERING, manifest=manifest)
            final_output = await render_engine.render(manifest, output_path)
            await render_repo.update_result(render_job_id, status=RenderJobStatus.COMPLETED, output_path=final_output, manifest=manifest)
            return {"render_job_id": render_job_id, "status": "completed", "output_path": final_output}
        except Exception as exc:
            await render_repo.update_result(render_job_id, status=RenderJobStatus.FAILED, manifest=manifest, error=str(exc))
            return {"render_job_id": render_job_id, "status": "failed", "error": str(exc)}


if __name__ == "__main__":
    asyncio.run(run_render_draft(1))
