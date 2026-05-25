import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.repositories.message import MessageRepository
from app.schemas.chat import MessageCreate, ConversationHistory, MessagePublic
from app.services.assistant import assistant_service
from app.services.rate_limiter import rate_limiter

router = APIRouter(tags=["assistant"])


@router.post("/message")
async def send_message(
    body: MessageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not await rate_limiter.check(user.id):
        raise HTTPException(
            status_code=429,
            detail="Слишком много сообщений. Подождите немного.",
        )

    try:
        conv_id, stream = await assistant_service.respond(user, body.message, db)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    async def sse_gen():
        yield f"data: {json.dumps({'conversation_id': conv_id})}\n\n"
        try:
            async for chunk in stream:
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(sse_gen(), media_type="text/event-stream")


@router.get("/history", response_model=ConversationHistory)
async def get_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    message_repo = MessageRepository(db)
    conv_id = await message_repo.get_active_conversation_id(user.id)
    if conv_id is None:
        return ConversationHistory(conversation_id=None, messages=[])
    messages = await message_repo.get_full_conversation(user.id, conv_id)
    return ConversationHistory(
        conversation_id=conv_id,
        messages=[MessagePublic.model_validate(m) for m in messages],
    )


@router.delete("/history", status_code=204)
async def clear_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await assistant_service.clear_conversation(user.id, db)
