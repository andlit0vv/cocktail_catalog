from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.favorite import Favorite


class FavoriteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_user(self, user_id: int) -> list[Favorite]:
        result = await self.session.execute(
            select(Favorite)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.added_at.desc())
        )
        return list(result.scalars().all())

    async def list_cocktail_ids(self, user_id: int) -> list[str]:
        result = await self.session.execute(
            select(Favorite.cocktail_id)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.added_at.desc())
        )
        return list(result.scalars().all())

    async def add(self, user_id: int, cocktail_id: str) -> Favorite:
        favorite = Favorite(user_id=user_id, cocktail_id=cocktail_id)
        self.session.add(favorite)
        try:
            await self.session.commit()
            await self.session.refresh(favorite)
            return favorite
        except IntegrityError:
            await self.session.rollback()
            result = await self.session.execute(
                select(Favorite).where(
                    Favorite.user_id == user_id,
                    Favorite.cocktail_id == cocktail_id,
                )
            )
            return result.scalar_one()

    async def remove(self, user_id: int, cocktail_id: str) -> bool:
        result = await self.session.execute(
            delete(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.cocktail_id == cocktail_id,
            )
        )
        await self.session.commit()
        return result.rowcount > 0

    async def exists(self, user_id: int, cocktail_id: str) -> bool:
        result = await self.session.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.cocktail_id == cocktail_id,
            )
        )
        return result.scalar_one_or_none() is not None
