from pydantic import BaseModel, ConfigDict


class UserPublic(BaseModel):
    id: int
    email: str
    name: str
    picture_url: str | None = None

    model_config = ConfigDict(from_attributes=True)
