from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.repositories.favorite import FavoriteRepository
from app.schemas.favorite import FavoriteCreate, FavoritePublic

router = APIRouter()


@router.get("", response_model=list[FavoritePublic])
async def list_favorites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = FavoriteRepository(db)
    return await repo.list_by_user(current_user.id)


@router.get("/ids", response_model=list[str])
async def list_favorite_ids(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = FavoriteRepository(db)
    return await repo.list_cocktail_ids(current_user.id)


@router.post("", response_model=FavoritePublic, status_code=201)
async def add_favorite(
    body: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = FavoriteRepository(db)
    return await repo.add(current_user.id, body.cocktail_id)


@router.delete("/{cocktail_id}", status_code=204)
async def remove_favorite(
    cocktail_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = FavoriteRepository(db)
    removed = await repo.remove(current_user.id, cocktail_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Favorite not found")
