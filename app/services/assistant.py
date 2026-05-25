import uuid
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import AsyncSessionLocal
from app.models.user import User
from app.repositories.message import MessageRepository
from app.services import cocktail_search
from app.services.mistral_client import mistral_client
from app.config import settings

SYSTEM_PROMPT = """Ты дружелюбный AI-бармен, помогаешь пользователю выбирать коктейли.
Тебе передаются релевантные коктейли из каталога TheCocktailDB в начале сообщения пользователя (после метки "КОНТЕКСТ:"). Опирайся в первую очередь на эти коктейли при рекомендациях.
Если контекст пустой или коктейли не подходят — можешь отвечать из общих знаний, но честно скажи, что в каталоге подходящих не нашлось.

Правила:
- ВСЕГДА отвечай на русском языке, независимо от языка контекста.
- Не повторяй контекст в начале ответа — сразу отвечай по существу.
- Отвечай кратко и по делу.
- Если рекомендуешь коктейль — назови ингредиенты с пропорциями и краткую инструкцию.
- Если пользователь спрашивает не про коктейли/алкоголь — мягко возвращай к теме.
- Если у пользователя есть только часть ингредиентов — предложи варианты замен или коктейли попроще.
- Не выдумывай коктейли, которых нет в каталоге. Лучше скажи "в каталоге не нашёл, но есть похожий: ..."
"""


class AssistantService:
    async def respond(
        self, user: User, message: str, db: AsyncSession
    ) -> tuple[str, AsyncIterator[str]]:
        message_repo = MessageRepository(db)

        conv_id = await message_repo.get_active_conversation_id(user.id)
        if conv_id is None:
            conv_id = str(uuid.uuid4())

        await message_repo.add(user.id, conv_id, "user", message)

        ingredients = await cocktail_search.extract_ingredients_from_text(message)
        cocktails = []
        if ingredients:
            cocktails = await cocktail_search.find_by_ingredients(ingredients, limit=8)
        if not cocktails:
            cocktails = await cocktail_search.find_by_name(message, limit=5)

        context = cocktail_search.format_cocktails_for_prompt(cocktails) if cocktails else ""

        history = await message_repo.get_history(
            user.id, conv_id, limit=settings.assistant_history_limit
        )

        messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in history[:-1]:
            messages.append({"role": msg.role, "content": msg.content})

        user_content = message
        if context:
            user_content = f"Релевантные коктейли из каталога:\n{context}\n\nВопрос пользователя: {message}"
        messages.append({"role": "user", "content": user_content})

        # Capture these for the closure — the outer `db` session may be closed
        # by FastAPI's dependency cleanup before streaming finishes.
        _user_id = user.id
        _conv_id = conv_id

        async def stream_and_save() -> AsyncIterator[str]:
            full_response: list[str] = []
            try:
                async for chunk in mistral_client.stream_chat(messages):
                    full_response.append(chunk)
                    yield chunk
            finally:
                if full_response:
                    # Use a fresh session — the request session is likely closed by now.
                    async with AsyncSessionLocal() as save_session:
                        repo = MessageRepository(save_session)
                        await repo.add(_user_id, _conv_id, "assistant", "".join(full_response))

        return conv_id, stream_and_save()

    async def clear_conversation(self, user_id: int, db: AsyncSession) -> None:
        message_repo = MessageRepository(db)
        conv_id = await message_repo.get_active_conversation_id(user_id)
        if conv_id:
            await message_repo.clear_conversation(user_id, conv_id)


assistant_service = AssistantService()
