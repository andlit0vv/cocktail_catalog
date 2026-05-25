from datetime import datetime
from pydantic import BaseModel, ConfigDict


class FavoriteCreate(BaseModel):
    cocktail_id: str


class FavoritePublic(BaseModel):
    cocktail_id: str
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)
