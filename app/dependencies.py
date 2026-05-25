from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.services import jwt_service


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = jwt_service.decode_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await UserRepository(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


async def get_optional_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User | None:
    token = request.cookies.get("access_token")
    if not token:
        return None
    user_id = jwt_service.decode_token(token)
    if user_id is None:
        return None
    return await UserRepository(db).get_by_id(user_id)
