from __future__ import annotations

from pathlib import Path

from trend2video.integrations.media.ffmpeg_runner import FFmpegRunner


class RenderEngine:
    def __init__(self, ffmpeg_runner: FFmpegRunner | None = None) -> None:
        self._runner = ffmpeg_runner or FFmpegRunner()

    async def render(self, manifest: dict, output_path: str) -> str:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        scenes = manifest.get("scenes", [])
        if not scenes:
            raise ValueError("render manifest does not contain scenes")

        filter_parts: list[str] = []
        args: list[str] = ["-y"]
        for index, scene in enumerate(scenes):
            args.extend(["-stream_loop", "-1", "-t", str(scene["duration_sec"]), "-i", scene["asset_path"]])
            drawtext = self._build_drawtext(scene.get("text") or "")
            filter_parts.append(
                f"[{index}:v]scale=1080:1920:force_original_aspect_ratio=cover,"
                f"crop=1080:1920,{drawtext},fps=30,format=yuv420p[v{index}]"
            )
        concat_inputs = "".join(f"[v{index}]" for index in range(len(scenes)))
        filter_parts.append(f"{concat_inputs}concat=n={len(scenes)}:v=1:a=0[vout]")
        args.extend(
            [
                "-filter_complex",
                ";".join(filter_parts),
                "-map",
                "[vout]",
                "-r",
                "30",
                "-pix_fmt",
                "yuv420p",
                str(output),
            ]
        )
        await self._runner.run(args)
        return str(output)

    def _build_drawtext(self, text: str) -> str:
        escaped = text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
        return (
            "drawtext=text='"
            f"{escaped}'"
            ":fontcolor=white:fontsize=48:line_spacing=8:borderw=2:bordercolor=black:"
            "x=(w-text_w)/2:y=h-(text_h*2)-180"
        )
