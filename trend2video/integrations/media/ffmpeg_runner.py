from __future__ import annotations

import asyncio
import shutil


class FFmpegRunner:
    def __init__(self, executable: str = "ffmpeg") -> None:
        self._executable = executable

    async def run(self, args: list[str]) -> None:
        if shutil.which(self._executable) is None:
            raise RuntimeError("ffmpeg binary is not available in PATH")
        process = await asyncio.create_subprocess_exec(
            self._executable,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(stderr.decode("utf-8", errors="ignore").strip() or "ffmpeg render failed")
