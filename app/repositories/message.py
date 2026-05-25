from datetime import datetime
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import Message


class MessageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active_conversation_id(self, user_id: int) -> str | None:
        result = await self._session.execute(
            select(Message.conversation_id)
            .where(Message.user_id == user_id)
            .order_by(desc(Message.created_at))
            .limit(1)
        )
        row = result.scalar_one_or_none()
        return row

    async def get_history(
        self, user_id: int, conversation_id: str, limit: int = 10
    ) -> list[Message]:
        result = await self._session.execute(
            select(Message)
            .where(Message.user_id == user_id, Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )
        messages = list(result.scalars().all())
        messages.reverse()
        return messages

    async def get_full_conversation(
        self, user_id: int, conversation_id: str
    ) -> list[Message]:
        result = await self._session.execute(
            select(Message)
            .where(Message.user_id == user_id, Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        return list(result.scalars().all())

    async def add(
        self, user_id: int, conversation_id: str, role: str, content: str
    ) -> Message:
        msg = Message(
            user_id=user_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=datetime.utcnow(),
        )
        self._session.add(msg)
        await self._session.commit()
        await self._session.refresh(msg)
        return msg

    async def clear_conversation(self, user_id: int, conversation_id: str) -> int:
        result = await self._session.execute(
            delete(Message).where(
                Message.user_id == user_id,
                Message.conversation_id == conversation_id,
            )
        )
        await self._session.commit()
        return result.rowcount
