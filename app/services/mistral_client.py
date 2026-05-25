from typing import AsyncIterator
from mistralai.client import Mistral
from app.config import settings


class MistralClient:
    def __init__(self) -> None:
        self._client = Mistral(api_key=settings.mistral_api_key)

    async def stream_chat(self, messages: list[dict]) -> AsyncIterator[str]:
        stream = await self._client.chat.stream_async(
            model=settings.mistral_model,
            messages=messages,
        )
        async for event in stream:
            choices = event.data.choices
            if not choices:
                continue
            content = choices[0].delta.content
            if isinstance(content, str) and content:
                yield content


mistral_client = MistralClient()
