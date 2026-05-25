from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class MessageCreate(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class MessagePublic(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationHistory(BaseModel):
    conversation_id: str | None
    messages: list[MessagePublic]
