from __future__ import annotations

from typing import Protocol, Type

from pydantic import BaseModel


class LLMClient(Protocol):
    """Абстракция LLM-клиента, выдающего структурированный JSON по схеме."""

    async def generate_structured(self, prompt: str, schema: Type[BaseModel]) -> dict:
        """Сгенерировать JSON, совместимый с переданной Pydantic-схемой."""

        ...

